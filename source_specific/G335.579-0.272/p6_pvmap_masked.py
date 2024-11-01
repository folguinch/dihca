"""Mask pv map over input limit."""
import sys

from astropy.io import fits
import astropy.units as u

# Open image
imgfile = sys.argv[1]
img = fits.open(imgfile)[0]
bunit = u.Unit(img.header['BUNIT'], format='fits')

# Read limit
limit = float(sys.argv[2]) * u.Unit(sys.argv[3])

# Mask values
mask = img.data*bunit < limit
img.data[mask] = float('nan')

# Write
img.writeto(imgfile.replace('.fits', '.masked.fits'))

