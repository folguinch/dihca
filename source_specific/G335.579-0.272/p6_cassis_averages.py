from pathlib import Path

from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u
import astropy.wcs as wcs
import numpy as np

# Some definitions
positions = {
    'ALMA1a': SkyCoord('16h30m58.767s', '-48d43m53.87s', frame='icrs'),
    'ALMA1b': SkyCoord('16h30m58.767s', '-48d43m53.80s', frame='icrs'),
    }
    #'ALMA1bow': SkyCoord('16h30m58.754s', '-48d43m54.058s', frame='icrs'),
bmin = 0.043 * u.arcsec
bmaj = 0.064 * u.arcsec
radius = np.sqrt(bmin*bmaj) / 2
print(f'Radius: {radius.value} {radius.unit}')

# Open data
results = Path(('/home/myso/share/binary_project/G333_G335/G335.579-0.272/'
                'results_final/concat'))
lte_dir = results / 'CH3OH/spectra/lte_fit'
files = ['nmol_1_map.fits', 'tex_1_map.fits']
bow_mask = fits.open(results /
                     'G335.579-0.272.alma1bow.130sigma.3600x3600.mask.fits')[0]
bow_mask = bow_mask.data.astype(bool)
print(f'Bow mask shape: {bow_mask.shape}')
print(f'Bow mask valid points: {np.sum(bow_mask)}')
for fitfile in files:
    # Open files
    print('='*40)
    print(f'Opening: {fitfile}')
    image = fits.open(lte_dir / fitfile)[0]
    error = fits.open(lte_dir / fitfile.replace('_map', '_map_error'))[0]
    image_wcs = wcs.WCS(image.header)

    # Data
    data = np.squeeze(image.data)
    data_error = np.squeeze(error.data)

    # Pixel size
    pixsize = np.abs(image.header['CDELT2']) * u.degree
    pixsize = pixsize.to(radius.unit)
    print(f'Pixel size: {pixsize}')
    print(f'Data shape: {image.data.shape}')

    for source, position in positions.items():
        print('-'*40)
        print(f'Source: {source}')
        # Mask
        xp, yp = wcs.utils.skycoord_to_pixel(position, image_wcs)
        y, x = np.indices(data.shape)
        distance = np.sqrt((y - yp)**2 + (x - xp)**2)
        rad = radius / pixsize
        print(f'Radius: {rad.value} pixels')
        mask = distance <= rad.value
        print(f'Valid points: {np.sum(mask)}')

        # Averages
        avg = np.mean(data[mask])
        err = np.sqrt(np.sum(data_error[mask]**2)) / np.sum(mask)
        print(f'Mean: {avg}')
        print(f'Std dev: {err}')

    # Bow
    print(f'Source: bow')
    nanmask = np.isnan(data[bow_mask])
    print(f'NaN values in bow: {np.sum(nanmask)}')
    avg = np.nanmean(data[bow_mask])
    err = np.sqrt(np.nansum(data_error[bow_mask]**2)) / \
            (np.sum(bow_mask) - np.sum(nanmask))
    print(f'Mean: {avg}')
    print(f'Std dev: {err}')

