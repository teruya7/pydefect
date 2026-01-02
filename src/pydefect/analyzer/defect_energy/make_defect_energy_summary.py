# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from itertools import groupby
from typing import List, Dict

from pydefect.analyzer.band_edge.band_edge_states import PerfectBandEdgeState
from pydefect.analyzer.defect_energy.defect_energy import DefectEnergyInfo, \
    DefectEnergySummary, DefectEnergies
from pydefect.analyzer.unitcell.unitcell import Unitcell
from pydefect.analyzer.chemical_potential.chem_pot_diag import TargetVertices


def make_defect_energy_summary(
        energy_infos: List[DefectEnergyInfo],
        target_vertices: TargetVertices,
        unitcell: Unitcell,
        perfect_band_edge: PerfectBandEdgeState) -> DefectEnergySummary:
    """Create DefectEnergySummary from individual energy calculations.

    Args:
        energy_infos: List of DefectEnergyInfo for all defects.
        target_vertices: Chemical potential vertices for target composition.
        unitcell: Unit cell properties.
        perfect_band_edge: Perfect supercell band edge states.

    Returns:
        DefectEnergySummary containing all defect energies.

    Example:
        >>> summary = make_defect_energy_summary(
        ...     energy_infos, target_vertices, unitcell, p_band_edge
        ... )
        >>> summary.to_json_file()
    """
    defect_energies = {}
    sort_key = lambda energy_info: energy_info.name
    # MUST NEED SORTED.
    for _, grouped_infos in groupby(sorted(energy_infos, key=sort_key), key=sort_key):
        grouped_infos = list(grouped_infos)
        defect_name = grouped_infos[0].name
        atom_count_changes = grouped_infos[0].atom_io
        charges = []
        defect_energy_list = []
        for energy_info in grouped_infos:
            try:
                assert sorted(atom_count_changes) == sorted(energy_info.atom_io)
            except AssertionError:
                print(atom_count_changes, energy_info.atom_io)
                raise

            charges.append(energy_info.charge)
            defect_energy_list.append(energy_info.defect_energy)
        defect_energies[defect_name] = DefectEnergies(
            atom_count_changes, charges, defect_energy_list)

    return DefectEnergySummary(title=unitcell.system,
                               defect_energies=defect_energies,
                               rel_chem_pots=target_vertices.chem_pots,
                               cbm=unitcell.cbm - unitcell.vbm,
                               supercell_vbm=perfect_band_edge.vbm_info.energy - unitcell.vbm,
                               supercell_cbm=perfect_band_edge.cbm_info.energy - unitcell.vbm)
