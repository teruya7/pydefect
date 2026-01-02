# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Utility Typer commands.

Commands for printing JSON/YAML files and creating VESTA files.

Example:
    $ pydefect util print calc_results.json
    $ pydefect util defect_vesta -d Va_O1_0
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app, util_app
from pydefect import api

logger = get_logger(__name__)


@util_app.command(name="print", help="Print JSON/YAML file contents.")
def print_json(
    files: List[Path] = typer.Argument(
        ...,
        help="JSON or YAML files to print."
    ),
    use_repr: bool = typer.Option(
        False, "--repr", "-r",
        help="Use __repr__ instead of __str__."
    ),
):
    """Print contents of JSON/YAML files."""
    for filename in files:
        typer.echo("-" * 80)
        typer.echo(f"file: {filename}")
        # Use API layer
        content = api.print_json(str(filename), use_repr=use_repr)
        typer.echo(content)


@util_app.command(name="defect_vesta", help="Create VESTA files for defect visualization.")
def defect_vesta(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect_structure_info.json."
    ),
    cutoff: float = typer.Option(
        5.0, "-c", "--cutoff",
        help="Cutoff distance for showing atoms."
    ),
    min_displace: float = typer.Option(
        0.1, "--min_displace",
        help="Minimum displacement to show arrows."
    ),
    arrow_factor: float = typer.Option(
        3.0, "--arrow_factor",
        help="Scaling factor for arrows."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Create VESTA visualization files for defect structures."""
    for _dir in dirs:
        try:
            # Load file (CLI responsibility)
            dsi = loadfn(_dir / "defect_structure_info.json")
            defect_entry = loadfn(_dir / "defect_entry.json")
            title = defect_entry.name

            # Call API (pure logic)
            vesta = api.make_defect_vesta_file(
                defect_structure_info=dsi,
                cutoff=cutoff,
                min_displace_w_arrows=min_displace,
                arrow_factor=arrow_factor,
                title=title,
            )

            # Write output (CLI responsibility)
            vesta.initial_vesta.write_file(str(_dir / "initial.vesta"))
            vesta.final_vesta.write_file(str(_dir / "final.vesta"))
            typer.echo(f"  {_dir}: Created initial.vesta and final.vesta")

        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")
