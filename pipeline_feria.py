"""Run MCMC modeling with FERIA."""
from typing import Dict, Tuple, Sequence, Union, Optional, List
from collections.abc import Iterable
from configparser import ConfigParser
from multiprocessing import Pool
from pathlib import Path
import argparse
import datetime
import json
import os
import sys

import corner # type: ignore
import emcee # type: ignore
import matplotlib.pyplot as plt
import numpy as np

#from common_paths import RESULTS, CONFIGS
from feria_mcmc import (log_posterior_cube, ObsFit, Model,
                        log_posterior_pv, pv_products)

#SOURCES = {
#    'G335.579-0.272': ('ALMAe4',),
#    #'G335.579-0.272': ('ALMAe1',),
#    #'G35.20-0.74_N': ('ALMAe1',),
#    #'NGC_6334_I_N': ('ALMAe8',),
#}
NCORE: int = 10
NWALKERS: int = 200
NSTEPS: int = 250
MAXITER: int = 30
#NCORE = 1
#NBURN = 180
#NWALKERS, NSTEPS, NBURN = 15, 30, 10
CUBE_FIT: bool = False
LABELS: Dict[str, str] = {
    'vsys': r'$\Delta v_{\rm sys}$ (km/s)',
    'mass': r'$M_{c}$ ($M_\odot$)',
    'rcb': '$R_{cb}$ (au)',
    'rin': '$R_{in}$ (au)',
    'incl': '$i$ (deg)',
    'rout': r'$R_{\rm out}$',
    'lw': 'Line width (km/s)',
    'pa': 'P.A. (deg)',
    'dra': r'$\Delta$R.A. (mas)',
    'ddec': r'$\Delta$Decl. (mas)',
    'ireflare': r'$\theta_{IRE}$ (deg)',
}

def initialize_guesses(param_ranges: Dict[str, Tuple[float, float]],
                       nwalkers: int):
    """Produce guess from the given range of parameters."""
    np.random.seed()
    guesses = [np.random.uniform(par[0], par[1], nwalkers)
               for key, par in param_ranges.items()]

    return np.array(guesses).T

def show_walkers(sampler: emcee.EnsembleSampler,
                 parameters: Dict[str, Tuple[float, float]],
                 output: Path) -> None:
    """Plot walkers."""
    # loop over the walkers and should how it converge
    nwalkers = sampler.chain.shape[0]
    ndim = len(parameters)
    labels = [LABELS[key] for key in parameters]

    plt.figure(figsize=(8, ndim*1.5))
    for j in range(nwalkers):
        for i in range(ndim):
            plt.subplot(ndim, 1, i+1)
            plt.plot(sampler.chain[j,:,i], ',')
            plt.ylabel(labels[i], fontsize=14)
            plt.xlabel('step', fontsize=14)

    plt.savefig(output / 'mcmc_walkers.pdf', bbox_inches='tight')
    plt.close()

def show_bestfit_params(sampler: Sequence,
                        parameters: Dict[str, Tuple[float, float]],
                        output: Path) -> None:
    """Corner plot of the modeling."""
    plt.figure(figsize=(10, 10))
    labels = [LABELS[key] for key in parameters]
    corner.corner(sampler, labels=labels, quantiles=[0.16, 0.5, 0.84],
                  show_titles=True)
    plt.savefig(output / 'mcmc_corner.pdf', bbox_inches='tight')
    plt.close()

def plot_autocorrelation(autocorr: Sequence,
                         nsteps: int,
                         outdir: Path) -> None:
    """Plot autocorrelation for steps."""
    n = nsteps * np.arange(1, len(autocorr) + 1)
    y = np.array(autocorr)
    plt.close()
    plt.plot(n, n / 100.0, '--k')
    plt.plot(n, y)
    plt.xlim(0, n.max())
    plt.ylim(0, y.max() + 0.1 * (y.max() - y.min()))
    plt.xlabel('Number of steps')
    plt.ylabel(r'Mean $\hat{\tau}$')
    plt.savefig(outdir / 'autocorrelation_time.png')
    plt.close()

def params_from_chain(chain: Sequence,
                      params: Iterable[str],
                      percentiles: Sequence[float] = (50,)
                      ) -> Tuple[Dict, List]:
    """Get parameter values from chain."""
    if len(percentiles) not in (1, 3):
        raise ValueError('Invalid number of percentiles')
    txtlines = []
    final_params = {}
    for i, param in enumerate(params):
        mcmc = np.percentile(chain[:, i], percentiles) # type: ignore
        if len(percentiles) == 3:
            q = np.diff(mcmc)
            txtlines.append(f'{param}: {mcmc[1]:.4f}   {q[0]:.4f}   {q[1]:.4f}')
            final_params[param] = mcmc[1]
        else:
            txtlines.append(f'{param}: {mcmc[0]:.4f}')
            final_params[param] = mcmc[0]

    return final_params, txtlines

