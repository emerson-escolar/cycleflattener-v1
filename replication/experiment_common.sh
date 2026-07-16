

run_experiments() {
    local DATADIR="$1"
    local DATA="$2"
    local timeLimit="$3"
    local nSolve="$4"

    if [ ! -f "${DATADIR}/gen_${DATA}_alphamap.txt" ]; then
	echo "${DATADIR}/gen_${DATA}_alphamap.txt not found; applying optiperslp..."
	optiperslp -e -z -p "$DATADIR" "${DATADIR}/${DATA}.txt" || exit 1
	echo "${DATADIR}/${DATA}.txt processed by optiperslp"
    else
	echo "${DATADIR}/gen_${DATA}_alphamap.txt found."
    fi

    # Hash output folders for different runs
    # UUID version 7 was introduced in python 3.14...
    # but cplex uses python 3.10
    local UUID="$(uv run -p 3.14 --no-project -m uuid -u uuid7)"

    if [[ "$(uname)" == "Darwin" ]]; then
	TIMESCRIPT=gtime
    else
	TIMESCRIPT=/usr/bin/time
    fi

    for RATIO in 0.1 0.2 0.4; do
	optiOutDir="${DATADIR}/$(printf "%04d" ${timeLimit})sec_${RATIO}ratio_${UUID}"
	mkdir -p "${optiOutDir}"
	${TIMESCRIPT} -v uv run main.py -i "${DATADIR}" -o "${optiOutDir}" "${DATA}" -r "${RATIO}" -c ./cplex_config_60s_mem_18deg.py -t "${timeLimit}" -n "${nSolve}" 2>&1 | tee "${optiOutDir}/output.log"
    done
}
