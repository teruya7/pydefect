# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for defect analysis and visualization.

This module provides functions for analyzing defect structures,
band edge states, and plotting defect energies.
"""

from typing import List, Optional

from pymatgen.core import Structure
from pymatgen.io.vasp import Vasprun, Outcar, Procar

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
from pydefect.analyzer.unitcell.unitcell import Unitcell
from pydefect.analyzer.unitcell.make_unitcell import make_unitcell_from_vasp as _make_unitcell
from pydefect.analyzer.calculation.make_calc_results import make_calc_results_from_vasp as _make_calc_results
from pydefect.analyzer.band_edge.make_perfect_band_edge_state import (
    make_perfect_band_edge_state_from_vasp as _make_perfect_band_edge_state,
)
from pydefect.analyzer.band_edge.make_band_edge_orbital_infos import (
    make_band_edge_orbital_infos as _make_band_edge_orbital_infos,
)
from pydefect.preparation.defect.defect_entry import DefectEntry
from pydefect.preparation.supercell.supercell_info import SupercellInfo


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


def make_unitcell_from_vasp(
    vasprun_band: Vasprun,
    outcar_band: Outcar,
    outcar_dielectric_clamped: Optional[Outcar] = None,
    outcar_dielectric_ionic: Optional[Outcar] = None,
    system_name: Optional[str] = None,
) -> Unitcell:
    """Create Unitcell object from VASP outputs.

    Args:
        vasprun_band: Vasprun from band structure calculation.
        outcar_band: Outcar from band structure calculation.
        outcar_dielectric_clamped: Outcar with clamped-ion dielectric tensor.
        outcar_dielectric_ionic: Outcar with ionic dielectric contribution.
        system_name: Optional name for the system.

    Returns:
        Unitcell object containing band edges and dielectric properties.

    Example:
        >>> from pydefect import api
        >>> from pymatgen.io.vasp import Vasprun, Outcar
        >>> unitcell = api.make_unitcell_from_vasp(
        ...     Vasprun("band/vasprun.xml"),
        ...     Outcar("band/OUTCAR"),
        ...     Outcar("dielectric/OUTCAR"),
        ... )
        >>> unitcell.to_yaml_file()
    """
    return _make_unitcell(
        vasprun_band=vasprun_band,
        outcar_band=outcar_band,
        outcar_dielectric_clamped=outcar_dielectric_clamped,
        outcar_dielectric_ionic=outcar_dielectric_ionic,
        system_name=system_name,
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


def make_perfect_band_edge_state(
    procar: Procar,
    vasprun: Vasprun,
    outcar: Outcar,
):
    """Create PerfectBandEdgeState from VASP outputs.

    Args:
        procar: Procar object from perfect supercell.
        vasprun: Vasprun object from perfect supercell.
        outcar: Outcar object from perfect supercell.

    Returns:
        PerfectBandEdgeState object.

    Example:
        >>> from pydefect import api
        >>> p_state = api.make_perfect_band_edge_state(procar, vasprun, outcar)
        >>> p_state.to_json_file()
    """
    return _make_perfect_band_edge_state(procar, vasprun, outcar)


def make_band_edge_orbital_infos(
    procar: Procar,
    vasprun: Vasprun,
    supercell_vbm: float,
    supercell_cbm: float,
    defect_structure_info=None,
    eigval_shift: float = 0.0,
):
    """Create BandEdgeOrbitalInfos from VASP outputs.

    Args:
        procar: Procar object.
        vasprun: Vasprun object.
        supercell_vbm: VBM energy of supercell.
        supercell_cbm: CBM energy of supercell.
        defect_structure_info: Optional DefectStructureInfo.
        eigval_shift: Energy shift for eigenvalues.

    Returns:
        BandEdgeOrbitalInfos object.

    Example:
        >>> from pydefect import api
        >>> orb_infos = api.make_band_edge_orbital_infos(
        ...     procar, vasprun, vbm, cbm
        ... )
        >>> orb_infos.to_json_file()
    """
    return _make_band_edge_orbital_infos(
        procar, vasprun, supercell_vbm, supercell_cbm,
        defect_structure_info, eigval_shift=eigval_shift,
    )

