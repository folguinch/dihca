#!/usr/bin/bash
set -e
################################################################################
################################################################################
# Globals                                                                      #
################################################################################
################################################################################
FIGS="../figures"
IMGS="../clean"
CFGS="../configs"
RSLT="../results"
PLOTTER="python ${HOME}/Python/plotter/plotter.py"
SCRIPTS="python ${HOME}/Python/scripts"
GOCO="${HOME}/Python/GoContinuum/"
SPW=( "spw1" "spw2" "spw3" )
REDO=0
SEP="################################################################################"

################################################################################
################################################################################
# Main                                                                         #
################################################################################
################################################################################

continuum="$IMGS/G335.579-0.272.config5.selfcal.cont_avg.robust0.5.image.fits"
for spw in ${SPW[@]}
do
    linecfg="$CFGS/lines_${spw}_alma1.cfg"
    preflags="--overall --overplot $continuum --opcolor #36fe30 --png"
    posflags="--vlsr -46.9 --lineconfig $linecfg"
    #posflags="$posflags --continuum $continuum"
    figconfig="$CFGS/line_figures.cfg"
    outbase="$FIGS/G335.579-0.272.config5.${spw}.alma1.png"
    cube="$IMGS/G335.579-0.272.config5.${spw}.fits"

    $PLOTTER $preflags $figconfig $outbase chanmap $posflags $cube
done
