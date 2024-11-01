"""Plot spectra at given positions."""
from pathlib import Path

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
from line_little_helper.spectrum import Spectrum, CassisModelSpectra
import astropy.units as u
import matplotlib.pyplot as plt

figures = Path('/data/share/binary_project/figures/G336.01-0.82/c8/papers')
basedir = Path('/data/share/binary_project/results/G336.01-0.82/c8/CH3OH')
moment = basedir / 'CH3OH_18_3_15_-17_4_14_A_vt_0.subcube.moment0.fits'
moment = fits.open(moment)[0]
spectra = basedir / 'spectra'
#lte_spectra = basedir / 'spectra_lte_fit'
wcs = WCS(moment)
positions = [SkyCoord('16h35m09.26085s -48d46m47.65854s', frame='icrs'),
             SkyCoord('16h35m09.25148s -48d46m47.5705s', frame='icrs'),
             SkyCoord('16h35m09.27024s -48d46m47.71483s', frame='icrs'),
             SkyCoord('16h35m09.268s -48d46m47.531s', frame='icrs'),
             SkyCoord('16h35m09.272s -48d46m47.530s', frame='icrs'),
             #SkyCoord('16h35m09.293s -48d46m47.651', frame='icrs'),
             SkyCoord('16h35m09.272s -48d46m47.844s', frame='icrs')]
titles = ['ALMA1',
          'ALMA1-WEST',
          'ALMA1-EAST',
          'Northern streamer 1',
          'Northern streamer 2',
          #'Northern arc 3',
          'Southern streamer']
dlines = 0.02
#lines = [216.945521, 218.440063, 220.078561, 233.795666, (234.68337, 234.698519)]
lines = [233.795666]
nrows = 1 #len(positions)
ncols = 6
labelsize = 10

fig, axs = plt.subplots(nrows, ncols, sharey=True, figsize=(12, 3)) #15))
fig.subplots_adjust(wspace=0.05) 

for i, (position, ax) in enumerate(zip(positions, axs)):
    x, y = list(map(int, position.to_pixel(wcs)))
    print(f'Position {i}: ', x, y)

    # Load data and models
    spec = Spectrum.from_cassis(spectra / f'spec_x{x}_y{y}.dat')
    #model = CassisModelSpectra.read(lte_spectra / f'spec_x{x}_y{y}.lis')

    #for i, ax in enumerate(axrow):
    ax.plot(spec.spectral_axis.to(u.GHz).value,
            spec.intensity.to(u.K).value, ds='steps-mid', ls='-', c='b')
    #ax.plot(mspec.spectral_axis.to(u.GHz).value,
    #        mspec.intensity.to(u.K).value, ls='-', c='r')
    #ax.set_xlim(mspec.spectral_axis.to(u.GHz).min().value,
    #            mspec.spectral_axis.to(u.GHz).max().value)
    ax.set_xlim(lines[0] - dlines, lines[0] + dlines)
    ax.axvline(lines[0], c='g', ls='--')
    ax.set_ylim(-15, 200)
    ax.xaxis.set_major_formatter('{x:.2f}')

    if 0 < i < ncols-1:
        ax.tick_params(labelleft=False, labelright=False,
                       left=True, right=True, 
                       labelbottom=True,
                       labelsize=labelsize-1, length=5)
    elif i == 0:
        ax.set_xlabel('Frequency (GHz)', fontsize=labelsize)
        ax.set_ylabel('Brightness Temperature (K)', fontsize=labelsize)
        ax.tick_params(labelright=False, right=True,
                       labelbottom=True,
                       labelsize=labelsize-1, length=5)
    elif i == ncols-1:
        ax.tick_params(labelleft=False, left=True,
                       labelbottom=True,
                       labelsize=labelsize-1, length=5)
    #ax.tick_params(axis='x', labelrotation=30)
    ax.set_title(titles[i], fontsize=labelsize)

fig.savefig(figures / 'example_spectra.png', bbox_inches='tight')
fig.savefig(figures / 'example_spectra.pdf', bbox_inches='tight')
