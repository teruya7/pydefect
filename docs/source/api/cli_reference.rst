CLI Reference
=============

Command-line interface reference.

pydefect
--------

Main commands (DFT-code independent):

.. code-block:: bash

    pydefect s           # Create supercell
    pydefect ds          # Generate defect set
    pydefect sre         # Standard and relative energies
    pydefect cv          # CPD and vertices
    pydefect pc          # Plot CPD
    pydefect pde         # Plot defect energies

pydefect_vasp
-------------

VASP-specific commands:

.. code-block:: bash

    pydefect_vasp u      # Create unitcell.yaml
    pydefect_vasp mp     # Get MP competing phases
    pydefect_vasp mce    # Make composition energies
    pydefect_vasp de     # Create defect entries
    pydefect_vasp cr     # Parse calc results
    pydefect_vasp efnv   # Make EFNV correction
    pydefect_vasp des    # Make defect energy summary

pydefect_util
-------------

Utility commands:

.. code-block:: bash

    pydefect_util ai     # Add interstitials
    pydefect_util pi     # Pop interstitial

pydefect_print
--------------

Print JSON files:

.. code-block:: bash

    pydefect_print supercell_info.json
    pydefect_print defect_entry.json
    pydefect_print calc_results.json
