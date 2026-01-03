# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Defect structure analysis result."""

from dataclasses import dataclass
from typing import List, Tuple

from monty.json import MSONable
from pymatgen.core import Structure
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn

from pydefect.analysis.defect_structure.models.site_diff import SiteDiff, SiteInfo
from pydefect.analysis.defect_structure.models.displacement import Displacement
from pydefect.analysis.defect_structure.models.defect_type import (
    determine_defect_type, symmetry_relation,
)
from pydefect.defaults import defaults
from pydefect.utils.formatting import pretty_coords


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
        return determine_defect_type(self.site_diff)

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
