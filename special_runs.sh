# Special run of scripts not covered by pipelines
declare -a flags 

# Compute peak maps using moment map sub-cube
# This was used for P7 as requested by referee
declare cube
declare moldir
moldir="/data/share/binary_project/results/G336.01-0.82/c8/CH3OH"
flags=( "--vlsr" "-47.2" "km/s"
        "--line_lists" "CDMS"
        "--molecule" "CH3OH"
        "--qns" "18(3,15)-17(4,14)A,vt=0"
        "--nsigma" "5"
        "--moments" "0"
        "--nlinewidth" "2"
        "--rms" "2.6" "mJy/beam"
        "--use_dask"
        "--common_beam" )
#"--linewidth_map" "${moldir}/CH3OH_18_3_15_-17_4_14_A_vt_0.subcube.moment2.fits"
cube="${moldir}/CH3OH_18_3_15_-17_4_14_A_vt_0.subcube.fits"
python -m line_little_helper.line_peak_map ${flags[@]} $cube $moldir
