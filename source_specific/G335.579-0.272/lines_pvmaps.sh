#!/bin/bash
#function get_pvmap () {
#    local script="python ~/Python/scripts/get_pvmaps.py"
#    $script $1 $2 $3
#}

function get_pv () {
    local script="$SCRIPTS/get_pvmaps.py"
    local src="$1"
    shift
    local rslt="$1"
    shift
    local flags="--invert --source ${CFGS}/source_${src,,}.cfg"
    #local flags="--source ${CFGS}/source_${src,,}.cfg"
    flags="$flags --pvconfig ${CFGS}/source_${src,,}_pv.cfg"

    # Run
    echo "PV map for: $src"
    for line in "$@"
    do
        echo "Line: $line"
        local lflags="$flags --config_section ${line}"
        lflags="$lflags --output ${rslt}/${FIELD}.${ARRAY}.${src,,}.${line}.pvmap.fits"
        $script $lflags
    done
}

function plot_pv () {
    local preflags="--png $1"
    local postflags="--section pvmap --selflevels"
    shift
    local rslt="$1"
    shift

    for line in "$@"
    do
        for fl in ${rslt}/*${line}.pvmap*
        do
            local figname="${FIGS}/config8_pv/$(basename $fl)"
            figname="${figname/.fits/.pdf}"
            echo "Plotting $fl"
            $PLOTTER $preflags $figname plotpvmaps $postflags $fl
        done
    done
}

