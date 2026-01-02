# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for supercell creation."""

from typing import List, Optional, Tuple

from pymatgen.core import Structure

from pydefect.makers.supercell.supercell_info import SupercellInfo
from pydefect.makers.supercell.supercell_maker import SupercellMaker
from pydefect.makers.supercell.manual_supercell_maker import (
    ManualSupercellMaker,
    make_sites_from_yaml_file,
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
