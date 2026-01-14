"""Plot power law index histogram."""
#from astropy.table import Table
from matplotlib.ticker import MaxNLocator
from tile_plotter.utils import tick_formatter
import matplotlib.pyplot as plt
import numpy as np

from common_paths import RESULTS, FIGURES
from dihca6_load_tables import load_summary, MASS, RADIUS

#figsize = (5, 18)
figsize = (10, 10)

# Load tables
summary = load_summary(masked=True)

# Bins alpha
alpha = summary['alpha']
bin_edges_alpha = np.histogram_bin_edges(-alpha.compressed(), bins='fd')
counts_alpha, bins_alpha = np.histogram(-alpha.compressed(),
                                        bins=bin_edges_alpha)
median_alpha = np.ma.median(-alpha)
print('Alpha median:', median_alpha)
print('Total: ', len(alpha.compressed()), '/', len(alpha))
print('=' * 80)

# Bins radius
radius = summary[RADIUS]
bin_edges_radius = np.histogram_bin_edges(radius.compressed(), bins='fd')
counts_radius, bins_radius = np.histogram(radius.compressed(),
                                          bins=bin_edges_radius)
counts_radius_all, bins_radius_all = np.histogram(radius.data.data,
                                                  bins=bin_edges_radius)
median_radius = np.ma.median(radius)
median_radius_all = np.ma.median(radius.data.data)
below200 = np.sum(radius < 200)
below200_all = np.sum(radius.data.data < 200)
print('Radius median:', median_radius)
print('Total: ', len(radius.compressed()), '/', len(radius))
print('Sources below 200 au:', below200, 'out of', np.sum(~radius.mask))
print('-' * 80)
print('[ALL] Radius median:', median_radius_all)
print('[ALL] Total : ', len(radius.data.data), '/', len(radius))
print('[ALL] Sources below 200 au:', below200_all, 'out of',
      len(radius.data.data))
print('=' * 80)

# Bins disk mass
mass = summary[MASS]
bin_edges_mass = np.histogram_bin_edges(mass.compressed(), bins='fd')
counts_mass, bins_mass = np.histogram(mass.compressed(),
                                      bins=bin_edges_mass)
counts_mass_all, bins_mass_all = np.histogram(mass.data.data,
                                              bins=bin_edges_mass)
median_mass = np.ma.median(mass)
median_mass_all = np.ma.median(mass.data.data)
below5 = np.sum(mass < 5)
below5_all = np.sum(mass.data.data < 5)
print('Mass median:', median_mass)
print('Total: ', len(mass.compressed()), '/', len(mass))
print('Sources below 5 Msun:', below5, 'out of', np.sum(~mass.mask))
print('-' * 80)
print('[ALL] Mass median:', median_mass_all)
print('[ALL] Total: ', len(mass.data.data), '/', len(mass))
print('[ALL] Sources below 5 Msun:', below5_all, 'out of', len(mass.data.data))
print('=' * 80)

# Bins Toomre Q
toomreq = summary['toomre_Q']
bin_edges_toomreq = np.histogram_bin_edges(toomreq.compressed(), bins='fd')
counts_toomreq, bins_toomreq = np.histogram(toomreq.compressed(),
                                            bins=bin_edges_toomreq)
counts_toomreq_all, bins_toomreq_all = np.histogram(toomreq.data.data,
                                                    bins=bin_edges_toomreq)
median_toomreq = np.ma.median(toomreq)
median_toomreq_all = np.ma.median(toomreq.data.data)
print('Q median:', median_toomreq)
print('Total: ', len(toomreq.compressed()), '/', len(toomreq))
print('Unstable: ', np.ma.sum(toomreq < 1))
print('-' * 80)
print('[ALL] Q median:', median_toomreq_all)
print('[ALL] Total: ', len(toomreq.data.data), '/', len(toomreq))

# By molecule
by_molecule = summary.group_by('molec')

# Figure
plt.style.use(['paper', 'aspect_auto'])
fig = plt.figure(figsize=figsize)
ax1 = fig.add_axes((0.08, 0.56, 0.4, 0.4))
ax2 = fig.add_axes((0.578, 0.56, 0.4, 0.4))
ax3 = fig.add_axes((0.08, 0.06, 0.4, 0.4))
ax4 = fig.add_axes((0.578, 0.06, 0.4, 0.4))
loc = 0.025, 0.92

