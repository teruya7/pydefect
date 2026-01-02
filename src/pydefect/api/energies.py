# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for chemical potential and defect energy calculations.

This module provides functions for creating chemical potential diagrams
and calculating defect formation energies.
"""

from typing import List, Optional, Union

from pymatgen.core import Composition

from pydefect.analyzer.calc_results import CalcResults
from pydefect.analyzer.defect_energy import DefectEnergyInfo
from pydefect.analyzer.make_defect_energy_info import (
    make_defect_energy_info as _make_defect_energy_info,
)
from pydefect.analyzer.make_defect_energy_summary import (
    make_defect_energy_summary as _make_defect_energy_summary,
)
from pydefect.analyzer.unitcell import Unitcell
from pydefect.analyzer.chem_pot_diag.chem_pot_diag import (
    CompositionEnergies,
    RelativeEnergies,
    StandardEnergies,
    ChemPotDiag,
    ChemPotDiagMaker,
    TargetVertices,
)
from pydefect.analyzer.corrections.abstract_correction import Correction
from pydefect.analyzer.corrections.no_correction import NoCorrection
from pydefect.input_maker.defect_entry import DefectEntry


def make_standard_and_relative_energies(
    composition_energies: CompositionEnergies,
) -> tuple:
    """Calculate standard and relative energies from composition energies.

    Args:
        composition_energies: CompositionEnergies object containing
            formation energies for all compositions.

    Returns:
        Tuple of (StandardEnergies, RelativeEnergies)

    Example:
        >>> from pydefect import api
        >>> comp_energies = CompositionEnergies.from_yaml("composition_energies.yaml")
        >>> std_energies, rel_energies = api.make_standard_and_relative_energies(comp_energies)
        >>> std_energies.to_yaml_file()
        >>> rel_energies.to_yaml_file()
    """
    std_energies, rel_energies = composition_energies.std_rel_energies
    return std_energies, rel_energies


def make_chem_pot_diag(
    relative_energies: RelativeEnergies,
    target: Optional[str] = None,
    elements: Optional[List[str]] = None,
) -> ChemPotDiag:
    """Create a chemical potential diagram.

    Args:
        relative_energies: RelativeEnergies object.
        target: Target composition string (e.g., "MgO").
        elements: List of elements to include in diagram.
            If not provided, derived from target or all elements in rel_energies.

    Returns:
        ChemPotDiag object containing the chemical potential diagram.

    Example:
        >>> from pydefect import api
        >>> rel_energies = RelativeEnergies.from_yaml("relative_energies.yaml")
        >>> cpd = api.make_chem_pot_diag(rel_energies, target="MgO")
        >>> cpd.to_json_file()
    """
    if target:
        elements = elements or Composition(target).chemical_system.split("-")
    else:
        elements = elements or list(relative_energies.all_element_set)

    cpd_maker = ChemPotDiagMaker(relative_energies, elements, target)
    return cpd_maker.chem_pot_diag


def make_defect_energy_info(
    defect_entry: DefectEntry,
    calc_results: CalcResults,
    perfect_calc_results: CalcResults,
    standard_energies: StandardEnergies,
    unitcell: Unitcell,
    correction: Optional[Correction] = None,
    band_edge_states=None,
) -> DefectEnergyInfo:
    """Calculate defect energy information.

    Args:
        defect_entry: DefectEntry object for the defect.
        calc_results: CalcResults from defect calculation.
        perfect_calc_results: CalcResults from perfect supercell.
        standard_energies: StandardEnergies for element references.
        unitcell: Unitcell object with band edge information.
        correction: Correction object (e.g., EfnvCorrection).
            If None, NoCorrection is applied.
        band_edge_states: Optional band edge states information.

    Returns:
        DefectEnergyInfo object.

    Example:
        >>> from pydefect import api
        >>> energy_info = api.make_defect_energy_info(
        ...     defect_entry, calc_results, perfect_calc_results,
        ...     std_energies, unitcell, correction=efnv_correction
        ... )
        >>> energy_info.to_yaml_file()
    """
    if correction is None:
        correction = NoCorrection()

    return _make_defect_energy_info(
        defect_entry=defect_entry,
        calc_results=calc_results,
        correction=correction,
        perfect_calc_results=perfect_calc_results,
        standard_energies=standard_energies,
        unitcell=unitcell,
        band_edge_states=band_edge_states,
    )


def make_defect_energy_summary(
    energy_infos: List[DefectEnergyInfo],
    target_vertices: TargetVertices,
    unitcell: Unitcell,
    perfect_band_edge_state=None,
):
    """Create a defect energy summary from multiple defect energy infos.

    Args:
        energy_infos: List of DefectEnergyInfo objects.
        target_vertices: TargetVertices specifying chemical potential vertices.
        unitcell: Unitcell object.
        perfect_band_edge_state: Optional perfect band edge state.

    Returns:
        DefectEnergySummary object.

    Example:
        >>> from pydefect import api
        >>> summary = api.make_defect_energy_summary(
        ...     energy_infos, target_vertices, unitcell
        ... )
        >>> summary.to_json_file()
    """
    return _make_defect_energy_summary(
        energy_infos, target_vertices, unitcell, perfect_band_edge_state
    )
