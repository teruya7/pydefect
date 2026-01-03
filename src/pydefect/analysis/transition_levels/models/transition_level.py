# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
"""Transition level data class for a single defect."""

from dataclasses import dataclass
from typing import List

from monty.json import MSONable


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
