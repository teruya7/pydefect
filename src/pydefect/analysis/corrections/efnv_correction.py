# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from monty.json import MSONable
from pydefect.analysis.corrections.abstract_correction import Correction
from tabulate import tabulate


@dataclass
class ExtendedFnvCorrection(Correction):
    """Extended FNV (Freysoldt-Neugebauer-Van de Walle) correction.

    Calculates electrostatic correction for charged defect calculations
    using the extended FNV scheme with point charge + alignment terms.

    Attributes:
        charge: Defect charge state.
        point_charge_correction: Correction energy for point charge
            interactions in eV.
        defect_region_radius: Maximum radius of sphere touching lattice
            planes (Angstroms). Defines the defect region boundary.
        sites: List of PotentialSite objects with potential information.
        defect_coords: Position of defect in fractional coordinates.

    Example:
        >>> correction = ExtendedFnvCorrection(
        ...     charge=2,
        ...     point_charge_correction=0.5,
        ...     defect_region_radius=3.0,
        ...     sites=[...],
        ...     defect_coords=(0.5, 0.5, 0.5)
        ... )
        >>> print(correction.correction_energy)
        0.65
    """
    charge: float
    point_charge_correction: float
    defect_region_radius: float
    sites: List["PotentialSite"]
    defect_coords: Tuple[float, float, float]

    def __str__(self):
        """Return formatted correction summary as table."""
        table_data = [["charge", self.charge],
             ["pc term", self.point_charge_correction],
             ["alignment term", self.alignment_correction],
             ["correction energy", self.correction_energy]]
        return tabulate(table_data, tablefmt='psql')

    @property
    def average_potential_diff(self):
        """Calculate average potential difference outside defect region.

        Returns:
            Mean of (DFT potential - point charge potential) for sites
            outside the defect region radius.
        """
        return np.mean([site.diff_pot for site in self.sites
                        if site.distance > self.defect_region_radius])

    @property
    def alignment_correction(self) -> float:
        """Calculate potential alignment correction.

        Returns:
            Alignment correction energy in eV.
        """
        return - self.average_potential_diff * self.charge

    @property
    def correction_energy(self) -> float:
        """Calculate total correction energy.

        Returns:
            Sum of point charge and alignment corrections in eV.
        """
        return self.point_charge_correction + self.alignment_correction

    @property
    def correction_dict(self):
        """Get correction terms as dictionary.

        Returns:
            Dict with 'pc term' and 'alignment term' keys.
        """
        return {"pc term": self.point_charge_correction,
                "alignment term": self.alignment_correction}


@dataclass
class PotentialSite(MSONable):
    specie: str
    distance: float
    potential: float
    pc_potential: Optional[float]

    @property
    def diff_pot(self):
        return self.potential - self.pc_potential
