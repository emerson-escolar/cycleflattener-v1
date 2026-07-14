#!/usr/bin/env bash

# Created by argbash-init v2.11.0
# Run 'argbash --strip user-content "experiment_cylinder.sh-parsing.m4" -o "experiment_cylinder.sh-parsing.sh"' to generate the 'experiment_cylinder.sh-parsing.sh' file.
# If you need to make changes later, edit 'experiment_cylinder.sh-parsing.sh' directly, and regenerate by running
# 'argbash --strip user-content "experiment_cylinder.sh-parsing.sh" -o "experiment_cylinder.sh-parsing.sh"'
# script_dir="$(cd "$(dirname "$(readlink -e "${BASH_SOURCE[0]}")")" && pwd)"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "${script_dir}/experiment_cylinder.sh-parsing.sh" || { echo "Couldn't find 'experiment_cylinder.sh-parsing.sh' parsing library in the '$script_dir' directory"; exit 1; }

# vvv  PLACE YOUR CODE HERE  vvv
# For example:
printf 'Value of --%s: %s\n' 'timeLimit' "$_arg_timelimit"
printf 'Value of --%s: %s\n' 'nSolve' "$_arg_nsolve"
printf 'Value of --%s: %s\n' 'radius' "$_arg_radius"
printf 'Value of --%s: %s\n' 'height' "$_arg_height"
printf "Value of '%s': %s\\n" 'NUM' "$_arg_num"

NUM="$_arg_num"
RADIUS="$_arg_radius"
HEIGHT="$_arg_height"
timeLimit="$_arg_timelimit"
nSolve="$_arg_nsolve"

origDir=$(pwd)
echo $origDir

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
projectDir=$replDir/../
echo $projectDir

cd $projectDir

DATA=cylinder_${HEIGHT}_${RADIUS}_${NUM}

# data generation and optiperslp output should be deterministic.
UUID=$(uv run -p 3.14 --no-project -m uuid -u uuid7)
FOLDER=${DATA}_${UUID}
echo $FOLDER

if [ ! -f "$replDir/$FOLDER/$DATA.txt" ]; then
    echo "$replDir/$FOLDER/$DATA.txt not found; generating data..."
    uv run ./tests/generate_testdata.py cylinder --num $NUM --radius_str $RADIUS --height_str $HEIGHT -o $replDir/$FOLDER
else
    echo "$replDir/$FOLDER/$DATA.txt found."
fi

if [ ! -f "$replDir/$FOLDER/gen_${DATA}_alphamap.txt" ]; then
    echo "$replDir/$FOLDER/gen_${DATA}_alphamap.txt not found; applying optiperslp..."
    echo "saving to $replDir/$FOLDER"
    optiperslp -e -z -p $replDir/$FOLDER $replDir/$FOLDER/$DATA.txt
else
    echo "$replDir/$FOLDER/gen_$DATA_alphamap.txt found."
fi

# Hash output folders for different runs
# UUID version 7 was introduced in python 3.14...
# but cplex uses python 3.10
UUID=$(uv run -p 3.14 --no-project -m uuid -u uuid7)

if [[ "$(uname)" == "Darwin" ]]; then
    TIMESCRIPT=gtime
else
    TIMESCRIPT=/usr/bin/time
fi

for RATIO in 0.1 0.2 0.4
do
    optiOutDir=$replDir/$FOLDER/$(printf "%04d" $timeLimit)sec_${RATIO}ratio_$UUID
    mkdir $optiOutDir
    $TIMESCRIPT -v uv run main.py -i $replDir/$FOLDER -o $optiOutDir $DATA -r ${RATIO} -c ./cplex_config_60s_mem_18deg.py -t $timeLimit -n $nSolve 2>&1 | tee $optiOutDir/output.log
done

cd $origDir


# ^^^  TERMINATE YOUR CODE BEFORE THE BOTTOM ARGBASH MARKER  ^^^
