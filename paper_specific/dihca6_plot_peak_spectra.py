from pathlib import Path
import json

import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
from radio_beam import Beams

from common_paths import RESULTS, FIGURES

spectra = RESULTS / 'spectra'
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

# Saved molecules
MOL_DIR = Path('../molecules')
SAVED_MOLS = {
    'CH3OH': MOL_DIR / 'ch3oh.json',
    'CH3CN': MOL_DIR / 'ch3cn.json',
    '(13)CH3OH': MOL_DIR / '13ch3oh.json',
    '(13)CH3CN': MOL_DIR / '13ch3cn.json',
    'c-HCOOH': MOL_DIR / 'c-hcooh.json',
    'HNCO': MOL_DIR / 'hnco.json',
    'CH2(OD)CHO': MOL_DIR / 'glycolaldehyde.json',
}


plt.style.use(['paper'])
fig, axs = plt.subplots(8, 4, figsize=(20, 50))
row = 0
col = 0

for field, val in sources.items():
    for hmc in val:
        alma = hmc['ALMA']
        molec = hmc['molec']
        qns = hmc.get('qns', LINE_TRANSITIONS.get(molec))
        print('Source:', field, f'ALMA{alma}')
        
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
        if col == 0 and row == 6:
            ax.set_ylabel('Brightness temperature (K)')
        if col == 0 and row == 7:
            ax.set_xlabel('Velocity (km/s)')
        if col%4 == 3:
            row += 1
            col = 0
        else:
            col += 1
        ax.set_xlim(-20, 20)
        ax.set_ylim(bottom=-2)

        print('-' * 80)

fig.savefig(FIGURES / 'papers/dihca6_peak_spectra.png', bbox_inches='tight')
fig.savefig(FIGURES / 'papers/dihca6_peak_spectra.pdf', bbox_inches='tight')
