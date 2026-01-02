# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
"""Concentration data classes."""

from dataclasses import dataclass
from typing import List, Optional, Dict

import numpy as np
from monty.json import MSONable
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn


@dataclass
class CarrierConcentration(MSONable):
    """Free carrier concentration in the material.

    Represents hole and electron concentrations per unit cell.

    Attributes:
        p: Hole concentration per cell.
        n: Electron concentration per cell.

    Example:
        >>> carriers = CarrierConcentration(p=1e15, n=1e10)
        >>> print(carriers.net_charge)
        9.99999...e+14
    """
    p: float
    n: float

    def __str__(self):
        """Return formatted carrier concentrations."""
        return f"p: {self.p:.2e}, n: {self.n:.2e}"

    @property
    def net_charge(self):
        """Get net charge (p - n)."""
        return self.p - self.n

    @property
    def abs_charge(self):
        """Get total carrier density (p + n)."""
        return self.p + self.n


@dataclass
class DefectConcentration(MSONable):
    """Defect concentration for a single defect type.

    Stores concentrations for each charge state of a defect.

    Attributes:
        name: Defect name (e.g., "Va_O1").
        charges: List of charge states.
        concentrations: Concentration for each charge state per cell.
    """
    name: str
    charges: List[int]
    concentrations: List[float]

    @property
    def str_header(self):
        """Get column headers with charge states."""
        return [f"{self.name}_{c}" for c in self.charges]

    @property
    def str_list(self):
        """Get concentrations as list for tabulation."""
        return self.concentrations

    def __str__(self):
        """Return formatted table of concentrations."""
        return tabulate([self.str_list], headers=self.str_header, floatfmt=".2e")

    @property
    def net_charge(self):
        """Calculate net charge from charge states and concentrations."""
        return sum(charge * conc for charge, conc in zip(self.charges, self.concentrations))

    @property
    def abs_charge(self):
        """Calculate absolute charge from charge states and concentrations."""
        return sum(abs(charge * conc)
                   for charge, conc in zip(self.charges, self.concentrations))

    @property
    def total_concentration(self):
        """Get sum of all charge state concentrations."""
        return sum(self.concentrations)


@dataclass
class Concentration(MSONable):
    """Complete concentration data at a given Fermi level.

    Contains carrier and defect concentrations for thermodynamic analysis.

    Attributes:
        Ef: Fermi level (eV from VBM).
        carrier: Free carrier concentrations.
        defects: List of defect concentrations.
    """
    Ef: float
    carrier: CarrierConcentration
    defects: List[DefectConcentration]

    @property
    def pinning_levels(self) -> List[float]:
        result = [float("-inf"), float("inf")]
        for d in self.defects:
            lower, upper = d.pinning_levels
            result = [max([result[0], lower]), min([result[1], upper])]
        return result

    @property
    def str_header(self):
        result = ["Ef", "p", "n"]
        for d in self.defects:
            result.extend(d.str_header)
        result.extend(["net charge", "net ratio"])
        return result

    @property
    def str_list(self):
        result = [self.Ef, self.carrier.p, self.carrier.n]
        for defect in self.defects:
            result.extend(defect.str_list)
        result.extend([self.net_charge, self.net_abs_ratio])
        return result

    def __str__(self):
        str_list = [self.str_list]
        floatfmt = [".3f"] + [".1e"] * (len(str_list[0]) - 1)
        return tabulate(str_list, headers=self.str_header, floatfmt=floatfmt)

    @property
    def net_charge(self):
        total_defect_charge = sum(d.net_charge for d in self.defects)
        return self.carrier.net_charge + total_defect_charge

    @property
    def abs_charge(self):
        defect_abs_charge = sum(d.abs_charge for d in self.defects)
        return self.carrier.abs_charge + defect_abs_charge

    @property
    def net_abs_ratio(self):
        return abs(self.net_charge) / self.abs_charge


@dataclass
class ConcentrationByFermiLevel(MSONable, ToJsonFileMixIn):
    """Concentration per cell at multiple Fermi levels."""
    T: float
    concentrations: List[Concentration]
    pinning_levels: Dict[str, List[Optional[float]]] = None
    equilibrium_concentration: Optional[Concentration] = None
    T_before_quench: float = None

    def __post_init__(self):
        self.concentrations.sort(key=lambda x: x.Ef)

    @property
    def pinning_level(self):
        if self.pinning_levels:
            lower = max(i[0] for i in self.pinning_levels.values())
            upper = min(i[1] for i in self.pinning_levels.values())
            return [lower, upper]

    def __str__(self):
        result = [f"T: {self.T}"]

        table = []
        if self.pinning_levels:
            for name, levels in self.pinning_levels.items():
                table.append([name, levels[0], levels[1]])
            result.append("Pinning levels:")
            result.append(tabulate(table, floatfmt=".3f"))

        table = []
        for c in self.concentrations:
            table.append(c.str_list)
        floatfmt = [".3f"] + [".1e"] * (len(c.str_list) - 1)
        result.append(tabulate(table, c.str_header, floatfmt=floatfmt))
        result.append("-"*50)
        if self.equilibrium_concentration:
            result.append("Equilibrium concentration")
            result.append(self.equilibrium_concentration.__str__())
        return "\n".join(result)

    @property
    def most_neutral_concentration(self) -> Concentration:
        return min(self.concentrations, key=lambda x: abs(x.net_charge))

    def next_Ef_to_neutral_concentration(
            self, n_Ef: int = 10) -> Optional[List[float]]:
        """Return Fermi levels closest to charge neutral condition."""
        try:
            c_minus = min([c for c in self.concentrations if c.net_charge > 0],
                          key=lambda x: x.net_charge)
            c_plus = min([c for c in self.concentrations if c.net_charge <= 0],
                         key=lambda x: abs(x.net_charge))
        except ValueError:
            return None

        return np.linspace(
            c_minus.Ef, c_plus.Ef, n_Ef + 2, endpoint=True).tolist()


@dataclass
class TotalDos(MSONable, ToJsonFileMixIn):
    """Total density of states for carrier concentration calculations.

    Attributes:
        energies: List of energy values (VBM set to 0).
        dos: Density of states values.
        volume: Cell volume in Å^3.
        vbm: Valence band maximum.
        cbm: Conduction band minimum.
    """
    energies: List[float]
    dos: List[float]
    volume: float
    vbm: float
    cbm: float

    @property
    def fermi_level(self):
        """Get intrinsic Fermi level (mid-gap)."""
        return (self.vbm + self.cbm) / 2

    def __str__(self):
        """Return formatted DOS summary."""
        result = [["vbm", self.vbm],
                  ["cbm", self.cbm],
                  ["band_gap", self.cbm - self.vbm],
                  ["volume", self.volume],
                  ["fermi_level", self.fermi_level],
                  ["len(energies)", len(self.energies)],
                  ["len(dos)", len(self.dos)]]
        return tabulate(result)
