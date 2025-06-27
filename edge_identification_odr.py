"""Fit PV maps using in-edge detection."""
from dataclasses import dataclass
from pathlib import Path
import sys

import astropy.constants as ct
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.modeling import models, fitting
from astropy.stats import gaussian_fwhm_to_sigma
from astropy.wcs import WCS
from configparseradv.configparser import ConfigParserAdv as ConfigParser
from line_little_helper.molecule import Molecule
from scipy.odr import RealData, ODR, Model 
from toolkit.astro_tools.masking import mask_structures
from toolkit.astro_tools.images import get_coord_axes
from toolkit.array_utils import save_struct_array

from common_paths import RESULTS, CONFIGS
from edge_identification import PiecewisePowerLaw

def model(params, x):
    """Params are: amplitude, x_0, alpha, vsys, off0."""
    amplitude, x_0, alpha, vsys, off0 = params
    mask = x < off0
    vals = np.zeros(len(x))
    vals[mask] = amplitude * (np.abs(x[mask] - off0) / x_0)**-alpha
    vals[~mask] = -amplitude * ((x[~mask] - off0) / x_0)**-alpha

    return vals + vsys

@dataclass
class ModelData:
    amplitude: float
    x_0: float
    alpha: float
    vsys: float
    off0: float
    sd_amplitude: float
    sd_x_0: float
    sd_alpha: float
    sd_vsys: float
    sd_off0: float
    info: int
    names: tuple = ('amplitude', 'x_0', 'alpha', 'vsys', 'offset0',
                     'sd_amplitude', 'sd_x_0', 'sd_alpha', 'sd_vsys',
                     'sd_offset0', 'info')

    @property
    def params(self):
        return [self.amplitude, self.x_0, self.alpha, self.vsys, self.off0]

    def __call__(self, x):
        return model(self.params, x)

    def to_txt(self):
        params = [f'{self.amplitude}',
                  f'{self.x_0}',
                  f'{self.alpha}',
                  f'{self.vsys}',
                  f'{self.off0}',
                  f'{self.sd_amplitude}',
                  f'{self.sd_x_0}',
                  f'{self.sd_alpha}',
                  f'{self.sd_vsys}',
                  f'{self.sd_off0}',
                  f'{self.info}']
        coefs = 'coeficients ='
        lines = []
        for name, param in zip(self.names, params):
            if 'sd' not in name and name != 'info':
                coefs += f' ${{model_{name}}}'
            lines.append(f'model_{name} = {param}')
        lines.append(coefs)
        
        return '\n'.join(lines)

def update_plot_config(plot_config, config):
    cfg = ConfigParser()
    cfg.read([plot_config, config])
    with open(plot_config, 'w') as configfile:
        cfg.write(configfile)

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
    xyvals = xyvals[:ind+1]

    # Get average
    edge_points = []
    edge_errors = []
    for x, y in xyvals:
        xran = np.arange(max(x - delta, 0),
                         min(x + delta + 1, data.shape[1]),
                         dtype=int)
        weight = data[y][xran]
        nanmask = np.isnan(weight)
        weight = weight[~nanmask]
        xran = xran[~nanmask]
        avg = np.sum(weight * xran) / np.sum(weight)
        err = np.sqrt(np.sum(weight**2 * beam.value**2)) / np.sum(weight)
        edge_points.append([avg, y])
        edge_errors.append(err)

    return np.array(edge_points), np.array(edge_errors)*beam.unit

def get_edge(fitsfile, rms, nsigma=3, delta=2, quadrant=1, xlim=None, ylim=None):
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

    # Get vsys
    xcoords_upper = np.array([coord[0] for coord in coords_upper])
    xcoords_lower = np.array([coord[0] for coord in coords_lower])
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
    # Limits
    if xlim is not None:
        xmask = (edges_x > xlim[0]) & (edges_x < xlim[1])
        edges_x = edges_x[xmask]
        edges_y = edges_y[xmask]
        errors = errors[xmask]
    if ylim is not None:
        ymask = (edges_y > ylim[0]) & (edges_y < ylim[1])
        edges_x = edges_x[ymask]
        edges_y = edges_y[ymask]
        errors = errors[ymask]
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

    return (edges_x, edges_y), (errors, yerr), vsys.to(u.km/u.s)

