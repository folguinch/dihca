"""Find if a coordinate is in image."""
from pathlib import Path
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np

sources = {
    #'G10.62-0.38': [
    #    SkyCoord('18h10m28.61s', '-19d55m49.487s', frame='icrs'),
    #    SkyCoord('18h10m28.709s', '-19d55m50.099s', frame='icrs')
    #],
    #'G11.1-0.12': [
    #    SkyCoord('18h10m28.24854s', '-19d22m30.3222s', frame='icrs')
    #],
    #'G11.92-0.61': [
    #    SkyCoord('18h13m58.11097s', '-18d54m20.2010s', frame='icrs'),
    #    SkyCoord('18h13m58.12719s', '-18d54m20.7199s', frame='icrs'),
    #    SkyCoord('18h13m58.13491s', '-18d54m16.2731s', frame='icrs')
    #],
    #'G14.22-0.50_S': [
    #    SkyCoord('18h18m13.34872s', '-16d57m23.9282s', frame='icrs'),
    #    SkyCoord('18h18m12.86253s', '-16d57m20.3683s', frame='icrs')
    #],
    #'G24.60+0.08': [
    #    SkyCoord('18h35m40.12384s', '-07d18m35.3018s', frame='icrs'),
    #    SkyCoord('18h35m40.12731s', '-07d18m35.0339s', frame='icrs')
    #],
    #'G29.96-0.02': [
    #    SkyCoord('18h46m03.77860s', '-02d39m22.3746s', frame='icrs')
    #],
    #'G333.12-0.56': [
    #    SkyCoord('16h21m35.37589s', '-50d40m56.6044s', frame='icrs'),
    #    SkyCoord('16h21m36.25475s', '-50d40m47.2340s', frame='icrs')
    #],
    #'G333.23-0.06': [
    #    SkyCoord('16h19m50.88363s', '-50d15m10.5272s', frame='icrs'),
    #    SkyCoord('16h19m51.27585s', '-50d15m14.5305s', frame='icrs')
    #],
    #'G333.46-0.16': [
    #    SkyCoord('16h21m20.20863s', '-50d09m46.8522s', frame='icrs'),
    #    SkyCoord('16h21m20.18163s', '-50d09m46.4200s', frame='icrs'),
    #    SkyCoord('16h21m20.17290s', '-50d09m48.8762s', frame='icrs')
    #],
    #'G335.579-0.272': [
    #    SkyCoord('16h30m58.76705s', '-48d43m53.8816s', frame='icrs'),
    #    SkyCoord('16h30m58.63085s', '-48d43m51.2159s', frame='icrs')
    #],
    #'G335.78+0.17': [
    #    SkyCoord('16h29m47.33461s', '-48d15m52.2666s', frame='icrs'),
    #    SkyCoord('16h29m46.12974s', '-48d15m49.9512s', frame='icrs')
    #],
    #'G336.01-0.82': [
    #    SkyCoord('16h35m09.34751s', '-48d46m47.8950s', frame='icrs')
    #],
    #'G34.43+0.24': [
    #    SkyCoord('18h53m18.00684s', '+01d25m25.4228s', frame='icrs')
    #],
    #'G34.43+0.24MM2': [
    #    SkyCoord('18h53m18.55026s', '+01d24m45.1362s', frame='icrs')
    #],
    #'G343.12-0.06': [
    #    SkyCoord('16h58m17.20735s', '-42d52m07.4161s', frame='icrs')
    #],
    #'G35.03+0.35_A': [
    #    SkyCoord('18h54m00.65099s', '+02d01m19.3410s', frame='icrs')
    #],
    #'G35.13-0.74': [
    #    SkyCoord('18h58m06.13626s', '+01d37m07.4306s', frame='icrs'),
    #    SkyCoord('18h58m06.16874s', '+01d37m08.1602s', frame='icrs'),
    #    SkyCoord('18h58m06.27972s', '+01d37m07.2029s', frame='icrs')
    #],
    #'G35.20-0.74_N': [
    #    SkyCoord('18h58m12.95261s', '+01d40m37.3652s', frame='icrs'),
    #    SkyCoord('18h58m13.025s', '+01d40m35.92s', frame='icrs')
    #],
    #'G351.77-0.54': [
    #    SkyCoord('17h26m42.531s', '-36d09m17.376s', frame='icrs')
    #],
    #'G5.89-0.37': [
    #    SkyCoord('18h00m30.639s', '-24d04m03.082s', frame='icrs'),
    #    SkyCoord('18h00m30.507s', '-24d04m00.561s', frame='icrs')
    #],
    #'IRAS_165623959': [
    #    SkyCoord('16h59m41.62564s', '-40d03m43.6385s', frame='icrs'),
    #    SkyCoord('16h59m41.08769s', '-40d03m39.0848s', frame='icrs')
    #],
    #'IRAS_180891732': [
    #    SkyCoord('18h11m51.45454s', '-17d31m28.8163s', frame='icrs'),
    #    SkyCoord('18h11m51.39962s', '-17d31m29.9457s', frame='icrs')
    #],
    #'IRAS_181511208': [
    #    SkyCoord('18h17m58.33328s', '-12d07m23.9798s', frame='icrs'), #ALMA1-81
    #    SkyCoord('18h17m58.21401s', '-12d07m24.8938s', frame='icrs'), #ALMA2-74
    #    SkyCoord('18h17m58.12348s', '-12d07m24.7644s', frame='icrs'), #ALMA4
    #    SkyCoord('18h17m58.04552s', '-12d07m23.0619s', frame='icrs'), #ALMA5
    #],
    'IRAS_181622048':[
        SkyCoord('18h19m12.093s', '-20d47m30.946s', frame='icrs')
    ],
    #'IRAS_18182-1433': [
    #    SkyCoord('18h21m09.12462s', '-14d31m48.5998s', frame='icrs'),
    #    SkyCoord('18h21m08.97822s', '-14d31m47.5970s', frame='icrs'),
    #    SkyCoord('18h21m09.04928s', '-14d31m47.7925s', frame='icrs'),
    #    SkyCoord('18h21m09.01686s', '-14d31m47.9397s', frame='icrs')
    #],
    #'IRAS_18337-0743':[
    #    SkyCoord('18h36m41.16616s', '-7d39m24.0363s', frame='icrs'),
    #    SkyCoord('18h36m40.97008s', '-7d39m09.1196s', frame='icrs'),
    #    SkyCoord('18h36m40.80607s', '-7d39m15.6003s', frame='icrs'),
    #    SkyCoord('18h36m40.73463s', '-7d39m16.1771s', frame='icrs')
    #],
    #'IRDC_182231243': [
    #    SkyCoord('18h25m08.55193s', '-12d45m23.7189s', frame='icrs')
    #],
    #'NGC6334I': [
    #    SkyCoord('17h20m53.413s', '-35d46m57.881s', frame='icrs'), # alma1
    #    SkyCoord('17h20m53.416s', '-35d46m58.397s', frame='icrs'), # alma2
    #    SkyCoord('17h20m53.101s', '-35d47m03.322s', frame='icrs'), # alma3
    #    SkyCoord('17h20m53.187s', '-35d46m59.328s', frame='icrs'), # alma4
    #],
    #'NGC_6334_I_N': [
    #    # alma1
    #    SkyCoord('17h20m55.19122s', '-35d45m03.9506457765s', frame='icrs'),
    #    # alma 2
    #    SkyCoord('17h20m54.59259s', '-35d45m17.3664586427s', frame='icrs'),
    #    # alma 4
    #    SkyCoord('17h20m54.87219s', '-35d45m06.4298713643s', frame='icrs'),
    #    # alma 6
    #    SkyCoord('17h20m54.61936s', '-35d45m08.6730547234s', frame='icrs'),
    #    # alma 11
    #    SkyCoord('17h20m54.83885s', '-35d45m06.0538803313s', frame='icrs')
    #],
    #'W33A': [
    #    SkyCoord('18h14m39.51004s', '-17d52m00.1338s', frame='icrs')
    #],
}

molec = 'CH3OH'
#molec = 'CH3CN'

for source, coords in sources.items():
    print('=' * 80)
    print(f'Source: {source}')
    mask_dir = Path(f'../results/{source}/c5c8/per_hot_core/')
    for img in mask_dir.glob(f'*{molec}*.mask.fits'):
        mask = fits.open(img)[0]
        val = mask.data.astype(bool)
        wcs = WCS(mask)
        
        for coord in coords:
            pix_x, pix_y = wcs.world_to_pixel(coord)
            if val[int(pix_y), int(pix_x)]:
                print(f'Coord {coord.ra.hms} {coord.ra.dms} in {img.name}')
                print(f'Npix = {np.sum(val)}')
