# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Formation energy summary data class."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from monty.json import MSONable
from tabulate import tabulate
from vise.util.logger import get_logger
from vise.util.mix_in import ToJsonFileMixIn
from vise.util.string import latexify, numbers_to_lowercases

from pydefect.analysis.formation_energy.models.collection import (
    FormationEnergyCollection,
)
from pydefect.analysis.formation_energy.models.fermi_energies import (
    FermiLevelDependentEnergies,
    ChargeStateEnergies,
)
from pydefect.utils.formatting import prettify_names


logger = get_logger(__name__)


@dataclass
class FormationEnergySummary(MSONable, ToJsonFileMixIn):
    """Summary of defect formation energies for all defects.

    Contains energies at multiple chemical potential conditions
    and enables Fermi-level-dependent formation energy analysis.
    Energy zero is set at VBM.

    Attributes:
        title: System title (e.g., "MgO").
        formation_energies: Dict of defect name to FormationEnergyCollection.
        rel_chem_pots: Dict of label to element chemical potentials.
        cbm: Supercell CBM energy relative to VBM.
        supercell_vbm: Supercell VBM (typically 0).
        supercell_cbm: Supercell CBM.
    """
    title: str
    formation_energies: Dict[str, FormationEnergyCollection]
    rel_chem_pots: Dict[str, Dict[str, float]]
    cbm: float
    supercell_vbm: float
    supercell_cbm: float

    def __post_init__(self):
        if self.supercell_cbm < self.cbm - 0.01:
            logger.warning(f"Supercell CBM {self.supercell_cbm} is lower in "
                           f"energy than the unitcell CBM {self.cbm}")

    def filter_shallow_defects(self,
                               allow_shallow: bool,
                               excluded_defects: List[str] = None
                               ) -> Dict[str, FormationEnergyCollection]:
        """Filter formation energies based on screening criteria.

        Args:
            allow_shallow: If True, include shallow defects.
            excluded_defects: List of defect names to exclude.

        Returns:
            Filtered dict of defect name to FormationEnergyCollection.
        """
        result = {}
        for defect_name, energy_collection in self.formation_energies.items():
            filtered_charges = []
            filtered_energies = []
            for charge, formation_energy in zip(energy_collection.charges,
                                                 energy_collection.formation_energies):
                if allow_shallow is False and formation_energy.is_shallow is True:
                    continue
                if excluded_defects and f"{defect_name}_{charge}" in excluded_defects:
                    continue
                filtered_charges.append(charge)
                filtered_energies.append(formation_energy)
            result[defect_name] = FormationEnergyCollection(
                energy_collection.atom_io,
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
        for defect_name, energy_collection in self.formation_energies.items():
            atom_io_str = " ".join(
                [f"{element}: {count}" for element, count in energy_collection.atom_io.items()])
            charges_energies = list(zip(energy_collection.charges,
                                         energy_collection.formation_energies))
            charges_energies.sort(key=lambda x: x[0])
            for charge, formation_energy in charges_energies:
                defects.append([defect_name, atom_io_str, charge,
                               formation_energy.formation_energy,
                               formation_energy.total_correction,
                               formation_energy.is_shallow])
                defect_name, atom_io_str = "", ""
        headers = ("name", "atom_io", "charge", "energy", "correction",
                   "is_shallow")
        floatfmt = ("", "", "", ".3f", ".3f", "")
        lines.append(tabulate(defects, headers=headers, floatfmt=floatfmt))

        return "\n".join(lines)

    def get_fermi_level_energies(self,
                                 chem_pot_label: str,
                                 allow_shallow: bool,
                                 with_corrections: bool,
                                 e_range: Tuple[float, float],
                                 name_style: Optional[str] = None
                                 ) -> FermiLevelDependentEnergies:
        """Get Fermi level dependent energies for plotting.

        Args:
            chem_pot_label: Label for chemical potential vertex.
            allow_shallow: If True, include shallow defects.
            with_corrections: If True, include energy corrections.
            e_range: (e_min, e_max) Fermi level range.
            name_style: Optional name style for prettifying.

        Returns:
            FermiLevelDependentEnergies for plotting.
        """
        rel_chem_pot = self.rel_chem_pots[chem_pot_label]
        charge_energies_dict = {}
        for defect_name, defect_data in self.filter_shallow_defects(allow_shallow).items():
            if not defect_data:
                logger.info(f"defect {defect_name} has no energy data.")
                continue
            charge_energy_list = []
            for charge, formation_energy in zip(defect_data.charges,
                                                 defect_data.formation_energies):
                reservoir_energy = sum([-count * rel_chem_pot[element]
                                       for element, count in defect_data.atom_io.items()])
                energy = formation_energy.get_energy(with_corrections) + reservoir_energy
                charge_energy_list.append((charge, energy))

            if charge_energy_list:
                charge_energies_dict[defect_name] = ChargeStateEnergies(charge_energy_list)

        if not charge_energies_dict:
            logger.warning(f"No defect data is available. Try to switch on "
                           f"allow_shallow flag.")

        if name_style is not False:
            charge_energies_dict = \
                prettify_names(charge_energies_dict, name_style)

        return FermiLevelDependentEnergies(charge_energies_dict, e_range[0], e_range[1])

    @property
    def latexified_title(self):
        """Get LaTeX formatted title."""
        return latexify(self.title)

    # Backward compatibility methods
    def screened_defect_energies(self, allow_shallow: bool,
                                  excluded_defects: List[str] = None):
        """Deprecated: Use filter_shallow_defects() instead."""
        return self.filter_shallow_defects(allow_shallow, excluded_defects)

    def charge_energies(self, chem_pot_label: str, allow_shallow: bool,
                        with_corrections: bool, e_range: Tuple[float, float],
                        name_style: Optional[str] = None):
        """Deprecated: Use get_fermi_level_energies() instead."""
        return self.get_fermi_level_energies(
            chem_pot_label, allow_shallow, with_corrections, e_range, name_style)

    # Backward compatibility property
    @property
    def defect_energies(self):
        """Deprecated: Use formation_energies instead."""
        return self.formation_energies


# Backward compatible class
class DefectEnergySummary(FormationEnergySummary):
    """Backward compatible alias for FormationEnergySummary."""

    def __init__(self, title, defect_energies=None, formation_energies=None,
                 rel_chem_pots=None, cbm=None, supercell_vbm=None, supercell_cbm=None):
        energies = formation_energies if formation_energies is not None else defect_energies
        super().__init__(
            title=title,
            formation_energies=energies,
            rel_chem_pots=rel_chem_pots,
            cbm=cbm,
            supercell_vbm=supercell_vbm,
            supercell_cbm=supercell_cbm
        )
