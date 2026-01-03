# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for interstitial site management.

This module provides functions for finding and managing interstitial sites.
"""

from typing import List, Optional, Union

from pymatgen.io.vasp import Chgcar
from pymatgen.core import Structure

from pydefect.preparation.supercell.interstitial_utils import (
    append_interstitial as _append_interstitial,
)
from pydefect.preparation.supercell.models.local_extrema import (
    VolumetricDataAnalyzeParams,
    VolumetricDataLocalExtrema,
)
from pydefect.preparation.supercell.interstitial_finder import (
    make_local_extrema_from_volumetric_data,
)
from pydefect.preparation.supercell.models.supercell_info import SupercellInfo


def append_interstitial(
    supercell_info: SupercellInfo,
    base_structure: Structure,
    frac_coords: List[float],
    info: Optional[str] = None,
) -> SupercellInfo:
    """Append an interstitial site to SupercellInfo.

    Args:
        supercell_info: Existing SupercellInfo object.
        base_structure: Base structure to reference for interstitial.
        frac_coords: Fractional coordinates [x, y, z] of the interstitial.
        info: Optional description of the interstitial site.

    Returns:
        Updated SupercellInfo with new interstitial site.

    Example:
        >>> from pydefect import api
        >>> supercell_info = api.append_interstitial(
        ...     supercell_info, structure, [0.5, 0.5, 0.5], info="octahedral"
        ... )
    """
    return _append_interstitial(
        supercell_info,
        base_structure,
        [frac_coords],
        [info] if info else [None],
    )


def pop_interstitial(
    supercell_info: SupercellInfo,
    index: Optional[int] = None,
    pop_all: bool = False,
) -> SupercellInfo:
    """Remove interstitial site(s) from SupercellInfo.

    Args:
        supercell_info: SupercellInfo object to modify.
        index: 1-based index of interstitial to remove.
            Required if pop_all is False.
        pop_all: If True, remove all interstitials.

    Returns:
        Modified SupercellInfo object.
    """
    if pop_all:
        while supercell_info.interstitials:
            supercell_info.interstitials.pop()
    else:
        if index is None or index < 1:
            raise ValueError("index must be >= 1 when pop_all is False")
        supercell_info.interstitials.pop(index - 1)

    return supercell_info


def make_local_extrema(
    volumetric_data: Union[Chgcar, List[Chgcar]],
    threshold_frac: Optional[float] = None,
    threshold_abs: Optional[float] = None,
    min_dist: float = 0.5,
    tol: float = 0.5,
    radius: float = 0.4,
    find_max: bool = False,
    supercell_info: Optional[SupercellInfo] = None,
) -> VolumetricDataLocalExtrema:
    """Find local extrema in volumetric data for interstitial sites.

    Args:
        volumetric_data: Chgcar or list of Chgcar to analyze.
        threshold_frac: Fractional threshold for extrema detection.
        threshold_abs: Absolute threshold for extrema detection.
        min_dist: Minimum distance between extrema.
        tol: Tolerance for grouping equivalent sites.
        radius: Radius for local extrema search.
        find_max: If True, find maxima instead of minima.
        supercell_info: Optional SupercellInfo for structure reference.

    Returns:
        LocalExtrema object containing found sites.

    Example:
        >>> from pydefect import api
        >>> from pymatgen.io.vasp import Chgcar
        >>> extrema = api.make_local_extrema(Chgcar.from_file("CHGCAR"))
        >>> extrema.to_json_file()
    """
    if isinstance(volumetric_data, list):
        vd = volumetric_data[0]
        for v in volumetric_data[1:]:
            vd += v
    else:
        vd = volumetric_data

    params = VolumetricDataAnalyzeParams(
        threshold_frac, threshold_abs, min_dist, tol, radius
    )

    return make_local_extrema_from_volumetric_data(
        volumetric_data=vd,
        params=params,
        info=supercell_info,
        find_min=not find_max,
    )
