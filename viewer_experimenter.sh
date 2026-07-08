#!/usr/bin/env bash

uv run main.py -i ./tests/testdata/cylinder/ -o ./tests/testdata/cylinder-out -r 0.1 -c ./cplex_config_60s_mem_18deg.py -t 2 -n 2 cylinder_2.0_1.0_300
