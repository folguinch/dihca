"""Plot relations between measured parameters."""
from astropy.table import Table
from tile_plotter.utils import tick_formatter
import matplotlib.pyplot as plt
import numpy as np

from common_paths import RESULTS, FIGURES

figsize = (10, 10)

# Load tables
condensations = RESULTS / 'tables/dihca6_condensations.csv'
condensations = np.loadtxt(condensations,
                           delimiter=',',
                           usecols=(0, 18, 20, 21),
                           dtype={'names':('name', 'mstar', 'mdisk', 'radius'),
                                  'formats':('S10', float, float, float)})
archive_im = np.loadtxt(RESULTS / 'tables/beltran_dewit_im_stars.csv',
                        delimiter=',',
                        usecols=(1, 2, 3),
                        dtype={'names':('radius', 'mdisk', 'mstar'),
                               'formats':(float, float, float)})
archive_hm = np.loadtxt(RESULTS / 'tables/beltran_dewit_hm_stars.csv',
                        delimiter=',',
                        usecols=(1, 2, 3),
                        dtype={'names':('radius', 'mdisk', 'mstar'),
                               'formats':(float, float, float)})
summary = RESULTS / 'tables/dihca6_summary.csv'
summary = Table.read(summary)

plt.style.use(['paper', 'aspect_auto'])
#fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
fig = plt.figure(figsize=figsize)
ax1 = fig.add_axes((0.08, 0.56, 0.4, 0.4))
ax2 = fig.add_axes((0.578, 0.56, 0.4, 0.4))
ax3 = fig.add_axes((0.08, 0.06, 0.4, 0.4))

# Relation 1
ratio = condensations['mdisk']/condensations['mstar']
implot1, = ax1.loglog(archive_im['radius'],
                      archive_im['mdisk']/archive_im['mstar'],
                      'ko',
                      label='Intermediate mass')
hmplot1, = ax1.loglog(archive_hm['radius'],
                      archive_hm['mdisk']/archive_hm['mstar'],
                      'r^',
                      label='High-mass')
dihcaplot1, = ax1.loglog(condensations['radius'],
                         ratio,
                         'bs',
                         label='High-mass DIHCA')
ax1.set_xlabel('Disk radius (au)')
ax1.set_ylabel(r'$M_g/M_c$')
ax1.legend(handles=[implot1, hmplot1, dihcaplot1], fontsize='x-small')
ax1.annotate('(a)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax1.xaxis.set_major_formatter(tick_formatter('log'))
ax1.yaxis.set_major_formatter(tick_formatter('log'))

# Relation 2
implot2, = ax2.loglog(archive_im['mstar'],
                      archive_im['mdisk'],
                      'ko',
                      label='Intermediate mass')
hmplot2, = ax2.loglog(archive_hm['mstar'],
                      archive_hm['mdisk'],
                      'r^',
                      label='High-mass')
dihcaplot2, = ax2.loglog(condensations['mstar'],
                         condensations['mdisk'],
                         'bs',
                         label='High-mass DIHCA')
ax2.set_xlabel(r'$M_c$ (M$_\odot$)')
ax2.set_ylabel(r'$M_g$ (M$_\odot$)', labelpad=-0.2)
ax2.annotate('(b)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax2.legend(handles=[implot2, hmplot2, dihcaplot2], fontsize='x-small',
           loc='lower left')
ax2.xaxis.set_major_formatter(tick_formatter('log'))
ax2.yaxis.set_major_formatter(tick_formatter('log'))

# Relation 3
lum = summary['wlum']
mass = summary['mass_cen']
mask1 = (
    (summary['#Source'] == 'G10.62-0.38') |
    ((summary['#Source'] == 'G335.579-0.272') & (summary['ALMA'] == '1')) |
    (summary['#Source'] == 'G35.20-0.74 N'))
mask2 = (
    (summary['molec'] != 'CH3CN') &
    (summary['molec'] != 'CH3OH')
    )
lum = np.ma.masked_where(mask1 | mask2, lum)
mass = np.ma.array(summary['mass_cen'], mask=lum.mask)
ax3.loglog(mass, lum, 'bs')
ax3.loglog(mass.data[mask1], lum.data[mask1], 'ro')
ax3.loglog(mass.data[mask2], lum.data[mask2], 'c>')
ax3.set_xlabel(r'$M_c$ (M$_\odot$)')
ax3.set_ylabel(r'$L_\star$ (L$_\odot$)', labelpad=-0.1)
xlim = ax3.get_xlim()
xval = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]))
ms1 = 10**1.47 * xval**1.66
ms2 = 10**1.237 * xval**2.726
ax3.loglog(xval, ms1, 'g-.')
ax3.loglog(xval, ms2, 'm--')
ax3.set_ylim(100, 1e6)
ax3.annotate('(c)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax3.xaxis.set_major_formatter(tick_formatter('log'))
ax3.yaxis.set_major_formatter(tick_formatter('log'))

fig.savefig(FIGURES / 'papers/dihca6_relations.png')
fig.savefig(FIGURES / 'papers/dihca6_relations.pdf')
