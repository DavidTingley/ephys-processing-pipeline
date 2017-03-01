# -*- coding: utf-8 -*-

"""Test launcher."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op
from textwrap import dedent

from pytest import fixture

from ..launch import klusta
from ..datasets import download_test_data
from ..kwik.model import KwikModel


#------------------------------------------------------------------------------
# Fixtures
#------------------------------------------------------------------------------

@fixture
def prm_path_real(tempdir):
    dat_path = download_test_data('test-32ch-10s.dat')
    prm = dedent("""
        prb_file = '1x32_buzsaki'
        experiment_name = 'test_real'
        traces = dict(
            raw_data_files = ["%s"],
            voltage_gain = 10.,
            sample_rate = 20000,
            n_channels = 32,
            dtype = 'int16',
        )
        spikedetekt = {}
        klustakwik2 = dict(num_starting_clusters=10)
        """ % dat_path)
    path = op.join(tempdir, 'params.prm')
    with open(path, 'w') as f:
        f.write(prm)
    return path


@fixture
def prm_path_shanks(tempdir):
    dat_path = download_test_data('test-32ch-10s.dat')

    # Create the PRB.
    prb = dedent("""
                 channel_groups = {
                    0: {'channels': [0, 1],
                        'graph': [[0, 1]],
                        },
                    1: {'channels': [2, 3],
                        'graph': [[2, 3]],
                        }
                 }
                 """)
    path = op.join(tempdir, 'probe.prb')
    with open(path, 'w') as f:
        f.write(prb)

    # Create the PRM.
    prm = dedent("""
        prb_file = '%s'
        experiment_name = 'test_shanks'
        traces = dict(
            raw_data_files = ["%s"],
            sample_rate = 20000,
            n_channels = 32,
            dtype = 'int16',
        )
        spikedetekt = {}
        klustakwik2 = dict(num_starting_clusters=20)
        """ % (path, dat_path))
    path = op.join(tempdir, 'params.prm')
    with open(path, 'w') as f:
        f.write(prm)

    return path


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------

def test_launch_shanks(tempdir, prm_path_shanks):
    kwik_path = klusta(prm_path_shanks,
                       output_dir=tempdir,
                       )

    model = KwikModel(kwik_path)

    model.channel_group = 0
    model.describe()
    assert model.n_spikes > 0
    assert model.n_clusters > 0

    model.channel_group = 1
    model.describe()
    assert model.n_spikes == 0
    assert model.n_clusters == 0

    assert model.clustering_metadata['klustakwik2_num_starting_clusters'] == 20

    klusta(kwik_path)


def test_launch_real(tempdir, prm_path_real):
    kwik_path = klusta(prm_path_real,
                       interval=(0., 4.),
                       output_dir=tempdir,
                       )

    # Check.
    model = KwikModel(kwik_path)
    assert model.n_spikes >= 100
    assert model.n_clusters >= 2
    model.describe()
