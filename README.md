Cambridge Digital Communications Assessment Model (cdcam)
=========================================================

[![PyPI](https://img.shields.io/pypi/v/cdcam)](https://pypi.org/project/cdcam/)
[![Documentation Status](https://readthedocs.org/projects/cdcam/badge/?version=latest)](https://cdcam.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/nismod/cdcam.svg?branch=master)](https://travis-ci.com/nismod/cdcam)
[![Coverage Status](https://coveralls.io/repos/github/nismod/cdcam/badge.svg?branch=master)](https://coveralls.io/github/nismod/cdcam?branch=master)
[![Zenodo DOI](https://zenodo.org/badge/215249573.svg)](https://zenodo.org/badge/latestdoi/215249573)
[![JOSS DOI](https://joss.theoj.org/papers/10.21105/joss.01911/status.svg)](https://doi.org/10.21105/joss.01911)

Description
===========

The **Cambridge Digital Communications Assessment Model** (`cdcam`) is a decision support tool
to quantify the performance of national digital infrastructure strategies for mobile broadband,
focussing on 4G and 5G technologies.

Citations
---------

- Oughton, E.J. and Frias, Z. (2017) The Cost, Coverage and Rollout Implications of 5G
  Infrastructure in Britain. Telecommunications Policy.
  https://doi.org/10.1016/j.telpol.2017.07.009.
- Oughton, E.J., Z. Frias, T. Russell, D. Sicker, and D.D. Cleevely. 2018. Towards 5G:
  Scenario-Based Assessment of the Future Supply and Demand for Mobile Telecommunications
  Infrastructure. Technological Forecasting and Social Change, 133 (August): 141–55.
  https://doi.org/10.1016/j.techfore.2018.03.016.
- Oughton, E.J., Frias, Z., van der Gaast, S. and van der Berg, R. (2019) Assessing the
  Capacity, Coverage and Cost of 5G Infrastructure Strategies: Analysis of The Netherlands.
  Telematics and Informatics (January). https://doi.org/10.1016/j.tele.2019.01.003.


Setup and configuration
=======================

All code for **The Cambridge Digital Communications Assessment Model** is written in Python
(Python>=3.5). The core model has no other dependencies.

See `requirements-dev.txt` for a full list of optional dependencies used in supporting
scripts.


Using conda
-----------

The recommended installation method is to use [conda](http://conda.pydata.org/miniconda.html),
which handles packages and virtual environments, along with the
[`conda-forge`](https://conda-forge.org/) channel which has a host of pre-built libraries and
packages.

Create a conda environment called `cdcam`:

    conda create --name cdcam python=3.7

Activate it (run this each time you switch projects):

    conda activate cdcam

First, install optional packages:

    conda install fiona shapely rtree pyproj tqdm

Then install `cdcam`:

    pip install cdcam

Alternatively, for development purposes, clone this repository and run:

    python setup.py develop

Install test/dev requirements:

    conda install pytest pytest-cov

Run the tests:

    pytest --cov-report=term --cov=cdcam tests/


Quick start
-----------

If you want to quickly generate results, first download the sample dataset available at [DOI
10.5281/zenodo.3525285](https://doi.org/10.5281/zenodo.3525285), then run:

    python scripts/run.py

You should see the model printing output such as `Running: baseline baseline macrocell`
which means the data have been loaded and you are running the baseline population scenario,
baseline data throughput scenario and macrocell upgrade strategy.

You should then see an output for each year (`- 2020`) indicating how much money was spent on
either servicing a specified coverage obligation (`Service`) or in meeting demand (`Demand`):

    - 2020
    Service 0
    Demand 14614
    - 2021
    Service 0
    Demand 3293

More details are provided in the [Getting
Started](https://cdcam.readthedocs.io/en/latest/getting-started.html) documentation.

Contributions
-------------

Contributions to this package are welcomed via the usual pull request mechanism.

Support
-------

If you encounter a bug, feel the documentation is incorrect or incomplete, or want to suggest
new features, please post an issue in the [issues](https://github.com/nismod/cdcam/issues) tab.


DAFNI
=====

[DAFNI](https://www.dafni.ac.uk) provides another environment to run the model.

To prepare the model for DAFNI, there are two elements:
- build a docker container image, and upload as a DAFNI model
- prepare the project data files, and upload as DAFNI datasets

DAFNI model
-----------

To build a docker image, install docker and check out this repository.

The Dockerfile defines how the model image is built. The image includes a python
environment with `cdcam` installed, and the `run.py` and `dafni-run.sh` scripts.

To build and export, run:

```bash
docker build . -t nismod/cdcam
docker save nismod/cdcam | gzip > cdcam.tar.gz
```

Then upload the `cdcam.tar.gz` file along with the `dafni-model-definition.yml`
as a model to DAFNI.

DAFNI data
----------

The DAFNI model uses "dataslots" to input the project data files. Initially, the
project sample data package (also available on Zenodo) has been uploaded.


Background and funding
======================

The **Cambridge Digital Communications Assessment Model** has been collaboratively developed
between the [Environmental Change Institute](http://www.eci.ox.ac.uk/) at the [University of
Oxford](https://www.ox.ac.uk/), the [Networks and Operating Systems Group
(NetOS)](http://www.cl.cam.ac.uk/research/srg/netos) at the [Cambridge Computer
Laboratory](http://www.cl.cam.ac.uk),  and the UK's [Digital
Catapult](http://www.digtalcatapult.org.uk). Research activity between 2017-2018 also took
place at the [Cambridge Judge Business School](http://www.jbs.cam.ac.uk/home/) at the
[University of Cambridge](http://www.cam.ac.uk/).

Development has been funded by the EPSRC via (i) the [Infrastructure Transitions Research
Consortium](http://www.itrc.org.uk/) (EP/N017064/1) and (ii) the UK's [Digital
Catapult](http://www.digicatapult.org.uk) Researcher in Residence programme.

Contributors
============
- Edward J. Oughton (University of Oxford)
- Tom Russell (University of Oxford)
