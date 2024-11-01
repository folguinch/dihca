#!/bin/bash
readonly SEP="========================================"
if [[ "$HOSTNAME" == "venus" ]]; then
  readonly DATA="/home/data/share/binary_project"
else
  readonly DATA="/data/share/binary_project"
fi
readonly CATALOGUES="${DATA}/catalogue"

#######################################
# Defines the SB directory.
# Globals:
#   DATA
# Arguments:
#   The SB name.
# Returns:
#   Defines the global variable SBDIR.
#######################################
function sb_dir() {
  declare -g SBDIR
  case "$1" in
    G333_G335 | IRAS_18089 | IRAS_18182)
      SBDIR="/home/myso/share/binary_project/$1"
      ;;
    *)
      SBDIR="${DATA}/$1"
      ;;
  esac
}

#######################################
# Iterate over sources in input file.
# Globals:
#   HOME
#   SBDIR
# Arguments:
#   The catalogue file name.
#######################################
function iter_sources() {
  local cmd="python ${HOME}/python_devel/line_little_helper/spectrum_helper.py"
  local catname="$(basename $1)"
  local sbname="${catname/_catalogue_extended.csv/}"
  local line field src_number radec radius res_dir plot_file aux cube specfile
  local -a lines
  local -a row
  local -a flags
  local -a cubes

  # Define SB directory
  echo "SB name: ${sbname}"
  sb_dir "${sbname}"

  # Iterate over lines
  readarray -s 1 lines < $1
  for line in "${lines[@]}"; do
    # Separate fields
    row=( ${line//,/ } )
    field="${row[0]}"
    src_number="${row[1]}"
    radec="${row[@]:2:2}"
    radius="${row[4]}"
    echo "Field: ${field} ALMA${src_number}"

    # Cubes
    aux="${SBDIR}/${field}/final_data/config5"
    if [[ ! -d "$aux" ]]; then
      echo "Moving directories"
      mv "${SBDIR}/${field}/clean" "${SBDIR}/${field}/final_data"
      mkdir "${aux}"
      mv ${SBDIR}/${field}/final_data/*.{fits,image} "${aux}"
    fi
    cubes=( ${aux}/*.fits )

    for cube in "${cubes[@]}"; do
      # Make results directory
      res_dir="${SBDIR}/${field}/results_final/config5/specs"
      if [[ ! -d "$res_dir" ]]; then
        echo "Creating directory: ${res_dir}"
        mkdir -p "${res_dir}"
      fi

      # Plot and original spectrum file
      plot_file="$(basename ${cube})"
      specfile="${res_dir}/${plot_file/.image.fits/.image_spec0.dat}"
      plot_file="${res_dir}/${plot_file/.image.fits/.spec.png}"
      plot_file="${plot_file/.config5./.ALMA${src_number}.}"


      # Run spectrum extractor
      flags=( --coordinate "${radec}" "icrs" --radius "${radius}" "arcsec"
              --plot "${plot_file}" )
      if [[ -e "${plot_file/.spec.png/.spec.dat}" ]]; then
        specfile="${plot_file/.spec.png/.spec.dat}"
        echo "Working on spectrum: ${specfile}"
        $cmd "${specfile}" "${flags[@]}"
      else
        flags+=( --outdir "${res_dir}" )
        echo "Working on cube: ${cube}"
        $cmd "${cube}" "${flags[@]}"
        mv ${specfile} "${plot_file/.spec.png/.spec.dat}"
      fi
      exit
    done
  done
}

# Main
for catalogue in ${CATALOGUES}/*[0-9]*_catalogue_extended.csv; do
  echo "Working on catalogue: ${catalogue}"
  iter_sources "${catalogue}"
  echo "$SEP"
  break
done
