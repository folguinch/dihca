"""Plot relations between measured parameters."""
from astropy.table import Table
from tile_plotter.utils import tick_formatter
import matplotlib.pyplot as plt
import numpy as np

from common_paths import RESULTS, FIGURES

figsize = (7, 8)

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
fig, ax = plt.subplots(1, 1, figsize=figsize)
#fig = plt.figure(figsize=figsize)
#ax1 = fig.add_axes((0.08, 0.56, 0.4, 0.4))
#ax2 = fig.add_axes((0.578, 0.56, 0.4, 0.4))
#ax3 = fig.add_axes((0.08, 0.06, 0.4, 0.4))

# Relation 1
ratio = condensations['mdisk']/condensations['mstar']
implot1, = ax.loglog(archive_im['radius'],
                     archive_im['mdisk']/archive_im['mstar'],
                     'ko',
                     label='Intermediate mass [1]')
hmplot1, = ax.loglog(archive_hm['radius'],
                     archive_hm['mdisk']/archive_hm['mstar'],
                     'r^',
                     label='High-mass [1]')
dihcaplot1, = ax.loglog(condensations['radius'],
                        ratio,
                        'bs',
                        label='High-mass DIHCA')
ax.set_xlabel('Disk radius (au)')
ax.set_ylabel(r'$M_g/M_c$')
ax.legend(handles=[implot1, hmplot1, dihcaplot1], fontsize='small',
          loc='lower right')
#ax1.annotate('(a)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax.xaxis.set_major_formatter(tick_formatter('log'))
ax.yaxis.set_major_formatter(tick_formatter('log'))

fig.savefig(FIGURES / 'posters/dihca6_relations.png', bbox_inches='tight')
fig.savefig(FIGURES / 'posters/dihca6_relations.eps', bbox_inches='tight')
fig.savefig(FIGURES / 'posters/dihca6_relations.pdf', bbox_inches='tight')
