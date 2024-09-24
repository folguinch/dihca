"""Calculate the Toomre Q parameter using epicyclic frequency.

Original provided by Xing Lu.
"""
from pathlib import Path

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.modeling.models import BlackBody
from radio_beam import Beam
from scipy.interpolate import griddata
import numpy as np
import astropy.constants as ct
import astropy.units as u

# Constants
source = 'G336.01-0.82'
distance = 3.1 * u.kpc
method = 'cubic'
center = SkyCoord('16h35m09.26085s', '-48d46m47.65854s', frame='icrs')
results = Path(f'/data/share/binary_project/results/{source}')

# Whether to calculate Q with the epicyclic frequency without the assumption of Keplerian rotation (True)
# or with the angular velocity assuming Keplerian rotation (False)
diff = True

# Whether to consider the non-thermal component in the velocity dispersion
totalv = False

# Position angle of the disk (north to east)
pa = 125. * u.deg

# Inclination angle of the disk w.r.t. the plane of the sky
incl = 65 * u.deg

# Continuum image
contim = Path(('/data/share/binary_project/G336.01/'
               f'{source}/final_data/config8/continuum_clean'))
contim = contim / f'{source}.config8.cont_avg.selfcal.robust0.5.hogbom.image.pbcor.fits'
maskim = results / 'CH3OH/source_mask.fits'
data, hdr = fits.getdata(contim, 0, header=True)
data = np.squeeze(data) * u.Unit(hdr['BUNIT'])
mask, mask_hdr = fits.getdata(maskim, 0, header=True)
mask = mask.astype(bool)
beam = Beam.from_fits_header(hdr)
print(f'Continuum shape: {data.shape}')
print(f'Mask shape: {mask.shape}')

# Gas temperature map
tempim = results / 'CH3OH/spectra_lte_fit/tex_1_map.fits'
Tgas, Tgas_hdr = fits.getdata(tempim, 0, header=True)
Tgas = Tgas * u.Unit(Tgas_hdr['BUNIT'])
print(f'Temperature shape: {Tgas.shape}')

# Velocity dispersion map
sigmaim = results / 'CH3OH/spectra_lte_fit/fwhm_1_map.fits'
sigmav, sigmav_hdr = fits.getdata(sigmaim, 0, header=True)
sigmav = sigmav * u.Unit(sigmav_hdr['BUNIT'])
#mmol = 60. # Molecular weight of CH3OCHO
# Useful page: https://www.webqc.org/molecular-weight-of-CH3OH.html
mmol = 32 * u.u # CH3OH
nonthermal = np.sqrt(sigmav**2 - ct.k_B * Tgas / mmol)
cs = np.sqrt(ct.k_B * Tgas / 2.37 / ct.m_p)

# Use the total linewidth (non-thermal + sound speed)
if totalv:
    cs = np.sqrt(nonthermal**2 + cs**2)

# Surface density
opacity = 1.0 * u.cm**2 / u.g
freq = 225.987 * u.GHz
BT = BlackBody(Tgas)
BT = BT(freq)
Rdg = 0.01
# Surface density of the disk (projected)
Sigma = data * u.beam * np.cos(incl) / (beam.sr * BT * opacity * Rdg)
Sigma = Sigma.decompose().to(u.g / u.cm**2)

# Get the differential rotation
# Read in the fitted centroid velocity map (~mom1)
velim = results / 'CH3OH/spectra_lte_fit/vlsr_1_map.fits'
Vmap, vel_hdr = fits.getdata(velim, 0, header=True)
# Already corrected for systemic velocity
Vmap = np.abs(Vmap) * u.Unit(vel_hdr['BUNIT'])
print(f'Velocity shape: {Vmap.shape}')
## Should consider the projection of the disk
## Use vrot along the kinematic major axis (e.g., along the kinematic minor
## axis, the observed vrot is always 0, because it is perpendicular to LOS) 
## Rotation curve for Keplerian rotation
#para = [-0.5,  1.86383746]

