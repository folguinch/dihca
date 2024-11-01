from astropy.modeling import models, fitting
from matplotlib.ticker import FuncFormatter
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

def formatter(kind, sci=(-3,4)):
    if kind == 'log':
        def logformatter(x, pos):
            if x <= 10**sci[0]:
                return '10$^{%i}$' % np.floor(np.log10(x))
            elif x < 1:
                return '%g' % x
            elif x < 10**sci[1]:
                return '%i' % x
            else:
                return '$10^{%i}$' % np.floor(np.log10(x))
        return FuncFormatter(logformatter)

freq = np.array([6.0, 8.0, 23.0, 25.0, 43.2, 226.2]) * u.GHz
snu = np.array([0.16, 0.302, 1.76, 1.41, 3.14, 93]) * u.mJy
snu_err =  np.array([0.036, 0.039, 0.22, 0.17, 0.91, 9.3]) * u.mJy

fitter = fitting.LevMarLSQFitter()

dust_init = models.PowerLaw1D(amplitude=90*u.mJy, x_0=220*u.GHz,
                              alpha=-(2.0+2), fixed={'alpha': True})
ff_init = models.PowerLaw1D(amplitude=1*u.mJy, x_0=220*u.GHz, alpha=-0.5)
total_init = dust_init + ff_init

def tied(model):
    return model.x_0_0

total_init.x_0_1.tied = tied

fitted_model = fitter(total_init, freq, snu, weights=1/snu_err)

print(fitted_model)

xval = np.logspace(0, 4)
yval = fitted_model(xval * u.GHz)

# Free-free contribution
ff_model = models.PowerLaw1D(amplitude=fitted_model.amplitude_1,
                             x_0=fitted_model.x_0_1,
                             alpha=fitted_model.alpha_1)
ff_contribution = ff_model(freq[-1]).to(u.Jy)
yval_ff = ff_model(xval * u.GHz)
print('Free-free model:', ff_model)
print(f'Free-free contribution: {ff_contribution}')

# Only free-free
fitted_ff = fitter(ff_model, freq[:-1], snu[:-1], weights=1/snu_err[:-1])
yval_ff = fitted_ff(xval * u.GHz)
ff_contribution = fitted_ff(freq[-1]).to(u.mJy)
print(f'All free-free contribution: {ff_contribution}')

fig = plt.figure(figsize=(4,7))
ax = fig.add_subplot()
capsize = 2

ax.set_yscale('log')
ax.set_xscale('log')
ax.xaxis.set_major_formatter(formatter('log'))
ax.yaxis.set_major_formatter(formatter('log'))
ax.errorbar(freq[:-1].value, snu[:-1].value, yerr=snu_err[:-1].value,
            fmt='o', color='r', mec='r', capsize=capsize)
ax.errorbar(freq[-1].value, snu[-1].value, yerr=snu_err[-1].value,
            fmt='s', color='b', mec='b', capsize=capsize)
ax.errorbar(freq[-1].value, 69, yerr=6, fmt='^', color='g', mec='g',
            capsize=capsize)
ax.errorbar(freq[-1].value, 72, yerr=3, fmt='p', color='c', mec='c',
            capsize=capsize)
ax.plot(xval, yval_ff, color='#666666', ls='--')
ax.plot(xval, yval, 'b-')
ax.annotate(r'$\alpha_{ff} = ' + f'{-fitted_model.alpha_1:.2f}$', 
            xy=(0.1,0.95), xytext=(0.1,0.95), xycoords='axes fraction',
            color='b')
#ax.annotate(r'$\alpha_{ff} = ' + f'{-fitted_ff.alpha:.2f}$', 
#            xy=(0.1,0.95), xytext=(0.1,0.90), xycoords='axes fraction',
#            color='#666666')
ax.set_xlabel('Frequency (GHz)')
ax.set_ylabel('Flux (mJy)')
ax.set_xlim(1, 1000)
ax.set_ylim(0.1, 500)
fig.savefig('../figures/P6/alma1_sed.pdf', bbox_inches='tight')
fig.savefig('../figures/P6/alma1_sed.png', bbox_inches='tight')
