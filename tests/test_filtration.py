import pytest
import tempfile
import textwrap

import cycleflattener.filtration as cf

@pytest.fixture
def resource_i2p():
    data = '''\
    0 -2 -2 -2 0
    1 2 2 2 0
    2 -2 -2 2 0
    3 2 2 -2 0
    4 2 -2 -2 0
    5 2 -2 2 0
    6 -2 2 2 0
    7 -2 2 -2 0
    '''.rstrip()
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as fp:
        fp.write(textwrap.dedent(data))
        fp.close()
        print(f"wrote i2p resource in {fp.name}")
        yield fp.name

    print("done");


class TestFiltrationLoaders:
    def test_load_vertices(self, resource_i2p):
        filt = cf.Filtration()
        filt.load_vertices(resource_i2p)

        assert filt.num_vertices == 8
