"""Fit PV maps using SLAM."""
from configparser import ConfigParser
from pathlib import Path
import sys

import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.modeling import models, fitting, Parameter, Fittable1DModel
from astropy.stats import gaussian_fwhm_to_sigma
from astropy.wcs import WCS
from line_little_helper.molecule import Molecule
from toolkit.astro_tools.masking import mask_structures

from pipeline_feria import SOURCES, SECTIONS
from source_pipeline_extracted import SAVED_MOLS

MOLECULE = 'CH3OH'
TRANSITION = '18(3,15)-17(4,14)A,vt=0'
RESULTS = Path('/mnt/metis/dihca/results')

class BrokenPowerLaw(Fittable1DModel):
    amplitude = Parameter()
    x_mid = Parameter()
    x_0 = Parameter()
    alpha = Parameter()
    cons = Parameter()

    #def __init__(self, amplitude, x_0, alpha, cons):
    #    super().__init__(amplitude=amplitude, x_0=x_0, alpha=alpha)
    #    self.cons.value = cons

    @staticmethod
    def evaluate(x, amplitude, x_mid, x_0, alpha, cons):
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
    def fit_deriv(x, amplitude, x_mid, x_0, alpha, cons):
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

def get_edge(fitsfile, outdir, rms, nsigma=3, delta=2, quadrant=1):
    # Open data
    image = fits.open(fitsfile)[0]
    mask = image.data > rms * nsigma
    beam = np.sqrt(image.header['BMAJ'] * image.header['BMIN']) * u.deg
    beam = beam.to(u.arcsec) * gaussian_fwhm_to_sigma

    # Get axes

    # Get mask of the largest object
    mask, labels, nlabels = mask_structures(mask)
    component_sizes = np.bincount(labels.ravel())
    max_component = component_sizes == np.nanmax(component_sizes[1:])
    max_mask = max_component[labels]
    mask[~max_mask] = False

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

    # Fit power law
    xmid = image.data.shape[1] / 2
    ind1 = np.nanargmax(np.abs(edges_upper[:, 0] - xmid))
    ind2 = np.nanargmax(np.abs(edges_lower[:, 0] - xmid))
    vsys = (edges_upper[ind1, 1] + edges_lower[ind2, 1]) / 2
    fit_x = np.append(edges_upper[:, 0], edges_lower[:, 0])
    ind = np.argsort(fit_x)
    fit_y = np.append(edges_upper[:, 1], edges_lower[:, 1])
    fit_x = fit_x[ind]
    fit_y = fit_y[ind]
    amplitude = np.max(fit_y) - vsys
    x_0 = np.abs(np.min(fit_x))
    # Upper
    fitter = fitting.SLSQPLSQFitter()
    model = BrokenPowerLaw(amplitude=amplitude,
                           x_mid=xmid,
                           x_0=x_0,
                           alpha=0.5,
                           cons=vsys)
    #model.alpha.fixed = True
    fitted = fitter(model, fit_x, fit_y)
    print(fitted)
    #ind = np.nanargmin(np.abs(edges_upper[:, 0] - xmid))
    #vsysm = models.Const1D(amplitude=vsys)
    #pwlaw = models.PowerLaw1D(amplitude=edges_upper[ind, 1] - vsys,
    #                          x_0=edges_upper[ind, 0] - xmid,
    #                          alpha=0.5)
    #model = pwlaw + vsysm
    #model.alpha_0.fixed = True
    ##model.x_0_0.min = min(xmid, edges_upper[ind, 0])
    ##model.x_0_0.max = edges_upper[ind, 0]
    ##model.amplitude_0.max = edges_upper[ind, 1] - vsys
    ##model.amplitude_1.min = vsys - 3
    ##model.amplitude_1.max = vsys + 3
    #fit_upper = fitter(model, edges_upper[:, 0] - xmid, edges_upper[:,1])
    ## Lower
    #ind = np.nanargmin(np.abs(edges_lower[:, 0] - xmid))
    #pwlaw = models.PowerLaw1D(amplitude=edges_lower[ind, 1] - vsys,
    #                          x_0=np.abs(edges_lower[ind, 0] - xmid),
    #                          alpha=0.5)
    #model = pwlaw + vsysm
    #model.alpha_0.fixed = True
    ##model.x_0_0.min = min(xmid, edges_lower[ind, 0])
    #model.x_0_0.max = edges_lower[ind, 0]
    #model.amplitude_0.min = edges_lower[ind, 1] - vsys
    #sign_lower = np.sign(edges_lower[:,0]-xmid)[0]
    #fit_x = np.abs(edges_lower[:,0] - xmid)
    #fit_lower = fitter(model, fit_x, edges_lower[:,1])

    newx = np.linspace(0, image.shape[1])
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    ax1.plot(np.log10(np.abs(fit_x - fitted.x_mid.value)),
             np.log10(np.abs(fit_y - fitted.cons.value)),
             'kx')
    ax2.imshow(image.data, origin='lower')
    ax2.contour(image.data, levels=[rms * nsigma])
    ax2.plot(fit_x, fit_y, 'ro')
    ax2.plot(newx, fitted(newx), 'k-')
    #ax.plot(edges_upper[:,0], edges_upper[:,1], 'ro')
    #ax.plot(sign_lower * fit_x + xmid, edges_lower[:,1], 'bo')
    #ax.plot(newx + xmid, fit_upper(newx), 'k-')
    #ax.plot(sign_lower * newx + xmid, fit_lower(newx), 'k-')
    ax2.axhline(vsys, color='g', ls=':')
    ax2.axhline(fitted.cons.value, color='g', ls='--')
    ax2.axvline(fitted.x_mid.value, color='g', ls='--')
    ax2.axvline(fitted.x_0.value, color='g', ls='--')
    ax2.axvline(xmid, color='g', ls=':')
    ax2.set_xlim(0, image.shape[1])
    ax2.set_ylim(image.shape[0], 0)
    fig.savefig(outdir / 'edges.png')

    # Convert to coordinates
    wcs = WCS(image.header)
    coords_upper = wcs.pixel_to_world_values(edges_upper)
    coords_lower = wcs.pixel_to_world_values(edges_lower)

if __name__ == '__main__':
    # Set config sections
    section_src, section_pv = SECTIONS[MOLECULE]

    # Load molecule information
    molecule = Molecule.from_json(SAVED_MOLS[MOLECULE])
    restfreq = molecule.transition_info(TRANSITION).restfreq

    for src, hmcs in SOURCES.items():
        for hmc in hmcs:
            fitsfile = RESULTS / f'{src}/c5c8/per_hot_core/{hmc}_pvmaps'
            fitsfile = fitsfile / 'G335.579-0.272_hmc2_rotation.CH3OH_spw0.ra247.74430_dec-48.73089.PA202.fits'
            outdir = RESULTS / f'{src}/c5c8/per_hot_core/{hmc}_pvmaps'
            outdir.mkdir(exist_ok=True)
            get_edge(fitsfile, outdir, 1.5e-3)
