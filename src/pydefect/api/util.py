# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for utility functions.

This module provides utility functions for printing JSON/YAML files
and creating VESTA visualization files.
"""

from pathlib import Path
from typing import Optional

from monty.serialization import loadfn

from pydefect.analyzer.defect_structure.defect_structure_info import DefectStructureInfo
from pydefect.analyzer.defect_structure.make_defect_vesta_file import MakeDefectVestaFile
from pydefect.defaults import defaults


def print_json(
    filename: str,
    use_repr: bool = False,
) -> str:
    """Print the contents of a JSON/YAML file.

    Args:
        filename: Path to JSON or YAML file.
        use_repr: If True, use __repr__ instead of __str__.

    Returns:
        String representation of the object.

    Example:
        >>> from pydefect import api
        >>> content = api.print_json("supercell_info.json")
        >>> print(content)
    """
    obj = loadfn(filename)
    return obj.__repr__() if use_repr else obj.__str__()


def make_defect_vesta_file(
    defect_structure_info: DefectStructureInfo,
    cutoff: float = defaults.show_structure_cutoff,
    min_displace_w_arrows: float = 0.1,
    arrow_factor: float = 3.0,
    title: Optional[str] = None,
) -> MakeDefectVestaFile:
    """Create VESTA visualization files for defect structures.

    Args:
        defect_structure_info: DefectStructureInfo object.
        cutoff: Cutoff distance for showing atoms around defect.
        min_displace_w_arrows: Minimum displacement to show arrows.
        arrow_factor: Scaling factor for displacement arrows.
        title: Title for the VESTA file.

    Returns:
        MakeDefectVestaFile object with initial_vesta and final_vesta attributes.

    Example:
        >>> from pydefect import api
        >>> from monty.serialization import loadfn
        >>> dsi = loadfn("defect_structure_info.json")
        >>> vesta = api.make_defect_vesta_file(dsi, title="Va_O1")
        >>> vesta.initial_vesta.write_file("initial.vesta")
        >>> vesta.final_vesta.write_file("final.vesta")
    """
    return MakeDefectVestaFile(
        defect_structure_info=defect_structure_info,
        cutoff=cutoff,
        min_displace_w_arrows=min_displace_w_arrows,
        arrow_factor=arrow_factor,
        title=title,
    )
