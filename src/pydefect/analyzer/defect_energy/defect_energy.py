# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

import numpy as np
from monty.json import MSONable
from monty.serialization import loadfn
from pydefect.formatting import prettify_names
from scipy.spatial import HalfspaceIntersection
from tabulate import tabulate
from vise.util.logger import get_logger
from vise.util.mix_in import ToJsonFileMixIn, ToYamlFileMixIn
from vise.util.string import latexify, numbers_to_lowercases


logger = get_logger(__name__)


@dataclass
class DefectEnergy(MSONable):
    """Energy data for a single defect charge state.

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
        >>> energy = DefectEnergy(
        ...     formation_energy=1.5,
        ...     energy_corrections={"efnv": 0.1, "alignment": -0.05}
        ... )
        >>> energy.total_correction
        0.05
        >>> energy.energy(with_correction=True)
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

    def energy(self, with_correction):
        """Get formation energy with or without corrections.

        Args:
            with_correction: If True, include energy corrections.

        Returns:
            Formation energy in eV.
        """
        if with_correction:
            return self.formation_energy + self.total_correction
        return self.formation_energy


@dataclass
class DefectEnergyInfo(MSONable, ToYamlFileMixIn):
    """Complete information for a defect's energy analysis.

    Stores defect identification, atomic changes, and energy data.
    Formation energy is referenced to elemental standard states
    and calculated at Fermi level = VBM.

    Attributes:
        name: Defect name following convention (e.g., "Va_O1" for oxygen
            vacancy, "Mg_Al1" for Mg substitution on Al site).
        charge: Charge state of the defect (positive for donors).
        atom_io: Dict of element symbol to count change.
            Positive values indicate atoms added, negative indicate removed.
        defect_energy: DefectEnergy object with formation energy and corrections.

    Example:
        >>> info = DefectEnergyInfo(
        ...     name="Va_O1",
        ...     charge=2,
        ...     atom_io={"O": -1},
        ...     defect_energy=DefectEnergy(formation_energy=5.2)
        ... )
        >>> print(info.name, info.charge)
        Va_O1 2
    """
    name: str
    charge: int
    atom_io: Dict[str, int]
    defect_energy: DefectEnergy
    # This defect formation energy is estimated at the Fermi level locating at
    # the vbm and references are set to their standard states.

    def to_yaml(self) -> str:
        lines = [f"name: {self.name}",
                 f"charge: {self.charge}",
                 f"formation_energy: {self.defect_energy.formation_energy}",
                 f"atom_io:"]
        for k, v in self.atom_io.items():
            lines.append(f"  {k}: {v}")
        lines.append(f"energy_corrections:")
        for k, v in self.defect_energy.energy_corrections.items():
            lines.append(f"  {k}: {v}")
        is_shallow = "" if self.defect_energy.is_shallow is None \
            else self.defect_energy.is_shallow
        lines.append(f"is_shallow: {is_shallow}")
        return "\n".join(lines)

    @classmethod
    def from_yaml(cls, filename: str = "defect_energy_info.yaml"
                  ) -> "DefectEnergyInfo":
        d = loadfn(filename)
        if d["atom_io"] is None:
            d["atom_io"] = {}
        if d["energy_corrections"] is None:
            d["energy_corrections"] = {}
        return cls(d.pop("name"), d.pop("charge"), d.pop("atom_io"),
                   DefectEnergy(**d))


@dataclass
class DefectEnergies(MSONable):
    atom_io: Dict[str, int]
    charges: List[int]
    defect_energies: List[DefectEnergy]

    def to_yaml(self):
        pass


@dataclass
class DefectEnergySummary(MSONable, ToJsonFileMixIn):
    """Summary of defect formation energies for all defects.

    Contains energies at multiple chemical potential conditions
    and enables Fermi-level-dependent formation energy analysis.
    Energy zero is set at VBM.

    Attributes:
        title: System title (e.g., "MgO").
        defect_energies: Dict of defect name to DefectEnergies.
        rel_chem_pots: Dict of label to element chemical potentials.
        cbm: Supercell CBM energy relative to VBM.
        supercell_vbm: Supercell VBM (typically 0).
        supercell_cbm: Supercell CBM.
    """
    title: str
    # key is a defect name such as "Va_O1".
    defect_energies: Dict[str, "DefectEnergies"]
    rel_chem_pots: Dict[str, Dict[str, float]]
    cbm: float
    supercell_vbm: float
    supercell_cbm: float
    """ The base Fermi level is set at the VBM."""

    def __post_init__(self):
        if self.supercell_cbm < self.cbm - 0.01:
            logger.warning(f"Supercell CBM {self.supercell_cbm} is lower in "
                           f"energy than the unitcell CBM {self.cbm}")

    def screened_defect_energies(self,
                                 allow_shallow: bool,
                                 excluded_defects: List[str] = None
                                 ) -> Dict[str, DefectEnergies]:
        """Filter defect energies based on screening criteria."""
        result = {}
        for defect_name, defect_energies in self.defect_energies.items():
            filtered_charges = []
            filtered_energies = []
            for charge, defect_energy in zip(defect_energies.charges, 
                                              defect_energies.defect_energies):
                if allow_shallow is False and defect_energy.is_shallow is True:
                    continue
                if excluded_defects and f"{defect_name}_{charge}" in excluded_defects:
                    continue
                filtered_charges.append(charge)
                filtered_energies.append(defect_energy)
            result[defect_name] = DefectEnergies(defect_energies.atom_io, 
                                                  filtered_charges, 
                                                  filtered_energies)
        return result

    def __str__(self):
        lines = [f"title: {numbers_to_lowercases(self.title)}",
                 "rel_chem_pots:"]
        chem_pot_lines = []
        for label, element_pots in self.rel_chem_pots.items():
            elem_list = [f"{element}: {potential:.2f}" 
                         for element, potential in element_pots.items()]
            chem_pot_lines.append(f" -{label} " + " ".join(elem_list))
        lines.append('\n'.join(chem_pot_lines))
        lines.append(f"vbm: 0.00, cbm: {self.cbm:.2f}, "
                     f"supercell vbm: {self.supercell_vbm:.2f}, "
                     f"supercell cbm: {self.supercell_cbm:.2f}")
        lines.append("")

        defects = []
        for defect_name, defect_energies in self.defect_energies.items():
            atom_io_str = " ".join(
                [f"{element}: {count}" for element, count in defect_energies.atom_io.items()])
            charges_energies = list(zip(defect_energies.charges, 
                                         defect_energies.defect_energies))
            charges_energies.sort(key=lambda x: x[0])
            for charge, defect_energy in charges_energies:
                defects.append([defect_name, atom_io_str, charge, 
                               defect_energy.formation_energy,
                               defect_energy.total_correction, 
                               defect_energy.is_shallow])
                defect_name, atom_io_str = "", ""
        headers = ("name", "atom_io", "charge", "energy", "correction",
                   "is_shallow")
        floatfmt = ("", "", "", ".3f", ".3f", "")
        lines.append(tabulate(defects, headers=headers, floatfmt=floatfmt))

        return "\n".join(lines)

    def charge_energies(self,
                        chem_pot_label: str,
                        allow_shallow: bool,
                        with_corrections: bool,
                        e_range: Tuple[float, float],
                        name_style: Optional[str] = None
                        ) -> "ChargeEnergies":

        rel_chem_pot = self.rel_chem_pots[chem_pot_label]
        charge_energies_dict = {}
        for defect_name, defect_data in self.screened_defect_energies(allow_shallow).items():
            if not defect_data:
                logger.info(f"defect {defect_name} has no energy data.")
                continue
            charge_energy_list = []
            for charge, defect_energy in zip(defect_data.charges, 
                                              defect_data.defect_energies):
                reservoir_energy = sum([-count * rel_chem_pot[element]
                                       for element, count in defect_data.atom_io.items()])
                energy = defect_energy.energy(with_corrections) + reservoir_energy
                charge_energy_list.append((charge, energy))

            if charge_energy_list:
                charge_energies_dict[defect_name] = SingleChargeEnergies(charge_energy_list)

        if not charge_energies_dict:
            logger.warning(f"No defect data is available. Try to switch on "
                           f"allow_shallow flag.")

        if name_style is not False:
            charge_energies_dict = \
                prettify_names(charge_energies_dict, name_style)

        return ChargeEnergies(charge_energies_dict, e_range[0], e_range[1])

    @property
    def latexified_title(self):
        return latexify(self.title)


@dataclass
class ChargeEnergies:
    """Formation energies as functions of Fermi level.

    Calculates transition levels and pinning levels from
    charge-dependent formation energies.

    Attributes:
        charge_energies_dict: Dict of defect name to SingleChargeEnergies.
        e_min: Minimum Fermi level (typically 0, VBM).
        e_max: Maximum Fermi level (CBM).
    """
    charge_energies_dict: Dict[str, "SingleChargeEnergies"]
    e_min: float
    e_max: float
    _cross_point_dicts: dict = None
    _e_min_max_energies_dict: dict = None

    @property
    def cross_point_dicts(self):
        if self._cross_point_dicts:
            return self._cross_point_dicts
        self.calc_cross_points()
        return self._cross_point_dicts

    @property
    def e_min_max_energies_dict(self):
        if self._e_min_max_energies_dict:
            return self._e_min_max_energies_dict
        self.calc_cross_points()
        return self._e_min_max_energies_dict

    def calc_cross_points(self):
        """Calculate charge state transition cross points."""
        self._cross_point_dicts = {}
        self._e_min_max_energies_dict = {}
        large_minus_number = -1e4
        for defect_name, single_charge_energies in self.charge_energies_dict.items():
            half_spaces = []
            e_min_max_energies = []
            for charge, energy in single_charge_energies.charge_energies:
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
        candidates = []
        for cp in self.cross_point_dicts.values():
            candidates.extend(cp.t_all_sorted_points[1])
        return [min(candidates) - space, max(candidates) + space]

    @property
    def pinning_levels(self) -> Dict[str, List[float]]:
        result = {}
        for k, v in self.charge_energies_dict.items():
            pl = v.pinning_level(self.e_min, self.e_max)
            lower = pl[0][0] if pl[0] else None
            upper = pl[1][0] if pl[1] else None
            result[k] = [lower, upper]
        return result


@dataclass
class SingleChargeEnergies(MSONable):
    """
    charge_energies store the energy at each charge state at the E_F=0 in the
    situation where the VBM is set to 0.

    """
    charge_energies: List[Tuple[int, float]]

    def pinning_level(self, e_min, e_max
                      ) -> Tuple[Tuple[float, Optional[int]],
                                 Tuple[float, Optional[int]]]:
        """
        :return: ((Lower pinning, its charge), (Upper pinning, its charge))
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
        """
        :return: (Lowest energy, its charge)
        """
        result = []
        for charge, energy in self.charge_energies:
            result.append((charge, energy + charge * ef))
        return result

    def energy_at_ef(self, ef: float) -> Tuple[float, int]:
        """
        :return: (Lowest energy, its charge)
        """
        result_e, result_charge = float("inf"), None
        for charge, energy in self.charge_energies:
            energy = energy + charge * ef
            if energy < result_e:
                result_e, result_charge = energy, charge
        return result_e, result_charge


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
    def all_sorted_points(self):
        return sorted(self.boundary_points + self.inner_cross_points,
                      key=lambda v: v[0])

    @property
    def t_all_sorted_points(self):
        return np.transpose(np.array(self.all_sorted_points)).tolist()

    @property
    def t_inner_cross_points(self):
        return np.transpose(np.array(self.inner_cross_points)).tolist()

    @property
    def t_boundary_points(self):
        return np.transpose(np.array(self.boundary_points)).tolist()

    @property
    def charges(self) -> List[int]:
        result = []
        for i, j in zip(self.all_sorted_points[:-1], self.all_sorted_points[1:]):
            dx = j[0] - i[0]
            dy = j[1] - i[1]
            result.append(int(round(dy / dx)))
        return result

    @property
    def charge_list(self):
        charges = [None] + self.charges + [None]
        return list(zip(charges[:-1], charges[1:]))

    @property
    def annotated_charge_positions(self):
        result = {}
        for ((x1, y1), (x2, y2)), charge \
                in zip(zip(self.all_sorted_points[:-1],
                           self.all_sorted_points[1:]),
                       self.charges):
            result[charge] = [(x1 + x2) / 2, (y1 + y2) / 2]
        return result


