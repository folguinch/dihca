from typing import Dict, Sequence
from configparser import ConfigParser
from pathlib import Path
import sys

from astro_source.source import Source
#from line_little_helper.scripts.cassis_rebuild_map import rebuild_map
from line_little_helper.auto_subcube import auto_subcube
from line_little_helper.moving_moments import moving_moments
from line_little_helper.spectrum_helper import spectrum_helper
from line_little_helper.line_peak_map import line_peak_map
from line_little_helper.molecule import NoTransitionError
from line_little_helper.pvmap_extractor import pvmap_extractor
from line_little_helper.pvmap_fitter import pvmap_fitter
from line_little_helper.subcube_extractor import subcube_extractor
from line_little_helper.symmetric_moments import symmetric_moments
from line_little_helper.local_moments import local_moments
from line_little_helper.utils import normalize_qns
from line_little_helper.velocity_gradient import velocity_gradient
from tile_plotter.plotter import plotter

from common_paths import RESULTS, CONFIGS, FIGURES

# Molecules to analyze
#MOLECULES = ('CH3OH',)
MOLECULES = ('CH3OH', 'CH3CN')
#MOLECULES = ('CH3CN',)
#MOLECULES = ('c-HCOOH',)
#MOLECULES = ('HNCO',)
#MOLECULES = ('CH2(OD)CHO',)

# Source lists:
SOURCES_970 = ('G10.62-0.38', 'G11.1-0.12', 'G11.92-0.61',
               'G34.43+0.24MM2', 'G35.13-0.74', 'G5.89-0.37',
               'IRAS_181511208', 'IRAS_18182-1433', 'IRDC_182231243',
               'IRAS_181622048',
               'W33A', 'IRAS_180891732')
SOURCES_490 = ('G14.22-0.50_S', 'G24.60+0.08', 'G29.96-0.02',
               'G333.12-0.56', 'G333.23-0.06', 'G333.46-0.16',
               'G335.579-0.272', 'G335.78+0.17', 'G336.01-0.82',
               'G34.43+0.24', 'G343.12-0.06', 'G35.03+0.35_A',
               'G35.20-0.74_N', 'G351.77-0.54', 'IRAS_165623959',
               'IRAS_18337-0743', 'NGC6334I', 'NGC_6334_I_N')
WITH_LINES_PV = ('G10.62-0.38', 'G11.1-0.12', 'G11.92-0.61', 'G29.96-0.02',
                 'G333.12-0.56', 'G333.23-0.06', 'G333.46-0.16',
                 'G335.579-0.272', 'G335.78+0.17', 'G336.01-0.82',
                 'G34.43+0.24', 'G343.12-0.06', 'G35.03+0.35_A', 'G35.13-0.74',
                 'G35.20-0.74_N', 'G351.77-0.54', 'IRAS_165623959',
                 'IRAS_180891732', 'IRAS_18182-1433', 'NGC_6334_I_N', 'W33A')
WITH_K8 = ('G10.62-0.38_alma1a', 'G11.92-0.61_alma1a', 'G333.46-0.16_alma1',
           'IRAS_180891732_alma1', 'IRAS_18182-1433_alma2',
           'IRAS_18182-1433_alma3')
SOURCES = SOURCES_970 + SOURCES_490
#SOURCES = WITH_LINES_PV
#SOURCES = ('G10.62-0.38', 'NGC_6334_I_N')# 'G35.13-0.74')
#SOURCES = ('IRAS_181622048',)
#SOURCES = ('NGC6334I',)
#SOURCES = WITH_K8
#SOURCES = ('G333.23-0.06_alma3b', )

