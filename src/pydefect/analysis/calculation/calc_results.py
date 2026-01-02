# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from dataclasses import dataclass
from typing import List, Optional

from monty.json import MSONable
from pymatgen.core import IStructure
from vise.util.logger import get_logger
from vise.util.mix_in import ToJsonFileMixIn


logger = get_logger(__name__)


@dataclass
class CalcResults(MSONable, ToJsonFileMixIn):
    """Results from a DFT calculation.

    Stores structure, energy, magnetization, and convergence information
    from a defect or perfect supercell calculation.

    Attributes:
        structure: Relaxed structure from calculation.
        energy: Total energy in eV.
        magnetization: Total magnetization in μB (Bohr magnetons).
        potentials: Electrostatic potentials at atomic sites in eV.
            Sign convention: positive for positive charge.
        electronic_conv: Whether SCF converged. None if not checked.
        ionic_conv: Whether ionic relaxation converged. None if not checked.

    Example:
        >>> from pymatgen.core import Structure
        >>> structure = Structure.from_file("CONTCAR")
        >>> results = CalcResults(
        ...     structure=structure,
        ...     energy=-100.5,
        ...     magnetization=0.0,
        ...     potentials=[0.1, -0.2, 0.15],
        ...     electronic_conv=True,
        ...     ionic_conv=True
        ... )
        >>> results.to_json_file("calc_results.json")
    """
    # keep structure and site_symmetry in CalcResults
    structure: IStructure
    energy: float
    magnetization: float
    # potential acting on the positive unit charge, whose sign is reserved from
    # vasp convention of atomic site potential.
    potentials: List[float]
    electronic_conv: Optional[bool] = None
    ionic_conv: Optional[bool] = None

    def show_convergence_warning(self):
        """Log warnings if calculation did not converge."""
        if self.electronic_conv is False:
            logger.warning("SCF is not converged.")
        if self.ionic_conv is False:
            logger.warning("Ionic relaxation is not converged.")

    def __str__(self):
        """Return formatted string representation of results."""
        return f""" -- calc results info
energy: {self.energy:10.3f}
magnetization: {self.magnetization:6.2f}
electronic convergence: {self.electronic_conv}
ionic convergence: {self.ionic_conv}"""


class NoElectronicConvError(AssertionError):
    pass


class NoIonicConvError(AssertionError):
    pass
