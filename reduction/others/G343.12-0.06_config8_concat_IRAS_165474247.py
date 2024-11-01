"""Concatenate config8 contsub data for imaging."""
from pathlib import Path

from astropy.coordinates import SkyCoord
from casatools import msmetadata
import casatasks as tasks

data = Path('./uvdata')
vis_g343 = data / 'G343.12-0.06.config8.selfcal.ms.contsub'
vis_i165 = data / 'IRAS_165474247.config8.selfcal.ms.contsub'
field = 'G343.12-0.06'

# Initial check
_ = tasks.listobs(f'{vis_g343}')
_ = tasks.listobs(f'{vis_i165}')

# Put the same field name
tasks.vishead(f'{vis_g343}', mode='put', hdkey='field', hdindex='0',
              hdvalue=field)
tasks.vishead(f'{vis_i165}', mode='put', hdkey='field', hdindex='0',
              hdvalue=field)

# Put the same source_name
for i in range(4):
    tasks.vishead(f'{vis_g343}', mode='put', hdkey='source_name',
                  hdindex=f'{i}', hdvalue=field)
    tasks.vishead(f'{vis_i165}', mode='put', hdkey='source_name',
                  hdindex=f'{i}', hdvalue=field)

# Check
_ = tasks.listobs(f'{vis_g343}')
_ = tasks.listobs(f'{vis_i165}')

# Get phasecenter
metadata = msmetadata()
metadata.open(f'{vis_g343}')
phasecenter = metadata.phasecenter()
print(phasecenter)
metadata.close()
phasecenter_coord = SkyCoord(phasecenter['m0']['value'],
                             phasecenter['m1']['value'],
                             unit=(phasecenter['m0']['unit'],
                                   phasecenter['m1']['unit']),
                             frame=phasecenter['refer'].lower())
new_phasecenter = phasecenter_coord.to_string('hmsdms')
print(new_phasecenter)

# Fill by hand with rounded values
new_phasecenter = 'ICRS 16h58m17.164800 -42d52m07.55200'
outputvis = vis_i165.with_suffix('.fixvis.ms')
tasks.fixvis(vis=f'{vis_i165}', outputvis=f'{outputvis}',
             phasecenter=new_phasecenter)

# Check phase center
_ = tasks.listobs(f'{vis_g343}')
_ = tasks.listobs(f'{outputvis}')

# Concatenate
concatvis = data / f'{field}.config8.selfcal.contsub.concat.ms'
tasks.concat(vis=[f'{vis_g343}', f'{outputvis}'], concatvis=f'{concatvis}')
_ = tasks.listobs(f'{concatvis}')

# Merge spws
vis_spw0 = concatvis.with_suffix('.spw0.ms')
vis_spw1 = concatvis.with_suffix('.spw1.ms')
vis_spw2 = concatvis.with_suffix('.spw2.ms')
vis_spw3 = concatvis.with_suffix('.spw3.ms')
tasks.cvel2(vis=f'{concatvis}', outputvis=f'{vis_spw0}', spw='0,4',
            mode='frequency', field=field, start='233553.303MHz',
            width='488.281kHz')
_ = tasks.listobs(f'{vis_spw0}')
# Number of channels: 3840
tasks.cvel2(vis=f'{concatvis}', outputvis=f'{vis_spw1}', spw='1,5',
            mode='frequency', field=field, start='231053.404MHz',
            width='488.281kHz')
# Number of channels: 3840
tasks.cvel2(vis=f'{concatvis}', outputvis=f'{vis_spw2}', spw='2,6',
            mode='frequency', field=field, start='218728.216MHz',
            width='-488.281kHz')
# Number of channels: 3840
tasks.cvel2(vis=f'{concatvis}', outputvis=f'{vis_spw3}', spw='3,7',
            mode='frequency', field=field, start='220928.125MHz',
            width='-488.281kHz')
# Number of channels: 3840

# Concat into 1 ms
concatvis = data / f'{field}.config8.selfcal.contsub.concat.cvel.ms'
tasks.concat(vis=[f'{vis_spw0}', f'{vis_spw1}', f'{vis_spw2}', f'{vis_spw3}'],
             concatvis=f'{concatvis}')
_ = tasks.listobs(f'{concatvis}')
