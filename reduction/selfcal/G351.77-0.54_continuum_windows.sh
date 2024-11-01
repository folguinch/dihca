source /home/myso/share/binary_project/maat_venv/env/bin/activate
declare field="G351.77-0.54"
declare cmd="python ${HOME}/Python/scripts/get_continuum_windows.py"
declare -a flags=( --noise "8E-4" --step "0.9" --plot )
declare plotname

for dirty in dirty/${field}.config8.spw*.robust2.0.image.fits; do
    echo "###########################################################"
    echo "Working on: $dirty"
    plotname="$(basename $dirty)"
    plotname="plots/${plotname/image.fits/image.selfcal.cont_win.auto.png}"
    if [[ ! -e "${plotname}" ]]; then
      ${cmd} "${flags[@]}" "$plotname" $dirty
    fi
done

deactivate
