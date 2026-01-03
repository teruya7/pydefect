# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Unit cell analysis module.

Public API:
- Models: Unitcell
- Functions: create_unitcell_from_vasp
"""

# Data models
from pydefect.analysis.unitcell.models import Unitcell

# Creation function
from pydefect.analysis.unitcell.unitcell import (
    create_unitcell_from_vasp,
    # Backward compatibility
    make_unitcell_from_vasp,
)

__all__ = [
    "Unitcell",
    "create_unitcell_from_vasp",
    # Backward compatibility
    "make_unitcell_from_vasp",
]
