from typing import Dict, Sequence
from configparser import ConfigParser
from pathlib import Path
import sys

from astro_source.source import Source
#from line_little_helper.scripts.cassis_rebuild_map import rebuild_map
from line_little_helper.auto_subcube import auto_subcube
from line_little_helper.moving_moments import moving_moments
#from line_little_helper.scripts.spectrum_helper import spectrum_helper
from line_little_helper.line_peak_map import line_peak_map
from line_little_helper.molecule import NoTransitionError
from line_little_helper.pvmap_extractor import pvmap_extractor
from line_little_helper.pvmap_fitter import pvmap_fitter
from line_little_helper.subcube_extractor import subcube_extractor
from line_little_helper.symmetric_moments import symmetric_moments
from line_little_helper.utils import normalize_qns
from tile_plotter.plotter import plotter

from common_paths import results, configs, figures

# Source lists:
SOURCES_970 = ('G10.62-0.38', 'G11.1-0.12', 'G11.92-0.61',
               'G34.43+0.24MM2', 'G35.13-0.74', 'G5.89-0.37',
               'IRAS_181511208', 'IRAS_18182-1433', 'IRDC_182231243',
               'W33A', 'IRAS_180891732')
SOURCES_490 = ('G14.22-0.50_S', 'G24.60+0.08', 'G29.96-0.02',
               'G333.12-0.56', 'G333.23-0.06', 'G333.46-0.16',
               'G335.579-0.272', 'G335.78+0.17', 'G336.01-0.82',
               'G34.43+0.24', 'G343.12-0.06', 'G35.03+0.35_A',
               'G35.20-0.74_N', 'G351.77-0.54', 'IRAS_165623959',
               'IRAS_18337-0743', 'NGC6334I', 'NGC_6334_I_N')
SOURCES = SOURCES_970 + SOURCES_490

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
}

