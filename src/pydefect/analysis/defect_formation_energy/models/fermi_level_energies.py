# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Fermi level dependent energies data classes."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from monty.json import MSONable
from scipy.spatial import HalfspaceIntersection

from pydefect.analysis.defect_formation_energy.models.cross_points import CrossPoints


@dataclass
class ChargeStateEnergies(MSONable):
    """Energies for a single defect at multiple charge states.

    Stores the energy at each charge state at E_F=0
    (with VBM set to 0).

    Attributes:
        charge_energies: List of (charge, energy) tuples.
    """
    charge_energies: List[Tuple[int, float]]

    def pinning_level(self, e_min: float, e_max: float
                      ) -> Tuple[Tuple[float, Optional[int]],
                                 Tuple[float, Optional[int]]]:
        """Calculate Fermi level pinning positions.

        Returns:
            ((Lower pinning, its charge), (Upper pinning, its charge))
        """
        lower_pinning, upper_pinning = float("-inf"), float("inf")
        lower_charge, upper_charge = None, None
        for charge, energy in self.charge_energies:
            if charge == 0:
                continue
            pinning = - energy / charge
            if charge > 0 and pinning > lower_pinning:
                lower_pinning, lower_charge = pinning, charge
            elif charge < 0 and pinning < upper_pinning:
                upper_pinning, upper_charge = pinning, charge

        if lower_charge is None or lower_pinning < e_min:
            lower = None
        else:
            lower = (lower_pinning, lower_charge)

        if upper_charge is None or upper_pinning > e_max:
            upper = None
        else:
            upper = (upper_pinning, upper_charge)
        return lower, upper

    def charge_energies_at_ef(self, ef: float) -> List[Tuple[int, float]]:
        """Get charge energies at a given Fermi level.

        Args:
            ef: Fermi level position.

        Returns:
            List of (charge, energy) at the given Fermi level.
        """
        result = []
        for charge, energy in self.charge_energies:
            result.append((charge, energy + charge * ef))
        return result

    def energy_at_ef(self, ef: float) -> Tuple[float, int]:
        """Get lowest energy and its charge at a given Fermi level.

        Args:
            ef: Fermi level position.

        Returns:
            (Lowest energy, its charge)
        """
        result_e, result_charge = float("inf"), None
        for charge, energy in self.charge_energies:
            energy = energy + charge * ef
            if energy < result_e:
                result_e, result_charge = energy, charge
        return result_e, result_charge


@dataclass
class FermiLevelDependentEnergies:
    """Formation energies as functions of Fermi level.

    Calculates transition levels and pinning levels from
    charge-dependent formation energies.

    Attributes:
        charge_energies_dict: Dict of defect name to ChargeStateEnergies.
        e_min: Minimum Fermi level (typically 0, VBM).
        e_max: Maximum Fermi level (CBM).
    """
    charge_energies_dict: Dict[str, ChargeStateEnergies]
    e_min: float
    e_max: float
    _cross_point_dicts: dict = None
    _e_min_max_energies_dict: dict = None

    @property
    def cross_point_dicts(self) -> Dict[str, CrossPoints]:
        """Get transition level crossing points."""
        if self._cross_point_dicts:
            return self._cross_point_dicts
        self.calculate_transition_levels()
        return self._cross_point_dicts

    @property
    def e_min_max_energies_dict(self) -> dict:
        """Get min/max energies dictionary."""
        if self._e_min_max_energies_dict:
            return self._e_min_max_energies_dict
        self.calculate_transition_levels()
        return self._e_min_max_energies_dict

    def calculate_transition_levels(self) -> None:
        """Calculate charge state transition cross points."""
        self._cross_point_dicts = {}
        self._e_min_max_energies_dict = {}
        large_minus_number = -1e4
        for defect_name, charge_state_energies in self.charge_energies_dict.items():
            half_spaces = []
            e_min_max_energies = []
            for charge, energy in charge_state_energies.charge_energies:
                half_spaces.append([-charge, 1, -energy])
                e_min_max_energies.append([energy,
                                           energy + self.e_max * charge])

            half_spaces.append([-1, 0, self.e_min])
            half_spaces.append([1, 0, -self.e_max])
            half_spaces.append([0, -1, large_minus_number])

            feasible_point = np.array([(self.e_min + self.e_max) / 2, -1e3])

            hs = HalfspaceIntersection(np.array(half_spaces), feasible_point)
            boundary_points = []
            inner_cross_points = []
            for intersection in hs.intersections:
                x, y = np.round(intersection, 8)
                if self.e_min + 0.001 < x < self.e_max - 0.001:
                    inner_cross_points.append([x, y])
                elif y > large_minus_number + 1:
                    boundary_points.append([x, y])

            self._cross_point_dicts[defect_name] = CrossPoints(inner_cross_points,
                                                        boundary_points)
            self._e_min_max_energies_dict[defect_name] = e_min_max_energies

    def energy_range(self, space: float) -> List[float]:
        """Get energy range for plotting."""
        candidates = []
        for cp in self.cross_point_dicts.values():
            candidates.extend(cp.t_all_sorted_points[1])
        return [min(candidates) - space, max(candidates) + space]

    @property
    def pinning_levels(self) -> Dict[str, List[float]]:
        """Get Fermi level pinning positions for all defects."""
        result = {}
        for k, v in self.charge_energies_dict.items():
            pl = v.pinning_level(self.e_min, self.e_max)
            lower = pl[0][0] if pl[0] else None
            upper = pl[1][0] if pl[1] else None
            result[k] = [lower, upper]
        return result

    # Backward compatibility
    def calc_cross_points(self) -> None:
        """Deprecated: Use calculate_transition_levels() instead."""
        self.calculate_transition_levels()


# Backward compatibility aliases
SingleChargeEnergies = ChargeStateEnergies
ChargeEnergies = FermiLevelDependentEnergies
