from pathlib import Path
import warnings

from astropy.io import fits
from multicube.astro_toolbox import get_ncores
from spectral_cube import SpectralCube
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
import pyspeckit

warnings.filterwarnings('ignore')

# Various definitions
basedir = Path('/data/share/binary_project/results/G336.01-0.82/CH3OH/')
results = 'spectra_fit_gaussian'
figs = 'spectra_fit_gaussian/figs'
mask = 'source_mask.fits'
cubes = [#'CH3OH_5_-1_4_-4_-2_3_E_vt_0.subcube.fits',
         #'CH3OH_4_-2_3_-3_-1_2_E_vt_0.subcube.fits',
         #'CH3OH_8_-0_8_-7_-1_6_E_vt_0.subcube.fits',
         'CH3OH_18_3_15_-17_4_14_A_vt_0_nchans60_masked_shrink.fits']
         #'CH3OH_4_2_3_-5_1_4_A_vt_0.subcube.fits',
         #'CH3OH_5_4_2_-6_3_3_E_vt_0.subcube.fits']
rms = 2.6E-3

for cube in cubes:
    # Load cube
    scfile = basedir / cube
    spc = pyspeckit.Cube(scfile)
    cb = SpectralCube.read(scfile)
    shape = cb.shape[-2:]
    #errmap = np.ones(shape) * rms
    start_from_point = (shape[1]//2, shape[0]//2)

    # Guesses
    cbvel = cb.with_spectral_unit(u.km/u.s, velocity_convention='radio')
    guesses = np.array([np.nanmax(cb.unmasked_data[:].value, axis=0),
                        cbvel.moment1().value,
                        (cbvel.moment2()**0.5).value])
    
    # Fit spectra
    spc.fiteach(fittype='gaussian',
                guesses=guesses,
                #errmap=errmap,
                #signal_cut=3, # ignore pixels with SNR<3
                blank_value=np.nan,
                multicore=get_ncores(),
                start_from_point=start_from_point)
    #modelcube = spc.get_modelcube(multicore=get_ncores())
    modelcube = spc.get_modelcube()

    for y, x in np.ndindex(spc.cube.shape[1:]):
        if np.all(np.isnan(spc.cube[:,y,x])):
            continue
        plt.plot(spc.xarr, spc.cube[:,y,x], 'k-')
        plt.plot(spc.xarr, modelcube[:,y,x], 'r-')
        figname = basedir / figs / scfile.name
        figname = figname.with_suffix(f'.x{x}y{y}.png')
        plt.savefig(figname, bbox_inches='tight')
        plt.close()
