# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""CLI commands for defect preparation.

Commands for creating defect sets and entries.

Example:
    $ pydefect defect_set -d Al
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api

logger = get_logger(__name__)


# Callback for --oxi_states to parse "Mg 2 O -2" format
def parse_oxi_states(values: Optional[List[str]]) -> Optional[dict]:
    if not values:
        return None
    result = {}
    for i in range(0, len(values), 2):
        result[values[i]] = int(values[i + 1])
    return result


@app.command(name="ds", help="Make defect_in.yaml file.")
def defect_set(
    oxi_states: Optional[List[str]] = typer.Option(
        None, "-o", "--oxi_states",
        help="Oxidation states, e.g., Mg 2 O -2."
    ),
    dopants: Optional[List[str]] = typer.Option(
        None, "-d", "--dopants",
        help="Dopant element names, e.g., Al Ga."
    ),
    keywords: Optional[List[str]] = typer.Option(
        None, "-k", "--keywords",
        help="Keywords to filter defects (regex supported)."
    ),
):
    """Create defect set configuration file."""
    oxi_dict = parse_oxi_states(oxi_states)

    # Load file (CLI responsibility)
    supercell_info = loadfn("supercell_info.json")

    # Call API (pure logic)
    defect_set_obj = api.make_defect_set(
        supercell_info=supercell_info,
        oxi_states=oxi_dict,
        dopants=dopants,
        keywords=keywords,
    )

    # Write output (CLI responsibility)
    defect_set_obj.to_yaml()
    typer.echo("Created defect_in.yaml")


@app.command(name="de", help="Create defect entry directories.")
def defect_entries():
    """Create defect entry directories from supercell_info and defect_set."""
    # Load files (CLI responsibility)
    supercell_info = loadfn("supercell_info.json")
    defect_set_yaml = loadfn("defect_in.yaml")

    # Call API (pure logic)
    api.make_defect_entries(supercell_info, defect_set_yaml)
    typer.echo("Created defect entry directories")
