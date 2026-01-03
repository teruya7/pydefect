# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for defect analysis operations.

This module provides functions for defect structure analysis,
defect energy calculations, and visualization.
"""

from typing import List, Optional

from pymatgen.core import Structure

from pydefect.analysis.calculation.models import CalcResults
from pydefect.analysis.corrections.models import Correction, NoCorrection
from pydefect.analysis.formation_energy.models import FormationEnergyInfo
from pydefect.analysis.formation_energy.plotter import FormationEnergyMplPlotter
from pydefect.analysis.formation_energy.calculation import (
    calculate_formation_energy_info as _make_defect_energy_info,
    calculate_formation_energy_summary as _make_defect_energy_summary,
)
from pydefect.analysis.structure.models import DefectStructureInfo
from pydefect.analysis.structure.analyzer import MakeDefectStructureInfo
from pydefect.analysis.structure.vesta import MakeDefectVestaFile
from pydefect.analysis.chemical_potential.models import (
    StandardEnergies,
    TargetVertices,
)
from pydefect.analysis.unitcell.models import Unitcell
from pydefect.defaults import defaults
from pydefect.preparation.defect.models.entry import DefectEntry


# Backward compatibility alias
DefectEnergyMplPlotter = FormationEnergyMplPlotter


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


def make_defect_vesta_file(
    defect_structure_info: DefectStructureInfo,
    cutoff: float = defaults.show_structure_cutoff,
    min_displace_w_arrows: float = 0.1,
    arrow_factor: float = 3.0,
    title: Optional[str] = None,
) -> MakeDefectVestaFile:
    """Create VESTA visualization files for defect structures.

    Args:
        defect_structure_info: DefectStructureInfo object.
        cutoff: Cutoff distance for showing atoms around defect.
        min_displace_w_arrows: Minimum displacement to show arrows.
        arrow_factor: Scaling factor for displacement arrows.
        title: Title for the VESTA file.

    Returns:
        MakeDefectVestaFile object with initial_vesta and final_vesta attributes.

    Example:
        >>> from pydefect import api
        >>> from monty.serialization import loadfn
        >>> dsi = loadfn("defect_structure_info.json")
        >>> vesta = api.make_defect_vesta_file(dsi, title="Va_O1")
        >>> vesta.initial_vesta.write_file("initial.vesta")
        >>> vesta.final_vesta.write_file("final.vesta")
    """
    return MakeDefectVestaFile(
        defect_structure_info=defect_structure_info,
        cutoff=cutoff,
        min_displace_w_arrows=min_displace_w_arrows,
        arrow_factor=arrow_factor,
        title=title,
    )


def make_defect_energy_info(
    defect_entry: DefectEntry,
    calc_results: CalcResults,
    perfect_calc_results: CalcResults,
    standard_energies: StandardEnergies,
    unitcell: Unitcell,
    correction: Optional[Correction] = None,
    band_edge_states=None,
) -> FormationEnergyInfo:
    """Calculate defect energy information.

    Args:
        defect_entry: DefectEntry object for the defect.
        calc_results: CalcResults from defect calculation.
        perfect_calc_results: CalcResults from perfect supercell.
        standard_energies: StandardEnergies for element references.
        unitcell: Unitcell object with band edge information.
        correction: Correction object (e.g., EfnvCorrection).
            If None, NoCorrection is applied.
        band_edge_states: Optional band edge states information.

    Returns:
        DefectEnergyInfo object.

    Example:
        >>> from pydefect import api
        >>> energy_info = api.make_defect_energy_info(
        ...     defect_entry, calc_results, perfect_calc_results,
        ...     std_energies, unitcell, correction=efnv_correction
        ... )
        >>> energy_info.to_yaml_file()
    """
    if correction is None:
        correction = NoCorrection()

    return _make_defect_energy_info(
        defect_entry=defect_entry,
        calc_results=calc_results,
        correction=correction,
        perfect_calc_results=perfect_calc_results,
        standard_energies=standard_energies,
        unitcell=unitcell,
        band_edge_states=band_edge_states,
    )


def make_defect_energy_summary(
    energy_infos: List[FormationEnergyInfo],
    target_vertices: TargetVertices,
    unitcell: Unitcell,
    perfect_band_edge_state=None,
):
    """Create a defect energy summary from multiple defect energy infos.

    Args:
        energy_infos: List of DefectEnergyInfo objects.
        target_vertices: TargetVertices specifying chemical potential vertices.
        unitcell: Unitcell object.
        perfect_band_edge_state: Optional perfect band edge state.

    Returns:
        DefectEnergySummary object.

    Example:
        >>> from pydefect import api
        >>> summary = api.make_defect_energy_summary(
        ...     energy_infos, target_vertices, unitcell
        ... )
        >>> summary.to_json_file()
    """
    return _make_defect_energy_summary(
        energy_infos, target_vertices, unitcell, perfect_band_edge_state
    )


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
