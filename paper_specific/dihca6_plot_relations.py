"""Plot relations between measured parameters."""
from astropy.table import Table
from tile_plotter.utils import tick_formatter
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np

from common_paths import RESULTS, FIGURES
from dihca6_load_tables import get_masks, MASS, RADIUS

figsize = (10, 10)

# Load tables
summary = RESULTS / 'tables/dihca6_summary.csv'
summary = Table.read(summary)
archive_im = Table.read(RESULTS / 'tables/beltran_dewit_im_stars.csv')
archive_hm = Table.read(RESULTS / 'tables/beltran_dewit_hm_stars.csv')
zams = Table.read(RESULTS / 'tables/ZAMS_Ekstrom+2012.dat', format='ascii')

# Figure
plt.style.use(['paper', 'aspect_auto'])
fig = plt.figure(figsize=figsize)
ax1 = fig.add_axes((0.08, 0.56, 0.4, 0.4))
ax2 = fig.add_axes((0.578, 0.56, 0.4, 0.4))
ax3 = fig.add_axes((0.08, 0.06, 0.4, 0.4))
ax4 = fig.add_axes((0.578, 0.06, 0.4, 0.4))

# Masks
mask_G10, _, mask_faceon, mask_mols, mask_rad = get_masks(summary)

# Relation 1
mask1 = mask_G10 | mask_rad | mask_faceon | mask_mols
xval = summary[RADIUS]
yval = summary[MASS] / summary['mass_cen']
implot1, = ax1.loglog(archive_im['radius'],
                      archive_im['Mgas']/archive_im['Mstar'],
                      'ko',
                      label='Intermediate mass')
hmplot1, = ax1.loglog(archive_hm['radius'],
                      archive_hm['Mgas']/archive_hm['Mstar'],
                      'r^',
                      label='High-mass')
dihcaplot1a, = ax1.loglog(xval[~mask1], yval[~mask1], 'bs',
                          label='High-mass DIHCA')
dihcaplot1b, caps, bars = ax1.errorbar(xval[mask_rad], yval[mask_rad],
                                       xerr=xval[mask_rad]/5,
                                       xuplims=1,
                                       marker='s',
                                       color='b',
                                       linestyle='none',
                                       capsize=2,
                                       elinewidth=0.5,
                                       label='Upper limit')
dihcaplot1c, = ax1.loglog(xval[mask_G10], yval[mask_G10], 'gv',
                          label='G10.62-0.38')
dihcaplot1d, = ax1.loglog(xval[mask_faceon], yval[mask_faceon], 'ro',
                          label='Face-on sources')
dihcaplot1e, = ax1.loglog(xval[mask_mols], yval[mask_mols], 'c>',
                          label='c-HCOOH & HNCO')
