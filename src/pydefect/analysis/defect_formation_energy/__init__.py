# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Defect formation energy analysis module.

This module provides classes and functions for analyzing defect formation energies:

Data Models:
- DefectFormationEnergy: Formation energy for a single charge state
- FormationEnergyInfo: Complete info for a defect's energy
- FormationEnergyCollection: Collection of energies at multiple charges
- FormationEnergySummary: Summary of all defect energies
- FermiLevelDependentEnergies: Energies as functions of Fermi level
- ChargeStateEnergies: Energies at different charge states
- CrossPoints: Transition level crossing points

Functions:
- calculate_formation_energy_info: Calculate formation energy from VASP
- calculate_formation_energy_summary: Create summary from multiple defects
- calculate_u_values: Calculate Hubbard U values

Plotting:
- FormationEnergyMplPlotter: Matplotlib plotter
- PlotSettings: Plot configuration
"""
from pydefect.analysis.defect_formation_energy.models import (
    # New names
    DefectFormationEnergy,
    FormationEnergyInfo,
    FormationEnergyCollection,
    FormationEnergySummary,
    FermiLevelDependentEnergies,
    ChargeStateEnergies,
    CrossPoints,
    # Backward compatibility
    DefectEnergy,
    DefectEnergyInfo,
    DefectEnergies,
    DefectEnergySummary,
    ChargeEnergies,
    SingleChargeEnergies,
)

from pydefect.analysis.defect_formation_energy.defect_formation_energy import (
    calculate_formation_energy_info,
    calculate_formation_energy_summary,
    calculate_composition_change,
    # Backward compatibility
    make_defect_energy_info,
    make_defect_energy_summary,
    num_atom_differences,
)

from pydefect.analysis.defect_formation_energy.u_value import (
    calculate_u_values,
    # Backward compatibility
    u_values_from_defect_energies,
)

from pydefect.analysis.defect_formation_energy.plotter import (
    FormationEnergyMplPlotter,
    FormationEnergyPlotterBase,
    PlotSettings,
    # Backward compatibility
    DefectEnergyMplPlotter,
    DefectEnergyPlotter,
    DefectEnergiesMplSettings,
)
