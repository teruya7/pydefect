# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for supercell and defect structure creation.

This module provides functions for creating supercells, defect sets,
and managing interstitial sites.
"""

from typing import List, Optional, Dict, Tuple, Union

from pymatgen.core import Structure
from pymatgen.io.vasp import Chgcar

from pydefect.preparation.supercell.supercell import Supercell
from pydefect.preparation.supercell.supercell_info import SupercellInfo
from pydefect.preparation.supercell.supercell_maker import SupercellMaker
from pydefect.preparation.supercell.manual_supercell_maker import (
    ManualSupercellMaker,
    make_sites_from_yaml_file,
)
from pydefect.preparation.defect.defect_set import DefectSet
from pydefect.preparation.defect.defect_set_maker import DefectSetMaker
from pydefect.preparation.defect.defect_entries_maker import DefectEntriesMaker
from pydefect.preparation.interstitial.append_interstitial import (
    append_interstitial as _append_interstitial,
)
from pydefect.preparation.interstitial.local_extrema import (
    VolumetricDataAnalyzeParams,
    VolumetricDataLocalExtrema,
)
from pydefect.preparation.interstitial.make_local_extrema import (
    make_local_extrema_from_volumetric_data,
)


def make_supercell(
    unitcell: Structure,
    matrix: Optional[List[List[int]]] = None,
    min_num_atoms: int = 50,
    max_num_atoms: int = 300,
    analyze_symmetry: bool = True,
    sites_yaml_filename: Optional[str] = None,
) -> Tuple[SupercellInfo, Structure]:
    """Create a supercell from a unitcell structure.

    Args:
        unitcell: The primitive/unit cell structure.
        matrix: Optional explicit transformation matrix (3x3).
            If provided, min_num_atoms and max_num_atoms are ignored.
        min_num_atoms: Minimum number of atoms in the supercell.
        max_num_atoms: Maximum number of atoms in the supercell.
        analyze_symmetry: If True, use automatic symmetry analysis.
            If False, use manual site specification from sites_yaml_filename.
        sites_yaml_filename: Path to YAML file with site information.
            Required when analyze_symmetry is False.

    Returns:
        Tuple of (SupercellInfo, supercell Structure)

    Example:
        >>> from pymatgen.core import Structure
        >>> from pydefect import api
        >>> unitcell = Structure.from_file("POSCAR")
        >>> supercell_info, supercell = api.make_supercell(unitcell)
        >>> supercell_info.to_json_file()
        >>> supercell.to("SPOSCAR")
    """
    kwargs = {}

    if analyze_symmetry:
        supercell_maker = SupercellMaker
    else:
        supercell_maker = ManualSupercellMaker
        if sites_yaml_filename:
            kwargs["sites"] = make_sites_from_yaml_file(sites_yaml_filename)

    if matrix:
        maker = supercell_maker(unitcell, matrix=matrix, **kwargs)
    else:
        kwargs["min_num_atoms"] = min_num_atoms
        kwargs["max_num_atoms"] = max_num_atoms
        maker = supercell_maker(unitcell, **kwargs)

    return maker.supercell_info, maker.supercell.structure


def make_defect_set(
    supercell_info: SupercellInfo,
    oxi_states: Optional[Dict[str, int]] = None,
    dopants: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
) -> DefectSet:
    """Create a set of defect configurations.

    Args:
        supercell_info: SupercellInfo object containing supercell information.
        oxi_states: Dictionary mapping element symbols to oxidation states.
            Example: {"Mg": 2, "O": -2}
        dopants: List of dopant element symbols to include.
        keywords: List of keywords to filter defects.

    Returns:
        DefectSet containing all defect configurations.

    Example:
        >>> from pydefect import api
        >>> supercell_info = SupercellInfo.from_json("supercell_info.json")
        >>> defect_set = api.make_defect_set(supercell_info, dopants=["Al"])
        >>> defect_set.to_yaml()
    """
    maker = DefectSetMaker(
        supercell_info,
        oxi_states,
        dopants,
        keywords=keywords,
    )
    return maker.defect_set


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


def make_defect_entries(
    supercell_info: SupercellInfo,
    defect_set: DefectSet,
):
    """Create defect entries from supercell info and defect set.

    Args:
        supercell_info: SupercellInfo object.
        defect_set: DefectSet object.

    Returns:
        List of DefectEntry objects.

    Example:
        >>> from pydefect import api
        >>> entries = api.make_defect_entries(supercell_info, defect_set)
        >>> for entry in entries:
        ...     entry.to_json_file(f"{entry.full_name}/defect_entry.json")
    """
    maker = DefectEntriesMaker(supercell_info, defect_set)
    return maker.defect_entries

