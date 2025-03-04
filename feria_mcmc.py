#!/bin/python3
from configparser import ConfigParser
from itertools import product
from pathlib import Path
from string import Template
import sys
import subprocess
import math

import astropy.units as u
import numpy as np

from .common_paths import CONFIGS

FERIA = Path('~/clones/feria/feria').expanduser()
TEMPLATE = CONFIGS / 'templates/template.in'

class Observation:
    source: Dict
    obs_pars: Dict
    data: Dict

    def __init__(self,
                 config: Path,
                 section: str,
                 line: str,
                 restfreq: u.Quantity,
                 pixsize: str = '0.004',
                 velres: str = '0.1'):
        parser = ConfigParser()
        parser.read(config)
        distance = parser[section]['distance'].split()
        distance = float(distance[0]) * u.Unit(distance[1])
        vlsr = parser[section]['vlsr'].split()
        vlsr = float(vlsr[0]) * u.Unit(vlsr[1])
        self.source = {
            'object' = parser[section]['name'],
            'ra' = parser[section]['ra'],
            'dec' = parser[section]['dec'],
            'distance' = f'{distance.to(u.pc).value}',
        }
        self.obs_pars = {
            'line': line,
            'restfreq': f'{restfreq.to(u.GHz).value}'
            'pixsize': pixsize,
            'velres': velres,
        }

        self.data['cube'] = Path(parser[section]['file'])
        rms = parser[section]['rms'].split()
        rms = float(rms[0]) * u.Unit(rms[1])
        masked_cube, unit, beam, ra, dec, vel = self.get_cube_pars(rms,
                                                                   restfreq)
        self.data['rms'] = rms.to(unit)
        self.data['masked_cube'] = masked_cube
        self.data['beam'] = beam
        self.data['ra'] = ra
        self.data['dec'] = dec
        self.data['vel'] = vel - vlsr

        # Store beam in obs params
        self.obs_pars['bmaj'] = f'{beam.major.to(u.arcsec).value}'
        self.obs_pars['bmin'] = f'{beam.minor.to(u.arcsec).value}'
        self.obs_pars['bpa'] = f'{beam.pa.to(u.deg).value}'
        

    def get_cube_pars(self,
                      rms: str,
                      restfreq: u.Quantity,
                      nsigma: float = 5):
        # Open cube
        cube = SpectralCube.read(self['cube'])

        # Change to velocity
        cube = cube.with_spectral_unit(u.km/u.s,
                                       velocity_convention='radio',
                                       rest_value=restfreq)
        unit = cube.unit
        beam = cube.beam

        # Get axes
        ra, dec, vel = cube_axes(cube)
        
        # Create masked data
        data = cube.unmasked_data[:,:,:]
        mask = data >= nsigma * rms
        mask = binary_dilation(mask, iterations=5)
        data = np.ma.array(data.value, mask=~mask)
        data = np.ma.masked_invalid(data)

        return data, unit, beam, ra, dec, vel

class Model:
    pars: Dict

    def __init__(self, **params):
        self.pars = params
        if self.pars['rin'] == 'CB':
            self.pars['rin'] = self.pars['rcb']

    def __call__(self,
                 output: Path,
                 obspars: Observation,
                 template: Path = TEMPLATE) -> Tuple[Path]:
        template = Template(template.read_text())
        outcube = output / self.get_cubename()
        infile = outcube.with_suffix('.in')
        params = {key: f'{val}' for key, val in self.pars.items()}
        params = params | obspars.source | obspars.obs_pars
        infile.write_text(template.substitute(output=f'{outcube}',
                                              **params))
        if outcube.is_file():
            cube = outcube
            pvmaps = list(output.glob(cube.name + '*PV*.fits'))
        else:
            in_parent_in = list(output.glob('*.fits'))
            subprocess.call(f'{FERIA} < {output}', shell = True)
            in_parent_out = list(output.glob('*.fits'))
            
            pvmaps = []
            cube = None
            for aux in filter(lambda x: x not in in_parent_in, in_parent_out):
                if 'PV' in aux.name:
                    pvmaps.append(aux)
                elif cube is None:
                    cube = aux
                else:
                    raise ValueError(f'Directory {aux.parent} not empty')

        return cube, pvmaps

    def get_cubename(self):
        cube = ['cube',
                '_'.join(f'{k}{v}' for k, v in self.pars.items())]
        return '_'.join(cube) + '.fits'

