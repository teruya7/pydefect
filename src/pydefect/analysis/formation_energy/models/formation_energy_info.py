# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Formation energy info data class."""
from dataclasses import dataclass
from typing import Dict

from monty.json import MSONable
from monty.serialization import loadfn
from vise.util.mix_in import ToYamlFileMixIn

from pydefect.analysis.formation_energy.models.defect_formation_energy import (
    DefectFormationEnergy,
)


@dataclass
class FormationEnergyInfo(MSONable, ToYamlFileMixIn):
    """Complete information for a defect's formation energy analysis.

    Stores defect identification, atomic changes, and energy data.
    Formation energy is referenced to elemental standard states
    and calculated at Fermi level = VBM.

    Attributes:
        name: Defect name following convention (e.g., "Va_O1" for oxygen
            vacancy, "Mg_Al1" for Mg substitution on Al site).
        charge: Charge state of the defect (positive for donors).
        atom_io: Dict of element symbol to count change.
            Positive values indicate atoms added, negative indicate removed.
        formation_energy: DefectFormationEnergy object with energy and corrections.

    Example:
        >>> info = FormationEnergyInfo(
        ...     name="Va_O1",
        ...     charge=2,
        ...     atom_io={"O": -1},
        ...     formation_energy=DefectFormationEnergy(formation_energy=5.2)
        ... )
        >>> print(info.name, info.charge)
        Va_O1 2
    """
    name: str
    charge: int
    atom_io: Dict[str, int]
    formation_energy: DefectFormationEnergy

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        lines = [f"name: {self.name}",
                 f"charge: {self.charge}",
                 f"formation_energy: {self.formation_energy.formation_energy}",
                 f"atom_io:"]
        for k, v in self.atom_io.items():
            lines.append(f"  {k}: {v}")
        lines.append(f"energy_corrections:")
        for k, v in self.formation_energy.energy_corrections.items():
            lines.append(f"  {k}: {v}")
        is_shallow = "" if self.formation_energy.is_shallow is None \
            else self.formation_energy.is_shallow
        lines.append(f"is_shallow: {is_shallow}")
        return "\n".join(lines)

    @classmethod
    def from_yaml(cls, filename: str = "formation_energy_info.yaml"
                  ) -> "FormationEnergyInfo":
        """Load from YAML file."""
        d = loadfn(filename)
        if d["atom_io"] is None:
            d["atom_io"] = {}
        if d["energy_corrections"] is None:
            d["energy_corrections"] = {}
        return cls(d.pop("name"), d.pop("charge"), d.pop("atom_io"),
                   DefectFormationEnergy(**d))

    # Properties for backward compatibility
    @property
    def defect_energy(self) -> DefectFormationEnergy:
        """Deprecated: Use formation_energy instead."""
        return self.formation_energy


# Backward compatible class
class DefectEnergyInfo(FormationEnergyInfo):
    """Backward compatible alias for FormationEnergyInfo."""

    def __init__(self, name, charge, atom_io, defect_energy=None, formation_energy=None):
        energy = formation_energy if formation_energy is not None else defect_energy
        super().__init__(name=name, charge=charge, atom_io=atom_io, formation_energy=energy)
