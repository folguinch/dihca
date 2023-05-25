"""Calculate physical quantity maps.

Implemented:
  - Column density
  - Toomre Q
"""
import argparse

from astropy.io import fits
from astropy.modeling.models import BlackBody
from radio_beam import Beam
from astropy.wcs import WCS
from astropy.wcs.utils import skycoord_to_pixel, proj_plane_pixel_area
from astropy.stats import gaussian_fwhm_to_sigma
from toolkit.argparse_tools import actions
from toolkit.astro_tools.images import image_cutout
import astropy.units as u
import astropy.constants as ct
import numpy as np

def hdu_to_quantity(hdu):
    return np.squeeze(hdu.data) * u.Unit(hdu.header['BUNIT'])

def keplerian_projected(mass, incl, pa, wcs, shape, position, distance):
    """Compute a map of velocities projected on the plane of the sky.

    Inclination `incl` is 0 for face-on disk. Position angle is the angle
    between the major axis of the disk ellipse and the north-south axis.

    Returns:
      A map of Keplerian velocities (vkep).
      A map of angular velocities (vkep = r * Omega).
    """
    # Get indices
    x0, y0 = skycoord_to_pixel(position, wcs)
    y, x = np.indices(shape)
    pixsize = np.sqrt(wcs.proj_plane_pixel_area())
    pixsize = pixsize.to(u.arcsec) * distance.to(u.pc)
    pixsize = pixsize.value * u.au
    x = (x - x0) * pixsize
    y = (y - y0) * pixsize

    # Projected distances to source
    th = 270.* u.deg - pa
    r = (x*np.cos(th) - y*np.sin(th))**2
    r = r + (x*np.sin(th) + y*np.cos(th))**2 / np.cos(incl)**2
    r = np.sqrt(r)

    # Keplerian Velocity
    vel = np.sqrt(ct.G * mass / r)
    omega = vel / r

    return vel.to(u.km/u.s), omega.to(1/u.s)

def column_density(continuum, temperature, kappa=1.0*u.cm**2/u.g, Rdg=0.01,
                   mu=2.8):
    """Column density map."""
    # Convert to quantities
    cont = hdu_to_quantity(continuum) * u.beam
    temp = hdu_to_quantity(temperature)
    nu = continuum.header['CRVAL3'] * u.Hz
    beam = Beam.from_fits_header(continuum.header)
    print(continuum.header['CDELT1'], temperature.header['CDELT1'])

    # Compute column density
    bb = BlackBody(temp)
    mH = 1.008 * u.u
    mH = mH.cgs
    bnu = bb(nu)
    colden = cont / (beam.sr * bnu * kappa * mu * mH * Rdg)
    colden = colden.decompose().to(1./u.cm**2)

    # Generate FITS
    header = continuum.header
    header['BUNIT'] = f'{colden.unit:FITS}'
    colmap = fits.PrimaryHDU(data=colden.value, header=header)
    
    return colmap

def toomre_q(colmap, position, incl, pa, mass, distance, temperature=None,
             linewidth=None, mu=2.8):
    """Toomre Q parameter map."""
    # Quantities
    colden = hdu_to_quantity(colmap)

    # Velocities
    wcs = WCS(colmap, naxis=2)
    vel, angvel = keplerian_projected(mass, incl, pa, wcs, colden.shape,
                                      position, distance)

    # Speed of sound
    if temperature is not None:
        temp = hdu_to_quantity(temperature)
        cs = np.sqrt(ct.k_B * temp / (2.37 * ct.m_p))
    elif linewidth is not None:
        cs = hdu_to_quantity(linewidth) * gaussian_fwhm_to_sigma
    else:
        raise ValueError('Need temperature or linewidth')
    cs = cs.to(u.km/u.s)

    # Toomre Q
    mH = 1.008 * u.u
    mH = mH.cgs
    tq = cs * angvel / (np.pi * ct.G * mu * mH * colden)
    tq = tq.to(1)

    # Generate FITS
    header = fits.Header(colmap.header, copy=True)
    header['BUNIT'] = f'{tq.unit:FITS}'
    tq = fits.PrimaryHDU(data=tq.value, header=header)
    header = fits.Header(colmap.header, copy=True)
    header['BUNIT'] = f'{angvel.unit:FITS}'
    angvel = fits.PrimaryHDU(data=angvel.value, header=header)

    return tq, angvel

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--mass', action=actions.ReadQuantity, nargs=2,
                        help='Central source mass')
    parser.add_argument('-i', '--incl', action=actions.ReadQuantity, nargs=2,
                        help='Source inclination')
    parser.add_argument('--pa', action=actions.ReadQuantity, nargs=2,
                        help='Source position angle')
    parser.add_argument('--position', action=actions.ReadSkyCoords, nargs=2,
                        help='Source position')
    parser.add_argument('--distance', action=actions.ReadQuantity, nargs=2,
                        help='Source distance')
    parser.add_argument('--size', action=actions.ReadQuantity, nargs=2,
                        help='Cutout size')
    parser.add_argument('--linewidth', action=actions.CheckFile, nargs=1,
                        help='Use linewidth map instead of speed of sound')
    parser.add_argument('continuum', action=actions.CheckFile, nargs=1,
                        help='Continuum map file')
    parser.add_argument('temperature', action=actions.CheckFile, nargs=1,
                        help='Temperature map file')
    #parser.add_argument('velocity', action=actions.CheckFile, nargs=1,
    #                    help='Velocity map file')
    parser.add_argument('outdir', action=actions.NormalizePath, nargs=1,
                        help='Output directory')
    args = parser.parse_args()

    # Load maps
    continuum = fits.open(args.continuum[0])[0]
    temperature = fits.open(args.temperature[0])[0]

    # Cutout
    if args.size is not None:
        continuum = image_cutout(continuum, args.position[0], args.size)
        temperature = image_cutout(temperature, args.position[0], args.size)
    if np.squeeze(continuum.data).shape != np.squeeze(temperature.data).shape:
        raise ValueError(('Un-matched sizes: '
                          f'continuum={continuum.data.shape}'
                          f'temperature={temperature.data.shape}'))

    # Column density
    colmap = column_density(continuum, temperature)
    colmap.writeto(args.outdir[0] / 'column_density.fits', overwrite=True)

    # Toomre Q
    if (args.mass is not None and args.incl is not None and
        args.pa is not None and args.position is not None):
        if args.linewidth is not None:
            linewidth = fits.open(args.linewidth[0])[0]
        qmap, angvel = toomre_q(colmap, args.position[0], args.incl, args.pa,
                                args.mass, args.distance,
                                temperature=temperature)
        qmap.writeto(args.outdir[0] / 'toomre_q.fits', overwrite=True)
        angvel.writeto(args.outdir[0] / 'angular_velocity.fits', overwrite=True)
        if args.linewidth is not None:
            linewidth = fits.open(args.linewidth[0])[0]
            qmap, _ = toomre_q(colmap, args.position[0], args.incl,
                               args.pa, args.mass, args.distance,
                               linewidth=linewidth)
            qmap.writeto(args.outdir[0] / 'toomre_q_linewidth.fits', overwrite=True)

