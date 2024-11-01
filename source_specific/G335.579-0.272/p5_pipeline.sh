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
RSLT="../results_interim/config5"
FRSLT="../results_final/config5"
PAPER="${HOME}/Documents/Papers/P5"
PLOTTER="python2 ${HOME}/Python/plotter/plotter.py"
SCRIPTS="python2 ${HOME}/Python/scripts"
GOCO="${HOME}/Python/GoContinuum/"
REDO=0
SOURCES=( "ALMA1" "ALMA3" )
ARRAY="config5"
VLSRS=( "-46.9" "-47.6" )
SEP="################################################################################"
source analysis_pipe.sh
source lines_pvmaps.sh

################################################################################
################################################################################
# Functions                                                                    #
################################################################################
################################################################################
# Plot continuum
function plot_continuum () {
    local preflags="--png --shape 1 1"
    local posflags="--selflevels"
    local suffix="config5.selfcal.cont_avg.robust0.5.image"
    local image="$IMGS/${FIELD}.${suffix}.fits"
    local config="$CFGS/p5_figures.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.pdf"
    $PLOTTER $preflags $config $figure plotmaps $posflags $image
    copy_to_paper $figure $1
}

# Plot k-ladder
function plot_kladder () {
    local preflag="--png"
    local suffix="config5.ch3cn_ladder.continuum"
    local config="$CFGS/multiplot_ch3cn.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.pdf"
    $PLOTTER $preflag $config $figure multiplot
    copy_to_paper $figure $1
}

# CH3CN moment maps
function plot_line_moments () {
    local kval=${2}
    local linetags="ch3cn_k${kval}"
    local suffix="config5.${linetags}"
    local cubename="$IMGS/${FIELD}.config5.spw3.fits"
    local fluxlimit="0.025"
    if [[ "${kval}" == "7" ]]
    then
        local chanwidths=( "10" "25" )
        local freq="220.53932350"
        #local to_paper="$1a"
    elif [[ "${kval}" == "4" ]]
    then
        local chanwidths=( "12" "25" )
        local freq="220.67928690"
        #local to_paper="$1b"
    fi
    # Calculate moments
    for i in "${!SOURCES[@]}"
    do
        # Calculate moment
        local outname="${IMGS}/subcubes/${FIELD}.${SOURCES[$i]}.${suffix}"
        local aux="${chanwidths[$i]} $freq ${VLSRS[$i]} $fluxlimit"
        aux="$aux $cubename $outname 0 1 2"
        echo "$SEP"
        echo "SOURCE: ${SOURCES[$i]}"
        echo "K: $kval"
        if [[ ! -e "${outname}.subcube.moment0.fits" ]]
        then
            symmetric_moments "chan_halfwidth" $aux
        fi

        # Velocity gradient
        if [[ "${SOURCES[$i]}" == "ALMA3" ]]
        then
            echo "Computing velocity gradient"
            vel_gradient ${SOURCES[$i]} $kval
        fi

        # Plot
        local preflag="--png"
        local config="$CFGS/multiplot_${ARRAY}_${linetags}_moments_${SOURCES[$i],,}.cfg"
        local figure="$FIGS/${FIELD}.${SOURCES[$i]}.${suffix}.subcube.moments.pdf"
        if [[ -e $config ]]
        then
            $PLOTTER $preflag $config $figure multiplot
        fi

        if [[ "${SOURCES[$i]}" == "ALMA1" ]] && [[ "${kval}" == "7" ]]
        then
            copy_to_paper $figure "${1}"
        elif [[ "${SOURCES[$i]}" == "ALMA3" ]] && [[ "${kval}" == "4" ]]
        then
            copy_to_paper $figure "${1}"
        fi
    done
}

# Plot SiO and 13CO red/blueshifted
function plot_split_lines () {
    local preflags="--shape 2 1 --detailaxlabel --png"
    local overplot="--opmapping 0 0 1 1 --overplot"
    local molecs=( "13CO.blue" "13CO.red" "SiO.blue" "SiO.red" )
    #overplot="$overplot $RSLT/${FIELD}.config5.13CO.blue.mom0.image.fits"
    #overplot="$overplot $RSLT/${FIELD}.config5.13CO.red.mom0.image.fits"
    #overplot="$overplot $RSLT/${FIELD}.config5.SiO.blue.mom0.image.fits"
    #overplot="$overplot $RSLT/${FIELD}.config5.SiO.red.mom0.image.fits"
    local config="$CFGS/p5_figures.cfg"
    local figure="$FIGS/${FIELD}.config5.13CO.SiO.split.pdf" 
    local postflags="--section split_lines"
    local images="$IMGS/${FIELD}.config5.selfcal.cont_avg.robust0.5.image.fits"
    images="$images $images"
    
    for molec in ${molecs[@]}
    do
        local outname="${IMGS}/subcubes/${FIELD}.config5.${molec}"
        overplot="$overplot ${outname}.subcube.moment0.fits"
        if [[ -e ${outname}.subcube.moment0.fits ]]
        then
            continue
        fi

        if [[ $molec == "13CO.blue" ]]
        then
            local aux="chan_range  992 1027"
            local cubename="$IMGS/${FIELD}.config5.spw3.fits"
        elif [[ $molec == "13CO.red" ]]
        then
            local aux="chan_range 1037 1072"
            local cubename="$IMGS/${FIELD}.config5.spw3.fits"
        elif [[ $molec == "SiO.blue" ]]
        then
            local aux="chan_range 3248 3268"
            local cubename="$IMGS/${FIELD}.config5.spw2.fits"
        elif [[ $molec == "SiO.red" ]]
        then
            local aux="chan_range 3278 3298"
            local cubename="$IMGS/${FIELD}.config5.spw2.fits"
        fi
        aux="$aux $cubename $outname 0"
        echo "Obtaining moments for $molec"
        symmetric_moments $aux
        echo $SEP
        
    done
    overplot="$overplot --opcolor b #c71f0e b #c71f0e" 

    echo "Plotting ..."
    $PLOTTER $overplot $preflags $config $figure plotmaps $postflags $images
    copy_to_paper $figure $1
}

