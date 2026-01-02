Workflow Overview
=================

This page provides an overview of the pydefect workflow for point-defect calculations.

.. image:: /_images/pydefect.png
   :width: 700px
   :align: center

Key Concepts
------------

Point-defect calculations require three main components:

1. **Host Material Properties**
   
   - Relaxed crystal structure
   - Band edges (VBM and CBM)
   - Dielectric constants (electronic and ionic)

2. **Chemical Potential Diagram**
   
   - Competing phases and their energies
   - Chemical potentials at equilibrium conditions
   - Stability region of the host material

3. **Defect Calculations**
   
   - Supercell with appropriate size
   - Defect structures for each charge state
   - Electrostatic corrections (EFNV)
   - Formation energy analysis

Workflow Steps
--------------

.. list-table::
   :widths: 10 40 50
   :header-rows: 1

   * - Step
     - Task
     - Output
   * - 1
     - Relax unit cell
     - ``CONTCAR``
   * - 2
     - Calculate band structure
     - VBM, CBM
   * - 3
     - Calculate dielectric constants
     - ``unitcell.yaml``
   * - 4
     - Prepare competing phases
     - ``composition_energies.yaml``
   * - 5
     - Generate chemical potential diagram
     - ``cpd.pdf``, ``cpd_and_vertices.yaml``
   * - 6
     - Create supercell
     - ``supercell_info.json``
   * - 7
     - Define defect species
     - ``defect_in.yaml``
   * - 8
     - Create defect structures
     - ``defect_entry.json`` per defect
   * - 9
     - Run defect calculations
     - ``vasprun.xml``, ``OUTCAR``
   * - 10
     - Analyze results
     - ``calc_results.json``
   * - 11
     - Apply corrections
     - ``correction.json``
   * - 12
     - Plot formation energies
     - ``defect_energy.pdf``

Directory Structure
-------------------

.. code-block:: text

    project_name/
    │
    ├── pydefect.yaml          # pydefect configuration
    ├── vise.yaml              # vise configuration
    │
    ├── unitcell/
    │   ├── structure_opt/     # Step 1: Structure relaxation
    │   ├── band/              # Step 2: Band structure
    │   ├── dos/               # Step 2: Density of states
    │   └── dielectric/        # Step 3: Dielectric constants
    │
    ├── cpd/                   # Step 4-5: Competing phases
    │   ├── MgO_mp-1265/
    │   ├── Al2O3_mp-1143/
    │   └── ...
    │
    └── defect/                # Step 6-12: Defect calculations
        ├── perfect/
        ├── Va_O1_0/
        ├── Va_O1_1/
        └── ...

Continue to the next sections for detailed instructions on each step.