# Define maps
wcs = WCS(Tgas_hdr)
nx = Tgas_hdr['NAXIS1']
ny = Tgas_hdr['NAXIS2']
x = np.arange(nx)
y = np.arange(ny)
#yg, xg = np.meshgrid(x, y)
yg, xg = np.indices(mask.shape)
xvalid = xg[mask]
yvalid = yg[mask]
vrot_obs = np.zeros([ny, nx]) * Vmap.unit
vrot_obs[~mask] = np.nan
rv = np.zeros([ny, nx]) * Vmap.unit * u.au
rv[~mask] = np.nan
radii = np.zeros([ny, nx]) * u.au
radii[~mask] = np.nan
dfr = np.zeros([ny, nx]) * rv.unit / radii.unit
dfr[~mask] = np.nan

# Plane of the sky
sky = wcs.pixel_to_world(xvalid, yvalid)
sep = center.separation(sky)
# Position angle of the pixel wrt the center
sep_pa = center.position_angle(sky)
# Subtract (from) PA of the disk
new_pa = pa - sep_pa
# Get the deprojected distance or radius
dist_maj = sep * np.abs(np.cos(new_pa))
dist_min = sep * np.abs(np.sin(new_pa)) / np.cos(incl)
# The deprojected radius of the pixel from the disk center
rad = np.sqrt(dist_maj**2 + dist_min**2)
if diff:
    # See Appendix C of Johnston 2020
    rad = rad.to(u.arcsec).value * distance.to(u.pc).value * u.au # cm
    vrot_obs[mask] = np.abs(Vmap[mask]) / np.abs(np.cos(new_pa)) / np.sin(incl)
    rv[mask] = vrot_obs[mask] * rad
    radii[mask] = rad
else: # Assuming purely Keplerian rotation
    raise NotImplementedError
    #vrot[j,i] = para[1]*(rad**para[0])
    #omega[j,i] = vrot[j,i] * 1e5 / (rad/3600./180.*np.pi*8100*pc)
    #vrot_model[j,i] = vrot[j,i] * np.cos(new_pa) * np.sin(incl) - 49.243

hdr['BUNIT'] = f'{radii.cgs.unit:FITS}'
hdr['BTYPE'] = 'Distance'
fits.writeto(results / 'projected_radius.fits', radii.cgs.value, hdr,
             overwrite=True)

hdr['BUNIT'] = f'{rv.cgs.unit:FITS}'
hdr['BTYPE'] = 'Momentum'
fits.writeto(results / 'momentum_azimuthal.fits', rv.cgs.value, hdr,
             overwrite=True)

if diff:
    #f_ra = interpolate.LinearNDInterpolator(list(zip(xvalid.ravel(),
    #                                                 yvalid.ravel())),
    #                                        radii[mask].value)
    #f_rv = interpolate.LinearNDInterpolator(list(zip(xvalid.ravel(),
    #                                                 yvalid.ravel())),
    #                                        rv[mask].value)
    step = abs(hdr['CDELT1']) * u.deg
    # Derive the differential of r*v ( d(r*v) / dr )
    ucoord = sky.directional_offset_by(sep_pa, step)
    upix = wcs.world_to_pixel(ucoord)
    #u_rv = f_rv(upix[0], upix[1]) * rv.unit
    #u_ra = f_ra(upix[0], upix[1]) * radii.unit
    u_rv = griddata(list(zip(xvalid.ravel(), yvalid.ravel())),
                    rv[mask].value,
                    upix,
                    method=method) * rv.unit
    u_ra = griddata(list(zip(xvalid.ravel(), yvalid.ravel())),
                    radii[mask].value,
                    upix,
                    method=method) * radii.unit
    lcoord = sky.directional_offset_by(sep_pa + 180*u.deg, step)
    lpix = wcs.world_to_pixel(lcoord)
    #l_rv = f_rv(lpix[0], lpix[1]) * rv.unit
    #l_ra = f_ra(lpix[0], lpix[1]) * radii.unit
    l_rv = griddata(list(zip(xvalid.ravel(), yvalid.ravel())),
                    rv[mask].value,
                    lpix,
                    method=method) * rv.unit
    l_ra = griddata(list(zip(xvalid.ravel(), yvalid.ravel())),
                    radii[mask].value,
                    lpix,
                    method=method) * radii.unit
    dfr[mask] = (u_rv - l_rv) / (u_ra - l_ra)
    kappa_sq = 2 * vrot_obs * dfr / radii**2 
    omega = np.sqrt(kappa_sq)
    omega[kappa_sq < 0] = 1.414 * vrot_obs[kappa_sq < 0] / radii[kappa_sq < 0]
    omega = omega.to(1/u.s)

