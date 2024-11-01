import astropy.units as u
from astropy.modeling import models
import numpy as np

## Beam area
bmin = 0.043 * u.arcsec
bmaj = 0.064 * u.arcsec
fwhm_to_sigma = 1. / (8 * np.log(2))**0.5
beam_area = 2. * np.pi * (bmaj*bmin*fwhm_to_sigma**2)
beam_area = beam_area.to(u.sr)


distance = 3.25 * u.kpc
Rgd = 100
kappanu = 1 * u.cm**2 / u.g
sigma = 66E-6 * u.Jy
temp = 10 * u.K
bnu = models.BlackBody(temp)
freq = 2.261500254156E+11 * u.Hz

mass = (5. * sigma) * distance**2 * Rgd
mass = mass / (kappanu * u.sr * bnu(freq))
mass = mass.decompose().to(u.M_sun)

print(f'Mass sensitivity = {mass.value} {mass.unit}')
