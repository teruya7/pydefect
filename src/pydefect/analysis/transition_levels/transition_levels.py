# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
"""Calculate transition levels from cross point data."""

from typing import Dict

from pydefect.analysis.formation_energy.models import CrossPoints
from pydefect.analysis.transition_levels.models import (
    TransitionLevel, TransitionLevels,
)


def calculate_transition_levels(cross_point_dicts: Dict[str, CrossPoints],
                                 cbm: float,
                                 supercell_vbm: float,
                                 supercell_cbm: float) -> TransitionLevels:
    """Create TransitionLevels from cross point data.

    Args:
        cross_point_dicts: Dict mapping defect name to CrossPoints.
        cbm: Conduction band minimum (eV from VBM).
        supercell_vbm: Supercell VBM energy.
        supercell_cbm: Supercell CBM energy.

    Returns:
        TransitionLevels object with all transition data.

    Example:
        >>> from pydefect.analysis.transition_levels import calculate_transition_levels
        >>> tls = calculate_transition_levels(cross_points, cbm=3.0, ...)
        >>> tls.to_json_file()
    """
    transition_levels = []
    for defect_name, cross_point in cross_point_dicts.items():
        charges = [list(charge_pair) for charge_pair in cross_point.charge_list[1:-1]]
        if cross_point.inner_cross_points:
            energies = cross_point.t_inner_cross_points[1]
            fermi_levels = cross_point.t_inner_cross_points[0]
        else:
            energies, fermi_levels = [], []
        transition_levels.append(
            TransitionLevel(defect_name, charges, energies, fermi_levels))

    return TransitionLevels(
        transition_levels, cbm, supercell_vbm, supercell_cbm)


# Backward compatibility alias
make_transition_levels = calculate_transition_levels