def fit_edge(fitsfile, edges, errors, vsys, distance, rms, name, nsigma=3,
             plot_config=None):
    # Open data
    image = fits.open(fitsfile)[0]
    xaxis, yaxis = get_coord_axes(image)
    xaxis = xaxis.to(u.arcsec)
    yaxis = yaxis.to(u.km/u.s)

    # Fit power law
    print('Initial vsys:', vsys)
    fit_x, fit_y = edges
    errx, erry = errors
    data = RealData(fit_x.value, fit_y.value, sx=errx.value, sy=erry.value)
    #amplitude = np.max(fit_y) - vsys.to(fit_y.unit)
    x_0 = 100 / distance.to(u.pc).value * u.arcsec
    x_0 = x_0.to(fit_x.unit)
    ind = fit_x > 0
    amplitude = fit_y[ind][np.nanargmin(fit_x[ind] - x_0)]
    print('100 au to arcsec: ', x_0)
    print('Initial amplitude: ', amplitude.value)
    beta0kep = [amplitude.value, x_0.value, 0.5, vsys.to(fit_y.unit).value, 0.]
    ifixbkep1 = [1, 0, 0, 1, 1]
    ifixbunre = [1, 0, 1, 1, 1]
    ifixbkep2 = [1, 0, 0, 0, 0]
    pwlaw = Model(model)
    fitter = fitting.SLSQPLSQFitter()
    apymodel = PiecewisePowerLaw(amplitude=amplitude.value,
                                 x_0=x_0.value,
                                 alpha=0.5,
                                 cons=vsys.to(fit_y.unit).value,
                                 x_mid=0.)
    apymodel.x_0.fixed = True
    apymodel.alpha.fixed = True
    apymodel.x_mid.min = np.nanmax(fit_x[fit_x < 0])
    apymodel.x_mid.max = np.nanmin(fit_x[fit_x > 0])
    print('x_mid range: ', apymodel.x_mid.min, apymodel.x_mid.max)
    keplerian = fitter(apymodel, fit_x.value, fit_y.value)
    print('Keplerian amplitude: ', keplerian.amplitude.value)
    #keplerian_odr = ODR(data, pwlaw, beta0=beta0kep, ifixb=ifixbkep1)
    #output1 = keplerian_odr.run()
    #print('First Keplerian run: ')
    #output1.pprint()
    beta0 = [keplerian.amplitude.value, x_0.value, 0.5, keplerian.cons.value,
             keplerian.x_mid.value]
    unrestricted_odr = ODR(data, pwlaw, beta0=beta0, ifixb=ifixbunre)
    output2 = unrestricted_odr.run()
    unrestricted = ModelData(*output2.beta, *output2.sd_beta, output2.info)
    print('Unrestricted run: ')
    output2.pprint()
    beta0 = output2.beta
    beta0[2] = 0.5
    keplerian_odr = ODR(data, pwlaw, beta0=beta0, ifixb=ifixbkep2)
    output3 = keplerian_odr.run()
    keplerian = ModelData(*output3.beta, *output3.sd_beta, output3.info)
    print('Last Keplerian:')
    output3.pprint()

    # Mass
    vel = np.abs(keplerian.amplitude) * fit_y.unit
    mass = vel**2 * 100*u.au / ct.G
    mass = mass.to(u.M_sun)
    sd_mass = np.abs(2 * mass * keplerian.sd_amplitude / keplerian.amplitude)
    print('Keplerian mass: ', mass, '+/-', sd_mass)

    # Config section and write results
    unrestricted_txt = unrestricted.to_txt()
    keplerian_txt = keplerian.to_txt()
    yunit_str = f'{fit_y.unit}'.replace(' ', '')
    sect1 = [f'[{name}_pvedge]',
             f"structured_array = {fitsfile.with_suffix('.edge.dat')}",
             'marker = o',
             'color = #46eff2',
             'linestyle = none',
             'plot_keys = OFFSET, VRAD']
    sect2 = [f'[{name}_keplerian_fit]',
             'function = piecewise_powerlaw',
             f'xrange = {xaxis[0].value} {xaxis[-1].value} {xaxis.unit}',
             f'yunit = {yunit_str}',
             'sampling = 500',
             'linestyle = --',
             'color = #eb5252',
             f'model_mass = {mass}',
             f'model_sd_mass = {sd_mass}']
    sect3 = [f'[{name}_unrestricted_fit]',
             'function = piecewise_powerlaw',
             f'xrange = {xaxis[0].value} {xaxis[-1].value} {xaxis.unit}',
             f'yunit = {yunit_str}',
             'sampling = 500',
             'linestyle = -',
             'color = #adacac']
    text = ('\n'.join(sect1) + '\n'*2 +
            '\n'.join(sect2) + '\n' + keplerian_txt + '\n'*2 +
            '\n'.join(sect3) + '\n' + unrestricted_txt)
    config = fitsfile.with_suffix('.plot.cfg')
    config.write_text(text)
    if plot_config is not None:
        update_plot_config(plot_config, config)

    # Quick look at fit
    newx = np.linspace(0., xaxis[-1].value, 500)
    extent = [xaxis[0].value, xaxis[-1].value,
              yaxis[0].value, yaxis[-1].value]
    fig, ax = plt.subplots()
    ax.imshow(image.data, origin='lower', extent=extent)
    ax.contour(image.data, levels=[rms * nsigma], extent=extent)
    ax.plot(fit_x, fit_y, 'ro')
    ax.plot(newx + unrestricted.off0,
            unrestricted(newx + unrestricted.off0),
            -newx + unrestricted.off0,
            unrestricted(-newx + unrestricted.off0),
            linestyle='-', color='k')
    #ax.plot(-newx + unrestricted.x_mid,
    #        unrestricted(-newx + unrestricted.x_mid), 'k-')
    ax.plot(newx + keplerian.off0,
            keplerian(newx + keplerian.off0), 'b--')
    ax.plot(-newx + keplerian.off0,
            keplerian(-newx + keplerian.off0), 'b--')
    ax.axhline(unrestricted.vsys, color='g', ls=':')
    ax.axhline(unrestricted.vsys, color='g', ls='--')
    ax.axvline(unrestricted.off0, color='g', ls='--')
    ax.set_xlim(xaxis[0].value, xaxis[-1].value)
    ax.set_ylim(yaxis[0].value, yaxis[-1].value)
    ax.set_xlabel('Offset (arcsec)')
    ax.set_ylabel('Radial Velocity (km/s)')
    ax.set_aspect('auto') 
    fig.savefig(fitsfile.with_suffix('.edges.png'))

    fig, ax = plt.subplots()
    ax.plot(np.log10(np.abs(fit_x.value - unrestricted.off0)),
            np.log10(np.abs(fit_y.value - unrestricted.vsys)),
            'kx')
    ax.set_xlabel('log(Offset / arcsec)')
    ax.set_ylabel('log(|$v_{rad} - v_{sys}$| / km/s)')
    fig.savefig(fitsfile.with_suffix('.profile.png'))

