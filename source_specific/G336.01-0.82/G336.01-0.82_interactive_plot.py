"""Interactive figure of G336 with models.

Part of the code is based on:
    - The X3D Pathway: https://fpavogt.github.io/x3d-pathway/index.html
    - `tdviz`: https://github.com/xinglunju/tdviz
"""
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.table import QTable
from mayavi import mlab
from spectral_cube import SpectralCube
import astropy.units as u
import numpy as np
import scipy.interpolate as interp

# Constants
cube_file = 'CH3OH_18_3_15_-17_4_14_A_vt_0_nchans60_masked_shrink.fits'
rms = 2.6 * u.mJy
vlsr = -47.2 * u.km/u.s
isolevels = np.array([5, 7.5, 10, 12.5, 15]) * rms
color_scale = np.array([1, 20]) * rms
zstretch = 2
coord_alma1 = SkyCoord('16h35m09.26085s -48d46m47.65854s', frame='icrs')
# Triggers for static pictures
plot_rotation = True
plot_streamers = True
save_x3d = False
show_fig = True

# Model cube
model_file = ('G336-Vsys-47.2_LineCH3OH_Pix0.004as0.1kmps_D3100M10CB200.I65.'
              'PA125Rot1Rout800.Rin200._IRE-T0.Flare30Nprof-1.5Tprof-0.4_'
              'Kep-T0.5Flare30Nprof-1.5Tprof-0.4_LW1.0_'
              'Beam0.0692x0.0517PA-29.07.fits')

# Streamers
stream_north = QTable.read(('stream_north_rmin400_r02500_rc400_'
                            'theta080_phi060_vr00.ecsv'))
stream_south = QTable.read(('stream_south_rmin400_r02500_rc400_'
                            'theta080_phi0280_vr02.ecsv'))
vel_north = stream_north['vlsr']
vel_south = stream_south['vlsr']
stream_north = SkyCoord(stream_north['ra'], stream_north['dec'], frame='icrs')
stream_south = SkyCoord(stream_south['ra'], stream_south['dec'], frame='icrs')

# Load files
# Observed
cube = fits.open(cube_file)[0]
header = cube.header
bunit = u.Unit(cube.header['BUNIT']) * u.beam
data = np.squeeze(cube.data)
data[np.isnan(data)] = 0.0
data = data * bunit
data = data.to(u.mJy)
bunit = u.mJy
# Model
model = fits.open(model_file)[0]
model_data = np.squeeze(model.data) * u.Unit(model.header['BUNIT']) * u.beam
model_data[np.isnan(model_data)] = 0.0
model_data = model_data.to(bunit)

# Extremes in pixel units
nv, ny, nx = data.shape
datamax = np.max(data)
datamin = np.min(data)
xstart = 0
xend = nx - 1
ystart = 0
yend = ny - 1
zstart = 12
zend = 46

# Data to plot
region = data[zstart:zend, ystart:yend, xstart:xend]
vol = region.shape

# Stretch v axis
sregion = np.empty((vol[0]*zstretch, vol[1], vol[2]))
chanindex = np.linspace(0, vol[0]-1, vol[0])
chanindex2 = np.linspace(0, vol[0]-1, vol[0]*zstretch)
for j in range(0, vol[1]-1):
    for k in range(0, vol[2]-1):
        spec = region[:,j,k].value
        tck = interp.splrep(chanindex, spec, k=1)
        sregion[:,j,k] = interp.splev(chanindex2, tck)
sregion = np.swapaxes(sregion, 0, 2)[::-1,:,::-1]

# Velocity
spcube = SpectralCube.read(cube_file)
vel = spcube.spectral_axis.to(u.km/u.s) - vlsr
wcs = spcube.wcs

# Extremes in physical units
coord_ll = SkyCoord.from_pixel(xstart, ystart, wcs)
coord_ur = SkyCoord.from_pixel(xend, yend, wcs)
ra_start = coord_ll.ra
ra_end = coord_ur.ra
dec_start = coord_ll.dec
dec_end = coord_ur.dec
vel_start = vel[zstart]
vel_end = vel[zend]

# Convert to offsets
ramax_off, decmin_off = coord_alma1.spherical_offsets_to(coord_ll)
ramin_off, decmax_off = coord_alma1.spherical_offsets_to(coord_ur)
ramin_off = ramin_off.to(u.arcsec).value
ramax_off = ramax_off.to(u.arcsec).value
decmin_off = decmin_off.to(u.arcsec).value
decmax_off = decmax_off.to(u.arcsec).value
vel_start = vel_start.to(u.km/u.s).value
vel_end = vel_end.to(u.km/u.s).value

