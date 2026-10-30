"""Plot corner plot from results."""
from pathlib import Path
from itertools import product

import corner
import emcee
import numpy as np
import matplotlib.pyplot as plt

LABELS = {
    'vsys': r'$\Delta v_{\rm sys}$ (km/s)',
    'mass': r'$M_{c}$ ($M_\odot$)',
    'rcb': r'$R_{\rm cb}$ (au)',
    'rin': r'$R_{\rm in}$ (au)',
    'incl': '$i$ (deg)',
    'rout': r'$R_{\rm out}$',
    'lw': r'$\Delta$ v (km/s)',
    'pa': r'PA$_{\rm mid}$ (deg)',
    'dra': r'$\Delta\alpha$ (mas)',
    'ddec': r'$\Delta\delta$ (mas)',
    'ireflare': r'$F_{IRE}$ (deg)',
}
parameters = ['mass', 'rcb', 'incl', 'rout', 'lw', 'ireflare', 'pa', 'dra',
              'ddec']

results = Path('../../../results/feria_fit')
figures = Path('../../../figures/G335.579-0.272/papers')
region = 'G335.579-0.272' 
sources = ['ALMAe1', 'ALMAe4']
fits = ['ire_all', 'ire_pvrot', 'ire_pvrot_pvout',
        'ire+disk_all', 'ire_pvrot', 'ire_pvrot_pvout']

for source, fit in product(sources, fits):
    model = results / f'{region}_{source}_{fit}'
    preliminary = results / f'{region}_{source}_{fit}_preliminary'
    if preliminary.exists():
        model = preliminary
    print('Model:', model)

    filename = model / 'chain.h5'
    sampler = emcee.backends.HDFBackend(filename)
    tau = sampler.get_autocorr_time(tol=0)
    burnin = int(2 * np.max(tau))
    print('Burn:', burnin)
    post = sampler.get_chain(discard=burnin, flat=True)

    plt.figure(figsize=(10, 10))
    labels = [LABELS[key] for key in parameters]
    corner.corner(post, labels=labels, quantiles=[0.16, 0.5, 0.84],
                  show_titles=True, title_fmt='.2g')
    figname = figures / f'{source}_{fit}_mcmc_corner.pdf'
    plt.savefig(figname, bbox_inches='tight')
    plt.close()
