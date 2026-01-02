# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Localized state data classes."""

from dataclasses import dataclass
from typing import List, Dict, Optional

from monty.json import MSONable
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn
from vise.util.typing import GenCoords

from pydefect.analysis.band_edge.models.edge_info import EdgeInfo
from pydefect.analysis.band_edge.models.orbital_info import pretty_orbital
from pydefect.defaults import defaults
from pydefect.utils.formatting import pretty_coords


@dataclass
class LocalizedOrbital(MSONable):
    """In-gap localized orbital state.

    Represents a defect-induced localized state within the band gap.

    Attributes:
        band_idx: 0-based band index.
        ave_energy: K-point averaged energy in eV.
        occupation: Occupation number.
        orbitals: Orbital decomposition by element.
        participation_ratio: Spatial localization measure.
        radius: Estimated spatial extent in Angstrom.
        center: Estimated center coordinates.
    """
    band_idx: int
    ave_energy: float
    occupation: float
    orbitals: Dict[str, List[float]]
    participation_ratio: Optional[float] = None
    radius: Optional[float] = None
    center: Optional[GenCoords] = None

    @property
    def band_index(self):
        return self.band_idx

    @property
    def eigenvalue(self):
        return self.ave_energy


@dataclass
class BandEdgeState(MSONable):
    """Information related to the band edge in a defect supercell.

    E.g.,
    # 124   --   <- CBM
    # 123   --   <- localized orbital
    # 122   --   <- localized orbital
    # 121   --   <- VBM
    """

    vbm_info: EdgeInfo
    cbm_info: EdgeInfo
    vbm_orbital_diff: float  # Difference from those of perfect supercell.
    cbm_orbital_diff: float
    localized_orbitals: List[LocalizedOrbital]
    vbm_hole_occupation: float
    cbm_electron_occupation: float

    @property
    def is_shallow(self):
        return self.has_donor_phs or self.has_acceptor_phs

    @property
    def has_donor_phs(self):
        return self.cbm_electron_occupation > defaults.state_occupied_threshold

    @property
    def has_acceptor_phs(self):
        return self.vbm_hole_occupation > defaults.state_occupied_threshold

    @property
    def has_unoccupied_localized_state(self):
        return any([lo.occupation < defaults.state_unoccupied_threshold
                    for lo in self.localized_orbitals])

    @property
    def has_occupied_localized_state(self):
        return any([lo.occupation > defaults.state_occupied_threshold
                    for lo in self.localized_orbitals])

    def __str__(self):
        return "\n".join([self._edge_info,
                          "---", "Localized Orbital(s)",
                          self._orbital_info])

    @property
    def _orbital_info(self):
        inner_table = [["Index", "Energy", "P-ratio", "Occupation", "Orbitals"]]
        w_radius = self.localized_orbitals and self.localized_orbitals[0].radius
        if w_radius:
            inner_table[0].extend(["Radius", "Center"])

        for lo in self.localized_orbitals:
            participation_ratio = f"{lo.participation_ratio:5.2f}" \
                if lo.participation_ratio else "None"
            inner = [lo.band_idx + 1,
                     f"{lo.ave_energy:7.3f}",
                     participation_ratio,
                     f"{lo.occupation:5.2f}",
                     pretty_orbital(lo.orbitals)]
            if w_radius:
                inner.extend([f"{lo.radius:5.2f}", pretty_coords(lo.center)])
            inner_table.append(inner)

        return tabulate(inner_table, tablefmt="plain")

    @property
    def _edge_info(self):
        inner_table = [["", "Index", "Energy", "P-ratio", "Occupation",
                        "OrbDiff", "Orbitals", "K-point coords"],
                       ["VBM"] + self._show_edge_info(
                           self.vbm_info, self.vbm_orbital_diff),
                       ["CBM"] + self._show_edge_info(
                           self.cbm_info, self.cbm_orbital_diff)]
        table = tabulate(inner_table, tablefmt="plain")
        vbm_phs = f"vbm has acceptor phs: {self.has_acceptor_phs} " \
                  f"({self.vbm_hole_occupation:5.3f} vs. {defaults.state_occupied_threshold})"
        cbm_phs = f"cbm has donor phs: {self.has_donor_phs} " \
                  f"({self.cbm_electron_occupation:5.3f} vs. {defaults.state_occupied_threshold})"
        return "\n".join([table, vbm_phs, cbm_phs])

    @staticmethod
    def _show_edge_info(edge_info: EdgeInfo, orb_diff: float):
        p_ratio = f"{edge_info.p_ratio:5.2f}" if edge_info.p_ratio else "None"
        return [edge_info.band_idx + 1,
                f"{edge_info.energy:7.3f}",
                p_ratio,
                f"{edge_info.occupation:5.2f}",
                f"{orb_diff:5.2f}",
                pretty_orbital(edge_info.orbital_info.orbitals),
                pretty_coords(edge_info.kpt_coord)]


@dataclass
class BandEdgeStates(MSONable, ToJsonFileMixIn):
    """Band edge states for all spins in a defect supercell.

    Container for spin-resolved BandEdgeState objects.
    Provides aggregate properties across all spin channels.

    Attributes:
        states: List of BandEdgeState, one per spin channel.
    """
    states: List[BandEdgeState]  # by spin.

    @property
    def is_shallow(self):
        return any([i.is_shallow for i in self.states])

    @property
    def has_donor_phs(self):
        return any([i.has_donor_phs for i in self.states])

    @property
    def has_acceptor_phs(self):
        return any([i.has_acceptor_phs for i in self.states])

    @property
    def has_unoccupied_localized_state(self):
        return any([i.has_unoccupied_localized_state for i in self.states])

    @property
    def has_occupied_localized_state(self):
        return any([i.has_occupied_localized_state for i in self.states])

    @property
    def band_indices_from_vbm_to_cbm(self) -> List[int]:
        indices_set = set()
        for state in self.states:
            indices_set.add(state.vbm_info.band_idx)
            for lo in state.localized_orbitals:
                indices_set.add(lo.band_idx)
            indices_set.add(state.cbm_info.band_idx)
        return sorted([i for i in indices_set])

    def __str__(self):
        lines = [" -- band-edge states info"]
        for spin, state in zip(["up", "down"], self.states):
            lines.append(f"Spin-{spin}")
            lines.append(state.__str__())
            lines.append("")

        return "\n".join(lines)
