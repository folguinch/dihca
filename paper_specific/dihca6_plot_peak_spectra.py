from pathlib import Path
from configparser import ConfigParser
import json

from astropy.table import Table
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
from radio_beam import Beams

from common_paths import RESULTS, FIGURES, CONFIGS
from common_vars import SAVED_MOLS, NORM_SOURCES

config_dir = CONFIGS / 'extracted'
spectra = RESULTS / 'spectra'
summary = RESULTS / 'tables/dihca6_summary.csv'
summary = Table.read(summary)
sources = {'G10.62-0.38': [{'ALMA': '1a', 'molec': 'CH3CN'},
                           {'ALMA': '1c', 'molec': 'CH3CN'}],
           'G11.1-0.12': [{'ALMA': '1', 'molec': 'CH3CN'}], 
           'G11.92-0.61': [{'ALMA': '1a', 'molec': 'CH3CN'},
                           {'ALMA': '3', 'molec': 'CH3CN'}],
           'G29.96-0.02': [{'ALMA': '1', 'molec': 'CH3OH'}],
           'G333.12-0.56': [{'ALMA': '1', 'molec': 'CH3OH'}], 
           'G333.23-0.06': [{'ALMA': '3', 'molec': 'CH3CN'}, 
                            {'ALMA': '3b', 'molec': 'CH3CN'}],
           'G333.46-0.16': [{'ALMA': '1', 'molec': 'HNCO',
                             'qns': '10(0,10)-9(0,9)'},
                            {'ALMA': '7', 'molec': 'CH3CN'}],
           'G335.579-0.272': [{'ALMA': '1', 'molec': 'CH3OH'}, 
                              {'ALMA': '3', 'molec': 'CH3OH'}],
           'G335.78+0.17': [{'ALMA': '1', 'molec': 'CH3OH'}, 
                            {'ALMA': '2', 'molec': 'CH3OH'}], 
           'G336.01-0.82': [{'ALMA': '1', 'molec': 'CH3OH'}],
           'G34.43+0.24': [{'ALMA': '1', 'molec': 'CH3OH'}],
           'G35.03+0.35_A': [{'ALMA': '1', 'molec': 'CH3CN'}], 
           'G35.13-0.74': [{'ALMA': '1', 'molec': 'CH3CN'}, 
                           {'ALMA': '2', 'molec': 'CH3CN'}], 
           'G35.20-0.74_N': [{'ALMA': '1', 'molec': 'CH3OH'}],
           'G5.89-0.37': [{'ALMA': '14', 'molec': 'CH3CN'}],
           'IRAS_180891732': [{'ALMA': '1', 'molec': 'CH3CN'},
                              {'ALMA': '3', 'molec': 'CH3CN'}], 
           'IRAS_181622048': [{'ALMA': '1', 'molec': 'c-HCOOH'}], 
           'IRAS_18182-1433': [{'ALMA': '3', 'molec': 'CH3CN'}], 
           'NGC6334I': [{'ALMA': '1', 'molec': 'HNCO', 'qns':'10(3,8)-9(3,7)'}, 
                        {'ALMA': '4', 'molec': 'HNCO', 'qns':'10(3,8)-9(3,7)'}], 
           'NGC_6334_I_N': [{'ALMA': '1', 'molec': 'CH3OH'}, 
                            {'ALMA': '4', 'molec': 'CH3CN'}, 
                            {'ALMA': '6', 'molec': 'CH3CN'}], 
           'W33A': [{'ALMA': '1a', 'molec': 'CH3CN'}], 
           }

LINE_TRANSITIONS = {
    'CH3OH': '18(3,15)-17(4,14)A,vt=0',
    'CH3CN': '12(3)-11(3)',
    'c-HCOOH': '10(4,6)-9(4,5)',
    }

plt.style.use(['paper'])
nrow, ncol = 5, 7
#fig, axs = plt.subplots(8, 4, figsize=(20, 50))
fig, axs = plt.subplots(nrow, ncol, figsize=(25, 30))
row = 0
col = 0

