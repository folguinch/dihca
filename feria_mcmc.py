#!/bin/python3
"""Classes and functions for MCMC fitting with FERIA."""
from typing import Dict, Tuple, List
from configparser import ConfigParser, ExtendedInterpolation
from itertools import product
from pathlib import Path
from string import Template
import sys
import subprocess
import warnings
warnings.filterwarnings('ignore')

from astropy.coordinates import SkyCoord
from astropy.io import fits
from casatasks import importfits, imregrid
from line_little_helper.molecule import Molecule
from line_little_helper.pvmap_extractor import get_pvmap_from_slit
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import binary_dilation
from spectral_cube import SpectralCube
from toolkit.astro_tools.masking import proportional_dilation
from toolkit.converters import array_to_hdu
import astropy.units as u
import numpy as np
import toolkit.astro_tools.images as imtools

try: 
    from common_paths import CONFIGS
    from common_vars import SAVED_MOLS

    FERIA = Path('~/clones/FERIA/feria').expanduser()
    TEMPLATE = CONFIGS / 'templates/feria_template.in'
except ImportError:
    CONFIGS = None
    SAVED_MOLS = None
    FERIA = None
    TEMPLATE = None

class ObsFit:
    config: ConfigParser
    source: Dict
    obs_pars: Dict
    data: Dict

    def __init__(self,
                 config: Path,
                 outdir: Path,
                 pixsize: str = '0.01',
                 velres: str = '0.2'):
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(config)

        # Sections
        molecule = self.config['molecule']
        info = self.config['info']

        # Store parameters
        self.source = {
            'object': info['name'],
            'ra': info['ra'],
            'dec': info['dec'],
            'distance': f'{self.distance.to(u.pc).value}',
            'vsys': f'{self.vsys.to(u.km/u.s).value}'
        }
        self.obs_pars = {
            'line': molecule['name'],
            'restfreq': f'{self.restfreq.to(u.GHz).value}',
            'pixsize': molecule.get('pixsize', fallback=pixsize),
            'velres': molecule.get('velres', fallback=velres),
        }

        # Source cube
        cube, cube_beam = self.get_cube_pars(outdir)
        self.obs_pars.update(cube_beam)
        self.data = {'cube': cube}

        # Source pv
        if 'pv_rms' in self.config['data']:
            self.data['pv_data'] = self.get_pv_pars()

    @property
    def position(self) -> SkyCoord:
        return SkyCoord(self.source['ra'], self.source['dec'], frame='icrs')

    @property
    def distance(self) -> u.Quantity:
        distance = self.config['info']['distance'].split()
        return float(distance[0]) * u.Unit(distance[1])

    @property
    def vsys(self) -> u.Quantity:
        vsys = self.config['info']['vsys'].split()
        return float(vsys[0]) * u.Unit(vsys[1])

    @property
    def restfreq(self) -> u.Quantity:
        # Load molecule information
        molecule = self.config['molecule']
        if 'restfreq' in molecule:
            restfreq = molecule['restfreq'].split()
            restfreq = float(restfreq[0]) * u.Unit(restfreq[1])
        elif SAVED_MOLS is not None:
            aux = Molecule.from_json(SAVED_MOLS[molecule['name']])
            restfreq = aux.transition_info(molecule['transition']).restfreq

        return restfreq

    def get_cube_pars(self,
                      outdir: Path,
                      nsigma: float = 5
                      #dilate: int = 10
                      ) -> Tuple[Dict]:
        # Import cube to CASA format
        cube_path = Path(self.config['data']['cube'])
        imagename = outdir / cube_path.with_suffix('.image').name
        if not imagename.exists():
            importfits(fitsimage=f'{cube_path}',
                       imagename=f'{imagename}',
                       overwrite=True)
        
        # Open cube
        cube = SpectralCube.read(cube_path)

        # Change to velocity
        cube = cube.with_spectral_unit(u.km/u.s,
                                       velocity_convention='radio',
                                       rest_value=self.restfreq)
        unit = cube.unit
        beam = cube.beam

        # Create masked data
        rms = self.config['data']['cube_rms'].split()
        rms = float(rms[0]) * u.Unit(rms[1])
        nsigma = self.config.getfloat('data', 'cube_nsigma', fallback=nsigma)
        data = cube.unmasked_data[:,:,:]
        mask = data >= nsigma * rms

        # Proportional dilate
        mask, dilate = proportional_dilation(mask)
        data = np.ma.array(data.value, mask=~mask)
        data = np.ma.masked_invalid(data)

        # Save mask
        maskfile = cube_path.with_suffix(f'.{nsigma}sigma.dilate{dilate}.mask.fits')
        if not maskfile.exists():
            hdu = fits.PrimaryHDU(data=mask.astype(int),
                                  header=cube.wcs.to_header())
            hdu.writeto(maskfile)

        # Max map
        mask = cube >= nsigma * rms
        cube = cube.with_mask(mask)
        max_map = np.ma.array(cube.argmax_world(axis=0).value, fill_value=0.)
        max_map = np.ma.masked_invalid(max_map)
        sigma_vel = np.mean(np.abs(cube.spectral_axis[:-1] -
                                   cube.spectral_axis[1:]))
        sigma_vel = sigma_vel.to(u.km/u.s).value / 2

        # Save max map
        maxfile = imagename.with_suffix(
            f'.{nsigma}sigma.max_map.fits')
        if not maxfile.exists():
            hdu = fits.PrimaryHDU(data=max_map.filled(fill_value=0.),
                                  header=cube.wcs.sub(2).to_header())
            hdu.header['BUNIT'] = f'{cube.unit:fits}'
            hdu.writeto(maxfile)

        # Store parameters
        cube_pars = {'cubename': cube_path,
                     'imagename': imagename,
                     'rms': rms.to(unit),
                     'masked_cube': data,
                     'max_map': max_map,
                     'sigma_vel': sigma_vel,
                     'beam': beam,
                     'wcs': cube.wcs}

        # Store beam in obs params
        beam_pars = {'bmaj': f'{beam.major.to(u.arcsec).value}',
                     'bmin': f'{beam.minor.to(u.arcsec).value}',
                     'bpa': f'{beam.pa.to(u.deg).value}'}

        return cube_pars, beam_pars

    def _get_pv(self,
                label: str,
                cube: SpectralCube,
                length: u.Quantity,
                width: u.Quantity,
                angle: u.Quantity,
                rms: u.Quantity,
                nsigma: float,
                ):
        """Load pv map."""
        suffix = f'.pv_{label}.fits'
        filename = self.data['cube']['imagename'].with_suffix(suffix)
        if not filename.exists():
            pv = get_pvmap_from_slit(cube, self.position, length, width, angle,
                                     recenter=True)
            pv.writeto(filename)

        # Load stored
        pv = fits.open(filename)[0]
        bunit = u.Unit(pv.header['BUNIT'])

        # Masks
        mask = pv.data * bunit >= nsigma * rms.to(bunit)
        mask, dilate = proportional_dilation(mask, fraction=2)

        # Save mask
        mask_suffix = f'.{nsigma}sigma.dilate{dilate}.mask.fits'
        maskfile = filename.with_suffix(mask_suffix)
        if not maskfile.exists():
            hdu = fits.PrimaryHDU(data=mask.astype(int),
                                  header=pv.header)
            hdu.writeto(maskfile)

        return pv, bunit, mask

    def get_pv_pars(self) -> Dict:
        """Load pv data."""
        # Separate cases
        if 'pa_disk' in self.config['info']:
            angles = {'disk': u.Quantity(self.config.get('info', 'pa_disk')),
                      'out': u.Quantity(self.config.get('info', 'pa_out'))}
        elif 'pv_angles' in self.config['info']:
            vals, unit = self.config['info']['pv_angles'].split()
            vals = [u.Quantity(f'{val}{unit}') for val in vals.split(',')]
            if 'pv_labels' in self.config['info']:
                labels = self.config['info']['pv_labels'].split()
            else:
                labels = [f'{val.value:g}' for val in vals]
            angles = {label: val for label, val in zip(labels, vals)}
        elif 'pv_auto' in self.config['info']:
            nangles, *start = self.config['info']['pv_auto'].split()
            start = u.Quantity(' '.join(start))
            vals = np.linspace(start.to(u.deg).value,
                               start.to(u.deg).value + 180,
                               nangles + 1)[:-1]
            labels = [f'{val:g}' for val in vals]
            angles = {label: val*start.unit for label, val in zip(labels, vals)}

        # Get weights
        aux = self.config.get('info', 'pv_weights', fallback='0.4').split()
        if len(aux) == len(angles):
            weights = {}
            for label, weight in zip(angles, aux):
                weights[label] = float(weight)
        elif len(aux) == 1:
            weights = {label: float(aux[0]) for label in angles}
        else:
            raise ValueError(f'Cannot determine weights: {aux}')

        # Global parameters
        length = u.Quantity(self.config.get('data', 'pv_length'))
        width = u.Quantity(self.config.get('data', 'pv_width'))
        rms = u.Quantity(self.config['data']['pv_rms'])
        nsigma = self.config.getfloat('data', 'pv_nsigma ', fallback=3)
        #dilate = self.config.getfloat('data', 'pv_nsigma ', fallback=5)

        # Open cube
        cube = SpectralCube.read(self.data['cube']['cubename'])
        cube = cube.with_spectral_unit(u.km/u.s,
                                       velocity_convention='radio',
                                       rest_value=self.restfreq)

        # Load maps
        pv_data = {}
        for label, angle in angles.items():
            pv, bunit, mask = self._get_pv(label, cube, length, width, angle,
                                           rms, nsigma)
            xunit = u.Unit(pv.header['CUNIT1'])
            yunit = u.Unit(pv.header['CUNIT2'])
            xdir = np.sign(float(pv.header['CDELT1']))
            ydir = np.sign(float(pv.header['CDELT2']))
            pv_data[label] = {
                'data': np.ma.array(pv.data / np.nanmax(pv.data),
                                    mask=~mask),
                'rms': rms.to(bunit).value / np.nanmax(pv.data),
                'path': (length, width, angle),
                'weight': weights[label],
                'axes_units': (xunit, yunit),
                'axes_directions': (xdir, ydir),
            }

        return pv_data

    def get_param_ranges(self):
        """Read range of parameters from config."""
        vals = {}
        for opt, val in self.config.items('param_ranges'):
            vals[opt] = tuple(map(float, val.split()))

        return vals

    def get_fixed_params(self):
        """Read fixed parameters."""
        vals = {}
        for opt, val in self.config.items('fixed_params'):
            if opt == 'rot':
                vals[opt] = int(val)
            elif opt == 'rin' and val == 'CB':
                vals[opt] = val
            else:
                vals[opt] = float(val)

        return vals

