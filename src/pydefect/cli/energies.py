# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Energy-related Typer commands.

Commands for chemical potential diagrams and defect energy calculations.

Example:
    $ pydefect standard_and_relative_energies
    $ pydefect cpd_and_vertices -t MgO
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api
from pydefect.analyzer.unitcell import Unitcell
from pydefect.analyzer.defect_energy import DefectEnergyInfo
from pydefect.analyzer.chem_pot_diag.chem_pot_diag import (
    CompositionEnergies, RelativeEnergies, StandardEnergies, TargetVertices
)
from pydefect.analyzer.corrections.no_correction import NoCorrection

logger = get_logger(__name__)


@app.command(name="standard_and_relative_energies",
             help="Calculate standard and relative energies.")
def standard_and_relative_energies(
    composition_energies_yaml: Path = typer.Option(
        "composition_energies.yaml", "-y", "--composition_energies_yaml",
        help="composition_energies.yaml file."
    ),
):
    """Calculate standard and relative energies from composition energies."""
    from pymatgen.analysis.phase_diagram import PDPlotter
    from matplotlib import pyplot as plt

    # Load file (CLI responsibility)
    comp_energies = CompositionEnergies.from_yaml(str(composition_energies_yaml))

    # Call API (pure logic)
    std_energies, rel_energies = api.make_standard_and_relative_energies(comp_energies)

    # Write output (CLI responsibility)
    std_energies.to_yaml_file()
    rel_energies.to_yaml_file()
    typer.echo("Created standard_energies.yaml and relative_energies.yaml")

    try:
        pd = comp_energies.to_phase_diagram()
        plotter = PDPlotter(pd, backend="matplotlib", show_unstable=float("inf"))
        plotter.get_plot(plt=plt)
        plt.savefig("convex_hull.pdf")
        typer.echo("Created convex_hull.pdf")
    except Exception:
        pass

    if rel_energies.unstable_compounds:
        logger.info("The unstable compound information is shown below.")
        typer.echo(rel_energies.unstable_comp_info)


@app.command(name="cpd_and_vertices",
             help="Make chemical potential diagram and vertices.")
def cpd_and_vertices(
    rel_energy_yaml: Path = typer.Option(
        "relative_energies.yaml", "-y", "--rel_energy_yaml",
        help="relative_energies.yaml file."
    ),
    target: Optional[str] = typer.Option(
        None, "-t", "--target",
        help="Target composition, e.g., MgO."
    ),
    elements: Optional[List[str]] = typer.Option(
        None, "-e", "--elements",
        help="Element names for diagram."
    ),
):
    """Make chemical potential diagram."""
    # Load file (CLI responsibility)
    rel_energies = RelativeEnergies.from_yaml(str(rel_energy_yaml))

    # Call API (pure logic)
    cpd = api.make_chem_pot_diag(rel_energies, target=target, elements=elements)

    # Write output (CLI responsibility)
    cpd.to_json_file()
    typer.echo("Created chem_pot_diag.json")

    if target:
        cpd.to_target_vertices.to_yaml_file()
        typer.echo("Created target_vertices.yaml")


@app.command(name="plot_cpd", help="Plot chemical potential diagram.")
def plot_cpd(
    chem_pot_diag_path: Path = typer.Option(
        "chem_pot_diag.json", "-cpd", "--chem_pot_diag",
        help="chem_pot_diag.json file."
    ),
):
    """Plot chemical potential diagram as PDF."""
    from pydefect.analyzer.chem_pot_diag.chem_pot_diag import change_element_sequence
    from pydefect.analyzer.chem_pot_diag.cpd_plotter import (
        ChemPotDiag2DMplPlotter, ChemPotDiag3DMplPlotter
    )

    # Load file (CLI responsibility)
    cpd = loadfn(str(chem_pot_diag_path))
    cpd = change_element_sequence(cpd)

    # Plot (CLI responsibility - no API call needed for plotting)
    if cpd.dim == 2:
        plotter = ChemPotDiag2DMplPlotter(cpd)
    elif cpd.dim == 3:
        plotter = ChemPotDiag3DMplPlotter(cpd)
    else:
        typer.echo(f"Only 2 or 3 dimensions supported. Got {cpd.dim}.", err=True)
        raise typer.Exit(1)

    plt = plotter.draw_diagram()
    plt.savefig(fname="cpd.pdf")
    typer.echo("Created cpd.pdf")
    plt.show()


