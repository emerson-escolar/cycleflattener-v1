
.PHONY: all
all: experiment_circle.sh-parsing.sh \
     experiment_cylinder.sh-parsing.sh \
     experiment_slipper.sh-parsing.sh \
     experiment_repeated.sh-parsing.sh


experiment_circle.sh-parsing.sh: experiment_circle.sh-parsing.m4
	argbash --strip user-content "experiment_circle.sh-parsing.m4" -o "experiment_circle.sh-parsing.sh"


experiment_cylinder.sh-parsing.sh: experiment_cylinder.sh-parsing.m4
	argbash --strip user-content "experiment_cylinder.sh-parsing.m4" -o "experiment_cylinder.sh-parsing.sh"


experiment_slipper.sh-parsing.sh: experiment_slipper.sh-parsing.m4
	argbash --strip user-content "experiment_slipper.sh-parsing.m4" -o "experiment_slipper.sh-parsing.sh"


experiment_repeated.sh-parsing.sh: experiment_repeated.sh-parsing.m4
	argbash --strip user-content "experiment_repeated.sh-parsing.m4" -o "experiment_repeated.sh-parsing.sh"
