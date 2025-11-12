"""DIHCA VI: Spearman coeficient for different relations."""
from astropy.modeling.models import Linear1D
from astropy.modeling.fitting import LinearLSQFitter
from astropy.table import Table
from scipy.stats import spearmanr, ks_2samp
import numpy as np

from dihca6_load_tables import load_summary, MASS, RADIUS

# Values
table = load_summary(masked=True)
pairs = [
    ('alpha', 'distance'),
    ('mass_cen', 'distance'),
    (f'{MASS}/mass_cen', 'distance'),
    ('mass_cen', 'wlum'),
    ('wlum/mass_cen', RADIUS),
    ('wlum/mass_cen', MASS),
    (RADIUS, MASS),
    (MASS, 'mass_cen'),
    ('alpha', RADIUS)
]
labels = {
    'mass_cen': 'stellar mass',
    'wlum': 'luminosity',
    f'{RADIUS}': 'disk radius',
    f'{MASS}': 'disk mass',
}

def get_value(table, col):
    if '/' in col:
        col1, col2 = col.split('/')
        val = table[col1] / table[col2]
        name1 = labels.get(col1, col1)
        name2 = labels.get(col2, col2)
        name = f'{name1} / {name2}'
    else:
        val = table[col]
        name = labels.get(col, col)

    return val, name.title()

# Calculate correlations
for col1, col2 in pairs:
    val1, name1 = get_value(table, col1)
    val2, name2 = get_value(table, col2)
    print(f'Correlation: {name1} vs {name2}')

    # Unmasked
    corr, pval = spearmanr(val1.data.data, val2.data.data)
    nvals = len(val1.data.data)
    print(f'Unmasked ({nvals}): {corr:.3} (p-value={pval:.1e})')

    # Masked
    mask = val1.mask | val2.mask
    val1 = np.ma.masked_where(mask, val1)
    val2 = np.ma.masked_where(mask, val2)
    corr, pval = spearmanr(val1.compressed(), val2.compressed())
    nvals = len(val1.compressed())
    print(f'Masked ({nvals}): {corr:.3f} (p-value={pval:.1e})')
    print('-'*80)

    if col1 == 'mass_cen' and col2 == 'wlum':
        fitter = LinearLSQFitter()
        model = Linear1D(slope=1.5, intercept=1.5)
        fit = fitter(model,
                     np.log10(val1.compressed()),
                     np.log10(val2.compressed()))
        print('M-L relation:', fit)
        print('-'*80)