# Plot alpha
N, bins, patches = ax1.hist(bins_alpha[:-1], bins_alpha, weights=counts_alpha, label='Total')
for patch in patches:
    patch.set_edgecolor('w')
colors = {'CH3CN': 'g',
          'CH3OH': 'r'}
edges = {'CH3CN': '#a5d6b2',
         'CH3OH': '#e39ad8'}
for molec, group in zip(by_molecule.groups.keys, by_molecule.groups):
    if molec['molec'] not in colors:
        continue
    alpha = np.ma.masked_where(group['alpha']>=2, group['alpha'])
    counts_group, _ = np.histogram(-alpha.compressed(), bins=bin_edges_alpha)
    N, bins, patches = ax1.hist(bins_alpha[:-1], bins_alpha, weights=counts_group,
                                label=molec['molec'].replace('3', '$_3$'),
                                color=colors[molec['molec']], alpha=0.6)
    for patch in patches:
        patch.set_edgecolor(edges[molec['molec']])
ax1.annotate('(a)', loc, xytext=loc, xycoords='axes fraction')
ax1.axvline(median_alpha, color='r', linestyle='--',
            label=f'Median = {median_alpha:.1f}')
ax1.legend(loc=(0.01, 0.5))
ax1.set_ylim(0, 12)
ax1.set_xlabel(r'Index $\alpha$')
ax1.set_ylabel('Number')

N, bins, patches = ax2.hist(bins_mass_all[:-1], bins_mass_all,
                            weights=counts_mass_all,
                            color='#8c918d',
                            alpha=0.6,
                            label='With outliers')
N, bins, patches = ax2.hist(bins_mass[:-1], bins_mass,
                            weights=counts_mass,
                            label='Without outliers')
ax2.annotate('(b)', loc, xytext=loc, xycoords='axes fraction')
ax2.axvline(median_mass, color='r', linestyle='--',
           label=f'Median = {median_mass:.1f} ' + r'M$_\odot$')
ax2.legend()
ax2.set_ylim(0, 23)
#ax2.set_ylim(0, int(np.max(np.ceil(counts_mass)) + 2))
ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
ax2.set_xlabel(r'Condensation mass (M$_\odot$)')
ax2.set_ylabel('Number')
for patch in patches:
    patch.set_edgecolor('w')

N, bins, patches = ax3.hist(bins_radius_all[:-1], bins_radius_all,
                            weights=counts_radius_all,
                            color='#8c918d',
                            alpha=0.6,
                            label='With outliers')
N, bins, patches = ax3.hist(bins_radius[:-1], bins_radius,
                            weights=counts_radius,
                            label='Without outliers')
ax3.annotate('(c)', loc, xytext=loc, xycoords='axes fraction')
ax3.axvline(median_radius, color='r', linestyle='--',
            label=f'Median = {median_radius:.0f} au')
ax3.legend()
ax3.set_ylim(0, 12)
ax3.set_xlabel('Condensation radius (au)')
ax3.set_ylabel('Number')
for patch in patches:
    patch.set_edgecolor('w')

N, bins, patches = ax4.hist(bins_toomreq_all[:-1], bins_toomreq_all,
                            weights=counts_toomreq_all,
                            color='#8c918d',
                            alpha=0.6,
                            label='With outliers')
N, bins, patches = ax4.hist(bins_toomreq[:-1], bins_toomreq,
                            weights=counts_toomreq,
                            label='Without outliers')
ax4.annotate('(d)', loc, xytext=loc, xycoords='axes fraction')
ax4.axvline(median_toomreq, color='r', linestyle='--',
            label=f'Median = {median_toomreq:.2f}')
ax4.legend()
ax4.set_ylim(0, int(np.max(np.ceil(counts_toomreq_all)) + 2))
ax4.yaxis.set_major_locator(MaxNLocator(integer=True))
ax4.set_xlabel('Toomre $Q$')
ax4.set_ylabel('Number')
for patch in patches:
    patch.set_edgecolor('w')

fig.savefig(FIGURES / 'papers/dihca6_alpha_histogram.png', bbox_inches='tight')
fig.savefig(FIGURES / 'papers/dihca6_alpha_histogram.pdf', bbox_inches='tight')
#fig.savefig(FIGURES / 'papers/dihca6_alpha_histogram.eps', bbox_inches='tight')
