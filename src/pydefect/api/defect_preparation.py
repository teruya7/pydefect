# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for defect preparation operations.

This module provides functions for creating defect sets and entries.
"""

from typing import Dict, List, Optional

from pydefect.preparation.defect.models.entry import DefectEntry
from pydefect.preparation.defect.entry_generator import DefectEntryGenerator
from pydefect.preparation.defect.models.set import DefectSet
from pydefect.preparation.defect.set_generator import DefectSetGenerator
from pydefect.preparation.supercell.models.supercell_info import SupercellInfo


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
    maker = DefectSetGenerator(
        supercell_info,
        oxi_states,
        dopants,
        keywords=keywords,
    )
    return maker.defect_set


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
    maker = DefectEntryGenerator(supercell_info, defect_set)
    return maker.defect_entries
