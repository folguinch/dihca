source ../../anubis_venv/env/bin/activate
CMD="python ${HOME}/Python/scripts/get_continuum_windows.py"
FLAGS=( "--noise" "5E-4" "--step" "0.9" "--plot" )

for dirty in dirty/W33A.*.config8.spw*.robust2.0.image.fits; do
    echo "############################################################################################################################"
    echo "Working on: $dirty"
    plotname="$(basename $dirty)"
    plotname="plots/${plotname/image.fits/image.selfcal.cont_win.auto.png}"
    echo "$CMD ${FLAGS[@]} $plotname $dirty"
    $CMD ${FLAGS[@]} $plotname $dirty
done
