

run_experiments() {
    local DATADIR="$1"
    local DATA="$2"
    local timeLimit="$3"
    local nSolve="$4"
    local UUID="$5"

    if [ ! -f "${DATADIR}/gen_${DATA}_alphamap.txt" ]; then
	echo "${DATADIR}/gen_${DATA}_alphamap.txt not found; applying optiperslp..."
	optiperslp -e -z -p "$DATADIR" "${DATADIR}/${DATA}.txt" || exit 1
	echo "${DATADIR}/${DATA}.txt processed by optiperslp"
    else
	echo "${DATADIR}/gen_${DATA}_alphamap.txt found."
    fi

    if [[ "$(uname)" == "Darwin" ]]; then
	TIMESCRIPT=gtime
    else
	TIMESCRIPT=/usr/bin/time
    fi

    for RATIO in 0.1 0.2 0.4; do
	optiOutDir="${DATADIR}/$(printf "%04d" ${timeLimit})sec_${RATIO}ratio${UUID}"
	mkdir -p "${optiOutDir}"
	${TIMESCRIPT} -v uv run -m cycleflattener -i "${DATADIR}" -o "${optiOutDir}" -r "${RATIO}" -c ./cplex_config_60s_mem_18deg.py -t "${timeLimit}" -n "${nSolve}" "${DATA}" 2>&1 | tee "${optiOutDir}/output.log"
    done
}




run_experiments_nonsimple() {
    local DATADIR="$1"
    local DATA="$2"
    local timeLimit="$3"
    local nSolve="$4"
    local UUID="$5"

    if [ ! -f "${DATADIR}/gen_${DATA}_alphamap.txt" ]; then
	echo "${DATADIR}/gen_${DATA}_alphamap.txt not found; applying optiperslp..."
	optiperslp -e -z -p "$DATADIR" "${DATADIR}/${DATA}.txt" || exit 1
	echo "${DATADIR}/${DATA}.txt processed by optiperslp"
    else
	echo "${DATADIR}/gen_${DATA}_alphamap.txt found."
    fi

    if [[ "$(uname)" == "Darwin" ]]; then
	TIMESCRIPT=gtime
    else
	TIMESCRIPT=/usr/bin/time
    fi

    for RATIO in 0.1; do
	optiOutDir="${DATADIR}/$(printf "%04d" ${timeLimit})sec_${RATIO}ratio${UUID}"
	mkdir -p "${optiOutDir}"
	${TIMESCRIPT} -v uv run cf_aohcp_nonsimple -i "${DATADIR}" -o "${optiOutDir}" -r "${RATIO}" -c ./cplex_config_60s_mem_18deg.py -t "${timeLimit}" -n "${nSolve}" "${DATA}" 2>&1 | tee "${optiOutDir}/output.log"
    done
}
