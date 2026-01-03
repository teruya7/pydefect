# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Calculate charge localization from partial charge density files."""
from typing import List

import numpy as np
from pydefect.analysis.localization.models import (
    ChargeLocalizationInfo,
    RadialChargeDist,
)
from pydefect.analysis.corrections.models import Grids
from pydefect.analysis.corrections.efnv import (
    calculate_max_inscribed_radius as calc_max_sphere_radius,
)
from pymatgen.io.vasp import Chgcar
from vise.analyzer.vasp.handle_volumetric_data import make_spin_charges


def find_periodic_center(grid_points: List[float]) -> int:
    """Find center of periodic quantity by minimizing moment.

    Uses moment minimization to locate the center of a periodic
    distribution, handling wrap-around effects.

    Args:
        grid_points: 1D list of values on periodic grid.

    Returns:
        Index of the center point.

    Example:
        >>> data = [0.1, 0.5, 0.3, 0.1]
        >>> center_idx = find_periodic_center(data)
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


def calculate_radial_distribution(
        parchg: Chgcar,
        grids: Grids,
        distance_bins: np.ndarray
) -> List[RadialChargeDist]:
    """Calculate radial charge distribution from PARCHG.

    Args:
        parchg: Partial charge density from VASP.
        grids: Precomputed grid distances.
        distance_bins: Radial distance bins for averaging.

    Returns:
        List of RadialChargeDist per spin channel.
    """
    assert parchg.structure.lattice == grids.lattice
    assert parchg.dim == grids.dim

    spin_charges = make_spin_charges(parchg)

    dists = []
    defect_center_idxs = []
    for charge_data in spin_charges:
        center = [find_periodic_center(
            charge_data.get_average_along_axis(axis)) for axis in [0, 1, 2]]
        defect_center_idxs.append(np.array(center))
        data = charge_data.data["total"]
        dists.append(grids.spherical_dist(data, center, distance_bins))

    result = []
    for center_idx, distribution in zip(defect_center_idxs, dists):
        result.append(RadialChargeDist(
            tuple(center_idx / grids.dim), distribution))

    return result


def calculate_charge_localization(
        parchgs: List[Chgcar],
        band_indices: List[int],
        bin_interval: float,
        grids: Grids = None
) -> ChargeLocalizationInfo:
    """Calculate charge localization info from partial charge files.

    Analyzes PARCHG files to determine how localized defect-induced
    states are by examining radial charge density distributions.

    Args:
        parchgs: List of PARCHG files for each band.
        band_indices: Band indices corresponding to parchgs.
        bin_interval: Radial bin width (Å).
        grids: Optional precomputed Grids object.

    Returns:
        ChargeLocalizationInfo with charge distributions.

    Example:
        >>> from pymatgen.io.vasp import Chgcar
        >>> parchgs = [Chgcar.from_file(f"PARCHG.{i}") for i in range(3)]
        >>> info = calculate_charge_localization(parchgs, [10, 11, 12], 0.1)
    """
    if grids is None:
        grids = Grids.from_chgcar(parchgs[0])

    radius = calc_max_sphere_radius(parchgs[0].structure.lattice.matrix)
    num_bins = int(np.ceil(radius / bin_interval))
    distance_bins = np.array(
        [bin_interval * i for i in range(num_bins)] + [radius])
    uniform_density = 1.0 / parchgs[0].structure.volume
    
    radial_distributions = []
    for parchg in parchgs:
        radial_distributions.append(
            calculate_radial_distribution(parchg, grids, distance_bins))
    
    return ChargeLocalizationInfo(
        distance_bins.tolist(),
        band_indices,
        radial_distributions,
        uniform_density,
    )


# Backward compatibility aliases
center_1d_periodic_quantity = find_periodic_center
make_charge_dist = calculate_radial_distribution
make_defect_charge_info = calculate_charge_localization