def params_to_config(params_fitted: Union[Dict[str, Union[float, int]],
                                          Iterable[str]],
                     params_fixed: Dict[str, Union[float, int]],
                     outdir: Path,
                     chain: Optional[Sequence] = None,
                     ):
    """Store parameters in confi file."""
    if chain is not None:
        final_params, _ = params_from_chain(chain, params_fitted)
    else:
        final_params = params_fitted # type: ignore
    final_config = {'best_fit': final_params | params_fixed}
    config = ConfigParser()
    config.read_dict(final_config)
    config_file = outdir / 'best_model.cfg'
    with config_file.open('w') as fl:
        config.write(fl)

def store_parameters(chain: Sequence,
                     outdir: Path,
                     params_ranges: Dict[str, Tuple[float, float]],
                     params_fixed: Dict[str, Union[float, int]],
                     percentiles: Sequence[float] = (16, 50, 84),
                     **texts) -> Dict[str, Union[float, int]]:
    """Store best parameters in text file and config file."""
    # Text file
    fout = outdir / 'mcmc_paramters.dat'
    txtlines = [f'{key}: {val}' for key, val in texts.items()]
    final_params, lines = params_from_chain(chain, params_ranges,
                                            percentiles=percentiles)
    txtlines += lines
    fout.write_text('\n'.join(txtlines))

    # Config file
    params_to_config(final_params, params_fixed, outdir)

    return final_params

def calc_mcmc(params_ranges: Dict[str, Tuple[float, float]],
              params_fixed: Dict[str, Union[float, int]],
              obs: ObsFit,
              outdir: Path,
              ncore: int = 1,
              nwalkers: int = NWALKERS,
              nsteps: int = NSTEPS,
              maxiter: int = MAXITER,
              nburn: Optional[int] = None,
              cube_fit: bool = False):
    """Run MCMC fitting."""
    # Record inital time
    start = datetime.datetime.now()

    # initialize guesses
    guesses = initialize_guesses(params_ranges, nwalkers)

    # Create directory for models
    out_iter = outdir / 'models'
    out_iter.mkdir(parents=False, exist_ok=True)

    # Posterior keyword arguments
    posterior_kwargs = {'fixed_params': params_fixed,
                        'ranges': params_ranges,
                        'obs': obs,
                        'outdir': out_iter}

    # EMCEE backend to store chain
    filename = outdir / 'chain.h5'
    backend = emcee.backends.HDFBackend(filename)

    # Check autocorrelation file
    autocorr_file = outdir / 'autocorr.json'
    if autocorr_file.is_file():
        print('Reading autocorr file')
        autocorr = json.loads(autocorr_file.read_text())
        old_tau = autocorr[-1]
        print(f'Old autocorr tau: {old_tau}')
    else:
        autocorr = []
        old_tau = np.inf

    # Run MCMC
    with Pool(ncore) as pool:
        for i in range(maxiter):
            print(f'Iteration {i+1}')
            sampler = emcee.EnsembleSampler(
                nwalkers,
                len(params_ranges),
                log_posterior_cube if cube_fit else log_posterior_pv,
                kwargs=posterior_kwargs,
                pool=pool,
                parameter_names=list(params_ranges.keys()),
                backend=backend,
                )
            sampler.run_mcmc(guesses, nsteps, progress=True)

            # Check convergence
            print('Checking convergence')
            tau = sampler.get_autocorr_time(tol=0)
            autocorr.append(float(np.mean(tau)))
            autocorr_file.write_text(json.dumps(autocorr))
            converged = (np.all(tau * 100 < sampler.iteration) &
                         np.all(np.abs(old_tau - tau) / tau < 0.01))
            if converged:
                print('Chain converged')
                break
            os.system(f'rm -r {out_iter}')
            out_iter.mkdir(parents=False, exist_ok=True)
            old_tau = tau

    # Plot walkers
    show_walkers(sampler, params_ranges, outdir)

    # Post-process chain
    #tau = backend.get_autocorr_time(tol=0)
    print(f'Mean autocorrelation times per iteration: {autocorr}')
    if nburn is not None:
        burnin = nburn
    else:
        burnin = int(2 * np.max(tau))
    print(f'Final tau: {tau}')
    print(f'Burn: {burnin}')
    #thin = int(0.5 * np.min(tau))
    #post = np.concatenate(sampler.chain[:, nburn:, :])
    post = sampler.get_chain(discard=burnin, flat=True)
    #post = backend.get_chain(discard=burnin, flat=True)

    # Plots
    show_bestfit_params(post, params_ranges, outdir)

    # Plot tau
    plot_autocorrelation(autocorr, nsteps, outdir)

    # Save the best fit parameters
    final_params = store_parameters(post, outdir, params_ranges,
                                    params_fixed, burn=burnin)

    # Compute best model
    best_model = Model(list(params_fixed.keys()),
                       **(final_params | params_fixed))
    best_model_cube = best_model(outdir, obs)
    _ = pv_products(best_model_cube, obs, save_products=True)

    # Final time
    end = datetime.datetime.now()

    print(start)
    print(end)
    print(end - start)

