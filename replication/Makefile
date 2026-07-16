
.PHONY: all
all: experiment_circle.sh-parsing.sh \
     experiment_cylinder.sh-parsing.sh \
     experiment_slipper.sh-parsing.sh \
     experiment_torus.sh-parsing.sh \
     experiment_doubletorus.sh-parsing.sh \
     experiment_repeated.sh-parsing.sh


%-parsing.sh: %-parsing.m4
	argbash --strip user-content $< -o $@
