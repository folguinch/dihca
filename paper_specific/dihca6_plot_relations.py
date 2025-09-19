"""Plot relations between measured parameters."""
from astropy.table import Table
from tile_plotter.utils import tick_formatter
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np

from common_paths import RESULTS, FIGURES

figsize = (10, 10)

# Load tables
#condensations = RESULTS / 'tables/dihca6_condensations.csv'
#condensations = np.loadtxt(condensations,
#                           delimiter=',',
#                           usecols=(0, 18, 20, 21),
#                           dtype={'names':('name', 'mstar', 'mdisk', 'radius'),
#                                  'formats':('S10', float, float, float)})
#archive_im = np.loadtxt(RESULTS / 'tables/beltran_dewit_im_stars.csv',
#                        delimiter=',',
#                        usecols=(1, 2, 3),
#                        dtype={'names':('radius', 'mdisk', 'mstar'),
#                               'formats':(float, float, float)})
#archive_hm = np.loadtxt(RESULTS / 'tables/beltran_dewit_hm_stars.csv',
#                        delimiter=',',
#                        usecols=(1, 2, 3),
#                        dtype={'names':('radius', 'mdisk', 'mstar'),
#                               'formats':(float, float, float)})
summary = RESULTS / 'tables/dihca6_summary.csv'
summary = Table.read(summary)
archive_im = Table.read(RESULTS / 'tables/beltran_dewit_im_stars.csv')
archive_hm = Table.read(RESULTS / 'tables/beltran_dewit_hm_stars.csv')
zams = Table.read(RESULTS / 'tables/ZAMS_Ekstrom+2012.dat', format='ascii')

plt.style.use(['paper', 'aspect_auto'])
#fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
fig = plt.figure(figsize=figsize)
ax1 = fig.add_axes((0.08, 0.56, 0.4, 0.4))
ax2 = fig.add_axes((0.578, 0.56, 0.4, 0.4))
ax3 = fig.add_axes((0.08, 0.06, 0.4, 0.4))
ax4 = fig.add_axes((0.578, 0.06, 0.4, 0.4))

# Relation 1
maskG10 = (summary['Source'] == 'G10.62-0.38')
ratio = summary['dust_mass'] / summary['mass_cen']
ratio = np.ma.masked_where(maskG10, ratio)
implot1, = ax1.loglog(archive_im['radius'],
                      archive_im['Mgas']/archive_im['Mstar'],
                      'ko',
                      label='Intermediate mass')
hmplot1, = ax1.loglog(archive_hm['radius'],
                      archive_hm['Mgas']/archive_hm['Mstar'],
                      'r^',
                      label='High-mass')
dihcaplot1a, = ax1.loglog(summary['disk_radius'],
                          ratio,
                          'bs',
                          label='High-mass DIHCA')
dihcaplot1b, = ax1.loglog(summary['disk_radius'][maskG10],
                          (summary['dust_mass'] / summary['mass_cen'])[maskG10],
                          'gv',
                          label='G10.62-0.38')
ax1.set_xlabel('Disk radius (au)')
ax1.set_ylabel(r'$M_g/M_c$')
ax1.legend(handles=[implot1, hmplot1, dihcaplot1a, dihcaplot1b], fontsize='xx-small')
ax1.annotate('(a)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax1.xaxis.set_major_formatter(tick_formatter('log'))
ax1.yaxis.set_major_formatter(tick_formatter('log'))

# Relation 2
#implot2, = ax2.loglog(archive_im['mstar'],
#                      archive_im['mdisk'],
#                      'ko',
#                      label='Intermediate mass')
#hmplot2, = ax2.loglog(archive_hm['mstar'],
#                      archive_hm['mdisk'],
#                      'r^',
#                      label='High-mass')
dihcaplot2a, = ax2.loglog(summary['mass_cen'][~maskG10],
                          summary['dust_mass'][~maskG10],
                          'bs',
                          label='High-mass DIHCA')
dihcaplot2b, = ax2.loglog(summary['mass_cen'][maskG10],
                          summary['dust_mass'][maskG10],
                          'gv',
                          label='G10.62-0.38')
ax2.set_xlabel(r'$M_c \sin^2 i$ (M$_\odot$)')
ax2.set_ylabel(r'$M_g$ (M$_\odot$)', labelpad=-0.2)
ax2.annotate('(b)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
xvals = np.logspace(0, 2)
mcmgplot, = ax2.loglog(xvals, xvals, 'b--', label=r'$M_g = M_c \sin^2 i$')
ax2.legend(handles=[dihcaplot2a, dihcaplot2b, mcmgplot], fontsize='xx-small',
           loc='lower left')
ax2.set_xlim(1, 80)
ax2.set_ylim(0.1, 50)
ax2.xaxis.set_major_formatter(tick_formatter('log'))
ax2.yaxis.set_major_formatter(tick_formatter('log'))

# Relation 3
mask1 = (
    ((summary['Source'] == 'G335.579-0.272') & (summary['ALMA'] == '1')) |
    (summary['Source'] == 'G35.20-0.74 N'))
mask2 = (
    (summary['molec'] != 'CH3CN') &
    (summary['molec'] != 'CH3OH')
    )
lum = summary['wlum']
lum = np.ma.masked_where(maskG10 | mask1 | mask2, lum)
mass = np.ma.array(summary['mass_cen'], mask=lum.mask)
radius = np.ma.array(summary['disk_radius'], mask=lum.mask)
dihcaplot3a, = ax3.semilogy(radius, lum/mass, 'bs', label='High-mass DIHCA')
dihcaplot3b, = ax3.semilogy(summary['disk_radius'][maskG10], lum.data[maskG10]/mass.data[maskG10], 'gv', label='G10.62-0.38')
dihcaplot3c, = ax3.semilogy(summary['disk_radius'][mask1], lum.data[mask1]/mass.data[mask1], 'ro', label='Face-on sources')
dihcaplot3d, = ax3.semilogy(summary['disk_radius'][mask2], lum.data[mask2]/mass.data[mask2], 'c>', label='c-HCOOH & HNCO')
ax3.set_ylabel(r'$L_\star/(M_c \sin^2 i)$ (L$_\odot$/M$_\odot$)',  labelpad=-0.1)
ax3.set_xlabel('Disk radius (au)')
#ax3.set_ylim(100, 1e6)
ax3.annotate('(c)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax3.legend(handles=[dihcaplot3a, dihcaplot3b, dihcaplot3c, dihcaplot3d],
           fontsize='xx-small')
#ax3.xaxis.set_major_formatter(tick_formatter('log'))
ax3.yaxis.set_major_formatter(tick_formatter('log'))

# Relation 4
dihcaplot4a, = ax4.loglog(mass, lum, 'bs', label='High-mass DIHCA')
dihcaplot4b, = ax4.loglog(mass.data[maskG10], lum.data[maskG10], 'gv', label='G10.62-0.38')
dihcaplot4c, = ax4.loglog(mass.data[mask1], lum.data[mask1], 'ro', label='Face-on sources')
dihcaplot4d, = ax4.loglog(mass.data[mask2], lum.data[mask2], 'c>', label='c-HCOOH & HNCO')
ax4.set_xlabel(r'$M_c \sin^2 i$ (M$_\odot$)')
ax4.set_ylabel(r'$L_\star$ (L$_\odot$)', labelpad=-0.1)
#xlim = ax4.get_xlim()
xlim = (2.3, 60.)
xval = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]))
#ms1 = 10**1.47 * xval**1.66
ms1 = 10**1.52 * xval**1.62
powerlawplot, = ax4.loglog(xval, ms1, 'b-', label=r'$\log L=1.62 \log M + 1.52$')
#ms2 = 10**1.237 * xval**2.726
#ax4.loglog(xval, ms2, 'm--')
lum_func = interp1d(zams['m'], 10**zams['logL'], kind='cubic',
                    bounds_error=False, fill_value='extrapolate')
