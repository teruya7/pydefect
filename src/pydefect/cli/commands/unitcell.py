# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Unitcell and calc_results related CLI commands (u, cr, mce)."""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from pymatgen.io.vasp import Vasprun, Outcar
from vise.util.logger import get_logger

from pydefect import api
from pydefect.defaults import defaults

logger = get_logger(__name__)


def register_vasp_commands(app: typer.Typer):
    """Register VASP-specific unitcell/calc commands (u, cr, mce, mp)."""

    @app.command(name="u", help="Create Unitcell from VASP outputs.")
    def unitcell(
        vasprun_band: Path = typer.Option(
            ..., "-vb", "--vasprun_band",
            help="vasprun.xml from band calculation."
        ),
        outcar_band: Path = typer.Option(
            ..., "-ob", "--outcar_band",
            help="OUTCAR from band calculation."
        ),
        outcar_dielectric_clamped: Path = typer.Option(
            ..., "-odc", "--outcar_dielectric_clamped",
            help="OUTCAR with clamped-ion dielectric."
        ),
        outcar_dielectric_ionic: Path = typer.Option(
            ..., "-odi", "--outcar_dielectric_ionic",
            help="OUTCAR with ionic dielectric."
        ),
        name: Optional[str] = typer.Option(
            None, "-n", "--name",
            help="System name."
        ),
    ):
        """Create Unitcell from VASP band and dielectric calculations."""
        vr = Vasprun(str(vasprun_band), parse_potcar_file=False)
        oc = Outcar(str(outcar_band))
        odc = Outcar(str(outcar_dielectric_clamped))
        odi = Outcar(str(outcar_dielectric_ionic))

        unitcell_obj = api.make_unitcell_from_vasp(
            vasprun_band=vr,
            outcar_band=oc,
            outcar_dielectric_clamped=odc,
            outcar_dielectric_ionic=odi,
            system_name=name,
        )

        unitcell_obj.to_yaml_file()
        typer.echo("Created unitcell.yaml")

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
        from vise.defaults import defaults as vise_defaults

        for _dir in dirs:
            try:
                vasprun = Vasprun(str(_dir / vise_defaults.vasprun), parse_potcar_file=False)
                outcar = Outcar(str(_dir / vise_defaults.outcar))

                result = api.make_calc_results_from_vasp(vasprun, outcar)

                result.to_json_file(str(_dir / "calc_results.json"))
                typer.echo(f"  {_dir}: Created calc_results.json")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        typer.echo("Done.")

    @app.command(name="mce", help="Make composition energies from directories.")
    def make_composition_energies(
        dirs: List[Path] = typer.Option(
            ..., "-d", "--dirs",
            help="Directories with competing phase calculations."
        ),
        yaml_file: Optional[Path] = typer.Option(
            None, "-y", "--yaml_file",
            help="composition_energies.yaml to overwrite."
        ),
        verbose: bool = typer.Option(
            False, "-v", "--verbose",
            help="Show traceback on errors."
        ),
    ):
        """Make composition energies from the directories with competing phases."""
        from vise.defaults import defaults as vise_defaults
        from pydefect.analysis.chemical_potential.models import CompositionEnergies

        comp_energies = {}

        for _dir in dirs:
            try:
                vasprun = Vasprun(str(_dir / vise_defaults.vasprun), parse_potcar_file=False)
                outcar = Outcar(str(_dir / vise_defaults.outcar))
                
                composition = vasprun.final_structure.composition.reduced_formula
                energy_per_atom = outcar.final_energy / vasprun.final_structure.num_sites
                comp_energies[composition] = energy_per_atom
                typer.echo(f"  {_dir}: {composition} = {energy_per_atom:.6f} eV/atom")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        result = CompositionEnergies(comp_energies)
        if yaml_file:
            existing = CompositionEnergies.from_yaml(str(yaml_file))
            existing.composition_energies.update(result.composition_energies)
            result = existing
        
        result.to_yaml_file()
        typer.echo("Created composition_energies.yaml")

    @app.command(name="mp", help="Get competing phases from Materials Project.")
    def make_poscars(
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
