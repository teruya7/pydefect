# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Displacement data class for atomic displacements."""

from dataclasses import dataclass
from typing import Optional, Tuple

from monty.json import MSONable


@dataclass
class Displacement(MSONable):
    """Atomic displacement from defect relaxation.

    Attributes:
        specie: Element symbol.
        original_pos: Original fractional coordinates before relaxation.
        final_pos: Final fractional coordinates after relaxation.
        distance_from_defect: Distance from the defect center (Å).
        disp_vector: Displacement vector (fractional).
        displace_distance: Magnitude of displacement (Å).
        angle: Angle of displacement relative to defect center (degrees).
    """
    specie: str
    original_pos: Tuple[float, float, float]
    final_pos: Tuple[float, float, float]
    distance_from_defect: float
    disp_vector: Tuple[float, float, float]
    displace_distance: float
    angle: Optional[float]
