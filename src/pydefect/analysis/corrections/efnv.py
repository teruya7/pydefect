# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Extended FNV correction calculation."""

from typing import Optional, Tuple

import numpy as np
from numpy import dot, cross
from numpy.linalg import norm

from pydefect.analysis.calculation.models import CalcResults
from pydefect.analysis.structure.comparator import (
    DefectStructureComparator,
)
from pydefect.analysis.corrections.models import (
    ExtendedFnvCorrection,
    PotentialSite,
)
from pydefect.analysis.corrections.ewald import Ewald
from pydefect.defaults import defaults
from pydefect.error import SupercellError, NoCalculatedPotentialSiteError


Coords = Tuple[float, float, float]


def calculate_efnv_correction(charge: float,
                              calc_results: CalcResults,
                              perfect_calc_results: CalcResults,
                              dielectric_tensor: np.array,
                              defect_coords: Optional[Coords] = None,
                              accuracy: float = defaults.ewald_accuracy,
                              defect_region_radius: float = None,
                              calc_all_sites: bool = False,
                              unit_conversion: float = 180.95128169876497):
    """Create Extended FNV correction for charged defect.

    Args:
        charge: Defect charge state.
        calc_results: CalcResults from defect calculation.
        perfect_calc_results: CalcResults from perfect supercell.
        dielectric_tensor: Dielectric tensor (3x3).
        defect_coords: Optional defect center coordinates.
        accuracy: Ewald accuracy parameter.
        defect_region_radius: Radius to exclude from averaging.
        calc_all_sites: If True, calculate all site potentials.
        unit_conversion: Unit conversion factor.

    Returns:
        ExtendedFnvCorrection object.

    Example:
        >>> correction = calculate_efnv_correction(
        ...     charge=2,
        ...     calc_results=defect_results,
        ...     perfect_calc_results=perfect_results,
        ...     dielectric_tensor=unitcell.dielectric_constant
        ... )
    """
    sites, rel_coords, defect_coords = \
        create_potential_sites(calc_results, perfect_calc_results, defect_coords)

    lattice = calc_results.structure.lattice
    ewald = Ewald(lattice.matrix, dielectric_tensor, accuracy=accuracy)
    point_charge_correction = \
        0.0 if not charge else - ewald.lattice_energy * charge ** 2
    if defect_region_radius is None:
        defect_region_radius = calculate_max_inscribed_radius(lattice.matrix)

    has_calculated_sites = False
    for site, rel_coord in zip(sites, rel_coords):
        if calc_all_sites is True or site.distance > defect_region_radius:
            has_calculated_sites = True
            if charge == 0:
                site.pc_potential = 0
            else:
                site.pc_potential = (ewald.atomic_site_potential(rel_coord)
                                     * charge * unit_conversion)

    if has_calculated_sites is False:
        raise NoCalculatedPotentialSiteError(
            "Change the spherical radius of defect region manually. "
            f"Now {defect_region_radius:4.2f}Å is set.")

    return ExtendedFnvCorrection(
        charge=charge,
        point_charge_correction=point_charge_correction * unit_conversion,
        defect_region_radius=defect_region_radius,
        sites=sites,
        defect_coords=tuple(defect_coords))


def create_potential_sites(calc_results, perfect_calc_results, defect_coords):
    """Create potential sites for EFNV correction.

    Args:
        calc_results: Defect calculation results.
        perfect_calc_results: Perfect supercell results.
        defect_coords: Optional defect coordinates.

    Returns:
        Tuple of (sites, relative_coords, defect_coords).
    """
    if calc_results.structure.lattice != perfect_calc_results.structure.lattice:
        raise SupercellError("The lattice constants for defect and perfect "
                             "models are different")
    structure_analyzer = DefectStructureComparator(
        calc_results.structure, perfect_calc_results.structure)
    if defect_coords is None:
        defect_coords = structure_analyzer.defect_center_coord
    lattice = calc_results.structure.lattice
    sites, rel_coords = [], []

    for defect_idx, perfect_idx in structure_analyzer.atom_mapping.items():
        species = str(calc_results.structure[defect_idx].specie)
        frac_coords = calc_results.structure[defect_idx].frac_coords
        distance, _ = lattice.get_distance_and_image(defect_coords, frac_coords)
        potential_diff = (calc_results.potentials[defect_idx] 
                          - perfect_calc_results.potentials[perfect_idx])
        sites.append(PotentialSite(species, distance, potential_diff, None))
        site_coord = calc_results.structure[defect_idx].frac_coords
        rel_coords.append([coord - center for coord, center 
                           in zip(site_coord, defect_coords)])

    return sites, rel_coords, defect_coords


def calculate_max_inscribed_radius(lattice_matrix) -> float:
    """Calculate maximum radius of a sphere fitting inside the unit cell.

    Uses cross product formula: (a_i x a_j) . a_k / |a_i x a_j|
    to find distances between parallel planes.

    Args:
        lattice_matrix: 3x3 lattice vectors matrix.

    Returns:
        Maximum inscribed sphere radius in Angstrom.
    """
    plane_distances = np.zeros(3, dtype=float)
    for axis in range(3):
        cross_product = cross(lattice_matrix[axis - 2], lattice_matrix[axis - 1])
        normal_vector = lattice_matrix[axis]
        plane_distances[axis] = abs(dot(cross_product, normal_vector)) / norm(cross_product)
    return max(plane_distances) / 2.0


# Backward compatibility aliases
make_efnv_correction = calculate_efnv_correction
make_sites = create_potential_sites
calc_max_sphere_radius = calculate_max_inscribed_radius
