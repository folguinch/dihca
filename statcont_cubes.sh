declare -a molecules sources
declare src base wkdir cwdir per_hmc mol cube link_name fname
molecules=( "CH3OH" "CH3CN" )
sources=( "G10.62-0.38" "G11.1-0.12" "G11.92-0.61" "G14.22-0.50_S" "G24.60+0.08"
          "G29.96-0.02" "G333.12-0.56"  "G333.23-0.06" "G333.46-0.16"
          "G335.579-0.272" "G335.78+0.17" "G336.01-0.82" "G34.43+0.24"
          "G34.43+0.24MM2" "G343.12-0.06" "G35.03+0.35_A" "G35.13-0.74"
          "G35.20-0.74_N" "G351.77-0.54" "G5.89-0.37" "IRAS_165623959"
          "IRAS_180891732" "IRAS_181511208" "IRAS_18182-1433" "IRAS_18337-0743"
          "IRDC_182231243" "NGC6334I" "NGC_6334_I_N" "W33A" )
base="/Volumes/Pegasus32 R8/dihca/results"
wkdir="${base}/statcont"
cwkdir=$(pwd)

echo "Changing to ${wkdir}"
cd "${wkdir}"

for src in "${sources[@]}"; do
  echo "================================================================================"
  echo "Working on source ${src}"
  per_hmc="${base}/${src}/c5c8/per_hot_core"
  for mol in "${molecules[@]}"; do
    for cube in "${per_hmc}"/*"${mol}"*.subcube.fits; do
      if [[ -f $cube ]]; then
        echo "--------------------------------------------------------------------------------"
        echo "Working on cube ${cube}"
        fname=$(basename "$cube")
        fname="${src}_${fname}"
        link_name="${wkdir}/data/${fname}"
        if [[ -L ${link_name} ]]; then
          echo "Link available"
        else
          echo "Creating link: ${link_name}"
          ln -s "${cube}" "${link_name}"
        fi
        statcont -i "${fname%.*}" --continuum -n 0.002
      fi
    done
  done
done

echo "Changing back to ${cwkdir}"
cd "${cwkdir}"
