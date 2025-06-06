"""Calculate mass upper limits from pv map values."""
from configparseradv.configparser import ConfigParserAdv as ConfigParser
import astropy.constants as ct
import astropy.units as u
import numpy as np

from common_paths import CONFIGS

sources = {
    'G11.92-0.61_alma1b': ((-0.069 * u.arcsec,),
                           (33.0 * u.km/u.s,)),
    'G333.12-0.56_alma2': ((-0.17 * u.arcsec, 0.018 * u.arcsec),
                           (-59.4 * u.km/u.s, -50.1 * u.km/u.s)),
    'G333.46-0.16_alma1': ((-0.19 * u.arcsec, 0.33 * u.arcsec),
                           (-48.5 * u.km/u.s, -39.7 * u.km/u.s)),
    'G343.12-0.06_alma1': ((-0.16 * u.arcsec, 0.23 * u.arcsec),
                           (-40.1 * u.km/u.s, -31.3 * u.km/u.s)),
    'G35.20-0.74_N_alma2': ((-0.32 * u.arcsec, 0.030 * u.arcsec),
                            (26.0 * u.km/u.s, 32.9 * u.km/u.s)), 
    'IRAS_165623959_alma2': ((-0.053 * u.arcsec, 0.079 * u.arcsec),
                             (-14.6 * u.km/u.s, -9.3 * u.km/u.s)),
    'IRAS_18182-1433_alma1': ((-0.077 * u.arcsec, 0.017 * u.arcsec),
                              (61.0 * u.km/u.s, 66.3 * u.km/u.s)),
    'IRAS_18182-1433_alma2': ((-0.035 * u.arcsec, 0.077 * u.arcsec),
                              (57.1 * u.km/u.s, 63.7 * u.km/u.s)),
    'IRAS_18182-1433_alma5': ((0.0 * u.arcsec, 0.036 * u.arcsec),
                              (59.1 * u.km/u.s, 65.0 * u.km/u.s)),
    'NGC_6334_I_N_alma2': ((-0.15 * u.arcsec, 0.11 * u.arcsec),
                           (-8.65 * u.km/u.s, -0.5 * u.km/u.s)),
    'NGC_6334_I_N_alma11': ((-0.087 * u.arcsec,),
                            (-10.1 * u.km/u.s,)),
    'W33A_alma1b': ((-0.17 * u.arcsec,),
                    (31.9 * u.km/u.s,)),
}

config = ConfigParser()
config.read(CONFIGS / 'extracted/summary.cfg')

for section, (offset, vel) in sources.items():
    cfg = config[section]
    d = cfg.getquantity('distance')
    if len(offset) == 2:
        v = np.abs(vel[0] - vel[1]) / 2
        r = np.abs(offset[0] - offset[1]) / 2
    else:
        vlsr = cfg.getquantity('vlsr')
        v = np.abs(vel[0] - vlsr)
        r = np.abs(offset[0])
    r = r.to(u.arcsec).value * d.to(u.pc).value * u.au
    mass = r / ct.G * v**2
    mass = mass.to(u.M_sun)

    print('Results for: ', section)
    print('v: ', v)
    print('r: ', r)
    print('mass: ', mass)
    print('-' * 80)

