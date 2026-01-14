"""Synchronize summary tables.

This scripts also compiles the results in other scripts:
    - `dihca6_masses.py`: calculates the masses.
    - `dihca6_toomreq.py`: calculates the Toomre-Q
"""
from pathlib import Path

from astropy.modeling import models
from astropy.coordinates import SkyCoord
from astropy.table import QTable, Table
from radio_beam import Beams
import astropy.constants as ct
import astropy.units as u
import numpy as np

from dihca6_load_tables import MASS, RADIUS

# Tables
tab_name = Path('../../results/tables/dihca6_summary.csv')
qtab_name = tab_name.with_suffix('.ecsv')

# Rounding function
def round_to_significant_figures(number, sig_figs):
    #if number == 0:
    #    return 0.0
    # Calculate the power of 10 to shift the number
    power = np.floor(np.log10(abs(number.value))) - (sig_figs - 1)
    # Scale, round, and then scale back
    rounded_number = np.round(number / (10**power)) * (10**power)
    return rounded_number

def set_value(table, key, val):
    try:
        table.add_column(val, name=key)
    except ValueError:
        table.replace_column(key, val)

# Units of summary Table
units = {
    'Source': None,
    'ALMA': None,
    'ALMAe': None,
    'molec': None,
    'ra': None,
    'dec': None,
    'distance': u.kpc,
    'vlsr': u.km/u.s,
    'pa': u.deg,
    'alpha': u.Unit(1),
    'e_alpha': u.Unit(1),
    'v100': u.km/u.s,
    'e_v100': u.km/u.s,
    'vsys': u.km/u.s,
    'e_vsys': u.km/u.s,
    'offset': u.mas,
    'e_offset': u.mas,
    'v100': u.km/u.s,
    'e_v100': u.km/u.s,
    'mass_cen': u.M_sun,
    'e_mass_cen': u.M_sun,
    'lum': u.L_sun,
    'wlum': u.L_sun,
    'disk_radius': u.au,
    'disk_radius_dec': u.au,
    'temp': u.K,
    'flux': u.mJy,
    'peak_int': u.mJy,
    'bmaj': u.arcsec,
    'bmin': u.arcsec,
}
sorted_values = ['Source', 'ALMA', 'ALMAe', 'ra', 'dec', 'distance', 'vlsr',
                 'molec', 'pa', 'alpha', 'e_alpha', 'v100', 'e_v100', 'vsys',
                 'e_vsys', 'offset', 'e_offset', 'mass_cen', 'e_mass_cen',
                 'lum', 'wlum', 'temp', 'flux', 'peak_int', 'bmaj', 'bmin',
                 'disk_radius', 'disk_radius_dec', 'dust_mass',
                 'dust_mass_corr', 'col_den_peak', 'surface_den', 'toomre_Q',
                 'op_depth_peak']

# Sync to QTable
table = Table.read(tab_name, units=units)
if not qtab_name.exists():
    qtable = QTable(table)
    coord = SkyCoord(ra=table['ra'], dec=table['dec'], unit=(u.hourangle, u.deg), frame='icrs')
    qtable.add_column(coord, name='position', index=5)
else:
    qtable = QTable.read(qtab_name)
    for key in units:
        set_value(qtable, key, table[key])
qtable.write(qtab_name, format='ascii.ecsv', overwrite=True)

# Calculate mass
# Hot dust in high-mass disks (Yamamuro, Tanaka & Okuzumi 2025)
kappa = 0.24 * u.cm**2 / u.g
Rdg = 0.01
wav = 1.33 * u.mm
bb = models.BlackBody(temperature=qtable['temp'])
mass = qtable['flux'] * qtable['distance']**2 / (Rdg * kappa * bb(wav))
mass = mass.to(u.M_sun, equivalencies=u.dimensionless_angles())
set_value(qtable, 'dust_mass', mass)

# Calculate peak column density
mH = 1.008 * u.u
mu = 2.8
beam = Beams(qtable['bmaj'], qtable['bmin'])
colden = qtable['peak_int'] / (beam.sr * bb(wav) * Rdg * kappa * mu * mH)
#tau_peak = Rdg * kappa * mu * mH * colden
#tau_peak = tau_peak.to(1)
set_value(qtable, 'col_den_peak', colden)
#set_value(qtable, 'op_depth_peak', tau_peak)

# Optical depth
tau_peak = -np.log(1 - qtable['peak_int'] / (beam.sr * bb(wav)))
nan_val = np.isnan(tau_peak)
set_value(qtable, 'op_depth_peak', tau_peak)
tau_peak = tau_peak.to(1)
print('NaN sources: ')
for src, ind in zip(qtable['Source'][nan_val], qtable['ALMAe'][nan_val]):
    print(f'{src} ALMAe{ind}')

# Calculate mass corected by dust opacity at peak
mass_corr = tau_peak * mass * beam.sr * bb(wav) / qtable['peak_int']
mass_corr[nan_val] = mass[nan_val] 
#mass_corr = mass * tau_peak / (1 - np.exp(-tau_peak))
mass_corr = mass_corr.to(u.M_sun)
set_value(qtable, 'dust_mass_corr', mass_corr)

# Calculate surface density
sigma = qtable[MASS] / (np.pi * qtable[RADIUS]**2)
sigma = sigma.to(u.g / u.cm**2)
set_value(qtable, 'surface_den', sigma)

#tau = Rdg * kappa * sigma
#tau = tau.to(1)
#set_value(qtable, 'surface_den', sigma)
#set_value(qtable, 'op_depth', tau)
#
## Alternative corrected mass
#mass_corr = mass * tau / (1 - np.exp(-tau))
#mass_corr = mass_corr.to(u.M_sun)
#set_value(qtable, 'dust_mass_corr', mass_corr)

# Calculate Toomre-Q
total_mass = qtable['mass_cen'] + qtable[MASS]
speed_sound = np.sqrt(7 * ct.k_B * qtable['temp'] / (5 * mu * mH))
omega = np.sqrt(ct.G * total_mass / qtable[RADIUS]**3)
#tau = Rdg * kappa * sigma
#tau = tau.to(1)
#set_value(qtable, 'op_depth_corr', tau)
# Toomre Q
toomre_q = speed_sound * omega / (np.pi * ct.G * sigma)
toomre_q = toomre_q.to(1)
set_value(qtable, 'toomre_Q', toomre_q)

# Round values and copy results colmuns
cols = [key for key in sorted_values if key not in units]
for col in cols:
    val = round_to_significant_figures(qtable[col], 2)
    set_value(table, col, val)
table = table[sorted_values]
qtable = qtable[sorted_values]
table.write(tab_name, format='ascii.csv', overwrite=True)
table.write(tab_name.with_suffix('.dat'), format='ascii.fixed_width',
            overwrite=True)
qtable.write(qtab_name, format='ascii.ecsv', overwrite=True)

# Build latex table
ltable = Table()
cols = ['Source', 'ALMAe', 'temp', 'wlum', 'flux', 'peak_int', 'op_depth_peak', 
        RADIUS, MASS, 'surface_den', 'toomre_Q']
for col in cols:
    ltable[col] = table[col]
ltable.write(tab_name.with_suffix('.tex'), format='ascii.fixed_width', overwrite=True)
