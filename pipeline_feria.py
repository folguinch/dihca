"""Run MCMC modeling with FERIA for all sources."""
from multiprocessing import Pool
from configparser import ConfigParser
import datetime

import corner
import emcee
import numpy as np
import matplotlib.pyplot as plt
from line_little_helper.molecule import Molecule

from common_paths import RESULTS, CONFIGS
from source_pipeline_extracted import SAVED_MOLS
from feria_mcmc import log_posterior_cube, ObsFit, Model, log_posterior_pv

#MOLECULE = 'CH3OH'
#TRANSITION = '18(3,15)-17(4,14)A,vt=0'
SOURCES = {
    'G335.579-0.272': ('alma3',),
}
#SECTIONS = {
#    'CH3OH': ('b6_c5c8_spw0_1000_CH3OH_18_3_15_-17_4_14_A_vt_0',
#              'CH3OH_spw0'),
#}
NCORE = 10
NWALKERS, NSTEPS, NBURN = 120, 250, 180
#NCORE = 1
#NWALKERS, NSTEPS, NBURN = 15, 30, 10
CUBE_FIT = False

#FIXED_PARAMS = {
#    'rot': -1,
#    'rin': 'CB',
#    #'vsys': -48.8,
#    'ireheight': 0.,
#    'ireflare': 30,
#    'irenprof': -1.5,
#    'iretprof': -0.4,
#    'kepheight': 0.5,
#    'kepflare': 30,
#    'kepnprof': -1.5,
#    'keptprof': -0.4,
#    'cbdens': 1e-2,
#    'cbtemp': 50,
#    'pvra': 0.0,
#    'pvdec': 0.0,
#}
#PARAMS = {
#    'vsys': 0,
#    'mass': 10,
#    'rcb': 200,
#    'incl': 60,
#    #'pa': 
#    'rout': 1000,
#    'lw': 2.0,
#}
#RANGES = {
#    #'vsys': (-2, 2),
#    'mass': (3, 40),
#    'rcb': (10, 1000),
#    #'rin': (10, 100),
#    'incl': (-90, 90),
#    'rout': (500, 5000),
#    'lw': (0.1, 3.0),
#}
LABELS = {
    'vsys': r'$\Delta v_{\rm sys}$ (km/s)',
    'mass': r'$M_{c}$ ($M_\odot$)',
    'rcb': '$R_{cb}$ (au)',
    'rin': '$R_{in}$ (au)',
    'incl': '$i$ (deg)',
    'rout': r'$R_{\rm out}$',
    'lw': 'Line width (km/s)',
    'pa': 'P.A. (deg)',
}

def initialize_guesses(param_ranges, nwalkers):
    # Produce guess from the given range of parameters
    np.random.seed()
    guesses = [np.random.uniform(par[0], par[1], nwalkers)
               for key, par in param_ranges.items()]

    return np.array(guesses).T

def show_walkers(sampler, parameters, output):
    # loop over the walkers and should how it converge
    nwalkers = sampler.chain.shape[0]
    ndim = len(parameters)
    labels = [LABELS[key] for key in parameters]

    plt.figure(figsize=(8, ndim*1.5))
    for j in range(nwalkers):
        for i in range(ndim):
            plt.subplot(ndim, 1, i+1)
            plt.plot(sampler.chain[j,:,i], ',')
            plt.ylabel(labels[i], fontsize=14);
            plt.xlabel('step', fontsize=14);

    plt.savefig(output / 'mcmc_walkers.pdf', bbox_inches='tight')

def show_bestfit_paras(sampler, parameters, output):

    # show the summary plot of fitted parameters
    plt.figure(figsize=(10, 10))
    labels = [LABELS[key] for key in parameters]
    corner.corner(sampler, labels=labels, quantiles=[0.16, 0.5, 0.84],
                  show_titles=True)
    plt.savefig(output / 'mcmc_corner.pdf', bbox_inches='tight')

def calc_mcmc(params_ranges, params_fixed, obs, outdir, ncore=NCORE,
              nwalkers=NWALKERS, nsteps=NSTEPS, nburn=NBURN):
    # initialize guesses
    guesses = initialize_guesses(params_ranges, nwalkers)

    # Run MCMC
    start = datetime.datetime.now()
    out_iter = outdir / 'models'
    out_iter.mkdir(parents=False, exist_ok=True)
    posterior_kwargs = {'fixed_params': params_fixed,
                        'ranges': params_ranges,
                        'obs': obs,
                        'outdir': out_iter}
    with Pool(ncore) as pool:
        sampler = emcee.EnsembleSampler(
            nwalkers,
            len(params_ranges),
            log_posterior_cube if CUBE_FIT else log_posterior_pv,
            kwargs=posterior_kwargs,
            pool=pool,
            parameter_names=list(params_ranges.keys()),
            )
        sampler.run_mcmc(guesses, nsteps, progress=True)
    
    # Plots
    show_walkers(sampler, params_ranges, outdir)
    post = np.concatenate(sampler.chain[:, nburn:, :])
    show_bestfit_paras(post, params_ranges, outdir)

    # Print the best fit parameters
    fout = outdir / 'mcmc_paramters.dat'
    txtlines = []
    final_params = {}
    for i, param in enumerate(params_ranges):
       mcmc = np.percentile(post[:, i], [16, 50, 84])
       q = np.diff(mcmc)
       txtlines.append(f'{param}: {mcmc[1]:.4f}   {q[0]:.4f}   {q[1]:.4f}')
       final_params[param] = mcmc[1]
    fout.write_text('\n'.join(txtlines))

    # Compute best model
    best_model = Model(list(params_fixed.keys()),
                       **(final_params | params_fixed))
    best_model_cube = best_model(outdir, obs)
    end = datetime.datetime.now()

    print(start)
    print(end)
    print(end - start)

if __name__ == '__main__':
    # Set config sections
    #section_src, section_pv = SECTIONS[MOLECULE]

    # Load molecule information
    #molecule = Molecule.from_json(SAVED_MOLS[MOLECULE])
    #restfreq = molecule.transition_info(TRANSITION).restfreq

    for src, hmcs in SOURCES.items():
        for hmc in hmcs:
            # Create results directory
            outdir = RESULTS / src / f'c5c8/per_hot_core/{hmc}_feria_mcmc'
            outdir.mkdir(parents=False, exist_ok=True)

            # Open pv config
            #pvconfig_file = CONFIGS / f'extracted/pvmaps/{src}_{hmc}_rotation.cfg'
            #pvconfig = ConfigParser()
            #pvconfig.read(pvconfig_file)

            # Create observation
            config_file = CONFIGS / f'feria_fit/{src}_{hmc}.cfg'
            #obs = Observation(config_file, section_src, MOLECULE, restfreq,
            #                  outdir)
            obs = ObsFit(config_file, outdir)

            # Parameter ranges
            #pa = pvconfig.getfloat(section_pv, 'disk_pa')
            #params_ranges = RANGES | {'pa': (pa - 50, pa + 50)}
            #params_fixed = FIXED_PARAMS | {'pvpa': pa}
            params_ranges = obs.get_param_ranges()
            params_fixed = obs.get_fixed_params()

            # Run MCMC
            calc_mcmc(params_ranges, params_fixed, obs, outdir)

