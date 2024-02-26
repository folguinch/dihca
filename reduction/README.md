# G335.579-0.272

## Source data:

Measured values updated with the correct positions. For ALMA source, first line
measurement in the non-pbcor image, second in pbcor one.

Origin            |      RA       |      Dec      | Ref.
----------------- | ------------- | ------------- | ----
MM1a              | 16h30m58.765s | -48d43m54.00s | 1
                  | 16h30m58.768s | -48d43m54.05s | 
MM1b              | 16h30m58.638s | -48d43m51.70s | 1
                  | 16h30m58.649s | -48d43m51.45s |
H2O - maser       | 16h30m58.730s | -48d43m51.20s | 2
CH3OH - CII maser | 16h30m58.670s | -48d43m50.70s | 3
CH3OH - CII maser | 16h30m58.790s | -48d43m53.40s | 3
ALMA 1            | 16h30m58.761s | -48d43m54.01s | 
                  | 16h30m58.761s | -48d43m54.01s |
ALMA 2            | 16h30m58.703s | -48d43m52.60s |
                  | 16h30m58.703s | -48d43m52.60s |
ALMA 3            | 16h30m58.631s | -48d43m51.28s |
                  | 16h30m58.631s | -48d43m51.28s |
ALMA 4            | 16h30m58.676s | -48d43m51.78s |
                  | 16h30m58.676s | -48d43m51.78s |
ALMA 5            | 16h30m58.891s | -48d43m55.16s |
                  | 16h30m58.889s | -48d43m55.18s |

