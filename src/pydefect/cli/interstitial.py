# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""CLI commands for interstitial site management.

Commands for appending and removing interstitial sites.

Example:
    $ pydefect append_interstitial -p POSCAR -c 0.5 0.5 0.5
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from pymatgen.core import Structure
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api

logger = get_logger(__name__)


@app.command(name="append_interstitial", help="Append interstitial to supercell_info.")
def append_interstitial(
    supercell_info_path: Path = typer.Option(
        "supercell_info.json", "-s", "--supercell_info",
        help="Path to supercell_info.json."
    ),
    base_structure: Path = typer.Option(
        ..., "-p", "--base_structure",
        help="Structure file for fractional coordinates."
    ),
    frac_coords: List[float] = typer.Option(
        ..., "-c", "--frac_coords",
        help="Fractional coordinates (3 values)."
    ),
    info: str = typer.Option(
        "None", "-i", "--info",
        help="Description of interstitial site."
    ),
):
    """Append interstitial site to supercell_info."""
    # Load files (CLI responsibility)
    supercell_info = loadfn(str(supercell_info_path))
    structure = Structure.from_file(str(base_structure))

    # Call API (pure logic)
    result = api.append_interstitial(
        supercell_info=supercell_info,
        base_structure=structure,
        frac_coords=list(frac_coords),
        info=info if info != "None" else None,
    )

    # Write output (CLI responsibility)
    result.to_json_file()
    typer.echo("Updated supercell_info.json")


@app.command(name="pop_interstitial", help="Remove interstitial from supercell_info.")
def pop_interstitial(
    supercell_info_path: Path = typer.Option(
        "supercell_info.json", "-s", "--supercell_info",
        help="Path to supercell_info.json."
    ),
    index: Optional[int] = typer.Option(
        None, "-i", "--index",
        help="Interstitial index to remove (1-based)."
    ),
    pop_all: bool = typer.Option(
        False, "--pop_all",
        help="Remove all interstitials."
    ),
):
    """Remove interstitial site(s) from supercell_info."""
    logger.info("Be careful that the interstitials indices are changed.")

    # Load file (CLI responsibility)
    supercell_info = loadfn(str(supercell_info_path))

    # Call API (pure logic)
    result = api.pop_interstitial(
        supercell_info=supercell_info,
        index=index,
        pop_all=pop_all,
    )

    # Write output (CLI responsibility)
    result.to_json_file()
    typer.echo("Updated supercell_info.json")
