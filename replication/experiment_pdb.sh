#!/usr/bin/env bash


script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/experiment_pdb.sh-parsing.sh" || { echo "Couldn't find 'experiment_pdb.sh-parsing.sh' parsing library in the '$script_dir' directory"; exit 1; }

# vvv  PLACE YOUR CODE HERE  vvv
printf 'Value of --%s: %s\n' 'timeLimit' "$_arg_timelimit"
printf 'Value of --%s: %s\n' 'nSolve' "$_arg_nsolve"
printf 'Value of --%s: %s\n' 'CODE' "$_arg_code"

# Setting directories.
origDir=$(pwd)

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
[ -e "${replDir}/experiment_common.sh" ] || exit 1
source "${replDir}/experiment_common.sh"

projectDir="${replDir}/../"

cd $projectDir
#

DATA="pdb_${_arg_code}"

# data generation and optiperslp output should be deterministic.
UUID=$(uv run -p 3.14 --no-project -m uuid -u uuid7)
FOLDER=${DATA}
DATADIR="${replDir}/${FOLDER}"

if [ ! -f "${DATADIR}/${DATA}.txt" ]; then
    echo "${DATADIR}/${DATA}.txt not found; generating data..."
    uv run cf_generate_data pdb "${_arg_code}" -o "${DATADIR}"
else
    echo "${DATADIR}/${DATA}.txt found."
fi

run_experiments	"${DATADIR}" "${DATA}" "$_arg_timelimit" "$_arg_nsolve"

cd $origDir
