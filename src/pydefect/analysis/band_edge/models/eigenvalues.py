# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Eigenvalue data class."""

from dataclasses import dataclass
from typing import List

from monty.json import MSONable
from vise.util.mix_in import ToJsonFileMixIn


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