@app.command(name="defect_energy_infos", help="Calculate defect energy infos.")
def defect_energy_infos(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect calculations."
    ),
    unitcell: Path = typer.Option(
        ..., "-u", "--unitcell",
        help="Path to unitcell.yaml."
    ),
    perfect_calc_results: Path = typer.Option(
        ..., "-pcr", "--perfect_calc_results",
        help="Path to perfect calc_results.json."
    ),
    std_energies: Path = typer.Option(
        ..., "-s", "--std_energies",
        help="Path to standard_energies.yaml."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Calculate defect energy information for multiple directories."""
    # Load shared files (CLI responsibility)
    unitcell_obj = Unitcell.from_yaml(str(unitcell))
    pcr = loadfn(str(perfect_calc_results))
    std_energies_obj = StandardEnergies.from_yaml(str(std_energies))
    file_name = "defect_energy_info.yaml"

    for _dir in dirs:
        try:
            # Load per-directory files (CLI responsibility)
            calc_results = loadfn(_dir / "calc_results.json")
            defect_entry = loadfn(_dir / "defect_entry.json")
            try:
                correction = loadfn(_dir / "correction.json")
            except FileNotFoundError:
                logger.warning(f"  {_dir}: No correction.json, applying no correction.")
                correction = NoCorrection()
            try:
                band_edge_states = loadfn(_dir / "band_edge_states.json")
            except FileNotFoundError:
                band_edge_states = None

            # Call API (pure logic)
            energy_info = api.make_defect_energy_info(
                defect_entry=defect_entry,
                calc_results=calc_results,
                perfect_calc_results=pcr,
                standard_energies=std_energies_obj,
                unitcell=unitcell_obj,
                correction=correction,
                band_edge_states=band_edge_states,
            )

            # Write output (CLI responsibility)
            energy_info.to_yaml_file(str(_dir / file_name))
            typer.echo(f"  {_dir}: Created {file_name}")

        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


@app.command(name="defect_energy_summary", help="Create defect energy summary.")
def defect_energy_summary(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect_energy_info.yaml."
    ),
    unitcell: Path = typer.Option(
        ..., "-u", "--unitcell",
        help="Path to unitcell.yaml."
    ),
    p_state: Path = typer.Option(
        ..., "-pbes", "--p_state",
        help="Path to perfect_band_edge_state.json."
    ),
    target_vertices_yaml: Path = typer.Option(
        ..., "-t", "--target_vertices_yaml",
        help="Path to target_vertices.yaml."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Create defect energy summary from multiple defect calculations."""
    # Load shared files (CLI responsibility)
    unitcell_obj = Unitcell.from_yaml(str(unitcell))
    p_state_obj = loadfn(str(p_state))
    target_vertices = TargetVertices.from_yaml(str(target_vertices_yaml))
    energy_infos = []

    for _dir in dirs:
        try:
            # Load per-directory files (CLI responsibility)
            energy_info = DefectEnergyInfo.from_yaml(str(_dir / "defect_energy_info.yaml"))
            energy_infos.append(energy_info)
        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    # Call API (pure logic)
    summary = api.make_defect_energy_summary(energy_infos, target_vertices, unitcell_obj, p_state_obj)

    # Write output (CLI responsibility)
    summary.to_json_file()
    typer.echo("Created defect_energy_summary.json")


@app.command(name="plot_defect_formation_energy",
             help="Plot defect formation energies.")
def plot_defect_formation_energy(
    defect_energy_summary_path: Path = typer.Option(
        ..., "-d", "--defect_energy_summary",
        help="defect_energy_summary.json file."
    ),
    label: str = typer.Option(
        ..., "-l", "--label",
        help="Chemical potential vertex label."
    ),
    y_range: Optional[List[float]] = typer.Option(
        None, "-y", "--y_range",
        help="Y-axis energy range (min max)."
    ),
    allow_shallow: bool = typer.Option(
        False, "--allow_shallow",
        help="Show shallow defects."
    ),
    no_corrections: bool = typer.Option(
        False, "--no_corrections",
        help="Disable corrections in plot."
    ),
    no_label_line: bool = typer.Option(
        False, "--no_label_line",
        help="Don't place labels on lines."
    ),
    no_add_charges: bool = typer.Option(
        False, "--no_add_charges",
        help="Don't show charges."
    ),
    plot_all_energies: bool = typer.Option(
        False, "--plot_all_energies",
        help="Plot all charge states."
    ),
):
    """Plot defect formation energies as a function of Fermi level."""
    # Load file (CLI responsibility)
    summary = loadfn(str(defect_energy_summary_path))

    # Call API (pure logic + plotting)
    api.plot_defect_energy(
        defect_energy_summary=summary,
        chem_pot_label=label,
        y_range=list(y_range) if y_range else None,
        allow_shallow=allow_shallow,
        with_corrections=not no_corrections,
        label_line=not no_label_line,
        add_charges=not no_add_charges,
        plot_all_energies=plot_all_energies,
        save_path=f"energy_{label}.pdf",
    )
    typer.echo(f"Created energy_{label}.pdf")
