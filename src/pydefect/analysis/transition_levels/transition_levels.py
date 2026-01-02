# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from dataclasses import dataclass
from itertools import zip_longest
from typing import Dict, List

from monty.json import MSONable
from pydefect.analysis.defect_formation_energy.models import CrossPoints
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn


@dataclass
class TransitionLevel(MSONable):
    """Charge state transition level for a single defect.

    Represents the Fermi level position where two charge states
    have equal formation energy.

    Attributes:
        name: Defect name (e.g., "Va_O1").
        charges: List of [initial, final] charge pairs for each transition.
        energies: Formation energies at transition points (eV).
        fermi_levels: Fermi levels where transitions occur (eV from VBM).

    Example:
        >>> tl = TransitionLevel(
        ...     name="Va_O1",
        ...     charges=[[2, 1], [1, 0]],
        ...     energies=[2.5, 3.0],
        ...     fermi_levels=[0.5, 1.2]
        ... )
    """
    name: str
    charges: List[List[int]]  # [[2, 1], [1, 0]]
    energies: List[float]
    fermi_levels: List[float]


@dataclass
class TransitionLevels(MSONable, ToJsonFileMixIn):
    """Collection of transition levels for all defects.

    Contains charge state transition level data for visualization
    and analysis of defect thermodynamics.

    Attributes:
        transition_levels: List of TransitionLevel objects for each defect.
        cbm: Conduction band minimum energy (eV from VBM).
        supercell_vbm: Supercell VBM energy for reference.
        supercell_cbm: Supercell CBM energy.

    Example:
        >>> tls = TransitionLevels.from_json_file("transition_levels.json")
        >>> print(tls)
    """
    transition_levels: List[TransitionLevel]
    cbm: float
    supercell_vbm: float
    supercell_cbm: float

    def __str__(self):
        header = f"vbm: 0.00, cbm: {self.cbm:.2f}, " \
                 f"supercell vbm: {self.supercell_vbm:.2f}, " \
                 f"supercell_cbm: {self.supercell_cbm:.2f}\n"
        result = []
        for transition_level in self.transition_levels:
            if not transition_level.energies:
                continue
            for name, charge, energy, fermi in zip_longest(
                    [transition_level.name], transition_level.charges, 
                    transition_level.energies, transition_level.fermi_levels,
                    fillvalue=""):
                pretty_charges = f"{charge[0]} | {charge[1]}"
                result.append([name, pretty_charges, fermi, energy])
        headers = ["name", "charges", "Fermi level", "Formation energy"]
        floatfmt = ("", "", ".3f", ".3f", "")
        return header + tabulate(result, headers=headers, floatfmt=floatfmt)


def make_transition_levels(cross_point_dicts: Dict[str, CrossPoints],
                           cbm: float,
                           supercell_vbm: float,
                           supercell_cbm: float) -> TransitionLevels:
    """Create TransitionLevels from cross point data.

    Args:
        cross_point_dicts: Dict mapping defect name to CrossPoints.
        cbm: Conduction band minimum (eV from VBM).
        supercell_vbm: Supercell VBM energy.
        supercell_cbm: Supercell CBM energy.

    Returns:
        TransitionLevels object with all transition data.
    """
    transition_levels = []
    for defect_name, cross_point in cross_point_dicts.items():
        charges = [list(charge_pair) for charge_pair in cross_point.charge_list[1:-1]]
        if cross_point.inner_cross_points:
            energies = cross_point.t_inner_cross_points[1]
            fermi_levels = cross_point.t_inner_cross_points[0]
        else:
            energies, fermi_levels = [], []
        transition_levels.append(
            TransitionLevel(defect_name, charges, energies, fermi_levels))

    return TransitionLevels(
        transition_levels, cbm, supercell_vbm, supercell_cbm)