# Source-specific half widths
HWIDTHS = {
    'G11.92-0.61': {
        'hmc1': {
            'CH3OH': 16,
            'CH3CN': 25,
            },
        'hmc2': {
            'CH3OH': 12,
            'CH3CN': 12,
            },
        'hmc3': {
            'CH3OH': 12,
            'CH3CN': 12,
            },
        },
    'G29.96-0.02': 20,
    'G333.12-0.56': {
        'hmc1': {
            'CH3OH': 17,
            'CH3CN': 17,
            },
        'hmc2': {
            'CH3OH': 15,
            'CH3CN': 15,
            },
        },
    'G335.579-0.272': 20,
    'G335.78+0.17': {
        'hmc1': {
            'CH3OH': 22,
            },
        'hmc2': {
            'CH3OH': 20,
            },
        },
    'G343.12-0.06': 10,
    'IRAS_165623959': {
        'hmc1': {
            'CH3OH': 15,
            'CH3CN': 15,
            },
        'hmc2': {
            'CH3OH': 12,
            'CH3CN': 12,
            },
        },
    'IRAS_180891732': {
        'hmc1': {
            'CH3OH': 15,
            'CH3CN': 20,
            },
        'hmc2': {
            'CH3OH': 10,
            'CH3CN': 15,
            },
        },
    'NGC_6334_I_N': {
        'alma1': {
            'CH3OH': 15,
            'CH3CN': 15,
            },
        'alma2': {
            'CH3OH': 15,
            'CH3CN': 15,
            },
        'alma6': {
            'CH3OH': 20,
            'CH3CN': 20,
            },
        'alma4': {
            'CH3OH': 15,
            'CH3CN': 15,
            },
        'alma11': {
            'CH3OH': 15,
            'CH3CN': 15,
            },
        },
}

# Recommended line lists
LINE_LISTS = {
    '(13)CO': 'JPL',
    'H2CO': 'JPL',
    'SiO': 'JPL',
    'Hα': 'Recomb',
    'CH3CN': 'JPL',
    '(13)CH3CN': 'CDMS',
    'CH3OH': 'CDMS',
    '(13)CH3OH': 'CDMS',
    'CH3CHO': 'SLAIM',
    'CH3OCHO': 'SLAIM',
    'HNCO': 'CDMS',
    'SO2': 'CDMS',
    'HC3N': 'CDMS',
    'NH2CHO': 'CDMS',
    'c-HCOOH': 'CDMS',
    'CH2(OD)CHO': 'CDMS',
}

# Molecules and transitions of interest
LINE_TRANSITIONS = {
    'CH3OH': (#'4(2,3)-5(1,4)A,vt=0',       #spw0
              #'5(4,2)-6(3,3)E,vt=0',
              '18(3,15)-17(4,14)A,vt=0',
              #'10(2,9)-9(3,6)A,vt=0',      #spw1
              #'10(2,8)-9(3,7)A,vt=0',
              #'18(3,16)-17(4,13)A,vt=0',
              #'4(-2,3)-3(-1,2)E,vt=0',      #spw2
              #'5(-1,4)-4(-2,3)E,vt=0',
              #'20(-1,19)-20(-0,20)E,vt=0',
              #'8(-0,8)-7(-1,6)E,vt=0',     #spw3
              #'23(-5,18)-22(-6,17)E,vt=0',
              #'25(-3,23)-24(-4,20)E,vt=0',
              #'6(1,5)-7(2,6)--,vt=1',      # other
              #'13(3,10)-14(4,10)A,vt=2',
              #'34(-13,22)-33(-11,22)E,vt=0-vt=1',
              ),
    '(13)CH3OH': (#'10(2,8)-9(3,7)++',
                  '5(1,5)-4(1,4)++',),
    'CH3CN': (#'12(0)-11(0)',
              #'12(1)-11(1)',
              #'12(2)-11(2)',
              '12(3)-11(3)',
              #'12(4)-11(4)',
              #'12(8)-11(8)'
              ),
    'c-HCOOH': ('10(4,6)-9(4,5)',),
    '(13)CH3CN': ('13(3)-12(3)',
                  '13(4)-12(4)'),
    'CH3CHO': ('2(2,0)-3(1,3)A++,vt=2',),
    'HNCO': (#'28(1,28)-29(0,29)',
             '10(3,8)-9(3,7)',
             '10(2,9)-9(2,8)',
             '10(0,10)-9(0,9)'),
    'CH3OCHO': ('20(0,20)-19(0,19)A',
                '32(9,24)-32(8,25)E',
                '48(14,35)-47(15,32)E'),
    'SO2': ('59(14,46)-60(13,47)',
            '28(3,25)-28(2,26)',
            '99(9,91)-98(10,88)',
            '94(21,73)-95(20,76)'),
    'HC3N': ('J=24-23,l=0',
             'J=24-23,l=2e',
             'J=24-23,l=1f'),
    'NH2CHO': ('11(2,10)-10(2,9)',),
    'CH2(OD)CHO': ('59(13,46)-59(12,47)',),
}

