# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
"""Degeneracy calculation."""

from collections import defaultdict

from pydefect.analysis.calc_results.models import CalcResults
from pydefect.analysis.concentration.models import Degeneracy, Degeneracies
from pydefect.analysis.formation_energy.models import FormationEnergyInfo
from pydefect.analysis.structure.models import DefectStructureInfo
from pymatgen.symmetry.groups import SpaceGroup
from vise.util.structure_symmetrizer import num_symmetry_operation


class DegeneracyCalculator:
    """Calculate degeneracy factors from defect calculations.

    Computes site and spin degeneracy from structure symmetry
    and magnetization.

    Attributes:
        degeneracies: Resulting Degeneracies object.
    """
    def __init__(self,
                 primitive_sg_symbol: str,
                 int_threshold: float = 0.1):
        """Initialize DegeneracyCalculator.

        Args:
            primitive_sg_symbol: Space group symbol of primitive cell.
            int_threshold: Threshold for integer magnetization check.
        """
        self._int_threshold = int_threshold
        self._primitive_num_sym_opt = len(SpaceGroup(primitive_sg_symbol))
        self._deg_dict = defaultdict(dict)

    def add_degeneracy(self,
                       energy_info: FormationEnergyInfo,
                       calc_results: CalcResults,
                       structure_info: DefectStructureInfo):
        """Add degeneracy for a defect charge state."""
        spin = self.mag_to_spin_degeneracy(calc_results.magnetization)
        site = (self._primitive_num_sym_opt
                / num_symmetry_operation(structure_info.final_site_sym))

        degeneracy = Degeneracy(int(site), spin,
                                structure_info.initial_site_sym,
                                structure_info.final_site_sym)
        self._deg_dict[energy_info.name][energy_info.charge] = degeneracy

    def mag_to_spin_degeneracy(self, mag: float) -> int:
        """Convert magnetization to spin degeneracy."""
        rounded_mag = round(mag)
        if abs(rounded_mag - mag) > self._int_threshold:
            raise ValueError
        return 2 * abs(rounded_mag) + 1

    @property
    def degeneracies(self):
        """Get calculated degeneracies."""
        return Degeneracies(self._deg_dict)


# Backward compatibility alias
MakeDegeneracy = DegeneracyCalculator