handles = [implot1, hmplot1, dihcaplot1a, dihcaplot1c, dihcaplot1d, dihcaplot1e]
ax1.set_xlabel('Radius (au)')
ax1.set_ylabel(r'$M_g/M_c$')
ax1.set_xlim(left=10)
ax1.set_ylim(bottom=0.002)
ax1.legend(handles=handles, fontsize='xx-small', frameon=True, fancybox=True)
ax1.annotate('(a)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax1.xaxis.set_major_formatter(tick_formatter('log'))
ax1.yaxis.set_major_formatter(tick_formatter('log'))

# Relation 2
mask2 = mask_G10 | mask_faceon | mask_mols
xval = summary['mass_cen']
yval = summary[MASS]
dihcaplot2a, = ax2.loglog(xval[~mask2], yval[~mask2], 'bs',
                          label='High-mass DIHCA')
dihcaplot2b, = ax2.loglog(xval[mask_G10], yval[mask_G10], 'gv',
                          label='G10.62-0.38')
dihcaplot2c, = ax2.loglog(xval[mask_faceon], yval[mask_faceon], 'ro',
                          label='Face-on sources')
dihcaplot2d, = ax2.loglog(xval[mask_mols], yval[mask_mols], 'c>',
                          label='c-HCOOH & HNCO')
xvals = np.logspace(0, 2)
mcmgplot, = ax2.loglog(xvals, xvals, 'b--',
                       label=r'$M_g = M_c \sin^2 i$')
handles = [dihcaplot2a, dihcaplot2b, dihcaplot2c, dihcaplot2d, mcmgplot]
ax2.set_xlabel(r'$M_c \sin^2 i$ (M$_\odot$)')
ax2.set_ylabel(r'$M_g$ (M$_\odot$)', labelpad=-0.2)
ax2.set_xlim(1, 80)
ax2.set_ylim(0.03, 80)
ax2.legend(handles=handles, fontsize='xx-small',
           loc='lower left', frameon=True, fancybox=True)
ax2.annotate('(b)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax2.xaxis.set_major_formatter(tick_formatter('log'))
ax2.yaxis.set_major_formatter(tick_formatter('log'))

# Relation 3
mask3 = mask2
xval = summary[MASS]
yval = summary['wlum'] / summary['mass_cen']
dihcaplot3a, = ax3.loglog(xval[~mask3], yval[~mask3], 'bs',
                          label='High-mass DIHCA')
dihcaplot3b, = ax3.loglog(xval[mask_G10], yval[mask_G10], 'gv',
                          label='G10.62-0.38')
dihcaplot3c, = ax3.loglog(xval[mask_faceon], yval[mask_faceon], 'ro',
                          label='Face-on sources')
dihcaplot3d, = ax3.loglog(xval[mask_mols], yval[mask_mols], 'c>',
                          label='c-HCOOH & HNCO')
ax3.set_ylabel(r'$L_{\rm core}/(M_c \sin^2 i)$ (L$_\odot$/M$_\odot$)',
               labelpad=-0.1)
ax3.set_xlabel(r'$M_g$ (M$_\odot$)')
ax3.set_xlim(left=0.03)
ax3.legend(handles=[dihcaplot3a, dihcaplot3b, dihcaplot3c, dihcaplot3d],
           fontsize='xx-small', loc=(0.05, 0.68), frameon=True, fancybox=True)
ax3.annotate('(c)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax3.xaxis.set_major_formatter(tick_formatter('log'))
ax3.yaxis.set_major_formatter(tick_formatter('log'))

# Relation 4
mask4 = mask_G10 | mask_rad
xval = summary[RADIUS]
yval = summary[MASS]
dihcaplot4a, = ax4.loglog(xval[~mask4], yval[~mask4], 'bs',
                          label='High-mass DIHCA')
dihcaplot4b, caps, bars = ax4.errorbar(xval[mask_rad], yval[mask_rad],
                                       xerr=xval[mask_rad]/5,
                                       xuplims=1,
                                       marker='s',
                                       color='b',
                                       linestyle='none',
                                       capsize=2,
                                       elinewidth=0.5,
                                       label='Upper limit')
dihcaplot4c, = ax4.loglog(xval[mask_G10], yval[mask_G10], 'gv',
                          label='G10.62-0.38')
ax4.set_xlabel(r'Radius (au)')
ax4.set_ylabel(r'$M_g$ (M$_\odot$)', labelpad=-0.1)
ax4.set_xlim(left=10)
ax4.set_ylim(0.03, 50)
ax4.legend(handles=[dihcaplot4a, dihcaplot4c],
           fontsize='xx-small', loc=(0.05, 0.7), frameon=True, fancybox=True)
ax4.annotate('(d)', (0.05, 0.95), xytext=(0.05, 0.9), xycoords='axes fraction')
ax4.xaxis.set_major_formatter(tick_formatter('log'))
ax4.yaxis.set_major_formatter(tick_formatter('log'))

# Save figure 1
fig.savefig(FIGURES / 'papers/dihca6_relations.png')
fig.savefig(FIGURES / 'papers/dihca6_relations.pdf')

# Lstar vs Mstar
figsize = (5, 5)
fig = plt.figure(figsize=figsize)
ax = fig.add_axes((0.16, 0.12, 0.82, 0.82))

# Plot relation
mask = mask_G10 | mask_faceon | mask_mols
xval = summary['mass_cen']
yval = summary['wlum']
xlim = (2.3, 60.)
xvals = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]))
ms = 10**1.52 * xvals**1.62
lum_func = interp1d(zams['m'], 10**zams['logL'], kind='cubic',
                    bounds_error=False, fill_value='extrapolate')
