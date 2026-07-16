#!/usr/bin/env bash

# script_dir="$(cd "$(dirname "$(readlink -e "${BASH_SOURCE[0]}")")" && pwd)"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/experiment_slipper.sh-parsing.sh" || { echo "Couldn't find 'experiment_slipper.sh-parsing.sh' parsing library in the '$script_dir' directory"; exit 1; }

# vvv  PLACE YOUR CODE HERE  vvv
printf 'Value of --%s: %s\n' 'timeLimit' "$_arg_timelimit"
printf 'Value of --%s: %s\n' 'nSolve' "$_arg_nsolve"
printf "Value of '%s': %s\\n" 'BS' "$_arg_bs"
printf "Value of '%s': %s\\n" 'FS' "$_arg_fs"
printf "Value of '%s': %s\\n" 'FR' "$_arg_fr"

BS="$_arg_bs"
FS="$_arg_fs"
FR="$_arg_fr"


# Setting directories.
origDir=$(pwd)

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
[ -e "${replDir}/experiment_common.sh" ] || exit 1
source "${replDir}/experiment_common.sh"

projectDir="${replDir}/../"

cd $projectDir
#

DATA="slipper_2_1_1_${BS}_${FS}_${FR}"


# data generation
FOLDER="${DATA}"
DATADIR="${replDir}/${FOLDER}"

if [ ! -f "${DATADIR}/${DATA}.txt" ]; then
    echo "${DATADIR}/${DATA}.txt not found; generating data..."
    uv run ./tests/generate_testdata.py slipper --bs "$BS" --fs "$FS" --fr "$FR" -o "${DATADIR}"
    echo "${DATADIR}/${DATA}.txt generated."
else
    echo "${DATADIR}/${DATA}.txt found."
fi

run_experiments	"${DATADIR}" "${DATA}" "$_arg_timelimit" "$_arg_nsolve"

cd $origDir

# ^^^  TERMINATE YOUR CODE BEFORE THE BOTTOM ARGBASH MARKER  ^^^