def cube_axes(cube):
    nx = cube.shape[2]
    ny = cube.shape[1]
    wcs = cube.wcs.celestial
    ra = wcs.wcs_pix2world(np.arange(nx), np.zeros(nx), 0)[0] * u.deg
    dec = wcs.wcs_pix2world(np.zeros(ny), np.arange(ny), 0)[1] * u.deg
    vel = cube.spectral_axis

    return ra, dec, vel

def log_posterior(params: Dict, **kwargs):
    """Calculate the posterior probability.

    Used keyword arguments are:
    
    - `fixed_params`: a dictionary with fixed parameters.
    - `ranges`: a dictionary with parameter ranges.
    - `obs`: an `Observation` object.
    - `outdir`: a `Path` for the output directory.

    The `params` are concatenated with `fixed_params` to generate a model.
    """
    model_dir = kwargs['outdir']
    def log_like_f(parms, obs, model_dir):
        # Compute model
        model = Model(params)
        model_cube, _ = model(model_dir, obs)

        # Open output cube and interpolate
        cube = SpectralCube.read(model_cube)
        ra, dec, vel = cube_axes(cube)
        vel, dec, ra = np.meshgrid(vel, dec, ra, indexing='ij')
        outvel, outdec, outra = np.meshgrid(obs.data['vel'],
                                            obs.data['dec'],
                                            obs.data['ra'],
                                            indexing='ij')
        interp = LinearNDInterpolator(list(zip(vel.flatten(),
                                               dec.flatten(),
                                               ra.flatten())),
                                      cube.unmasked_data[:].flatten(),
                                      fill_value=0.)
        new_cube = interp(outvel, outdec, outra)

        # Normalize to the peak observed intensity
        ind = np.unravel_index(np.nanargmax(obs.data['masked_cube']),
                               obs.data['masked_cube'].shape)
        new_cube = new_cube / new_cube[ind] * obs.data['masked_cube'][ind]
    
        # Chi
        sigma = obs.data['masked_cube'] * 0.1
        sigma = np.sqrt(sigma**2 + obs.data['rms'].value**2)
        term1 = -0.5 * np.ma.sum(np.log(2 * np.pi * sigma**2))
        chi2 = (obs.data['masked_cube'] - new_cube)**2 / sigma**2
        term2 = -0.5 * np.ma.sum(chi2)

        # Remove model cube
     
        return term1 + term2

    def log_prior(params, ranges):
        for key, val in ranges.items():
            if params[key] < val[0] or params[key] > val[1]:
                return -np.inf
        if params['rin'] > params['rcb'] or params['rout'] <= params['rcb']:
            return -np.inf
        return 0

    if log_prior(params | kwargs['fixed_params'], kwargs['ranges']) == 0:
        return log_like_f(params | kwargs['fixed_params'], kwargs['obs'],
                          model_dir)
    else:
        return -np.inf


#basedir = Path('./')
#fname_cubein = Path('./feria.in')
#fname_exec = '../feria'

#source = {'object': 'G336',
#          'ra': '16h35m09.261s',
#          'dec': '-48d46m47.66s',
#          'vsys': '-47.2'}

obs_pars = {'line': 'CH3OH',
            'restfreq': '233.795666',
            'pixsize': '0.004',
            'velres': '0.1'}

phys_pars = {'distance': ['3100'], # pc
             'mass': ['5', '8', '10', '12', '15'], # msun
             'rcb': ['100', '200.', '250', '300.', '350', '400.', '450', '500.'], # au
             'incl': ['50.', '55.', '60.', '65.', '70.', '75', '80.', '85', '90'],
             #'pa': ['125'],
             'pa': ['125', '130', '135', '140', '145', '150'],
             'rot': ['1'],
             'rout': ['700.', '800.', '900.', '1000'],
             'rin': ['CB'],
             'ireheight': ['0.'],
             'ireflare': ['30'],
             'irenprof': ['-1.5'],
             'iretprof': ['-0.4'],
             'kepheight': ['0.5'],
             'kepflare': ['30'],
             'kepnprof': ['-1.5'],
             'keptprof': ['-0.4'],
             'cbdens': ['1e-2'],
             'cbtemp': ['50'],
             'lw': ['2.0', '4.0', '6.0'],
             'bmaj': ['0.0692'],
             'bmin': ['0.0517'],
             'bpa': ['-29.07']
             #'bmaj': ['0'],
             #'bmin': ['0'],
             #'bpa': ['0']
             }

pv_pars = {'pvpa': ['125'],
           'pvra': ['0.0'],
           'pvdec': ['0.0']}



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