if __name__ == '__main__':
    # Summary information
    source_info = ConfigParser()
    source_info.read(CONFIGS / 'extracted/summary.cfg')

    for section in source_info.sections():
        #if section not in ['NGC_6334_I_N_alma1']:
        #    continue
        print('Working on section: ', section)
        config = source_info[section]
        name = config['name'] + '_alma' + config['alma']
        fitsfile = config.getpath('pvmap')
        rms = config.getquantity('pvnoise').to(u.Jy/u.beam).value
        distance = config.getquantity('distance')
        xlim = config.getquantity('xlim', fallback=None)
        ylim = config.getquantity('ylim', fallback=None)
        quadrant = config.getint('pvquadrant', fallback=1)
        nsigma = config.getfloat('pvnsigma', fallback=3.)
        plot_number = config.get('nplot', fallback=None)
        if plot_number is not None:
            plot_config = CONFIGS / f'plots/papers/group_pv_maps.{plot_number}.cfg'
        else:
            plot_config = None
        edges, errors, vsys = get_edge(fitsfile, rms, nsigma=nsigma,
                                       quadrant=quadrant,
                                       xlim=xlim, ylim=ylim)
        fit_edge(fitsfile, edges, errors, vsys, distance, rms, name, nsigma=nsigma,
                 plot_config=plot_config)
        print('=' * 80)