class Model:
    pars: Dict
    fixed: Tuple

    def __init__(self, fixed, **params):
        self.pars = params
        if self.pars['rin'] == 'CB':
            self.pars['rin'] = self.pars['rcb']
        self.fixed = fixed

    def __call__(self,
                 output: Path,
                 obspars: ObsFit,
                 template: Path = TEMPLATE) -> Path:
        template = Template(template.read_text())
        outcube = output / self.get_cubename()
        infile = outcube.with_suffix('.in')
        params = {}
        for key, val in self.pars.items():
            if key in ['dra', 'ddec']:
                continue
            params[key] = f'{val}'
        #params = {key: f'{val}' for key, val in self.pars.items()}
        params = params | obspars.source | obspars.obs_pars
        
        # Shift model coordinates
        if self.pars['dra'] != 0 or self.pars['ddec'] != 0:
            pos = obspars.position
            dra = self.pars['dra'] * u.mas
            ddec = self.pars['ddec'] * u.mas
            pos = SkyCoord(pos.ra + dra, pos.dec + ddec, frame=pos.frame.name)
            ra, dec = pos.to_string(style='hmsdms').split()
            params['ra'], params['dec'] = ra, dec

        infile.write_text(template.substitute(output=f'{outcube}',
                                              **params))
        if not outcube.is_file():
            in_parent_in = list(output.glob('*.fits'))
            subprocess.run(f'{FERIA} < {infile}', shell=True,
                           capture_output=False)
            in_parent_out = list(output.glob('*.fits'))

        return outcube

    def get_cubename(self):
        cube = ['cube',
                '_'.join(f'{k}{v:.2f}'
                         for k, v in self.pars.items()
                         if k not in self.fixed)]
        return '_'.join(cube) + '.fits'

    def to_config(self, output: Path):
        raise NotImplementedError

