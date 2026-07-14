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
printf "Value of '%s': %s\\n" 'DIR' "$_arg_dir"
printf "Value of '%s': %s\\n" 'DATANAME' "$_arg_dataname"

timeLimit="$_arg_timelimit"
nSolve="$_arg_nsolve"
RATIO="$_arg_ratio"
DIR="$_arg_dir"
DATANAME="$_arg_dataname"

# name of data folder (inside replication directory) and input name
# FOLDER=C2_cylinder_2.0_1.0_500_019f4645-905d-7479-900d-ffd9195b399c
# DATA=cylinder_2.0_1.0_500

# FOLDER=slipper_2_1_1_30_30_20
# DATA=slipper_2_1_1_30_30_20

# FOLDER=S1_slipper_2_1_1_20_20_10
# DATA=slipper_2_1_1_20_20_10

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
projectDir=$replDir/../

UUID=$(uv run -p 3.14 --no-project -m uuid -u uuid7)

for JJ in {1..100}; do
    for II in {1..2}; do
	optiOutDir=${DIR}/repeats_${UUID}/$(printf "%04d" $timeLimit)sec_${RATIO}ratio_trial$(printf %03d $JJ)_${II}
	echo "Writing to $optiOutDir"
	mkdir -p $optiOutDir
	uv run $projectDir/main.py -i $DIR -o $optiOutDir -r $RATIO -c ./cplex_config_60s_mem_18deg.py -t $timeLimit -n $nSolve $DATANAME 2>&1 | tee $optiOutDir/output.log &
    done
    wait
done

wait



# ^^^  TERMINATE YOUR CODE BEFORE THE BOTTOM ARGBASH MARKER  ^^^
