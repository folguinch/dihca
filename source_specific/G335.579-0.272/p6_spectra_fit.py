from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sourcedir = Path('/home/myso/share/binary_project/G333_G335/G335.579-0.272')
results = sourcedir / 'results_final/concat/CH3OH/spectra'
figures = sourcedir / 'figures/P6/ch3oh_spectra_fit.png'
positions = {'1a': (1797,1808),
             '1b': (1797,1814),
             'bow': (1805,1796)}
xy = (0.05, 0.95)
xy_res1 = (-0.2, 1.01)
xy_res2 = (0.6, 1.01)

def get_results(file_name):
    results = file_name.read_text()
    results = results.split('\n')

    # Column density
    nmol = results[11].split()
    nmol_std = float(nmol[-1])
    nmol = float(nmol[-3])
    nmol_exp = int(np.floor(np.log10(nmol)))
    nmol = nmol / 10**nmol_exp
    nmol_std = nmol_std / 10**nmol_exp
    label1 = '$N = '
    label1 += r'{0:.1f}\pm{1:.1f}\times 10^{{{2:d}}}$'.format(nmol, nmol_std,
                                                              nmol_exp)
    label1 += ' cm$^{-2}$'

    # Temperature
    tex = results[12].split()
    tex_std = float(tex[-1])
    tex = float(tex[-3])
    label2 = r'$T_{\rm ex} = ' 
    label2 += f'{tex:.0f}\pm{tex_std:.0f}$ K'

    return label1, label2

# Figure
fig, axs = plt.subplots(3, 1, figsize=(3,13), sharex=True)
fig.subplots_adjust(hspace=0.08)

i = 0
for (label, position), ax in zip(positions.items(), axs):
    data = results / 'spec_x{0}_y{1}.dat'.format(*position)
    model = results / 'lte_fit' / 'spec_x{0}_y{1}.lis'.format(*position)
    
    # Load files
    dfreq, dtemp = np.loadtxt(data, comments='/', skiprows=3, usecols=(0, 4),
                              unpack=True)
    mfreq, mtemp = np.loadtxt(model, comments='/', skiprows=3, usecols=(0, 4),
                              unpack=True)

    # Plot
    ind = np.argsort(mfreq)
    ax.plot(dfreq/1000, dtemp, 'k-')
    ax.plot(mfreq[ind]/1000, mtemp[ind], 'b-')
    ax.annotate('({0}) {1}'.format(chr(ord('a')+i), label), xy=xy, xytext=xy,
                xycoords='axes fraction')
    i += 1

    # Annotate results
    label_res = get_results(model.with_suffix('.txt'))
    ax.annotate(label_res[0], xy=xy_res1, xytext=xy_res1,
                xycoords='axes fraction', color='b')
    ax.annotate(label_res[1], xy=xy_res2, xytext=xy_res2,
                xycoords='axes fraction', color='b')
    
    # Common configuration
    ax.axvline(219.983675, ls='--', c='#6e6e6e')
    ax.axvline(219.993658, ls='--', c='#6e6e6e')
    ax.set_xlim(219.96, 220.02)

ax.set_ylabel('Brightness temperature (K)')
ax.set_xlabel('Rest Frequency (GHz)')
ax.set_xticks([219.96, 219.98, 220.00, 220.02], minor=False)
ax.set_xticklabels(['219.96', '219.98', '220.00', '220.02'])
ax.annotate('$25_3-24_4$', xy=(219.983675,-52), xytext=(219.983675,-52),
            xycoords='data', rotation='vertical')
ax.annotate('$23_5-22_6$', xy=(219.993658,-52), xytext=(219.993658,-52),
            xycoords='data', rotation='vertical')

fig.savefig(figures, bbox_inches='tight')
fig.savefig(figures.with_suffix('.pdf'), bbox_inches='tight')