def cube_axes(cube):
    nx = cube.shape[2]
    ny = cube.shape[1]
    wcs = cube.wcs.celestial
    ra = wcs.wcs_pix2world(np.arange(nx), np.zeros(nx), 0)[0] * u.deg
    dec = wcs.wcs_pix2world(np.zeros(ny), np.arange(ny), 0)[1] * u.deg
    vel = cube.spectral_axis.to(u.km/u.s)

    return ra, dec, vel

def log_posterior_cube(params: Dict, **kwargs):
    """Calculate the posterior probability.

    Used keyword arguments are:
    
    - `fixed_params`: a dictionary with fixed parameters.
    - `ranges`: a dictionary with parameter ranges.
    - `obs`: an `ObsFit` object.
    - `outdir`: a `Path` for the output directory.

    The `params` are concatenated with `fixed_params` to generate a model.
    """
    model_dir = kwargs['outdir']
    def log_like_f(params, obs, model_dir, fixed):
        # Compute model
        model = Model(fixed, **params)
        model_cube = model(model_dir, obs)

        # Convert to CASA
        cube_name = model_cube.with_suffix('.image')
        importfits(fitsimage=f'{model_cube}', imagename=f'{cube_name}',
                   overwrite=True)
            
        # Regrid cube
        template = obs.data['cube']['imagename']
        cube_regrid = cube_name.with_suffix('.interp.image')
        imregrid(f'{cube_name}', template=f"{template}",
                 output=f'{cube_regrid}', asvelocity=True, overwrite=True)
        new_cube = SpectralCube.read(cube_regrid)
        restfreq = float(obs.obs_pars['restfreq']) * u.GHz
        new_cube = new_cube.with_spectral_unit(u.km/u.s,
                                               velocity_convention='radio',
                                               rest_value=restfreq)
        mask = (np.isnan(new_cube.unmasked_data[:]) &
                ~obs.data['cube']['masked_cube'].mask)
        new_cube.unmasked_data[:][mask] = 0. * new_cube.unit

        # Normalize to the peak intensity
        obs_max = np.nanmax(obs.data['cube']['masked_cube'])
        norm_obs_cube = np.nanargmax(obs.data['cube']['masked_cube']) / obs_max
        norm_cube = (new_cube.unmasked_data[:].value /
                     new_cube.max().value)

        # Save model cube
        new_cube = SpectralCube(data=norm_cube, wcs=new_cube.wcs)
        cube_regrid = cube_name.with_suffix('.interp.fits')
        new_cube.write(cube_regrid, overwrite=True)
    
        # Chi
        sigma = obs.data['cube']['masked_cube'] * 0.1 / obs_max
        sigma = np.sqrt(sigma**2 + (obs.data['cube']['rms'].value / obs_max)**2)
        #sigma = obs.data['cube']['rms'].value / obs_max
        if np.nan in sigma or np.inf in sigma:
            raise Exception
        term1 = -0.5 * np.ma.sum(np.log(2 * np.pi * sigma**2))
        chi2 = (norm_obs_cube - norm_cube)**2 / sigma**2
        term2 = -0.5 * np.ma.sum(chi2)

        return term1 + term2

    def log_prior(params, ranges):
        if params['rin'] == 'CB':
            rin = params['rcb']
        else:
            rin = params['rin']
        for key, val in ranges.items():
            if params[key] < val[0] or params[key] > val[1]:
                return -np.inf
        if rin > params['rcb'] or params['rout'] <= params['rcb']:
            return -np.inf
        return 0

    if log_prior(params | kwargs['fixed_params'], kwargs['ranges']) == 0:
        return log_like_f(params | kwargs['fixed_params'], kwargs['obs'],
                          model_dir, list(kwargs['fixed_params'].keys()))
    else:
        return -np.inf

