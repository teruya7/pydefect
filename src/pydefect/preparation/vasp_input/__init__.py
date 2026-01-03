# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Charge-related makers for defect calculations.

This module provides functions for calculating charge-related properties:

- calculate_charge_state: Determine charge state from VASP inputs
- calculate_charge_localization: Analyze charge localization from PARCHG
"""
from pydefect.preparation.vasp_input.charge_state import (
    calculate_charge_state,
    # Backward compatibility
    get_defect_charge_state,
)
from pydefect.analysis.localization.localization import (
    calculate_charge_localization,
    calculate_radial_distribution,
    find_periodic_center,
    # Backward compatibility
    make_defect_charge_info,
    make_charge_dist,
    center_1d_periodic_quantity,
)
