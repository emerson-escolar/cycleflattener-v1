
.PHONY: all
all: experiment_circle.sh-parsing.sh experiment_cylinder.sh-parsing.sh


experiment_circle.sh-parsing.sh: experiment_circle.sh-parsing.m4
	argbash --strip user-content "experiment_circle.sh-parsing.m4" -o "experiment_circle.sh-parsing.sh"


experiment_cylinder.sh-parsing.sh: experiment_cylinder.sh-parsing.m4
	argbash --strip user-content "experiment_cylinder.sh-parsing.m4" -o "experiment_cylinder.sh-parsing.sh"
