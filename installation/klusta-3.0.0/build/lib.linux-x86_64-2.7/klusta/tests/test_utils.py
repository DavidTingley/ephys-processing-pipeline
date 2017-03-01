# -*- coding: utf-8 -*-

"""Tests of misc type utility functions."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op

import numpy as np
from numpy.testing import assert_array_equal as ae
from pytest import raises, mark

from ..kwik.mock import artificial_spike_clusters
from ..utils import (Bunch, _is_integer, captured_output,
                     _load_arrays, _save_arrays,
                     _pad,
                     _spikes_per_cluster,
                     get_excerpts,
                     chunk_bounds,
                     data_chunk,
                     excerpts,
                     )


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------

def test_bunch():
    obj = Bunch()
    obj['a'] = 1
    assert obj.a == 1
    obj.b = 2
    assert obj['b'] == 2


def test_integer():
    assert _is_integer(3)
    assert _is_integer(np.arange(1)[0])
    assert not _is_integer(3.)


def test_captured_output():
    with captured_output() as (out, err):
        print('Hello world!')
    assert out.getvalue().strip() == 'Hello world!'


@mark.parametrize('n', [20, 0])
def test_load_save_arrays(tempdir, n):
    path = op.join(tempdir, 'test.npy')
    # Random arrays.
    arrays = []
    for i in range(n):
        size = np.random.randint(low=3, high=50)
        assert size > 0
        arr = np.random.rand(size, 3).astype(np.float32)
        arrays.append(arr)
    _save_arrays(path, arrays)

    arrays_loaded = _load_arrays(path)

    assert len(arrays) == len(arrays_loaded)
    for arr, arr_loaded in zip(arrays, arrays_loaded):
        assert arr.shape == arr_loaded.shape
        assert arr.dtype == arr_loaded.dtype
        ae(arr, arr_loaded)


def test_pad():
    arr = np.random.rand(10, 3)

    ae(_pad(arr, 0, 'right'), arr[:0, :])
    ae(_pad(arr, 3, 'right'), arr[:3, :])
    ae(_pad(arr, 9), arr[:9, :])
    ae(_pad(arr, 10), arr)

    ae(_pad(arr, 12, 'right')[:10, :], arr)
    ae(_pad(arr, 12)[10:, :], np.zeros((2, 3)))

    ae(_pad(arr, 0, 'left'), arr[:0, :])
    ae(_pad(arr, 3, 'left'), arr[7:, :])
    ae(_pad(arr, 9, 'left'), arr[1:, :])
    ae(_pad(arr, 10, 'left'), arr)

    ae(_pad(arr, 12, 'left')[2:, :], arr)
    ae(_pad(arr, 12, 'left')[:2, :], np.zeros((2, 3)))

    with raises(ValueError):
        _pad(arr, -1)


def test_spikes_per_cluster():
    """Test _spikes_per_cluster()."""

    n_spikes = 1000
    spike_ids = np.arange(n_spikes).astype(np.int64)
    n_clusters = 10
    spike_clusters = artificial_spike_clusters(n_spikes, n_clusters)

    spikes_per_cluster = _spikes_per_cluster(spike_ids, spike_clusters)
    assert list(spikes_per_cluster.keys()) == list(range(n_clusters))

    for i in range(10):
        ae(spikes_per_cluster[i], np.sort(spikes_per_cluster[i]))
        assert np.all(spike_clusters[spikes_per_cluster[i]] == i)


#------------------------------------------------------------------------------
# Test chunking
#------------------------------------------------------------------------------

def test_chunk_bounds():
    chunks = chunk_bounds(200, 100, overlap=20)

    assert next(chunks) == (0, 100, 0, 90)
    assert next(chunks) == (80, 180, 90, 170)
    assert next(chunks) == (160, 200, 170, 200)


def test_chunk():
    data = np.random.randn(200, 4)
    chunks = chunk_bounds(data.shape[0], 100, overlap=20)

    with raises(ValueError):
        data_chunk(data, (0, 0, 0))

    assert data_chunk(data, (0, 0)).shape == (0, 4)

    # Chunk 1.
    ch = next(chunks)
    d = data_chunk(data, ch)
    d_o = data_chunk(data, ch, with_overlap=True)

    ae(d_o, data[0:100])
    ae(d, data[0:90])

    # Chunk 2.
    ch = next(chunks)
    d = data_chunk(data, ch)
    d_o = data_chunk(data, ch, with_overlap=True)

    ae(d_o, data[80:180])
    ae(d, data[90:170])


def test_excerpts_1():
    bounds = [(start, end) for (start, end) in excerpts(100,
                                                        n_excerpts=3,
                                                        excerpt_size=10)]
    assert bounds == [(0, 10), (45, 55), (90, 100)]


def test_excerpts_2():
    bounds = [(start, end) for (start, end) in excerpts(10,
                                                        n_excerpts=3,
                                                        excerpt_size=10)]
    assert bounds == [(0, 10)]


def test_get_excerpts():
    data = np.random.rand(100, 2)
    subdata = get_excerpts(data, n_excerpts=10, excerpt_size=5)
    assert subdata.shape == (50, 2)
    ae(subdata[:5, :], data[:5, :])
    ae(subdata[-5:, :], data[-10:-5, :])

    data = np.random.rand(10, 2)
    subdata = get_excerpts(data, n_excerpts=10, excerpt_size=5)
    ae(subdata, data)