def log_posterior_pv(params: Dict, **kwargs):
    """Calculate the posterior probability.

    Used keyword arguments are:
    
    - `fixed_params`: a dictionary with fixed parameters.
    - `ranges`: a dictionary with parameter ranges.
    - `obs`: an `ObsFit` object.
    - `outdir`: a `Path` for the output directory.

    The `params` are concatenated with `fixed_params` to generate a model.
    """
    model_dir = kwargs['outdir']
    def log_like_f(params, obs, model_dir, fixed):
        # Compute model
        model = Model(fixed, **params)
        model_cube_name = model(model_dir, obs)
        model_pvs, model_max = pv_products(model_cube_name, obs)

        # Chi
        chis = []
        total_weight = 0
        for label, model_pv in model_pvs.items():
            sigma = np.repeat(obs.data['pv_data'][label]['rms'],
                              np.sum(~obs.data['pv_data'][label]['data'].mask))
            term1 = -0.5 * np.ma.sum(np.log(2 * np.pi * sigma**2))
            norm_model = model_pv.data / np.nanmax(model_pv.data)
            chi2 = (obs.data['pv_data'][label]['data'] - norm_model)**2
            chi2 = chi2 / obs.data['pv_data'][label]['rms']**2
            term2 = -0.5 * np.ma.sum(chi2)
            weight = obs.data['pv_data'][label]['weight']
            chis.append((term1 + term2) * weight)
            total_weight += weight

        if total_weight != 1:
            sigma_max = np.repeat(obs.data['cube']['sigma_vel'],
                                  np.sum(~obs.data['cube']['max_map'].mask))
            term1_max = -0.5 * np.ma.sum(np.log(2 * np.pi * sigma_max**2))
            chi2_max = (obs.data['cube']['max_map'] - model_max)**2 
            chi2_max = chi2_max / obs.data['cube']['sigma_vel']**2
            term2_max = -0.5 * np.ma.sum(chi2_max)
            weight_max = 1 - total_weight
            if weight_max < 0:
                raise ValueError
            chis.append((term1_max + term2_max) * weight_max)

        chi_tot = np.sum(chis)
        if np.isnan(chi_tot):
            return -np.inf
        else:
            return chi_tot

    def log_prior(params, ranges):
        if params['rin'] == 'CB':
            rin = params['rcb']
        else:
            rin = params['rin']
        for key, val in ranges.items():
            if params[key] < val[0] or params[key] > val[1]:
                return -np.inf
        if rin > params['rcb'] or params['rout'] <= params['rcb']:
            return -np.inf
        return 0

    if log_prior(params | kwargs['fixed_params'], kwargs['ranges']) == 0:
        return log_like_f(params | kwargs['fixed_params'], kwargs['obs'],
                          model_dir, list(kwargs['fixed_params'].keys()))
    else:
        return -np.inf

