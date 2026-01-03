# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Calculate defect formation energy from VASP results."""
from collections import defaultdict
from itertools import groupby
from typing import Dict, List

from pydefect.analysis.band_edge.models import BandEdgeStates, PerfectBandEdgeState
from pydefect.analysis.calculation.models import CalcResults
from pydefect.analysis.formation_energy.models import (
    FormationEnergy,
    FormationEnergyInfo,
    FormationEnergyCollection,
    FormationEnergySummary,
)
from pydefect.analysis.unitcell.models import Unitcell
from pydefect.analysis.chemical_potential.models import StandardEnergies, TargetVertices
from pydefect.analysis.corrections.models import Correction
from pydefect.makers.defect.defect_entry import DefectEntry
from pymatgen.core import IStructure


def calculate_formation_energy_info(
        defect_entry: DefectEntry,
        calc_results: CalcResults,
        correction: Correction,
        perfect_calc_results: CalcResults,
        standard_energies: StandardEnergies,
        unitcell: Unitcell,
        band_edge_states: BandEdgeStates = None
) -> FormationEnergyInfo:
    """Calculate formation energy info for a defect calculation.

    Args:
        defect_entry: Defect specification.
        calc_results: Defect calculation results.
        correction: Electrostatic correction.
        perfect_calc_results: Perfect supercell results.
        standard_energies: Elemental reference energies.
        unitcell: Unit cell properties.
        band_edge_states: Optional band edge analysis.

    Returns:
        FormationEnergyInfo with formation energy.

    Example:
        >>> info = calculate_formation_energy_info(
        ...     defect_entry, calc_results, correction,
        ...     perfect_results, std_energies, unitcell
        ... )
        >>> info.to_json_file()
    """
    atom_count_changes = calculate_composition_change(
        calc_results.structure, perfect_calc_results.structure)

    formation_energy = calc_results.energy - perfect_calc_results.energy
    formation_energy += defect_entry.charge * unitcell.vbm
    for element, count in atom_count_changes.items():
        formation_energy -= standard_energies[element] * count

    is_shallow = band_edge_states.is_shallow if band_edge_states else None
    defect_formation_energy = FormationEnergy(
        formation_energy=formation_energy,
        energy_corrections=correction.correction_dict,
        is_shallow=is_shallow)

    return FormationEnergyInfo(
        defect_entry.name,
        defect_entry.charge,
        atom_io=atom_count_changes,
        formation_energy=defect_formation_energy)


def calculate_formation_energy_summary(
        energy_infos: List[FormationEnergyInfo],
        target_vertices: TargetVertices,
        unitcell: Unitcell,
        perfect_band_edge: PerfectBandEdgeState
) -> FormationEnergySummary:
    """Create FormationEnergySummary from individual energy calculations.

    Args:
        energy_infos: List of FormationEnergyInfo for all defects.
        target_vertices: Chemical potential vertices for target composition.
        unitcell: Unit cell properties.
        perfect_band_edge: Perfect supercell band edge states.

    Returns:
        FormationEnergySummary containing all defect energies.

    Example:
        >>> summary = calculate_formation_energy_summary(
        ...     energy_infos, target_vertices, unitcell, p_band_edge
        ... )
        >>> summary.to_json_file()
    """
    formation_energies = {}
    sort_key = lambda energy_info: energy_info.name
    # MUST NEED SORTED.
    for _, grouped_infos in groupby(sorted(energy_infos, key=sort_key), key=sort_key):
        grouped_infos = list(grouped_infos)
        defect_name = grouped_infos[0].name
        atom_count_changes = grouped_infos[0].atom_io
        charges = []
        defect_formation_energies = []
        for energy_info in grouped_infos:
            try:
                assert sorted(atom_count_changes) == sorted(energy_info.atom_io)
            except AssertionError:
                print(atom_count_changes, energy_info.atom_io)
                raise

            charges.append(energy_info.charge)
            defect_formation_energies.append(energy_info.formation_energy)
        formation_energies[defect_name] = FormationEnergyCollection(
            atom_count_changes, charges, defect_formation_energies)

    return FormationEnergySummary(
        title=unitcell.system,
        formation_energies=formation_energies,
        rel_chem_pots=target_vertices.chem_pots,
        cbm=unitcell.cbm - unitcell.vbm,
        supercell_vbm=perfect_band_edge.vbm_info.energy - unitcell.vbm,
        supercell_cbm=perfect_band_edge.cbm_info.energy - unitcell.vbm)


def calculate_composition_change(
        structure: IStructure,
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
    reference_composition = defaultdict(float, **ref_structure.composition.as_dict())
    result = {}
    all_elements = set(target_composition.keys()) | set(reference_composition.keys())
    for element in all_elements:
        atom_count_diff = int(target_composition[element] - reference_composition[element])
        if atom_count_diff:
            result[element] = atom_count_diff
    return result


# Backward compatibility aliases
make_defect_energy_info = calculate_formation_energy_info
make_defect_energy_summary = calculate_formation_energy_summary
num_atom_differences = calculate_composition_change
