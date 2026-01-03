# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Defect formation energy data class."""
from dataclasses import dataclass
from typing import Dict, Optional

from monty.json import MSONable


@dataclass
class FormationEnergy(MSONable):
    """Formation energy for a single defect charge state.

    Stores the formation energy and energy corrections for a specific
    defect charge state. The formation energy is typically calculated
    at the Fermi level equal to VBM.

    Attributes:
        formation_energy: Formation energy in eV (without corrections).
        energy_corrections: Dict of correction name to energy value in eV.
            Common corrections include "efnv" (FNV electrostatic correction)
            and "alignment" (potential alignment).
        is_shallow: Whether this defect is a shallow donor/acceptor.
            True indicates the defect level is resonant with the band.

    Example:
        >>> energy = FormationEnergy(
        ...     formation_energy=1.5,
        ...     energy_corrections={"efnv": 0.1, "alignment": -0.05}
        ... )
        >>> energy.total_correction
        0.05
        >>> energy.get_energy(with_correction=True)
        1.55
    """
    formation_energy: float
    energy_corrections: Dict[str, float] = None
    is_shallow: Optional[bool] = None

    @property
    def total_correction(self) -> float:
        """Calculate total energy correction.

        Returns:
            Sum of all energy corrections in eV. Returns 0.0 if no corrections.
        """
        if self.energy_corrections:
            return sum([v for v in self.energy_corrections.values()])
        return 0.0

    def get_energy(self, with_correction: bool = True) -> float:
        """Get formation energy with or without corrections.

        Args:
            with_correction: If True, include energy corrections.

        Returns:
            Formation energy in eV.
        """
        if with_correction:
            return self.formation_energy + self.total_correction
        return self.formation_energy

    # Backward compatibility
    def energy(self, with_correction: bool = True) -> float:
        """Deprecated: Use get_energy() instead."""
        return self.get_energy(with_correction)


# Backward compatibility alias
DefectEnergy = FormationEnergy
