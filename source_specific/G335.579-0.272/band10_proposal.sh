#!/usr/bin/bash
#set +e
################################################################################
################################################################################
# Globals                                                                      #
################################################################################
################################################################################
FIELD="G335.579-0.272"
FIGS="$HOME/Documents/Proposals/2021_ALMA/G335_band10/figures"
IMGS="../clean"
SBCB="${IMGS}/subcubes"
CFGS="../configs"
RSLT="../results_interim/config8"
DIRTY="../dirty"
PAPER="${HOME}/Documents/Papers/P6/figures"
PLOTTER="python2 ${HOME}/Python/plotter/plotter.py"
SCRIPTS="python2 ${HOME}/Python/scripts"
GOCO="${HOME}/Python/GoContinuum/"
SOURCE="ALMA1"
ARRAY="config8"
VLSR="-46.9 km/s"
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
    local config="$CFGS/band10_proposal_figure_continuum_alma1.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.${SOURCE}.pdf"
    $PLOTTER $preflag $config $figure multiplot
}

# Plot CH3CN k-ladder
function plot_ch3cn_kladder () {
    local preflag="--png"
    local suffix="config8.alma1.ch3cn_ladder.continuum"
    local config="$CFGS/multiplot_config8_figure_ch3cn_kladder.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.pdf"
    $PLOTTER $preflag $config $figure multiplot
    copy_to_paper $figure $1
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
    local preflag="--png"
    local config="$CFGS/multiplot_config8_ch3cn_moments_${SOURCE,,}.cfg"
    local figure="$FIGS/${FIELD}.${suffix}.${SOURCE}.subcube.moments.pdf"
    if [[ -e $config ]]
    then
        $PLOTTER $preflag $config $figure multiplot
    fi

    copy_to_paper $figure "${1}"
}

function plot_line_moments () {
    local cubename="$IMGS/${FIELD}.${ARRAY}.spw3.partial11.cube.image.fits"
    local linetags=( "ch3cn_k8" "hdco" "13co" "glycine" "vinyl_cyanide" "cyanoacetylene" "glycolaldehyde")
    local chanwidths=( "7" "7" "3" "5" "5" "7" "7")
    local freqs=( "220.47580720" "220.02940780" "220.39868420" "219.52028560" "219.40058460" "219.67465000" "219.911720")
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
            symmetric_moments "chan_halfwidth" $aux
        fi

        # Plot
        local preflag="--png"
        local config="$CFGS/multiplot_config8_${linetags[$i]}_moments_${SOURCE,,}.cfg"
        local figure="$FIGS/${FIELD}.${suffix}.${SOURCE}.subcube.moments.pdf"
        if [[ -e $config ]]
        then
            $PLOTTER $preflag $config $figure multiplot
        fi
    done
}

function plot_pvmaps () {
    local lines=( "CH2CHCN_23_4_19-22_4_18" "CH2CHCN_23_10_13-22_10_12" 
                  "CH2CHCN_23_8_15-22_8_14" "CH2CHCN_26_2_25-26_1_26" 
                  "CH2CHCN_23_2_22-22_2_21" "CH3CH2CHO_35_4_31-35_4_32"
                  "CH3_2CO_19_3_16-18_4_15EE" "CH3_2CO_19_4_16-18_3_15AA")
    local sources=( "alma1a" "alma1b" )
    local fig_config="${CFGS}/figures_pvmaps_${ARRAY}.cfg"

    #for src in ${sources[@]}; do
    #    get_pv $src $RSLT "${lines[@]}"
    #done
    #plot_pv $fig_config $RSLT "${lines[@]}"

    # Channel maps
    local figconfig="${CFGS}/plot_config8_spw2_chanmaps.cfg"
    local lineconfig="${CFGS}/lines_config8_spw2.cfg"
    local figname="${FIGS}/config8_chanmaps/${FIELD}.${ARRAY}.selfcal.contsub.spw2.alma1.png"
    local cubename="$DIRTY/${FIELD}.${ARRAY}.selfcal.contsub.spw2.robust2.0.image.fits"
    local clinps=( "--vlsr" "-46.9"  "--lines" )
    $PLOTTER  $figconfig $figname chanmap "${clinps[@]}" "${lines[@]}" "--lineconfig" "$lineconfig" $cubename
}

# Plot inverse p-Cygni lines
function plot_pcyg_profile () {
    local config="$CFGS/plot_13co_ch3cn_line.cfg"
    local figure="$FIGS/${FIELD}.config8.alma1.13co_ch3cn_line.png"
    $PLOTTER $config $figure multiplot
}

