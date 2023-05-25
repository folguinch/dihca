"""Calculate the Toomre Q parameter using epicyclic frequency.

Original provided by Xing Lu.
"""
import numpy as np
import astropy.constants as const
import astropy.units as u
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.modeling.blackbody import blackbody_nu
from scipy import interpolate

kb = const.k_B.cgs.value
G = const.G.cgs.value
mp = const.m_p.cgs.value
pc = const.pc.cgs.value
AU = const.au.cgs.value
jy = u.Jy.cgs.scale

# Whether to calculate Q with the epicyclic frequency without the assumption of Keplerian rotation (True)
# or with the angular velocity assuming Keplerian rotation (False)
diff = True

# Whether to consider the non-thermal component in the velocity dispersion
totalv = False

# Position angle of the disk (north to east)
pa = 125. # deg

# Inclination angle of the disk w.r.t. the plane of the sky
#ra = 0.29 # arcsec
#rb = 0.21 # arcsec
#incl = np.arccos(rb/ra)/np.pi*180.
#print('The inclination angle (the angle between the rotation axis and line of sight) is {:.1f} deg'.format(incl))
# Here we use the fitting result of BBarolo
incl = 65 # deg

# Continuum image
contim = '../calc_mass_column_ToomreQ/sgrc_c43_8_cont_selfcal.image.pbcor.cutout.fits'
data,hdr = fits.getdata(contim, 0, header=True)
bmaj = hdr['BMAJ']
bmin = hdr['BMIN']

# Gas temperature map
Tgas, Tgas_hdr = fits.getdata('../sgrc_13ch3cn_t1_1compo_chs_vofffixnp2_vwrefixhcooch3_extk0123_confp75mask_notuseiso.fits', 0, header=True)
minT = np.nanmin(Tgas)
Tgas[np.where(Tgas < minT)] = minT
Tgas[np.isnan(Tgas)] = minT

# Velocity dispersion map
sigmav = fits.getdata('../spw0/fit_HCOOCH3/sigmavmap_smaller.fits', 0) * 1e5 # cm/2
mmol = 60. # Molecular weight of CH3OCHO
nonthermal = np.sqrt(sigmav**2 - kb * Tgas / mmol / mp)
cs = np.sqrt(kb * Tgas / 2.37 / mp) # cm/s

# Use the total linewidth (non-thermal + sound speed)
if totalv:
    cs = np.sqrt(nonthermal**2 + cs**2)

opacity = 1.99 # cm^2 g^-1. MRN without ice mantles, 10^6 cm^-3 density, 10^5 years coagulation (OH94)
beamA = np.pi * (bmaj/180.*np.pi * bmin/180.*np.pi) / 4.
# the beam size should be in radian, not cm
freq = 225.987 # GHz
BT = blackbody_nu(freq*u.GHz, Tgas*u.K).cgs.value
# Surface density of the disk (projected)
Sigma = 100. * data * jy / beamA / BT / opacity * np.cos(incl/180.*np.pi)

# Get the differential rotation
# Read in the fitted centroid velocity map (~mom1)
Vmap = fits.getdata('../spw0/fit_HCOOCH3/Centvmap_masked_smaller.fits', 0)
# Shift the velocities to the Vlsr of the disk
Vmap = np.abs(Vmap + 49.243)
## Should consider the projection of the disk
## Use vrot along the kinematic major axis (e.g., along the kinematic minor axis, the observed vrot is always 0, because it is perpendicular to LOS) 
## Here we use the rotation curve derived from BBarolo
para = [-0.5,  1.86383746]
w = WCS(Tgas_hdr)
nx = Tgas_hdr['NAXIS1']
ny = Tgas_hdr['NAXIS2']
# Define the disk center
center = SkyCoord('17h44m40.15266s', '-29d28m12.8756s', frame='fk5')
omega = np.zeros([ny, nx])
vrot = np.zeros([ny, nx])
vrot_obs = np.zeros([ny, nx])
vrot_model = np.zeros([ny, nx])
rv = np.zeros([ny, nx])
radii = np.zeros([ny, nx])
dfr = np.zeros([ny, nx])

for i in np.arange(nx):
    for j in np.arange(ny):
        sky = w.pixel_to_world(i, j)
        sep = center.separation(sky).arcsecond
        # Position angle of the pixel wrt the center
        sep_pa = center.position_angle(sky).deg
        # Subtract (from) PA of the disk
        new_pa = pa - sep_pa
        # Get the deprojected distance or radius
        dist_maj = sep * np.abs(np.cos(new_pa/180.*np.pi))
        dist_min = sep * np.abs(np.sin(new_pa/180.*np.pi)) / np.cos(incl/180.*np.pi)
        # The deprojected radius of the pixel from the disk center
        rad = np.sqrt(dist_maj**2 + dist_min**2) # arcsec
        if diff: # See Appendix C of Johnston 2020
            rad = rad/3600./180.*np.pi*8100*pc # cm
            vrot_obs[j,i] = np.abs(Vmap[j,i]) / np.abs(np.cos(new_pa/180.*np.pi)) / np.sin(incl/180.*np.pi) * 1e5
            rv[j,i] = vrot_obs[j,i] * rad # vrot (cm/s) * r (cm)
            radii[j,i] = rad # cm
        else: # Assuming purely Keplerian rotation
            vrot[j,i] = para[1]*(rad**para[0])
            omega[j,i] = vrot[j,i] * 1e5 / (rad/3600./180.*np.pi*8100*pc)
            vrot_model[j,i] = vrot[j,i] * np.cos(new_pa/180.*np.pi) * np.sin(incl/180.*np.pi) - 49.243

if diff:
    x = np.arange(nx)
    y = np.arange(ny)
    rv[np.where(np.isnan(rv))] = 0.0
    f_ra = interpolate.interp2d(x,y,radii,kind='linear')
    f_rv = interpolate.interp2d(x,y,rv,   kind='linear')
    step = abs(hdr['CDELT1'])*3600 * u.arcsec
    # Derive the differential of r*v ( d(r*v) / dr )
    for i in np.arange(nx-10)+5:
        for j in np.arange(ny-10)+5:
            sky = w.pixel_to_world(i, j)
            sep_pa = center.position_angle(sky)
            ucoord = sky.directional_offset_by(sep_pa,step)
            upix = w.world_to_pixel(ucoord)
            u_rv = f_rv(upix[0], upix[1])
            u_ra = f_ra(upix[0], upix[1])
            lcoord = sky.directional_offset_by(sep_pa+180.*u.deg,step)
            lpix = w.world_to_pixel(lcoord)
            l_rv = f_rv(lpix[0], lpix[1])
            l_ra = f_ra(lpix[0], lpix[1])
            dfr[j,i] = (u_rv - l_rv) / (u_ra - l_ra)

    kappa_sq = 2 * vrot_obs/radii**2 * dfr
    omega[kappa_sq >= 0] = np.sqrt(kappa_sq[kappa_sq >= 0])
    omega[kappa_sq < 0] = 1.414 * vrot_obs[kappa_sq < 0] / radii[kappa_sq < 0]

Q = cs * omega / np.pi / G / Sigma
Q[np.where(Q <= 0.)] = 0.

hdr['BUNIT'] = 1.
hdr['BTYPE'] = 'TOOMRE Q'

fits.writeto('sgrc_disk_ToomreQ_Omegamap_includesigmav_differential.fits', Q, hdr, overwrite=True)
