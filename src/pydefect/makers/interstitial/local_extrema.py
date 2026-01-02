# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from dataclasses import dataclass
from typing import List, Optional

from monty.json import MSONable
from pydefect.makers.interstitial.append_interstitial import append_interstitial
from pydefect.utils.formatting import pretty_coords
from pydefect.utils.structure_tools import Coordination
from pymatgen.core import Structure
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn
from vise.util.typing import Coords


@dataclass
class CoordInfo(MSONable):
    """Coordination information for an interstitial site.

    Attributes:
        site_symmetry: Point group symmetry.
        coordination: Neighboring atoms information.
        frac_coords: Fractional coordinates.
        quantities: Associated values (e.g., charge density).

    Example:
        >>> info = CoordInfo("T_d", coordination, [(0.5, 0.5, 0.5)])
    """
    site_symmetry: str
    coordination: Coordination
    frac_coords: List[Coords]
    quantities: List[float] = None


@dataclass
class VolumetricDataAnalyzeParams(MSONable):
    """Parameters for volumetric data analysis.

    Attributes:
        threshold_frac: Fractional threshold for extrema.
        threshold_abs: Absolute threshold for extrema.
        min_dist: Minimum distance between extrema (Å).
        tol: Tolerance for clustering (Å).
        radius: Radius for local averaging (Å).
    """
    threshold_frac: Optional[float]
    threshold_abs: Optional[float]
    min_dist: float
    tol: float
    radius: float


@dataclass
class VolumetricDataLocalExtrema(MSONable, ToJsonFileMixIn):
    """Local extrema in volumetric data for interstitial sites.

    Stores potential interstitial positions from charge density analysis.

    Attributes:
        unit_cell: Unit cell structure.
        is_min: True if minima, False if maxima.
        extrema_points: List of CoordInfo for each site.
        info: Description string.
        params: Analysis parameters used.
    """
    unit_cell: Structure
    is_min: bool
    extrema_points: List[CoordInfo]
    info: str
    params: VolumetricDataAnalyzeParams

    def __str__(self):
        min_or_max = "min" if self.is_min else "max"
        extrema_table = [["#", "site_sym", "coordination", "frac_coords", "quantity"]]
        for site_idx, extrema_point in enumerate(self.extrema_points, 1):
            extrema_table.append([site_idx,
                                  extrema_point.site_symmetry,
                                  extrema_point.coordination.distance_dict,
                                  pretty_coords(extrema_point.frac_coords[0]),
                                  f"{extrema_point.quantities[0]:.2g}"])
        lines = [f"info: {self.info}",
                 f"min_or_max: {min_or_max}",
                 f"extrema_points:",
                 tabulate(extrema_table, tablefmt="plain")]
        return "\n".join(lines)

    def append_sites_to_supercell_info(self, supercell_info, indices):
        """Append selected interstitial sites to supercell info."""
        frac_coords, infos = [], []
        for site_idx, extrema_point in enumerate(self.extrema_points, 1):
            if site_idx in indices:
                frac_coords.append(extrema_point.frac_coords[0])
                infos.append(f"{self.info} #{site_idx}")

        result = append_interstitial(supercell_info,
                                     self.unit_cell,
                                     frac_coords=frac_coords,
                                     infos=infos)
        return result

