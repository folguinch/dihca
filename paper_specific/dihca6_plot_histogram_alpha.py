"""Plot power law index histogram."""
from astropy.table import Table
from tile_plotter.utils import tick_formatter
import matplotlib.pyplot as plt
import numpy as np

from common_paths import RESULTS, FIGURES

figsize = (10, 10)

# Load tables
summary = RESULTS / 'tables/dihca6_summary.csv'
summary = Table.read(summary)

# Bins
alpha = np.array(summary['alpha'])
alpha = np.ma.masked_where(alpha>=2, alpha)
bin_edges = np.histogram_bin_edges(alpha.compressed(), bins='fd')
counts, bins = np.histogram(alpha.compressed(), bins=bin_edges)
median = np.ma.median(alpha)
print('Alpha median:', median)

# By molecule
by_molecule = summary.group_by('molec')
print(by_molecule.groups.keys)
#counts_methanol, _ = np.histogram(by_molecule, bins=bin_edges)

fig, ax = plt.subplots(1, 1)
ax.hist(bins[:-1], bins, weights=counts, label='Total')
colors = {'CH3CN': 'g',
          'CH3OH':'r'}
for molec, group in zip(by_molecule.groups.keys, by_molecule.groups):
    if molec['molec'] not in colors:
        continue
    alpha = np.ma.masked_where(group['alpha']>=2, group['alpha'])
    counts_group, _ = np.histogram(alpha.compressed(), bins=bin_edges)
    ax.hist(bins[:-1], bins, weights=counts_group, label=molec['molec'],
            color=colors[molec['molec']], alpha=0.6)
ax.legend()
ax.set_xlabel(r'Index $\alpha$')
ax.set_ylabel('Number')

fig.savefig(FIGURES / 'papers/dihca6_alpha_histogram.png', bbox_inches='tight')
fig.savefig(FIGURES / 'papers/dihca6_alpha_histogram.pdf', bbox_inches='tight')
