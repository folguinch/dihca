source /home/myso/share/binary_project/anubis_venv/env/bin/activate
declare cmd="${HOME}/Python/GoContinuum/goco"
declare field="G351.77-0.54"
declare -a pbclean=( "gridwt" "image" "image.pbcor" "mask" "model" "pb"
                     "psf" "residual" "sumwt" "workdirectory" )
declare -a flags
declare -a pbims
export PATH=/home/myso/opt/casa-release-5.6.0-60.el7/bin:$PATH

# AFOLI only
#flags=( --skip "DIRTY" "SPLIT" "CONTSUB" "YCLEAN" "PBCLEAN" --pos 1398 1401 )

# Create ms
# continuum
#flags=( --noredo --skip "DIRTY" "AFOLI" "CONTSUB" "YCLEAN" --pos 1398 1401 )
# lines
#flags=( --noredo --skip "DIRTY" "SPLIT" "YCLEAN" "PBCLEAN" --pos 1398 1401 )
flags=( --noredo --skip "DIRTY" "AFOLI" "YCLEAN" )

$cmd "${flags[@]}" "${field}"

for pb in "${pbclean[@]}"; do
  pbims=( pbclean/${field}.config8.*.robust0.5.${pb} )
  if [[ -d "${pbims[0]}" ]]; then
    rm -r "${pbims[@]}"
  fi
done
    
deactivate
