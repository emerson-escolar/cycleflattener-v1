import ast
import itertools
import numpy as np
import scipy.spatial.distance as ssd
import scipy.sparse as ssm
import networkx as nx

import cycleflattener.angleoptimizer as ao

def list_to_lookupdict(x:list):
    return {v:k for k,v in enumerate(x)}

def compute_angle(a, b):
    cos = np.inner(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))
    clipped_cos = np.clip(cos, -1, 1)
    assert np.isclose(clipped_cos, cos)
    rad = np.arccos(clipped_cos)
    return rad

class Filtration:
    vertex_coordinates: np.array
    simplices: list[dict[str, any]]
    boundaries: list[dict[int, float]]
    cycles: list

    KEY_birth="b"
    KEY_dim="d"
    KEY_vlist="v"

    def __init__(self):
        self.vertex_coordinates = np.array([])
        self.simplices = []
        self.boundary_dict = {}
        self.cycles = []


    @property
    def num_vertices(self):
        return self.vertex_coordinates.shape[0]

    @property
    def vertexindex_to_simplexindex(self):
        # vertexindex is index in self.vertices
        # vertex_simplexindex is index in self.simplices (looking only at dim 0 simplices)
        return { self.get_simplex_vlist(simplexindex)[0] : simplexindex
                 for simplexindex in self.get_simplexindices_satisfying(dim=0)}

    @property
    def vertex_simplexindex_to_vertexindex(self):
        # vertexindex is index in self.vertices
        # vertex_simplexindex is index in self.simplices (looking only at dim 0 simplices)
        return { simplexindex : self.get_simplex_vlist(simplexindex)[0]
                 for simplexindex in self.get_simplexindices_satisfying(dim=0)}

    @property
    def num_simplices(self):
        return len(self.simplices)

    @property
    def last_birth(self):
        return max(self.get_simplex_birth(simplexindex)
                   for simplexindex in range(self.num_simplices))

    def load_vertices(self, fname: str):
        # expects "i2p" file
        # format: vertexindex x y z r
        self.vertex_coordinates = np.loadtxt(fname, usecols=[1, 2, 3])


    def load_alpha_simplices(self, fname:str, maxbirth=np.inf):
        # expects "alphamap" file
        # format: dim birth (comma-separated vertex indices)

        def __alphamap_processor(ifile):
            for line in ifile:
                part = line.split(" ")
                if float(part[1]) <= maxbirth:
                    yield {type(self).KEY_dim: int(part[0]),
                           type(self).KEY_birth: float(part[1]),
                           type(self).KEY_vlist: [int(v) for v in part[2].split(",")]}
                else:
                    break

        with open(fname) as ifile:
            self.simplices = list(__alphamap_processor(ifile))


    def load_1_cycles(self, fname:str):
        # expects: optiperslp generators format
        # only works for dimension 1 cycles.

        cycles = []
        edge_simplexindex_dict = self.__vindex_fset_to_edge_simplexindex()
        with open(fname) as ifile:
            cycle = {}
            for line in ifile:
                line = line.strip()
                # print(line)
                if line[0] == ';':
                    if len(cycle) != 0:
                        cycles.append( (cycle, bdpair) )
                        cycle = {}
                    lifespan_part = line.split()
                    # print(lifespan_part)
                    birth = float(lifespan_part[1])
                    death = float(lifespan_part[2])
                    bdpair = (birth, death)
                else:
                    cycle_part = line.split(",")
                    assert(len(cycle_part) == 3)

                    coeff = float(cycle_part[0])
                    v_fset = frozenset([int(cycle_part[1]), int(cycle_part[2])])
                    cycle[edge_simplexindex_dict[v_fset]] = coeff

            cycle_bd = (cycle, bdpair)
            cycles.append( cycle_bd )
        self.cycles = cycles


    def get_lifespans(self):
        ans = [bd[1]-bd[0] for _,bd in self.cycles]
        return ans


    def __vindex_fset_to_edge_simplexindex(self):
        edges = self.get_simplexindices_satisfying(dim=1)
        return { frozenset(self.get_simplex_vlist(simplexindex)) : simplexindex
                 for simplexindex in edges }

    def load_boundaries(self, fname:str):
        # expects "boundary" file
        # format: simplexindex : {(simplexindex, coeff), ... }

        def __boundary_processor(ifile):
            for i, line in enumerate(ifile):
                part = line.split(":")
                simplex_index = int(part[0])
                assert(simplex_index == i)
                if simplex_index >= self.num_simplices:
                    break
                yield {entry[0]:entry[1] for entry in ast.literal_eval(str(part[1]))}

        with open(fname) as ifile:
            self.boundaries = list(__boundary_processor(ifile))


    def get_simplex_birth(self, simplexindex:int) -> float:
        return self.simplices[simplexindex][type(self).KEY_birth]
    def get_simplex_dim(self, simplexindex:int) -> int:
        return self.simplices[simplexindex][type(self).KEY_dim]
    def get_simplex_vlist(self, simplexindex:int) -> list[int]:
        return self.simplices[simplexindex][type(self).KEY_vlist]


    def get_neighborhood_simplexindices(self, vertexindices:list, eps:float=0.0) -> list:
        # From the list of candidate_simplexindices,
        # extract the sublist of simplexindices whose simplex has each vertex
        # at most distance eps from the set of vertexindices.

        dist_vs = ssd.cdist(self.vertex_coordinates[vertexindices], self.vertex_coordinates)
        neighborhood_vertexindices = {vertexindex for vertexindex in range(self.num_vertices) if
                                      np.min(dist_vs[:, vertexindex]) <= eps}

        def __generator(neighborhood_vertexindices):
            for simplexindex in range(self.num_simplices):
                if set(self.get_simplex_vlist(simplexindex)).issubset(neighborhood_vertexindices):
                    yield simplexindex

        return list(__generator(neighborhood_vertexindices))


    def get_simplexindices_satisfying(self, dim:int, maxbirth=np.inf, nbhd:list=None) -> list:
        if nbhd is None:
            nbhd = range(self.num_simplices)
        return [i for i in nbhd if
                (self.simplices[i][type(self).KEY_birth] <= maxbirth) and
                (self.simplices[i][type(self).KEY_dim] == dim)]

    def context_triangles(self, maxbirth=np.inf, nbhd:list=None):
        # Member functions with "context" depend on the context of
        #  maxbirth and nbhd
        # i.e.\ taken in the context of a subsmplicial complex defined by these parameters.
        # For consistency, ensure that the same context is used!

        return [ self.get_simplex_vlist(simplexindex) for simplexindex
                 in self.get_simplexindices_satisfying(2, maxbirth=maxbirth, nbhd=nbhd) ]



    def get_boundary_coeff(self, query_simplexindex, face_simplexindex):
        return self.boundaries[query_simplexindex].get(query_simplexindex, 0)

    def context_boundary_matrix(self, dim:int, maxbirth=np.inf, nbhd:list=None):
        # Member functions with "context" depend on the context of
        #  maxbirth and nbhd
        # i.e.\ taken in the context of a subsmplicial complex defined by these parameters.
        # For consistency, ensure that the same context is used!

        cur_simplices = self.get_simplexindices_satisfying(dim=dim, maxbirth=maxbirth, nbhd=nbhd)
        dwn_simplices = self.get_simplexindices_satisfying(dim=dim-1, maxbirth=maxbirth, nbhd=nbhd)

        # subindex is index in simplices restricted to dimension dim and dim-1
        cur_tosubindex_dict = list_to_lookupdict(cur_simplices)
        dwn_tosubindex_dict = list_to_lookupdict(dwn_simplices)

        csr_data = []
        csr_row_indices = []
        csr_col_indices = []

        for simplexindex in cur_simplices:
            for face_simplexindex in self.boundaries[simplexindex]:
                csr_data.append(self.boundaries[simplexindex][face_simplexindex])
                csr_col_indices.append( cur_tosubindex_dict[simplexindex] )
                csr_row_indices.append( dwn_tosubindex_dict[face_simplexindex] )

        return ssm.csr_matrix((csr_data, (csr_row_indices,csr_col_indices)),
                              shape=(len(dwn_simplices),len(cur_simplices)))


    def context_exterior_angles_matrix(self, maxbirth=np.inf, nbhd:list=None):
        # Member functions with "context" depend on the context of
        #  maxbirth and nbhd
        # i.e.\ taken in the context of a subsmplicial complex defined by these parameters.
        # For consistency, ensure that the same context is used!

        edges = self.get_simplexindices_satisfying(dim=1, maxbirth=maxbirth, nbhd=nbhd)
        vertices = self.get_simplexindices_satisfying(dim=0, maxbirth=maxbirth, nbhd=nbhd)
        vertices_tosubindex_dict = list_to_lookupdict(vertices)

        csr_data = []
        csr_row_indices = []
        csr_col_indices = []

        bdd = self.context_boundary_matrix(1, maxbirth=maxbirth, nbhd=nbhd)
        for vertex_simplexindex in vertices:
            vertex_subindex = vertices_tosubindex_dict[vertex_simplexindex]
            coface_subindices = bdd[vertex_subindex].nonzero()[1]

            v_vindex = self.vertex_simplexindex_to_vertexindex[vertex_simplexindex]
            def __get_other(vlist, toexclude):
                other = [v for v in vlist if v!=toexclude]
                assert(len(other) == 1)
                return other[0]
            for e1_sub, e2_sub in itertools.combinations(coface_subindices, 2):
                e1 = edges[e1_sub]
                e2 = edges[e2_sub]
                x_vindex = __get_other(self.get_simplex_vlist(e1), v_vindex)
                y_vindex = __get_other(self.get_simplex_vlist(e2), v_vindex)

                # print("edge pair:", (x_vindex, v_vindex), (v_vindex, y_vindex))
                a = self.vertex_coordinates[x_vindex, :] - self.vertex_coordinates[v_vindex, :]
                b = self.vertex_coordinates[v_vindex, :] - self.vertex_coordinates[y_vindex, :]
                angle = compute_angle(a,b)

                csr_data.append(angle)
                csr_row_indices.append(e1_sub)
                csr_col_indices.append(e2_sub)

                csr_data.append(angle)
                csr_row_indices.append(e2_sub)
                csr_col_indices.append(e1_sub)

        return ssm.csr_matrix((csr_data, (csr_row_indices,csr_col_indices)),
                              shape=(len(edges),len(edges)))

    def get_1_cycle_vertices(self, cycle) -> list[list[int]]:
        #  cycle is a dictionary {simplexindex:coeff} representing a cycle.
        G = nx.DiGraph()
        edges = []
        for simplexindex, coeff in cycle.items():
            vlist = self.get_simplex_vlist(simplexindex)
            if coeff > 0:
                edges.append((vlist[0],vlist[1]))
            elif coeff < 0:
                edges.append((vlist[1],vlist[0]))
        G.add_edges_from(edges)
        return nx.simple_cycles(G)

    def get_1_cycle_geometric_length(self, cycle) -> float:
        #  cycle is a dictionary {simplexindex:coeff} representing a cycle.
        ans = 0
        for simplexindex, coeff in cycle.items():
            vlist = self.get_simplex_vlist(simplexindex)
            ans += np.linalg.norm(self.vertex_coordinates[vlist[0], :]
                                  - self.vertex_coordinates[vlist[1], :], ord=2)
        return ans

    def get_1_cycle_total_absolute_curvature(self, cycle) -> float:
        maxbirth = max(self.get_simplex_birth(simplexindex) for simplexindex in cycle)

        Q = self.context_exterior_angles_matrix(maxbirth=maxbirth)
        z = self.context_vectorize_1_cycle(cycle, maxbirth=maxbirth)
        z_abs = np.abs(z.todense())

        # silence weird bug in M4 mac
        # https://stackoverflow.com/questions/79792627/divide-by-zero-encountered-in-matmul-on-macos-m4-with-numpy-v2-0-0
        with np.errstate(divide='ignore', over='ignore', invalid='ignore'):
            ans = 0.5 * z_abs.T @ Q.todense() @ z_abs

        return ans[0,0]


    def print_1_cycle(self, cycle):
        for simple_cycle in self.get_1_cycle_vertices(cycle):
            print(simple_cycle)


    def context_vectorize_1_cycle(self, cycle, maxbirth=np.inf, nbhd:list=None):
        # Member functions with "context" depend on the context of
        #  maxbirth and nbhd
        # i.e.\ taken in the context of a subsmplicial complex defined by these parameters.
        # For consistency, ensure that the same context is used!

        #  cycle is a dictionary {simplexindex:coeff} representing a cycle.

        edges = self.get_simplexindices_satisfying(dim=1, maxbirth=maxbirth, nbhd=nbhd)
        edges_tosubindex_dict = list_to_lookupdict(edges)

        csr_data = []
        csr_row_indices = []
        csr_col_indices = []

        for simplexindex, coeff in cycle.items():
            csr_data.append(coeff)
            csr_row_indices.append(edges_tosubindex_dict[simplexindex])
            csr_col_indices.append(0)

        return ssm.csr_matrix((csr_data, (csr_row_indices,csr_col_indices)),
                              shape=(len(edges),1))


    def context_vector_to_1_cycle(self, vec:ssm.csr_matrix,
                                  maxbirth=np.inf, nbhd:list=None):
        # Member functions with "context" depend on the context of
        #  maxbirth and nbhd
        # i.e.\ taken in the context of a subsmplicial complex defined by these parameters.
        # For consistency, ensure that the same context is used!

        # vec is a ssm.csr_matrix representing vector, with respect to subindices
        # cycle is a dictionary {simplexindex:coeff} representing a cycle.

        edges = self.get_simplexindices_satisfying(dim=1, maxbirth=maxbirth, nbhd=nbhd)

        vec_coo = vec.tocoo()
        cycle = {edges[r]: v for r, v in zip(vec_coo.row, vec_coo.data)}

        return cycle


    def context_solve_aohcp(self, cycle, maxbirth=np.inf, nbhd:list=None,
                            qcr_shift:bool=False,
                            export_file=None,
                            cplex_config_file=None, timelimit=None):

        ans = self.context_solve_aohcp_repeated(cycle, maxbirth=maxbirth, nbhd=nbhd,
                                                qcr_shift=qcr_shift,
                                                export_file=export_file,
                                                cplex_config_file=cplex_config_file, timelimit=timelimit,
                                                n_epoch=1)

        return list(ans)[0]



    def context_solve_aohcp_repeated(self, cycle,
                                     maxbirth=np.inf, nbhd:list=None,
                                     qcr_shift:bool=False,
                                     export_file=None,
                                     cplex_config_file=None,
                                     timelimit=None,
                                     n_epoch=1):
        # assumptions:
        #  cycle is a dictionary {simplexindex:coeff} representing a cycle.

        # get incident vertices:
        vertex_vindices = []
        for edge_simplexindex in cycle.keys():
            for vindex in self.get_simplex_vlist(edge_simplexindex):
                vertex_vindices.append(vindex)
        vertex_vindices = list(set(vertex_vindices))

        Q = self.context_exterior_angles_matrix(maxbirth=maxbirth, nbhd=nbhd)
        D2 = self.context_boundary_matrix(dim=2, maxbirth=maxbirth, nbhd=nbhd)
        z = self.context_vectorize_1_cycle(cycle, maxbirth=maxbirth, nbhd=nbhd)

        Qhat = 0.5 * ssm.vstack((ssm.hstack((Q, Q)),
                                 ssm.hstack((Q, Q))))
        E = ssm.identity(D2.shape[0], dtype=float, format="csr")
        A = ssm.hstack((E, -E, -D2, D2))

        m = A.shape[1]
        Qhat.resize((m,m))

        if qcr_shift:
            diag_list = [2*np.pi]*(2*A.shape[0]) + [1]*(m-2*A.shape[0])
            Qhat += ssm.csr_matrix((diag_list, (range(m), range(m))), shape=(m,m))
            b = -np.array(diag_list)
            eigs = np.linalg.eigvalsh(Qhat.toarray())
            print(f"Qhat min eigenvalue: {min(eigs)}, max eigenvalue: {max(eigs)}")
        else:
            b = None

        angleoptimizer = ao.AngleOptimizer(Qhat, b, A, z, "Angle Optimization via BQP",
                                           cplex_config_file, timelimit)
        # angleoptimizer.mdl.parameters.print_information(print_all=True)

        print("******************************")
        print("num x vars: ", angleoptimizer.num_x_variables)
        print("num y vars: ", angleoptimizer.num_y_variables)

        if export_file is not None:
            angleoptimizer.mdl.export_as_lp(basename="quadratic_optimize",
                                            path=str(export_file))

        for i in range(n_epoch):
            solution, x_vec, y_vec = angleoptimizer.solve(log_output=True)
            cycle = self.context_vector_to_1_cycle(x_vec, maxbirth=maxbirth, nbhd=nbhd)

            print("******************************")
            print(f"SOLUTION after {i+1} solves:")
            print(f"  ||z{i+1}||_0: {len(cycle)}")
            print(f"  l(z{i+1}): {self.get_1_cycle_geometric_length(cycle)}")
            print(f"  k(z{i+1}): {solution.objective_value} ~ {solution.objective_value / np.pi} pi")
            print(f"  z_{i+1}, as vertices:")
            self.print_1_cycle(cycle)
            print("******************************")

            yield (cycle, solution.objective_value)
