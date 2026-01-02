# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from typing import List, Tuple, Optional

import numpy as np
from pydefect.defaults import defaults
from pydefect.input_maker.defect import SimpleDefect
from pydefect.input_maker.defect_entry import DefectEntry, PerturbedSite
from pydefect.input_maker.defect_set import DefectSet
from pydefect.input_maker.supercell_info import SupercellInfo
from pymatgen.core import Structure, IStructure
from pymatgen.core.structure import PeriodicNeighbor
from vise.util.structure_symmetrizer import StructureSymmetrizer
from vise.util.typing import Coords


class DefectEntriesMaker:
    """Create DefectEntry objects from SupercellInfo and DefectSet.

    Generates defect structures with optional perturbation for breaking
    symmetry and finding lower-energy configurations.

    Attributes:
        supercell_info: SupercellInfo containing structure and site info.
        defect_entries: Set of generated DefectEntry objects.

    Example:
        >>> from pydefect.input_maker.supercell_info import SupercellInfo
        >>> from pydefect.input_maker.defect_set import DefectSet
        >>> info = SupercellInfo.from_json_file("supercell_info.json")
        >>> defects = DefectSet.from_yaml("defect_in.yaml")
        >>> maker = DefectEntriesMaker(info, defects)
        >>> for entry in maker.defect_entries:
        ...     entry.to_json_file(f"{entry.name}_{entry.charge}/defect_entry.json")
    """
    def __init__(self, supercell_info: SupercellInfo, defect_set: DefectSet):
        """Initialize DefectEntriesMaker.

        Args:
            supercell_info: SupercellInfo with structure and site data.
            defect_set: DefectSet with defects to create.
        """
        self.supercell_info = supercell_info
        self.defect_entries = set()

        for defect in defect_set:
            (structure, coords, site_sym,
             perturbed_structure, perturbed_sites, perturbed_site_sym) = \
                self._create_defect_structures(defect)

            for charge in defect.charges:
                self.defect_entries.add(
                    DefectEntry(name=defect.name,
                                charge=charge,
                                structure=structure,
                                site_symmetry=site_sym,
                                defect_center=coords,
                                perturbed_structure=perturbed_structure,
                                perturbed_sites=perturbed_sites,
                                perturbed_site_symmetry=perturbed_site_sym))

    def _create_defect_structures(
            self, defect: SimpleDefect
    ) -> Tuple[IStructure, Coords, str, Optional[IStructure],
               Optional[Tuple[PerturbedSite, ...]], Optional[str]]:
        """Create defect structure with optional perturbation."""
        structure = copy_to_structure(self.supercell_info.structure)

        if defect.out_atom[0] == "i":
            interstitial_index = int(defect.out_atom[1:]) - 1
            site = self.supercell_info.interstitials[interstitial_index]
            cutoff = self.supercell_info.interstitial_coords(interstitial_index).cutoff
            defect_coords = self.supercell_info.interstitials[interstitial_index].frac_coords
        else:
            site = self.supercell_info.sites[defect.out_atom]
            cutoff = self.supercell_info.coords(defect.out_atom).cutoff
            removed_site_index = site.equivalent_atoms[0]
            defect_coords = structure.pop(removed_site_index).frac_coords

        if defaults.displace_distance:
            perturbed_structure, perturbed_sites = perturb_structure(
                structure, defect_coords, cutoff)

            perturbed_symmetry = StructureSymmetrizer(
                perturbed_structure,
                defaults.symmetry_length_tolerance,
                defaults.symmetry_angle_tolerance).point_group

            if defect.in_atom:
                add_atom_to_structure(structure, defect.in_atom, defect_coords)
                add_atom_to_structure(perturbed_structure, defect.in_atom, defect_coords)

            return (to_istructure(structure), tuple(defect_coords), site.site_symmetry,
                    to_istructure(perturbed_structure), perturbed_sites, perturbed_symmetry)
        else:
            if defect.in_atom:
                add_atom_to_structure(structure, defect.in_atom, defect_coords)
            return (to_istructure(structure), tuple(defect_coords), site.site_symmetry,
                    None, None, None)


def copy_to_structure(structure: IStructure) -> Structure:
    return Structure.from_dict(structure.as_dict())


def to_istructure(structure: Structure) -> IStructure:
    return IStructure.from_dict(structure.as_dict())


def add_atom_to_structure(structure: Structure, element: str, coords: List[float]):
    """In-place atom insertion to structure.

    Inserts atom at the appropriate position to maintain element ordering.
    """
    try:
        insert_idx = next(idx for idx, site in enumerate(structure) 
                          if str(site.specie) == element)
    except StopIteration:
        insert_idx = len(structure)

    structure.insert(insert_idx, element, coords)


def perturb_structure(structure: Structure, center: List[float], cutoff: float
                      ) -> Tuple[Structure, Tuple[PerturbedSite, ...]]:
    """Apply random perturbation to atoms near defect center.

    Args:
        structure: pymatgen Structure object.
        center: Fractional coordinates of defect center.
        cutoff: Radius in Angstrom for perturbation sphere.

    Returns:
        Tuple of (perturbed structure, perturbed site info).
    """
    perturbed_structure = structure.copy()
    perturbed_sites = []
    center_cartesian = structure.lattice.get_cartesian_coords(center)
    neighboring_atoms: List[PeriodicNeighbor] = structure.get_sites_in_sphere(
        pt=center_cartesian, r=cutoff, include_index=True)

    for neighbor in neighboring_atoms:
        displacement_vector, displacement_distance = random_3d_vector(
            defaults.displace_distance)
        perturbed_structure.translate_sites(
            neighbor.index, displacement_vector, frac_coords=False)
        site_info = PerturbedSite(
             element=str(neighbor.specie),
             distance=float(neighbor.nn_distance),
             initial_coords=tuple([float(coord) for coord in neighbor.frac_coords]),
             perturbed_coords=tuple([float(coord) 
                                     for coord in perturbed_structure[neighbor.index].frac_coords]),
             displacement=displacement_distance)
        perturbed_sites.append(site_info)

    return perturbed_structure, tuple(perturbed_sites)


def random_3d_vector(max_distance: float) -> Tuple[np.ndarray, float]:
    """Random 3d vector with uniform spherical distribution with 0 <= norm <= 1.
    stackoverflow.com/questions/5408276/python-uniform-spherical-distribution
    """
    phi = np.random.uniform(0, np.pi * 2)
    cos_theta = np.random.uniform(-1, 1)
    theta = np.arccos(cos_theta)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    distance = np.random.uniform(high=max_distance)
    return np.array([x, y, z]) * distance, distance