dihcaplot4a, = ax.loglog(xval[~mask], yval[~mask], 'bs',
                         label='High-mass DIHCA')
dihcaplot4b, = ax.loglog(xval[mask_G10], yval[mask_G10], 'gv',
                         label='G10.62-0.38')
dihcaplot4c, = ax.loglog(xval[mask_faceon], yval[mask_faceon], 'ro',
                         label='Face-on sources')
dihcaplot4d, = ax.loglog(xval[mask_mols], yval[mask_mols], 'c>',
                         label='c-HCOOH & HNCO')
powerlawplot, = ax.loglog(xvals, ms, 'b-',
                          label=r'$\log L=1.62 \log M + 1.52$')
zamsplot, = ax.loglog(xvals, lum_func(xvals), 'm--',
                      label='ZAMS')
massivedisk, = ax.loglog(xvals, lum_func(xvals / 1.5), 'c:',
                         label='Massive disk')
binariesplot, = ax.loglog(xvals,  2 * lum_func(xvals / 2),
                          'g-.', label='Same mass binaries')
ax.set_xlabel(r'$M_c \sin^2 i$ (M$_\odot$)')
ax.set_ylabel(r'$L_{\rm core}$ (L$_\odot$)', labelpad=-0.1)
ax.set_xlim(*xlim)
ax.set_ylim(50, 1e6)
ax.legend(handles=[powerlawplot, zamsplot, massivedisk, binariesplot],
          fontsize='xx-small', loc='lower right', frameon=True, fancybox=True)
ax.xaxis.set_major_formatter(tick_formatter('log'))
ax.yaxis.set_major_formatter(tick_formatter('log'))

# Save figure 2
fig.savefig(FIGURES / 'papers/dihca6_LM_relation.png')
fig.savefig(FIGURES / 'papers/dihca6_LM_relation.pdf')

# Lstar vs Mstar for orignal luminosity
figsize = (5, 5)
fig = plt.figure(figsize=figsize)
ax = fig.add_axes((0.16, 0.12, 0.82, 0.82))

# Plot relation
mask = mask_G10 | mask_faceon | mask_mols
xval = summary['mass_cen']
yval = summary['lum']
xlim = (2.3, 60.)
xvals = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]))
ms = 10**1.52 * xvals**1.62
lum_func = interp1d(zams['m'], 10**zams['logL'], kind='cubic')
dihcaplotaux_a, = ax.loglog(xval[~mask], yval[~mask], 'bs',
                            label='High-mass DIHCA')
dihcaplotaux_b, = ax.loglog(xval[mask_G10], yval[mask_G10], 'gv',
                            label='G10.62-0.38')
dihcaplotaux_c, = ax.loglog(xval[mask_faceon], yval[mask_faceon], 'ro',
                            label='Face-on sources')
dihcaplotaux_d, = ax.loglog(xval[mask_mols], yval[mask_mols], 'c>',
                            label='c-HCOOH & HNCO')
powerlawplot, = ax.loglog(xvals, ms, 'b-',
                          label=r'$\log L=1.62 \log M + 1.52$')
zamsplot, = ax.loglog(xvals, lum_func(xvals), 'm--',
                      label='ZAMS')
massivedisk, = ax.loglog(xvals, lum_func(xvals / 1.5), 'c:',
                         label='Massive disk')
binariesplot, = ax.loglog(xvals,  2 * lum_func(xvals / 2), 'g-.',
                          label='Same mass binaries')
ax.set_xlabel(r'$M_c \sin^2 i$ (M$_\odot$)')
ax.set_ylabel(r'$L_{\rm core}$ (L$_\odot$)', labelpad=-0.1)
ax.set_xlim(*xlim)
ax.set_ylim(50, 1e6)
ax.legend(handles=[powerlawplot, zamsplot, massivedisk, binariesplot],
           fontsize='xx-small', loc='lower right', frameon=True, fancybox=True)
ax.xaxis.set_major_formatter(tick_formatter('log'))
ax.yaxis.set_major_formatter(tick_formatter('log'))

# Save figure 3
fig.savefig(FIGURES / 'papers/dihca6_relations_aux.png')
fig.savefig(FIGURES / 'papers/dihca6_relations_aux.pdf')