def feria_fit(cmdargs: argparse.Namespace):
    """Fit data with FERIA."""
    # Get configs
    #configs = []
    #outdirs = []
    #if args.config is None:
    #    # Use the global values in the script
    #    for src, hmcs in SOURCES.items():
    #        for hmc in hmcs:
    #        # Create results directory
    #        outdir = RESULTS / src / f'c5c8/per_hot_core/{hmc}_feria_mcmc'
    #        outdir.mkdir(parents=False, exist_ok=True)
    #        outdirs.append(outdir)
    #
    #        # Create observation
    #        config_file = CONFIGS / f'feria_fit/{src}_{hmc}.cfg'
    #        args.configs.append(config_file)
    for config in map(Path, cmdargs.config):
        # Create results directory
        outdir = Path(cmdargs.outdir[0]) / config.stem
        outdir.mkdir(parents=True, exist_ok=True)

        # Read observations
        obs = ObsFit(config, outdir)

        # Parameter ranges
        params_ranges = obs.get_param_ranges()
        params_fixed = obs.get_fixed_params()

        # Run MCMC
        calc_mcmc(params_ranges, params_fixed, obs, outdir,
                  ncore=cmdargs.ncore, nwalkers=cmdargs.nwalkers,
                  nsteps=cmdargs.nsteps, maxiter=cmdargs.maxiter,
                  nburn=cmdargs.nburn, cube_fit=cmdargs.fit_cube)

def to_config(cmdargs: argparse.Namespace):
    burnin = cmdargs.nburn
    for config in map(Path, cmdargs.config):
        # Create results directory
        outdir = Path(cmdargs.outdir[0]) / config.stem
        outdir.mkdir(parents=True, exist_ok=True)

        # Read observations
        obs = ObsFit(config, outdir)
        params_ranges = obs.get_param_ranges()
        params_fixed = obs.get_fixed_params()

        # Load chain
        filename = outdir / 'chain.h5'
        print(f'Loading chain {filename}')
        backend = emcee.backends.HDFBackend(filename)
        if burnin is None:
            tau = backend.get_autocorr_time(tol=0)
            burnin = int(2 * np.max(tau))
        print(f'Burn: {burnin}')
        chain = backend.get_chain(discard=burnin, flat=True)

        # To config
        params_to_config(params_ranges.keys(), params_fixed, outdir,
                         chain=chain)

def from_model_cube(cmdargs: argparse.Namespace):
    """Obtain additional PVs from model results.

    The information about the additional PVs is given in a configuration
    file.
    """
    # Output directory
    config = Path(args.config[0])
    outdir = Path(cmdargs.outdir[0]) / config.stem
    outdir.mkdir(parents=True, exist_ok=True)
    obs = ObsFit(config, outdir)
    
    for cube in args.cubes:
        print(f'Working on cube: {cube}')
        _ = pv_products(cube, obs, save_products=True,
                        is_regrid=args.is_regrid, get_max_map=False)

if __name__ == '__main__':
    # Parser
    parser = argparse.ArgumentParser(
        add_help=True,
        description='Data fitting with FERIA.',
    )

    # Subparsers
    subparsers = parser.add_subparsers(title='Functionality',
                                       required=True,
                                       help='Subcommand help')
    fitting = subparsers.add_parser(
        'fit',
        help='Fit data using FERIA models')
    postproc = subparsers.add_parser(
        'from_model',
        conflict_handler='resolve',
        help='Calculate product images from model')
    convert = subparsers.add_parser(
        'to_config',
        help='Convert final parameters to configuration (for old runs)')

    # Common arguments
    parser.add_argument('--outdir', nargs=1, default=['./'],
                        help='Output directory')
    parser.add_argument('config', nargs='+', default=None,
                        help='Configuration files')

    # Fitting arguments
    fitting.add_argument('--ncore', type=int, default=NCORE,
                         help='Number of processes')
    fitting.add_argument('--nwalkers', type=int, default=NWALKERS,
                         help='Number of MCMC walkers')
    fitting.add_argument('--nsteps', type=int, default=NSTEPS,
                         help='Number of MCMC steps')
    fitting.add_argument('--nburn', type=int, default=None,
                         help='Number of steps to burn')
    fitting.add_argument('--maxiter', type=int, default=MAXITER,
                         help='Maximum number of iterations')
    fitting.add_argument('--fit_cube', action='store_true',
                         help='Fit cube instead of PV')
    fitting.set_defaults(func=feria_fit)

    # Convert best model to config
    convert.add_argument('--nburn', type=int, default=None,
                         help='Number of steps to burn')

    # Calculate additional images
    postproc.add_argument('--is_regrid', action='store_true',
                          help='Are the input cubes regrided?')
    postproc.add_argument('config', nargs=1, default=None,
                          help='Configuration files')
    postproc.add_argument('cubes', nargs='+', default=None,
                          help='Model cubes')
    postproc.set_defaults(func=feria_fit)

    # Process arguments
    args = parser.parse_args(sys.argv[1:])
    args.func(args)

