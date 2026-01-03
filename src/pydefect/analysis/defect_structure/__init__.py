# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Defect structure analysis module.

Public API:
- Models: SiteDiff, Displacement, DefectType, SymmRelation, DefectStructureInfo
- Analyzers: StructureComparator, DefectStructureAnalyzer
- Utilities: VestaFileGenerator, refine_defect_structure
"""

# Data models
from pydefect.analysis.defect_structure.models import (
    SiteDiff,
    SiteInfo,
    Displacement,
    DefectType,
    SymmRelation,
    DefectStructureInfo,
    determine_defect_type,
    symmetry_relation,
    unique_point_group,
    # Backward compatibility
    judge_defect_type,
)

# Comparator
from pydefect.analysis.defect_structure.comparator import (
    StructureComparator,
    # Backward compatibility
    DefectStructureComparator,
)

# Analyzer
from pydefect.analysis.defect_structure.analyzer import (
    DefectStructureAnalyzer,
    folded_coords,
    # Backward compatibility
    MakeDefectStructureInfo,
)

# VESTA file generator
from pydefect.analysis.defect_structure.vesta import (
    VestaFileGenerator,
    fold_coords_in_structure,
    # Backward compatibility
    MakeDefectVestaFile,
)

# Refinement
from pydefect.analysis.defect_structure.refine import (
    refine_defect_structure,
)

__all__ = [
    # Models
    "SiteDiff",
    "SiteInfo",
    "Displacement",
    "DefectType",
    "SymmRelation",
    "DefectStructureInfo",
    "determine_defect_type",
    "symmetry_relation",
    "unique_point_group",
    # Comparator
    "StructureComparator",
    # Analyzer
    "DefectStructureAnalyzer",
    "folded_coords",
    # VESTA
    "VestaFileGenerator",
    "fold_coords_in_structure",
    # Refinement
    "refine_defect_structure",
    # Backward compatibility aliases
    "judge_defect_type",
    "DefectStructureComparator",
    "MakeDefectStructureInfo",
    "MakeDefectVestaFile",
]