# Stream offset
stream_north_ra, stream_north_dec = coord_alma1.spherical_offsets_to(
    stream_north
)
stream_north_ra = stream_north_ra.to(u.arcsec).value
stream_north_dec = stream_north_dec.to(u.arcsec).value
stream_south_ra, stream_south_dec = coord_alma1.spherical_offsets_to(
    stream_south
)
stream_south_ra = stream_south_ra.to(u.arcsec).value
stream_south_dec = stream_south_dec.to(u.arcsec).value

# Data ranges
ranges = [ramin_off,
          ramax_off,
          decmin_off,
          decmax_off,
          vel_start,
          vel_end]
nx, ny, nz = sregion.shape
pix_extent = [0, nx-1, 0, ny-1, 0, nz-1]

# Map pixel with physical coordinates
xpix = np.arange(nx)
ypix = np.arange(ny)
zpix = np.arange(nz)
xphy = np.linspace(ramin_off, ramax_off, num=nx, endpoint=True)
yphy = np.linspace(decmin_off, decmax_off, num=ny, endpoint=True)
zphy = np.linspace(vel_end, vel_start, num=nz, endpoint=True)
xfn = interp.interp1d(xphy, xpix, bounds_error=False, fill_value='extrapolate')
yfn = interp.interp1d(yphy, ypix, bounds_error=False, fill_value='extrapolate')
zfn = interp.interp1d(zphy, zpix, bounds_error=False, fill_value='extrapolate')

# Plot contours
cm_tweak = 1.0
mlab.figure(bgcolor=(1,1,1))
mlab.contour3d(sregion * cm_tweak, #data_slc.value * cm_tweak,
               contours=list(isolevels.to(bunit).value * cm_tweak),
               opacity=0.2,
               vmin=color_scale[0].value * cm_tweak,
               vmax=color_scale[1].value * cm_tweak,
               name='levels',
               #extent=extent,
               colormap='cool')
               #colormap='Spectral')

# Plot FERIA rotation model
if plot_rotation:
    # Evaluate model in grid and plot
    model_data = np.swapaxes(model_data.value, 0, 2)
    model_data = model_data * datamax.value / np.nanmax(model_data)
    model_nx, model_ny, model_nz = model_data.shape
    model_xpix = np.arange(model_nx)
    model_ypix = np.arange(model_ny)
    model_zpix = np.arange(model_nz)
    model_xphy = ((model_xpix + 1 - model.header['CRPIX1']) *
                  model.header['CDELT1'] * u.deg)
    model_yphy = ((model_ypix + 1 - model.header['CRPIX2']) *
                  model.header['CDELT2'] * u.deg)
    model_zphy = ((model_zpix + 1 - model.header['CRPIX3']) *
                  model.header['CDELT3'] * u.m/u.s)
    model_fn = interp.RegularGridInterpolator((model_xphy.to(u.arcsec).value,
                                               model_yphy.to(u.arcsec),
                                               model_zphy.to(u.km/u.s)),
                                              model_data,
                                              method='linear',
                                              bounds_error=False,
                                              fill_value=0.0)
    model_xnew, model_ynew, model_znew = np.meshgrid(xphy, yphy, zphy,
                                                     indexing='ij')
    model_interp = model_fn((model_xnew, model_ynew, model_znew))

    mlab.contour3d(model_interp * cm_tweak,
                contours=list(isolevels.to(bunit).value * cm_tweak),
                opacity=0.2,
                vmin=color_scale[0].value * cm_tweak,
                vmax=color_scale[1].value * cm_tweak,
                name='levels_model',
                colormap='inferno')

# Box
mlab.outline(color=(0,0,0), line_width = 2.0, extent=pix_extent)
ax = mlab.axes(color=(0,0,0), nb_labels=3, ranges=ranges)
ax.scene.parallel_projection = True
ax.visible = False

# ALMA1
mlab.points3d([xfn(0)], [yfn(0)], [zfn(0)], 5, color=(1,1,0.5), scale_factor=1)

# Streamers
if plot_streamers:
    mlab.plot3d(xfn(stream_north_ra), yfn(stream_north_dec), zfn(vel_north),
                color=(0,0,1), tube_radius=1.5, representation='wireframe')
    mlab.plot3d(xfn(stream_south_ra), yfn(stream_south_dec), zfn(vel_south),
                color=(1,0,0), tube_radius=1.5, representation='wireframe')

# Axes text
pad_label = -6
mlab.text3d(nx/2+13 , pad_label, 0, 'R.A. offset (arcsec)',
            orient_to_camera=False, color=(0,0,0), scale=2,
            orientation=(0,180,0))
