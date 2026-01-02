# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Radial charge distribution data class."""
from dataclasses import dataclass
from typing import List

from monty.json import MSONable
from vise.util.mix_in import ToJsonFileMixIn
from vise.util.typing import Coords


@dataclass
class RadialChargeDist(MSONable, ToJsonFileMixIn):
    """Radial charge density distribution from defect center.

    Stores the charge density profile as a function of radial distance
    from the defect center, calculated from PARCHG files.

    Attributes:
        defect_center: Fractional coordinates of defect center.
        density_profile: Charge density at each radial bin.

    Example:
        >>> dist = RadialChargeDist(
        ...     defect_center=(0.5, 0.5, 0.5),
        ...     density_profile=[0.1, 0.2, 0.15, 0.05]
        ... )
    """
    defect_center: Coords
    density_profile: List[float]
