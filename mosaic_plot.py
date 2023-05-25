from astropy.io import fits
from astropy.wcs import WCS
from astropy.visualization import LogStretch
from astropy.visualization.mpl_normalize import ImageNormalize
import astropy.units as u
import matplotlib.pyplot as plt
import configparseradv.configparser as cfgparser
import numpy as np

from common_paths import *

# Filenames
configfile = configs / 'plots' / 'presentations' / 'mosaic.cfg'
figfile = figures / 'mosaic.eps'

# Configuration
config = cfgparser.ConfigParserAdv()
config.read(configfile)

# Figure
plt.style.use(['maps', 'inferno'])
fig, axs = plt.subplots(3, 10, figsize=(37, 10),
                        gridspec_kw={'wspace': 0.05,
                                     'hspace': 0.08})
radius = 1200 * u.au

# Plot each
for section, ax in zip(config.sections(), axs.ravel()):
    print(section)
    # Load image
    img = fits.open(config[section]['image'])[0]
    data = np.squeeze(img.data)
    wcs = WCS(img, naxis=2)

    # Source position
    position = config[section].getskycoord('position')
    distance = config[section].getquantity('distance')
    distance = distance.to(u.pc)
    r = radius.value / distance.value * u.arcsec

    # Recenter
    x, y = wcs.world_to_pixel(position)
    cdelt = np.sqrt(wcs.proj_plane_pixel_area())
    r = r.to(u.deg) / cdelt.to(u.deg)
    xmin, xmax = x-r.value, x+r.value
    ymin, ymax = y-r.value, y+r.value

    # Plot
    vmax = np.nanmax(data[int(ymin):int(ymax), int(xmin):int(xmax)])
    vmin = 60E-6
    a = 100
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LogStretch(a=a))
    ax.imshow(data, norm=norm)

    # Contours
    levels = np.geomspace(1, 256, num=9) * 5 * vmin
    ax.contour(data, levels=levels, colors='#7f7f7f', linewidths=0.5)

    # Configure axes
    title = config[section]['name']
    ax.set(aspect=1, xticks=[], yticks=[])
    ax.set_title(title, pad=-4, y=1.0, backgroundcolor='k',
                 fontdict={'fontsize': 10, 'color': 'w'})
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    #ax.set_axis_off()

fig.savefig(figfile, bbox_inches='tight')
