from pathlib import Path

from astropy.io import fits
from spectral_cube import SpectralCube
import astropy.units as u
import numpy as np

# Various definitions
basedir = Path('/data/share/binary_project/results/G336.01-0.82/CH3OH/')
cubes = ['CH3OH_5_-1_4_-4_-2_3_E_vt_0.subcube.fits',
         #'CH3OH_4_-2_3_-3_-1_2_E_vt_0.subcube.fits',
         #'CH3OH_8_-0_8_-7_-1_6_E_vt_0.subcube.fits',
         'CH3OH_4_2_3_-5_1_4_A_vt_0.subcube.fits',
         #'CH3OH_5_4_2_-6_3_3_E_vt_0.subcube.fits',
         ]

for cube in cubes:
    cbname = basedir / cube
    cb = SpectralCube.read(cbname)
    cb.allow_huge_operations=True
    cb = cb.to(u.K)

    try:
        peak += np.nanmax(cb.unmasked_data[:], axis=0)
    except NameError:
        peak = np.nanmax(cb.unmasked_data[:], axis=0)

    wcs = cb.wcs.sub(2)

hdr = fits.PrimaryHDU(data=peak.value/2, header=wcs.to_header())
hdr.writeto(basedir / 'brightness_temperature_map.fits', overwrite=True)
