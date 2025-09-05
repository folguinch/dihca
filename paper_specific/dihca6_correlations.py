"""DIHCA VI: Spearman coeficient for different relations"""
from astropy.modeling.models import Linear1D
from astropy.modeling.fitting import LinearLSQFitter
from astropy.table import Table
from scipy.stats import spearmanr, ks_2samp
import numpy as np

from common_paths import RESULTS

table = RESULTS / 'tables/dihca6_summary.csv'
table = Table.read(table)

# Unfiltered results
alphavdist = spearmanr(table['alpha'], table['distance']*1e3)
massvdist = spearmanr(table['mass_cen'], table['distance']*1e3)
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
lumvmass = spearmanr(np.log10(mass), np.log10(lum))
print('With outliers:')
print(f'Luminosity vs. mass: {lumvmass.statistic}',
      f'(p-value = {lumvmass.pvalue})')
mask1 = (
    (table['Source'] == 'G10.62-0.38') |
    ((table['Source'] == 'G335.579-0.272') & (table['ALMA'] == '1')) |
    (table['Source'] == 'G35.20-0.74 N'))
mask2 = (
    (table['molec'] != 'CH3CN') &
    (table['molec'] != 'CH3OH')
    )
lum = np.ma.masked_where(mask1 | mask2, lum)
mass = np.ma.array(table['mass_cen'], mask=lum.mask)
lumvmass = spearmanr(np.log10(mass.compressed()), np.log10(lum.compressed()))
print('Without outliers:')
print(f'Luminosity vs. mass: {lumvmass.statistic}',
      f'(p-value = {lumvmass.pvalue})')

# Fit
#fit = np.polyfit(np.log10(mass), np.log10(lum), 1)
#print(fit)
print('M-L relation:')
fitter = LinearLSQFitter()
model = Linear1D(slope=2.5, intercept=0.1)
fit = fitter(model, np.log10(mass.compressed()), np.log10(lum.compressed()))
print(fit)

# Condensations
print('Stellar/disk mass vs radius:')
intermediate = RESULTS / 'tables/beltran_dewit_im_stars.csv'
highmass = RESULTS / 'tables/beltran_dewit_hm_stars.csv'
intermediate = Table.read(intermediate)
highmass = Table.read(highmass)
ratio1 = np.array(table['disk_mass']/table['mass_cen'])
ratio2 = np.append(ratio1, np.array(intermediate['Mgas']/intermediate['Mstar']))
ratio2 = np.append(ratio2, np.array(highmass['Mgas']/highmass['Mstar']))
radius = np.array(table['disk_radius'])
radius = np.append(radius, np.array(intermediate['radius']))
radius = np.append(radius, np.array(highmass['radius']))
ratiovradius = spearmanr(np.log10(radius), np.log10(ratio2))
print((f'All data: {ratiovradius.statistic}'
       f'(p-value = {ratiovradius.pvalue})'))
#mask = ratio2 > 0.01
#ratiovradius = spearmanr(np.log10(radius[mask]), np.log10(ratio2[mask]))
#print((f'Without outliers: {ratiovradius.statistic}'
#       f'(p-value = {ratiovradius.pvalue})'))

# Mg/Mc vs distance
print('Stellar/disk mass vs distance:')
ratiovdistance = spearmanr(np.array(table['distance']), ratio1)
print((f'All data: {ratiovdistance.statistic}'
       f'(p-value = {ratiovdistance.pvalue})'))
#mask = ratio1 > 0.01
#ratiovdistance = spearmanr(np.array(condensations['distance'])[mask], ratio1[mask])
#print((f'Without outliers: {ratiovdistance.statistic}'
#       f'(p-value = {ratiovdistance.pvalue})'))

# High mass populations
ratio_kstest = ks_2samp(table['disk_mass']/table['mass_cen'],
                        highmass['Mgas']/highmass['Mstar'])
radius_kstest = ks_2samp(table['disk_radius'], highmass['radius'])
print('KS test for Md/Mc:', ratio_kstest)
print('KS test for Rd:', radius_kstest)

