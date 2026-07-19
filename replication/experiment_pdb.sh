#!/usr/bin/env bash

CODE=${1}
timeLimit=5
nSolve=20

# Setting directories.
origDir=$(pwd)

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
[ -e "${replDir}/experiment_common.sh" ] || exit 1
source "${replDir}/experiment_common.sh"

projectDir="${replDir}/../"

cd $projectDir
#

DATA=pdb_${CODE}

# data generation and optiperslp output should be deterministic.
UUID=$(uv run -p 3.14 --no-project -m uuid -u uuid7)
FOLDER=${DATA}
DATADIR="${replDir}/${FOLDER}"

if [ ! -f "${DATADIR}/${DATA}.txt" ]; then
    echo "${DATADIR}/${DATA}.txt not found; generating data..."
    uv run cf_generate_data pdb "${CODE}" -o "${DATADIR}"
else
    echo "${DATADIR}/${DATA}.txt found."
fi

run_experiments	"${DATADIR}" "${DATA}" "$timeLimit" "$nSolve"

cd $origDir