# Saved molecules
MOL_DIR = Path('./molecules')
SAVED_MOLS = {
    'CH3OH': MOL_DIR / 'ch3oh.json',
    'CH3CN': MOL_DIR / 'ch3cn.json',
    '(13)CH3OH': MOL_DIR / '13ch3oh.json',
    '(13)CH3CN': MOL_DIR / '13ch3cn.json',
    'c-HCOOH': MOL_DIR / 'c-hcooh.json',
    'HNCO': MOL_DIR / 'hnco.json',
    'CH2(OD)CHO': MOL_DIR / 'glycolaldehyde.json',
}

def search_molecule(source, molecule, array, line_filter=None):
    data = []
    for key in src.get_data_sections():
        if 'molecules' not in src.config[key] or array not in key:
            continue
        if line_filter is not None and line_filter.lower() not in key.lower():
            continue
        molecules = src.config[key]['molecules'].split()
        if molecule in molecules:
            data.append(src.config[key])

    return data

def gen_plot_config(source, moments, template, outfile, mol=None, qns=None):
    # Open template
    if outfile.exists():
        return
    config = ConfigParser()
    config.read(template)

    # Moment sections
    for i in range(3):
        section = f'moment{i}'
        position = source.position.to_string(style='hmsdms')
        position = f'{position} {source.position.frame.name}'
        config[section]['moment'] = str(moments[i])
        config[section]['center'] = position
        config[section]['label'] = f'Moment {i}'
        if i == 0 and mol is not None:
            title = f'{mol}' if qns is None else f'{mol} ({qns})'
            config[section]['title'] = title
        if i == 1:
            # Shift data is additive
            vlsr = f'{-source.vlsr.value}'
            vlsr += ' ' + f'{source.vlsr.unit}'.replace(' ', '')
            config[section]['shift_data'] = vlsr

    # Continuum
    config['continuum']['contour'] = source.config['b6_c8_continuum']['file']

    # Write
    with open(outfile, 'w') as configfile:
        config.write(configfile)

def crop_line(source: Source,
              hmc: str,
              outdir: Path,
              array: str,
              molecules: Sequence = MOLECULES,
              qns_mol: Dict = LINE_TRANSITIONS,
              half_width: int = 20):
              #half_width: int = 30):
    """Crop a cube to extract line and add new section to source config."""
    for mol in molecules:
        configs_with_mol = search_molecule(source, mol, array)
        processed = []
        norm_mol = mol.replace('(', '').replace(')', '')
        for qns in qns_mol[mol]:
            if qns in processed:
                continue
            norm_qns = normalize_qns(qns)

            for src_cfg in configs_with_mol:
                # Config
                cube = src_cfg['file']
                new_section = src_cfg.name + f'_{norm_mol}_{norm_qns}'

                # Directories
                moldir = outdir / 'line_cubes'
                name = f'{hmc}_{norm_mol}_{norm_qns}_nchans{half_width*2}.fits'
                out_cube = moldir / name

                # Check
                if new_section in source.config or out_cube.is_file():
                    print(f'Skipping {src_cfg.name}')
                    continue
                
                # Flags
                flags = ['--vlsr', f'{source.vlsr.value}',
                         f'{source.vlsr.unit}'.replace(' ', ''),
                         '--line_lists', LINE_LISTS.get(mol, 'CDMS'),
                         '--molecule', mol,
                         '--qns', qns,
                         '--common_beam',
                         '--put_linefreq',
                         '--win_halfwidth', f'{half_width}',
                         '--spectral_axis', 'velocity',
                        ]
                if mol in SAVED_MOLS:
                    flags += ['--restore_molecule', f'{SAVED_MOLS[mol]}']
                if 'rms' in src_cfg:
                    flags += ['--rms'] + src_cfg['rms'].split()

                # Compute moments
                try:
                    print(f'Working on cube: {cube}')
                    moldir.mkdir(parents=True, exist_ok=True)
                    subcube_extractor(flags + [cube, f'{out_cube}'])
                    processed.append(qns)
                except NoTransitionError:
                    print(f'{mol} ({qns}): not in cube {cube}')
                    continue

                # Put new source config section
                source.copy_config(src_cfg.name, new_section)
                source.config[new_section]['file'] = f'{out_cube}'
                source.write()

