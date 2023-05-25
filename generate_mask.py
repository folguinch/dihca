"""Generate a mask from a given image filtering small clumps."""
from pathlib import Path

from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
import scipy.ndimage as ndimg

from common_paths import *

# Input information
source = 'G336.01-0.82'
image = results / source / 'CH3OH'
image = image / 'CH3OH_18_3_15_-17_4_14_A_vt_0.subcube.moment1.fits'
maskname = image.with_suffix('.source_mask.fits')
minsize = 50

# Open image
data = fits.open(image)[0]
wcs = WCS(data, naxis=2)

# Initial mask
masked = np.ma.masked_invalid(np.squeeze(data.data))
mask = ~masked.mask

# Identify pieces
structure = ndimg.generate_binary_structure(mask.ndim, 1)
labels, nlab = ndimg.label(mask, structure=structure)
component_sizes = np.bincount(labels.ravel())

# Filter small
small_mask = component_sizes < minsize
small_mask = small_mask[labels]
mask[small_mask] = False

# Save mask
header = wcs.to_header()
hdu = fits.PrimaryHDU(header=header, data=mask.astype('int16'))
hdu.writeto(maskname, overwrite=True)
