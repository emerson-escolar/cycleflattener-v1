#!/usr/bin/env bash

# Created by argbash-init v2.11.0
# Run 'argbash --strip user-content "experiment_repeated.sh-parsing.m4" -o "experiment_repeated.sh-parsing.sh"' to generate the 'experiment_repeated.sh-parsing.sh' file.
# If you need to make changes later, edit 'experiment_repeated.sh-parsing.sh' directly, and regenerate by running
# 'argbash --strip user-content "experiment_repeated.sh-parsing.sh" -o "experiment_repeated.sh-parsing.sh"'
# script_dir="$(cd "$(dirname "$(readlink -e "${BASH_SOURCE[0]}")")" && pwd)"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/experiment_repeated.sh-parsing.sh" || { echo "Couldn't find 'experiment_repeated.sh-parsing.sh' parsing library in the '$script_dir' directory"; exit 1; }

# vvv  PLACE YOUR CODE HERE  vvv
# For example:
printf 'Value of --%s: %s\n' 'timeLimit' "$_arg_timelimit"
printf 'Value of --%s: %s\n' 'nSolve' "$_arg_nsolve"
printf 'Value of --%s: %s\n' 'ratio' "$_arg_ratio"
printf 'Value of --%s: %s\n' 'nRepeat' "$_arg_nrepeat"
printf 'Value of --%s: %s\n' 'nParallel' "$_arg_nparallel"
printf 'Value of --%s: %s\n' 'nouuid' "$_arg_nouuid"
printf "Value of '%s': %s\\n" 'DIR' "$_arg_dir"
printf "Value of '%s': %s\\n" 'DATANAME' "$_arg_dataname"

timeLimit="$_arg_timelimit"
nSolve="$_arg_nsolve"
RATIO="$_arg_ratio"
DIR="$_arg_dir"
DATANAME="$_arg_dataname"


replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
projectDir=$replDir/../

if [ "$_arg_nouuid" = off ]; then
    UUID="_$(uv run -p 3.14 --no-project -m uuid -u uuid7)"
else
    UUID=""
fi


for ((JJ=1; JJ<=$_arg_nrepeat; JJ++)); do
    for ((II=1; II<=$_arg_nparallel; II++)); do
	optiOutDir="${DIR}/$(printf "%04d" ${timeLimit})sec_${RATIO}ratio_repeats${UUID}/$(printf "%04d" $timeLimit)sec_${RATIO}ratio_trial$(printf %03d $JJ)_${II}"
	echo "Writing to ${optiOutDir}"
	mkdir -p "${optiOutDir}"
	uv run -m cycleflattener --nolp -i "${DIR}" -o "${optiOutDir}" -r "${RATIO}" -c ./cplex_config_60s_mem_18deg.py -t "${timeLimit}" -n "${nSolve}" "${DATANAME}" 2>&1 | tee $optiOutDir/output.log &
    done
    wait
done

wait



# ^^^  TERMINATE YOUR CODE BEFORE THE BOTTOM ARGBASH MARKER  ^^^
