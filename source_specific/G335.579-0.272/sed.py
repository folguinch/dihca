import astropy.units as u
import numpy as np

MM1 = {
    'PACS_BLUE': {
        'wav': 70. * u.um,
        'F': 792. * u.Jy,
        'Ferr': 158. * u.Jy,
    },
    'PACS_GREEN': {
        'wav': 160. * u.um,
        'F': 1456. * u.Jy,
        'Ferr': 582. * u.Jy,
    },
    'PARTEMIS':{
        'wav': 450. * u.um,
        'F': * u.Jy,
        'Ferr': * u.Jy,
    },
    'LABOCA': {
        'wav': 870. * u.um,
        'F': 8.92 * u.Jy,
        'Ferr': 5.34 u.Jy,
    },
    'ALMA_B6': {
        'wav': 1.33 * u.mm,
        'F': 1.4 * u.Jy,
        'Ferr': 0.14 * u.Jy,
    },
    'ALMA_B3': {
        'wav': 3.20 * u.mm,
        'F': 0.101 * u.Jy,
        'Ferr': 0.01 * u.Jy,
    },
    'ATCA'
}
