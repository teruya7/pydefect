# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Structure comparator for identifying defect sites."""

from typing import List

import numpy as np
from pydefect.defaults import defaults
from pydefect.utils.structure_tools import Distances
from pydefect.analysis.structure.models.site_diff import SiteDiff
from pymatgen.core import IStructure, Structure


class StructureComparator:
    """Compare defect and perfect structures to identify defect sites.

    Maps atoms between the defect and perfect structures to find vacancies,
    interstitials, and substitutions. Calculates defect center coordinates
    based on the identified defect sites.

    Attributes:
        dist_tol: Distance tolerance for site matching in Angstroms.
        perfect_to_defect_indices: Mapping from perfect to defect structure
            indices. Value is None if atom was removed.
        defect_to_perfect_indices: Mapping from defect to perfect structure
            indices. Value is None if atom was inserted.

    Example:
        >>> from pymatgen.core import Structure
        >>> perfect = Structure.from_file("perfect.vasp")
        >>> defect = Structure.from_file("defect.vasp")
        >>> comparator = StructureComparator(defect, perfect)
        >>> print(comparator.removed_indices)  # Vacancy sites
        [42]
        >>> print(comparator.defect_center_coord)
        [0.5, 0.5, 0.5]
    """
    def __init__(self,
                 defect_structure: IStructure,
                 perfect_structure: IStructure,
                 dist_tol: float = defaults.dist_tol):
        """Initialize StructureComparator.

        Args:
            defect_structure: Structure containing the defect.
            perfect_structure: Reference perfect supercell structure.
            dist_tol: Distance tolerance for site matching in Angstroms.
        """
        self._defect_structure = defect_structure
        self._perfect_structure = perfect_structure
        self.dist_tol = dist_tol
        self.perfect_to_defect_indices = self._create_perfect_to_defect_mapping()
        self.defect_to_perfect_indices = self._create_defect_to_perfect_mapping()
        # Deprecated aliases for backward compatibility
        self.p_to_d = self.perfect_to_defect_indices
        self.d_to_p = self.defect_to_perfect_indices

    @property
    def atom_mapping(self):
        """Get mapping of defect atoms to their perfect structure counterparts."""
        return {defect_idx: perfect_idx 
                for defect_idx, perfect_idx in enumerate(self.defect_to_perfect_indices)
                if defect_idx not in self.inserted_indices}

    def _atom_projection(self, structure_from, structure_to, match_species=True):
        """Project atoms from one structure to closest sites in another."""
        result = []
        for site in structure_from:
            distances = Distances(structure_to,
                                  site.frac_coords,
                                  self.dist_tol)
            species_filter = site.specie if match_species else None
            result.append(distances.atom_idx_at_center(specie=species_filter))
        return result

    def _create_perfect_to_defect_mapping(self):
        """Create mapping from perfect structure indices to defect structure."""
        return self._atom_projection(
            self._perfect_structure, self._defect_structure)

    def _create_defect_to_perfect_mapping(self):
        """Create mapping from defect structure indices to perfect structure."""
        return self._atom_projection(
            self._defect_structure, self._perfect_structure)

    # Deprecated method aliases for backward compatibility
    def make_p_to_d(self):
        return self._create_perfect_to_defect_mapping()

    def make_d_to_p(self):
        return self._create_defect_to_perfect_mapping()

    @property
    def removed_indices(self):
        """Get indices of atoms in perfect structure that are missing in defect."""
        result = []
        for perfect_idx, defect_idx in enumerate(self.perfect_to_defect_indices):
            try:
                if self.defect_to_perfect_indices[defect_idx] != perfect_idx:
                    result.append(perfect_idx)
            except (IndexError, TypeError):
                result.append(perfect_idx)
        return sorted(result)

    @property
    def inserted_indices(self):
        """Indices of atoms in defect structure that are new (not in perfect)."""
        result = []
        for defect_idx, perfect_idx in enumerate(self.defect_to_perfect_indices):
            try:
                if self.perfect_to_defect_indices[perfect_idx] != defect_idx:
                    result.append(defect_idx)
            except (IndexError, TypeError):
                result.append(defect_idx)
        return sorted(result)

    @property
    def defect_center_coord(self):
        """Calculate center coordinates of the defect region."""
        coords_list = []
        for vacancy_idx in self.removed_indices:
            coords_list.append(self._perfect_structure[vacancy_idx].frac_coords)
        for interstitial_idx in self.inserted_indices:
            coords_list.append(self._defect_structure[interstitial_idx].frac_coords)

        lattice = self._perfect_structure.lattice
        reference_coords = coords_list[0]
        translated_coords = [list(reference_coords)]
        for coord in coords_list[1:]:
            _, translation = lattice.get_distance_and_image(reference_coords, coord)
            translated_coords.append([coord[axis] + translation[axis] for axis in range(3)])
        return np.average(translated_coords, axis=0) % 1

    def neighboring_atom_indices(self, cutoff_factor=None):
        """Find indices of atoms neighboring the defect sites."""
        distances_list = []
        for vacancy_idx in self.removed_indices:
            distances_list.append(Distances(
                self._defect_structure,
                self._perfect_structure[vacancy_idx].frac_coords,
                self.dist_tol))
        for interstitial_idx in self.inserted_indices:
            distances_list.append(Distances(
                self._defect_structure,
                self._defect_structure[interstitial_idx].frac_coords,
                self.dist_tol))
        result = set()
        for distance_calc in distances_list:
            result.update(distance_calc.coordination(cutoff_factor=cutoff_factor)
                          .neighboring_atom_indices)
        return sorted(list(result))

    def make_site_diff(self):
        """Create SiteDiff object describing structure differences."""
        removed_sites = [self._perfect_structure[site_idx]
                         for site_idx in self.removed_indices]
        inserted_sites = [self._defect_structure[site_idx]
                          for site_idx in self.inserted_indices]

        try:
            removed_structure = Structure.from_sites(removed_sites)
        except ValueError:
            removed_structure = None

        try:
            inserted_structure = Structure.from_sites(inserted_sites)
        except ValueError:
            inserted_structure = None

        if inserted_structure and removed_structure:
            removed_to_inserted = self._atom_projection(
                removed_structure, inserted_structure, match_species=False)
            inserted_to_removed = self._atom_projection(
                inserted_structure, removed_structure, match_species=False)
        else:
            removed_to_inserted = [None] * len(removed_sites)
            inserted_to_removed = [None] * len(inserted_sites)

        substitution_mapping = []
        removed_by_substitution_indices = []
        inserted_by_substitution_indices = []
        for removed_idx, inserted_idx in enumerate(removed_to_inserted):
            if inserted_idx is not None and removed_idx == inserted_to_removed[inserted_idx]:
                substitution_mapping.append(
                    (self.removed_indices[removed_idx], self.inserted_indices[inserted_idx]))
                removed_by_substitution_indices.append(self.removed_indices[removed_idx])
                inserted_by_substitution_indices.append(self.inserted_indices[inserted_idx])

        removed_vacancies = []
        removed_by_substitution = []
        for site_idx in self.removed_indices:
            site = self._perfect_structure[site_idx]
            frac_coords = tuple([float(coord) for coord in site.frac_coords])
            site_info = (site_idx, site.species_string, frac_coords)
            if site_idx in removed_by_substitution_indices:
                removed_by_substitution.append(site_info)
            else:
                removed_vacancies.append(site_info)

        inserted_interstitials = []
        inserted_by_substitution = []
        for site_idx in self.inserted_indices:
            site = self._defect_structure[site_idx]
            frac_coords = tuple([float(coord) for coord in site.frac_coords])
            site_info = (site_idx, site.species_string, frac_coords)
            if site_idx in inserted_by_substitution_indices:
                inserted_by_substitution.append(site_info)
            else:
                inserted_interstitials.append(site_info)

        return SiteDiff(removed=removed_vacancies,
                        inserted=inserted_interstitials,
                        removed_by_sub=removed_by_substitution,
                        inserted_by_sub=inserted_by_substitution)


# Backward compatibility alias
DefectStructureComparator = StructureComparator
