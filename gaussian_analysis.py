"""Plots and analysis of 2-D Gaussian fit results."""
from pathlib import Path

from common_paths import configs, results
from casatasks import exportfits

if __name__ == '__main__':
    # List all the sources
    config = 'c8'
    cont_suffix = '.config8.cont_avg.selfcal_0.5_hogbom.image.fits'
    sources = [cfg.stem for cfg in configs.glob('*.cfg')]
    
    # Iterate over results
    for source in sources:
        result_dir = results / source / config / 'gaussian_fit'
        if not result_dir.is_dir():
            print(f'Skipping {source}: no results')
            continue
        residuals = list(result_dir.glob('*.residual'))
        if len(residual) == 0:
            print(f'Skipping {source}: no residuals')
            continue
        
        # Continuum
        continuum_map = continuum / f'{source}{cont_suffix}'
        if not continuum_map.exists():
            print(f'Skipping {source}: no continuum')
            continue

        # Iterate over residuals
        for residual in residuals:
            # Convert to FITS
            fitsresidual = residual.with_suffix('.residual.fits')
            if not fitsresidual.exists():
                exportfits(imagename=f'{residual}', fitsimage=fitsresidual)

            # Central position
            logfile = residual.with_suffix('.Log.txt')
            logtxt = logfile.read_text()
            ind_ra = logtxt.find('ra:')
            ind_dec = logtxt.find('dec:')
            ra = txt[ind_ra:].split()[1]
            dec = txt[ind_dec:].split()[1]
            ra = '{0}h{1}m{2}s'.format(*ra.split(':'))
            dec = '{0}d{1}m{2}.{3}s'.format(*tuple(map(int, dec.split('.'))))
            center = SkyCorrd(ra, dec, frame='icrs')

            # Plot
        
