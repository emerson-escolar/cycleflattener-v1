import numpy as np
import ast

class Filtration:
    vs: np.array
    simplices: dict[int, dict]
    cycles: list
    boundary_dict: dict[int, set]

    def __init__(self):
        self.vs = np.array([])

        self.simplices = {}
        self.cycles = []
        self.boundary_dict = {}


    def _load_vertices(self, fname: str):
        # expects "i2p" file
        # format: vertexindex x y z r
        self.vs = np.loadtxt(fname, usecols=[1, 2, 3])


    def _load_alpha_simplices(self, fname:str):
        # expects "alphamap" file
        # format: dim birth (comma-separated vertex indices)

        with open(fname) as ifile:
            lines = ifile.read().splitlines()

        self.simplices = {}
        for index, line in enumerate(lines):
            part = line.split(" ")
            dim = int(part[0])
            birth = float(part[1])
            vertex_list = [int(v) for v in part[2].split(",")]
            simplex = {"dim": dim, "birth": birth, "vertex_list": vertex_list}
            self.simplices.update({index: simplex})


    def _load_boundary_dict(self, fname:str):
        # expects "boundary" file
        # format: simplexindex : {(simplexindex, coeff), ... }

        with open(fname) as f:
            lines = f.read().splitlines()

        # TODO: think about data structure for boundary_dict...
        self.boundary_dict = {}
        for line in lines:
            part = line.split(":")
            simplex_index = int(part[0])

            bd_sets = ast.literal_eval(str(part[1]))
            self.boundary_dict.update({simplex_index: bd_sets})
