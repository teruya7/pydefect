# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Unitcell-related CLI commands."""

from pathlib import Path
from typing import Optional

import typer
from pymatgen.io.vasp import Vasprun, Outcar

from pydefect.cli.typer_app import app
from pydefect import api


@app.command(name="unitcell", help="Create Unitcell from VASP outputs.")
def unitcell(
    vasprun_band: Path = typer.Option(
        ..., "-vb", "--vasprun_band",
        help="vasprun.xml from band calculation."
    ),
    outcar_band: Path = typer.Option(
        ..., "-ob", "--outcar_band",
        help="OUTCAR from band calculation."
    ),
    outcar_dielectric_clamped: Optional[Path] = typer.Option(
        None, "-odc", "--outcar_dielectric_clamped",
        help="OUTCAR with clamped-ion dielectric."
    ),
    outcar_dielectric_ionic: Optional[Path] = typer.Option(
        None, "-odi", "--outcar_dielectric_ionic",
        help="OUTCAR with ionic dielectric."
    ),
    name: Optional[str] = typer.Option(
        None, "-n", "--name",
        help="System name."
    ),
):
    """Create Unitcell from VASP band and dielectric calculations."""
    # Load files (CLI responsibility)
    vr = Vasprun(str(vasprun_band), parse_potcar_file=False)
    oc = Outcar(str(outcar_band))
    odc = Outcar(str(outcar_dielectric_clamped)) if outcar_dielectric_clamped else None
    odi = Outcar(str(outcar_dielectric_ionic)) if outcar_dielectric_ionic else None

    # Call API (pure logic)
    unitcell_obj = api.make_unitcell_from_vasp(
        vasprun_band=vr,
        outcar_band=oc,
        outcar_dielectric_clamped=odc,
        outcar_dielectric_ionic=odi,
        system_name=name,
    )

    # Write output (CLI responsibility)
    unitcell_obj.to_yaml_file()
    typer.echo("Created unitcell.yaml")