zamsplot, = ax4.loglog(xval, lum_func(xval), 'm--',
                       label='ZAMS')
massivedisk, = ax4.loglog(xval, lum_func(xval / 1.5), 'c:',
                          label='Massive disk')
binariesplot, = ax4.loglog(xval,  2 * lum_func(xval / 2),
                           'g-.', label='Same mass binaries')
ax4.set_ylim(50, 1e6)
ax4.set_xlim(*xlim)
ax4.annotate('(d)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax4.legend(handles=[#dihcaplot4a, dihcaplot4b, dihcaplot4c, dihcaplot4d,
                    powerlawplot, zamsplot, massivedisk, binariesplot],
           fontsize='xx-small', loc='lower right')
ax4.xaxis.set_major_formatter(tick_formatter('log'))
ax4.yaxis.set_major_formatter(tick_formatter('log'))

fig.savefig(FIGURES / 'papers/dihca6_relations.png')
fig.savefig(FIGURES / 'papers/dihca6_relations.pdf')

# Relation 4 for orignal luminosity
figsize = (5, 5)
fig = plt.figure(figsize=figsize)
ax = fig.add_axes((0.16, 0.12, 0.82, 0.82))

olum = summary['lum']
olum = np.ma.masked_where(lum.mask, olum)
dihcaplotaux_a, = ax.loglog(mass, olum, 'bs', label='High-mass DIHCA')
dihcaplotaux_b, = ax.loglog(mass.data[maskG10], olum.data[maskG10], 'gv', label='G10.62-0.38')
dihcaplotaux_c, = ax.loglog(mass.data[mask1], olum.data[mask1], 'ro', label='Face-on sources')
dihcaplotaux_d, = ax.loglog(mass.data[mask2], olum.data[mask2], 'c>', label='c-HCOOH & HNCO')
ax.set_xlabel(r'$M_c \sin^2 i$ (M$_\odot$)')
ax.set_ylabel(r'$L_\star$ (L$_\odot$)', labelpad=-0.1)
#xlim = ax.get_xlim()
xlim = (2.3, 60.)
xval = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]))
ms1 = 10**1.52 * xval**1.62
powerlawplot, = ax.loglog(xval, ms1, 'b-', label=r'$\log L=1.62 \log M + 1.52$')
lum_func = interp1d(zams['m'], 10**zams['logL'], kind='cubic')
zamsplot, = ax.loglog(xval, lum_func(xval), 'm--',
                      label='ZAMS')
massivedisk, = ax.loglog(xval, lum_func(xval / 1.5), 'c:',
                         label='Massive disk')
binariesplot, = ax.loglog(xval,  2 * lum_func(xval / 2),
                          'g-.', label='Same mass binaries')
ax4.set_ylim(50, 1e6)
ax.set_xlim(*xlim)
#ax.annotate('(d)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax.legend(handles=[#dihcaplot4a, dihcaplot4b, dihcaplot4c, dihcaplot4d,
                    powerlawplot, zamsplot, massivedisk, binariesplot],
           fontsize='xx-small', loc='lower right')
ax.xaxis.set_major_formatter(tick_formatter('log'))
ax.yaxis.set_major_formatter(tick_formatter('log'))

fig.savefig(FIGURES / 'papers/dihca6_relations_aux.png')
fig.savefig(FIGURES / 'papers/dihca6_relations_aux.pdf')
