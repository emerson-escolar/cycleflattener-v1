#!/usr/bin/env bash

CODE=${1}
timeLimit=5
nSolve=20

origDir=$(pwd)
echo $origDir

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
projectDir=$replDir/../
echo $projectDir

cd $projectDir

DATA=pdb_${CODE}

# data generation and optiperslp output should be deterministic.
UUID=$(uv run -p 3.14 --no-project -m uuid -u uuid7)
FOLDER=${DATA}
echo $FOLDER

if [ ! -f "$replDir/$FOLDER/$DATA.txt" ]; then
    echo "$replDir/$FOLDER/$DATA.txt not found; generating data..."
    uv run ./tests/generate_testdata.py pdb $CODE -o $replDir/$FOLDER
else
    echo "$replDir/$FOLDER/$DATA.txt found."
fi

if [ ! -f "$replDir/$FOLDER/gen_${DATA}_alphamap.txt" ]; then
    echo "$replDir/$FOLDER/gen_${DATA}_alphamap.txt not found; applying optiperslp..."
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