mlab.text3d(nx/2-13 , ny-1, pad_label-3, 'R.A. offset (arcsec)',
            orient_to_camera=False, color=(0,0,0), scale=2,
            orientation=(270,180,180))
mlab.text3d(nx+1-pad_label , ny/2-15, 0, 'Decl. offset (arcsec)',
            orient_to_camera=False, color=(0,0,0), scale=2,
            orientation=(180,0,90))
mlab.text3d(0 , ny/2-15, pad_label-3, 'Decl. offset (arcsec)',
            orient_to_camera=False, color=(0,0,0), scale=2,
            orientation=(270,90,180))
mlab.text3d(0 , pad_label, nz/2-15, 'Velocity (km/s)',
            orient_to_camera=False, color=(0,0,0), scale=2,
            orientation=(180,90,180))
mlab.text3d(pad_label , ny-1, nz/2-15, 'Velocity (km/s)',
            orient_to_camera=False, color=(0,0,0), scale=2,
            orientation=(0,270,270))

# Ticks
xticks = np.array([0.5, 0.4, 0.3, 0.2, 0.1, 0, -0.1, -0.2])
for tick in xticks:
    xval = xfn(tick)
    mlab.plot3d([xval, xval], [0, -1], [0, 0], color=(0,0,0), tube_radius=0.1)
    mlab.plot3d([xval, xval], [ny-1, ny-1], [0, -1], color=(0,0,0),
                tube_radius=0.1)
    if tick == 0:
        mlab.plot3d([xval, xval], [0, ny-1], [0, 0], color=(0,1,0),
                    tube_radius=0.1)
        mlab.plot3d([xval, xval], [ny-1, ny-1], [0, nz-1], color=(0,1,0),
                    tube_radius=0.1)
    mlab.text3d(xval+2, -3, 0, f'{tick:.1f}',
                orient_to_camera=False,
                color=(0,0,0), scale=1.5, orientation=(0,180,0))
    mlab.text3d(xval-1, ny-1, -6, f'{tick:.1f}',
                orient_to_camera=False,
                color=(0,0,0), scale=1.5, orientation=(0,270,270))
yticks = np.array([-0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2])
for tick in yticks:
    yval = yfn(tick)
    mlab.plot3d([nx-1, nx], [yval, yval], [0, 0], color=(0,0,0),
                tube_radius=0.1)
    mlab.plot3d([0, 0], [yval, yval], [0, -1], color=(0,0,0), tube_radius=0.1)
    if tick == 0:
        mlab.plot3d([0, nx-1], [yval, yval], [0, 0], color=(0,1,0),
                    tube_radius=0.1)
        mlab.plot3d([0, 0], [yval, yval], [0, nz-1], color=(0,1,0),
                    tube_radius=0.1)
    mlab.text3d(nx+5, yval-1, 0, f'{tick:.1f}', orient_to_camera=False,
                color=(0,0,0), scale=1.5, orientation=(0,180,0))
    mlab.text3d(0, yval-1, -6, f'{tick:.1f}', orient_to_camera=False,
                color=(0,0,0), scale=1.5, orientation=(180,90,180))
zticks = np.array([-8, -6, -4, -2, 0, 2, 4, 6, 8, 10])
for tick in zticks:
    zval = zfn(tick)
    mlab.plot3d([0, 0], [0, -1], [zval, zval], color=(0,0,0), tube_radius=0.1)
    mlab.plot3d([0, -1], [ny-1, ny-1], [zval, zval], color=(0,0,0),
                tube_radius=0.1)
    if tick == 0:
        mlab.plot3d([0, 0], [0, ny-1], [zval, zval], color=(0,1,0),
                    tube_radius=0.1)
        mlab.plot3d([0, nx-1], [ny-1, ny-1], [zval, zval], color=(0,1,0),
                    tube_radius=0.1)
    mlab.text3d(0, -3, zval-2, f'{tick:.1f}', orient_to_camera=False,
                color=(0,0,0), scale=1.5, orientation=(180,90,180))
    mlab.text3d(-3, ny-1, zval-2, f'{tick:.1f}', orient_to_camera=False,
                color=(0,0,0), scale=1.5, orientation=(0,270,270))

# Set the view from the oposite side
mlab.view(0, 180, 70)

# Save figure
if save_x3d:
    mlab.savefig('interactive_figure.x3d')
if plot_streamers and not plot_rotation:
    mlab.savefig('interactive_figure_streamers.png')
if plot_rotation and not plot_streamers:
    mlab.savefig('interactive_figure_rotation.png')
if show_fig:
    mlab.show()