def moments(source: Source,
            hmc: str,
            outdir: Path,
            array: str,
            molecules: Sequence[str] = MOLECULES,
            qns_mol: Dict = LINE_TRANSITIONS):
    """Calculate different types of moments."""
    half_width_def = {488: 15, 976: 10}
    for mol in molecules:
        # Find what molecules are in the source
        configs_with_mol = search_molecule(source, mol, array, line_filter=mol)
        processed = []
        norm_mol = mol.replace('(', '').replace(')', '')
        for qns in qns_mol[mol]:
            if qns in processed:
                continue

            for src_cfg in configs_with_mol:
                # Some values
                cube = src_cfg['file']
                norm_qns = normalize_qns(qns)
                chanwidth = int(src_cfg['chan_width'].split()[0])
                half_width = HWIDTHS.get(source.name, half_width_def[chanwidth])
                try:
                    half_width = half_width[hmc][mol]
                except TypeError:
                    pass
                
                # Moment flags
                flags = ['--vlsr', f'{source.vlsr.value}',
                         f'{source.vlsr.unit}'.replace(' ', ''),
                         '--line_lists', LINE_LISTS.get(mol, 'CDMS'),
                         '--molecule', mol,
                         '--qns', qns,
                         '--nsigma', '5',
                        ]
                if mol in SAVED_MOLS:
                    flags += ['--restore_molecule', f'{SAVED_MOLS[mol]}']
                if 'rms' in src_cfg:
                    flags += ['--rms'] + src_cfg['rms'].split()
                
                # Compute moments
                try:
                    name = (f'{norm_mol}_{norm_qns}_'
                            f'width{half_width*2}')
                    moldir = outdir / f'{hmc}_moments'
                    moldir.mkdir(parents=True, exist_ok=True)
                    # Symmetric
                    print('-' * 20 + 'Symmetric' + '-' * 20)
                    filenames = symmetric_moments(
                        flags + ['--win_halfwidth', f'{half_width}',
                                 cube, str(moldir / name), '0', '1', '2'])
                    # Local
                    print('-' * 20 + 'Local' + '-' * 20)
                    local_moments([cube, str(moldir / name),
                                   '--win_halfwidth', f'{half_width}',
                                   '--moments', '1', '2'] + flags)
                    # Moving
                    print('-' * 20 + 'Moving' + '-' * 20)
                    moving_moments(['20', f'{moldir}', cube,
                                    '--savemasks'] + flags)
                    processed.append(qns)
                except NoTransitionError:
                    print(f'{mol} ({qns}): not in cube {cube}')
                    continue

