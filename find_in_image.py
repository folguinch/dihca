"""Find if a coordinate is in image."""
from pathlib import Path
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np

source = 'G10.62-0.38'
sources = {
    'G10.62-0.38': [
        SkyCoord('18h10m28.61s', '-19d55m49.487s', frame='icrs'),
        SkyCoord('18h10m28.709s', '-19d55m50.099s', frame='icrs')
    ],
}
mask_dir = Path('/mnt/Umbriel/dihca/results/wkdir')
for img in mask_dir.glob('*.fits'):
    mask = fits.open(img)[0]
    val = mask.data.astype(bool)
    wcs = WCS(mask)
    
    for coord in sources[source]:
        pix_x, pix_y = wcs.world_to_pixel(coord)
        if val[int(pix_y), int(pix_x)]:
            print(f'Coord {coord.ra.hms} {coord.ra.dms} in {img.name}')
            print(f'Npix = {np.sum(val)}')
