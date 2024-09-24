from pathlib import Path

import astropy.units as u
import astropy.constants as ct
import numpy as np
import velocity_tools.stream_lines as SL
from astropy.coordinates import SkyCoord

# Constants
outdir = Path(('/data/share/binary_project/results/G336.01-0.82/paper_2023/c8/'
               'CH3OH/streamer_models_incl65_cb200/'))
mstar = 10 * u.Msun
rmin = rc = 400 * u.au

# Blue streamer
r0 = 2500 * u.au
theta = 80 * u.deg
phi = 60 * u.deg
vr0 = 0 * u.km / u.s

# Omega
omega0 = np.sqrt(rc * ct.G * mstar) / r0**2
omega0 = omega0.to(1 / u.s)

# Coords
name = 'north'
fname = 'rmin400_r02500_rc400_theta080_phi060_vr00'
tab_name = outdir / 'regions' / f'stream_positions_{name}_{fname}.ecsv'
(x, y, z), *_ = SL.xyz_stream(mass=mstar, r0=r0, theta0=theta,
                              phi0=phi, omega=omega0, v_r0=vr0,
                              inc=0*u.deg, pa=0*u.deg, rmin=rmin)
fil = SkyCoord(x, y, z, representation_type='cartesian')
fil_table = fil.to_table()
fil_table.write(tab_name, overwrite=True)

# Red streamer
r0 = 2500 * u.au
theta = 80 * u.deg
phi = 280 * u.deg
vr0 = 2 * u.km / u.s

# Omega
omega0 = np.sqrt(rc * ct.G * mstar) / r0**2
omega0 = omega0.to(1 / u.s)

# Coords
name = 'south'
fname = 'rmin400_r02500_rc400_theta080_phi0280_vr02'
tab_name = outdir / 'regions' / f'stream_positions_{name}_{fname}.ecsv'
(x, y, z), *_ = SL.xyz_stream(mass=mstar, r0=r0, theta0=theta,
                              phi0=phi, omega=omega0, v_r0=vr0,
                              inc=0*u.deg, pa=0*u.deg, rmin=rmin)
fil = SkyCoord(x, y, z, representation_type='cartesian')
fil_table = fil.to_table()
fil_table.write(tab_name, overwrite=True)
