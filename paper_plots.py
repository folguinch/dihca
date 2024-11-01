
from tile_plotter.plotter import plotter

from common_paths import *

array = 'c8'
config_dir = configs / 'plots' / 'papers'

if __name__ == '__main__':
    # Steps
    steps = {
        1: 'continuum',
        2: 'moments',
        3: 'split_moments',
        4: 'pv_maps',
        5: 'cassis',
        6: 'toomreq',
        7: 'streamers',
        8: 'temperature',
    }
    skip = [4, 2, 3, 5, 6, 7, 8]

    # Read sources from command line
    sources = ['G336.01-0.82']

    # Iterate over sources
    for source in sources:
        # Iterate over steps
        for key, val in steps.items():
            if key in skip:
                continue

            config = config_dir / f'{source}_{val}.cfg'
            if config.exists():
                print(f'Plotting {config}')
                plotname = figures / source / array / 'papers' / f'{val}.png'
                plotter([f'{config}', f'{plotname}', '--pdf'])
            elif config_dir.glob(f'{source}_{val}_*.cfg'):
                for config in config_dir.glob(f'{source}_{val}_*.cfg'):
                    print(f'Plotting {config}')
                    name = config.stem.split('_')
                    ind = name.index(val.split('_')[0])
                    name = '_'.join(name[ind:])
                    plotname = figures / source / array / 'papers' / f'{name}.png'
                    #try:
                    plotter([f'{config}', f'{plotname}', '--pdf'])
                    #except FileNotFoundError:
                    #    print(f'WARNING: Skipping {config}: File not found')
            else:
                print(f'Skipping: {config}')
                continue
