# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for chemical potential diagram calculations."""

from pathlib import Path
from typing import List, Optional

from pymatgen.core import Composition, Structure
from pymatgen.io.vasp import Outcar

from pydefect.analysis.chemical_potential.models import (
    CompositionEnergy,
    CompositionEnergies,
    RelativeEnergies,
    ChemPotDiag,
    ChemPotDiagMaker,
)


def make_composition_energies(
    directories: List[Path],
    existing_composition_energies: Optional[CompositionEnergies] = None,
) -> CompositionEnergies:
    """Collect composition energies from multiple VASP calculations.

    Args:
        directories: List of directories containing VASP calculations.
        existing_composition_energies: Optional existing CompositionEnergies
            to update (lower energies will overwrite).

    Returns:
        CompositionEnergies object.

    Example:
        >>> from pydefect import api
        >>> comp_energies = api.make_composition_energies(
        ...     [Path("MgO"), Path("Mg"), Path("O2")]
        ... )
        >>> comp_energies.to_yaml_file()
    """
    from vise.defaults import defaults

    if existing_composition_energies:
        composition_energies = existing_composition_energies
    else:
        composition_energies = CompositionEnergies()

    for _dir in directories:
        outcar = Outcar(_dir / defaults.outcar)
        composition = Structure.from_file(_dir / defaults.contcar).composition
        energy = float(outcar.final_energy)
        ce = CompositionEnergy(energy, str(_dir))

        if composition in composition_energies:
            original = composition_energies[composition]
            if ce.energy > original.energy:
                continue  # Skip if new energy is higher

        composition_energies[composition] = ce

    return composition_energies


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
    std_energies, rel_energies = composition_energies.standard_and_relative_energies
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
