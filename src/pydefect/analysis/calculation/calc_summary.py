# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from dataclasses import dataclass
from typing import Optional, Dict

from monty.json import MSONable
from pydefect.analysis.defect_structure.defect_structure_info import SymmRelation, DefectType
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn


@dataclass
class SingleCalcSummary(MSONable):
    """Summary of a single defect calculation.

    Records convergence status, structural changes, and electronic states.

    Attributes:
        charge: Charge state.
        atom_io: Dict of element to atom count change.
        electronic_conv: Whether SCF converged.
        ionic_conv: Whether ionic relaxation converged.
        is_energy_strange: Whether formation energy is anomalous.
        same_config_from_init: Whether configuration matches initial.
        defect_type: Type of defect (vacancy, interstitial, etc.).
        symm_relation: Symmetry relation to initial structure.
        donor_phs: Whether has donor perturbed host state.
        acceptor_phs: Whether has acceptor perturbed host state.

    Example:
        >>> summary = SingleCalcSummary(
        ...     charge=2,
        ...     atom_io={"O": -1},
        ...     electronic_conv=True,
        ...     ionic_conv=True
        ... )
    """
    charge: int
    atom_io: dict
    electronic_conv: Optional[bool] = None
    ionic_conv: Optional[bool] = None
    is_energy_strange: Optional[bool] = None
    same_config_from_init: Optional[bool] = None
    defect_type: Optional[str] = None
    symm_relation: Optional[str] = None
    donor_phs: Optional[bool] = None
    acceptor_phs: Optional[bool] = None
    unoccupied_deep_state: Optional[bool] = None
    occupied_deep_state: Optional[bool] = None
    same_structure: Optional[str] = None

    def same_atom_charge_io(self, other: "SingleCalcSummary"):
        return self.charge == other.charge and self.atom_io == other.atom_io

    @property
    def is_converged(self):
        return self.electronic_conv and self.ionic_conv

    @property
    def is_proper_result(self):
        return self.is_converged is True and self.is_energy_strange is False

    @property
    def is_unusual(self):
        return (self.symm_relation is SymmRelation.supergroup or
                self.same_config_from_init is False)

    @property
    def config_list(self):
        if self.is_proper_result:
            result = [".", ".", "."]
            if self.same_config_from_init in (False, None):
                result.extend([str(self.same_config_from_init),
                               str(self.defect_type),
                               str(self.symm_relation)])
            else:
                result.extend([".", ".", "."])
            return result
        elif self.is_converged:
            return [".", ".", self.is_energy_strange]
        else:
            return [self.electronic_conv, self.ionic_conv]


@dataclass
class CalcSummary(MSONable, ToJsonFileMixIn):
    """Summary of all defect calculations.

    Attributes:
        single_summaries: Dict of defect name to SingleCalcSummary.
    """
    single_summaries: Dict[str, SingleCalcSummary]

    def __str__(self):
        lines = [["name", "Ele. conv.", "Ionic conv.", "Is energy strange",
                  "Same config.", "Defect type", "Symm. Relation"]]
        for defect_name, calc_summary in self.single_summaries.items():
            lines.append([defect_name] + calc_summary.config_list)
        return tabulate(lines, stralign="center", tablefmt="pipe")
