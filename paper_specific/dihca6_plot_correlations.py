"""Plot correlation map."""
from itertools import product

from astropy.table import Table
from numpy.lib import recfunctions as rfn
from tile_plotter.utils import tick_formatter
from scipy.interpolate import interp1d
from scipy.stats import spearmanr
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from common_paths import RESULTS, FIGURES
from utils import round_to_significant_figures
from dihca6_load_tables import load_summary, MASS, RADIUS

figsize = (6, 5)

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw=None, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (M, N).
    row_labels
        A list or array of length M with the labels for the rows.
    col_labels
        A list or array of length N with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current Axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if ax is None:
        ax = plt.gca()

    if cbar_kw is None:
        cbar_kw = {}

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cax = ax.figure.add_axes([ax.get_position().x1+0.01, ax.get_position().y0,
                              0.02, ax.get_position().height])
    cbar = ax.figure.colorbar(im, ax=ax, cax=cax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(range(data.shape[1]), labels=col_labels,
                  rotation=-30, ha="right", rotation_mode="anchor", size=12)
    ax.set_yticks(range(data.shape[0]), labels=row_labels, size=12)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False,
                   right=False, direction='out', length=7, width=1)
    ax.tick_params(which='minor', top=False, bottom=False, right=False,
                   left=False)

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

def annotate_heatmap(im, pval, data=None, valfmt="{x:.2f}",
                     textcolors=("black", "white"),
                     threshold=0.39, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt([data[i, j], pval[i, j]], None),
                                **kw)
            texts.append(text)

    return texts

# Select columns
cols = ['distance', 'alpha', 'mass_cen', MASS, RADIUS]
names = ['$d$', r'$\alpha$', r'$M_c \sin^2 i$', '$M_g$', '$R$']
selected = load_summary(masked=True, selected=cols)

# Correlations
nvals = len(cols)
corr, pval = np.ones((nvals, nvals)), np.ones((nvals, nvals))
for i, j in product(range(nvals), range(nvals)):
    if i == j:
        continue
    mask = selected[cols[i]].mask | selected[cols[j]].mask
    col1 = np.ma.masked_where(mask, selected[cols[i]])
    col2 = np.ma.masked_where(mask, selected[cols[j]])
    corr[i, j], pval[i, j] = spearmanr(col1.compressed(), col2.compressed())

# Plot
fig, ax = plt.subplots(1, 1, figsize=figsize)
#ax = fig.add_axes((0.16, 0.12, 0.82, 0.82))
im, _ = heatmap(corr, names, names, ax=ax,
                cmap="PuOr", vmin=-1, vmax=1,
                cbarlabel="Correlation coefficient")

def func(x, pos):
    val = f"{x[0]:.2f}".replace("1.00", "")
    if val != '':
        val += '\n'
        if x[1] < 10**-3:
            lg = int(np.floor(np.log10(x[1])))
            num = x[1] / 10**lg
            val += f'({num:.0f}' + r'$\times 10^{' + f'{lg}' + '}$)'
        else:
            rounded, power = round_to_significant_figures(x[1], 2)
            if power < 0:
                fmt = f'({{0:.{abs(int(power))}f}})'
                val += fmt.format(rounded)
            else:
                val += f'({rounded})'
    return val

annotate_heatmap(im, pval, valfmt=matplotlib.ticker.FuncFormatter(func), size=10)

fig.savefig(FIGURES / 'papers/dihca6_correlation_map.png', bbox_inches='tight')
fig.savefig(FIGURES / 'papers/dihca6_correlation_map.pdf', bbox_inches='tight')