# Molecules and transitions of interest
LINE_TRANSITIONS = {
    'CH3OH': ('4(2,3)-5(1,4)A,vt=0',       #spw0
              '5(4,2)-6(3,3)E,vt=0',
              '18(3,15)-17(4,14)A,vt=0',
              '10(2,9)-9(3,6)A,vt=0',      #spw1
              '10(2,8)-9(3,7)A,vt=0',
              '18(3,16)-17(4,13)A,vt=0',
              '4(-2,3)-3(-1,2)E,vt=0',      #spw2
              '5(-1,4)-4(-2,3)E,vt=0',
              '20(-1,19)-20(-0,20)E,vt=0',
              '8(-0,8)-7(-1,6)E,vt=0',     #spw3
              '23(-5,18)-22(-6,17)E,vt=0',
              '25(-3,23)-24(-4,20)E,vt=0',
              '6(1,5)-7(2,6)--,vt=1',      # other
              '13(3,10)-14(4,10)A,vt=2',
              '34(-13,22)-33(-11,22)E,vt=0-vt=1',
              ),
    '(13)CH3OH': (#'10(2,8)-9(3,7)++',
                  '5(1,5)-4(1,4)++',),
    'CH3CN': (#'12(0)-11(0)',
              #'12(1)-11(1)',
              '12(2)-11(2)',
              '12(3)-11(3)',
              '12(4)-11(4)',
              '12(8)-11(8)'),
    '(13)CH3CN': ('13(3)-12(3)',
                  '13(4)-12(4)'),
    'CH3CHO': ('2(2,0)-3(1,3)A++,vt=2',),
    'HNCO': ('28(1,28)-29(0,29)',
             '10(3,8)-9(3,7)',
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
}

# Saved molecules
MOL_DIR = Path('./molecules')
SAVED_MOLS = {
    'CH3OH': MOL_DIR / 'ch3oh.json',
    'CH3CN': MOL_DIR / 'ch3cn.json',
    '(13)CH3OH': MOL_DIR / '13ch3oh.json',
    '(13)CH3CN': MOL_DIR / '13ch3cn.json',
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
              molecules: Sequence = ('CH3OH',),
              qns_mol: Dict = LINE_TRANSITIONS,
              half_width: int = 20):
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
                cube = src_cfg['file']
                
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
                moldir = outdir / 'line_cubes'
                try:
                    print(cube)
                    name = f'{hmc}_{norm_mol}_{norm_qns}_nchans{half_width*2}.fits'
                    out_cube = moldir / name
                    moldir.mkdir(parents=True, exist_ok=True)
                    subcube_extractor(flags + [cube, f'{out_cube}'])
                    processed.append(qns)
                except NoTransitionError:
                    print(f'{mol} ({qns}): not in cube {cube}')
                    continue

                # Put new source config section
                section = src_cfg.name + f'_{norm_mol}_{norm_qns}'
                source.copy_config(src_cfg.name, section)
                source.config[section]['file'] = f'{out_cube}'
                source.write()

def moments(source: Source,
            hmc: str,
            outdir: Path,
            array: str,
            molecules: Sequence[str] = ('CH3OH',),
            qns_mol: Dict = LINE_TRANSITIONS):
    """Calculate different types of moments."""
    half_width = {488: 10, 976: 5}
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
                
                # Moment flags
                flags = ['--vlsr', f'{source.vlsr.value}',
                         f'{source.vlsr.unit}'.replace(' ', ''),
                         '--line_lists', LINE_LISTS.get(mol, 'CDMS'),
                         '--molecule', mol,
                         '--qns', qns,
                         '--nsigma', '5',
                         '--win_halfwidth', f'{half_width[chanwidth]}',
                        ]
                if mol in SAVED_MOLS:
                    flags += ['--restore_molecule', f'{SAVED_MOLS[mol]}']
                if 'rms' in src_cfg:
                    flags += ['--rms'] + src_cfg['rms'].split()
                
                # Compute moments
                try:
                    name = f'{norm_mol}_{norm_qns}'
                    moldir = outdir / '{hmc}_moments'
                    moldir.mkdir(parents=True, exist_ok=True)
                    # Symmetric
                    filenames = symmetric_moments(
                        flags + ['--win_halfwidth', f'{half_width[chanwidth]}',
                                 cube, str(moldir / name), '0', '1', '2'])
                    # Local
                    processed.append(qns)
                    local_moments(flags + ['--win_halfwidth',
                                           f'{half_width[chanwidth]}',
                                           '--moments', '1', '2',
                                           cube, str(moldir / name)])
                    # Moving
                    moving_moments(flags + ['--savemasks', '10', f'{moldir}',
                                            cube])
                except NoTransitionError:
                    print(f'{mol} ({qns}): not in cube {cube}')
                    continue

def pv_maps(source, outdir, configs, figures, array):
    # Search for configs
    streams = configs / f'pvmaps/{source.name}_streams.cfg'
    rotation = configs / f'pvmaps/{source.name}_rotation.cfg'
    if streams.is_file():
        pv_streams(streams, source, outdir, figures, array)
    if rotation.is_file():
        pv_rotation(rotation, source, outdir, figures, array)

def pv_extractor(pvconfig, source, outdir, recenter=False):
    results = outdir / f'{pvconfig.stem}.fits'
    flags = ['--pvconfig', f'{pvconfig}', '--output', f'{results}',
             '--estimate_error', '--source', f'{source.config_file}',
             '--common_beam']
    if recenter:
        flags += ['--recenter']
    return pvmap_extractor(flags)
    #return results.parent.glob(f'{pvconfig.stem}*.fits')
    
def pv_streams(pvconfig, source, outdir, figures, array):
    # Extract pv maps
    pvout = outdir / 'pvmaps'
    pvmaps = list(pvout.glob('*stream*.fits'))
    if len(pvmaps) == 0:
        pvmaps = pv_extractor(pvconfig, source, pvout)

    # Fit gradient
    plotname = figures / source.name / array / 'pvmaps_streams.png'
    flags = ['--bunit', 'mJy/beam', '--outdir', f'{pvout}', '--plotname',
             f'{plotname}']
    print(pvmaps)
    pvmap_fitter(list(map(str, pvmaps)) + flags)

def pv_rotation(pvconfig, source, outdir, figures, array):
    pvout = outdir / 'pvmaps'
    pvmaps = pv_extractor(pvconfig, source, pvout, recenter=True)

    # Fit gradient
    plotname = figures / source.name / array / 'pvmaps_rotation.png'
    flags = ['--bunit', 'mJy/beam', '--outdir', f'{pvout}', '--plotname',
             f'{plotname}', '--function', 'plot']
    pvmap_fitter(list(map(str, pvmaps)) + flags)

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

if __name__ == '__main__':
    # Steps
    steps = {
        1: crop_line,
        2: moments,
    #    2: split_moments,
    #    3: pv_maps,
    #    4: extract_cassis,
    #    5: cassis_to_fits,
    #    7: peak_maps,
    #    8: line_cube,
    }
    skip = [3, 4, 5, 6, 7,8]
    array = 'c5c8'

    # Read sources from command line
    #sources_970kHz = ['G10.62-0.38', 'G11.1-0.12', 'G11.92-0.61',
    #                  'G34.43+0.24MM2', 'G35.13-0.74', 'G5.89-0.37',
    #                  'IRAS_181511208', 'IRAS_18182-1433', 'IRDC_182231243',
    #                  'W33A', 'IRAS_180891732']
    #sources_490kHz = ['G14.22-0.50_S', 'G24.60+0.08', 'G29.96-0.02',
    #                  'G333.12-0.56', 'G333.23-0.06', 'G333.46-0.16',
    #                  'G335.579-0.272', 'G335.78+0.17', 'G336.01-0.82',
    #                  'G34.43+0.24', 'G343.12-0.06', 'G35.03+0.35_A',
    #                  'G35.20-0.74_N', 'G351.77-0.54', 'IRAS_165623959',
    #                  'IRAS_18337-0743', 'NGC6334I', 'NGC_6334_I_N']
    #sources = ['G14.22-0.50_S']
    #sources = sources_490kHz
    sources = ['G11.92-0.61']

    # Iterate over source config files
    config_dir = configs / 'extracted'
    for source in sources:
        for config in config_dir.glob(f'{source}_hmc*.cfg'):
            # Open source
            src = Source(config_file=config)
            outdir = results / src.name / array / 'per_hot_core'
            hmc = config.stem.split('_')[-1]

            # Run steps
            for n, func in steps.items():
                if n in skip:
                    continue
                print(f'Step {n}')
                func(src, hmc, outdir, array)
                print("=" * 80)
