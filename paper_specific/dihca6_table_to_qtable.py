"""Convert tables to QTables."""
from pathlib import Path

from astropy.coordinates import SkyCoord
from astropy.table import QTable, Table
import astropy.units as u

tab_name = Path('../../results/tables/dihca6_summary.csv')
units = {
    'Source': None,
    'ALMA': None,
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
table = Table.read(tab_name, units=units)
qtable = QTable(table)
coord = SkyCoord(ra=table['ra'], dec=table['dec'], unit=(u.hourangle, u.deg), frame='icrs')
qtable.add_column(coord, name='position', index=5)
qtable['major_axis'] = qtable['major_axis'].to(u.arcsec)
qtable.write(tab_name.with_suffix('.ecsv'), format='ascii.ecsv')

