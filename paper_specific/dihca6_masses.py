"""Calculate condensation masses."""
from pathlib import Path

from astropy.modeling import models
from astropy.table import QTable
import astropy.units as u

tab_name = Path('../../results/tables/dihca6_summary.ecsv')
table = QTable.read(tab_name, format='ascii.ecsv')

# Hot dust in high-mass disks (Yamamuro, Tanaka & Okuzumi 2025)
kappa = 0.24 * u.cm**2 / u.g
Rdg = 0.01
wav = 1.33 * u.mm
bb = models.BlackBody(temperature=table['temp'])
mass = table['flux'] * table['distance']**2 / (Rdg * kappa * bb(wav))
mass = mass.to(u.M_sun, equivalencies=u.dimensionless_angles())

try:
    table.add_column(mass, name='dust_mass')
except ValueError:
    table.replace_column('dust_mass', mass)
table.write(tab_name, format='ascii.ecsv', overwrite=True)

## test
#kappa = 0.9 * u.cm**2 / u.g
#nu = 224.6975 * u.GHz
#bb = models.BlackBody(12 * u.K)
#flux = 12.2 * u.mJy
#distance =  5.1 * u.kpc
#mass = flux * distance**2 / (Rdg * kappa * bb(nu))
#print(mass.to(u.M_sun, equivalencies=u.dimensionless_angles()))
