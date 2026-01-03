# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
"""Concentration calculation functions."""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np

from pydefect.analysis.concentration.models import (
    DefectConcentration,
    CarrierConcentration,
    Concentration,
    ConcentrationByFermiLevel,
    TotalDos,
    Degeneracies,
)
from pydefect.analysis.concentration.distribution_function import (
    boltzmann_dist,
    fermi_dirac,
)
from pydefect.analysis.formation_energy.models import (
    FermiLevelDependentEnergies,
    ChargeStateEnergies,
    # Backward compatibility aliases
    ChargeEnergies,
    SingleChargeEnergies,
)
from vise.util.logger import get_logger


logger = get_logger(__name__)


class CarrierConcentrationCalculator:
    """Calculate carrier concentrations from DOS.

    Computes hole and electron concentrations at different
    Fermi levels using the total density of states.

    Attributes:
        T: Temperature (K).
        vb_dos: Valence band DOS.
        cb_dos: Conduction band DOS.
    """
    def __init__(self, total_dos: TotalDos, T: float):
        """Initialize carrier concentration calculator.

        Args:
            total_dos: TotalDos object with DOS data.
            T: Temperature in Kelvin.
        """
        self._fermi_level = total_dos.fermi_level
        self._tdos = np.array(total_dos.dos)
        self._abs_energies = np.array(total_dos.energies)
        self._V = total_dos.volume / 10**24  # in cm^3
        self._vbm = total_dos.vbm
        self.T = T
        self._make_vb_dos()
        self._make_cb_dos()

    def _make_vb_dos(self):
        energy_range = self._abs_energies < self._fermi_level
        energies = np.array(self._abs_energies)[energy_range]
        doses = self._tdos[energy_range].tolist()
        self.vb_dos = VBDos((energies - self._vbm).tolist(), doses)

    def _make_cb_dos(self):
        energy_range = self._abs_energies > self._fermi_level
        energies = np.array(self._abs_energies)[energy_range]
        doses = self._tdos[energy_range].tolist()
        self.cb_dos = CBDos((energies - self._vbm).tolist(), doses)

    def carrier_concentration(self, Ef):
        p = float(self.vb_dos.carrier_concentration(Ef, self.T) / self._V)
        n = float(self.cb_dos.carrier_concentration(Ef, self.T) / self._V)
        return CarrierConcentration(p, n)

    def _concentration(self, Ef):
        return Concentration(Ef, self.carrier_concentration(Ef), [])

    def make_concentrations_by_fermi_level(self, Efs: List[float],
                                           ) -> ConcentrationByFermiLevel:
        concentrations = [self._concentration(Ef) for Ef in Efs]
        return ConcentrationByFermiLevel(self.T, concentrations, None)


class ConcentrationCalculator:
    """Calculate defect and carrier concentrations."""
    
    def __init__(self,
                 total_dos: TotalDos,
                 charge_energies: ChargeEnergies,
                 degeneracies: Degeneracies,
                 T: float,
                 fixed_defect_concentrations: Dict[str, float] = None):

        self._tdos = np.array(total_dos.dos)
        self._abs_energies = np.array(total_dos.energies)
        self._V = total_dos.volume / 10**24  # in cm^3
        self.fixed_con = fixed_defect_concentrations

        self.carrier_calculator = CarrierConcentrationCalculator(total_dos, T)

        self.T = T
        self.charge_energies = charge_energies
        self._degeneracies = degeneracies

    def _make_defect_concentration(self,
                                   name: str,
                                   Ef: float,
                                   single_energies: SingleChargeEnergies):
        """Calculate defect concentration at given Fermi level."""
        charges, concentrations = [], []
        for (charge, energy) in single_energies.charge_energies_at_ef(Ef):
            charges.append(charge)
            deg = self._degeneracies[name][charge].degeneracy
            concentrations.append(float(boltzmann_dist(energy, self.T) * deg / self._V))

        concentrations = self._redistribute(concentrations, name)
        return DefectConcentration(name, charges, concentrations)

    def _calc_pinning(self, single_energies):
        pin_level = single_energies.pinning_level(float("-inf"), float("inf"))
        try:
            lower = pin_level[0][0]
        except TypeError:
            lower = float("-inf")
        try:
            upper = pin_level[1][0]
        except TypeError:
            upper = float("inf")
        return [lower, upper]

    def _redistribute(self, concentrations, name):
        if self.fixed_con:
            return redistribute_concentration(
                concentrations, self.fixed_con[name])
        return concentrations

    def _make_all_concentration(self, Ef: float):
        carrier = self.carrier_calculator.carrier_concentration(Ef)

        defects = []
        for name, single in self.charge_energies.charge_energies_dict.items():
            concentration = self._make_defect_concentration(name, Ef, single)
            defects.append(concentration)

        return Concentration(Ef, carrier, defects)

    def make_concentrations_by_fermi_level(self, Efs: List[float],
                                           ) -> ConcentrationByFermiLevel:
        concentrations = [self._make_all_concentration(Ef) for Ef in Efs]
        pinning_levels = self.charge_energies.pinning_levels
        return ConcentrationByFermiLevel(self.T,
                                         concentrations,
                                         pinning_levels)


def redistribute_concentration(
        concentrations: List[float], total: float) -> List[float]:
    factor = total / np.sum(concentrations)
    return (np.array(concentrations) * factor).tolist()


def equilibrium_concentration(make_cc: ConcentrationCalculator,
                              e_min: float,
                              e_max: float,
                              n: int = 10,
                              n_iter: int = 10,
                              net_abs_ratio: float = 1.0e-5
                              ) -> Optional[Concentration]:
    """Find equilibrium concentration at charge-neutral Fermi level."""
    Efs = np.linspace(e_min, e_max, n + 1).tolist()

    for iteration in range(n_iter):
        logger.info(f"Calc equilibrium concentration: iteration {iteration}")
        cons_Ef = make_cc.make_concentrations_by_fermi_level(Efs)

        if cons_Ef.most_neutral_concentration.net_abs_ratio < net_abs_ratio:
            logger.info(f"Equilibrium concentration is found.")
            return cons_Ef.most_neutral_concentration

        Efs = cons_Ef.next_Ef_to_neutral_concentration(n)

        if Efs is None:
            logger.warning(f"Charge balance is out of {e_min}--{e_max}.")
            return

    logger.warning("No convergence is obtained.")


@dataclass
class Dos(metaclass=ABCMeta):
    """Base class for density of states."""
    energies: List[float]
    doses: List[float]

    def carrier_concentration(self, Ef, T) -> float:
        result = 0.0
        for E, dos in zip(self.energies, self.doses):
            result += self.interval * dos * self._fermi_dirac(Ef, E, T)
        return result

    @staticmethod
    @abstractmethod
    def _fermi_dirac(Ef, E, T):
        pass

    @property
    def interval(self) -> float:
        return self.energies[1] - self.energies[0]


class VBDos(Dos):
    """Valence band density of states."""
    carrier_type = "p"

    @staticmethod
    def _fermi_dirac(Ef, E, T):
        return fermi_dirac(Ef - E, T)


class CBDos(Dos):
    """Conduction band density of states."""
    carrier_type = "n"

    @staticmethod
    def _fermi_dirac(Ef, E, T):
        return fermi_dirac(E - Ef, T)


# Backward compatibility aliases
MakeCarrierConcentrations = CarrierConcentrationCalculator
MakeConcentrations = ConcentrationCalculator