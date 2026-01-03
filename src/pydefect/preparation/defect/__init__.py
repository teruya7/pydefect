# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Defect preparation module.

Public API:
- Models: Defect, SimpleDefect, DefectEntry, DefectSet, PerturbedSite
- Generators: DefectEntryGenerator, DefectSetGenerator
- Functions: create_defect_entry, filter_defect, filter_defect_set
"""

# Data models
from pydefect.preparation.defect.models import (
    Defect,
    SimpleDefect,
    PerturbedSite,
    DefectEntry,
    DefectSet,
    filter_defect,
    filter_defect_set,
    create_defect_entry,
    # Backward compatibility
    screen_simple_defect,
    screen_defect_set,
    make_defect_entry,
)

# Generators
from pydefect.preparation.defect.entry_generator import (
    DefectEntryGenerator,
    perturb_structure,
    # Backward compatibility
    DefectEntriesMaker,
)

from pydefect.preparation.defect.set_generator import (
    DefectSetGenerator,
    charge_set,
    # Backward compatibility
    DefectSetMaker,
)

__all__ = [
    # Models
    "Defect",
    "SimpleDefect",
    "PerturbedSite",
    "DefectEntry",
    "DefectSet",
    # Functions
    "create_defect_entry",
    "filter_defect",
    "filter_defect_set",
    # Generators
    "DefectEntryGenerator",
    "DefectSetGenerator",
    "perturb_structure",
    "charge_set",
    # Backward compatibility
    "screen_simple_defect",
    "screen_defect_set",
    "make_defect_entry",
    "DefectEntriesMaker",
    "DefectSetMaker",
]
