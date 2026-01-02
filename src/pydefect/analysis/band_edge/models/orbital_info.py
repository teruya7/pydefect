# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Orbital information data classes."""

from copy import deepcopy
from dataclasses import dataclass
from typing import List, Dict, Tuple

import numpy as np
from monty.json import MSONable
from tabulate import tabulate
from vise.util.logger import get_logger
from vise.util.mix_in import ToJsonFileMixIn
from vise.util.typing import GenCoords

from pydefect.utils.formatting import pretty_coords

logger = get_logger(__name__)

printed_orbital_weight_threshold = 0.1


def pretty_orbital(orbitals: Dict[str, List[float]]):
    """Format orbital weights as readable string.

    Converts orbital weight dictionary into a human-readable string,
    filtering out small contributions below the threshold.

    Args:
        orbitals: Dict mapping element symbol to list of orbital weights.
            The list contains [s, p, d, (f)] weights in order.

    Returns:
        Formatted string like "Mn-d: 0.50, O-p: 0.40".
        Only orbitals with weight > printed_orbital_weight_threshold
        (0.1) are included.

    Example:
        >>> pretty_orbital({"Mn": [0.01, 0.02, 0.85, 0.02], "O": [0.0, 0.10, 0.0]})
        'Mn-d: 0.85, O-p: 0.10'
    """
    orbital_infos = []
    for element, orbital_weights in orbitals.items():
        for orbital_name, weight in zip(["s", "p", "d", "f"], orbital_weights):
            if weight > printed_orbital_weight_threshold:
                orbital_infos.append(f"{element}-{orbital_name}: {weight:.2f}")
    return ", ".join(orbital_infos)


@dataclass
class OrbitalInfo(MSONable):
    """Orbital-resolved information for a single band at one k-point.

    Contains eigenvalue, orbital decomposition, and occupation for
    detailed band character analysis. Note that orbital projections
    are PAW projector dependent and vary between VASP versions.

    Attributes:
        energy: Eigenvalue energy in eV (typically referenced to VBM).
        orbitals: Dict mapping element symbol to [s, p, d, (f)] orbital weights.
            Weights are normalized fractions summing approximately to 1.
        occupation: Band occupation (0-2 for non-spin-polarized, 0-1 for spin).
        participation_ratio: Localization measure from 0 to 1.
            Higher values indicate more delocalized states.
            None if not calculated.

    Example:
        >>> orb_info = OrbitalInfo(
        ...     energy=0.5,
        ...     orbitals={"O": [0.1, 0.8, 0.0], "Mg": [0.05, 0.05, 0.0]},
        ...     occupation=2.0,
        ...     participation_ratio=0.95
        ... )
    """
    energy: float  # max eigenvalue
    # {"Mn": [0.01, ..], "O": [0.03, 0.5]},
    # where lists contain s, p, d, (f) orbital components.
    orbitals: Dict[str, List[float]]
    occupation: float
    participation_ratio: float = None


