"""Calculate the effect of nsigma in the parameter values."""
import astropy.units as u
import numpy as np
from configparseradv.configparser import ConfigParserAdv as ConfigParser

from common_paths import RESULTS, CONFIGS
from edge_identification_odr import get_edge, fit_edge

def summarize(results):
    unrestricted = []
    keplerian = []
    mass = []
    for result in results:
        unrestricted.append(result[0].params)
        keplerian.append(result[1].amplitude)
        mass.append(result[2].value)

    unrestricted_mean = np.mean(np.array(unrestricted), axis=0)
    unrestricted_std = np.std(np.array(unrestricted), axis=0)
    keplerian_mean = np.mean(keplerian)
    keplerian_std = np.std(keplerian)
    mass_mean = np.mean(mass)
    mass_std = np.std(mass)

    return (unrestricted_mean, unrestricted_std, keplerian_mean, keplerian_std,
            mass_mean, mass_std)

def write_summary(results, filename):
    head = ['#Name', 'amplitude', 'x_0', 'alpha', 'vsys', 'offset0',
            'amplitude_kep', 'mass']
    means = ['\t'.join(head)]
    stds = ['\t'.join(head)]
    for name, res in results.items():
        vals = res[::2]
        vals = [name] + list(vals[0]) + [vals[1], vals[2]]
        means.append('\t'.join(map(str, vals)))
        vals = res[1::2]
        vals = [name] + list(vals[0]) + [vals[1], vals[2]]
        stds.append('\t'.join(map(str, vals)))

    filename.with_suffix('.means.dat').write_text('\n'.join(means))
    filename.with_suffix('.stds.dat').write_text('\n'.join(stds))

def write_source_results(name, results, nsigma):
    filename = RESULTS / 'overall' / f'{name}_nsigma_error.txt'
    alphas = ['alpha']
    masses = ['kep_mass']
    for result in results:
        alphas.append(result[0].alpha)
        masses.append(result[2].value)
    lines = [f'nsigma: {nsigma}']
    lines += ['\t'.join(map(str, alphas))]
    lines += ['\t'.join(map(str, masses))]
    filename.write_text('\n'.join(lines))

if __name__ == '__main__':
    # Summary information
    source_info = ConfigParser()
    source_info.read(CONFIGS / 'extracted/summary.cfg')
    results_per_source = {}

    for section in source_info.sections():
        #if section not in ['G333.46-0.16_alma1_hnco']:
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
        orig_nsigma = config.getfloat('pvnsigma', fallback=3.)
        plot_number = config.get('nplot', fallback=None)
        ncomponents = config.getint('ncomponents', fallback=1)

        if plot_number is not None:
            nsigma = max(5, orig_nsigma)
            results = []
            for nsig in range(3, int(nsigma)+1):
                print('Nsigma:', nsig)
                edges, errors, vsys = get_edge(fitsfile,
                                               rms,
                                               nsigma=nsig,
                                               quadrant=quadrant,
                                               xlim=xlim,
                                               ylim=ylim,
                                               ncomponents=ncomponents,
                                               save_edge=False)
                results.append(
                    fit_edge(fitsfile,
                             edges,
                             errors,
                             vsys,
                             distance,
                             rms,
                             name,
                             nsigma=nsig,
                             write_config=False,
                             plot_results=False)
                )
                print('-' * 80)
            write_source_results(name, results, orig_nsigma)
            results_per_source[name] = summarize(results)
        print('=' * 80)
    write_summary(results_per_source, RESULTS /
                  'overall/edge_identification_odr_nsigma_error.dat')
