"""Fit PV maps using in-edge detection."""
from pathlib import Path
import sys

import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.modeling import models, fitting, Parameter, Fittable1DModel
from astropy.stats import gaussian_fwhm_to_sigma
from astropy.wcs import WCS
from configparseradv.configparser import ConfigParserAdv as ConfigParser
from line_little_helper.molecule import Molecule
from toolkit.astro_tools.masking import mask_structures
from toolkit.astro_tools.images import get_coord_axes
from toolkit.array_utils import save_struct_array

from common_paths import RESULTS, CONFIGSS

class PiecewisePowerLaw(Fittable1DModel):
    amplitude = Parameter()
    x_0 = Parameter()
    alpha = Parameter()
    cons = Parameter()
    x_mid = Parameter()

    @staticmethod
    def evaluate(x, amplitude, x_0, alpha, cons, x_mid):
        mask = x < x_mid
        vals = np.zeros(len(x))
        vals[mask] = models.PowerLaw1D.evaluate(np.abs(x[mask] - x_mid),
                                                amplitude,
                                                x_0,
                                                alpha)
        vals[~mask] = models.PowerLaw1D.evaluate(x[~mask] - x_mid,
                                                 -amplitude,
                                                 x_0,
                                                 alpha)
        return vals + cons

    @staticmethod
    def fit_deriv(x, amplitude, x_0, alpha, cons, x_mid):
        mask = x < x_mid

        d_amp_neg, d_x0_neg, d_alpha_neg  = models.PowerLaw1D.fit_deriv(
            np.abs(x[mask] - xmid),
            amplitude,
            x_0,
            alpha)
        d_amp_pos, d_x0_pos, d_alpha_pos  = models.PowerLaw1D.fit_deriv(
            x[~mask] - x_mid,
            -amplitude,
            x_0,
            alpha)
        d_amp = np.zeros(x.size)
        d_amp[mask] = d_amp_neg
        d_amp[~mask] = d_amp_pos
        d_x0 = np.zeros(x.size)
        d_x0[mask] = d_x0_neg
        d_x0[~mask] = d_x0_pos
        d_alpha = np.zeros(x.size)
        d_alpha[mask] = d_alpha_neg
        d_alpha[~mask] = d_alpha_pos
        d_xmid = np.zeros(x.size)
        d_xmid[mask] = amplitude * x_0**alpha * alpha * \
                np.abs(x - x_mid)**(-alpha - 1)
        d_xmid[~mask] = -amplitude * x_0**alpha * alpha * \
                (x - x_mid)**(-alpha - 1)
        d_cons = np.ones(x.size)

        return [d_amp, d_xmid, d_x0, d_alpha, d_cons]

def find_edge(slcs, fn, data, beam, delta=2, inverted=False):
    xmid = data.shape[1] / 2
    yaxis = np.arange(data.shape[0], dtype=int)
    if inverted:
        yaxis = yaxis[::-1]

    # Find edge values
    xyvals = np.array([[fn(slci[0].start, slci[-1].stop-1), y]
                       for y, slci in zip(yaxis, slcs)
                       if len(slci) != 0])
    ind = np.nanargmax(np.abs(xyvals[:,0] - xmid))
    xyvals = xyvals[:ind]

    # Get average
    edge_points = []
    edge_errors = []
    for x, y in xyvals:
        xran = np.arange(max(x - delta, 0),
                         min(x + delta + 1, data.shape[1]),
                         dtype=int)
        weight = data[y][xran]
        avg = np.sum(weight * xran) / np.sum(weight)
        err = np.sqrt(np.sum(weight**2 * beam.value**2)) / np.sum(weight)
        edge_points.append([avg, y])
        edge_errors.append(err)

    return np.array(edge_points), np.array(edge_errors)*beam.unit

