"""Plot spectra at given positions."""
from pathlib import Path

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
from line_little_helper.spectrum import Spectrum, CassisModelSpectra
import astropy.units as u
import matplotlib.pyplot as plt

figures = Path('/data/share/binary_project/figures/G336.01-0.82/papers')
basedir = Path('/data/share/binary_project/results/G336.01-0.82/CH3OH')
moment = basedir / 'CH3OH_18_3_15_-17_4_14_A_vt_0.subcube.moment0.fits'
moment = fits.open(moment)[0]
spectra = basedir / 'spectra'
lte_spectra = basedir / 'spectra_lte_fit'
wcs = WCS(moment)
positions = [SkyCoord('16h35m09.26085s -48d46m47.65854s', frame='icrs'),
             SkyCoord('16h35m09.25148s -48d46m47.5705s', frame='icrs'),
             SkyCoord('16h35m09.27024s -48d46m47.71483s', frame='icrs'),
             SkyCoord('16h35m09.268s -48d46m47.531s', frame='icrs'),
             SkyCoord('16h35m09.274s -48d46m47.530', frame='icrs'),
             SkyCoord('16h35m09.293s -48d46m47.651', frame='icrs'),
             SkyCoord('16h35m09.271s -48d46m47.844', frame='icrs')]
titles = ['ALMA1', 'ALMA1-WEST', 'ALMA1-EAST', 'Northern arc 1',
          'Northern arc 2', 'Northern arc 3', 'Southern arc']
dlines = 0.02
lines = [216.945521, 218.440063, 220.078561, 233.795666, (234.68337, 234.698519)]
nrows = len(positions)
ncols = 5
labelsize = 15

fig, axs = plt.subplots(nrows, ncols, sharey=True, figsize=(12, 15))
fig.subplots_adjust(wspace=0.05) 

for nsrc, (position, axrow) in enumerate(zip(positions, axs)):
    x, y = list(map(int, position.to_pixel(wcs)))
    print(f'Position {nsrc}: ', x, y)

    # Load data and models
    spec = Spectrum.from_cassis(spectra / f'spec_x{x}_y{y}.dat')
    model = CassisModelSpectra.read(lte_spectra / f'spec_x{x}_y{y}.lis')

    for i, (ax, mspec) in enumerate(zip(axrow, model)):
        ax.plot(spec.spectral_axis.to(u.GHz).value,
                spec.intensity.to(u.K).value, ds='steps-mid', ls='-', c='b')
        ax.plot(mspec.spectral_axis.to(u.GHz).value,
                mspec.intensity.to(u.K).value, ls='-', c='r')
        #ax.set_xlim(mspec.spectral_axis.to(u.GHz).min().value,
        #            mspec.spectral_axis.to(u.GHz).max().value)
        if i != ncols-1:
            ax.set_xlim(lines[i] - dlines, lines[i] + dlines)
            ax.axvline(lines[i], c='g', ls='--')
        else:
            ax.set_xlim(sum(lines[i])/2 - dlines, sum(lines[i])/2 + dlines)
            ax.axvline(lines[i][0], c='g', ls='--')
            ax.axvline(lines[i][1], c='g', ls='--')
        ax.set_ylim(-5, 200)
        ax.xaxis.set_major_formatter('{x:.2f}')

        if 0 < i < ncols-1:
            ax.spines.left.set_visible(False)
            ax.spines.right.set_visible(False)
            ax.tick_params(labelleft=False, labelright=False,
                           left=False, right=False, 
                           labelbottom=nsrc == nrows-1,
                           labelsize=labelsize, length=5)
            d = .5 
            kwargs = dict(marker=[(-d, -1), (d, 1)], markersize=12,
                          linestyle="none", color='k', mec='k',
                          mew=1, clip_on=False)
            ax.plot([0, 1], [0, 0], transform=ax.transAxes, **kwargs)
            ax.plot([0, 1], [1, 1], transform=ax.transAxes, **kwargs)
            if i == 2 and nsrc == nrows-1:
                ax.set_xlabel('Frequency (GHz)', fontsize=labelsize)
        elif i == 0:
            ax.spines.right.set_visible(False)
            ax.tick_params(labelright=False, right=False,
                           labelbottom=nsrc == nrows-1,
                           labelsize=labelsize, length=5)
            d = .5 
            kwargs = dict(marker=[(-d, -1), (d, 1)], markersize=12,
                          linestyle="none", color='k', mec='k',
                          mew=1, clip_on=False)
            ax.plot([1, 1], [1, 0], transform=ax.transAxes, **kwargs)
            if nsrc == nrows-1:
                ax.set_ylabel('Brightness Temperature (K)', fontsize=labelsize)
        elif i == ncols-1:
            ax.spines.left.set_visible(False)
            ax.tick_params(labelleft=False, left=False,
                           labelbottom=nsrc == nrows-1,
                           labelsize=labelsize, length=5)
            d = .5 
            kwargs = dict(marker=[(-d, -1), (d, 1)], markersize=12,
                          linestyle="none", color='k', mec='k',
                          mew=1, clip_on=False)
            ax.plot([0, 0], [0, 1], transform=ax.transAxes, **kwargs)
        ax.tick_params(axis='x', labelrotation=30)
        if i == 2:
            ax.set_title(titles[nsrc], fontsize=labelsize)

fig.savefig(figures / 'cassis_spectra.png', bbox_inches='tight')
fig.savefig(figures / 'cassis_spectra.pdf', bbox_inches='tight')
