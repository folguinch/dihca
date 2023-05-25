from .common_paths import *

def plot_pvmaps(source: str):
    config = configs / f'{source}'

if __name__ == '__main__':
    # Steps
    steps = {
        1: plot_continuum,
        2: moments,
        3: split_moments,
        4: pv_maps,
    }
    skip = [1, 2, 3]

    # Read sources from command line
    #sources = ['IRAS_180891732', 'G336.01-0.82']
    sources = ['G336.01-0.82']

    # Iterate over source config files
    iterover = (configs / f'{source}.cfg' for source in sources)
    for config in iterover:
        # Open source
        src = Source(config_file=config)
        outdir = results / src.name

        # Run steps
        for n, func in steps.items():
            if n in skip:
                continue
            print(f'Step {n}')
            func(src, outdir, configs, figures)

