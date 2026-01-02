Quick Start
===========

This guide gives you a 5-minute overview of pydefect workflow.

Overview
--------

pydefect automates point-defect calculations in non-metallic solids:

.. image:: /_images/pydefect.png
   :width: 600px
   :align: center

The workflow consists of three main parts:

1. **Unitcell**: Relaxed structure, band edges, dielectric constants
2. **Chemical Potential Diagram (CPD)**: Competing phases and chemical potentials
3. **Defect**: Supercell, defect structures, formation energies

Directory Structure
-------------------

We recommend the following directory structure:

.. code-block:: text

    MgAl2O4/
    ├── pydefect.yaml        # Configuration
    ├── vise.yaml
    ├── unitcell/
    │   ├── structure_opt/   # Relaxed structure
    │   ├── band/            # Band structure
    │   ├── dos/             # Density of states
    │   └── dielectric/      # Dielectric constants
    ├── cpd/                 # Competing phases
    │   ├── MgO_mp-xxx/
    │   ├── Al2O3_mp-xxx/
    │   └── ...
    └── defect/              # Defect calculations
        ├── perfect/
        ├── Va_O1_0/
        ├── Va_O1_1/
        └── ...

CLI Commands
------------

pydefect provides five main command-line tools:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Command
     - Description
   * - ``pydefect``
     - Main commands (DFT-code independent)
   * - ``pydefect_vasp``
     - VASP-specific commands
   * - ``pydefect_util``
     - Utility commands
   * - ``pydefect_vasp_util``
     - VASP-specific utilities
   * - ``pydefect_print``
     - Print JSON files in readable format

Use ``-h`` flag to see available options:

.. code-block:: bash

    pydefect s -h

Minimal Example
---------------

Here's a minimal workflow for MgAl₂O₄:

.. code-block:: bash

    # 1. Create supercell
    pydefect s -p unitcell/structure_opt/CONTCAR

    # 2. Generate defect set
    pydefect ds

    # 3. Create defect directories
    pydefect_vasp de

    # 4. (Run VASP calculations)

    # 5. Analyze results
    pydefect_vasp cr -d Va_O1_0
    pydefect_vasp efnv -d Va_O1_0 Va_O1_1 Va_O1_2

    # 6. Plot formation energies
    pydefect_vasp des
    pydefect pde

Next Steps
----------

- :doc:`/user_guide/index` - Detailed step-by-step tutorial
- :doc:`/explanation/index` - Theoretical background
- :doc:`/api/index` - Python API reference
