from pathlib import Path

from astropy.io import fits
from astropy.modeling.models import BlackBody
from astropy.wcs import WCS
from radio_beam import Beam
from spectral_cube import SpectralCube
from regions import Regions, PolygonSkyRegion
import astropy.units as u
import numpy as np
import numpy.ma as ma

# Various definitions
data58 = Path('/data/share/binary_project/G336.01/G336.01-0.82/final_data/concat5_8')
data8 = Path('/data/share/binary_project/G336.01/G336.01-0.82/final_data/config8')
basedir = Path('/data/share/binary_project/results/G336.01-0.82/concat/CH3CN/')
results = Path('/data/share/binary_project/results/G336.01-0.82/c8/')
temp = basedir / 'brightness_temperature_map.fits'
#continuum = data58 / 'G336.01-0.82.config8and5.cont_avg.selfcal_0.5_hogbom.image.pbcor.fits'
continuum = data8 / 'continuum_clean' / 'G336.01-0.82.config8.cont_avg.selfcal.robust0.5.hogbom.image.pbcor.fits'
regions = [data58 / 'north_streamer_5sigma_contour.crtf',
           data58 / 'south_streamer_5sigma_contour.crtf']

# Constants
kappa = 1.0 * u.cm**2/u.g
Rdg = 0.01
nu = 226.15 * u.GHz
distance = 3.1 * u.kpc
pixsize = 0.01 * u.arcsec

# Load maps
temp = fits.open(temp)[0]
continuum = fits.open(continuum)[0]
header = continuum.header

# Quantities
beam = Beam.from_fits_header(header)
temp = np.squeeze(temp.data) * u.Unit(temp.header['BUNIT'])
temp[temp <= 0] = np.nan
continuum = np.squeeze(continuum.data) * u.Unit(header['BUNIT'])
continuum = continuum * u.beam
bb = BlackBody(temp)
bnu = bb(nu)
surfden = continuum / (beam.sr * bnu * kappa * Rdg)

# Mass
#mass = continuum * distance**2 / (Rdg * kappa * bb(nu))
mass = 2.7 / 2.8 * distance**2 * pixsize.to(u.rad)**2 * surfden / u.sr
mass = mass.to(u.M_sun)

# Save map
wcs = WCS(header, naxis=2)
new_header = wcs.to_header()
new_header['BUNIT'] = f'{mass.unit:FITS}'
hdu = fits.PrimaryHDU(data=mass.value, header=new_header)
hdu.writeto(results / 'mass_map.fits', overwrite=True)

# Calculate mass within regions
for region in regions:
    reg = Regions.read(region).pop()
    reg_pix = reg.to_pixel(wcs)
    mask = reg_pix.to_mask().to_image(mass.shape).astype(bool)
    total_mass = np.sum(mass[mask])
    avg_temp = np.mean(temp[mask])
    print(f'Region {region.name} temperature: {avg_temp}')
    print(f'Region {region.name} mass: {total_mass}')
