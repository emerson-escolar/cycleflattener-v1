#!/bin/env bash

origDir=$(pwd)
echo $origDir

replDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
projectDir=$replDir/../
echo $projectDir

cd $projectDir

BS=20
FS=20
FR=10
DATA=slipper_2_1_1_$BS\_$FS\_$FR
echo $DATA

uv run ./tests/generate_testdata.py --bs $BS --fs $FS --fr $FR -o $replDir
optiperslp -e -z $replDir/$DATA/$DATA.txt -p $replDir/$DATA
uv run main.py -i $replDir/$DATA $DATA -c ./cplex_config_quick.py


cd $origDir
