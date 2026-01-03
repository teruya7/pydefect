# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Calculation results related CLI commands."""

from pathlib import Path
from typing import List

import typer
from monty.serialization import loadfn
from pymatgen.io.vasp import Vasprun, Outcar
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api

logger = get_logger(__name__)


@app.command(name="cr", help="Create calc_results.json from VASP outputs.")
def calc_results(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with VASP calculations."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Create calc_results.json from VASP outputs."""
    from vise.defaults import defaults

    for _dir in dirs:
        def _inner(_dir: Path):
            # Load files (CLI responsibility)
            vasprun = Vasprun(str(_dir / defaults.vasprun), parse_potcar_file=False)
            outcar = Outcar(str(_dir / defaults.outcar))

            # Call API (pure logic)
            result = api.make_calc_results_from_vasp(vasprun, outcar)

            # Write output (CLI responsibility)
            result.to_json_file(str(_dir / "calc_results.json"))
            typer.echo(f"  {_dir}: Created calc_results.json")

        try:
            _inner(_dir)
        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


@app.command(name="cs", help="Create calculation summary.")
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
