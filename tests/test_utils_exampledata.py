import pytest
import tempfile

import cycleflattener.utils.exampledata as cue

def test_generate_soleless_slipper():
    data = cue.generate_soleless_slipper(2, 1, 1, 30, 30, 10)
    assert len(data.shape)==2
    assert data.shape[1] == 3
    assert data.shape[0] == 30 + 30*10

    data = cue.generate_soleless_slipper(2, 1, 1, 50, 50, 15)
    assert data.shape[0] == 50 + 50*15

def test_generate_torus():
    data = cue.generate_torus(100, 1, 1)
    assert len(data.shape)==2
    assert data.shape[1] == 3
    assert data.shape[0] == 100

def test_generate_noisy_circle():
    data = cue.generate_noisy_circle(100, 0.1, 1.0, based=False)
    assert len(data.shape)==2
    assert data.shape[1] == 3
    assert data.shape[0] == 100

    data = cue.generate_noisy_circle(100, 0.1, 1.0, based=True)
    assert len(data.shape)==2
    assert data.shape[1] == 3
    assert data.shape[0] == 2*100

def test_generate_cylinder():
    data = cue.generate_cylinder(100, 2.0, 1.0, based=False)
    assert len(data.shape)==2
    assert data.shape[1] == 3
    assert data.shape[0] == 100

    data = cue.generate_cylinder(100, 2.0, 1.0, based=True)
    assert len(data.shape)==2
    assert data.shape[1] == 3
    assert data.shape[0] == 2*100

def test_generate_double_torus():
    data = cue.generate_double_torus(800, 2.0, 1.0)
    assert len(data.shape)==2
    assert data.shape[1] == 3
    assert data.shape[0] == 800