def pv_products(model_cube_name: Path,
                obs: ObsFit,
                save_products: bool = False,
                is_regrid: bool = False,
                get_max_map: bool = True):
    """Generate products from model."""
    # Convert to CASA
    cube_name = model_cube_name.with_suffix('.image')
    importfits(fitsimage=f'{model_cube_name}', imagename=f'{cube_name}',
               overwrite=True)
            
    # Regrid cube
    if not is_regrid:
        template = obs.data['cube']['imagename']
        cube_regrid = cube_name.with_suffix('.interp.image')
        imregrid(f'{cube_name}', template=f"{template}",
                 output=f'{cube_regrid}', asvelocity=True, overwrite=True)
    else:
        cube_regrid = cube_name
    model_cube = SpectralCube.read(cube_regrid)
    model_cube = model_cube.with_spectral_unit(u.km/u.s,
                                               velocity_convention='radio')
        
    # Get pv maps from cube
    model_pvs = {}
    for label, data in obs.data['pv_data'].items():
        length, width, angle = data['path']
        if save_products:
            filename = model_cube_name.with_suffix(f'.regrid.pv_{label}.fits')
        else:
            filename = None
        model_pv = get_pvmap_from_slit(model_cube, obs.position,
                                       length, width, angle,
                                       recenter=True, filename=filename)
        # Check axes
        xunit = u.Unit(model_pv.header['CUNIT1'])
        yunit = u.Unit(model_pv.header['CUNIT2'])
        xdir = np.sign(float(model_pv.header['CDELT1']))
        ydir = np.sign(float(model_pv.header['CDELT2']))
        if data['axes_units'][0] != xunit:
            raise ValueError('PV X-units do not match')
        elif data['axes_units'][1] != yunit:
            raise ValueError('PV Y-units do not match')
        if data['axes_directions'][0] != xdir:
            raise ValueError('PV X-directions do not match')
        elif data['axes_directions'][1] != ydir:
            raise ValueError('PV Y-directions do not match')

        # Pass
        model_pv.data[np.isnan(model_pv.data)] = 0.
        model_pvs[label] = model_pv

    # Get max map
    if get_max_map:
        model_max = np.ma.masked_invalid(model_cube.argmax_world(axis=0).value)
        model_max = np.ma.fix_invalid(model_max, fill_value=np.nan).data
        if save_products:
            hdu = fits.PrimaryHDU(data=model_max,
                                  header=model_cube.wcs.sub(2).to_header())
            hdu.header['BUNIT'] = f'{model_cube.unit:fits}'
            hdu.writeto(model_cube_name.with_suffix('.regrid.max_map.fits'))
    else:
        model_max = None

    return model_pvs, model_max

