# -*- coding: utf-8 -*-

"""py.test utilities."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import logging
import numpy as np
import os
import os.path as op

from pytest import yield_fixture

from klusta import add_default_handler
from klusta.datasets import download_test_data
from klusta.kwik.mea import load_probe
from klusta.kwik.mock import artificial_traces
from klusta.tempdir import TemporaryDirectory
from klusta.utils import Bunch, _read_python


#------------------------------------------------------------------------------
# Common fixtures
#------------------------------------------------------------------------------

logging.getLogger().setLevel(logging.DEBUG)
add_default_handler('DEBUG')

# Fix the random seed in the tests.
np.random.seed(2016)


@yield_fixture
def tempdir():
    with TemporaryDirectory() as tempdir:
        yield tempdir


@yield_fixture
def chdir_tempdir():
    curdir = os.getcwd()
    with TemporaryDirectory() as tempdir:
        os.chdir(tempdir)
        yield tempdir
    os.chdir(curdir)


@yield_fixture(params=['null', 'artificial', 'real'])
def raw_dataset(request):
    sample_rate = 20000
    curdir = op.realpath(op.dirname(__file__))
    path = op.join(curdir, 'traces/default_settings.py')
    params = _read_python(path)['spikedetekt']
    data_type = request.param
    if data_type == 'real':
        path = download_test_data('test-32ch-10s.dat')
        traces = np.fromfile(path, dtype=np.int16).reshape((200000, 32))
        traces = traces[:45000]
        n_samples, n_channels = traces.shape
        params['use_single_threshold'] = False
        probe = load_probe('1x32_buzsaki')
    else:
        probe = {'channel_groups': {
            0: {'channels': [0, 1, 2],
                'graph': [[0, 1], [0, 2], [1, 2]],
                },
            1: {'channels': [3],
                'graph': [],
                'geometry': {3: [0., 0.]},
                }
        }}
        if data_type == 'null':
            n_samples, n_channels = 25000, 4
            traces = np.zeros((n_samples, n_channels))
        elif data_type == 'artificial':
            n_samples, n_channels = 25000, 4
            traces = artificial_traces(n_samples, n_channels)
            traces[5000:5010, 1] *= 5
            traces[15000:15010, 3] *= 5
    n_samples_w = params['extract_s_before'] + params['extract_s_after']
    yield Bunch(n_channels=n_channels,
                n_samples=n_samples,
                sample_rate=sample_rate,
                n_samples_waveforms=n_samples_w,
                traces=traces,
                params=params,
                probe=probe,
                )
