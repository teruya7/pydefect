# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Defect type and symmetry relation enumerations."""

from monty.json import MSONable
from vise.util.enum import ExtendedEnum
from pymatgen.symmetry.groups import SpaceGroup


class DefectType(MSONable, ExtendedEnum):
    """Enumeration of defect types.

    Attributes:
        vacancy: Single atom removed.
        interstitial: Single atom added.
        substituted: One atom replaced by another.
        vacancy_split: Multiple vacancies of same element.
        interstitial_split: Multiple interstitials of same element.
        unknown: Complex or unrecognized defect.
    """
    vacancy = "vacancy"
    interstitial = "interstitial"
    substituted = "substituted"
    vacancy_split = "vacancy_split"
    interstitial_split = "interstitial_split"
    unknown = "unknown"


class SymmRelation(MSONable, ExtendedEnum):
    """Symmetry relation between initial and final defect structures."""
    same = "same"
    subgroup = "subgroup"
    supergroup = "supergroup"
    another = "another"


def determine_defect_type(site_diff):
    """Determine defect type from site difference analysis.

    Args:
        site_diff: SiteDiff object from structure comparison.

    Returns:
        DefectType enum value.
    """
    if site_diff.is_vacancy:
        return DefectType.vacancy
    elif site_diff.is_interstitial:
        return DefectType.interstitial
    elif site_diff.is_substituted:
        return DefectType.substituted

    elements_involved = set()
    for _, elem, _ in site_diff.removed + site_diff.inserted:
        elements_involved.add(elem)

    if len(elements_involved) == 1 and not site_diff.removed_by_sub:
        if len(site_diff.removed) - len(site_diff.inserted) == 1:
            return DefectType.vacancy_split
        elif len(site_diff.removed) - len(site_diff.inserted) == -1:
            return DefectType.interstitial_split

    return DefectType.unknown


def remove_dot(point_group_symbol):
    """Remove dots from point group symbol."""
    return "".join([char for char in point_group_symbol if char != "."])


def unique_point_group(pg):
    """Normalize point group to unique representation."""
    result = remove_dot(pg)
    if result == "2mm" or result == "m2m":
        return "mm2"
    if result == "-4m2":
        return "-42m"
    if result == "m3":
        return "m-3"
    return result


def symmetry_relation(initial_point_group, final_point_group):
    """Check the point group symmetry relation.

    Args:
        initial_point_group: Initial site point group.
        final_point_group: Final site point group.

    Returns:
        SymmRelation enum value.
    """
    if initial_point_group in ["3m", "-3m"]:
        initial_point_group += "1"
    if final_point_group in ["3m", "-3m"]:
        final_point_group += "1"

    initial = SpaceGroup(f"P{initial_point_group}")
    final = SpaceGroup(f"P{final_point_group}")
    if initial == final:
        return SymmRelation.same
    elif final.is_subgroup(initial):
        return SymmRelation.subgroup
    elif final.is_supergroup(initial):
        return SymmRelation.supergroup
    else:
        return SymmRelation.another


# Backward compatibility aliases
judge_defect_type = determine_defect_type
