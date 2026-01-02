# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from collections import defaultdict
from typing import Dict

from pydefect.analysis.band_edge.models import BandEdgeStates
from pydefect.analysis.calculation.models import CalcResults
from pydefect.analysis.defect_energy.defect_energy import DefectEnergy, DefectEnergyInfo
from pydefect.analysis.unitcell.unitcell import Unitcell
from pydefect.analysis.chemical_potential.chem_pot_diag import StandardEnergies
from pydefect.analysis.corrections.abstract_correction import Correction
from pydefect.makers.defect.defect_entry import DefectEntry
from pymatgen.core import IStructure


def make_defect_energy_info(defect_entry: DefectEntry,
                            calc_results: CalcResults,
                            correction: Correction,
                            perfect_calc_results: CalcResults,
                            standard_energies: StandardEnergies,
                            unitcell: Unitcell,
                            band_edge_states: BandEdgeStates = None
                            ) -> DefectEnergyInfo:
    """Create DefectEnergyInfo for a defect calculation.

    Args:
        defect_entry: Defect specification.
        calc_results: Defect calculation results.
        correction: Electrostatic correction.
        perfect_calc_results: Perfect supercell results.
        standard_energies: Elemental reference energies.
        unitcell: Unit cell properties.
        band_edge_states: Optional band edge analysis.

    Returns:
        DefectEnergyInfo with formation energy.

    Example:
        >>> info = make_defect_energy_info(
        ...     defect_entry, calc_results, correction,
        ...     perfect_results, std_energies, unitcell
        ... )
        >>> info.to_json_file()
    """
    atom_count_changes = num_atom_differences(calc_results.structure,
                                               perfect_calc_results.structure)

    formation_energy = calc_results.energy - perfect_calc_results.energy
    formation_energy += defect_entry.charge * unitcell.vbm
    for element, count in atom_count_changes.items():
        formation_energy -= standard_energies[element] * count

    is_shallow = band_edge_states.is_shallow if band_edge_states else None
    defect_energy = DefectEnergy(formation_energy=formation_energy,
                                  energy_corrections=correction.correction_dict,
                                  is_shallow=is_shallow)

    return DefectEnergyInfo(defect_entry.name, defect_entry.charge,
                            atom_io=atom_count_changes, defect_energy=defect_energy)


def num_atom_differences(structure: IStructure,
                         ref_structure: IStructure,
                         ) -> Dict[str, int]:
    """Calculate atom count difference between structures.

    Args:
        structure: Target structure.
        ref_structure: Reference structure.

    Returns:
        Dict of element symbol to count difference.
    """
    target_composition = defaultdict(float, **structure.composition.as_dict())
    reference_composition = defaultdict(float,
                                        **ref_structure.composition.as_dict())
    result = {}
    all_elements = set(target_composition.keys()) | set(reference_composition.keys())
    for element in all_elements:
        atom_count_diff = int(target_composition[element] - reference_composition[element])
        if atom_count_diff:
            result[element] = atom_count_diff
    return result
