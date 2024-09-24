from pathlib import Path
import textwrap

from astropy.modeling import models, fitting, Fittable1DModel, Parameter
from astropy.stats import gaussian_sigma_to_fwhm
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

# Some definitions
source_dir = Path('/home/myso/share/binary_project/G333_G335/G335.579-0.272')
figs = source_dir / 'figures/P6/'
spec_dir = source_dir / 'results_final/concat/specs'
spectra = ['G335.579-0.272.alma1a.ch3cn_k3.spec.dat',
           'G335.579-0.272.alma1a.13co.spec.dat']
limit = 3 * u.km/u.s
rms = 2 * u.mJy

fig, axs = plt.subplots(1, 2)

fmt = textwrap.dedent("""\
    B = {0.value} {0.unit} beam$^{{-1}}$ (fixed)
    A = {1.value:.1f} {1.unit} beam$^{{-1}}$
    $\mu$ = {2.value:.1f} {2.unit:latex_inline}
    FWHM = {3.value:.1f} {3.unit:latex_inline}""")

for i, (ax, spec) in enumerate(zip(axs, spectra)):
    # Load data
    vel, inty = np.loadtxt(spec_dir / spec, unpack=True)
    vel = vel * u.km/u.s
    inty =  inty * 1000 * u.mJy

    # Mask
    if 'ch3cn_k3' in spec:
        mask = (vel >= -0.0 * u.km/u.s) & (vel <= 3.0 *u.km/u.s)
        model_init = models.Const1D(amplitude=5*u.mJy) - \
                models.Gaussian1D(amplitude=4*u.Jy,
                                  mean=0*u.km/u.s,
                                  stddev=5*u.km/u.s)
    else:
        mask = (vel >= -2.5 * u.km/u.s) & (vel <= 3.2 *u.km/u.s)
        model_init = models.Const1D(amplitude=15*u.mJy) - \
                models.Gaussian1D(amplitude=4*u.Jy,
                                  mean=0*u.km/u.s,
                                  stddev=5*u.km/u.s)
    model_init.amplitude_0.fixed = True
    
    # Fit
    #model_init = NegGaussian1D(amplitude=4, mean=0,
    #                           stddev=.1, baseline=5)
    fitter = fitting.LevMarLSQFitter()
    #model_fit = fitter(model_init, vel[mask].value, inty[mask].value)
    model_fit = fitter(model_init, vel[mask], inty[mask])
    print(model_fit)

    # Plot
    new_vel = np.linspace(-10, 10, 100) * vel.unit
    ax.plot(vel, inty, ds='steps-mid', color='#249e4e')
    ax.plot(vel[mask], inty[mask], 'bs')
    ax.plot(new_vel, model_fit(new_vel), 'k-')
    ax.set_xlim(-10, 10)
    if 'ch3cn_k3' in spec:
        ax.set_ylim(-10, 40)
        ax.set_ylabel(f'Intensity ({inty.unit}/beam)')
        ax.annotate(
            fmt.format(
                model_fit.amplitude_0.quantity,
                model_fit.amplitude_1.quantity,
                model_fit.mean_1.quantity,
                model_fit.stddev_1.quantity*gaussian_sigma_to_fwhm,
            ),
            xy=(0.05, 0.75),
            xytext=(0.05, 0.75),
            xycoords='axes fraction',
            fontsize='x-small',
        )
    else:
        ax.set_ylim(-45, 70)
        ax.annotate(
            fmt.format(
                model_fit.amplitude_0.quantity,
                model_fit.amplitude_1.quantity,
                model_fit.mean_1.quantity,
                model_fit.stddev_1.quantity*gaussian_sigma_to_fwhm,
            ),
            xy=(0.35, 0.75),
            xytext=(0.35, 0.75),
            xycoords='axes fraction',
            fontsize='x-small',
        )
    ax.set_xlabel(f'Velocity ({vel.unit})')
    ax.annotate('({})'.format(chr(ord('a')+i)),
                xy=(0.08, 0.05),
                xytext=(0.08, 0.05),
                xycoords='axes fraction')

    # Error in sigma
    sigma = (4/np.pi)**0.25 * model_fit.stddev_1*gaussian_sigma_to_fwhm * rms / \
            (np.sqrt(8 * np.log(2)) * model_fit.amplitude_1.quantity)
    print(f'Error: {sigma}')
plt.savefig(figs / 'inverse_pcygni_gaussfit.pdf', bbox_inches='tight')
plt.savefig(figs / 'inverse_pcygni_gaussfit.png', bbox_inches='tight')
