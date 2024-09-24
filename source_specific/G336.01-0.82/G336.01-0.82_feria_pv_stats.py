"""Compute the statistics of the FERIA models."""
from pathlib import Path

from astropy.io import fits
from astropy.table import QTable
from toolkit.astro_tools.images import get_coord_axes
import astropy.units as u
import numpy as np
import numpy.ma as ma
import scipy.interpolate as interp

# Data
results = Path('/data/share/binary_project/results/G336.01-0.82/c8/feria')
pvmap = Path('/data/share/binary_project/results/G336.01-0.82/c8/pvmaps')
pvmap = pvmap / 'G336.01-0.82_rotation.CH3OH_spw0.ra248.78859_dec-48.77991.PA125.fits'
suffix = '3sigma'
#suffix = 'nothreshold'
log_results = results / f'best_models_{suffix}.log'
lower_limit = 3.6 * u.mJy/u.beam
#lower_limit = 6 * u.mJy/u.beam
#lower_limit = 7.2 * u.mJy/u.beam
sigma = 1.2 * u.mJy/u.beam
pvmap = fits.open(pvmap)[0]
cols, rows = get_coord_axes(pvmap)
cols = cols.to(u.arcsec)
rows = rows.to(u.km/u.s)

# Y-axis is inverted
#print(np.unravel_index(np.nanargmax(pvmap.data), pvmap.data.shape))
#print(np.unravel_index(np.nanargmax(pvmap.data[::-1]), pvmap.data.shape))
map_data = pvmap.data[::-1] * u.Unit(pvmap.header['BUNIT'])
map_data = map_data.to(u.mJy/u.beam)
rows = rows[::-1]
rr, cc = np.meshgrid(rows, cols, indexing='ij')

# Mask and normalize data
map_data = ma.masked_less(map_data.value, lower_limit.to(u.mJy/u.beam).value)
#map_data = ma.array(map_data.value, mask=np.zeros(map_data.shape, dtype=bool))
map_data.mask[:10] = True
map_data.mask[-5:] = True
#sigma2 = (map_data * 0.1)**2 + sigma.to(u.mJy/u.beam).value**2
sigma2 = sigma.to(u.mJy/u.beam).value**2
max_data = ma.max(map_data)
map_data = map_data / max_data
sigma2 = sigma2 / max_data**2
ndata = np.sum(~map_data.mask)
print(f'X-axis range: {cols[0]} {cols[-1]}')
print(f'Y-axis range: {rows[0]} {rows[-1]}')
print(f'Unmasked data: {ndata}')

# Models
models = Path('/home/users/folguin/clones/feria_G336/')
grids = ['large_grid_rout1000', 'large_grid_rout900', 'large_grid_rout800',
         'large_grid_rout700']

best_results = [f'Unmasked data: {ndata}']
for grid in grids:
    model_dir = models / grid
    qt = QTable(names=['mass', 'cb', 'incl', 'chi2'],
                units=[u.M_sun, u.au, u.deg, u.Unit(1)])

    for pvmodel in model_dir.glob('*PV-PA125deg*.fits'):
        # Otain model parameters from name
        #print(pvmodel)
        fl = str(pvmodel)
        ind = fl.find('D3100')
        fl = fl[ind:].split('.')
        mass_ind = fl[0].find('M')
        cb_ind = fl[0].find('CB')
        mass = float(fl[0][mass_ind+1:cb_ind]) * u.M_sun
        cb = float(fl[0][cb_ind+2:]) * u.au
        incl = float(fl[1][1:3]) * u.deg
        #print(f'Mass: {mass}')
        #print(f'CB: {cb}')
        #print(f'Inclination: {incl}')

        # Open map
        pvmapmod = fits.open(pvmodel)[0]
        mcols, mrows = get_coord_axes(pvmapmod)
        mcols = mcols.to(u.arcsec)
        mrows = mrows.to(u.km/u.s)
        #print(f'X-axis range: {mcols[0]} {mcols[-1]}')
        #print(f'Y-axis range: {mrows[0]} {mrows[-1]}')

        # Interpolate
        #pvmapmod_data = pvmapmod.data / np.nanmax(pvmapmod.data)
        fn = interp.RegularGridInterpolator((mrows.value, mcols.value),
                                            pvmapmod.data,
                                            bounds_error=False,
                                            fill_value=0.0)
        pvmod_int = fn((rr, cc))
        pvmod_int = pvmod_int / np.nanmax(pvmod_int)
        pvmod_int = ma.array(pvmod_int, mask=map_data.mask)

        # Chi2
        chimap = (pvmod_int - map_data)**2 / sigma2
        chi2 = ma.sum(chimap)
        #print(f'Chi2: {chi2}')
        qt.add_row([mass, cb, incl, chi2])

        # Test saving
        #hdu = fits.PrimaryHDU(data=map_data.filled(fill_value=np.nan))
        #hdu.writeto('test_pvmap.fits', overwrite=True)
        #hdu = fits.PrimaryHDU(data=sigma2.filled(fill_value=np.nan))
        #hdu.writeto('test_pvmap_error2.fits', overwrite=True)
        #hdu = fits.PrimaryHDU(data=pvmod_int.filled(fill_value=np.nan))
        #hdu.writeto('test_pvmap_model_interp.fits', overwrite=True)
        #hdu = fits.PrimaryHDU(data=chimap.filled(fill_value=np.nan))
        #hdu.writeto('test_pvmap_chimap.fits', overwrite=True)
        #break
    qt.write(results / f'{grid}_{suffix}.ecsv', format='ascii.ecsv', overwrite=True)
    qt.write(results / f'{grid}_{suffix}.html', format='ascii.html', overwrite=True)
    qt.write(results / f'{grid}_{suffix}.tex', format='ascii.latex', overwrite=True)
    best = np.argmin(qt['chi2'])
    best = qt[best]
    print(f'Best model {grid}: ')
    print(f'{best}')
    best_results += ['-'*80, f'Best model {grid}: ', f'{best}']
log_results.write_text('\n'.join(best_results))
    #break

