# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional, Set

import numpy as np
from monty.json import MSONable
from pydefect.defaults import defaults
from pymatgen.core import Structure, Element


class Distances:
    """Calculate distances from a center point in a structure.

    Provides atom finding, coordination, and distance analysis
    for defect structure comparisons and site identification.

    Attributes:
        structure: Input pymatgen Structure.
        coord: Center fractional coordinates.
        dist_tol: Distance tolerance for matching in Angstroms.

    Example:
        >>> from pymatgen.core import Structure
        >>> structure = Structure.from_file("POSCAR")
        >>> distances = Distances(structure, [0.5, 0.5, 0.5])
        >>> print(distances.shortest_distance)
        2.45
    """
    def __init__(self,
                 structure: Structure,
                 center_coord: np.array,
                 dist_tol: float = None):
        """Initialize Distances.

        Args:
            structure: Structure to analyze.
            center_coord: Center point fractional coordinates.
            dist_tol: Distance tolerance in Angstroms.
                Defaults to pydefect defaults.dist_tol.
        """
        self.structure = structure
        self.coord = center_coord
        self.dist_tol = dist_tol or defaults.dist_tol

    def distances(self, remove_self=True, specie=None) -> List[float]:
        """Calculate distances from center to all atoms.

        Args:
            remove_self: If True, exclude atoms at center (distance < 1e-5).
            specie: If provided, only include this element.

        Returns:
            List of distances in Angstroms.
        """
        result = []
        lattice = self.structure.lattice
        for site in self.structure:
            if specie and Element(specie) != site.specie:
                result.append(float("inf"))
                continue
            distance, _ = \
                lattice.get_distance_and_image(site.frac_coords, self.coord)
            if remove_self and distance < 1e-5:
                continue
            result.append(distance)

        return result

    def atom_idx_at_center(self, specie: str) -> Optional[int]:
        """Find atom index at center position.

        Args:
            specie: Element to search for.

        Returns:
            Index of atom at center, or None if not found.
        """
        distances = self.distances(remove_self=False, specie=specie)
        sorted_dists = sorted(distances)
        if sorted_dists[0] > self.dist_tol:
            return None
        return np.argmin(distances)

    @property
    def shortest_distance(self) -> float:
        return min(self.distances())

    def coordination(self, include_on_site=False, cutoff_factor=None
                     ) -> "Coordination":
        """Calculate coordination environment around center."""
        cutoff_factor = cutoff_factor or defaults.cutoff_distance_factor
        cutoff = self.shortest_distance * cutoff_factor
        elements = [site.specie.name for site in self.structure]
        element_distance_pairs = zip(elements, self.distances(remove_self=False))

        unsorted_distances = defaultdict(list)
        neighboring_atom_indices = []
        for atom_idx, (element, distance) in enumerate(element_distance_pairs):
            if distance < cutoff:
                if include_on_site or \
                        (include_on_site is False and distance > 1e-5):
                    unsorted_distances[element].append(round(distance, 2))
                    neighboring_atom_indices.append(atom_idx)

        distance_dict = {}
        for element, distances in unsorted_distances.items():
            distance_dict[element] = [float(dist) for dist in sorted(distances)]

        return Coordination(distance_dict, round(cutoff, 3),
                            neighboring_atom_indices)


@dataclass
class Coordination(MSONable):
    """Coordination environment around a site.

    Stores neighboring atom information for a specific site.

    Attributes:
        distance_dict: Dict mapping element to list of distances (Angstroms).
        cutoff: Distance cutoff used for coordination (Angstroms).
        neighboring_atom_indices: List of indices of neighboring atoms.

    Example:
        >>> coord = Coordination(
        ...     distance_dict={"O": [2.0, 2.0, 2.0, 2.0]},
        ...     cutoff=3.0,
        ...     neighboring_atom_indices=[0, 1, 2, 3]
        ... )
    """
    distance_dict: Dict[str, List]
    cutoff: float
    neighboring_atom_indices: List[int]
