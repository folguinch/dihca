#!/bin/python3
from typing import Dict, Tuple, List
from configparser import ConfigParser, ExtendedInterpolation
from itertools import product
from pathlib import Path
from string import Template
import sys
import subprocess
import math
import warnings
warnings.filterwarnings('ignore')

from astropy.coordinates import SkyCoord
from astropy.io import fits
from casatasks import importfits, imregrid
from line_little_helper.molecule import Molecule
from line_little_helper.pvmap_extractor import get_pvmap_from_slit
#from pvextractor import PathFromCenter, extract_pv_slice
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import binary_dilation
#from scipy.spatial import QhullError
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
                 #section: str,
                 #line: str,
                 #restfreq: u.Quantity,
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
        #cube.update(aux)
        self.obs_pars.update(cube_beam)
        self.data = {'cube': cube}

        # Source pv
        if 'pv_rms' in self.config['data']:
            pv_disk, pv_out = self.get_pv_pars()
            self.data['pv_disk'] = pv_disk
            self.data['pv_out'] = pv_out

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

        # Get axes
        #ra, dec, vel = cube_axes(cube)
        
        # Create masked data
        rms = self.config['data']['cube_rms'].split()
        rms = float(rms[0]) * u.Unit(rms[1])
        nsigma = self.config.getfloat('data', 'cube_nsigma', fallback=nsigma)
        #dilate = self.config.getint('data', 'cube_dilate', fallback=dilate)
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
        #self.data['ra'] = ra
        #self.data['dec'] = dec
        #self.data['vel'] = vel - vlsr

        # Store beam in obs params
        beam_pars = {'bmaj': f'{beam.major.to(u.arcsec).value}',
                     'bmin': f'{beam.minor.to(u.arcsec).value}',
                     'bpa': f'{beam.pa.to(u.deg).value}'}

        return cube_pars, beam_pars

    def get_pv_pars(self) -> Tuple[Dict]:
        """Load pv data."""
        # Open maps
        cube = SpectralCube.read(self.data['cube']['cubename'])
        pv_disk_name = self.data['cube']['imagename'].with_suffix(
            '.pv_disk.fits')
        pv_out_name = self.data['cube']['imagename'].with_suffix('.pv_out.fits')
        length = u.Quantity(self.config.get('data', 'pv_length'))
        width = u.Quantity(self.config.get('data', 'pv_width'))
        if not pv_disk_name.exists():
            angle = u.Quantity(self.config.get('info', 'pa_disk'))
            pv_disk = get_pvmap_from_slit(cube, self.position,
                                          length, width, angle,
                                          recenter=True)
            pv_disk.writeto(pv_disk_name)
        if not pv_out_name.exists():
            angle = u.Quantity(self.config.get('info', 'pa_out'))
            pv_out = get_pvmap_from_slit(cube, self.position,
                                         length, width, angle,
                                         recenter=True)
            pv_out.writeto(pv_out_name)
        #pv_disk = self.config['data']['pvmap_disk']
        #pv_out = self.config['data']['pvmap_out']
        pv_disk = fits.open(pv_disk_name)[0]
        pv_out = fits.open(pv_out_name)[0]
        bunit = u.Unit(pv_disk.header['BUNIT'])

        # PV rms
        rms = u.Quantity(self.config['data']['pv_rms'])
        nsigma = self.config.getfloat('data', 'pv_nsigma ', fallback=3)
        #dilate = self.config.getfloat('data', 'pv_nsigma ', fallback=5)
        rms = rms.to(bunit)

        # Masks
        mask_disk = pv_disk.data * bunit >= nsigma * rms
        mask_out = pv_out.data * bunit >= nsigma * rms
        #mask_disk = binary_dilation(mask_disk, iterations=dilate)
        #mask_out = binary_dilation(mask_out, iterations=dilate)
        mask_disk, dilate_disk = proportional_dilation(mask_disk)
        mask_out, dilate_out = proportional_dilation(mask_out)

        # Store data
        data_disk = {
            #'pv_header': pv_disk.header,
            'data': np.ma.array(pv_disk.data / np.nanmax(pv_disk.data),
                                mask=~mask_disk),
            'axes': imtools.get_coord_axes(pv_disk),
            'rms': rms.value / np.nanmax(pv_disk.data),
        }
        data_out = {
            #'pv_header': pv_out.header,
            'data': np.ma.array(pv_out.data / np.nanmax(pv_out.data),
                                mask=~mask_out),
            'axes': imtools.get_coord_axes(pv_out),
            'rms': rms.value / np.nanmax(pv_out.data),
        }
        
        return data_disk, data_out

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
                 template: Path = TEMPLATE) -> Tuple[Path, List[Path]]:
        template = Template(template.read_text())
        outcube = output / self.get_cubename()
        infile = outcube.with_suffix('.in')
        params = {key: f'{val}' for key, val in self.pars.items()}
        params = params | obspars.source | obspars.obs_pars
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
        #model_cube = SpectralCube.read(model_cube_name)
        #model_cube = model_cube.with_spectral_unit(u.km/u.s,
        #                                           velocity_convention='radio')

        # Convert to CASA
        cube_name = model_cube_name.with_suffix('.image')
        importfits(fitsimage=f'{model_cube_name}', imagename=f'{cube_name}',
                   overwrite=True)
            
        # Regrid cube
        template = obs.data['cube']['imagename']
        cube_regrid = cube_name.with_suffix('.interp.image')
        imregrid(f'{cube_name}', template=f"{template}",
                 output=f'{cube_regrid}', asvelocity=True, overwrite=True)
        model_cube = SpectralCube.read(cube_regrid)
        model_cube = model_cube.with_spectral_unit(u.km/u.s,
                                                   velocity_convention='radio')
        
        # Get pv maps from cube
        length = u.Quantity(obs.config.get('data', 'pv_length'))
        width = u.Quantity(obs.config.get('data', 'pv_width'))
        angle_disk = u.Quantity(obs.config.get('info', 'pa_disk'))
        angle_out = u.Quantity(obs.config.get('info', 'pa_out'))
        model_pv_disk = get_pvmap_from_slit(model_cube, obs.position,
                                            length, width, angle_disk,
                                            recenter=True)
        model_pv_disk.data[np.isnan(model_pv_disk.data)] = 0.
        #model_pv_disk.data[obs.data['pv_disk']['data'].mask] = 0.
        #model_pv_disk.writeto(model_cube_name.with_suffix('.regrid.pv_disk.fits'))
        model_pv_out = get_pvmap_from_slit(model_cube, obs.position,
                                           length, width, angle_out,
                                           recenter=True)
        model_pv_out.data[np.isnan(model_pv_out.data)] = 0.
        #model_pv_out.data[obs.data['pv_out']['data'].mask] = 0.
        #model_pv_out.writeto(model_cube_name.with_suffix('.regrid.pv_out.fits'))

        # Get max map
        model_max = np.ma.masked_invalid(model_cube.argmax_world(axis=0).value)
        model_max = np.ma.fix_invalid(model_max, fill_value=0.0).data
        #hdu = fits.PrimaryHDU(data=model_max,
        #                      header=model_cube.wcs.sub(2).to_header())
        #hdu.writeto(model_cube_name.with_suffix('.regrid.max_map.fits'))

        #model_pv_disk = get_pvmap_from_slit(model_cube, obs.position,
        #                                    length, width, angle_disk,
        #                                    recenter=True)
        #model_pv_disk.writeto(model_cube_name.with_suffix('.pv_disk.fits'))

        ## Max map
        #model_max_map = model_cube.max(axis=0)
        #model_max_map = array_to_hdu(model_max_map, model_cube)

        ## Interpolate disk pv
        #xval, yval = imtools.get_coord_axes(model_pv_disk)
        #print(xval, yval)
        #xunit, yunit = xval.unit, yval.unit
        #xval, yval = np.meshgrid(xval.value, yval.value)
        #interp = LinearNDInterpolator(list(zip(xval.flatten(), yval.flatten())),
        #                              model_pv_disk.data.flatten())

        ## Evaluate
        #new_xval, new_yval = np.meshgrid(*obs.data['pv_disk']['axes'])
        #print(new_xval, new_yval)
        #if new_xval.unit.is_equivalent(xunit):
        #    new_xval = new_xval.to(xunit).value
        #else:
        #    raise ValueError
        #if new_yval.unit.is_equivalent(yunit):
        #    new_yval = new_yval.to(yunit).value
        #else:
        #    ValueError
        #model_pv_disk = interp(new_xval, new_yval)
        #model_pv_disk = model_pv_disk / np.nanmax(model_pv_disk)
        #hdu = fits.PrimaryHDU(data=model_pv_disk,
        #                      header=obs.data['pv_disk']['pv_header'])
        #hdu.writeto(model_cube_name.with_suffix('.interp.norm.pv_disk.fits'))

        # Chi
        sigma_disk = np.repeat(obs.data['pv_disk']['rms'],
                               np.sum(~obs.data['pv_disk']['data'].mask))
        term1_disk = -0.5 * np.ma.sum(np.log(2 * np.pi * sigma_disk**2))
        norm_model_pv_disk = model_pv_disk.data / np.nanmax(model_pv_disk.data)
        chi2_disk = (obs.data['pv_disk']['data'] - norm_model_pv_disk )**2 
        chi2_disk = chi2_disk / obs.data['pv_disk']['rms']**2
        term2_disk = -0.5 * np.ma.sum(chi2_disk)
        sigma_out = np.repeat(obs.data['pv_out']['rms'],
                              np.sum(~obs.data['pv_out']['data'].mask))
        term1_out = -0.5 * np.ma.sum(np.log(2 * np.pi * sigma_out**2))
        norm_model_pv_out = model_pv_out.data / np.nanmax(model_pv_out.data)
        chi2_out = (obs.data['pv_out']['data'] - norm_model_pv_out )**2 
        chi2_out = chi2_out / obs.data['pv_out']['rms']**2
        term2_out = -0.5 * np.ma.sum(chi2_out)
        #max_max = np.nanmax(obs.data['cube']['max_map'])
        sigma_max = np.repeat(obs.data['cube']['sigma_vel'],
                              np.sum(~obs.data['cube']['max_map'].mask))
        term1_max = -0.5 * np.ma.sum(np.log(2 * np.pi * sigma_max**2))
        chi2_max = (obs.data['cube']['max_map'] - model_max)**2 
        chi2_max = chi2_max / obs.data['cube']['sigma_vel']**2
        term2_max = -0.5 * np.ma.sum(chi2_max)

        # Save model cube
        #spcube = SpectralCube(data=new_cube, wcs=obs.data['wcs'])
        #spcube.write(model_cube.with_suffix('.interp.fits'))
        total = ((term1_disk + term2_disk) * 0.4 +
                 (term1_out + term2_out) * 0.4 +
                 (term1_max + term2_max) * 0.2)
     
        return total

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

