Installation
============

Requirements
------------

- Python 3.9 or later
- VASP (Vienna Ab-initio Simulation Package)
- Materials Project API key (for retrieving competing phases)

Install pydefect
----------------

Install from PyPI:

.. code-block:: bash

    pip install pydefect

Or install from source:

.. code-block:: bash

    git clone https://github.com/kumagai-group/pydefect.git
    cd pydefect
    pip install -e .

Dependencies
------------

pydefect automatically installs the following dependencies:

- `pymatgen <https://pymatgen.org>`_ - Crystal structure manipulation
- `vise <https://kumagai-group.github.io/vise/>`_ - VASP input generation
- `monty <https://github.com/materialsvirtuallab/monty>`_ - Serialization utilities
- `numpy`, `scipy` - Numerical computations
- `matplotlib` - Plotting

Configuration
-------------

1. Create ``~/.pmgrc.yaml`` with your Materials Project API key:

.. code-block:: yaml

    PMG_DEFAULT_FUNCTIONAL: PBE_54
    PMG_MAPI_KEY: your_api_key_here
    PMG_VASP_PSP_DIR: /path/to/potcars/

2. (Optional) Create ``pydefect.yaml`` in your project directory to override defaults:

.. code-block:: yaml

    symmetry_length_tolerance: 0.1
    ewald_accuracy: 15.0

Verify Installation
-------------------

.. code-block:: bash

    python -c "import pydefect; print(pydefect.__version__)"

Next Steps
----------

Continue to :doc:`quick_start` for a brief overview of pydefect.
