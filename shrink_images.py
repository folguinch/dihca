"""Script for trimming the images to a common size."""
from typing import Sequence, Optional
from datetime import datetime
from pathlib import Path
import argparse
import os
import sys

from astropy.io import fits
from astropy.wcs import WCS
from casatasks import exportfits, imsubimage
from goco_helpers import argparse_parents as parents
import astropy.units as u
import numpy as np

def shrink_cubes(args: Optional[Sequence] = None) -> None:
    """Shrink cubes from command line inputs.

    Args:
      args: command line args.
    """
    # Command line options
    logfile = datetime.now().isoformat(timespec='milliseconds')
    logfile = f'debug_joincubes_{logfile}.log'
    args_parents = [parents.logger(logfile)]
    parser = argparse.ArgumentParser(
        description='Crop cubes produced by yclean',
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=args_parents,
        conflict_handler='resolve',
    )
    parser.add_argument('--clean', action='store_true',
                        help='Delete originals')
    parser.add_argument('--radius', nargs=1, default=[19],
                        help='Radius of the circumference in arcsec')
    parser.add_argument('--outdir', nargs=1, default='./',
                        help='Output directory')
    parser.add_argument('images', nargs='*', type=str,
                        help='Images to crop')
    parser.set_defaults(finalcube=None)

    # Check args
    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args(args)

    # Iterate over cubes
    outdir = Path(args.outdir[0])
    box = None
    for i, image in enumerate(map(Path, args.images)):
        # Check first is FITS
        if i == 0 and image.suffix != '.fits':
            raise ValueError('First value must be a FITS file')
        
        # Create box
        if box is None:
            # Data properties
            img = fits.open(image)[0]
            shape = img.data.shape[-2:]
            wcs = WCS(img, naxis=2)
            pixsize = np.sqrt(wcs.proj_plane_pixel_area()).to(u.arcsec)
            diam_pix = (2 * args.radius[0] * u.arcsec) / pixsize
            diam_pix = int(diam_pix.to(1).value)
            args.log.info('Spatial shape: %s', shape)
            args.log.info('Pixel size: %f %s', pixsize.value, pixsize.unit)
            args.log.info('Selected region size: %i', diam_pix)

            # Difference
            xdiff = shape[1] - diam_pix
            ydiff = shape[0] - diam_pix
            if xdiff % 2 != 0:
                xdiff += 1
            if ydiff % 2 != 0:
                ydiff += 1
            xdiff = xdiff // 2
            ydiff = ydiff // 2
            args.log.info('Margin to remove: %i %i', xdiff, ydiff)
            xdiff -= 1
            ydiff -= 1

            # Box
            box = f'{xdiff},{ydiff},{xdiff+diam_pix},{xdiff+diam_pix}'

        # Crop
        outimg = outdir / 'temp.image'
        args.log.info('Cropping image: %s', box)
        imsubimage(imagename=f'{image}', outfile=f'{outimg}', box=box)
        
        # Export fits?
        if image.suffix == '.fits':
            exportfits(imagename=f'{outimg}',
                       fitsimage=f'{outdir / image.name}',
                       overwrite=True)
            os.system(f'rm -rf {outimg}')
        else:
            os.system(f'mv {outimg} {outdir / image.name}')

        if args.clean:
            os.system(f'rm -rf {image}')

if __name__ == '__main__':
    shrink_cubes(sys.argv[1:])

