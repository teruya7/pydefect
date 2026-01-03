# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Charge localization analysis module.

This module provides data models for analyzing charge localization:

- ChargeLocalizationInfo: Analyze charge distribution around defects
- RadialChargeDist: Radial charge density distribution data

For creating these objects from VASP outputs, use:
- pydefect.preparation.vasp_input.calculate_charge_localization
- pydefect.preparation.vasp_input.calculate_charge_state
"""
from pydefect.analysis.localization.models import (
    ChargeLocalizationInfo,
    RadialChargeDist,
    # Backward compatibility
    DefectChargeInfo,
    AveChargeDensityDist,
)
