import numpy as np
import astropy.units as u
import astropy.constants as ct
from astropy.modeling import models

mu = 2.8
mH = 1.008 * u.u
mH = mH.cgs

def tau_nu(col_den: u.Quantity,
           kappa_nu: u.Quantity = 1 * u.cm**2 / u.g,
           dust_to_gas: float = 0.01) -> u.Quantity:
    tau = col_den * mu * mH * kappa_nu * dust_to_gas

    return tau.to(u.Unit(1))

def luminosity(temp: u.Quantity,
               reff: u.Quantity) -> u.Quantity:
    lum = 4 * np.pi * reff**2 * ct.sigma_sb * temp**4
    return lum.to(u.Lsun)

def luminosity_ir(temp: u.Quantity,
                  distance: u.Quantity,
                  solid_angle: u.Quantity,
                  col_den: u.Quantity):
    ngas = col_den * mu * mH
    ctn = 1 + 1.6E-3 * (ngas * u.cm**2/u.g) * (temp/u.K)**1.7
    lbol = 40*u.Lsun * (temp / (10*u.K))**5.7 * (distance / u.kpc)**2 
    lbol = lbol * (solid_angle/u.arcmin**2 ) 
    lbol = lbol * (ngas * u.cm**2/u.g) / ctn

    return lbol.to(u.Lsun)

def dust_mass(flux_peak: u.Quantity,
              flux_int: u.Quantity,
              temp: u.Quantity,
              beam_area: u.Quantity,
              distance: u.Quantity,
              freq: u.Quantity,
              kappa_nu: u.Quantity = 1 * u.cm**2/u.g) -> u.Quantity:

    bnu = models.BlackBody(temp)
    aux = flux_peak / (beam_area * bnu(freq))
    mass = - beam_area.to(u.sr) * flux_int * distance**2
    mass = mass / (kappa_nu * flux_peak * u.sr)
    mass = mass * np.log(1 - aux.decompose())

    return mass.to(u.Msun)

# Constants
distance = 3.25 * u.kpc
freq = 2.261500254156E+11 * u.Hz
tequiv = u.brightness_temperature(freq)
abundance = 1E-6

# Beam area
bmin = 0.043 * u.arcsec
bmaj = 0.064 * u.arcsec
fwhm_to_sigma = 1. / (8 * np.log(2))**0.5
beam_area = 2. * np.pi * (bmaj*bmin*fwhm_to_sigma**2)
beam_area = beam_area.to(u.sr)
bmin_radius = bmin.value * fwhm_to_sigma * distance.to(u.pc).value * u.au
print(f'Minimum radius = {bmin_radius.value:.1f} au')

# For 1a
Fpeak = 20.6 * u.mJy
Fint = 69 * u.mJy
radius = 149 * u.au
Tdust = 230 * u.K

# H2 Column density from CH3OH
col_den = 8.4E19 / abundance / u.cm**2

# Column density
kappa = 1 * u.cm**2 / u.g
N_thick = 1 / (mu*mH*kappa*0.01)
print(N_thick.to(1/u.cm**2))
tau = tau_nu(col_den)
print(f'1a: Optical depth ({freq.value} {freq.unit}) = {tau.value:.1f} {tau.unit}')

# To temperature
T = (Fpeak/beam_area).to(u.K, equivalencies=tequiv)
print(f'1a: Brightness temperature = {T.value:.1f} {T.unit}')

# Luminosity
#lum = luminosity(T, bmin_radius)
#print(f'1a: Luminosity lower limit = {lum.value:.3e} {lum.unit}')
#lum = luminosity(Tdust, bmin_radius)
#print(f'1a: Luminosity lower limit with Tdust = {lum.value:.3e} {lum.unit}')
lum = luminosity(T, radius)
print(f'1a: Luminosity with Tb = {lum.value:.3e} {lum.unit}')
lum = luminosity(Tdust, radius)
print(f'1a: Luminosity with Td = {lum.value:.3e} {lum.unit}')
#lum = luminosity(T, np.sqrt(bmin.value*bmaj.value*fwhm_to_sigma**2) * distance.to(u.pc).value * u.au)
#print(f'1a: Luminosity = {lum.value:.3e} {lum.unit}')
lum = luminosity_ir(T, distance, beam_area, col_den)
print(f'1a: Luminosity (IR) = {lum.value:.3e} {lum.unit}')

# Masses
mass = dust_mass(Fpeak, Fint, Tdust, beam_area, distance, freq)
print(f'1b: Corrected dust mass = {mass.value:.3e} {mass.unit}')

print("-"*40)
# For 1b
Fpeak = 11.8 * u.mJy
Fint = 72 * u.mJy
radius = 192 * u.au
Tdust = 220 * u.K

