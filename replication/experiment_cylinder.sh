#!/bin/env bash

NUM=300
RADIUS=1.0
HEIGHT=2.0
timeLimit=5
nSolve=20

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
    uv run ./tests/generate_testdata.py cylinder --num $NUM --radius $RADIUS --height $HEIGHT -o $replDir/$FOLDER
else
    echo "$replDir/$FOLDER/$DATA.txt found."
fi

if [ ! -f "$replDir/$FOLDER/gen_${DATA}_alphamap.txt" ]; then
    echo "$replDir/$FOLDER/gen_${DATA}_alphamap.txt not found; applying optiperslp..."
    optiperslp -e -z $replDir/$FOLDER/$DATA.txt -p $replDir/$FOLDER
else
    echo "$replDir/$FOLDER/gen_$DATA_alphamap.txt found."
fi

# Hash output folders for different runs
# UUID version 7 was introduced in python 3.14...
# but cplex uses python 3.10
UUID=$(uv run -p 3.14 --no-project -m uuid -u uuid7)

for RATIO in 0.1 0.2 0.4
do
    optiOutDir=$replDir/$FOLDER/$(printf "%04d" $timeLimit)sec_${RATIO}ratio_$UUID
    mkdir $optiOutDir
    /usr/bin/time -v uv run main.py -i $replDir/$FOLDER -o $optiOutDir $DATA -r ${RATIO} -c ./cplex_config_60s_mem_18deg.py -t $timeLimit -n $nSolve 2>&1 | tee $optiOutDir/output.log
done

cd $origDir
