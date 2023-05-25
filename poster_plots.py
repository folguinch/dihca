
from tile_plotter.plotter import plotter

from common_paths import *

config_dir = configs / 'plots' / 'posters'

if __name__ == '__main__':
    # Steps
    steps = {
        1: 'continuum',
        2: 'moment1',
        3: 'split_moments',
        4: 'pv_maps',
    }
    skip = [1, 2, 3]

    # Read sources from command line
    sources = ['G336.01-0.82']
    #sources = ['IRAS_180891732']

    # Iterate over sources
    for source in sources:
        # Iterate over steps
        for key, val in steps.items():
            if key in skip:
                continue

            config = config_dir / f'{source}_{val}.cfg'
            if config.exists():
                print(f'Plotting {config}')
                plotname = figures / source / 'posters' / f'{val}.eps'
                plotter([f'{config}', f'{plotname}'])
            elif config_dir.glob(f'{source}_{val}_*.cfg'):
                for config in config_dir.glob(f'{source}_{val}_*.cfg'):
                    print(f'Plotting {config}')
                    name = config.stem.split('_')
                    ind = name.index(val.split('_')[0])
                    name = '_'.join(name[ind:])
                    plotname = figures / source / 'posters' / f'{name}.eps'
                    plotter([f'{config}', f'{plotname}'])
            else:
                print(f'Skipping: {config}')
                continue
