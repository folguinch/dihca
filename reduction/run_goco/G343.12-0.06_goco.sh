source /home/myso/share/binary_project/maat_venv/env/bin/activate
declare cmd="${HOME}/Python/GoContinuum/goco"
declare field="G343.12-0.06"
declare -a pbclean=( "gridwt" "image" "image.pbcor" "mask" "model" "pb"
                     "psf" "residual" "sumwt" "workdirectory" )
declare -a flags
declare -a pbims

# AFOLI only
#flags=( --skip "DIRTY" "SPLIT" "CONTSUB" "YCLEAN" "PBCLEAN" )

# Create ms
# continuum and lines
flags=( --noredo --skip "DIRTY" "AFOLI" "YCLEAN" )

$cmd "${flags[@]}" "${field}"

for pb in "${pbclean[@]}"; do
  pbims=( pbclean/${field}.config8.*.robust0.5.${pb} )
  if [[ -d "${pbims[0]}" ]]; then
    rm -r "${pbims[@]}"
  fi
done
    
deactivate
