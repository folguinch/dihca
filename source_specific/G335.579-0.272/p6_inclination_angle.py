import numpy as np
import astropy.constants as ct
import astropy.units as u

# concat
maj_ct = 281
min_ct = 252
maj_ct_err = 14
min_ct_err = 13

# config8
maj_c8 = 162
min_c8 = 145
maj_c8_err = 17
min_c8_err = 19

# Random values
niter = 100000
maj_c8_rnd = np.random.default_rng().normal(maj_c8, maj_c8_err, niter)
min_c8_rnd = np.random.default_rng().normal(min_c8, min_c8_err, niter)
maj_ct_rnd = np.random.default_rng().normal(maj_ct, maj_ct_err, niter)
min_ct_rnd = np.random.default_rng().normal(min_ct, min_ct_err, niter)

# Inclination angles
inc_ct_rnd = np.degrees(np.arccos(min_ct_rnd/maj_ct_rnd))
inc_c8_rnd = np.degrees(np.arccos(min_c8_rnd/maj_c8_rnd))
inc_ct_rnd = inc_ct_rnd[~np.isnan(inc_ct_rnd)]
inc_c8_rnd = inc_c8_rnd[~np.isnan(inc_c8_rnd)]
inc_ct_error = np.std(inc_ct_rnd)
inc_c8_error = np.std(inc_c8_rnd)
inc_ct_rnd = np.mean(inc_ct_rnd)
inc_c8_rnd = np.mean(inc_c8_rnd)
inc_ct = np.degrees(np.arccos(min_ct/maj_ct))
inc_c8 = np.degrees(np.arccos(min_c8/maj_c8))

print(f'Inclination from concat = {inc_ct:.1f} deg')
print(f'Inclination from concat random = {inc_ct_rnd:.1f} +/- {inc_ct_error:.1f} deg')
print(f'Inclination from config8 = {inc_c8:.1f} deg')
print(f'Inclination from config8 random = {inc_c8_rnd:.1f} +/- {inc_c8_error:.1f} deg')

inclination = 0.5 * (inc_ct + inc_c8) * u.deg
inclination_err = 0.5 * np.sqrt(inc_ct_error**2 + inc_c8_error**2) * u.deg
print(f'Average inclination = {inclination:.0f} +/- {inclination_err:.0f}')

vel = 1.5 * u.km/u.s
vel_err = 0.6 * u.km/u.s
radius = 228 * u.au
radius_err = 32.5 * u.au

mass = radius * vel**2 / (ct.G * np.sin(inclination.to(u.rad).value)**2)
mass = mass.to(u.M_sun)
print(f'Kinetic mass = {mass:.1f}')

inc_rnd = np.random.default_rng().normal(inclination.value,
                                         inclination_err.value, 
                                         niter) * inclination.unit
vel_rnd = np.random.default_rng().normal(vel.value, vel_err.value,
                                         niter) * vel.unit
rad_rnd = np.random.default_rng().normal(radius.value, radius_err.value,
                                         niter) * radius.unit
mass_rnd = np.abs(rad_rnd) * np.abs(vel_rnd)**2 / (ct.G * np.sin(inc_rnd.to(u.rad).value)**2)
mass_rnd = mass_rnd.to(u.M_sun)
mass_rnd_err = np.std(mass_rnd)
mass_rnd = np.mean(mass_rnd)
print(f'Kinetic mass random = {mass_rnd:.1f} +/- {mass_rnd_err:.1f}')
