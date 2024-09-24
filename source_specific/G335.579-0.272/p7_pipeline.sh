#!/usr/bin/bash
set -e
################################################################################
################################################################################
# Globals                                                                      #
################################################################################
################################################################################
FIELD="G335.579-0.272"
FIGS="../figures"
IMGS="../clean"
CFGS="../configs"
RSLT="../results_interim/config8"
PAPER="${HOME}/Documents/Papers/P7/figures"
PLOTTER="python2 ${HOME}/Python/plotter/plotter.py"
SCRIPTS="python2 ${HOME}/Python/scripts"
GOCO="${HOME}/Python/GoContinuum/"
REDO=0
SOURCES=( "ALMA1" "ALMA3" )
VLSRS=( "-46.9" "-47.6" )
SEP="################################################################################"
source analysis_pipe.sh

################################################################################
################################################################################
# Functions                                                                    #
################################################################################
################################################################################

function plot_continuum () {
    local preflag="--png"
    local suffix="config8.selfcal.cont_avg.roubust0.5.image"
    local config="$CFGS/multiplot_config8_figure_continuum.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.pdf"
    $PLOTTER $preflag $config $figure multiplot
    copy_to_paper $figure $1
}

################################################################################
################################################################################
# Main                                                                         #
################################################################################
################################################################################

while [[ "$1" != "" ]]
do
    case $1 in
        1 ) # Continuum figure
            plot_continuum $1;;
        2 ) # CH3CN K ladder
            plot_kladder $1;;
        #3 ) # CH3CN K=4
        #    plot_line_moments $1 "4";;
        3 ) # CH3CN K=7
            plot_line_moments $1 "7"
            plot_line_moments $1 "4";;
        4 ) # 13CO and SiO lobes
            plot_split_lines $1;;
        5 ) # HDCO, acetone moments
            plot_hot_lines $1;;
        6 ) # HDCO velocity maps
            plot_hdco_velocities $1;;
        7 ) # 13CO H2CO lines
            plot_line_examples $1;;
        8 ) # 13CO H2CO lines
            plot_models $1;;
        dm ) # Dust mass
            shift
            dust_mass $1;;
        vlsr ) # Fit vlsr
            shift
            fit_vlsr $1;;
    esac
    shift
done

#function config8_continuum () {
#    local preflags="--png --shape 1 1"
#    local posflags=""
#    local suffix="config8.selfcal.cont_avg.robust0.5.image"
#    local image="$IMGS/${FIELD}.${suffix}.fits"
#    local config="$CFGS/p6_figures.cfg"
#    local figure="$1"
#    $PLOTTER $preflags $config $figure plotmaps $posflags $image
#    
#    local section="--section maps_plots_clean"
#    $PLOTTER $preflags $config ${figure/.pdf/nomarkers.pdf} plotmaps $posflags $section $image
#
#    local section="--section alma3"
#    local posflags="--selflevels"
#    $PLOTTER $preflags $config ${figure/.pdf/alma3.pdf} plotmaps $posflags $section $image
#    
#    local section="--section alma1"
#    $PLOTTER $preflags $config ${figure/.pdf/alma1.pdf} plotmaps $posflags $section $image
#}
#
## CH3CN moment maps config 8
#function plot_line_moments_config8 () {
#    local products="/home/myso/share/binary_project/2016.1.01036.S/science_goal.uid___A001_X88e_Xe8/group.uid___A001_X88e_Xe9/member.uid___A001_X88e_Xea/product"
#    products="$products/member.uid___A001_X88e_Xea._G335.579-0.272__sci.spw31.cube.I.pbcor.fits"
#    local linetags="ch3cn_k4"
#    local preflags="--png --shape 1 1"
#    local config="$CFGS/p6_figures.cfg"
#    local figure="$FIGS/${FIELD}.config8.alma1.pdf"
#    local postflags="--section ch3cn_moments_alma1"
#    local lines="--lineconfig $CFGS/lines_spw3_config8.cfg --lines $linetags"
#    local moments="--momentbase $RSLT/${FIELD}.config8"
#    moments="$moments --moments 0"
#    local sources="--atsources $CFGS/source_alma1.cfg"
#    local cubename="--cubename $products"
#    local postargs="$postflags $lines $moments $sources $cubename"
#    local overplot="--overall --opcolor #7f7f7f --overplot"
#    local suffix="config8.selfcal.cont_avg.robust0.5.image"
#    overplot="$overplot $IMGS/${FIELD}.${suffix}.fits"
#
#    $PLOTTER $overplot $preflags $config $figure plotmoments $postargs
#}
#
## config 8 continuum
#FIG="$FIGS/${FIELD}.config8.selfcal.cont_avg.robust0.5.image.pdf"
#if [[ ! -e $FIG ]] || [[ $REDO -eq 1 ]]
#then
#    config8_continuum $FIG
#else
#    echo "Skipping continuum image"
#fi
#echo $SEP
#
#plot_line_moments_config8
