#!/usr/bin/env bash

#S1

NAME=slipper_2_1_1_20_20_10
# ./experiment_slipper.sh --timeLimit 1 --nSolve 3 --nouuid 20 20 10
# ./experiment_repeated.sh --timeLimit 1 --nSolve 3 --ratio 0.2 --nouuid ${NAME}/ ${NAME}
# uv run ./repeated_parser.py ./${NAME}/0001sec_0.2ratio_repeats

COLL=./${NAME}/${NAME}_collected.txt

for tt in 0.1 0.2 0.4; do
    echo "**************************************************" >> ${COLL}
    echo ${tt} >> ${COLL}
    uv run cf_tabler ./${NAME}/${NAME}.txt ./${NAME}/0001sec_${tt}ratio/${NAME}_0th_solutions_v2.json >> ${COLL}
done
