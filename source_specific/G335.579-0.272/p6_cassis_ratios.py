import pathlib

from astropy.io import fits

results = pathlib.Path(('/home/myso/share/binary_project/G333_G335/'
                        'G335.579-0.272/results_final/concat/CH3OH/'
                        'spectra/lte_fit'))
col_den = results / 'nmol_1_map.fits'
col_den = fits.open(col_den)[0]
col_den_error = results / 'nmol_1_map_error.fits'
col_den_error = fits.open(col_den_error)[0]
print(col_den.header['BUNIT'])
print(col_den_error.header['BUNIT'])

header = col_den_error.header
del header['BUNIT']
hdu = fits.PrimaryHDU(col_den.data/col_den_error.data, header=header)
hdu.writeto(results / 'nmol_1_map_ratio.fits')

