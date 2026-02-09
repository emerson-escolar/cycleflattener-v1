import pytest
import tempfile
import textwrap

import numpy as np
import cycleflattener.filtration as cf

def test_list_inverter():
    sample_list = [2,-1,10]
    inv = cf.list_to_lookupdict(sample_list)
    assert inv == {2:0, -1:1, 10:2}


def test_angle_parallel():
    angle = cf.compute_angle(np.array([1,1,1]), np.array([2,2,2]))
    assert angle == 0.0

    angle = cf.compute_angle(np.array([1,1,1]), np.array([-2,-2,-2]))
    assert angle == np.pi

def test_angle_orthogonal():
    angle = cf.compute_angle(np.array([1,1,1]), np.array([-1,1,0]))
    assert angle == np.pi/2


def writer(data, name):
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as fp:
        fp.write(textwrap.dedent(data))
        fp.close()
        print(f"wrote {name} resource in {fp.name}")
        yield fp.name


@pytest.fixture(scope="module")
def resource_i2p():
    data = '''\
    0 1 1 0 0
    1 1 0 0 0
    2 0 1 0 0
    3 0 0 0.0001 0
    '''.rstrip()
    yield from writer(data, "i2p")

@pytest.fixture(scope="module")
def resource_alp():
    data = '''\
    0 0.0 0
    0 0.0 1
    0 0.0 2
    0 0.0 3
    1 0.5 0,1
    1 0.5 0,2
    1 0.5 3,1
    1 0.5 3,2
    1 1.0 1,2
    2 1.5 0,1,2
    '''.rstrip()
    yield from writer(data, "alphamap")

@pytest.fixture(scope="module")
def resource_bdd():
    data = '''\
    0:{}
    1:{}
    2:{}
    3:{}
    4:{(1,1),(0,-1)}
    5:{(2,1),(0,-1)}
    6:{(1,1),(3,-1)}
    7:{(2,1),(3,-1)}
    8:{(2,1),(1,-1)}
    9:{(8,1),(5,-1),(4,1)}
    '''.rstrip()
    yield from writer(data, "boundary")


@pytest.fixture
def resource_filt(resource_i2p, resource_alp, resource_bdd) -> cf.Filtration:
    filt = cf.Filtration()
    filt.load_vertices(resource_i2p)
    filt.load_alpha_simplices(resource_alp)
    filt.load_boundaries(resource_bdd)
    yield filt


class TestFiltrationLoaders:
    def test_load_vertices(self, resource_i2p):
        filt = cf.Filtration()
        filt.load_vertices(resource_i2p)
        assert filt.num_vertices == 4
        assert np.all(filt.vertex_coordinates[0,:] == np.array([1,1,0]))

    def test_load_simplices(self, resource_alp):
        filt = cf.Filtration()
        filt.load_alpha_simplices(resource_alp)
        assert filt.num_simplices == 10
        assert filt.last_birth == 1.5

        assert filt.get_simplex_birth(7) == 0.5
        assert filt.get_simplex_birth(8) == 1.0
        assert filt.get_simplex_birth(9) == 1.5

        assert filt.get_simplex_dim(8) == 1
        assert filt.get_simplex_dim(9) == 2

        assert set(filt.get_simplex_vlist(9)) == set([0,1,2])


    def test_neighborhood(self, resource_i2p, resource_alp):
        filt = cf.Filtration()
        filt.load_vertices(resource_i2p)
        filt.load_alpha_simplices(resource_alp)

        nbhd = filt.get_neighborhood_simplexindices([0], eps=0)
        assert set(nbhd) == set([0])

        nbhd = filt.get_neighborhood_simplexindices([0,1,2], eps=0)
        assert set(nbhd) == set([0,1,2,4,5,8,9])

        nbhd = filt.get_neighborhood_simplexindices([0], eps=1)
        assert set(nbhd) == set([0,1,2,4,5,8,9])

        nbhd = filt.get_neighborhood_simplexindices([0], eps=2)
        assert set(nbhd) == set(range(10))


    def test_context_dim(self, resource_i2p, resource_alp):
        filt = cf.Filtration()
        filt.load_vertices(resource_i2p)
        filt.load_alpha_simplices(resource_alp)

        sub = filt.get_simplexindices_satisfying(dim=0)
        assert sub == list(range(4))

        sub = filt.get_simplexindices_satisfying(dim=1)
        assert sub == list(range(4,9))

        sub = filt.get_simplexindices_satisfying(dim=2)
        assert sub == [9]

        sub = filt.get_simplexindices_satisfying(dim=3)
        assert sub == []

        sub = filt.get_simplexindices_satisfying(dim=-1)
        assert sub == []


    def test_context_maxbirth(self, resource_i2p, resource_alp):
        filt = cf.Filtration()
        filt.load_vertices(resource_i2p)
        filt.load_alpha_simplices(resource_alp)

        sub = filt.get_simplexindices_satisfying(dim=1, maxbirth=0.8)
        assert sub == list(range(4,8))



    def test_triple(self, resource_filt):
        filt = resource_filt

        assert filt.context_boundary_matrix(dim=0).shape == (0,4)

        bdd1 = np.array([[-1 ,-1 ,0  ,0  , 0],
                         [1  ,0  ,1  ,0  ,-1],
                         [0  ,1  ,0  ,1  , 1],
                         [0  ,0  ,-1 ,-1 , 0]])
        assert(np.allclose(filt.context_boundary_matrix(dim=1).toarray(), bdd1))

        angles_matrix = np.array([[0    ,0    ,0    ,0    ,0] ,
                                  [0.5  ,0    ,0    ,0    ,0] ,
                                  [0.5  ,0    ,0    ,0    ,0] ,
                                  [0    ,0.5  ,0.5  ,0    ,0] ,
                                  [0.75 ,0.75 ,0.75 ,0.75 ,0]]) * np.pi
        angles_matrix += angles_matrix.T
        assert(np.allclose(filt.context_exterior_angles_matrix().toarray(), angles_matrix))

        cycle = {4:1, 6:-1, 7:1, 5:-1}
        print("optimization target:")
        filt.print_1_cycle(cycle)

        filt.context_compute_angleoptimal_homologous_cycle((cycle, (0.5,np.inf)))