# H2 Column density from CH3OH
col_den = 5.5E19 / abundance / u.cm**2

# Column density
tau = tau_nu(col_den)
print(f'1b: Optical depth ({freq.value} {freq.unit}) = {tau.value:.1f} {tau.unit}')

# To temperature
T = (Fpeak/beam_area).to(u.K, equivalencies=tequiv)
print(f'1b: Brightness temperature = {T.value:.1f} {T.unit}')

# Luminosity
#lum = luminosity(T, bmin_radius)
#print(f'1b: Luminosity lower limit = {lum.value:.3e} {lum.unit}')
#lum = luminosity(Tdust, bmin_radius)
#print(f'1b: Luminosity lower limit with Tdust = {lum.value:.3e} {lum.unit}')
lum = luminosity(T, radius)
print(f'1b: Luminosity with Tb = {lum.value:.3e} {lum.unit}')
lum = luminosity(Tdust, radius)
print(f'1b: Luminosity with Td = {lum.value:.3e} {lum.unit}')
#lum = luminosity(T, np.sqrt(bmin.value*bmaj.value)/2 * distance.to(u.pc).value * u.au)
#print(f'1b: Luminosity = {lum.value:.3e} {lum.unit}')
lum = luminosity_ir(T, distance, beam_area, col_den)
print(f'1b: Luminosity (IR) = {lum.value:.3e} {lum.unit}')

# Masses
mass = dust_mass(Fpeak, Fint, Tdust, beam_area, distance, freq)
print(f'1b: Corrected dust mass = {mass.value:.3e} {mass.unit}')

print("-"*40)
# For bow
Fpeak = 12.1 * u.mJy
Fint = 93 * u.mJy
Tdust = 220 * u.K
bow_area = 0.01**2 * 282 * u.arcsec**2
radius = np.sqrt(bow_area / np.pi)
radius = radius.to(u.arcsec).value * distance.to(u.pc).value * u.au
print(f'bow: radius = {radius.value:.1f} {radius.unit}')

# H2 Column density from CH3OH
col_den = 2.5E19 / abundance / u.cm**2

# Column density
tau = tau_nu(col_den)
print(f'bow: Optical depth ({freq.value} {freq.unit}) = {tau.value:.1f} {tau.unit}')

# To temperature
T = (Fpeak/beam_area).to(u.K, equivalencies=tequiv)
print(f'bow: Brightness temperature = {T.value:.1f} {T.unit}')

# Luminosity
#lum = luminosity(T, bmin_radius)
#print(f'bow: Luminosity lower limit = {lum.value:.3e} {lum.unit}')
#lum = luminosity(Tdust, bmin_radius)
#print(f'bow: Luminosity lower limit with Tdust = {lum.value:.3e} {lum.unit}')
lum = luminosity(T, radius)
print(f'bow: Luminosity with Tb = {lum.value:.3e} {lum.unit}')
lum = luminosity(Tdust, radius)
print(f'bow: Luminosity with Td = {lum.value:.3e} {lum.unit}')
#lum = luminosity(T, np.sqrt(bmin.value*bmaj.value)/2 * distance.to(u.pc).value * u.au)
#print(f'bow: Luminosity = {lum.value:.3e} {lum.unit}')
lum = luminosity_ir(T, distance, beam_area, col_den)
print(f'bow: Luminosity (IR) = {lum.value:.3e} {lum.unit}')

# Masses
mass = dust_mass(Fpeak, Fint, Tdust, beam_area, distance, freq)
print(f'bow: Corrected dust mass = {mass.value:.3e} {mass.unit}')

print('='*40)
# Hill radius
inclination = 26*u.deg
#col_den = 1E25 * 1/u.cm**2
#sigma = col_den * mu * mH
radius = np.sqrt(bow_area / np.pi)
radius = radius.to(u.arcsec).value * distance.to(u.pc).value * u.au
bow_mass = 1.4 * u.Msun
sigma = bow_mass / (np.pi * radius**2)
length = 0.11 * distance.to(u.pc).value * u.au
vphi = 1.5 * u.km / u.s
radius = 0.14 * distance.to(u.pc).value * u.au / 2
omega = vphi / (radius * np.sin(inclination.to(u.rad)))
omega = omega.to(1/u.s)
print(f'Sigma = {sigma.cgs}')
print(f'Length = {length}')
print(f'Radius = {radius}')
print(f'Omega = {omega}')

rhill = ct.G * sigma * length**2 / (3 * omega**2)
rhill = rhill.to(u.au**3)
rhill = np.power(rhill, 1/3)
print(f'Rhill = {rhill}')