Q = cs * omega / (np.pi * ct.G * Sigma)
Q[np.where(Q <= 0.)] = 0. * u.Unit(1)
Q = Q.decompose()

hdr['BUNIT'] = f'{Q.unit:FITS}'
hdr['BTYPE'] = 'TOOMRE Q'
if totalv:
    # Effective sound speed
    fits.writeto(results / f'toomre_q_epicyclic_effcs_{method}.fits', Q.value,
                 hdr, overwrite=True)
else:
    # Thermal sound speed
    fits.writeto(results / f'toomre_q_epicyclic_{method}.fits', Q.value, hdr,
                 overwrite=True)

hdr['BUNIT'] = f'{omega.unit:FITS}'
hdr['BTYPE'] = 'OMEGA'
fits.writeto(results / f'angular_velocity_epicyclic_{method}.fits', omega.value,
             hdr, overwrite=True)

hdr['BUNIT'] = f'{Sigma.unit:FITS}'
hdr['BTYPE'] = 'Surface density'
# Thermal sound speed
fits.writeto(results / f'surface_density_projected_{method}.fits', Sigma.value,
             hdr, overwrite=True)

#omega = np.zeros([ny, nx])
#vrot_obs = np.zeros([ny, nx]) * Vmap.unit
#rv = np.zeros([ny, nx]) * Vmap.unit * u.au
#radii = np.zeros([ny, nx]) * u.au
##vrot = np.zeros([ny, nx])
##vrot_model = np.zeros([ny, nx])
##dfr = np.zeros([ny, nx])
#
#for i in np.arange(nx):
#    for j in np.arange(ny):
#        if np.isnan(Vmap[j,i]):
#            vrot_obs[j,i] = np.nan
#            rv[j,i] = np.nan
#            radii[j,i] = np.nan
#            continue
#        sky = wcs.pixel_to_world(i, j)
#        sep = center.separation(sky)
#        # Position angle of the pixel wrt the center
#        sep_pa = center.position_angle(sky)
#        # Subtract (from) PA of the disk
#        new_pa = pa - sep_pa
#        # Get the deprojected distance or radius
#        dist_maj = sep * np.abs(np.cos(new_pa))
#        dist_min = sep * np.abs(np.sin(new_pa)) / np.cos(incl)
#        # The deprojected radius of the pixel from the disk center
#        rad = np.sqrt(dist_maj**2 + dist_min**2)
#        if diff: # See Appendix C of Johnston 2020
#            rad = rad.to(u.arcsec).value * distance.to(u.pc).value * u.au # cm
#            vrot_obs[j,i] = np.abs(Vmap[j,i]) / np.abs(np.cos(new_pa)) / np.sin(incl)
#            rv[j,i] = vrot_obs[j,i] * rad
#            radii[j,i] = rad
#        else: # Assuming purely Keplerian rotation
#            raise NotImplementedError
#            #vrot[j,i] = para[1]*(rad**para[0])
#            #omega[j,i] = vrot[j,i] * 1e5 / (rad/3600./180.*np.pi*8100*pc)
#            #vrot_model[j,i] = vrot[j,i] * np.cos(new_pa) * np.sin(incl) - 49.243