#basedir = Path('./')
#fname_cubein = Path('./feria.in')
#fname_exec = '../feria'

#source = {'object': 'G336',
#          'ra': '16h35m09.261s',
#          'dec': '-48d46m47.66s',
#          'vsys': '-47.2'}

#obs_pars = {'line': 'CH3OH',
#            'restfreq': '233.795666',
#            'pixsize': '0.004',
#            'velres': '0.1'}
#
#phys_pars = {'distance': ['3100'], # pc
#             'mass': ['5', '8', '10', '12', '15'], # msun
#             'rcb': ['100', '200.', '250', '300.', '350', '400.', '450', '500.'], # au
#             'incl': ['50.', '55.', '60.', '65.', '70.', '75', '80.', '85', '90'],
#             #'pa': ['125'],
#             'pa': ['125', '130', '135', '140', '145', '150'],
#             'rot': ['1'],
#             'rout': ['700.', '800.', '900.', '1000'],
#             'rin': ['CB'],
#             'ireheight': ['0.'],
#             'ireflare': ['30'],
#             'irenprof': ['-1.5'],
#             'iretprof': ['-0.4'],
#             'kepheight': ['0.5'],
#             'kepflare': ['30'],
#             'kepnprof': ['-1.5'],
#             'keptprof': ['-0.4'],
#             'cbdens': ['1e-2'],
#             'cbtemp': ['50'],
#             'lw': ['2.0', '4.0', '6.0'],
#             'bmaj': ['0.0692'],
#             'bmin': ['0.0517'],
#             'bpa': ['-29.07']
#             #'bmaj': ['0'],
#             #'bmin': ['0'],
#             #'bpa': ['0']
#             }
#
#pv_pars = {'pvpa': ['125'],
#           'pvra': ['0.0'],
#           'pvdec': ['0.0']}



####################


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