# Additional moments
function special_moments () {
    local freq_ranges=( "218.326307-218.343466-GHz" "218.310352-218.32420-GHz"  
                        "218.228169-218.239006-GHz" "217.915191-217.927533-GHz"
                        "217.765375-217.783437-GHz" "217.220197-217.231335-GHz"
                        "217.074796-217.082924-GHz" )
    local cubename="$DIRTY/${FIELD}.${ARRAY}.selfcal.contsub.spw2.robust2.0.image.fits"
    local outdir="$RSLT/special_moments/"
    if [[ ! -d $outdir ]]; then
      mkdir -p $outdir
    fi

    for freq_range in ${freq_ranges[@]}; do
      local suffix="${ARRAY}.${freq_range}"

      # Calculate moments
      local outname="${outdir}/${FIELD}.${suffix}.${SOURCE}"
      local aux="${freq_range//-/ }"
      aux="$aux $cubename $outname 0 1 2"
      echo "$SEP"
      echo "SOURCE: ${SOURCE}"
      if [[ ! -e "${outname}.subcube.moment0.fits" ]]
      then
          symmetric_moments "freq_range" $aux
      fi
    done

    # Plot
    #local preflag="--png"
    local config="$CFGS/plot_config8_special_moments_${SOURCE,,}.cfg"
    local figdir="$FIGS/experimental"
    local figure="$figdir/${FIELD}.special_moments.${SOURCE}.subcube.moments.png"
    if [[ -e $config ]]
    then
        $PLOTTER $preflag $config $figure multiplot
    fi
}

function vinyl_cyanide_spw2 () {
    local freq_ranges=( "218.637607-218.657977-GHz" "218.541117-218.567385-GHz"
                        "218.446681-218.464130-GHz" "218.344953-218.367422-GHz"
                        "217.520379-217.540700-GHz" )
    local cubename="$DIRTY/${FIELD}.${ARRAY}.selfcal.contsub.spw2.robust2.0.image.fits"
    local outdir="$RSLT/special_moments_vinyl_cyanide/"
    if [[ ! -d $outdir ]]; then
      mkdir -p $outdir
    fi

    for freq_range in ${freq_ranges[@]}; do
      local suffix="${ARRAY}.${freq_range}"

      # Calculate moments
      local outname="${outdir}/${FIELD}.${suffix}.${SOURCE}"
      local aux="${freq_range//-/ }"
      aux="$aux $cubename $outname 0 1 2"
      echo "$SEP"
      echo "SOURCE: ${SOURCE}"
      if [[ ! -e "${outname}.subcube.moment0.fits" ]]
      then
          symmetric_moments "freq_range" $aux
      fi
    done

    # Plot
    #local preflag="--png"
    local config="$CFGS/plot_config8_special_moments_vinyl_cyanide_spw2_${SOURCE,,}.cfg"
    local figdir="$FIGS/experimental"
    local figure="$figdir/${FIELD}.special_moments_vinyl_cyanide_spw2.${SOURCE}.subcube.moments.png"
    if [[ -e $config ]]
    then
        $PLOTTER $preflag $config $figure multiplot
    fi
}

function single_peaked_spw2 () {
    local freq_ranges=( "218.367587-218.385429-GHz" "217.050569-217.060481-GHz" 
                        "217.096240-217.110052-GHz" )
    local cubename="$DIRTY/${FIELD}.${ARRAY}.selfcal.contsub.spw2.robust2.0.image.fits"
    local outdir="$RSLT/special_moments_single_peaked/"
    if [[ ! -d $outdir ]]; then
      mkdir -p $outdir
    fi

    for freq_range in ${freq_ranges[@]}; do
      local suffix="${ARRAY}.${freq_range}"

      # Calculate moments
      local outname="${outdir}/${FIELD}.${suffix}.${SOURCE}"
      local aux="${freq_range//-/ }"
      aux="$aux $cubename $outname 0 1 2"
      echo "$SEP"
      echo "SOURCE: ${SOURCE}"
      if [[ ! -e "${outname}.subcube.moment0.fits" ]]
      then
          symmetric_moments "freq_range" $aux
      fi
    done

    # Plot
    #local preflag="--png"
    local config="$CFGS/plot_config8_special_moments_single_peaked_spw2_${SOURCE,,}.cfg"
    local figdir="$FIGS/experimental"
    local figure="$figdir/${FIELD}.special_moments_single_peaked_spw2.${SOURCE}.subcube.moments.png"
    if [[ -e $config ]]
    then
        $PLOTTER $preflag $config $figure multiplot
    fi
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
            plot_ch3cn_kladder $1;;
        3 ) # CH3CN K=8 moment
            plot_ch3cn_moments $1 ;;
        moms ) # Moments of few lines
            plot_line_moments ;;
        pvs ) # pv maps of few lines
            plot_pvmaps ;;
        pcyg ) # p-cygni profiles
            plot_pcyg_profile ;;
        special ) # additional moments
            special_moments ;;
        special_vinyl ) # additional moments
            vinyl_cyanide_spw2 ;;
        special_single ) # additional moments
            single_peaked_spw2 ;;
    esac
    shift
done

