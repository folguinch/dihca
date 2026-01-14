"""Functions to load DIHCA VI tables."""
from astropy.table import Table

from common_paths import RESULTS

SUMMARY = RESULTS / 'tables/dihca6_summary.csv'
MASS = 'dust_mass_corr'
RADIUS = 'disk_radius_dec' 

def get_masks(table):
    mask_G10 = table['Source'] == 'G10.62-0.38'
    mask_outliers = table['alpha'] >= 2
    mask_faceon = (((table['Source'] == 'G335.579-0.272') &
                    (table['ALMA'] == '1')) |
                   (table['Source'] == 'G35.20-0.74 N'))
    mask_mols = (
        (table['molec'] != 'CH3CN') &
        (table['molec'] != 'CH3OH')
    )
    mask_radius = (((table['Source'] == 'G333.23-0.06') &
                    (table['ALMAe'] == 17)) |
                   ((table['Source'] == 'G35.03+0.35 A') &
                    (table['ALMAe'] == 1)))
    return mask_G10, mask_outliers, mask_faceon, mask_mols, mask_radius

def get_masks_bycols(table):
    G10, outliers, faceon, mols, radius = get_masks(table)
    masks = {
        'alpha': outliers,
        'mass_cen': faceon | mols,
        'dust_mass': G10,
        'dust_mass_corr': G10,
        'disk_radius_dec': radius,
        'lum': G10,
        'wlum': G10,
        'toomre_Q': G10 | radius | faceon | mols,
    }

    return masks

def load_summary(masked=False, selected=None):
    table = Table.read(SUMMARY)

    if masked:
        table = Table(table, masked=True)
        masks = get_masks_bycols(table)
        for key, mask in masks.items():
            table[key].mask = mask

    if selected is not None:
        table = Table(table[selected], masked=masked)

    return table