if __name__ == '__main__':
    ncube = np.prod([len(val) for val in phys_pars.values()])
    npv = np.prod([len(val) for val in pv_pars.values()])

    for i, physvals in enumerate(product(*phys_pars.values())):
        print(f'<<<<< Make a Cube ({i+1} / {ncube}) >>>>>')
        pars = dict(zip(phys_pars.keys(), physvals))
        cubename = normalize_name(source['object'], **pars)
        pars.update(source)
        pars.update(obs_pars)

        # Separate by disk PA
        modeldir = basedir / f"models_PA{pars['pa']}"
        modeldir.mkdir(exist_ok=True)
        cubename = modeldir / cubename
        if cubename.exists():
            print('Model already calculated, skipping')
            continue

        for j, pvvals in enumerate(product(*pv_pars.values())):
            print(f'<<< Make a PV ({j+1} / {npv}) >>>')
            pvdict = dict(zip(pv_pars.keys(), pvvals))
            pvname = modeldir / normalize_name(cubename.stem, **pvdict)
            pars.update(pvdict)

            make_cube(pars, fname_cubein)

            # Rename files
            print(f'Moving files to {modeldir}')
            pvfiles = list(basedir.glob('*PV*.fits'))
            if len(pvfiles) > 1:
                raise ValueError('Too many pv maps')
            pvfiles[0].rename(pvname)
            cubefiles = list(basedir.glob('*.fits'))
            if len(cubefiles) > 1:
                raise ValueError('Too many cubes')
            cubefiles[0].rename(cubename)

    print('\n\007\007')
    print(f'\n\n\n----------\n{sys.argv[0]} has been done.\n\n\n')


