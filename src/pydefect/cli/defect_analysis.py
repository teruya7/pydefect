# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""CLI commands for defect analysis.

Commands for defect structure analysis and energy calculations.

Example:
    $ pydefect defect_structure_info -d Va_O1_0
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api

logger = get_logger(__name__)


@app.command(name="dsi", help="Analyze defect structure.")
def defect_structure_info(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect calculations."
    ),
    supercell_info_path: Path = typer.Option(
        "supercell_info.json", "-s", "--supercell_info",
        help="Path to supercell_info.json."
    ),
    dist_tolerance: float = typer.Option(
        1.0, "-dt", "--dist_tolerance",
        help="Distance tolerance in Angstrom."
    ),
    symprec: float = typer.Option(
        0.1, "--symprec",
        help="Symmetry precision for spglib."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Analyze defect structure to get displacement and symmetry info."""
    supercell_info = loadfn(str(supercell_info_path))
    file_name = "defect_structure_info.json"

    for _dir in dirs:
        try:
            # Load files (CLI responsibility)
            calc_results = loadfn(_dir / "calc_results.json")
            defect_entry = loadfn(_dir / "defect_entry.json")

            # Call API (pure logic)
            info = api.make_defect_structure_info(
                perfect_structure=supercell_info.structure,
                initial_defect_structure=defect_entry.structure,
                final_defect_structure=calc_results.structure,
                dist_tol=dist_tolerance,
                symprec=symprec,
            )

            # Write output (CLI responsibility)
            info.to_json_file(str(_dir / file_name))
            typer.echo(f"  {_dir}: Created {file_name}")

        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


@app.command(name="dei", help="Calculate defect energy information.")
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
    from pydefect.analysis.chemical_potential.models import StandardEnergies
    from pydefect.analysis.corrections.models import NoCorrection

    # Load common files (CLI responsibility)
    unitcell_obj = loadfn(str(unitcell))
    pcr = loadfn(str(perfect_calc_results))
    std = StandardEnergies.from_yaml(str(std_energies))
    file_name = "defect_energy_info.yaml"

    for _dir in dirs:
        try:
            # Load files (CLI responsibility)
            calc_results = loadfn(_dir / "calc_results.json")
            defect_entry = loadfn(_dir / "defect_entry.json")

            try:
                correction = loadfn(_dir / "correction.json")
            except FileNotFoundError:
                correction = NoCorrection()

            # Call API (pure logic)
            info = api.make_defect_energy_info(
                defect_entry=defect_entry,
                calc_results=calc_results,
                correction=correction,
                perfect_calc_results=pcr,
                unitcell=unitcell_obj,
                standard_energies=std,
            )

            # Write output (CLI responsibility)
            info.to_yaml_file(str(_dir / file_name))
            typer.echo(f"  {_dir}: Created {file_name}")

        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


@app.command(name="des", help="Create defect energy summary.")
def defect_energy_summary(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect_energy_info.yaml."
    ),
    unitcell: Path = typer.Option(
        ..., "-u", "--unitcell",
        help="Path to unitcell.yaml."
    ),
    perfect_calc_results: Path = typer.Option(
        ..., "-pcr", "--perfect_calc_results",
        help="Path to perfect calc_results.json."
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
    from pydefect.analysis.chemical_potential.models import TargetVertices

    # Load common files (CLI responsibility)
    unitcell_obj = loadfn(str(unitcell))
    pcr = loadfn(str(perfect_calc_results))
    target_vertices = TargetVertices.from_yaml(str(target_vertices_yaml))
    infos = []

    for _dir in dirs:
        try:
            # Load files (CLI responsibility)
            energy_info = loadfn(_dir / "defect_energy_info.yaml")
            str_info = loadfn(_dir / "defect_structure_info.json")
            infos.append((energy_info, str_info))
        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    # Call API (pure logic)
    summary = api.make_defect_energy_summary(
        defect_energy_infos=infos,
        target_vertices=target_vertices,
        unitcell=unitcell_obj,
        perfect_calc_results=pcr,
    )

    # Write output (CLI responsibility)
    summary.to_json_file()
    typer.echo("Created defect_energy_summary.json")


@app.command(name="pe", help="Plot defect formation energy.")
def plot_defect_energy(
    defect_energy_summary_path: Path = typer.Option(
        ..., "-d", "--defect_energy_summary",
        help="defect_energy_summary.json file."
    ),
    label: Optional[str] = typer.Option(
        None, "-l", "--label",
        help="Label for this chemical potential condition."
    ),
    y_range: Optional[List[float]] = typer.Option(
        None, "--y_range",
        help="Y-axis range (min max)."
    ),
    filtering_words: Optional[List[str]] = typer.Option(
        None, "--filtering_words",
        help="Words to filter defects."
    ),
    except_filtering_words: Optional[List[str]] = typer.Option(
        None, "--except_filtering_words",
        help="Words to exclude from filter."
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

    # Call API (pure logic)
    api.plot_defect_energy(
        summary,
        label=label,
        y_range=list(y_range) if y_range else None,
        filtering_words=list(filtering_words) if filtering_words else None,
        except_filtering_words=list(except_filtering_words) if except_filtering_words else None,
        add_charges=not no_add_charges,
        plot_all_energies=plot_all_energies,
    )
    typer.echo("Created defect_formation_energy.pdf")
