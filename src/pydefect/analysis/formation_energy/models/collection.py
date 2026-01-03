# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Formation energy collection data class."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from monty.json import MSONable

from pydefect.analysis.formation_energy.models.energy import (
    FormationEnergy,
)


@dataclass
class FormationEnergyCollection(MSONable):
    """Collection of formation energies for a single defect at multiple charge states.

    Attributes:
        atom_io: Dict of element symbol to count change.
        charges: List of charge states.
        formation_energies: List of FormationEnergy for each charge state.
    """
    atom_io: Dict[str, int]
    charges: List[int]
    formation_energies: List[FormationEnergy] = field(default_factory=list)

    def __post_init__(self):
        """Handle backward compatibility for old attribute name."""
        pass

    def to_yaml(self):
        """Serialize to YAML (not implemented)."""
        pass

    # Backward compatibility property
    @property
    def defect_energies(self) -> List[FormationEnergy]:
        """Deprecated: Use formation_energies instead."""
        return self.formation_energies


def _create_formation_energy_collection(atom_io, charges, formation_energies=None, defect_energies=None):
    """Factory function with backward compatibility for defect_energies parameter."""
    energies = formation_energies if formation_energies is not None else defect_energies
    return FormationEnergyCollection(atom_io=atom_io, charges=charges, formation_energies=energies)


# Create a backward compatible class
class DefectEnergies(FormationEnergyCollection):
    """Backward compatible alias for FormationEnergyCollection."""

    def __init__(self, atom_io, charges, defect_energies=None, formation_energies=None):
        energies = formation_energies if formation_energies is not None else defect_energies
        super().__init__(atom_io=atom_io, charges=charges, formation_energies=energies)
