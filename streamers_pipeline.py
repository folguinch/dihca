"""Pipeline for analysing streamers."""
from pathlib import Path

from astro_source.source import Source
from line_little_helper.molecule_moments import main as mol_moments

# Globals
outdir = Path('/data/share/binary_project')
results = outdir / 'results'

# Steps
step_1 = True

# Iterate over sources
configs = Path('/data/share/binary_project/configs')
for config in configs.iterdir():
    # Open source
    molecule = 'H2CO'
    source = Source(config_file=config)
    results_src = results / f'{molecule}_moments/{source.name}'
    if results_src.is_dir():
        continue
    print(source)

    # vlsr
    vlsr = source.config['INFO']['vlsr'].split()

    # Continuum images
    source_dir = Path(source.config['INFO']['basedir'])
    #continuum = source_dir / 'pbclean'
    #continuum = list(continuum.glob('*.config8.*.cont_avg.*.fits'))[0]

    # Find sources with streamers
    if step_1:
        # Command arguments
        table = results / f'{molecule}_moments/moments_info.ecsv'
        args = ['--molecule', molecule, '--win_halfwidth', '8',
                '--line_lists', 'JPL', '--table', f'{table}', '--vlsr' ] + vlsr

        # Result directory
        if not results_src.is_dir():
            results_src.mkdir(parents=True)

        # Iterate over dirty cubes
        dirty_dir = source_dir / 'dirty' / 'config8'
        ditry_contsub = dirty_dir / 'contsub'
        if ditry_contsub.is_dir():
            dirty_dir = ditry_contsub
        for dirty in dirty_dir.glob('*.image.fits'):
            # Calculate moment
            output = results_src / dirty.stem
            posargs = [f'{dirty}', f'{output}', '0', '1', '2']
            mol_moments(args + posargs)
