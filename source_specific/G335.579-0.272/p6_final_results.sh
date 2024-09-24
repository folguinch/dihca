
python spectrum_extractor.py --coordinate "16h30m58.7672s -48d43m53.876s icrs"
--vlsr -46.9 km/s --cubes
/home/myso/share/binary_project/G333_G335/G335.579-0.272/final_data/G335.579-0.272.config8.spw3.partial11.cube.image.fits


python ~/python_devel/line_little_helper/moving_moments.py --vlsr -46.9 km/s
--rms 2 mJy/beam --savemasks --split 8 3 SiO 30 results_interim/config8/SiO
yclean_config8/G335.579-0.272_SiO_hogbom/autoG335.579-0.272_spw2.12m.tc_final.fits
