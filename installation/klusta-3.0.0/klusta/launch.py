# -*- coding: utf-8 -*-

"""Launch routines."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import logging
import os.path as op
import shutil
import sys

import click
import numpy as np

from .traces import SpikeDetekt
from .kwik.creator import create_kwik, KwikCreator
from .kwik.model import KwikModel
from .klustakwik import klustakwik
from .utils import _ensure_dir_exists
from .__init__ import __version_git__, add_default_handler

logger = logging.getLogger(__name__)


#------------------------------------------------------------------------------
# Launch
#------------------------------------------------------------------------------

def detect(model, interval=None, **kwargs):
    traces = model.all_traces

    # Setup the temporary directory.
    expdir = op.dirname(model.kwik_path)
    sd_dir = op.join(expdir, '.spikedetekt')
    _ensure_dir_exists(sd_dir)

    # Default interval.
    if interval is not None:
        (start_sec, end_sec) = interval
        sr = model.sample_rate
        interval_samples = (int(start_sec * sr),
                            int(end_sec * sr))
    else:
        interval_samples = None

    # Take the parameters in the Kwik file, coming from the PRM file.
    params = model.metadata
    params.update(kwargs)
    # Pretty print params.
    logger.info("SpikeDetekt parameters:")
    for key, value in params.items():
        logger.info("%s = %s", key, value)

    # Probe parameters required by SpikeDetekt.
    params['probe_channels'] = model.probe.channels_per_group
    params['probe_adjacency_list'] = model.probe.adjacency

    # Start the spike detection.
    logger.debug("Running SpikeDetekt...")
    sd = SpikeDetekt(tempdir=sd_dir, **params)
    out = sd.run_serial(traces, interval_samples=interval_samples)
    return out


def cluster(model, spike_ids=None, **kwargs):
    """Return the spike_clusters and metadata.

    Doesn't make any change to the model. The caller must add the clustering.

    """
    # Skip if no spikes.
    if not model.n_spikes:
        return np.array([], dtype=np.int32), {}

    # Setup the temporary directory.
    expdir = op.dirname(model.kwik_path)
    kk_dir = op.join(expdir, '.klustakwik2')
    _ensure_dir_exists(kk_dir)

    params = model.kk2_metadata
    params.update(kwargs)

    # Original spike_clusters array.
    if model.spike_clusters is None:
        n_spikes = (len(spike_ids) if spike_ids is not None
                    else model.n_spikes)
        spike_clusters_orig = np.zeros(n_spikes, dtype=np.int32)
    else:
        spike_clusters_orig = model.spike_clusters.copy()

    def on_iter(sc):
        # Update the original spike clusters.
        spike_clusters = spike_clusters_orig.copy()
        spike_clusters[spike_ids] = sc
        # Save to a text file.
        path = op.join(kk_dir, 'spike_clusters.txt')
        # Backup.
        if op.exists(path):
            shutil.copy(path, path + '~')
        np.savetxt(path, spike_clusters, fmt='%d')

    logger.info("Running KK...")
    # Run KK.
    sc, params = klustakwik(model=model,
                            spike_ids=spike_ids,
                            iter_callback=on_iter,
                            **params)
    logger.info("The automatic clustering process has finished.")

    # Save the results in the Kwik file.
    spike_clusters = spike_clusters_orig.copy()
    spike_clusters[spike_ids] = sc

    # Set the new clustering metadata.
    metadata = {'klustakwik2_{}'.format(name): value
                for name, value in params.items()}

    return sc, metadata


def klusta(prm_file,
           output_dir=None,
           interval=None,
           channel_group=None,
           detect_only=False,
           cluster_only=False,
           overwrite=False,
           ):

    if prm_file.endswith('.kwik'):
        kwik_path = prm_file
        logger.info("Call `klusta` on a PRM file to spikesort your data.")
        if op.exists(kwik_path):
            logger.info("Here is a description of `%s`:", kwik_path)
            model = KwikModel(kwik_path)
            model.describe()
        return

    # Detection and/or clustering.
    do_detect = not cluster_only
    do_cluster = not detect_only
    assert do_detect or do_cluster

    # Parse the interval (pair of floats).
    # if isinstance(interval, six.string_types):
    if interval and interval[0] is not None and interval[1] is not None:
        assert 0 <= interval[0] < interval[1]
    else:
        interval = None

    # Delete the SpikeDetekt cache if overwriting the files.
    if overwrite:
        sd_dir = op.join(output_dir or '', '.spikedetekt')
        if op.exists(sd_dir):
            logger.info("Deleting `%s`.", sd_dir)
            shutil.rmtree(sd_dir)

    # Ensure the kwik file exists. Doesn't overwrite it if it exists.
    kwik_path = create_kwik(prm_file=prm_file,
                            output_dir=output_dir,
                            overwrite=overwrite,
                            )

    # Detection.
    if do_detect:
        logger.info("Starting spike detection.")
        # NOTE: always detect on all shanks.
        model = KwikModel(kwik_path)
        out = detect(model, interval=interval)
        model.close()

        # Add the spikes to the kwik file.
        creator = KwikCreator(kwik_path)
        creator.add_spikes_after_detection(out)
        logger.info("Spike detection done!")

    # List of channel groups.
    if channel_group is None:
        channel_groups = out.groups
    else:
        channel_groups = [channel_group]

    # Clustering.
    if do_cluster:
        # Cluster every channel group.
        for channel_group in channel_groups:
            logger.info("Starting clustering on shank %d/%d.",
                        channel_group, len(channel_groups))
            model = KwikModel(kwik_path, channel_group=channel_group)
            logger.info("Clustering group %d (%d spikes).",
                        channel_group, model.n_spikes)
            # Skip clustering if there are no spikes.
            if not model.n_spikes:
                continue
            spike_clusters, metadata = cluster(model)
            model.close()

            # Add the results to the kwik file.
            model = KwikModel(kwik_path, channel_group=channel_group)
            model.add_clustering('main', spike_clusters)
            model.copy_clustering('main', 'original')
            model.clustering_metadata.update(metadata)
            model.save(clustering_metadata=model.clustering_metadata)
            model.close()
        logger.info("Clustering done!")

    return kwik_path


@click.command()
@click.argument('prm_file',
                type=click.Path(exists=True, file_okay=True, dir_okay=False),
                )
@click.option('--output-dir',
              type=click.Path(file_okay=False, dir_okay=True),
              help='Output directory.',
              )
@click.option('--interval',
              type=click.Tuple([float, float]),
              help='Interval in seconds, e.g. `--interval 0 2`.',
              default=(None, None),
              )
@click.option('--channel-group',
              type=click.INT,
              help='Channel group to cluster (all by default).',
              )
@click.option('--detect-only',
              help='Only do spike detection.',
              default=False,
              is_flag=True,
              )
@click.option('--cluster-only',
              help='Only do automatic clustering.',
              default=False,
              is_flag=True,
              )
@click.option('--overwrite',
              help='Overwrite the Kwik file.',
              default=False,
              is_flag=True,
              )
@click.option('--debug',
              help='Use the DEBUG logging level.',
              default=False,
              is_flag=True,
              )
@click.version_option(version=__version_git__)
@click.help_option()
def main(*args, **kwargs):
    """Spikesort a dataset.

    By default, perform spike detection (with SpikeDetekt) and automatic
    clustering (with KlustaKwik2). You can also choose to run only one step.

    You need to specify three pieces of information to spikesort your data:

    * The raw data file: typically a `.dat` file.

    * The PRM file: a Python file with the `.prm` extension, containing the parameters for your sorting session.

    * The PRB file: a Python file with the `.prb` extension, containing the layout of your probe.

    """  # noqa

    debug = kwargs.pop('debug', None)

    # Hide the traceback unless DEBUG mode.
    def exception_handler(exception_type, exception, traceback):
        print("{}: {}".format(exception_type.__name__, exception))
    if not debug:
        sys.excepthook = exception_handler

    add_default_handler('DEBUG' if debug else 'INFO')
    return klusta(*args, **kwargs)
