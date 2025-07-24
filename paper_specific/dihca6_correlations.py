"""DIHCA VI: Spearman coeficient for different relations"""
from astropy.table import Table
from scipy.stats import spearmanr
import numpy as np

from common_paths import RESULTS

table = RESULTS / 'tables/dihca6_summary.csv'
table = Table.read(table)

# Unfiltered results
alphavdist = spearmanr(table['alpha'], table['distance']*1e3)
massvdist = spearmanr(table['mass_cen'], table['distance'])
print(f'Alpha vs. distance: {alphavdist.statistic}',
      f'(p-value = {alphavdist.pvalue})')
print(f'Central mass vs. distance: {massvdist.statistic}',
      f'(p-value = {massvdist.pvalue})')

# Without outliers in alpha
alpha = np.array(table['alpha'])
alpha = np.ma.masked_where(alpha>=2, alpha)
mass = np.ma.array(table['mass_cen'], mask=alpha.mask)
dist = np.ma.array(table['distance'], mask=alpha.mask)
alphavdist = spearmanr(alpha.compressed(), dist.compressed())
massvdist = spearmanr(mass.compressed(), dist.compressed())
print('Without outliers in alpha:')
print(f'Alpha vs. distance: {alphavdist.statistic}',
      f'(p-value = {alphavdist.pvalue})')
print(f'Central mass vs. distance: {massvdist.statistic}',
      f'(p-value = {massvdist.pvalue})')

# Mass and luminosity
lum = table['wlum']
mass = table['mass_cen']
lumvmass = spearmanr(mass, lum)
print('With outliers:')
print(f'Luminosity vs. mass: {lumvmass.statistic}',
      f'(p-value = {lumvmass.pvalue})')
lum = np.ma.masked_where(
    (table['#Source'] == 'G10.62-0.38') | 
    ((table['#Source'] == 'G335.579-0.272') & (table['ALMA'] == '1')) |
    (table['#Source'] == 'G35.20-0.74 N'), lum)
mass = np.ma.array(table['mass_cen'], mask=lum.mask)
lumvmass = spearmanr(mass.compressed(), lum.compressed())
print('Without outliers:')
print(f'Luminosity vs. mass: {lumvmass.statistic}',
      f'(p-value = {lumvmass.pvalue})')

# Fit
fit = np.polyfit(np.log10(mass), np.log10(lum), 1)
print(fit)
