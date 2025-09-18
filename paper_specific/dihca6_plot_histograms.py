"""Plot power law index histogram."""
from astropy.table import Table
from tile_plotter.utils import tick_formatter
import matplotlib.pyplot as plt
import numpy as np

from common_paths import RESULTS, FIGURES

#figsize = (5, 18)
figsize = (10, 10)

# Load tables
summary = RESULTS / 'tables/dihca6_summary.csv'
summary = Table.read(summary)

# Bins alpha
alpha = np.array(summary['alpha'])
alpha = np.ma.masked_where(alpha >= 2, alpha)
bin_edges_alpha = np.histogram_bin_edges(-alpha.compressed(), bins='fd')
counts_alpha, bins_alpha = np.histogram(-alpha.compressed(),
                                        bins=bin_edges_alpha)
median_alpha = np.ma.median(-alpha)
print('Alpha median:', median_alpha)

# Bins radius
radius = np.ma.array(summary['disk_radius'])
bin_edges_radius = np.histogram_bin_edges(radius.compressed(), bins='fd')
counts_radius, bins_radius = np.histogram(radius.compressed(),
                                          bins=bin_edges_radius)
median_radius = np.ma.median(radius)
below200 = np.sum(radius < 200)
print('Radius median:', median_radius)
print('Sources below 200 au:', below200, 'out of', np.sum(~radius.mask))

# Bins disk mass
mass = np.ma.array(summary['dust_mass'])
bin_edges_mass = np.histogram_bin_edges(mass.compressed(), bins='fd')
counts_mass, bins_mass = np.histogram(mass.compressed(),
                                      bins=bin_edges_mass)
median_mass = np.ma.median(mass)
below5 = np.sum(mass < 5)
print('Mass median:', median_mass)
print('Sources below 5 Msun:', below5, 'out of', np.sum(~mass.mask))

# Bins Toomre Q
toomreq = np.ma.array(summary['toomre_Q'])
bin_edges_toomreq = np.histogram_bin_edges(toomreq.compressed(), bins='fd')
counts_toomreq, bins_toomreq = np.histogram(toomreq.compressed(),
                                            bins=bin_edges_toomreq)
median_toomreq = np.ma.median(toomreq)
print('Q median:', median_toomreq)

# By molecule
by_molecule = summary.group_by('molec')
print(by_molecule.groups.keys)
#counts_methanol, _ = np.histogram(by_molecule, bins=bin_edges)

# Figure
plt.style.use(['paper', 'aspect_auto'])
fig = plt.figure(figsize=figsize)
ax1 = fig.add_axes((0.08, 0.56, 0.4, 0.4))
ax2 = fig.add_axes((0.578, 0.56, 0.4, 0.4))
ax3 = fig.add_axes((0.08, 0.06, 0.4, 0.4))
ax4 = fig.add_axes((0.578, 0.06, 0.4, 0.4))
loc = 0.025, 0.92

# Plot alpha
ax1.hist(bins_alpha[:-1], bins_alpha, weights=counts_alpha, label='Total')
colors = {'CH3CN': 'g',
          'CH3OH':'r'}
for molec, group in zip(by_molecule.groups.keys, by_molecule.groups):
    if molec['molec'] not in colors:
        continue
    alpha = np.ma.masked_where(group['alpha']>=2, group['alpha'])
    counts_group, _ = np.histogram(-alpha.compressed(), bins=bin_edges_alpha)
    ax1.hist(bins_alpha[:-1], bins_alpha, weights=counts_group,
             label=molec['molec'].replace('3', '$_3$'),
             color=colors[molec['molec']], alpha=0.6)
ax1.annotate('(a)', loc, xytext=loc, xycoords='axes fraction')
#ax1.annotate('(a)', loc, xytext=loc, xycoords='axes fraction')
ax1.vlines(median_alpha, 0, 12, colors='r', linestyles='--',
           label=f'Median = {median_alpha:.1f}')
ax1.legend(loc=(0.01, 0.5))
ax1.set_ylim(0, 12)
ax1.set_xlabel(r'Index $\alpha$')
ax1.set_ylabel('Number')

ax2.hist(bins_radius[:-1], bins_radius, weights=counts_radius)
ax2.annotate('(b)', loc, xytext=loc, xycoords='axes fraction')
ax2.vlines(median_radius, 0, 12, colors='r', linestyles='--',
           label=f'Median = {median_radius:.0f} au')
ax2.legend()
ax2.set_ylim(0, 12)
ax2.set_xlabel('Disk radius (au)')
ax2.set_ylabel('Number')

ax3.hist(bins_mass[:-1], bins_mass, weights=counts_mass)
ax3.annotate('(c)', loc, xytext=loc, xycoords='axes fraction')
ax3.vlines(median_mass, 0, 18, colors='r', linestyles='--',
           label=f'Median = {median_mass:.1f} M$_\odot$')
ax3.legend()
ax3.set_ylim(0, 18)
ax3.set_xlabel(r'Disk mass (M$_\odot$)')
ax3.set_ylabel('Number')

ax4.hist(bins_toomreq[:-1], bins_toomreq, weights=counts_toomreq)
ax4.annotate('(d)', loc, xytext=loc, xycoords='axes fraction')
ax4.vlines(median_toomreq, 0, 18, colors='r', linestyles='--',
           label=f'Median = {median_toomreq:.1f}')
ax4.legend()
ax4.set_ylim(0, 18)
ax4.set_xlabel('Toomre $Q$')
ax4.set_ylabel('Number')

fig.savefig(FIGURES / 'papers/dihca6_alpha_histogram.png', bbox_inches='tight')
fig.savefig(FIGURES / 'papers/dihca6_alpha_histogram.pdf', bbox_inches='tight')
fig.savefig(FIGURES / 'papers/dihca6_alpha_histogram.eps', bbox_inches='tight')
