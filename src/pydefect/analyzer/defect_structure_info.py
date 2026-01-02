# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from dataclasses import dataclass
from typing import Optional, List, Tuple

from monty.json import MSONable
from pydefect.analyzer.defect_structure_comparator import \
    SiteDiff, SiteInfo
from pydefect.defaults import defaults
from pydefect.util.coords import pretty_coords
from pymatgen.core import Structure
from pymatgen.symmetry.groups import SpaceGroup
from tabulate import tabulate
from vise.util.enum import ExtendedEnum
from vise.util.logger import get_logger
from vise.util.mix_in import ToJsonFileMixIn

logger = get_logger(__name__)


class DefectType(MSONable, ExtendedEnum):
    """Enumeration of defect types.

    Attributes:
        vacancy: Single atom removed.
        interstitial: Single atom added.
        substituted: One atom replaced by another.
        vacancy_split: Multiple vacancies of same element.
        interstitial_split: Multiple interstitials of same element.
        unknown: Complex or unrecognized defect.
    """
    vacancy = "vacancy"
    interstitial = "interstitial"
    substituted = "substituted"
    vacancy_split = "vacancy_split"
    interstitial_split = "interstitial_split"
    unknown = "unknown"


def judge_defect_type(site_diff: SiteDiff):
    """Determine defect type from site difference analysis.

    Args:
        site_diff: SiteDiff object from structure comparison.

    Returns:
        DefectType enum value.

    Example:
        >>> from pydefect.analyzer.defect_structure_comparator import SiteDiff
        >>> diff = SiteDiff(removed=[(0, "O", (0.5, 0.5, 0.5))], ...)
        >>> judge_defect_type(diff)
        DefectType.vacancy
    """
    if site_diff.is_vacancy:
        return DefectType.vacancy
    elif site_diff.is_interstitial:
        return DefectType.interstitial
    elif site_diff.is_substituted:
        return DefectType.substituted

    elements_involved = set()
    for _, elem, _ in site_diff.removed + site_diff.inserted:
        elements_involved.add(elem)

    if len(elements_involved) == 1 and not site_diff.removed_by_sub:
        if len(site_diff.removed) - len(site_diff.inserted) == 1:
            return DefectType.vacancy_split
        elif len(site_diff.removed) - len(site_diff.inserted) == -1:
            return DefectType.interstitial_split

    return DefectType.unknown


def remove_dot(point_group_symbol):
    """Remove dots from point group symbol."""
    return "".join([char for char in point_group_symbol if char != "."])


def unique_point_group(pg):
    result = remove_dot(pg)
    if result == "2mm" or result == "m2m":
        return "mm2"
    if result == "-4m2":
        return "-42m"
    if result == "m3":
        return "m-3"
    return result


class SymmRelation(MSONable, ExtendedEnum):
    same = "same"
    subgroup = "subgroup"
    supergroup = "supergroup"
    another = "another"


@dataclass
class Displacement(MSONable):
    specie: str
    original_pos: Tuple[float, float, float]
    final_pos: Tuple[float, float, float]
    distance_from_defect: float
    disp_vector: Tuple[float, float, float]
    displace_distance: float
    angle: Optional[float]


def symmetry_relation(initial_point_group, final_point_group):
    """ Check the point group symmetry relation using the space group relation
    implemented in pymatgen.
    """
    if initial_point_group in ["3m", "-3m"]:
        initial_point_group += "1"
    if final_point_group in ["3m", "-3m"]:
        final_point_group += "1"

    initial = SpaceGroup(f"P{initial_point_group}")
    final = SpaceGroup(f"P{final_point_group}")
    if initial == final:
        return SymmRelation.same
    elif final.is_subgroup(initial):
        return SymmRelation.subgroup
    elif final.is_supergroup(initial):
        return SymmRelation.supergroup
    else:
        return SymmRelation.another


