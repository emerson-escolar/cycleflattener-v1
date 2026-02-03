import numpy as np
import ast
import scipy.spatial.distance as ssd
import scipy.sparse as ssm

import itertools

def list_to_lookupdict(x:list):
    return {v:k for k,v in enumerate(x)}

def compute_angle(a, b):
    cos = a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
    rad = np.arccos(cos)
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

    def _load_vertices(self, fname: str):
        # expects "i2p" file
        # format: vertexindex x y z r
        self.vertex_coordinates = np.loadtxt(fname, usecols=[1, 2, 3])


    def _load_alpha_simplices(self, fname:str, maxbirth=np.inf):
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


    def _load_boundaries(self, fname:str):
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


    def get_simplexindices_satisfying(self, dim:int, maxbirth=np.inf) -> list:
        return [i for i, simplex in enumerate(self.simplices) if
                (simplex[type(self).KEY_birth] <= maxbirth) and
                (simplex[type(self).KEY_dim] == dim)]

    def get_simplex_birth(self, simplexindex:int) -> float:
        return self.simplices[simplexindex][type(self).KEY_birth]
    def get_simplex_dim(self, simplexindex:int) -> int:
        return self.simplices[simplexindex][type(self).KEY_dim]
    def get_simplex_vlist(self, simplexindex:int) -> list[int]:
        return self.simplices[simplexindex][type(self).KEY_vlist]

    def get_exterior_angle(self, simplexindex1:int, simplexindex2:int) -> float:
        if self.get_simplex_dim(simplexindex1) != 1 or self.get_simplex_dim(simplexindex2) != 1:
            print(f"ERROR: get_exterior_angle called on non-edge(s): {simplexindex1} and {simplexindex2}")
            return -1.0

        # TODO
        return 0.0



    def get_neighborhood_simplexindices(self, vertexindices:list, eps:float=0.0,
                                        candidate_simplexindices:list|None=None) -> list:
        # From the list of candidate_simplexindices,
        # extract the sublist of simplexindices whose simplex has each vertex
        # at most distance eps from the set of vertexindices.

        dist_vs = ssd.cdist(self.vertex_coordinates[vertexindices], self.vertex_coordinates)
        neighborhood_vertexindices = {vertexindex for vertexindex in range(self.num_vertices) if
                                      np.min(dist_vs[:, vertexindex]) <= eps}

        if candidate_simplexindices is None: candidate_simplexindices = range(self.num_simplices)
        def __generator(neighborhood_vertexindices, candidate_simplexindices):
            for simplexindex in candidate_simplexindices:
                if set(self.get_simplex_vlist(simplexindex)).issubset(neighborhood_vertexindices):
                    yield simplexindex

        return list(__generator(neighborhood_vertexindices, candidate_simplexindices))


    def get_boundary_coeff(self, query_simplexindex, face_simplexindex):
        return self.boundaries[query_simplexindex].get(query_simplexindex, 0)

    def get_boundary_matrix(self, dim:int):
        cur_simplices = self.get_simplexindices_satisfying(dim=dim)
        dwn_simplices = self.get_simplexindices_satisfying(dim=dim-1)

        # subindex is index in simplices restricted to dimension dim and dim-1
        cur_subindex_dict = list_to_lookupdict(cur_simplices)
        dwn_subindex_dict = list_to_lookupdict(dwn_simplices)

        csr_data = []
        csr_row_indices = []
        csr_col_indices = []

        for simplexindex in cur_simplices:
            for face_simplexindex in self.boundaries[simplexindex]:
                csr_data.append(self.boundaries[simplexindex][face_simplexindex])
                csr_col_indices.append( cur_subindex_dict[simplexindex] )
                csr_row_indices.append( dwn_subindex_dict[face_simplexindex] )

        return ssm.csr_matrix((csr_data, (csr_row_indices,csr_col_indices)),
                              shape=(len(dwn_simplices),len(cur_simplices)))



    def get_exterior_angles_matrix(self):
        edges = self.get_simplexindices_satisfying(dim=1)
        vertices = self.get_simplexindices_satisfying(dim=0)

        edges_subindex_dict = list_to_lookupdict(edges)
        vertices_subindex_dict = list_to_lookupdict(vertices)

        bdd = self.get_boundary_matrix(1)
        for vertex_simplexindex in vertices:
            vertex_subindex = vertices_subindex_dict[vertex_simplexindex]
            coface_subindices = bdd[vertex_subindex].nonzero()[1]

            csr_data = []
            csr_row_indices = []
            csr_col_indices = []

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
