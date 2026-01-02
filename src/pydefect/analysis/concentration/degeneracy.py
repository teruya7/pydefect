# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, MutableMapping

from monty.json import MSONable
from ruamel.yaml.scalarint import ScalarInt

from pydefect.analysis.calculation.models import CalcResults
from pydefect.analysis.defect_energy.defect_energy import DefectEnergyInfo
from pydefect.analysis.defect_structure.defect_structure_info import DefectStructureInfo
from pymatgen.symmetry.groups import SpaceGroup
from vise.util.mix_in import ToYamlFileMixIn
from vise.util.structure_symmetrizer import num_symmetry_operation


@dataclass
class Degeneracy(MSONable):
    """Degeneracy factors for a defect charge state.

    Attributes:
        site: Site degeneracy (number of equivalent sites).
        spin: Spin degeneracy (2S+1).
        initial_site_sym: Initial site symmetry before relaxation.
        final_site_sym: Final site symmetry after relaxation.

    Example:
        >>> deg = Degeneracy(site=4, spin=2)
        >>> print(deg.degeneracy)
        8
    """
    site: int
    spin: int
    initial_site_sym: str = None
    final_site_sym: str = None

    @property
    def degeneracy(self) -> int:
        """Get total degeneracy (site * spin)."""
        return self.site * self.spin


@dataclass
class Degeneracies(MutableMapping, ToYamlFileMixIn):
    """Collection of degeneracy data for all defects.

    Dictionary-like mapping of defect name -> charge -> Degeneracy.

    Attributes:
        d: Dict mapping defect name to charge to Degeneracy.
    """
    d: Dict[str, Dict[int, Degeneracy]]

    def __iter__(self):
        return self.d.__iter__()

    def __len__(self) -> int:
        return len(self.d)

    def __getitem__(self, k):
        return self.d[k]

    def __delitem__(self, v) -> None:
        self.d.pop(v)

    def __setitem__(self, k, v) -> None:
        self.d[k] = v

    def as_dict(self):
        """Convert to dictionary for serialization."""
        result = {}
        for defect_name, charges in self.d.items():
            result[defect_name] = {}
            for charge, degeneracy in charges.items():
                deg_dict = degeneracy.as_dict()
                deg_dict.pop("@class")
                deg_dict.pop("@module")
                deg_dict.pop("@version")
                if isinstance(charge, ScalarInt):
                    charge = int(charge)
                result[defect_name][charge] = deg_dict
        return result

    @classmethod
    def from_dict(cls, d):
        """Create from dictionary."""
        result = cls(d)
        for defect_name, charges in result.items():
            for charge, deg_dict in charges.items():
                result[defect_name][charge] = Degeneracy.from_dict(deg_dict)
        return result


class MakeDegeneracy:
    """Calculate degeneracy factors from defect calculations.

    Computes site and spin degeneracy from structure symmetry
    and magnetization.

    Attributes:
        degeneracies: Resulting Degeneracies object.
    """
    def __init__(self,
                 primitive_sg_symbol: str,
                 int_threshold: float = 0.1):
        """Initialize MakeDegeneracy.

        Args:
            primitive_sg_symbol: Space group symbol of primitive cell.
            int_threshold: Threshold for integer magnetization check.
        """
        self._int_threshold = int_threshold
        self._primitive_num_sym_opt = len(SpaceGroup(primitive_sg_symbol))
        self._deg_dict = defaultdict(dict)

    def add_degeneracy(self,
                       energy_info: DefectEnergyInfo,
                       calc_results: CalcResults,
                       structure_info: DefectStructureInfo):
        spin = self.mag_to_spin_degeneracy(calc_results.magnetization)
        site = (self._primitive_num_sym_opt
                / num_symmetry_operation(structure_info.final_site_sym))

        degeneracy = Degeneracy(int(site), spin,
                                structure_info.initial_site_sym,
                                structure_info.final_site_sym)
        self._deg_dict[energy_info.name][energy_info.charge] = degeneracy

    def mag_to_spin_degeneracy(self, mag: float) -> int:
        rounded_mag = round(mag)
        if abs(rounded_mag - mag) > self._int_threshold:
            raise ValueError
        return 2 * abs(rounded_mag) + 1

    @property
    def degeneracies(self):
        return Degeneracies(self._deg_dict)