def get_edge(fitsfile, rms, nsigma=3, delta=2, quadrant=1):
    # Open data
    image = fits.open(fitsfile)[0]
    mask = image.data > rms * nsigma
    beam = np.sqrt(image.header['BMAJ'] * image.header['BMIN']) * u.deg
    beam = beam.to(u.arcsec) * gaussian_fwhm_to_sigma

    # Get mask of the largest object
    mask, labels, nlabels = mask_structures(mask)
    component_sizes = np.bincount(labels.ravel())
    max_component = component_sizes == np.nanmax(component_sizes[1:])
    max_mask = max_component[labels]
    mask[~max_mask] = False

    # Save mask
    hdu = fits.PrimaryHDU(data=mask.astype(int), header=image.header)
    hdu.writeto(fitsfile.with_suffix(f'.{nsigma}sigma.mask.fits'),
                overwrite=True)

    # Get structures
    image_masked = np.ma.array(image.data, mask=~mask)
    slcs = np.ma.notmasked_contiguous(image_masked, axis=1)

    # Get the positions in pv map
    if quadrant == 1:
        fn_upper = max
        fn_lower = min
    else:
        fn_upper = min
        fn_lower = max
    edges_upper, edges_upper_error = find_edge(slcs, fn_upper, image.data,
                                               beam, delta=delta)
    edges_lower, edges_lower_error = find_edge(slcs[::-1], fn_lower, image.data,
                                               beam, delta=delta, inverted=True)
    edges_x = np.append(edges_upper[:, 0], edges_lower[:, 0])
    edges_y = np.append(edges_upper[:, 1], edges_lower[:, 1])
    errors = np.append(edges_upper_error, edges_lower_error)
    ind = np.argsort(edges_x)
    edges_x = edges_x[ind]
    edges_y = edges_y[ind]
    errors = errors[ind]

    # Convert to coordinates
    wcs = WCS(image.header)
    coords_upper = wcs.pixel_to_world_values(edges_upper)
    coords_lower = wcs.pixel_to_world_values(edges_lower)
    coords = coords_upper + coords_lower
    edges_x = np.array([coord[0] for coord in coords])
    edges_y = np.array([coord[1] for coord in coords])
    errors = errors * image.header['CDELT1']

    # Get vsys
    xcoords_upper = np.array([coords_upper[0] for coord in coords_upper])
    xcoords_lower = np.array([coords_lower[0] for coord in coords_lower])
    ind1 = np.nanargmax(np.abs(xcoords_upper))
    ind2 = np.nanargmax(np.abs(xcoords_lower))
    vsys = (coords_upper[ind1][1] + coords_lower[ind2][1]) / 2

    # Save edges to file
    head1 = image.header['CTYPE1']
    head2 = image.header['CTYPE2']
    unit1 = u.Unit(image.header['CUNIT1'])
    unit2 = u.Unit(image.header['CUNIT2'])
    edges_x = edges_x * unit1
    edges_y = edges_y * unit2
    edges_x = edges_x.to(u.arcsec)
    edges_y = edges_y.to(u.km/u.s)
    errors = errors.to(u.arcsec)
    yerr = np.abs(image.header['CDELT2']) * unit2
    yerr = yerr.to(u.km/u.s)
    as_sarray = np.array(list(zip(edges_x.value,
                                  errors.value,
                                  edges_y.value,
                                  np.repeat(yerr.value, len(errors)))),
                         dtype=[(head1, float), (f'{head1}_error', float),
                                (head2, float), (f'{head2}_error', float)])
    units = {head1: u.arcsec,
             f'{head1}_error': u.arcsec,
             head2: u.km/u.s,
             f'{head2}_error': u.km/u.s,
             }
    save_struct_array(fitsfile.with_suffix('.edge.dat'), as_sarray, units,
                      fmt='%10.8e\t')

    # Convert to quantitites
    vsys = vsys * unit2

    return (edges_x, edges_y), vsys.to(u.km/u.s)

def params_to_txt(model):
    names = ['amplitude', 'x_0', 'alpha', 'cons', 'x_mid']
    params = [f'{model.amplitude.value}',
              f'{model.x_0.value}',
              f'{model.alpha.value}',
              f'{model.cons.value}',
              f'{model.x_mid.value}']
    coefs = 'coeficients ='
    lines = []
    for name, param in zip(names, params):
        coefs += f' ${{model_{name}}}'
        lines.append(f'model_{name} = param')
    lines.append(coefs)
    
    return '\n'.join(lines)