@dataclass
class DefectStructureInfo(MSONable, ToJsonFileMixIn):
    """Structural analysis results for a defect calculation.

    Contains information about defect type, site symmetry changes,
    and atomic displacements after relaxation.

    Attributes:
        shifted_final_structure: Final structure shifted to align with perfect.
        initial_site_sym: Initial defect site point group symmetry.
        final_site_sym: Final defect site point group symmetry.
        site_diff: Difference between perfect and final structures.
        site_diff_from_initial: Difference between initial and final defect.
        symprec: Symmetry precision used for analysis.
        dist_tol: Distance tolerance for site matching.
        anchor_atom_idx: Index of atom used as reference for alignment.
        neighbor_atom_indices: Indices of atoms neighboring the defect.
        neighbor_cutoff_factor: Factor for determining neighbor cutoff.
        drift_vector: Vector of drift during relaxation.
        drift_dist: Magnitude of drift distance.
        center: Estimated defect center coordinates.
        displacements: List of atomic displacements from relaxation.
    """
    shifted_final_structure: Structure
    initial_site_sym: str
    final_site_sym: str
    site_diff: SiteDiff
    site_diff_from_initial: SiteDiff
    symprec: float
    dist_tol: float
    anchor_atom_idx: int
    neighbor_atom_indices: List[int]
    neighbor_cutoff_factor: float
    drift_vector: Tuple[float, float, float]
    drift_dist: float
    center: Tuple[float, float, float]
    displacements: List[Displacement]

    @property
    def symm_relation(self):
        return symmetry_relation(self.initial_site_sym, self.final_site_sym)

    @property
    def same_config_from_init(self):
        return self.site_diff_from_initial.is_no_diff

    @property
    def defect_type(self):
        return judge_defect_type(self.site_diff)

    def __str__(self):
        sym_transition = f"{self.initial_site_sym} " \
                         f"-> {self.final_site_sym} ({self.symm_relation})"
        center_coords = pretty_coords(self.center)
        drift_dist = f"{self.drift_dist:5.3f}" if self.drift_dist else "N.A."
        lines = [" -- defect structure info",
                 f"Defect type: {self.defect_type}",
                 f"Site symmetry: {sym_transition}",
                 f"Has same configuration from initial structure: "
                 f"{self.same_config_from_init}",
                 f"Drift distance: {drift_dist}",
                 f"Defect center: {center_coords}"]

        def _site_info(header: str, site_info: List[SiteInfo]):
            if not site_info:
                return []
            _table = tabulate([[idx, elem, pretty_coords(coords)]
                              for idx, elem, coords in site_info],
                              tablefmt="plain")
            return [header, _table, ""]

        lines.extend(_site_info("Removed atoms:", self.site_diff.removed))
        lines.extend(_site_info("Added atoms:", self.site_diff.inserted))

        if self.same_config_from_init is False:
            lines.extend(_site_info("Removed atoms from initial structure:",
                                    self.site_diff_from_initial.removed))
            lines.extend(_site_info("Inserted atoms to initial structure:",
                                    self.site_diff_from_initial.inserted))

        min_distance = min([disp.distance_from_defect 
                            for disp in self.displacements if disp])
        cutoff = min_distance * self.neighbor_cutoff_factor
        lines.append(f"Neighbor max distance {cutoff:5.3f}")

        lines.append("Displacements")
        indexed_displacements = [[idx, disp] for idx, disp in enumerate(self.displacements)
                                 if disp is not None]
        table = [["Elem", "Dist", "Displace", "Angle", "Index",
                  "Initial site", "", "Final site", "Neighbor"]]

        for final_idx, disp in sorted(indexed_displacements,
                                       key=lambda item: item[1].distance_from_defect):
            is_neighbor = "T" if final_idx in self.neighbor_atom_indices else ""
            if disp.distance_from_defect > defaults.show_structure_cutoff:
                break
            initial_pos = pretty_coords(disp.original_pos)
            final_pos = pretty_coords(disp.final_pos)
            angle = int(round(disp.angle, -1)) if disp.angle else ""
            table.append([disp.specie, round(disp.distance_from_defect, 2),
                          round(disp.displace_distance, 2), angle, final_idx,
                          initial_pos, "->", final_pos, is_neighbor])
        lines.append(tabulate(table, tablefmt="plain"))

        return "\n".join(lines)