def moment1_gradients(source: Source,
                      hmc: str,
                      outdir: Path,
                      array: str,
                      ):
    """Calculate the velocity gradient from moment 1 maps."""
    #position = source.position.to_string(style='hmsdms')
    #flags = [--coordinate] + position.split()
    flags = ['--source', f'{source.config_file}']
    moldir = outdir / f'{hmc}_moments'
    files = list(moldir.glob('*moment1.fits'))
    files += list(moldir.glob('*moment1_dilate[0-9].fits'))
    files += list(moldir.glob('*moment1_dilate10.fits'))
    for mom1 in files:
        print('Calculating gradient on ', mom1)
        output = mom1.with_name(mom1.stem)
        stats = velocity_gradient([f'{mom1}', f'{output}'] + flags)
        stats_file = mom1.with_suffix('.gradient.txt')
        lines = [
            f'direction: {stats[0]} +/- {stats[1]}',
            f'direction_median: {stats[2]}'
            ]
        stats_file.write_text('\n'.join(lines))

def pv_extractor(pvconfig: Path,
                 source: Source,
                 outdir: Path,
                 recenter: bool = False):
    """Extract PV map"""
    results = outdir / f'{pvconfig.stem}.fits'
    flags = ['--pvconfig', f'{pvconfig}', '--output', f'{results}',
             '--estimate_error', '--source', f'{source.config_file}',
             '--common_beam']
    if recenter:
        flags += ['--recenter']

    return pvmap_extractor(flags)
    
def pv_maps(source: Source,
            hmc: str,
            outdir: Path,
            array: str):
    """Calculate different types of PV maps."""
    # Search for configs
    rotation = (source.config_file.parent /
                'pvmaps' /
                f'{source.name}_{hmc}_rotation.cfg')
    output = outdir / f'{hmc}_pvmaps'
    output.mkdir(parents=True, exist_ok=True)
    if rotation.is_file():
        pv_rotation(rotation, source, output)

def pv_rotation(pvconfig: Path,
                source: Source,
                outdir: Path):
    """Calculates and model rotation PV maps."""
    pvmaps = pv_extractor(pvconfig, source, outdir, recenter=True)

    # Fit gradient
    #plotname = figures / source.name / array / 'pvmaps_rotation.png'
    #flags = ['--bunit', 'mJy/beam', '--outdir', f'{pvout}', '--plotname',
    #         f'{plotname}', '--function', 'plot']
    #pvmap_fitter(list(map(str, pvmaps)) + flags)

def split_moments(source, outdir, configs, figures, array,
                  #molecules=['SiO', '(13)CO'],
                  molecules=['CH3OH'],
                  # SiO 480kHz
                  #chansep=5, chanwidth=6, bandwidth=80):
                  # CH3OH 900kHz
                  chansep=3, chanwidth=3, bandwidth=10):
                  # CH3OH 480kHz
                  #chansep=3, chanwidth=4, bandwidth=20):
    # Calculate split moments
    for mol in molecules:
        configs_with_mol = search_molecule(source, mol, array)
        norm_mol = mol.replace('(', '').replace(')', '')
        for config in configs_with_mol:
            cube = config['file']
            flags = ['--vlsr', f'{source.vlsr.value}',
                     f'{source.vlsr.unit}'.replace(' ', ''),
                     '--line_lists', LINE_LISTS.get(mol, 'CDMS'),
                     '--savemasks',
                     '--split', f'{chansep}', f'{chanwidth}',
                     '--molecule', mol]
            if mol in SAVED_MOLS:
                flags += ['--restore_molecule', f'{SAVED_MOLS[mol]}']
            if 'rms' in config:
                flags += ['--rms'] + config['rms'].split()
            dir_suff = f'{mol}_split{chansep}_{chanwidth}'
            moldir = (outdir / norm_mol /
                      f'split{chansep}_width{chanwidth}_range{bandwidth}')
            moving_moments(flags + [f'{bandwidth}', f'{moldir}', cube])

