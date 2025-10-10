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
print('-'*80)

# Central mass and luminosity
lum = table['wlum']
mass = table['mass_cen']
lumvmass = spearmanr(np.log10(mass), np.log10(lum))
print('With outliers:')
print(f'Luminosity vs. mass: {lumvmass.statistic}',
      f'(p-value = {lumvmass.pvalue})')
mask_G10 = table['Source'] == 'G10.62-0.38'
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
print(f'Luminosity vs. central mass: {lumvmass.statistic}',
      f'(p-value = {lumvmass.pvalue})')

# Fit
#fit = np.polyfit(np.log10(mass), np.log10(lum), 1)
#print(fit)
fitter = LinearLSQFitter()
model = Linear1D(slope=2.5, intercept=0.1)
fit = fitter(model, np.log10(mass.compressed()), np.log10(lum.compressed()))
print('M-L relation:', fit)
print('-'*80)

# Lstar/Mstar vs others
loverm = lum/mass
mdust = np.ma.array(table['dust_mass'], mask=loverm.mask)
radius = np.ma.array(table['disk_radius_dec'], mask=loverm.mask)
lmvsmdust = spearmanr(np.log10(mdust.compressed()), np.log10(loverm.compressed()))
lmvsradius = spearmanr(np.log10(radius.compressed()), np.log10(loverm.compressed()))
print('Valid Points: ', len(loverm.compressed()))
print((f'L/M vs gas mass: {lmvsmdust.statistic}'
       f'(p-value = {lmvsmdust.pvalue})'))
print((f'L/M vs radius: {lmvsradius.statistic}'
       f'(p-value = {lmvsradius.pvalue})'))
print('-'*80)

# Mg vs R
radius = np.ma.masked_where(mask_G10, table['disk_radius_dec'])
mdust = np.ma.array(table['dust_mass'], mask=radius.mask)
radiusvsmass = spearmanr(radius.compressed(), mdust.compressed())
fitter = LinearLSQFitter()
model = Linear1D(slope=2.5, intercept=0.1)
fit = fitter(model, radius.compressed(), mdust.compressed())
print('Valid Points: ', len(radius.compressed()))
print((f'Radius vs gas mass: {radiusvsmass.statistic}'
       f'(p-value = {radiusvsmass.pvalue})'))
print('-'*80)

# Condensations
print('Disk/stellar mass vs radius:')
intermediate = RESULTS / 'tables/beltran_dewit_im_stars.csv'
highmass = RESULTS / 'tables/beltran_dewit_hm_stars.csv'
intermediate = Table.read(intermediate)
highmass = Table.read(highmass)
ratio1 = np.ma.array(table['dust_mass']/table['mass_cen'])
ratio2 = np.ma.append(ratio1, np.ma.array(intermediate['Mgas']/intermediate['Mstar']))
ratio2 = np.ma.append(ratio2, np.ma.array(highmass['Mgas']/highmass['Mstar']))
radius1 = np.ma.array(table['disk_radius_dec'])
radius2 = np.ma.append(radius1, np.ma.array(intermediate['radius']))
radius2 = np.ma.append(radius2, np.ma.array(highmass['radius']))
ratiovradius = spearmanr(np.log10(radius2.compressed()),
                         np.log10(ratio2.compressed()))
print((f'All data: {ratiovradius.statistic}'
       f'(p-value = {ratiovradius.pvalue})'))
# Only DIHCA
dihca_ratiovradius = spearmanr(np.log10(radius1.compressed()),
                               np.log10(ratio1.compressed()))
print((f'DIHCA data: {dihca_ratiovradius.statistic}'
       f'(p-value = {dihca_ratiovradius.pvalue})'))
print('-'*80)

# Masses
print('Stellar vs disk mass:')
mdust = np.ma.masked_where(table['Source'] == 'G10.62-0.38',
                           table['dust_mass'])
mcen = np.ma.array(table['mass_cen'], mask=mdust.mask)
mcenvmdust = spearmanr(np.log10(mdust.compressed()),
                       np.log10(mcen.compressed()))
print((f'DIHCA data: {mcenvmdust.statistic}'
       f'(p-value = {mcenvmdust.pvalue})'))
print('-'*80)

# Alpha and condensations
print('alpha vs radius:')
radius = np.ma.masked_where(alpha.mask, table['disk_radius_dec'])
alpha_cond = np.ma.masked_where(table['dust_mass'].mask, alpha)
alphavsradius = spearmanr(alpha_cond.compressed(), radius.compressed())
print((f'DIHCA data: {alphavsradius.statistic}'
       f'(p-value = {alphavsradius.pvalue})'))
print('-'*80)

# Mg/Mc vs distance
print('Stellar/disk mass vs distance:')
ratiovdistance = spearmanr(np.ma.compressed(np.ma.array(table['distance'],
                                                        mask=ratio1.mask)),
                           ratio1.compressed())
print((f'All data: {ratiovdistance.statistic}'
       f'(p-value = {ratiovdistance.pvalue})'))
print('-'*80)

# High mass populations
ratio_kstest = ks_2samp(table['dust_mass']/table['mass_cen'],
                        highmass['Mgas']/highmass['Mstar'])
radius_kstest = ks_2samp(table['disk_radius_dec'], highmass['radius'])
print('KS test for Md/Mc:', ratio_kstest)
print('KS test for Rd:', radius_kstest)

