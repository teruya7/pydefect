# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Analysis-related Typer commands.

Commands for defect structure analysis and band edge states.

Example:
    $ pydefect defect_structure_info -d Va_O1_0 -s supercell_info.json
    $ pydefect band_edge_states -d Va_O1_0 -pbes perfect_band_edge_state.json
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api

logger = get_logger(__name__)


@app.command(name="defect_structure_info", help="Analyze defect structure.")
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


@app.command(name="band_edge_states", help="Determine band edge states.")
def band_edge_states(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect calculations."
    ),
    p_state: Path = typer.Option(
        ..., "-pbes", "--p_state",
        help="Path to perfect_band_edge_state.json."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Determine band edge states from orbital information."""
    p_state_obj = loadfn(str(p_state))
    file_name = "band_edge_states.json"

    for _dir in dirs:
        try:
            # Load files (CLI responsibility)
            orb_infos = loadfn(_dir / "band_edge_orbital_infos.json")
            try:
                defect_charge_info = loadfn(_dir / "defect_charge_info.json")
            except FileNotFoundError:
                defect_charge_info = None

            # Call API (pure logic)
            states = api.make_band_edge_states(orb_infos, p_state_obj, defect_charge_info)

            # Write output (CLI responsibility)
            states.to_json_file(str(_dir / file_name))
            typer.echo(f"  {_dir}: Created {file_name}")

        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


@app.command(name="calc_summary", help="Create calculation summary.")
def calc_summary(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect calculations."
    ),
    perfect_calc_results: Path = typer.Option(
        ..., "-pcr", "--perfect_calc_results",
        help="Path to perfect calc_results.json."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Create calculation summary from multiple defect calculations."""
    pcr = loadfn(str(perfect_calc_results))
    infos = []

    for _dir in dirs:
        try:
            # Load files (CLI responsibility)
            calc_results = loadfn(_dir / "calc_results.json")
            defect_entry = loadfn(_dir / "defect_entry.json")
            str_info = loadfn(_dir / "defect_structure_info.json")
            infos.append((calc_results, defect_entry, str_info))
        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    # Call API (pure logic)
    summary = api.make_calc_summary(infos, pcr)

    # Write output (CLI responsibility)
    summary.to_json_file()
    typer.echo("Created calc_summary.json")
