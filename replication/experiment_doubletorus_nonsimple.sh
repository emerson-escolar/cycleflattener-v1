#!/usr/bin/env bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/experiment_doubletorus.sh-parsing.sh" || { echo "Couldn't find 'experiment_doubletorus.sh-parsing.sh' parsing library in the '$script_dir' directory"; exit 1; }

# vvv  PLACE YOUR CODE HERE  vvv
printf 'Value of --%s: %s\n' 'timeLimit' "$_arg_timelimit"
printf 'Value of --%s: %s\n' 'nSolve' "$_arg_nsolve"
printf 'Value of --%s: %s\n' 'radius' "$_arg_radius"
printf 'Value of --%s: %s\n' 'tuberadius' "$_arg_tuberadius"
printf 'Value of --%s: %s\n' 'nouuid' "$_arg_nouuid"
printf "Value of '%s': %s\\n" 'NUM' "$_arg_num"

NUM="$_arg_num"


# Setting directories.
origDir=$(pwd)

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
[ -e "${replDir}/experiment_common.sh" ] || exit 1
source "${replDir}/experiment_common.sh"

projectDir="${replDir}/../"

cd $projectDir
#

DATA="solid_doubletorus_${_arg_radius}_${_arg_tuberadius}_${NUM}"


# data generation
if [ "$_arg_nouuid" = off ]; then
    UUID="_$(uv run -p 3.14 --no-project -m uuid -u uuid7)"
else
    UUID=""
fi
FOLDER=${DATA}${UUID}
DATADIR="${replDir}/${FOLDER}"

if [ ! -f "${DATADIR}/${DATA}.txt" ]; then
    echo "${DATADIR}/${DATA}.txt not found; generating data..."
    uv run cf_generate_data doubletorus --num "${NUM}" --radius_str "${_arg_radius}" --tube_radius_str "${_arg_tuberadius}" -o "${DATADIR}"
    echo "${DATADIR}/${DATA}.txt generated."
else
    echo "${DATADIR}/${DATA}.txt found."
fi

run_experiments_nonsimple "${DATADIR}" "${DATA}" "$_arg_timelimit" "$_arg_nsolve" "${UUID}"

cd $origDir


# ^^^  TERMINATE YOUR CODE BEFORE THE BOTTOM ARGBASH MARKER  ^^^
