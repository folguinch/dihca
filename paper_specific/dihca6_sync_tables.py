"""Synchronize summary tables.

This scripts also compiles the results in other scripts:
    - `dihca6_masses.py`: calculates the masses.
    - `dihca6_toomreq.py`: calculates the Toomre-Q
"""
from pathlib import Path

from astropy.modeling import models
from astropy.coordinates import SkyCoord
from astropy.table import QTable, Table
import astropy.constants as ct
import astropy.units as u
import numpy as np

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
    'v100_kep': u.km/u.s,
    'e_v100_kep': u.km/u.s,
    'mass_cen': u.M_sun,
    'e_mass_cen': u.M_sun,
    'lum': u.L_sun,
    'wlum': u.L_sun,
    'disk_mass': u.M_sun,
    'disk_radius': u.au,
    'temp': u.K,
    'flux': u.mJy,
    'major_axis': u.deg,
}

# Sync to QTable
table = Table.read(tab_name, units=units)
if not qtab_name.exists():
    qtable = QTable(table)
    coord = SkyCoord(ra=table['ra'], dec=table['dec'], unit=(u.hourangle, u.deg), frame='icrs')
    qtable.add_column(coord, name='position', index=5)
    qtable['major_axis'] = qtable['major_axis'].to(u.arcsec)
else:
    qtable = QTable.read(qtab_name)
    for key in units:
        qtable.replace_column(key, table[key])
qtable.write(qtab_name, format='ascii.ecsv', overwrite=True)

# (Re)calculate mass
# Hot dust in high-mass disks (Yamamuro, Tanaka & Okuzumi 2025)
kappa = 0.24 * u.cm**2 / u.g
Rdg = 0.01
wav = 1.33 * u.mm
bb = models.BlackBody(temperature=qtable['temp'])
mass = qtable['flux'] * qtable['distance']**2 / (Rdg * kappa * bb(wav))
mass = mass.to(u.M_sun, equivalencies=u.dimensionless_angles())
try:
    qtable.add_column(mass, name='dust_mass')
except ValueError:
    qtable.replace_column('dust_mass', mass)

# (Re)calculate Toomre-Q
# Parameters
mH = 1.008 * u.u
total_mass = qtable['mass_cen'] + qtable['dust_mass']
speed_sound = np.sqrt(7 * ct.k_B * qtable['temp'] / (5 * 2.8 * mH))
omega = np.sqrt(ct.G * total_mass / qtable['disk_radius']**3)
sigma = qtable['dust_mass'] / (np.pi * qtable['disk_radius']**2)
sigma = sigma.to(u.g / u.cm**2)
tau = Rdg * kappa * sigma
tau = tau.to(1)
try:
    qtable.add_column(sigma, name='surface_den')
    qtable.add_column(tau, name='op_depth')
except ValueError:
    qtable.replace_column('surface_den', sigma)
    qtable.replace_column('op_depth', tau)
# Toomre Q
toomre_q = speed_sound * omega / (np.pi * ct.G * sigma)
toomre_q = toomre_q.to(1)
try:
    qtable.add_column(toomre_q, name='toomre_Q')
except ValueError:
    qtable.replace_column('toomre_Q', toomre_q)

# Round values and copy results colmuns
cols = ['dust_mass', 'surface_den', 'op_depth', 'toomre_Q']
for col in cols:
    val = round_to_significant_figures(qtable[col], 2)
    try:
        table.add_column(val, name=col)
    except ValueError:
        table.replace_column(col, val)
table.write(tab_name, format='ascii.csv', overwrite=True)
table.write(tab_name.with_suffix('.dat'), format='ascii.fixed_width', overwrite=True)
