API Reference
=============

Programmatic interface for pydefect.

.. toctree::
   :maxdepth: 2

   pydefect_api
   analyzer
   input_maker
   cli_reference

Core API
--------

The recommended entry point for programmatic use:

.. code-block:: python

    from pydefect import api

    # Load data
    calc_results = api.load_calc_results("calc_results.json")
    unitcell = api.load_unitcell("unitcell.yaml")
    
    # Create correction
    correction = api.make_efnv_correction(
        defect_entry, calc_results, perfect_calc_results
    )

See :doc:`pydefect_api` for details.
