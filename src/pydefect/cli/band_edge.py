# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Band edge related CLI commands."""

from pathlib import Path
from typing import List

import typer
from monty.serialization import loadfn
from pymatgen.io.vasp import Vasprun, Procar, Outcar
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api

logger = get_logger(__name__)


@app.command(name="pbes",
             help="Create PerfectBandEdgeState from perfect supercell.")
def perfect_band_edge_state(
    dir_path: Path = typer.Option(
        ..., "-d", "--dir",
        help="Directory with perfect supercell calculation."
    ),
):
    """Create PerfectBandEdgeState from perfect supercell calculation."""
    from vise.defaults import defaults

    # Load files (CLI responsibility)
    procar = Procar(str(dir_path / defaults.procar))
    vasprun = Vasprun(str(dir_path / defaults.vasprun), parse_potcar_file=False)
    outcar = Outcar(str(dir_path / defaults.outcar))

    # Call API (pure logic)
    result = api.make_perfect_band_edge_state(procar, vasprun, outcar)

    # Write output (CLI responsibility)
    result.to_json_file(str(dir_path / "perfect_band_edge_state.json"))
    typer.echo(f"Created {dir_path}/perfect_band_edge_state.json")


@app.command(name="beoi",
             help="Create band edge orbital infos for defects.")
def band_edge_orbital_infos(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect calculations."
    ),
    p_state: Path = typer.Option(
        ..., "-pbes", "--p_state",
        help="Path to perfect_band_edge_state.json."
    ),
    no_participation_ratio: bool = typer.Option(
        False, "--no_participation_ratio",
        help="Skip participation ratio calculation."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Create band edge orbital infos and eigenvalue plots for defects."""
    from vise.defaults import defaults

    p_state_obj = loadfn(str(p_state))
    file_name = "band_edge_orbital_infos.json"

    for _dir in dirs:
        def _inner(_dir: Path):
            # Load files (CLI responsibility)
            try:
                dsi = loadfn(_dir / "defect_structure_info.json")
            except FileNotFoundError:
                dsi = None

            procar = Procar(str(_dir / defaults.procar))
            vasprun = Vasprun(str(_dir / defaults.vasprun), parse_potcar_file=False)

            # Call API (pure logic)
            orb_infos = api.make_band_edge_orbital_infos(
                procar, vasprun,
                p_state_obj.vbm_info.energy,
                p_state_obj.cbm_info.energy,
                dsi,
            )

            # Write output (CLI responsibility)
            orb_infos.to_json_file(str(_dir / file_name))
            typer.echo(f"  {_dir}: Created {file_name}")

        try:
            _inner(_dir)
        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


@app.command(name="bes", help="Determine band edge states.")
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
