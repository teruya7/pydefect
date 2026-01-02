# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from typing import List, Optional

import numpy as np
from pydefect.analysis.defect_charge.defect_charge_info import DefectChargeInfo, \
    AveChargeDensityDist
from pydefect.analysis.corrections.grids import Grids
from pydefect.analysis.corrections.efnv import calculate_max_inscribed_radius as calc_max_sphere_radius
from pymatgen.io.vasp import Chgcar
from vise.analyzer.vasp.handle_volumetric_data import make_spin_charges


def center_1d_periodic_quantity(grid_points: List[float]) -> int:
    """Find center of periodic quantity by minimizing moment.

    Args:
        grid_points: 1D list of values on periodic grid.

    Returns:
        Index of the center point.

    Example:
        >>> data = [0.1, 0.5, 0.3, 0.1]
        >>> center_idx = center_1d_periodic_quantity(data)
    """
    num_grid_pts = len(grid_points)
    moments = []
    for center_idx in range(num_grid_pts):
        moment = 0.0
        if num_grid_pts % 2 == 0:
            for offset in range(1, int(num_grid_pts / 2 + 1)):
                moment += grid_points[center_idx - offset] * offset
            for offset in range(1, int(num_grid_pts / 2)):
                wrapped_idx = (center_idx + offset - num_grid_pts) % num_grid_pts
                moment += grid_points[wrapped_idx] * offset
        else:
            half_range = int(np.floor(num_grid_pts / 2))
            for offset in range(1, half_range + 1):
                moment += grid_points[center_idx - offset] * offset
            for offset in range(1, half_range + 1):
                wrapped_idx = (center_idx + offset - num_grid_pts) % num_grid_pts
                moment += grid_points[wrapped_idx] * offset

        moments.append(moment)

    return np.nanargmin(moments)


def make_charge_dist(parchg: Chgcar, grids: Grids, distance_bins: np.ndarray):
    """Calculate radial charge distribution from PARCHG.

    Args:
        parchg: Partial charge density from VASP.
        grids: Precomputed grid distances.
        distance_bins: Radial distance bins for averaging.

    Returns:
        List of AveChargeDensityDist per spin.
    """
    assert parchg.structure.lattice == grids.lattice
    assert parchg.dim == grids.dim

    spin_charges = make_spin_charges(parchg)

    dists = []
    defect_center_idxs = []
    for charge_data in spin_charges:
        center = [center_1d_periodic_quantity(
            charge_data.get_average_along_axis(axis)) for axis in [0, 1, 2]]
        defect_center_idxs.append(np.array(center))
        data = charge_data.data["total"]
        dists.append(grids.spherical_dist(data, center, distance_bins))

    result = []
    for center_idx, distribution in zip(defect_center_idxs, dists):
        result.append(AveChargeDensityDist(tuple(center_idx / grids.dim), distribution))

    return result


def make_defect_charge_info(parchgs: List[Chgcar],
                            band_idxs: List[int],
                            bin_interval: float,
                            grids: Grids = None) -> DefectChargeInfo:
    """Create DefectChargeInfo from partial charge files.

    Args:
        parchgs: List of PARCHG files for each band.
        band_idxs: Band indices corresponding to parchgs.
        bin_interval: Radial bin width (Å).
        grids: Optional precomputed Grids.

    Returns:
        DefectChargeInfo with charge distributions.
    """
    if grids is None:
        grids = Grids.from_chgcar(parchgs[0])

    radius = calc_max_sphere_radius(parchgs[0].structure.lattice.matrix)
    num_bins = int(np.ceil(radius / bin_interval))
    distance_bins = np.array([bin_interval * i for i in range(num_bins)] + [radius])
    ave_charge_density = 1.0 / parchgs[0].structure.volume
    charge_dists = []
    for parchg in parchgs:
        charge_dists.append(make_charge_dist(parchg, grids, distance_bins))
    return DefectChargeInfo(distance_bins.tolist(), band_idxs, charge_dists,
                            ave_charge_density)

