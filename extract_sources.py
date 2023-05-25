#!/bin/python3
"""Generate a list of the main sources.

The list contains the directory and position of the main peak (from pbclean
directory) of the sources.
"""
from pathlib import Path

from astropy.io import fits
from astropy.wcs.utils import pixel_to_skycoord
from astropy.wcs import WCS
import astropy.units as u
import numpy as np

if __name__ == '__main__':
    # Globals
    sbs = ['G333_G335', 'IRAS_18089', 'G14.22', 'G24.6', 'G336.01',
           'G343_G351', 'G34.43', 'G35', 'IRAS_18182', 'NGC_6334']
    homes = [Path('/home/myso/share/binary_project'),
             Path('/data/share/binary_project')]
    catalogue = homes[1] / 'catalogue/sources_config8.dat'

    # Iterate over directories
    lines = []
    for home in homes:
        for content in home.iterdir():
            if not content.is_dir() or content.name not in sbs:
                continue
            for source in content.iterdir():
                # Check pbclean directory
                pbclean = source / 'pbclean'
                if not source.is_dir() or not pbclean.is_dir():
                    continue
                print(f'Source: {source.name}')

                # Get pbclean image
                pbimgs = list(pbclean.glob(f'*config8*cont_avg*.fits'))
                if len(pbimgs) != 1:
                    print(f'Skipping {list(pbimgs)}')
                else:
                    pbimg = pbimgs[0]
                img = fits.open(pbimg)[0]

                # WCS
                wcs = WCS(img, naxis=['latitude', 'longitude'])

                # Get peak
                data = np.squeeze(img.data)
                ypeak, xpeak = np.unravel_index(np.nanargmax(data), data.shape)
                coord = pixel_to_skycoord(xpeak, ypeak, wcs)
                print(f'Position: {coord}')

                # Store in list
                lines.append((f'{source}\t{coord.ra.to_string(u.hour)}\t'
                              f'{coord.dec.to_string(u.deg, alwayssign=True)}'))

    # Write positions
    catalogue.write_text('\n'.join(lines))
