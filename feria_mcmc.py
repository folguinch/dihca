#!/bin/python3
from itertools import product
from pathlib import Path
from string import Template
import sys
import subprocess
import math

import numpy as np

basedir = Path('./')
fname_cubein = Path('./feria.in')
fname_exec = '../feria'

source = {'object': 'G336',
          'ra': '16h35m09.261s',
          'dec': '-48d46m47.66s',
          'vsys': '-47.2'}

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

def make_cube(pars, output, template=Path('.configs/templates/template.in')):
    if pars['rin'] == 'CB':
        pars['rin'] = pars['rcb']
    template = Template(template.read_text())
    output.write_text(template.substitute(**pars))
    subprocess.call(f'{fname_exec} < {output}', shell = True)

def normalize_name(name, **pars):
    return f'{name}_' + '_'.join(f'{k}{v}' for k, v in pars.items()) + '.fits'


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