@dataclass
class BandEdgeOrbitalInfos(MSONable, ToJsonFileMixIn):
    """Collection of orbital information for bands near band edges.

    Stores detailed orbital decomposition for each band at each k-point,
    enabling analysis of band character and localization.

    Attributes:
        orbital_infos: [spin, k-idx, band-idx] -> OrbitalInfo.
        kpt_coords: K-point fractional coordinates.
        kpt_weights: K-point weights for averaging.
        lowest_band_index: 0-based index of lowest stored band.
        fermi_level: Fermi level energy in eV.
        eigval_shift: Energy shift to apply (e.g., for alignment).
    """
    orbital_infos: List[List[List["OrbitalInfo"]]]  # [spin, k-idx, band-idx]
    kpt_coords: List[GenCoords]
    kpt_weights: List[float]
    lowest_band_index: int  # python convention starting from 0.
    fermi_level: float
    eigval_shift: float = 0.0  # add this value to the energies.

    @property
    def shifted_orbital_infos(self) -> List[List[List[OrbitalInfo]]]:
        """Return new orbital_infos with energy shifted by eigval_shift."""
        new_orbital_infos = deepcopy(self.orbital_infos)
        for spin_idx in range(len(new_orbital_infos)):
            for k_idx in range(len(new_orbital_infos[spin_idx])):
                for band_idx in range(len(new_orbital_infos[spin_idx][k_idx])):
                    new_orbital_infos[spin_idx][k_idx][band_idx].energy \
                        += self.eigval_shift
        return new_orbital_infos

    def kpt_idx(self, kpt_coord):
        """Find index of k-point matching given coordinates."""
        for idx, stored_kpt in enumerate(self.kpt_coords):
            if sum(abs(coord1 - coord2) for coord1, coord2 in zip(stored_kpt, kpt_coord)) < 1e-5:
                return idx
        raise ValueError(f"{kpt_coord} not in kpt_coords {self.kpt_coords}.")

    @property
    def energies_and_occupations(self) -> List[List[List[List[float]]]]:
        result = np.zeros(np.shape(self.orbital_infos) + (2,))
        if self.eigval_shift:
            logger.info(
                f"The eigenvalues are shifted by {self.eigval_shift:4.2f}")
        for i, x in enumerate(self.orbital_infos):
            for j, y in enumerate(x):
                for k, z in enumerate(y):
                    result[i][j][k] = \
                        [z.energy + self.eigval_shift, z.occupation]
        return result.tolist()

    def __str__(self):
        return "\n".join([" -- band-edge orbitals info",
                          "K-points info",
                          self._kpt_block,
                          "",
                          "Band info near band edges",
                          self._band_block])

    @property
    def _band_block(self):
        band_block = [["Index", "Kpoint index", "Energy", "Occupation",
                       "P-ratio", "Orbital"]]
        if self.eigval_shift:
            band_block[0].insert(3, "Shifted")

        for orbital_info in self.orbital_infos:
            max_idx, min_idx, t_orb_info = self._band_idx_range(orbital_info)
            for band_idx in range(min_idx, max_idx):
                actual_band_idx = band_idx + self.lowest_band_index + 1
                for kpt_idx, orb_info in enumerate(t_orb_info[band_idx], 1):

                    energy = f"{orb_info.energy :5.2f}"
                    occupation = f"{orb_info.occupation:4.1f}"
                    if orb_info.participation_ratio:
                        p_ratio = f"{orb_info.participation_ratio:4.1f}"
                    else:
                        p_ratio = "N.A."
                    orbs = pretty_orbital(orb_info.orbitals)
                    data = [actual_band_idx, kpt_idx, energy, occupation,
                            p_ratio, orbs]
                    if self.eigval_shift:
                        shifted = f"{orb_info.energy + self.eigval_shift :5.2f}"
                        data.insert(3, shifted)
                    band_block.append(data)
                band_block.append(["--"])
            band_block.append("")
        return tabulate(band_block, tablefmt="plain")

    @property
    def _kpt_block(self):
        kpt_block = [["Index", "Coords", "Weight"]]
        for index, (kpt_coord, kpt_weight) in enumerate(
                zip(self.kpt_coords, self.kpt_weights), 1):
            coord = pretty_coords(kpt_coord)
            weight = f"{kpt_weight:4.3f}"
            kpt_block.append([index, coord, weight])
        return tabulate(kpt_block, tablefmt="plain")

    @staticmethod
    def _band_idx_range(orbital_info: List[List[OrbitalInfo]]
                        ) -> Tuple[int, int, List[List[OrbitalInfo]]]:
        # swap [kpt_idx][band_idx] -> [bane_idx][kpt_idx]
        t_orbital_info = np.array(orbital_info).T.tolist()
        middle_idx = int(len(t_orbital_info) / 2)
        for band_idx, (upper, lower) in enumerate(zip(t_orbital_info[1:],
                                                      t_orbital_info[:-1])):
            # determine the band_idx where the occupation changes largely.
            if lower[0].occupation - upper[0].occupation > 0.1:
                middle_idx = band_idx + 1
                break
        max_idx = min(middle_idx + 3, len(t_orbital_info))
        min_idx = max(middle_idx - 3, 0)
        return max_idx, min_idx, t_orbital_info


@dataclass
class BandEdgeEigenvalues(MSONable, ToJsonFileMixIn):
    """Eigenvalues and occupations at band edges.

    Stores energy eigenvalues and occupation numbers for bands
    near the band edges at each k-point. This data structure is
    used for band edge analysis and plotting.

    Attributes:
        energies_and_occupations: Nested list indexed as
            [spin, k-idx, band-idx] -> [energy, occupation].
            Energy in eV, occupation from 0 to 2 (or 1 for spin-polarized).
        kpt_coords: List of k-point fractional coordinates in
            reciprocal lattice units.
        lowest_band_index: 0-based index of the lowest band stored.
            Used for proper band numbering in output.

    Example:
        >>> bee = BandEdgeEigenvalues(
        ...     energies_and_occupations=[[[[-0.5, 2.0], [0.5, 0.0]]]],
        ...     kpt_coords=[[0.0, 0.0, 0.0]],
        ...     lowest_band_index=10
        ... )
    """
    # [spin, k-idx, band-idx] = energy, occupation
    energies_and_occupations: List[List[List[List[float]]]]
    kpt_coords: List[List[float]]
    lowest_band_index: int
