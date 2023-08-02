from pathlib import Path

from astropy.io import fits
from spectral_cube import SpectralCube
import astropy.units as u
import numpy as np

# Various definitions
basedir = Path('/data/share/binary_project/results/G336.01-0.82/concat/CH3CN/')
cubes = [#'CH3OH_5_-1_4_-4_-2_3_E_vt_0.subcube.fits',
         #'CH3OH_4_-2_3_-3_-1_2_E_vt_0.subcube.fits',
         #'CH3OH_8_-0_8_-7_-1_6_E_vt_0.subcube.fits',
         #'CH3OH_4_2_3_-5_1_4_A_vt_0.subcube.fits',
         #'CH3OH_5_4_2_-6_3_3_E_vt_0.subcube.fits',
         #'CH3CN_12_0_-11_0_.subcube.fits',
         #'CH3CN_12_1_-11_1_.subcube.fits',
         'CH3CN_12_2_-11_2_.subcube.fits',
         'CH3CN_12_3_-11_3_.subcube.fits',
         'CH3CN_12_4_-11_4_.subcube.fits',
         ]

peaks = []
for cube in cubes:
    cbname = basedir / cube
    cb = SpectralCube.read(cbname)
    cb.allow_huge_operations=True
    cb = cb.to(u.K)

    peaks += [np.nanmax(cb.unmasked_data[:], axis=0).value]
    #try:
    #    peak += np.nanmax(cb.unmasked_data[:], axis=0)
    #except NameError:
    #    peak = np.nanmax(cb.unmasked_data[:], axis=0)

    wcs = cb.wcs.sub(2)

peaks = np.array(peaks)
stds = np.std(peaks, axis=0)
peaks = np.mean(peaks, axis=0)

header = wcs.to_header()
header['BUNIT'] = 'K'
header.update(cb.beam.to_header_keywords())

hdr = fits.PrimaryHDU(data=peaks, header=header)
hdr.writeto(basedir / 'brightness_temperature_map.fits', overwrite=True)

hdr = fits.PrimaryHDU(data=stds, header=header)
hdr.writeto(basedir / 'brightness_temperature_error_map.fits', overwrite=True)
