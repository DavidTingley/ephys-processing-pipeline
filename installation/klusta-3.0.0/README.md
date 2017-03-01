# Klusta: automatic spike sorting up to 64 channels

[![Build Status](https://img.shields.io/travis/kwikteam/klusta.svg)](https://travis-ci.org/kwikteam/klusta)
[![codecov.io](https://img.shields.io/codecov/c/github/kwikteam/klusta.svg)](http://codecov.io/github/kwikteam/klusta?branch=master)
[![Documentation Status](https://readthedocs.org/projects/klusta/badge/?version=latest)](http://klusta.readthedocs.org/en/latest/)
[![PyPI release](https://img.shields.io/pypi/v/klusta.svg)](https://pypi.python.org/pypi/klusta)
[![GitHub release](https://img.shields.io/github/release/kwikteam/klusta.svg)](https://github.com/kwikteam/klusta/releases/latest)

[**klusta**](https://github.com/kwikteam/klusta) is an open source automatic spike sorting package for multielectrode neurophysiological recordings that scales to probes with up to 64 interdependent channels.

We are also working actively on more sophisticated algorithms that will scale to hundreds/thousands of channels. This work is being done within the [phy project](https://github.com/kwikteam/phy), which is still experimental at this point.

## Overview

**klusta** implements the following features:

* **Kwik**: An HDF5-based file format that stores the results of a spike sorting session.
* **Spike detection** (also known as SpikeDetekt): an algorithm designed for relatively large probes, based on a flood-fill algorithm in the adjacency graph formed by the recording sites in the probe.
* **Automatic clustering** (also known as Masked KlustaKwik): an automatic clustering algorithm designed for high-dimensional structured datasets.


## GUI

You will need a GUI to visualize the spike sorting results. **No GUI is included in this repository**.

We have developed two GUI programs:

* [**KlustaViewa**](https://github.com/klusta-team/klustaviewa): scales up to 64 channels, well-tested by many users over the last few years.
* **phy KwikGUI**: scales to hundreds/thousands of channels, still experimental. We will add a link when this GUI is ready (later in 2016).


## Technical details

**klusta** is written in pure Python. The clustering code, written in Python and Cython, currently lives in [another repository](https://github.com/kwikteam/klustakwik2/).


## Getting started

You will find installation instructions and a quick start guide in the [documentation](http://klusta.readthedocs.org/en/latest/) (work in progress).


## Links

* [Documentation](http://klusta.readthedocs.org/en/latest/) (work in progress)
* [Paper in Nature Neuroscience (April 2016)](http://www.nature.com/neuro/journal/vaop/ncurrent/full/nn.4268.html)
* [Mailing list](https://groups.google.com/forum/#!forum/klustaviewas)
* [Sample data repository](http://phy.cortexlab.net/data/) (work in progress)


## Credits

**klusta** is developed by [Cyrille Rossant](http://cyrille.rossant.net), [Shabnam Kadir](https://iris.ucl.ac.uk/iris/browse/profile?upi=SKADI56), [Dan Goodman](http://thesamovar.net/), [Max Hunter](https://iris.ucl.ac.uk/iris/browse/profile?upi=MLDHU99), and [Kenneth Harris](https://iris.ucl.ac.uk/iris/browse/profile?upi=KDHAR02), in the [Cortexlab](https://www.ucl.ac.uk/cortexlab), University College London.
