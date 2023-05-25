"""Generate a configuration file per source."""
from pathlib import Path

from astro_source.source import Source, SubSource
import astropy.units as u
import numpy as np

# Constants
props = {
    'G10.62-0.38': {'distance': 3.5*u.kpc, 'vlsr': -2*u.km/u.s},
    'IRAS_180891732': {'distance': 3.6*u.kpc, 'vlsr': 32*u.km/u.s},
    'IRAS_181622048': {'distance': 1.7*u.kpc, 'vlsr': 12*u.km/u.s},
    'G11.1-0.12': {'distance': 3.5*u.kpc, 'vlsr': 30*u.km/u.s},
    'W33A': {'distance': 3.8*u.kpc, 'vlsr': 38.5*u.km/u.s},
    'G5.89-0.37': {'distance': 3*u.kpc, 'vlsr': 10*u.km/u.s},
    'G11.92-0.61': {'distance': 3.4*u.kpc, 'vlsr': 35*u.km/u.s},
    'G333.23-0.06': {'distance': 3.7*u.kpc, 'vlsr': -87.2*u.km/u.s},
    'G335.579-0.272': {'distance': 3.25*u.kpc, 'vlsr': -46.9*u.km/u.s},
    'G14.22-0.50_S': {'distance': 2*u.kpc, 'vlsr': 22*u.km/u.s},
    'G24.60+0.08': {'distance': 3.6*u.kpc, 'vlsr': 53.4*u.km/u.s},
    'IRAS_18337-0743': {'distance': 3.8*u.kpc, 'vlsr': 60*u.km/u.s},
    'G336.01-0.82': {'distance': 3.8*u.kpc, 'vlsr': -47.4*u.km/u.s},
    'G335.78+0.17': {'distance': 3.8*u.kpc, 'vlsr': -49.5*u.km/u.s},
    'G333.12-0.56': {'distance': 2.4*u.kpc, 'vlsr': -56.4*u.km/u.s},
    'G333.46-0.16': {'distance': 2.4*u.kpc, 'vlsr': -42.5*u.km/u.s},
    'G343.12-0.06': {'distance': 2.0*u.kpc, 'vlsr': -30.4*u.km/u.s},
    'G351.77-0.54': {'distance': 2.2*u.kpc, 'vlsr': -3.6*u.km/u.s},
    'G34.43+0.24': {'distance': 1.6*u.kpc, 'vlsr': 57.6*u.km/u.s},
    'G29.96-0.02': {'distance': 3.5*u.kpc, 'vlsr': 98*u.km/u.s},
    'G35.03+0.35_A': {'distance': 3.2*u.kpc, 'vlsr': 48*u.km/u.s},
    'G35.20-0.74_N': {'distance': 2.2*u.kpc, 'vlsr': 30*u.km/u.s},
    'IRAS_165474247': {'distance': 2.0*u.kpc, 'vlsr': -30.4*u.km/u.s},
    'IRAS_165623959': {'distance': 1.7*u.kpc, 'vlsr': -14*u.km/u.s},
    'NGC6334I': {'distance': 1.7*u.kpc, 'vlsr': -8*u.km/u.s},
    'NGC_6334_I_N': {'distance': 1.7*u.kpc, 'vlsr': -5*u.km/u.s},
    'G34.43+0.24MM2': {'distance': 1.6*u.kpc, 'vlsr': 57.6*u.km/u.s},
    'G35.13-0.74': {'distance': 2.2*u.kpc, 'vlsr': 35*u.km/u.s},
    'IRAS_181511208': {'distance': 3*u.kpc, 'vlsr': 32.8*u.km/u.s},
    'IRAS_18182-1433': {'distance': 3.6*u.kpc, 'vlsr': 59*u.km/u.s},
    'IRDC_182231243': {'distance': 3.7*u.kpc, 'vlsr': 45.3*u.km/u.s},
}
catalogues = Path('/data/share/binary_project/catalogue')
catalogue = catalogues / 'sources_config8.dat'
catalogue_c5 = catalogues / 'core_catalogue_extended.csv'
configs = Path('/data/share/binary_project/configs')

# Open c5 catalogue
catc5 = np.genfromtxt(catalogue_c5, delimiter=',', skip_header=1,
                      usecols=(0,1,2,3,4),
                      names=('name', 'i', 'ra', 'dec', 'radius'),
                      dtype=None)

# Iterate over data
with catalogue.open() as fl:
    for line in fl.readlines():
        # Get information
        basedir, ra, dec = line.split()
        
        # Store
        name = Path(basedir).name
        src = Source.from_values(name, ra=ra, dec=dec, frame='icrs',
                                 basedir=basedir, **props[name])

        # Insert subsources
        if name in ['IRAS_165474247', 'G343.12-0.06']:
            catname = 'IRAS_16547_G343'
        else:
            catname = name
        aux = catc5['name'].astype(np.unicode_) == catname
        for row in catc5[aux]:
            num = row['i']
            subname = f'ALMA{num}'
            info = {'ra': row['ra'].astype(np.unicode_),
                    'dec': row['dec'].astype(np.unicode_),
                    'radius': f"{row['radius']} arcsec"}
            src.subsources[subname] = SubSource.from_dict(info, name=subname)

        # Write
        src.write(configs / f'{name}.cfg')
