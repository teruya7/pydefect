# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for defect correction calculations.

This module provides functions for calculating electrostatic corrections
including extended FNV (eFNV) and GKFO corrections.
"""

from typing import List, Optional

from pydefect.analysis.calculation.calc_results import CalcResults
from pydefect.analysis.unitcell.unitcell import Unitcell
from pydefect.analysis.corrections.make_efnv_correction import (
    make_efnv_correction as _make_efnv_correction,
)
from pydefect.analysis.corrections.make_gkfo_correction import (
    make_gkfo_correction as _make_gkfo_correction,
)
from pydefect.analysis.corrections.efnv_correction import ExtendedFnvCorrection
from pydefect.analysis.corrections.gkfo_correction import GkfoCorrection


def make_efnv_correction(
    charge: int,
    calc_results: CalcResults,
    perfect_calc_results: CalcResults,
    dielectric_tensor: List[List[float]],
    defect_region_radius: Optional[float] = None,
    calc_all_sites: bool = False,
) -> ExtendedFnvCorrection:
    """Calculate extended FNV (Freysoldt-Neugebauer-Van de Walle) correction.

    Args:
        charge: Defect charge state.
        calc_results: CalcResults from defect calculation.
        perfect_calc_results: CalcResults from perfect supercell.
        dielectric_tensor: 3x3 dielectric tensor.
        defect_region_radius: Radius for defect region in Angstroms.
            If None, automatically determined.
        calc_all_sites: If True, calculate correction for all sites.

    Returns:
        ExtendedFnvCorrection object containing correction energy and details.

    Example:
        >>> from pydefect import api
        >>> efnv = api.make_efnv_correction(
        ...     charge=-2,
        ...     calc_results=defect_calc_results,
        ...     perfect_calc_results=perfect_calc_results,
        ...     dielectric_tensor=unitcell.dielectric_constant,
        ... )
        >>> print(f"Correction energy: {efnv.correction_energy} eV")
        >>> efnv.to_json_file()
    """
    return _make_efnv_correction(
        charge=charge,
        calc_results=calc_results,
        perfect_calc_results=perfect_calc_results,
        dielectric_tensor=dielectric_tensor,
        defect_region_radius=defect_region_radius,
        calc_all_sites=calc_all_sites,
    )


def make_gkfo_correction(
    initial_efnv_correction: ExtendedFnvCorrection,
    initial_calc_results: CalcResults,
    final_calc_results: CalcResults,
    charge_diff: int,
    unitcell: Unitcell,
) -> GkfoCorrection:
    """Calculate GKFO (Gallino-Kresse-Fabris-Orlando) correction.

    This correction is used for charge state transitions (e.g., optical
    transitions) where the initial and final charge states differ.

    Args:
        initial_efnv_correction: eFNV correction for initial state.
        initial_calc_results: CalcResults from initial state.
        final_calc_results: CalcResults from final state.
        charge_diff: Charge difference between final and initial states.
            Example: if final charge is +3 and initial is +2, charge_diff = +1.
        unitcell: Unitcell object containing dielectric information.

    Returns:
        GkfoCorrection object.

    Example:
        >>> from pydefect import api
        >>> gkfo = api.make_gkfo_correction(
        ...     initial_efnv_correction=efnv,
        ...     initial_calc_results=initial_calc,
        ...     final_calc_results=final_calc,
        ...     charge_diff=1,
        ...     unitcell=unitcell,
        ... )
        >>> gkfo.to_json_file()
    """
    return _make_gkfo_correction(
        initial_efnv_correction=initial_efnv_correction,
        initial_calc_results=initial_calc_results,
        final_calc_results=final_calc_results,
        charge_diff=charge_diff,
        unitcell=unitcell,
    )
