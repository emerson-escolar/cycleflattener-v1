#!/usr/bin/env bash

S1() {
    local NAME=slipper_2_1_1_20_20_10
    local TIME=1
    local NSOLVE=3

    # basic run
    ./experiment_slipper.sh --timeLimit ${TIME} --nSolve ${NSOLVE} --nouuid 20 20 10

    # collect results for basic runs
    local COLL=./${NAME}/${NAME}_collected.txt
    for tt in 0.1 0.2 0.4; do
	echo "**************************************************" >> ${COLL}
	echo ${tt} >> ${COLL}
	uv run cf_tabler ./${NAME}/${NAME}.txt ./${NAME}/$(printf "%04d" ${TIME})sec_${tt}ratio/${NAME}_0th_solutions_v2.json >> ${COLL}
    done

    # repeated runs. hardcoded to do 0.2
    ./experiment_repeated.sh --timeLimit ${TIME} --nSolve ${NSOLVE} --ratio 0.2 --nouuid ${NAME}/ ${NAME}
    uv run ./repeated_parser.py ./${NAME}/$(printf "%04d" ${TIME})sec_0.2ratio_repeats
}


S1
