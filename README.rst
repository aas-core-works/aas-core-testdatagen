***********************
aas-core3.1-testdatagen
***********************

.. image:: https://github.com/aas-core-works/aas-core-testdatagen/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/aas-core-works/aas-core-testdatagen/actions/workflows/ci.yml
    :alt: Continuous integration

Generate test data for AAS elements based on the meta-model.

Installation
============
Check out the repository and change to its directory.

Create a virtual environment:

.. code-block::

    python -m venv venv

Activate it (on Windows):

.. code-block::

    venv/Scripts/activate

... or on Unix:

.. code-block::

    source venv/bin/activate

Install the dependencies:

.. code-block::

    pip3 install .

You can now run ``aas-core3.1-testdatagen`` (see ``--help`` section below).

``--help``
==========

.. Help starts: aas-core-testdatagen --help
.. code-block::

    usage: aas-core-testdatagen [-h] --model_path MODEL_PATH --output_dir
                                OUTPUT_DIR [--version]

    Generate test data for AAS elements based on the meta-model.

    options:
      -h, --help            show this help message and exit
      --model_path MODEL_PATH
                            path to the AAS meta-model
      --output_dir OUTPUT_DIR
                            path to the directory where test data is stored
      --version             show the current version and exit

.. Help ends: aas-core-testdatagen --help

Contributing
============
See `CONTRIBUTING.rst`_.

.. _CONTRIBUTING.rst: CONTRIBUTING.rst
