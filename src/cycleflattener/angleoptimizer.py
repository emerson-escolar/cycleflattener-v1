import scipy.sparse as ssm
import docplex.mp.model
import numpy as np
from typing import Optional

class AngleOptimizer:
    mdl: docplex.mp.model.Model
    z: ssm.csr_matrix

    def __init__(self, Qhat:ssm.csr_matrix, b:Optional[np.array], A:ssm.csr_matrix, z:ssm.csr_matrix,
                 model_name, cplex_config_file=None, timelimit=None):
        self.A = A
        self.z = z

        self.mdl = docplex.mp.model.Model(model_name)
        if cplex_config_file is not None:
            self.mdl.context.read_settings(cplex_config_file)
        if timelimit is not None:
            self.mdl.context.update({"cplex_parameters":{"timelimit":timelimit}})

        assert( z.shape[0] == A.shape[0] )
        assert( z.shape[1] == 1 )

        # setup variables:
        self.x_variables = self.mdl.binary_var_list(self.num_x_variables, name="x")
        self.y_variables = self.mdl.binary_var_list(self.num_y_variables, name="y")

        variables = self.x_variables + self.y_variables

        # add objective:
        obj = 0
        Qhat_coo = Qhat.tocoo()
        for r, c, v in zip(Qhat_coo.row, Qhat_coo.col, Qhat_coo.data):
            obj += variables[r] * v * variables[c]
        if b is not None:
            for c, v in enumerate(b):
                obj += v * variables[c]
        self.mdl.minimize(obj)

        # add constraints
        for i in range(A.shape[0]):
            lhs = 0
            row = A[i,:].tocoo()
            for c, v in zip(row.col, row.data):
                lhs +=  v * variables[c]
            self.mdl.add_constraint( lhs == self.z[i,0] )

        # add initial solution
        warm_start = self.mdl.new_solution()
        for i in range(self.z.shape[0]):
            coeff = self.z[i,0]
            if coeff >= 0:
                warm_start.add_var_value(self.x_variables[i], float(coeff))
            else:
                warm_start.add_var_value(self.x_variables[i+self.z.shape[0]], -float(coeff))

        print(f"Warm start is valid: {warm_start.is_valid_solution()}")
        if warm_start.is_valid_solution():
            self.mdl.add_mip_start(warm_start)


    @property
    def num_x_variables(self):
        return 2 * self.z.shape[0]

    @property
    def num_y_variables(self):
        return self.A.shape[1] - 2 * self.A.shape[0]


    def __solution_to_csr(self, solution:docplex.mp.solution.SolveSolution,
                          variables_choice:str):
        if variables_choice == "x":
            variables = self.x_variables
        elif variables_choice == "y":
            variables = self.y_variables
        else:
            variables = []

        assert(len(variables) % 2 == 0)
        mid = len(variables) // 2

        plus_minus = [0, 0]
        for j in range(2):
            csr_data = []
            csr_row_indices = []
            variables_half = variables[mid*j:mid*(j+1)]
            i=-1
            for i, value in enumerate(solution.get_value_list(variables_half)):
                if value != 0:
                    csr_data.append(value)
                    csr_row_indices.append(i)
            plus_minus[j] = ssm.csr_matrix((csr_data,
                                            (csr_row_indices, [0]*len(csr_data))),
                                            (i+1, 1))

        return plus_minus[0] - plus_minus[1]

    def solve(self, **kwargs):
        solution = self.mdl.solve(**kwargs)
        if solution is None:
            x_vec = None
            y_vec = None
        else:
            x_vec = self.__solution_to_csr(solution, "x")
            y_vec = self.__solution_to_csr(solution, "y")

        return solution, x_vec, y_vec
