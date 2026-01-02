# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Cross points data class for transition levels."""
from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class CrossPoints:
    """Transition level crossing points for a defect.

    Stores Fermi level positions where charge state transitions occur.

    Attributes:
        inner_cross_points: List of [Fermi level, energy] inside band gap.
        boundary_points: List of [Fermi level, energy] at VBM/CBM.
    """
    inner_cross_points: List[List[float]]  # [Fermi level, energy]
    boundary_points: List[List[float]]

    @property
    def all_sorted_points(self) -> List[List[float]]:
        """Get all points sorted by Fermi level."""
        return sorted(self.boundary_points + self.inner_cross_points,
                      key=lambda v: v[0])

    @property
    def t_all_sorted_points(self) -> List[List[float]]:
        """Get transposed all sorted points."""
        return np.transpose(np.array(self.all_sorted_points)).tolist()

    @property
    def t_inner_cross_points(self) -> List[List[float]]:
        """Get transposed inner cross points."""
        return np.transpose(np.array(self.inner_cross_points)).tolist()

    @property
    def t_boundary_points(self) -> List[List[float]]:
        """Get transposed boundary points."""
        return np.transpose(np.array(self.boundary_points)).tolist()

    @property
    def charges(self) -> List[int]:
        """Calculate charge states from slope between points."""
        result = []
        for i, j in zip(self.all_sorted_points[:-1], self.all_sorted_points[1:]):
            dx = j[0] - i[0]
            dy = j[1] - i[1]
            result.append(int(round(dy / dx)))
        return result

    @property
    def charge_list(self) -> List[tuple]:
        """Get list of charge pairs for each segment."""
        charges = [None] + self.charges + [None]
        return list(zip(charges[:-1], charges[1:]))

    @property
    def annotated_charge_positions(self) -> dict:
        """Get positions for annotating charges on plot."""
        result = {}
        for ((x1, y1), (x2, y2)), charge \
                in zip(zip(self.all_sorted_points[:-1],
                           self.all_sorted_points[1:]),
                       self.charges):
            result[charge] = [(x1 + x2) / 2, (y1 + y2) / 2]
        return result