def fit_edge(fitsfile, edges, vsys, distance, rms, nsigma=3):
    # Open data
    image = fits.open(fitsfile)[0]
    xaxis, yaxis = get_coord_axes(image)
    xaxis = xaxis.to(u.arcsec)
    yaxis = yaxis.to(u.km/u.s)

    # Fit power law
    print('Initial vsys:', vsys)
    fit_x, fit_y = edges
    amplitude = np.max(fit_y) - vsys.to(fit_y.unit)
    x_0 = 100 / distance.to(u.pc).value * u.arcsec
    x_0 = x_0.to(fit_x.unit)
    print('100 au to arcec: ', x_0)
    # Upper
    fitter = fitting.SLSQPLSQFitter()
    model = PiecewisePowerLaw(amplitude=-amplitude.value,
                              x_0=x_0.value,
                              alpha=0.5,
                              cons=vsys.to(fit_y.unit).value,
                              x_mid=0.)
    model.x_0.fixed = True
    unrestricted = fitter(model, fit_x.value, fit_y.value)
    model.alpha.fixed = True
    model.amplitude = unrestricted.amplitude
    model.cons = unrestricted.cons
    model.x_mid = unrestricted.x_mid
    keplerian = fitter(model, fit_x.value, fit_y.value)

    # Config section and write results
    unrestricted_txt = params_to_txt(unrestricted)
    keplerian_txt = params_to_txt(keplerian)
    sect1 = ['[pvedge]',
             f"structured_array = {fitsfile.with_suffix('.edge.dat')}"]
    sect2 = ['[unrestricted_fit]',
             'function = piecewise_powerlaw',
             f'xrange = {xaxis[0].value} {xaxis[-1].value} {xaxis.unit}',
             f'yunit = {fit_x.unit}',
             'linestyle = -',
             'color = k']
    sect3 = ['[keplerian_fit]',
             'function = piecewise_powerlaw',
             f'xrange = {xaxis[0].value} {xaxis[-1].value} {xaxis.unit}',
             f'yunit = {fit_x.unit}',
             'linestyle = --',
             'color = b']
    text = ('\n'.join(sect1) + '\n' +
            '\n'.join(sect2) + '\n' + unrestricted_txt + '\n' +
            '\n'.join(sect3) + '\n' + keplerian_txt)
    config = fitsfile.with_suffix('.plot.cfg')
    config.write_text(text)

    # Quick look at fit
    newx = np.linspace(0., xaxis[-1].value, 500)
    extent = [xaxis[0].value, xaxis[-1].value,
              yaxis[0].value, yaxis[-1].value]
    fig, ax = plt.subplots()
    ax.imshow(image.data, origin='lower', extent=extent)
    ax.contour(image.data, levels=[rms * nsigma], extent=extent)
    ax.plot(fit_x, fit_y, 'ro')
    ax.plot(newx + unrestricted.x_mid,
            unrestricted(newx + unrestricted.x_mid),
            -newx + unrestricted.x_mid,
            unrestricted(-newx + unrestricted.x_mid),
            linestyle='-', color='k')
    #ax.plot(-newx + unrestricted.x_mid,
    #        unrestricted(-newx + unrestricted.x_mid), 'k-')
    ax.plot(newx + keplerian.x_mid,
            keplerian(newx + keplerian.x_mid), 'b--')
    ax.plot(-newx + keplerian.x_mid,
            keplerian(-newx + keplerian.x_mid), 'b--')
    ax.axhline(unrestricted.cons.value, color='g', ls=':')
    ax.axhline(unrestricted.cons.value, color='g', ls='--')
    ax.axvline(unrestricted.x_mid.value, color='g', ls='--')
    ax.set_xlim(xaxis[0].value, xaxis[-1].value)
    ax.set_ylim(yaxis[0].value, yaxis[-1].value)
    ax.set_xlabel('Offset (arcsec)')
    ax.set_ylabel('Radial Velocity (km/s)')
    ax.set_aspect('auto') 
    fig.savefig(fitsfile.with_suffix('.edges.png'))

    fig, ax = plt.subplots()
    ax.plot(np.log10(np.abs(fit_x.value - unrestricted.x_mid.value)),
            np.log10(np.abs(fit_y.value - unrestricted.cons.value)),
            'kx')
    ax.set_xlabel('log(Offset / arcsec)')
    ax.set_ylabel('log(|$v_{rad} - v_{sys}$| / km/s)')
    fig.savefig(fitsfile.with_suffix('.profile.png'))

if __name__ == '__main__':
    # Summary information
    source_info = ConfigParser()
    source_info.read(CONFIGS / 'extracted/summary.cfg')

    for section in source_info:
        config = source_info[section]
        fitsfile = config.getpath('pvmap')
        rms = config.getquantity('rms').to(u.Jy/u.beam).value
        distance = config.getquantity('distance')
        edges, vsys = get_edge(fitsfile, rms)
        fit_edge(fitsfile, edges, vsys, distance, rms)
