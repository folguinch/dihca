#!/bin/bash
set -e
################################################################################
################################################################################
# Globals                                                                      #
################################################################################
################################################################################
#LINES_SPW0="acetone41EE acetone10-9EA"
LINES_SPW1="acetone54-54AE"
#LINES_SPW2="hc3n_24-23 g-ethanol"
#LINES_SPW3="acetone21-20EE acetone21-20AE"
#LINES_SPW3="HDCO"
FIELD="G335.579-0.272"
CFGS="../configs"
RSLT="../results"
IMGS="../clean"
FIGS="../figures"
FIGCONFIG="$CFGS/line_figures.cfg"
PLOTTER="python ${HOME}/Python/plotter/plotter.py"

################################################################################
################################################################################
# Functions                                                                    #
################################################################################
################################################################################
function plot_line_moments () {
    local spw=$1
    shift
    local lineconfig="$CFGS/lines_${spw}.cfg"
    local preflags="--png --detailaxlabel --shape 2 2"
    local figure="$FIGS/${FIELD}.config5.pdf"
    local postflags="--section line_moments"
    local lines="--lineconfig $lineconfig --lines $@"
    local moments="--momentbase $RSLT/${FIELD}.config5"
    moments="$moments --moments 0 1 1 2"
    local sources="--atsources $CFGS/source_alma1.cfg"
    sources="$sources $CFGS/source_alma1.cfg $CFGS/source_alma3.cfg"
    sources="$sources $CFGS/source_alma1.cfg"
    local cubename="--cubename $IMGS/${FIELD}.config5.${spw}.fits"
    local postargs="$postflags $lines $moments $sources $cubename"

    $PLOTTER $preflags $FIGCONFIG $figure plotmoments $postargs
}

################################################################################
################################################################################
# Main                                                                         #
################################################################################
################################################################################
# spw0
if [[ -n "$LINES_SPW0" ]]
then
    plot_line_moments "spw0" $LINES_SPW0
fi

# spw1
if [[ -n "$LINES_SPW1" ]]
then
    plot_line_moments "spw1" $LINES_SPW1
fi

# spw2
if [[ -n "$LINES_SPW2" ]]
then
    plot_line_moments "spw2" $LINES_SPW2
fi

# spw3
if [[ -n "$LINES_SPW3" ]]
then
    plot_line_moments "spw3" $LINES_SPW3
fi

