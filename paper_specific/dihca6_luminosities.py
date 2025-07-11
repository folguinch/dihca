"""Determine proportional luminosities"""
from astropy.table import Table, join
import numpy as np

from common_paths import RESULTS

lum_table = Table.read(RESULTS / 'tables/dihca_luminosities.dat',
                       format='ascii')
catalogue = Table.read(RESULTS / 'tables/dihca_c5_catalogue_std.csv',
                       format='ascii')

print(lum_table['Clump'])
print(catalogue['Clump'])

joint = join(catalogue, lum_table, join_type='left', keys='Clump')
cat_by_clump = joint.group_by('Clump')
total_flux = cat_by_clump.groups.aggregate(np.sum)
total_flux = Table([total_flux['Clump'], total_flux['IFlux']])
total_flux.rename_column('IFlux', 'FieldFlux')
joint = join(joint, total_flux, join_type='left', keys='Clump')
joint.add_column(joint['IFlux'] * joint['luminosity'] / joint['FieldFlux'],
                 name='ClumpLum')
joint.write(RESULTS / 'tables/dihca_c5_catalogue_with_lum.csv',
            format='ascii.csv', overwrite=True)
