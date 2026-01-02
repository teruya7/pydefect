# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Chemical potential related CLI commands."""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api
from pydefect.analyzer.chemical_potential.chem_pot_diag import (
    CompositionEnergies, RelativeEnergies
)

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
    # Load file (CLI responsibility)
    comp_energies = CompositionEnergies.from_yaml(str(composition_energies_yaml))

    # Call API (pure logic)
    std_energies, rel_energies = api.make_standard_and_relative_energies(comp_energies)

    # Write output (CLI responsibility)
    std_energies.to_yaml_file()
    rel_energies.to_yaml_file()
    typer.echo("Created standard_energies.yaml and relative_energies.yaml")


@app.command(name="cpd_and_vertices", help="Make chemical potential diagram.")
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
    logger.info("--- Check target_vertices.yaml, chemical potential vertices, for the target material.")
    cpd.target_vertices.to_yaml_file()
    typer.echo("Created chem_pot_diag.json and target_vertices.yaml")


@app.command(name="plot_cpd", help="Plot chemical potential diagram.")
def plot_cpd(
    chem_pot_diag_path: Path = typer.Option(
        "chem_pot_diag.json", "-cpd", "--chem_pot_diag",
        help="chem_pot_diag.json file."
    ),
):
    """Plot chemical potential diagram as PDF."""
    from pydefect.analyzer.chemical_potential.chem_pot_diag import (
        ChemPotDiag, ChemPotDiagMplPlotter
    )

    # Load file (CLI responsibility)
    cpd = ChemPotDiag.from_json(str(chem_pot_diag_path))

    # Plot and save (CLI responsibility)
    plotter = ChemPotDiagMplPlotter(cpd)
    plotter.construct_plot()
    plotter.plt.savefig("cpd.pdf")
    typer.echo("Created cpd.pdf")
