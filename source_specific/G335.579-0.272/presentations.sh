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
SBCB="${IMGS}/subcubes"
CFGS="../configs"
PLOTTER="python2 ${HOME}/Python/plotter/plotter.py"
SCRIPTS="python2 ${HOME}/Python/scripts"
GOCO="${HOME}/Python/GoContinuum/"
SOURCE="ALMA1"
ARRAY="config8"
VLSR="-46.9"
SEP="################################################################################"
source analysis_pipe.sh
source lines_pvmaps.sh

################################################################################
################################################################################
# Functions                                                                    #
################################################################################
################################################################################

# Plot continuum map
function plot_continuum () {
    local preflag="--png"
    local suffix="config8.selfcal.cont_avg.roubust0.5.image"
    local config="$CFGS/config8_figure_continuum_alma1.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.${SOURCE}.pdf"
    $PLOTTER $preflag $config $figure multiplot
}

# Plot CH3CN k-ladder
function plot_ch3cn_kladder () {
    local preflag="--png"
    local suffix="config8.alma1.ch3cn_ladder.continuum.presentation"
    local config="$CFGS/multiplot_config8_figure_ch3cn_kladder_presentation.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.pdf"
    $PLOTTER $preflag $config $figure multiplot
}

# Plot CH3CN K=8 moment maps
function plot_ch3cn_moments () {
    local kval="8"
    local linetags="ch3cn_k${kval}"
    local suffix="${ARRAY}.${linetags}"
    local cubename="$IMGS/${FIELD}.${ARRAY}.spw3.partial11.cube.image.fits"
    local chanwidth="25"
    local freq="220.47580720"
    local fluxlimit="0"

    # Calculate moments
    local outname="${IMGS}/subcubes/${FIELD}.${suffix}.${SOURCE}"
    local aux="${chanwidth} $freq ${VLSR} $fluxlimit"
    aux="$aux $cubename $outname 0 1 2"
    echo "$SEP"
    echo "SOURCE: ${SOURCE}"
    echo "K: $kval"
    if [[ ! -e "${outname}.subcube.moment0.fits" ]]
    then
        symmetric_moments "chan_halfwidth" $aux
    fi

    # Plot
    local config="$CFGS/multiplot_config8_ch3cn_k8_moments_${SOURCE,,}_presentation.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.${SOURCE}.subcube.moments.presentation.png"
    if [[ -e $config ]]
    then
        $PLOTTER $config $figure multiplot
    fi
}

function plot_line_moments () {
    local cubename="$IMGS/${FIELD}.${ARRAY}.spw3.partial11.cube.image.fits"
    #local linetags=( "ch3cn_k8" "hdco" "13co" "glycine" "vinyl_cyanide" "cyanoacetylene" "glycolaldehyde")
    #local chanwidths=( "7" "7" "3" "5" "5" "7" "7")
    #local freqs=( "220.47580720" "220.02940780" "220.39868420" "219.52028560" "219.40058460" "219.67465000" "219.911720")
    local linetags=( "ch3cn_k8" "hdco" "glycine" )
    local chanwidths=( "7" "7" "5" )
    local freqs=( "220.47580720" "220.02940780" "219.52028560" )
    local fluxlimit="0"

    for i in ${!linetags[@]}
    do
        local suffix="${ARRAY}.${linetags[$i]}"
        # Calculate moments
        local outname="${IMGS}/subcubes/${FIELD}.${suffix}.${SOURCE}"
        local aux="${chanwidths[$i]} ${freqs[$i]} ${VLSR} $fluxlimit"
        aux="$aux $cubename $outname 0 1 2"
        echo "$SEP"
        echo "SOURCE: ${SOURCE}"
        echo "Line: ${linetags[$i]}"
        if [[ ! -e "${outname}.subcube.moment0.fits" ]]
        then
            #symmetric_moments "chan_halfwidth" $aux
            echo skipping""
        fi

        # Plot
        local config="$CFGS/multiplot_config8_${linetags[$i]}_moments_${SOURCE,,}_presentation.cfg"
        local figure="$FIGS/${FIELD}.${suffix}.${SOURCE}.subcube.moments.presentation.png"
        if [[ -e $config ]]
        then
            $PLOTTER $preflag $config $figure multiplot
        fi
    done
}

function plot_hot_lines () {
    local cubename="$IMGS/${FIELD}.${ARRAY}.spw3.partial11.cube.image.fits"
    local config="$CFGS/multiplot_config8_hotlines_moments_${SOURCE,,}_presentation.cfg"
    local figure="$FIGS/${FIELD}.hotlines.${SOURCE}.subcube.moments.presentation.png"

    if [[ -e $config ]]
    then
        $PLOTTER $config $figure multiplot
    fi
}

function plot_pvmaps () {
    local lines=( "13CO" "ch3cn_k2" "ch3cn_k3" "ch3cn_k4" "ch3cn_k7" "ch3cn_k8" "glycine" )
    local sources=( "alma1a" "alma1b" )
    local fig_config="${CFGS}/figures_pvmaps_${ARRAY}.cfg"

    for src in ${sources[@]}
    do
        get_pv $src $RSLT "${lines[@]}"
    done
    plot_pv $fig_config $RSLT "${lines[@]}"
}

function plot_line_examples () {
    local config="$CFGS/plot_13co_ch3cn_k3_line_presentation.cfg"
    local figure="$FIGS/${FIELD}.config8.alma1.13co_ch3cn_k3_line.presentation.png"
    $PLOTTER $config $figure multiplot

    local config="$CFGS/plot_13co_ch3cn_k2_line_presentation.cfg"
    local figure="$FIGS/${FIELD}.config8.alma1.13co_ch3cn_k2_line.presentation.png"
    $PLOTTER $config $figure multiplot

    local config="$CFGS/plot_13co_ch3cn_k4_line_presentation.cfg"
    local figure="$FIGS/${FIELD}.config8.alma1.13co_ch3cn_k4_line.presentation.png"
    $PLOTTER $config $figure multiplot
}

################################################################################
################################################################################
# Main                                                                         #
################################################################################
################################################################################

while [[ "$1" != "" ]]
do
    case $1 in
        #1 ) # Continuum figure
        #    plot_continuum $1;;
        kladder ) # CH3CN K ladder
            plot_ch3cn_kladder $1;;
        ch3cnmom ) # CH3CN K=8 moment
            plot_ch3cn_moments $1 ;;
        moms ) # Moments of few lines
            plot_line_moments ;;
        hot ) # plot hot lines mosaic
            plot_hot_lines;;
        compare )
            plot_line_examples ;;
        #pvs ) # pv maps of few lines
        #    plot_pvmaps ;;
    esac
    shift
done

