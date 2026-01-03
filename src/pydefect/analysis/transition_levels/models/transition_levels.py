# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
"""Collection of transition levels for all defects."""

from dataclasses import dataclass
from itertools import zip_longest
from typing import List

from monty.json import MSONable
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn

from pydefect.analysis.transition_levels.models.transition_level import TransitionLevel


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
