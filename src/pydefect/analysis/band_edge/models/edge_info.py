# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Edge information data classes."""

from dataclasses import dataclass

from monty.json import MSONable
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn
from vise.util.typing import Coords

from pydefect.analysis.band_edge.models.orbital_info import (
    OrbitalInfo, pretty_orbital
)
from pydefect.utils.formatting import pretty_coords


@dataclass
class EdgeInfo(MSONable):
    """Information for a particular band edge, namely VBM or CBM."""
    band_idx: int
    kpt_coord: Coords
    orbital_info: "OrbitalInfo"

    @property
    def orbitals(self):
        return self.orbital_info.orbitals

    @property
    def energy(self):
        return self.orbital_info.energy

    @property
    def occupation(self):
        return self.orbital_info.occupation

    @property
    def p_ratio(self):
        return self.orbital_info.participation_ratio


@dataclass
class PerfectBandEdgeState(MSONable, ToJsonFileMixIn):
    """Band edge states for a perfect (defect-free) supercell.

    Reference data for comparing defect-induced band edge changes.

    Attributes:
        vbm_info: EdgeInfo for valence band maximum.
        cbm_info: EdgeInfo for conduction band minimum.
    """
    vbm_info: EdgeInfo
    cbm_info: EdgeInfo

    def __str__(self):
        def show_edge_info(edge_info: EdgeInfo):
            return [edge_info.band_idx,
                    edge_info.energy,
                    f"{edge_info.occupation:5.2f}",
                    pretty_orbital(edge_info.orbital_info.orbitals),
                    pretty_coords(edge_info.kpt_coord)]

        return tabulate([
            ["", "Index", "Energy", "Occupation", "Orbitals", "K-point coords"],
            ["VBM"] + show_edge_info(self.vbm_info),
            ["CBM"] + show_edge_info(self.cbm_info)], tablefmt="plain")
