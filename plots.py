"""Unified plotter script."""

from tile_plotter.plotter import plotter

from common_paths import configs, figures

PLOT_TYPE = 'papers'
STEPS = {
    1: 'continuum',
    2: 'moments',
    3: 'split_moments',
    4: 'pv_maps',
    5: 'streamers'
}

def by_source(sources, skip, flags):
    # Iterate over sources
    for source in sources:
        # Iterate over steps
        for key, val in STEPS.items():
            if key in skip:
                continue

            config = config_dir / f'{source}_{val}.cfg'
            plot_dir = figures / source / PLOT_TYPE
            plot_dir.mkdir(parents=True, exist_ok=True)
            if config.exists():
                print(f'Plotting {config}')
                plotname = plot_dir / f'{val}.png'
                plotter([f'{config}', f'{plotname}'] + flags)
            elif config_dir.glob(f'{source}_{val}_*.cfg'):
                for config in config_dir.glob(f'{source}_{val}_*.cfg'):
                    print(f'Plotting {config}')
                    name = config.stem.split('_')
                    ind = name.index(val.split('_')[0])
                    name = '_'.join(name[ind:])
                    plotname = plot_dir / f'{name}.png'
                    plotter([f'{config}', f'{plotname}'] + flags)
            else:
                print(f'Skipping: {config}')
                continue

if __name__ == '__main__':
    skip = [1, 2, 3, 4, 5]
    config_dir = configs / 'plots' / PLOT_TYPE

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

    # Flags
    flags = []
    if plot_type == 'papers':
        flags = ['--pdf']

    # Plot
    if len(sources) > 0:
        by_source(sources, skip, flags)
    else:
        raise NotImplementedError
