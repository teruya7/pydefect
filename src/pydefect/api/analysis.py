# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for defect analysis and visualization.

This module provides functions for analyzing defect structures,
band edge states, and plotting defect energies.
"""

from typing import List, Optional

from pydefect.analyzer.calculation.calc_results import CalcResults
from pydefect.analyzer.defect_structure.defect_structure_info import DefectStructureInfo
from pydefect.analyzer.defect_structure.make_defect_structure_info import MakeDefectStructureInfo
from pydefect.analyzer.band_edge.make_band_edge_states import (
    make_band_edge_states as _make_band_edge_states,
)
from pydefect.analyzer.calculation.make_calc_summary import (
    make_calc_summary as _make_calc_summary,
)
from pydefect.analyzer.defect_energy.defect_energy_plotter import DefectEnergyMplPlotter
from pydefect.input_maker.defect.defect_entry import DefectEntry
from pydefect.input_maker.supercell.supercell_info import SupercellInfo
from pymatgen.core import Structure


def make_defect_structure_info(
    perfect_structure: Structure,
    initial_defect_structure: Structure,
    final_defect_structure: Structure,
    dist_tol: float = 1.0,
    symprec: float = 0.1,
) -> DefectStructureInfo:
    """Analyze defect structure to get displacement and symmetry information.

    Args:
        perfect_structure: Perfect supercell structure.
        initial_defect_structure: Initial defect structure (before relaxation).
        final_defect_structure: Final defect structure (after relaxation).
        dist_tol: Distance tolerance for structure comparison.
        symprec: Symmetry precision for spglib.

    Returns:
        DefectStructureInfo containing structural analysis results.

    Example:
        >>> from pydefect import api
        >>> info = api.make_defect_structure_info(
        ...     perfect, initial, final
        ... )
        >>> info.to_json_file()
    """
    maker = MakeDefectStructureInfo(
        perfect_structure,
        initial_defect_structure,
        final_defect_structure,
        dist_tol=dist_tol,
        symprec=symprec,
    )
    return maker.defect_structure_info


def make_band_edge_states(
    band_edge_orbital_infos,
    perfect_band_edge_state,
    defect_charge_info=None,
):
    """Determine band edge states from orbital information.

    Args:
        band_edge_orbital_infos: BandEdgeOrbitalInfos object.
        perfect_band_edge_state: PerfectBandEdgeState from perfect calculation.
        defect_charge_info: Optional DefectChargeInfo object.

    Returns:
        BandEdgeStates object.

    Example:
        >>> from pydefect import api
        >>> states = api.make_band_edge_states(orb_infos, p_state)
        >>> states.to_json_file()
    """
    return _make_band_edge_states(
        band_edge_orbital_infos,
        perfect_band_edge_state,
        defect_charge_info,
    )


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


def plot_defect_energy(
    defect_energy_summary,
    chem_pot_label: str,
    y_range: Optional[List[float]] = None,
    allow_shallow: bool = False,
    with_corrections: bool = True,
    label_line: bool = True,
    add_charges: bool = True,
    plot_all_energies: bool = False,
    save_path: Optional[str] = None,
):
    """Plot defect formation energies as a function of Fermi level.

    Args:
        defect_energy_summary: DefectEnergySummary object.
        chem_pot_label: Label for chemical potential vertex (e.g., "A", "B").
        y_range: Y-axis range [min, max] in eV.
        allow_shallow: If True, show shallow defects.
        with_corrections: If True, include corrections in plot.
        label_line: If True, add labels to lines.
        add_charges: If True, add charge state labels.
        plot_all_energies: If True, plot all charge states as thin lines.
        save_path: Path to save the figure. If None, returns the plotter.

    Returns:
        DefectEnergyMplPlotter object (if save_path is None).

    Example:
        >>> from pydefect import api
        >>> api.plot_defect_energy(summary, "A", save_path="energy_A.pdf")
    """
    plotter = DefectEnergyMplPlotter(
        defect_energy_summary=defect_energy_summary,
        chem_pot_label=chem_pot_label,
        y_range=y_range,
        allow_shallow=allow_shallow,
        with_corrections=with_corrections,
        label_line=label_line,
        add_charges=add_charges,
        add_thin_lines=plot_all_energies,
    )
    plotter.construct_plot()

    if save_path:
        plotter.plt.savefig(save_path)
        return None

    return plotter