#hdr['BUNIT'] = f'{(1*u.cm).unit:FITS}'
#hdr['BTYPE'] = 'Distance'
#fits.writeto(results / 'projected_radius.fits', radii, hdr, overwrite=True)
#
#hdr['BUNIT'] = f'{u.cm**2/u.s:FITS}'
#hdr['BTYPE'] = 'Momentum'
#fits.writeto(results / 'momentum_azimuthal.fits', rv, hdr, overwrite=True)

#if diff:
#    x = np.arange(nx)
#    y = np.arange(ny)
#    #rv[np.where(np.isnan(rv))] = 0.0
#    #f_ra = interpolate.interp2d(x,y,radii,kind='linear')
#    #f_rv = interpolate.interp2d(x,y,rv,   kind='linear')
#    radii_masked = np.ma.masked_invalid(radii)
#    rv_masked = np.ma.masked_invalid(rv)
#    xg, yg = np.meshgrid(x, y, indexing='ij')
#    xvalid = xg[~radii_masked.mask]
#    yvalid = yg[~radii_masked.mask]
#    radii_valid = radii_masked[~radii_masked.mask]
#    rv_valid = rv_masked[~rv_masked.mask]
#    f_ra = interpolate.LinearNDInterpolator(list(zip(xvalid, yvalid)),
#                                            radii_valid)
#    f_rv = interpolate.LinearNDInterpolator(list(zip(xvalid, yvalid)),
#                                            rv_valid)
#    step = abs(hdr['CDELT1'])*3600 * u.arcsec
#    # Derive the differential of r*v ( d(r*v) / dr )
#    for i in np.arange(nx-10)+5:
#        for j in np.arange(ny-10)+5:
#            if np.isnan(rv[j,i]):
#                dfr[j,i] = np.nan
#                continue
#            sky = w.pixel_to_world(i, j)
#            sep_pa = center.position_angle(sky)
#            ucoord = sky.directional_offset_by(sep_pa,step)
#            upix = w.world_to_pixel(ucoord)
#            u_rv = f_rv(upix[0], upix[1])
#            u_ra = f_ra(upix[0], upix[1])
#            lcoord = sky.directional_offset_by(sep_pa+180.*u.deg,step)
#            lpix = w.world_to_pixel(lcoord)
#            l_rv = f_rv(lpix[0], lpix[1])
#            l_ra = f_ra(lpix[0], lpix[1])
#            dfr[j,i] = (u_rv - l_rv) / (u_ra - l_ra)
#
#    kappa_sq = 2 * vrot_obs/radii**2 * dfr
#    omega[kappa_sq >= 0] = np.sqrt(kappa_sq[kappa_sq >= 0])
#    omega[kappa_sq < 0] = 1.414 * vrot_obs[kappa_sq < 0] / radii[kappa_sq < 0]
#
#Q = cs * omega / np.pi / G / Sigma
#Q[np.where(Q <= 0.)] = 0.
#
#hdr['BUNIT'] = 1.
#hdr['BTYPE'] = 'TOOMRE Q'
#if totalv:
#    # Effective sound speed
#    fits.writeto(results / 'toomre_q_epicyclic_effcs.fits', Q, hdr, overwrite=True)
#else:
#    # Thermal sound speed
#    fits.writeto(results / 'toomre_q_epicyclic.fits', Q, hdr, overwrite=True)
#
#hdr['BUNIT'] = f'{(1/u.s).unit:FITS}'
#hdr['BTYPE'] = 'OMEGA'
#fits.writeto(results / 'angular_velocity_epicyclic.fits', omega, hdr, overwrite=True)
#
#hdr['BUNIT'] = f'{(1/u.cm**2).unit:FITS}'
#hdr['BTYPE'] = 'Surface density'
## Thermal sound speed
#fits.writeto(results / 'surface_density_projected.fits', Sigma, hdr, overwrite=True)
