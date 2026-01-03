# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""CLI commands for Materials Project integration.

Commands for querying Materials Project and creating competing phases.

Example:
    $ pydefect mp -e Mg Al O --e_above_hull 0.0005
"""

from pathlib import Path
from typing import List, Optional

import typer
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect.defaults import defaults

logger = get_logger(__name__)


@app.command(name="mp", help="Get competing phases from Materials Project.")
def mp(
    elements: List[str] = typer.Option(
        ..., "-e", "--elements",
        help="Element symbols, e.g., Mg Al O."
    ),
    e_above_hull: float = typer.Option(
        defaults.e_above_hull, "--e_above_hull",
        help="Energy above hull threshold in eV/atom."
    ),
):
    """Query Materials Project for competing phases and create POSCARs."""
    from pydefect.api.materials_project import MpQuery, make_poscars_from_query

    query = MpQuery(elements, e_above_hull=e_above_hull)
    make_poscars_from_query(query.materials, Path("."))
    typer.echo(f"Created directories for {len(query.materials)} materials.")


@app.command(name="mce", help="Make composition energies from MP.")
def mce(
    elements: List[str] = typer.Option(
        ..., "-e", "--elements",
        help="Element symbols to query."
    ),
    atom_energy_yaml: Optional[Path] = typer.Option(
        None, "-a", "--atom_energy_yaml",
        help="Path to atom energy YAML for energy alignment."
    ),
):
    """Fetch composition energies from Materials Project."""
    from pydefect.api.materials_project import make_composition_energies_from_mp

    comp_energies = make_composition_energies_from_mp(
        elements=list(elements),
        atom_energy_yaml=str(atom_energy_yaml) if atom_energy_yaml else None,
    )
    comp_energies.to_yaml_file()
    typer.echo("Created composition_energies.yaml")
