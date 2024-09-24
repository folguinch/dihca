#!/usr/bin/bash
#set +e
################################################################################
################################################################################
# Globals                                                                      #
################################################################################
################################################################################
FIELD="G335.579-0.272"
IMGS="../final_data"
SBCB="${IMGS}/subcubes"
CFGS="../configs"
RSLT="../results_interim"
DIRTY="../dirty"
PLOTTER="python2 ${HOME}/Python/plotter/plotter.py"
SCRIPTS="python2 ${HOME}/Python/scripts"
GOCO="${HOME}/Python/GoContinuum/"
SEP="################################################################################"

################################################################################
################################################################################
# Functions                                                                    #
################################################################################
################################################################################

#######################################
# Compute moving moments.
# Globals:
#   HOME
#   WIDTHS
#   RSLT
#   ARRAY
#   MOLEC
#   WIDTH
#   CLEAN
# Arguments:
#   None
#######################################
function get_split_moving_moments() {
  local cmd="python $HOME/python_devel/line_little_helper/moving_moments.py"
  local -a flags=( --vlsr "-46.9" "km/s" --rms "2" "mJy/beam" --savemasks
                   --split "$WIDTHS" --molecule "$MOLEC" )
  local outdir="$RSLT/$ARRAY/$MOLEC"
  $cmd ${flags[@]} $WIDTH $outdir $CLEAN
}

#######################################
# Compute moving moments.
# Globals:
#   HOME
#   RSLT
#   ARRAY
#   MOLEC
#   WIDTH
#   CLEAN
#   FIELD
# Arguments:
#   QNs
#######################################
function get_symmetric_moments() {
  local cmd="python $HOME/python_devel/line_little_helper/symmetric_moments.py"
  local -a flags=( --vlsr "-46.9" "km/s" --line_lists "JPL" --molecule "$MOLEC"
                   --qns "$1" --win_halfwidth "$WIDTH" )
  local baseout="$RSLT/$ARRAY/$MOLEC/${FIELD}_${MOLEC,,}_$1_hwidth$WIDTH"
  $cmd "${flags[@]}" $CLEAN $baseout 0 1 2
}

#######################################
# Plot moving moments.
# Globals:
#   RSLT
#   ARRAY
#   CFGS
#   IMGS
#   MOLEC
#   PLOTTER
# Arguments:
#   None
#######################################
function plot_moving_moments() {
  local indir="$RSLT/$ARRAY/$MOLEC"
  local outdir="$indir/figures"
  local cfgfile="$CFGS/moving_moments.cfg"
  local map="$IMGS/config8/G335.579-0.272.config8.selfcal.cont_avg.robust0.5.image.fits"

  if [[ ! -d "$outdir" ]]; then
    mkdir $outdir
  fi

  for image in $indir/*.fits; do
    local figure=$(basename $image)
    local color="blue"
    if [[ "$figure" != *"${color}"* ]]; then
      color="red"
    fi
    figure="$outdir/${figure/.fits/.png}"
    local flags=( "--overplot" $image "--opcolor" $color 
                  "--opmapping" "0" "--shape" "1" "1" )
    $PLOTTER "${flags[@]}" $cfgfile $figure plotmaps $map
  done
}

#######################################
# Plot CH3CN moments.
# Globals:
#   RSLT
#   ARRAY
#   CFGS
#   IMGS
#   MOLEC
#   PLOTTER
# Arguments:
#   None
#######################################
function plot_ch3cn_moments() {
  local indir="$RSLT/$ARRAY/$MOLEC"
  local outdir="$indir/figures"
  local cfgfile="$CFGS/ch3cn_moments.cfg"
  local map="$IMGS/config8/G335.579-0.272.config8.selfcal.cont_avg.robust0.5.image.fits"

  if [[ ! -d "$outdir" ]]; then
    mkdir $outdir
  fi

  for image in $indir/*moment*.fits; do
    local figure=$(basename $image)
    local color="k"
    figure="$outdir/${figure/.fits/.png}"
    local flags=( --overplot "$map" --opcolor "$color"
                  --opmapping "0" --shape "1" "1" )

    if [[ "$figure" == *"moment1"* ]]; then
      local cfg="${cfgfile/moments/moments1}"
    else
      local cfg="${cfgfile}"
    fi
    $PLOTTER "${flags[@]}" $cfg $figure plotmaps $image
  done
}

# Moving moments
# SiO
#ARRAY="config8"
#MOLEC="SiO"
#local widths="5 6"
#local width="80"
#local yclean="../yclean_$ARRAY/${FIELD}_$MOLEC/auto${FIELD}_spw2.12m.tc_final.fits"

# C18O
#ARRAY="config8"
#MOLEC="C18O"
#local widths="6 6"
#local width="90"
#local yclean="../yclean_$ARRAY/${FIELD}_spw3_10/auto${FIELD}_spw3_10.12m.tc_final.fits"

# 13CO
ARRAY="concat"
#MOLEC="13CO"
#WIDTHS="10 6"
#WIDTH="90"
##CLEAN="../yclean_$ARRAY/${FIELD}_spw3_4/auto${FIELD}_spw3_4.12m.tc_final.fits"
#CLEAN="../yclean_$ARRAY/${FIELD}_spw3_2630-2950/auto${FIELD}_spw0.12m.tc_final.fits"

# SO
MOLEC="SO"
WIDTHS="9 6"
WIDTH="80"
CLEAN="../dirty/G335.579-0.272.concat.selfcal.contsub.spw3.robust0.5.image.fits"
#local yclean="../yclean_$ARRAY/${FIELD}_$MOLEC/auto${FIELD}_spw2.12m.tc_final.fits"

# Moments
#ARRAY="concat"
#MOLEC="CH3CN"
#MOLEC="CH2CHCN"
#MOLEC="CH3OH"
#WIDTH=15
#CLEAN="../yclean_$ARRAY/${FIELD}_spw3_3290-3610/auto${FIELD}_spw0.12m.tc_final.fits"
#CLEAN="../yclean_$ARRAY/${FIELD}_spw3_830-1150/auto${FIELD}_spw0.12m.tc_final.fits"
#CLEAN="../yclean_$ARRAY/${FIELD}_spw3_290-610/auto${FIELD}_spw0.12m.tc_final.fits"
#CLEAN="../dirty/G335.579-0.272.concat.selfcal.contsub.spw3.robust0.5.image.fits"

if [[ ! -d "$RSLT/$ARRAY/$MOLEC" ]]; then
  mkdir -p "$RSLT/$ARRAY/$MOLEC"
fi

if [[ "$HOSTNAME" == "seth" ]]; then
  plot_moving_moments
  #plot_ch3cn_moments
elif [[ "$HOSTNAME" == "maat" ]]; then
  get_split_moving_moments
  #CH3CN
  #get_symmetric_moments "12(3)-11(3)"
  #get_symmetric_moments "12(4)-11(4)"
  # CH2CHCN
  #get_symmetric_moments "23(15,8)-22(15,7),F=22-21"
  #get_symmetric_moments "23(4,19)-22(4,18),F=23-23"
  # CH3OH
  #get_symmetric_moments "25(3)-24(4)E1vt=0"
  #get_symmetric_moments "23(5)-22(6)E1vt=0"
  #get_symmetric_moments 8
else
  echo "Unknown hostname"
fi