# Plot HDCO acetone moments
function plot_hot_lines () {
    local preflags="--png"
    local config="$CFGS/multiplot_hdco_acetone.cfg"
    local figure="$FIGS/${FIELD}.config5.alma1.hdco_acetone.pdf"
    local molecs=( "hdco" "acetone54-54AE" )
    local chanwidths=( "8" "10" )
    local freqs=( "220.02940780" "231.68683190" )
    local spws=( 3 1 )
    local fluxlimits=( "0.025" "0.027" )

    for i in ${!molecs[@]}
    do
        # Calculate moment
        local suffix="config5.${molecs[$i]}"
        local outname="${IMGS}/subcubes/${FIELD}.ALMA1.${suffix}"
        local cubename="$IMGS/${FIELD}.config5.spw${spws[$i]}.fits"
        local aux="${chanwidths[$i]} ${freqs[$i]} ${VLSRS[0]} ${fluxlimits[$i]}"
        aux="$aux $cubename $outname 0 1 2"
        echo "$SEP"
        echo "Molecule: ${molecs[$i]}"
        if [[ ! -e "${outname}.subcube.moment0.fits" ]]
        then
            symmetric_moments "chan_halfwidth" $aux
        fi
    done

    $PLOTTER $preflags $config $figure multiplot
    copy_to_paper $figure $1
}

# Plot HDCO velocity maps
function plot_hdco_velocities () {
    #local preflags="--detailaxlabel --png --shape 2 2"
    #local posflags="--section hdco_prog --lineconfig $CFGS/lines_spw3_alma1.cfg"
    #posflags="$posflags --lines HDCO --moments 1 1 1 1 --vlsr -46.9"
    #local results="$FRSLT/prog_first_mom_alma1_hdco"
    #local images="--imagenames $results/line_spec_peak_vel.fits"
    #images="$images $results/line_moment1_1sigma.fits"
    #images="$images $results/line_moment1_2sigma.fits"
    #images="$images $results/line_moment1_5sigma.fits"
    #local config="$CFGS/p5_figures.cfg"
    #local figure="$FIGS/${FIELD}.config5.alma1.hdco.prog_moments.pdf"
    #$PLOTTER $preflags $config $figure plotmoments $posflags $images
    #local figure="$FIGS/${FIELD}.config5.alma1.hdco.prog_moments.HDCO.moments.pdf"
    #copy_to_paper $figure $1
    local preflags="--png"
    local config="$CFGS/multiplot_config5_hdco_prog_moments.cfg"
    local figure="$FIGS/${FIELD}.config5.alma1.hdco.prog_moments.pdf"
    $PLOTTER $preflags $config $figure multiplot
    copy_to_paper $figure $1
}

# Plot 13CO H2CO lines
function plot_line_examples () {
    local preflags="--png"
    local config="$CFGS/plot_13co_h2co_line.cfg"
    local figure="$FIGS/${FIELD}.config5.alma1.13co_h2co_line.pdf"
    $PLOTTER $preflags $config $figure multiplot
    copy_to_paper $figure $1

    echo $SEP
    config="$CFGS/plot_hdco_line.cfg"
    figure="$FIGS/${FIELD}.config5.alma1.hdco_line.pdf"
    $PLOTTER $preflags $config $figure multiplot
    copy_to_paper $figure "9"

    echo $SEP
    config="$CFGS/plot_acetone_line.cfg"
    figure="$FIGS/${FIELD}.config5.alma1.acetone_line.pdf"
    $PLOTTER $preflags $config $figure multiplot
}

# Plot models
function plot_models () {
    local preflags="--png"
    local config="$CFGS/multiplot_models.cfg"
    local figure="$FIGS/${FIELD}.config5.alma1.models.pdf"
    $PLOTTER $preflags $config $figure multiplot
    copy_to_paper $figure $1
}

# pv maps
function plot_pvmaps () {
    local lines=( "13CO" )
    local fig_config="${CFGS}/p5_figures.cfg"

    # Iterate over sources
    for src in ${SOURCES[@]}
    do
        if [[ ${src,,} == "alma3" ]]
        then
            continue
        fi

        # Get the maps
        #get_pv $src $FRSLT "$lines"
    done
    plot_pv $fig_config $FRSLT "$lines"

    cp ${FIGS}/G335.579-0.272.config5.alma1.13CO.pvmap_PA90.png ${PAPER}/fig8.pdf
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
        3 ) # CH3CN K=7
            plot_line_moments $1 "7";;
        4 ) # CH3CN K=4
            plot_line_moments $1 "4";;
        5 ) # 13CO and SiO lobes
            plot_split_lines $1;;
        6 ) # HDCO, acetone moments
            plot_hot_lines $1;;
        7 ) # 13CO H2CO lines, HDCO fig9
            plot_line_examples $1;;
        8 ) # 13CO pv map
            plot_pvmaps $1;;
        10 ) # HDCO velocity maps
            plot_hdco_velocities $1;;
        12 ) # models
            plot_models $1;;
        dm ) # Dust mass
            shift
            dust_mass $1;;
        vlsr ) # Fit vlsr
            shift
            fit_vlsr $1;;
        radius ) # calculate radius
            source_radius;;
    esac
    shift
done