def peak_maps(source,
              outdir,
              configs,
              figures,
              array,
              molecules=['CH3OH'],
              #  qns_mol=line_transitions,
              qns_mol={'CH3OH':['18(3,15)-17(4,14)A,vt=0']},
              half_width=10):
    for mol in molecules:
        configs_with_mol = search_molecule(source, mol, array)
        processed = []
        norm_mol = mol.replace('(', '').replace(')', '')
        for qns in qns_mol[mol]:
            if qns in processed:
                continue

            for src_cfg in configs_with_mol:
                cube = src_cfg['file']
                # Plot config
                norm_qns = normalize_qns(qns)
                
                # Moment flags
                flags = ['--vlsr', f'{source.vlsr.value}',
                         f'{source.vlsr.unit}'.replace(' ', ''),
                         '--line_lists', LINE_LISTS.get(mol, 'CDMS'),
                         '--molecule', mol,
                         '--qns', qns,
                         '--nsigma', '5',
                         '--win_halfwidth', f'{half_width}',
                         '--moments', '0', '1',
                         '--nlinewidth', '2',
                         '--use_dask',
                         '--common_beam',
                        ]
                if mol in SAVED_MOLS:
                    flags += ['--restore_molecule', f'{SAVED_MOLS[mol]}']
                if 'rms' in src_cfg:
                    flags += ['--rms'] + src_cfg['rms'].split()
                
                # Compute moments
                try:
                    name = f'{norm_mol}_{norm_qns}'
                    moldir = outdir / norm_mol
                    moldir.mkdir(parents=True, exist_ok=True)
                    filenames = line_peak_map(flags + [cube, f'{moldir}'])
                    processed.append(qns)
                except NoTransitionError:
                    print(f'{mol} ({qns}): not in cube {cube}')
                    continue

def peak_spectrum(src: Source,
                  hmc: str,
                  outdir: Path,
                  array: str,
                  molecules: Sequence[str] = MOLECULES,
                  qns_mol: Dict = LINE_TRANSITIONS):
    """Extract average peak spectrum."""
    for mol in molecules:
        # Find what molecules are in the source
        configs_with_mol = search_molecule(src, mol, array)
        processed = []
        norm_mol = mol.replace('(', '').replace(')', '')
        for qns in qns_mol[mol]:
            if qns in processed:
                continue

            for src_cfg in configs_with_mol:
                # Some values
                cube = src_cfg['file']
                spectra = outdir / 'spectra'
                spectra.mkdir(exist_ok=True)

                # Falgs
                flags = ['--vlsr', f'{src.vlsr.value}',
                         f'{src.vlsr.unit}'.replace(' ', ''),
                         '--radius', '0.05', 'arcsec',
                         '--coordinate',
                         f"{src_cfg['ra']} {src_cfg['dec']} icrs",
                         '--rest',
                         '--vv', 'debug_pipeline.log',
                         '--outdir', f'{spectra}'
                        ]
                if 'rms' in src_cfg:
                    flags += ['--rms'] + src_cfg['rms'].split()
                
                spectrum_helper([cube] + flags)
                processed.append(qns)

if __name__ == '__main__':
    # Steps
    steps = {
        1: crop_line,
        2: moments,
        3: moment1_gradients,
        4: pv_maps,
        5: peak_spectrum,
    #    2: split_moments,
    #    4: extract_cassis,
    #    5: cassis_to_fits,
    #    7: peak_maps,
    #    8: line_cube,
    }
    #skip = [3, 4]
    skip = [1, 2, 3, 4]
    #skip = [4]
    #skip = []
    array = 'c5c8'

    # Read sources from command line
    sources = SOURCES

    # Iterate over source config files
    config_dir = CONFIGS / 'extracted'
    for source in sources:
        print('Source: ', source)
        for config in config_dir.glob(f'{source}*.cfg'):
            # Open source
            src = Source(config_file=config)
            outdir = RESULTS / src.name / array / 'per_hot_core'
            hmc = config.stem.split('_')[-1]

            # Run steps
            for n, func in steps.items():
                if n in skip:
                    continue
                print(f'Step {n}')
                func(src, hmc, outdir, array)
                print("=" * 80)
