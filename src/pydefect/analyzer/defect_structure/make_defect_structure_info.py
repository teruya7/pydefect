# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
import math
import warnings
from typing import List, Tuple

import numpy as np
from pydefect.analyzer.defect_structure.defect_structure_comparator import \
    DefectStructureComparator
from pydefect.analyzer.defect_structure.defect_structure_info import Displacement, \
    DefectStructureInfo, unique_point_group
from pydefect.defaults import defaults
from pymatgen.core import PeriodicSite, Structure
from vise.util.logger import get_logger
from vise.util.structure_symmetrizer import StructureSymmetrizer
from vise.util.typing import GenCoords


logger = get_logger(__name__)


def folded_coords(site: PeriodicSite,
                  center: GenCoords
                  ) -> GenCoords:
    """Fold site coordinates to be near center.

    Args:
        site: Periodic site to fold.
        center: Center coordinates to fold towards.

    Returns:
        Folded fractional coordinates.
    """
    _, image = site.distance_and_image_from_frac_coords(center)
    return tuple(site.frac_coords - image)


class MakeDefectStructureInfo:
    """Analyze defect structure changes from relaxation.

    Compares perfect, initial, and final structures to determine
    defect type, symmetry changes, and atomic displacements. The
    final structure is shifted so the defect center is aligned with
    the perfect supercell.

    Attributes:
        defect_structure_info: Resulting DefectStructureInfo object
            containing all analysis results.
        shifted_final: Final structure shifted to align defect center.
        center: Defect center coordinates after drift correction.
        comp_w_perf: Comparator between final and perfect structures.
        comp_w_init: Comparator between final and initial structures.

    Example:
        >>> from pymatgen.core import Structure
        >>> perfect = Structure.from_file("perfect/POSCAR")
        >>> initial = Structure.from_file("defect/POSCAR")
        >>> final = Structure.from_file("defect/CONTCAR")
        >>> analyzer = MakeDefectStructureInfo(
        ...     perfect=perfect,
        ...     initial=initial,
        ...     final=final,
        ...     symprec=0.01,
        ...     dist_tol=0.5
        ... )
        >>> print(analyzer.defect_structure_info)
    """
    def __init__(self,
                 perfect: Structure,
                 initial: Structure,
                 final: Structure,
                 symprec: float,
                 dist_tol: float,
                 neighbor_cutoff_factor: float = None):
        """Initialize MakeDefectStructureInfo.

        Args:
            perfect: Perfect supercell structure.
            initial: Initial defect structure before relaxation.
            final: Final defect structure after relaxation.
            symprec: Symmetry precision for spglib.
            dist_tol: Distance tolerance for site matching (Angstroms).
            neighbor_cutoff_factor: Cutoff factor for neighbor detection.
                Defaults to pydefect defaults.cutoff_distance_factor.
        """

        self.cutoff = neighbor_cutoff_factor or defaults.cutoff_distance_factor
        self.symprec = symprec
        self.perfect, self.initial, self.final = perfect, initial, final
        self.dist_tol = dist_tol

        assert perfect.lattice == initial.lattice == final.lattice
        self.lattice = perfect.lattice

        self._orig_comp = DefectStructureComparator(final, perfect, dist_tol)
        self._orig_center = self._orig_comp.defect_center_coord
        self._calc_drift()

        self.shifted_final = final.copy()
        self.center = tuple(self._orig_center - self._drift_vector)
        for site in self.shifted_final:
            site.frac_coords -= np.array(self._drift_vector)

        self.comp_w_perf = DefectStructureComparator(
            self.shifted_final, perfect, dist_tol)
        self.comp_w_init = DefectStructureComparator(
            self.shifted_final, initial, dist_tol)

        self.defect_structure_info = DefectStructureInfo(
            shifted_final_structure=self.shifted_final,
            initial_site_sym=self.initial_site_sym,
            final_site_sym=self.final_site_sym,
            site_diff=self.comp_w_perf.make_site_diff(),
            site_diff_from_initial=self.comp_w_init.make_site_diff(),
            symprec=symprec,
            dist_tol=dist_tol,
            anchor_atom_idx=self._anchor_atom_idx,
            neighbor_atom_indices=self._neighbor_atom_indices,
            neighbor_cutoff_factor=self.cutoff,
            drift_vector=self._drift_vector,
            drift_dist=self._drift_distance,
            center=self.center,
            displacements=self.calc_displacements())

    @property
    def _neighbor_atom_indices(self):
        return self.comp_w_perf.neighboring_atom_indices(self.cutoff)

    @property
    def initial_site_sym(self):
        return self._unique_point_group(self.initial)

    @property
    def final_site_sym(self):
        return self._unique_point_group(self.final)

    def _unique_point_group(self, structure):
        symmetrizer = StructureSymmetrizer(structure, self.symprec)
        return unique_point_group(symmetrizer.point_group)

    def _calc_drift(self) -> None:
        """Calculate drift vector from relaxation."""
        distances = []
        for site in self.final:
            distances.append(
                site.distance_and_image_from_frac_coords(self._orig_center)[0])

        self._anchor_atom_idx = int(np.argmax(distances))
        perfect_anchor_idx = self._orig_comp.defect_to_perfect_indices[self._anchor_atom_idx]
        if perfect_anchor_idx is None:
            logger.warning("The anchoring atom cannot be found, so the drift "
                           "vector is set to zero.")
            self._drift_distance = None
            self._drift_vector = tuple([0.0]*3)
            return

        defect_site = self.final[self._anchor_atom_idx]
        perfect_coords = self.perfect[perfect_anchor_idx].frac_coords
        self._drift_distance, image = \
            defect_site.distance_and_image_from_frac_coords(perfect_coords)
        self._drift_vector = tuple(defect_site.frac_coords - perfect_coords - image)

    def calc_displacements(self):
        """Calculate atomic displacements from initial to final structure."""
        result = []
        atom_mapping = self.comp_w_init.atom_mapping
        for defect_idx in range(len(self.shifted_final)):
            if defect_idx not in atom_mapping:
                result.append(None)
            else:
                initial_idx = atom_mapping[defect_idx]
                initial_element = str(self.initial[initial_idx].specie)
                final_element = str(self.shifted_final[defect_idx].specie)
                if initial_element != final_element:
                    result.append(None)
                    continue
                initial_pos = folded_coords(self.initial[initial_idx], self.center)
                final_pos = folded_coords(self.shifted_final[defect_idx], initial_pos)

                initial_pos_vector = self.lattice.get_cartesian_coords(
                    np.array(initial_pos) - self.center)
                initial_distance = np.linalg.norm(initial_pos_vector)

                displacement_distance, translation = self.lattice.get_distance_and_image(
                    self.shifted_final.frac_coords[defect_idx], 
                    self.initial.frac_coords[initial_idx])
                displacement_vector = self.lattice.get_cartesian_coords(
                    self.shifted_final.frac_coords[defect_idx] 
                    - self.initial.frac_coords[initial_idx] - translation)

                angle = self.calc_disp_angle(
                    displacement_distance, displacement_vector, 
                    initial_distance, initial_pos_vector)

                result.append(Displacement(
                    specie=initial_element,
                    original_pos=initial_pos,
                    final_pos=final_pos,
                    distance_from_defect=initial_distance,
                    disp_vector=tuple(displacement_vector),
                    displace_distance=displacement_distance,
                    angle=angle))
        return result

    @staticmethod
    def calc_disp_angle(disp_dist, disp_vec, ini_dist, initial_pos_vec):
        inner_prod = sum(initial_pos_vec * disp_vec)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # ignore "RuntimeWarning: invalid value encountered in double_scalars"
            cos = round(inner_prod / (ini_dist * disp_dist), 10)
        result = float(round(180 * (1 - np.arccos(cos) / np.pi), 1))
        if math.isnan(result):
            result = None
        return result

