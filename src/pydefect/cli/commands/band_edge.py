# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Band edge related CLI commands (bes, pbes, beoi)."""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect import api

logger = get_logger(__name__)


def register_commands(app: typer.Typer):
    """Register band edge state commands to the main app (bes)."""

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
        no_calc_results_check: bool = typer.Option(
            False, "-nccr", "--no_calc_results_check",
            help="Skip calc_results.json check."
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
                orb_infos = loadfn(_dir / "band_edge_orbital_infos.json")
                try:
                    defect_charge_info = loadfn(_dir / "defect_charge_info.json")
                except FileNotFoundError:
                    defect_charge_info = None

                states = api.make_band_edge_states(orb_infos, p_state_obj, defect_charge_info)

                states.to_json_file(str(_dir / file_name))
                typer.echo(f"  {_dir}: Created {file_name}")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        typer.echo("Done.")


def register_vasp_commands(app: typer.Typer):
    """Register VASP-specific band edge commands (pbes, beoi)."""
    from pymatgen.io.vasp import Vasprun, Outcar, Procar

    @app.command(name="pbes", help="Create PerfectBandEdgeState from perfect supercell.")
    def perfect_band_edge_state(
        dir_path: Path = typer.Option(
            ..., "-d", "--dir",
            help="Directory with perfect supercell calculation."
        ),
    ):
        """Create PerfectBandEdgeState from perfect supercell calculation."""
        from vise.defaults import defaults as vise_defaults

        procar = Procar(str(dir_path / vise_defaults.procar))
        vasprun = Vasprun(str(dir_path / vise_defaults.vasprun), parse_potcar_file=False)
        outcar = Outcar(str(dir_path / vise_defaults.outcar))

        result = api.make_perfect_band_edge_state(procar, vasprun, outcar)

        result.to_json_file(str(dir_path / "perfect_band_edge_state.json"))
        typer.echo(f"Created {dir_path}/perfect_band_edge_state.json")

    @app.command(name="beoi", help="Create band edge orbital infos for defects.")
    def band_edge_orbital_infos(
        dirs: List[Path] = typer.Option(
            ..., "-d", "--dirs",
            help="Directories with defect calculations."
        ),
        p_state: Path = typer.Option(
            ..., "-pbes", "--p_state",
            help="Path to perfect_band_edge_state.json."
        ),
        y_range: Optional[List[float]] = typer.Option(
            None, "-y", "--y_range",
            help="Energy range for eigenvalue.pdf."
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
        from vise.defaults import defaults as vise_defaults

        p_state_obj = loadfn(str(p_state))
        file_name = "band_edge_orbital_infos.json"

        for _dir in dirs:
            try:
                try:
                    dsi = loadfn(_dir / "defect_structure_info.json")
                except FileNotFoundError:
                    dsi = None

                procar = Procar(str(_dir / vise_defaults.procar))
                vasprun = Vasprun(str(_dir / vise_defaults.vasprun), parse_potcar_file=False)

                orb_infos = api.make_band_edge_orbital_infos(
                    procar, vasprun,
                    p_state_obj.vbm_info.energy,
                    p_state_obj.cbm_info.energy,
                    dsi,
                )

                orb_infos.to_json_file(str(_dir / file_name))
                typer.echo(f"  {_dir}: Created {file_name}")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        typer.echo("Done.")
