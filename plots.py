"""Unified plotter script."""
from pathlib import Path
import sys

from tile_plotter.plotter import plotter

from common_paths import CONFIGS, FIGURES

SKIP = [1, 4, 3, 5]
PLOT_TYPE = 'papers'
#PLOT_TYPE = 'posters'
STEPS = {
    1: 'continuum',
    2: 'moments',
    3: 'split_moments',
    4: 'pv_maps',
    5: 'streamers'
}
BY_GROUP = True
FIGSETS = False

def by_source(sources, config_dir, skip, flags, filters=None):
    # Iterate over sources
    for source in sources:
        print(source)
        # Iterate over steps
        for key, val in STEPS.items():
            if key in skip:
                continue
            plot_dir = FIGURES / source / PLOT_TYPE
            plot_dir.mkdir(parents=True, exist_ok=True)
            for config in config_dir.glob(f'{source}_{val}_*.cfg'):
                if filters is not None:
                    toskip = False
                    for filter_val in filters:
                        if filter_val not in f'{config}':
                            toskip = True
                            break
                    if toskip: 
                        print(f'Skipping: {config}')
                        continue
                print(f'Plotting {config}')
                name = config.stem.split('_')
                ind = name.index(val.split('_')[0])
                name = '_'.join(name[ind:])
                plotname = plot_dir / f'{name}.png'
                plotter([f'{config}', f'{plotname}'] + flags)

def by_group(config_dir, skip, flags):
    for key, group in STEPS.items():
        if key in skip:
            continue
        basename = f'group_{group}.*.cfg'
        plot_dir = FIGURES / f'group_{group}' / PLOT_TYPE
        plot_dir.mkdir(parents=True, exist_ok=True)
        for config in config_dir.glob(basename):
            print(f'Plotting {config}')
            plotname = plot_dir / config.with_suffix('.png').name
            plotter([f'{config}', f'{plotname}'] + flags)
            print('=' * 100)

def by_figset(config_dir, skip, flags):
    for key, group in STEPS.items():
        if key in skip:
            continue
        basename = f'*{group}*.*.cfg'
        plot_dir = FIGURES / 'figsets' / PLOT_TYPE / group
        plot_dir.mkdir(parents=True, exist_ok=True)
        for config in config_dir.glob(basename):
            print(f'Plotting {config}')
            plotname = plot_dir / config.with_suffix('.png').name
            plotter([f'{config}', f'{plotname}'] + flags)
            print('=' * 100)

def by_config(config, flags):
    plot_dir = FIGURES / f'by_config'
    plot_dir.mkdir(parents=True, exist_ok=True)
    print(f'Plotting {config}')
    plotname = plot_dir / config.with_suffix('.png').name
    plotter([f'{config}', f'{plotname}'] + flags)
    print('=' * 100)

if __name__ == '__main__':
    skip = SKIP
    config_dir = CONFIGS / 'plots' / PLOT_TYPE

    # Read sources from command line
    sources = ['G14.22-0.50_S', 'G24.60+0.08', 'G29.96-0.02',
               'G333.12-0.56', 'G333.23-0.06', 'G333.46-0.16',
               'G335.579-0.272', 'G335.78+0.17', 'G336.01-0.82',
               'G34.43+0.24', 'G343.12-0.06', 'G35.03+0.35_A',
               'G35.20-0.74_N', 'G351.77-0.54', 'IRAS_165623959',
               'IRAS_18337-0743', 'NGC6334I', 'NGC_6334_I_N',
               'G10.62-0.38', 'G11.1-0.12', 'G11.92-0.61',
               'G34.43+0.24MM2', 'G35.13-0.74', 'G5.89-0.37',
               'IRAS_181511208', 'IRAS_18182-1433', 'IRDC_182231243',
               'W33A', 'IRAS_180891732']
    #sources = ['G336.01-0.82']
    #sources = ['IRAS_180891732']
    filters = ['c5c8']

    # Flags
    flags = []
    if PLOT_TYPE in ['papers', 'posters']:
        flags = ['--pdf', '--eps']

    # Plot
    configs = sys.argv[1:]
    if len(configs) != 0:
        for config in configs:
            by_config(Path(config), flags)
    elif BY_GROUP:
        by_group(config_dir, skip, flags)
    elif FIGSETS:
        print('Plotting figure sets')
        by_figset(config_dir / 'figsets', skip, flags)
    elif len(sources) > 0:
        by_source(sources, config_dir, skip, flags, filters=filters)
    else:
        raise NotImplementedError
