#!/usr/bin/env bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/experiment_cylinder.sh-parsing.sh" || { echo "Couldn't find 'experiment_cylinder.sh-parsing.sh' parsing library in the '$script_dir' directory"; exit 1; }

# vvv  PLACE YOUR CODE HERE  vvv
printf 'Value of --%s: %s\n' 'timeLimit' "$_arg_timelimit"
printf 'Value of --%s: %s\n' 'nSolve' "$_arg_nsolve"
printf 'Value of --%s: %s\n' 'radius' "$_arg_radius"
printf 'Value of --%s: %s\n' 'height' "$_arg_height"
printf "Value of '%s': %s\\n" 'NUM' "$_arg_num"

NUM="$_arg_num"
RADIUS="$_arg_radius"
HEIGHT="$_arg_height"


# Setting directories.
origDir=$(pwd)

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
[ -e "${replDir}/experiment_common.sh" ] || exit 1
source "${replDir}/experiment_common.sh"

projectDir="${replDir}/../"

cd $projectDir
#

DATA=cylinder_${HEIGHT}_${RADIUS}_${NUM}


# data generation
UUID="$(uv run -p 3.14 --no-project -m uuid -u uuid7)"
FOLDER="${DATA}_${UUID}"
DATADIR="${replDir}/${FOLDER}"

if [ ! -f "${DATADIR}/${DATA}.txt" ]; then
    echo "${DATADIR}/${DATA}.txt not found; generating data..."
    uv run cf_generate_data cylinder --num "$NUM" --radius_str "$RADIUS" --height_str "$HEIGHT" -o "${DATADIR}"
    echo "${DATADIR}/${DATA}.txt generated."
else
    echo "${DATADIR}/${DATA}.txt found."
fi

run_experiments	"${DATADIR}" "${DATA}" "$_arg_timelimit" "$_arg_nsolve"

cd $origDir


# ^^^  TERMINATE YOUR CODE BEFORE THE BOTTOM ARGBASH MARKER  ^^^
