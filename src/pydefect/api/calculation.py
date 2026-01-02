# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for calculation results."""

from typing import List

from pymatgen.io.vasp import Vasprun, Outcar

from pydefect.analyzer.calculation.calc_results import CalcResults
from pydefect.analyzer.calculation.make_calc_results import (
    make_calc_results_from_vasp as _make_calc_results,
)
from pydefect.analyzer.calculation.make_calc_summary import (
    make_calc_summary as _make_calc_summary,
)


def make_calc_results_from_vasp(
    vasprun: Vasprun,
    outcar: Outcar,
) -> CalcResults:
    """Create CalcResults from VASP outputs.

    Args:
        vasprun: Vasprun object from calculation.
        outcar: Outcar object from calculation.

    Returns:
        CalcResults object containing structure, energy, and convergence info.

    Example:
        >>> from pydefect import api
        >>> calc_results = api.make_calc_results_from_vasp(
        ...     Vasprun("vasprun.xml", parse_potcar_file=False),
        ...     Outcar("OUTCAR"),
        ... )
        >>> calc_results.to_json_file()
    """
    return _make_calc_results(vasprun=vasprun, outcar=outcar)


def make_calc_summary(
    defect_info_list: List[tuple],
    perfect_calc_results: CalcResults,
):
    """Create a calculation summary from multiple defect calculations.

    Args:
        defect_info_list: List of (CalcResults, DefectEntry, DefectStructureInfo) tuples.
        perfect_calc_results: CalcResults from perfect supercell.

    Returns:
        CalcSummary object.

    Example:
        >>> from pydefect import api
        >>> summary = api.make_calc_summary(infos, perfect_calc_results)
        >>> summary.to_json_file()
    """
    return _make_calc_summary(defect_info_list, perfect_calc_results)
