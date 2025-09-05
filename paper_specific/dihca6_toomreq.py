"""Calculate condensation masses."""
from pathlib import Path

from astropy.modeling import models
from astropy.table import QTable
import astropy.constants as ct
import astropy.units as u
import numpy as np

tab_name = Path('../../results/tables/dihca6_summary.ecsv')
table = QTable.read(tab_name, format='ascii.ecsv')

# Parameters
mH = 1.008 * u.u
total_mass = table['mass_cen'] + table['dust_mass']
speed_sound = np.sqrt(7 * ct.k_B * table['temp'] / (5 * 2.8 * mH))
omega = np.sqrt(ct.G * total_mass / table['disk_radius']**3)
sigma = table['dust_mass'] / (np.pi * table['disk_radius']**2)

# Toomre Q
toomre_q = speed_sound * omega / (np.pi * ct.G * sigma)
toomre_q = toomre_q.to(1)

try:
    table.add_column(toomre_q, name='toomre_Q')
except ValueError:
    table.replace_column('toomre_Q', toomre_q)
table.write(tab_name, format='ascii.ecsv', overwrite=True)

## test
#kappa = 0.9 * u.cm**2 / u.g
#nu = 224.6975 * u.GHz
#bb = models.BlackBody(12 * u.K)
#flux = 12.2 * u.mJy
#distance =  5.1 * u.kpc
#mass = flux * distance**2 / (Rdg * kappa * bb(nu))
#print(mass.to(u.M_sun, equivalencies=u.dimensionless_angles()))