for field, val in sources.items():
    for hmc in val:
        alma = hmc['ALMA']
        molec = hmc['molec']
        norm_field = NORM_SOURCES[field]
        qns = hmc.get('qns', LINE_TRANSITIONS.get(molec))
        print('Source:', field, f'ALMA{alma}')

        #config
        cfg = ConfigParser()
        cfg.read(config_dir / f'{field}_alma{alma}.cfg')
        vlsr = float(cfg['INFO']['vlsr'].split()[0])
        if field == 'G333.23-0.06' and alma == '3':
            mask = ((summary['Source'] == norm_field) & 
                    (summary['ALMA'] == '3a'))
        else:
            mask = ((summary['Source'] == norm_field) & 
                    (summary['ALMA'] == alma))
        if np.sum(mask) != 1:
            print('Problem with: ', field, f'ALMA{hmc}')
            raise KeyError
        ind = np.nanargmax(mask)
        vsys = summary['vsys'][ind]
        almae = summary['ALMAe'][ind]
        print('vlsr:', vlsr, 'km/s')
        print('vsys:', vsys, 'km/s')
        dvlsr = vsys - vlsr
        
        src_dir = spectra / f'spectra_{field}_alma{alma}'
        print('Source dir: ', src_dir)
        specs = list(src_dir.glob(f'spw*_from_{molec}*.dat'))
        if len(specs) == 0 and molec in ['c-HCOOH', 'HNCO']:
            specs = list(src_dir.glob(f'spw*_from_CH3CN*.dat'))
        spec = specs[0]

        # Open spectrum
        freq, flux, bmaj, bmin, bpa = np.loadtxt(specs[0],
                                                 usecols=(0, 2, 3, 4, 5),
                                                 unpack=True)
        freq = freq * u.GHz
        flux = flux * u.Jy
        beams = Beams(bmaj * u.arcsec, bmin * u.arcsec, bpa * u.deg)
        
        # Molecule info
        molec_info = json.loads(SAVED_MOLS[molec].read_text())
        for trans in molec_info['transitions']:
            if trans['qns'] == qns:
                restfreq = trans['restfreq'] * u.GHz
                break
        print('Rest frequency:', restfreq)
        freq_to_vel = u.doppler_radio(restfreq)
        vel = freq.to(u.km/u.s, equivalencies=freq_to_vel)
        temp_mb = flux.to(u.K, equivalencies=u.brightness_temperature(freq,
                                                                      beams))
        
        # plot
        ax = axs[row][col]
        print('Plotting:', row, col)
        ax.plot(vel.value, temp_mb.value, 'k', ds='steps-mid')
        #if col == 0 and row == 6:
        if col == 0 and row == 4:
            ax.set_ylabel('Brightness temperature (K)')
        #if col == 0 and row == 7:
        if col == 0 and row == 4:
            ax.set_xlabel('Velocity (km/s)')
        #if col%4 == 3:
        if col%ncol == ncol-1:
            row += 1
            col = 0
        else:
            col += 1
        ax.set_xlim(-25, 25)
        print(field, almae)
        if field == 'IRAS_181622048' and alma == '1':
            ax.set_ylim(top=25, bottom=-200)
            ax.annotate(molec, (.55, 0.1), xytext=(.55,.1), xycoords='axes fraction')
        elif field == 'NGC_6334_I_N' and almae == 2:
            print('aaaa')
            ax.set_ylim(bottom=-30)
            ax.annotate(molec, (.6, 0.9), xytext=(.6,.9), xycoords='axes fraction')
        else:
            ax.set_ylim(bottom=-5)
            ax.annotate(molec, (.6, 0.9), xytext=(.6,.9), xycoords='axes fraction')
        ax.axvline(x=dvlsr)
        ax.set_title(f'{norm_field} ALMAe{almae}', fontsize=13)

        print('-' * 80)

fig.delaxes(axs[4][-1])
fig.delaxes(axs[4][-2])
fig.delaxes(axs[4][-3])

fig.savefig(FIGURES / 'papers/dihca6_peak_spectra.png', bbox_inches='tight')
fig.savefig(FIGURES / 'papers/dihca6_peak_spectra.pdf', bbox_inches='tight')
