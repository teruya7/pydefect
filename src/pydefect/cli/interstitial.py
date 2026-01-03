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


@app.command(name="local_extrema", help="Make local_extrema.json from volumetric data.")
def local_extrema(
    volumetric_data: List[Path] = typer.Option(
        ..., "-v", "--volumetric_data",
        help="Volumetric data files (e.g., AECCAR0 AECCAR2)."
    ),
    info: Optional[str] = typer.Option(
        None, "-i", "--info",
        help="Info string for saving."
    ),
    find_max: bool = typer.Option(
        False, "--find_max",
        help="Find maxima instead of minima."
    ),
    threshold_frac: Optional[float] = typer.Option(
        None, "--threshold_frac",
        help="Fractional threshold."
    ),
    threshold_abs: Optional[float] = typer.Option(
        None, "--threshold_abs",
        help="Absolute threshold."
    ),
    min_dist: float = typer.Option(
        0.5, "--min_dist",
        help="Minimum distance between extrema."
    ),
    tol: float = typer.Option(
        0.5, "--tol",
        help="Tolerance for grouping sites."
    ),
    radius: float = typer.Option(
        0.4, "--radius",
        help="Radius for local extrema search."
    ),
):
    """Find local extrema in volumetric data for interstitial sites."""
    from pymatgen.io.vasp import Chgcar

    # Load and sum volumetric data
    chgcars = [Chgcar.from_file(str(vd)) for vd in volumetric_data]

    extrema = api.make_local_extrema(
        volumetric_data=chgcars,
        threshold_frac=threshold_frac,
        threshold_abs=threshold_abs,
        min_dist=min_dist,
        tol=tol,
        radius=radius,
        find_max=find_max,
    )
    extrema.to_json_file()
    typer.echo(f"Created volumetric_data_local_extrema.json ({info})")

