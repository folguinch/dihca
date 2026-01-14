"""Calculate the angles between gradients and outflow, and stats."""
from astropy.table import Table
import numpy as np

from common_paths import RESULTS

# Paths
table = RESULTS / 'tables/dihca6_detections.csv'

# Read table
table = Table.read(table)

# Select columns
pa_grad = table['pa']
pa_out = table['pa_out']

# Absolute angles
ind = pa_grad < 0
pa_grad[ind] = 360 + pa_grad[ind] 
ind = pa_out < 0
pa_out[ind] = 360 + pa_out[ind]

# Difference
delta = np.abs(pa_grad - pa_out)
ind = delta > 180
delta[ind] = 360 - delta[ind]

for m, *val in zip(delta.mask, pa_grad,  pa_out, delta):
    if m: continue
    print(val)

# Stats
total = np.sum(~delta.mask)
ind10 = (delta >= 80) & (delta <= 100)
ind20 = (delta >= 70) & (delta <= 110)
ind45 = (delta >= 45) & (delta <= 135)
print('Total: ', total)
print('Delta 90+/-10: ', 100*np.sum(ind10)/total)
print('Delta 90+/-20: ', 100*np.sum(ind20)/total)
print('Delta 90+/-45: ', 100*np.sum(ind45)/total)