Refs.:
1. Radio sources from Avison et al. (2015)
2. [Breen et al. (2010)](https://ui.adsabs.harvard.edu/abs/2010MNRAS.406.1487B/abstract)
3. [Caswell et al. (2011)](https://ui.adsabs.harvard.edu/abs/2011MNRAS.417.1964C/abstract)

## Statistics

Check regions in `regions` directory.

- continuum:
  rms = 4.1E-4 Jy/beam
  freq = 226.15 GHz
  wav = 1.33 mm

- spw0:
  rms = 5.8E-3 Jy/beam

- spw1:
  rms = 5.4E-3 Jy/beam

- spw2:
  rms = 5.4E-3 Jy/beam

- spw3:
  rms = 4.1E-3 Jy/beam

## Measurements

- continuum:
  - Flux density over 5sigma = 1.22 Jy

- continuum pbcor:
  - Flux density over 5sigma = 1.23 Jy (measured over same mask)

## LSR velocity fit

- ALMA 1:
    - CH3CN K7:
        - Line peak at: -47.14 km/s
        - Line centroid at: -47.17 km/s
        - Line fit peak at velocity: -46.76 km/s
    - CH3CN K8:
        - Line peak at: -46.54 km/s
        - Line centroid at: -47.04 km/s
        - Line fit peak at velocity: -46.95 km/s
    - Fit vlsr: -46.85 km/s

- ALMA 3:
    - CH3CN K7:
        - Line peak at: -45.15 km/s
        - Line centroid at: -47.92 km/s
        - Line fit peak at velocity: -44.89 km/s
    - CH3CN K8:
        - Line peak at: -45.21 km/s
        - Line centroid at: -46.99 km/s
        - Line fit peak at velocity: -45.17 km/s
    - Fit vlsr: -45.03 km/s

## Useful information

- Band 3 median beam around CH3CN: 0.401"x0.350" PA=-57.849

- ALMA 1 peak pixel 480 480

- ALMA 3 peak pixel 502 526

## Command line for results

### Channel maps:

#### C18O
```bash
~/Python/plotter/plotter.py --shape 4 4 chanmap --image ../clean/G335.579-0.272.config5.cont_avg.fits --chanran 2742 2758 ../clean/G335.579-0.272.config5.spw3.fits figures.cfg ../figures/spw3_c18o_chanmap.png
```

#### CH3CN
```bash
~/Python/plotter/plotter.py --shape 4 4 chanmap --continuum clean/G335.579-0.272.config5.cont_avg.fits --chanran 448 464 clean/G335.579-0.272.config5.spw3.fits configs/figures.cfg figures/spw3_ch3cn_chanmap.png
```

#### 13CO
```bash
~/Python/plotter/plotter.py --shape 8 8 chanmap --continuum clean/G335.579-0.272.config5.cont_avg.fits --chanran 994 1058 clean/G335.579-0.272.config5.spw3.fits configs/figures.cfg figures/spw3_13co_chanmap.png
```

#### SiO
```bash
~/Python/plotter/plotter.py --shape 8 9 chanmap --continuum clean/G335.579-0.272.config5.cont_avg.fits --chanran 3231 3303 clean/G335.579-0.272.config5.spw2.fits configs/figures.cfg figures/spw2_sio_chanmap.png
```

### Moment maps

```bash
~/Python/plotter/plotter.py --detailaxlabel plotmoments --moments 0 1 --imagenames results/G335.579-0.272.config5.spw3.ch3cn_k4.integrated.all.fits results/G335.579-0.272.config5.spw3.ch3cn_k4.weighted_coord.fits configs/figures.cfg figures/ch3cn_k4_moments.png
```

### Continuum map:

```
~/Python/plotter/plotter.py --shape 1 1 plotmaps clean/G335.579-0.272.config5.cont_avg.fits configs/figures.cfg figures/continuum.png
```

### Dust masses:

```bash
python ~/Python/scripts/dust_mass.py --fluxfile results/fluxes.dat -d 3.25 kpc --nu 226.1500 GHz -t 100 150 200 --output results/dust_masses.txt
```

## CASA moments

See `scripts` directory for ch3cn.

### 13CO

Channels:
**original values**
- Blue: 992-1030
- Red:  1037-1064 
**symmetric values (35chans)**
- Line closest channel: 1032
- Blue: 992-1027
- Red: 1037-1072

### SiO

Channels:
**original values**
- Blue: 3251 3269
- Red: 3275 3288
**symmetric values (20chans)**
- Line closest channel: 3273
- Blue: 3248 3268
- Red: 3278 3298

~/Python/plotter/plotter.py --overall --overplot results/G335.579-0.272.config5.spw2.sio.integrated.blue.fits results/G335.579-0.272.config5.spw2.sio.integrated.red.fits --opcolor b r --shape 1 1 plotmaps clean/G335.579-0.272.config5.cont_avg.fits configs/figures.cfg figures/spw2_sio_split.png


~/Python/plotter/plotter.py --shape 2 3 configs/figures_poster.cfg figures/spw3_c18o_chanmap_poster.png chanmap --every 2 --auto_velshift --continuum clean/G335.579-0.272.config5.cont_avg.fits --chanran 2744 2755 clean/G335.579-0.272.config5.spw3.fits


~/Python/plotter/plotter.py --detailaxlabel --overall --overplot results/G335.579-0.272.config5.spw3.13co.integrated.blue.fits results/G335.579-0.272.config5.spw3.13co.integrated.red.fits --opcolor b r --shape 1 1 configs/figures_poster.cfg figures/spw3_13co_split_poster.png plotmaps --section split13co clean/G335.579-0.272.config5.cont_avg.fits

---

# G333.23-0.06

## Config5

- Lines and continuum were self-calibrated using the last phase selfcal table (done outside GoCo).

- CASA 5.6 was used for line imaging.

## Config8

- Lines and continuum were self-calibrated using the last phase selfcal table (done outside GoCo).

- Peak was chosen manualy from selfcal position: 1042 1006.

---

# NGC_6334_I_N

## Config5

- Peak position of EB1 jumping, so the combined position does not have line emission. Peak positions of EB2 are stable. So the peak position of EB2 was used for EB1. This works well enough and is closer to the best positions of EB1 in a couple of spws.

- Final run:
```bash
nohup ~/Python/GoContinuum/goco --skip DIRTY --pos 847 1164 --noredo --neb 2 NGC_6334_I_N &
```

## Config8

- Amp selfcal was applied to the continuum and last phase for lines. These were applied before goco.

- Possition in AFOLI jumping, fixed position to selfcal one: 1043 2007

---

# IRAS_165474247

## Config 8

- Amp selfcal and last phase selfcal were applied to continuum and contsub, respectively.

- AFOLI peak selection is ok.

---

# NGC6334I

## Config5

- Phase self-cal was used for all images (line and continuum) because amp selfcal did not work well.

## Config8

- Peak pixel shifted 1 pixel from the selfcal one. No changed made for AFOLI.

- Amp selfcal was used for continuum and phase for lines.

- Applycal was run before goco.

---

# IRAS_165623959

## Config8

- Amp selfcal applied to continuum and phase applied to lines.

- Applycal was run before goco.

---

# G34.43+0.24

## Config 8

### AFOLI

- Pixel position shifted from selfcal but with good ammount of lines

---

# G29.96-0.02

## Config 8

### AFOLI

- Scattered peaks, but close enough. Final pixel close to selfcal one.

---

# G35.03+0.35_A

## Config 8

### Goco

- Amp selfcal used for continuum and phase for lines

- Peak spectra ok.

---

# G35.20-0.74_N

## Config 8

### Goco

- Amp selfcal used for continuum and phase for lines.

- Peak position fixed to selfcal: 1513, 1539. Original positions change between EB, but similar spectra.

---

# IRAS_181511208

## Config 8

### GoCo

- Phase selfcal was used for both continuum and lines.

- Position fixed to selfcal position: 1466 1426

---

# IRDC_182231243

## Config 5

- Peak position jumping. Run with manual position 698 690 from spw 0.

- Frist run of AFOLI in folders run1 inside dirty and plots.

## Config 8

- Only 2 phase selfcal iterations were done because the S/N converged.

- Amplitude selfcal was applied to the continuum and 2nd phase selfcal table to the lines.

- Peak position jumping, selecting the same as selfcal: 1395 1360.

---

# IRAS_18182-1433

## Config 8

### Selfcal

- Position for spectrum was fixed to 1618 1696, because it hs more lines than the dust continuum peak.

### GoCo

- Amp selfcal was used for continuum and phase for lines.

- Position selected by goco is better than for selfcal, so was not changed.

---

# IRAS_181622048

## Config 8

- Phase self-cal was applied to lines and continuum, amp self-cal removed faint sources.

- Peak positions between EBs is almost the same (1 pix difference), so AFOLI was run without selecting peak manually.

---

# IRAS_180891732

## Config 8

### Selfcal

- Amplitude used for continuum and last phase for lines

### GoCo

- Dirty images were duplicated for running the code

- AFOLI looks alright, peak pixel close to selfcal one.

---

# G11.92-0.61

## Config 8

### Selfcal

- Amp. selfcal looks better for the continuum.

### AFOLI

- Lot of variation in peak results. Final run with the position fixed to: 1270 1284 (from eb1 but close to the position used for selfcal)

---

# G10.62-0.38

## Config 5

- Amp selfcal applied to continuum images and phase to lines.

## Config 8

- Amp selfcal applied to continuum images and phase to lines.

### AFOLI

- Position fixed to EB 2 position: 1452 1402

- Recomb line does not appear in the selected position, so channels are added by hand in spw1: 824~887

---

# W33A

## Config5

- Amp selfcal was used for lines and continuum.

- Cubes produced with CASA 5.4

## Config8

### Goco

- Position set to EB2 and 3: 1240 1488

---

# G11.1-0.12

## Config8

### GoCo

- Positions between the ebs jump, but are close to each other and with line emission. So we didn't fix the position do the peak spectrum.

---

# G5.89-0.37

## Config5

### Goco

- Positions jumping:

Original locations (in run1):

| x   | y   continuum spw0         spw1                 spw2                 spw3
| --- | --- 
| 535 | 482 SE        ok           slightly more lines  ok, noisier          less lines
| 516 | 494 same      ok, noisier  just recomb.         lines in absorption  lines in absorption
| 512 | 555 N(far)    ok           more lines           ok                   ok
| 482 | 530 NW        ok           more lines           ok                   ok

- `(512 555)` seems to be the best option

- Solution: in most spws the pixel selected by the jumping locations seems to 
  be alright in terms of lines flagged with respect to the original location. 
  For spw3 the channel files were combined with the channels from `(512 555)` 
  using `combine_casa_channels.py`.

## Config8

### Selfcal

- Amp selfcal applied to continuum and phase to lines.

### Goco

- Peak position jumping in first run. Position fixed to 1360 1466 from spw3 in selfcal.

---

# G343.12-0.06

## Concat

- Procedure to concat c8 and c5 images in `others/G343.12-0.06_config8_concat_IRAS_165474247.py`

---

# G351.77-0.54

## Config 8

### AFOLI

- Position from selfcal was used to get the spectrum for afoli.

---

# G336.01-0.82

## Config8

- Amp selfcal applied to continuum and last phase to lines.

- Position fixed to selfcal one: 1447, 1457

- to extract spectra:

"""bash
python ~/python/line_little_helper/scripts/spectrum_helper.py yclean_config8/G336.01-0.82_spw0_0_1000/autoG336.01-0.82_spw0.tc_final.image.fits yclean_config8/G336.01-0.82_spw0_2000_2800/autoG336.01-0.82_spw0.tc_final.image.fits --mask_from ../../results/G336.01-0.82/CH3OH/spectra/moment0_map_18-17.fits.subcube.moment0.fits --vlsr "-47.2" "km/s" --savemask spectra_mask_3sigma.fits --outdir ../../results/G336.01-0.82/CH3OH/spectra/ --rest --nsigma 3 --box 2527 2566 2644 2646 --rms 0.0025242791177874676 Jy/beam
"""

---

# G335.78+0.17

## Config 8

- Amp selfcal was applied to the continuum data and last phase to lines.

---

# G333.12-0.56

## Config 5

- Peak position replaced with selfcal one: 579 371

## Config 8

- Peak position replaced with selfcal one:  1990, 741

---

# G333.46-0.16

## Config 8

- amp selfcal -> continuum
- phase selfcal -> lines
- Positions jumping but in close pixels

---

# IRAS_18337-0743

## Config 5

- Peak position selected by hand using the selfcal max position: 396 374

## Config 8

- Not much improvement after phase 2nd iteration.
- Slight improvement after amp selfcal but lower aspect quality.
- Last phase selfcal tables applied for both continuum and lines.
- Selfcal position used to extract spectra.

---

# G24.60+0.08

## Config 5

- Channels masked manually in spw2 and 3 because there are a couple of wide 
lines in a different source. Run AFOLI again to recover the original.

## Config 8

- Phase selfcal used for continuum and lines. Amp selfcal seems to create new (faint) sources and improvement is not much.

- Selfcal position used as positions are jumping between spws.

--- 

# G35.13-0.74

## Config 5

- EB1 files were deleted and EB2 renamed.

- Amp. selfcal applied to continuum and phase to lines.

## Config 8

- Amp. selfcal applied to continuum and phase to lines.

---

# G34.43+0.24MM2

## Config5

- From QA README: This mOUS includes two EBs. However, one EB 
  (uid://A002/Xd58951/X788d) was not used for imaging because the data is not 
  good. The science target was fully flagged in the calibration process. 
  Regarding the other EB (uid://A002/Xd58951/Xe3ae), one antenna (DA55) and the
  beginning part of the observation were flagged by hand.

- Hence, only EB2 data was selfcal'ed and imaged. Noise levels seem similar to
  those of the other sources.

- Amplitude selfcal used for continuum and last phase to cubes during goco.

- Dirty cubes renamed to avoid the use of the EB suffix.

- EB1 data was deleted to avoid confussion and EB2 data renamed.

## Config 8

- Amp selfcal was used for continuum and last phase for contsub

---

# G14.22-0.50_S

## Config 5

### GoCo

- Peak positions jumping from max map. Solved running with the postion from selfcal: 397 446

## Config 8

- Amp selfcal applied to continuum and last phase to lines.
