import numpy as np

# context.cplex_parameters.preprocessing.qtolin.set(1)
context.cplex_parameters.timelimit = 15 # in seconds
# context.cplex_parameters.randomseed(42)
# context.cplex_parameters.parallel = 1
context.cplex_parameters.workmem = 2048*8

context.cplex_parameters.mip.strategy.file = 3 # Node file on disk and compressed
context.cplex_parameters.mip.strategy.nodeselect = 2 # best-estimate search
context.cplex_parameters.mip.tolerances.absmipgap = np.pi * 0.1 # 18 deg total departure
context.cplex_parameters.mip.display = 2

# if qcr_shift:
#     context.cplex_parameters.optimalitytarget = 1  # globally optimal solution to a convex model.
