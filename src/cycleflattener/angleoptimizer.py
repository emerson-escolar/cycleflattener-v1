import scipy.sparse as ssm
import docplex.mp.model


class AngleOptimizer:
    mdl: docplex.mp.model.Model

    def __init__(self, Qhat:ssm.csr_matrix, A:ssm.csr_matrix, z:ssm.csr_matrix, model_name):
        self.A = A
        self.z = z

        self.mdl = docplex.mp.model.Model(model_name)

        assert( z.shape[0] == A.shape[0] )
        assert( z.shape[1] == 1 )

        # setup variables:
        self.x_variables = self.mdl.binary_var_list(self.num_x_variables, name="x")
        self.y_variables = self.mdl.binary_var_list(self.num_y_variables, name="y")


        # add objective:
        obj = 0
        Qhat_coo = Qhat.tocoo()
        for r, c, v in zip(Qhat_coo.row, Qhat_coo.col, Qhat_coo.data):
            obj += self.x_variables[r] * v * self.x_variables[c]
        self.mdl.minimize(obj)

        # add constraints
        variables = self.x_variables + self.y_variables
        for i in range(A.shape[0]):
            lhs = 0
            for c, v in zip(A[i,:].col, A[i,:].data):
                lhs +=  v * variables[c]
            self.mdl.add_constraint( lhs == self.z[i] )


    @property
    def num_x_variables(self):
        return 2 * len(self.z)

    @property
    def num_y_variables(self):
        return self.A.shape[1] - 2 * self.A.shape[0]
