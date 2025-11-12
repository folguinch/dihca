"""Find the sources with temperatures in DIHCA V."""
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np

# NGC 6334I
coords = ['17:20:53.461 -35:46:57.23', '17:20:53.472 -35:46:57.59',
          '17:20:53.379 -35:46:57.18', '17:20:53.405 -35:46:59.34',
          '17:20:53.198 -35:46:59.48']
coords = SkyCoord(coords, frame='icrs', unit=(u.hourangle, u.deg))

# NGC 6334I ALMAe1
target = SkyCoord('17:20:53.41869 -35:46:57.8969', frame='icrs',
                  unit=(u.hourangle, u.deg))
dist = coords.separation(target).to(u.arcsec)
ind = np.nanargmin(dist)
print(f'NGC 6334I ALMAe1: P{ind+1} ({dist})')

# NGC 6334I ALMAe4
target = SkyCoord('17:20:53.16652 -35:46:59.1704', frame='icrs',
                  unit=(u.hourangle, u.deg))
dist = coords.separation(target).to(u.arcsec)
ind = np.nanargmin(dist)
print(f'NGC 6334I ALMAe4: P{ind+1} ({dist})')

# NGC 6334I(N)
coords = ['17:20:55.182 -35:45:3.94', '17:20:54.868 -35:45:6.46',
          '17:20:54.624 -35:45:8.67', '17:20:54.595 -35:45:17.31']
coords = SkyCoord(coords, frame='icrs', unit=(u.hourangle, u.deg))

# NGC 6334I(N) ALMAe5
target = SkyCoord('17:20:54.87122 -35:45:06.4309', frame='icrs',
                  unit=(u.hourangle, u.deg))
dist = coords.separation(target).to(u.arcsec)
ind = np.nanargmin(dist)
print(f'NGC 6334I(N) ALMAe5: P{ind+1} ({dist})')
