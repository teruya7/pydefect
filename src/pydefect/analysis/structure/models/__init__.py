# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Defect structure models - data classes for defect structure analysis."""

from pydefect.analysis.structure.models.site_diff import (
    SiteDiff,
    SiteInfo,
)
from pydefect.analysis.structure.models.displacement import (
    Displacement,
)
from pydefect.analysis.structure.models.defect_type import (
    DefectType,
    SymmRelation,
    determine_defect_type,
    symmetry_relation,
    unique_point_group,
    remove_dot,
    # Backward compatibility alias
    judge_defect_type,
)
from pydefect.analysis.structure.models.structure_info import (
    DefectStructureInfo,
)

__all__ = [
    "SiteDiff",
    "SiteInfo",
    "Displacement",
    "DefectType",
    "SymmRelation",
    "determine_defect_type",
    "symmetry_relation",
    "unique_point_group",
    "remove_dot",
    "judge_defect_type",
    "DefectStructureInfo",
]
