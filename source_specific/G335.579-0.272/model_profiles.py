import astropy.units as u
from astropy.analytic_functions import blackbody_nu
from scipy.integrate import dblquad
import matplotlib.pyplot as plt
import numpy as np

def power_law_func(x0, y0, p):
    return lambda x: y0 * (x/x0)**p

def power_law(x, x0, y0, p):
    fn = power_law_func(x0, y0, p)
    return fn(x)

def mass(r, r0, rho0):
    m = 8*np.pi/3. * (r * r0)**1.5 * rho0
    return m.to(u.M_sun)

def rthin(rout, rho0, r0, rgd=100., kappa=1.*u.cm**2/u.g):
    A = rgd / (2. * kappa * rho0 * r0**1.5)
    B = rout**-0.5
    r = (A + B)**-2

    return r.to(u.au)

def mdust(fnu, d, nu, t, Rdg=1/100., kappa=1.*u.cm**2/u.g):
    nu = nu.to(u.GHz, equivalencies=u.spectral())
    d = d.to(u.cm)
    Bnu = blackbody_nu(nu, t).to(u.W/u.m**2/u.Hz, u.dimensionless_angles())
    Bnu = Bnu.cgs.decompose()
    mass = fnu.decompose() * d**2 / (Rdg * kappa * Bnu)

    return mass.to(u.M_sun)

# Model parameters
p = -1.5
q = -0.5
a = 2000. * u.au
x = 1.E-8
rho_a = 2.868E-16 * u.g/u.cm**3
T_a = 33 * u.K

# Observed
Rd = 710 * u.au
d = 3.25 * u.kpc
F = 566 * u.mJy
nu = 226.2 * u.GHz
M300 = 6.2 * u.M_sun

# Determine thin radius
Rthin = rthin(Rd, rho_a, a)
Rthin2 = rthin(a, rho_a, a)
print(Rthin2)
print(Rthin)

# Temperatures
Tthin = power_law(Rthin, a, T_a, q)
Tthin2 = power_law(Rthin2, a, T_a, q)
Td = power_law(Rd, a, T_a, q)
print(Tthin, Tthin2, Td)

# Masses
Mthin = mdust(F, d, nu, Tthin)
Md = mdust(F, d, nu, Td)
Mrd = mass(Rd, a, rho_a)
print(power_law(Rd, a, T_a, q), mdust(F, d, nu, 55*u.K))

Tavg = (1.5 * T_a * (a/Rd)**0.5).to(u.K)
print('Average T in spherical: ', Tavg, 'Mass: ', mdust(F, d, nu, Tavg))
# Radii
r = np.logspace(1, 3.3, 1000) * u.au

# Itegrating plane of sky
#A = lambda z, r: r / (r**2 + z**2)
#B = lambda z, r: (r**2 + z**2)**(-3/4)
#intA = dblquad(A, 0, Rd.value, lambda z: -a.value, lambda z: a.value)[0]
#intB = dblquad(B, 0, Rd.value, lambda z: -a.value, lambda z: a.value)[0]
#Tavg = T_a * a.value**0.5 * intA / intB
#print('Average T in cylindrical: ', Tavg)

# Plot
fig = plt.figure(figsize=(6, 5))
ax1 = fig.add_subplot(111)
ax1.semilogx(r, mass(r, a, rho_a), 'r-')
ax1.set_ylabel('M(<r) (M$_\odot$)', color='r')
ax1.set_xlabel('r (au)')
ax1.axvline(Rthin.value, ls=':', color='#e18885')
ax1.axvline(Rd.value, ls=':', color='#cc3934')
ax1.annotate('$R_d={0.value:.0f}$ au'.format(Rd), xy=(0.65,1.02),
        xytext=(0.65,1.02), xycoords='axes fraction')
ax1.annotate('$M(<R_d)={0.value:.1f}$ {0.unit:latex}'.format(Mrd),
        xy=(0.5,0.25),
        xytext=(0.5,0.25), xycoords='axes fraction', color='r')
ax1.annotate(r'$T_{\rm thin}='+'{0.value:.0f}$ K'.format(Tthin), xy=(0.27,0.5),
        xytext=(0.27,0.5), xycoords='axes fraction', color='b')
ax1.annotate(r'$M_d(T_{\rm thin})='+'{0.value:.1f}$ {0.unit:latex}'.format(Mthin), 
        xy=(0.,0.2),
        xytext=(0.,0.2), xycoords='axes fraction', color='r')
ax1.annotate(r'$R_{\rm thin}=' + '{0.value:.0f}$ au'.format(Rthin),
        xy=(0.2,1.02),
        xytext=(0.2,1.02), xycoords='axes fraction')
ax1.plot(Rthin, Mthin, 'r^')
ax1.plot(Rd, M300, 'ko')

ax2 = ax1.twinx()
ax2.semilogx(r, power_law(r, a, T_a, q), 'b--')
ax2.set_ylabel('Temperature (K)', color='b')

fig.savefig('../figures/G335.579-0.272.config5.alma1.models.profiles.png')
