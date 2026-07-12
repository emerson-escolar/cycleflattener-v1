#!/usr/bin/env zsh


timeLimit=5
nSolve=3

# name of data folder (inside replication directory) and input name
FOLDER=C2_cylinder_2.0_1.0_500_019f4645-905d-7479-900d-ffd9195b399c
DATA=cylinder_2.0_1.0_500
RATIO=0.2

origDir=$(pwd)
echo $origDir

# replication directory and base project directory
replDir=$(dirname -- "$(readlink -f -- "$0")")
projectDir=$replDir/../
echo $projectDir

# change to base project directory
cd $projectDir

UUID=$(uv run -p 3.14 --no-project -m uuid -u uuid7)

for JJ in {1..100}; do
    for II in {1..2}; do
	optiOutDir=${replDir}/${FOLDER}/repeats_${UUID}/$(printf "%04d" $timeLimit)sec_${RATIO}ratio_trial$(printf %03d $JJ)_${II}
	echo "Writing to $optiOutDir"
	mkdir -p $optiOutDir
	uv run main.py -i $replDir/$FOLDER -o $optiOutDir -r $RATIO -c ./cplex_config_60s_mem_18deg.py -t $timeLimit -n $nSolve $DATA 2>&1 | tee $optiOutDir/output.log &
    done
    wait
done

wait

cd $origDir
