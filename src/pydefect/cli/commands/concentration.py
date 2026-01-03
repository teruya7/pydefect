# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Concentration related CLI commands (ccc, cdc, pcc, pdc, md)."""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect import api

logger = get_logger(__name__)


def register_util_commands(app: typer.Typer):
    """Register concentration utility commands."""

    @app.command(name="md", help="Make degeneracies from defect calculations.")
    def make_degeneracies(
        dirs: List[Path] = typer.Option(
            ..., "-d", "--dirs",
            help="Directories with defect calculations."
        ),
        supercell_info: Path = typer.Option(
            "supercell_info.json", "-s", "--supercell_info",
            help="Path to supercell_info.json."
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
        """Make degeneracies.yaml from defect calculations."""
        si = loadfn(str(supercell_info))
        degeneracies = {}

        for _dir in dirs:
            try:
                dsi = loadfn(_dir / "defect_structure_info.json")
                defect_entry = loadfn(_dir / "defect_entry.json")
                
                deg = api.get_degeneracy(
                    defect_entry=defect_entry,
                    defect_structure_info=dsi,
                    supercell_info=si,
                )
                degeneracies[defect_entry.full_name] = deg
                typer.echo(f"  {_dir}: {defect_entry.full_name} = {deg}")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        from pydefect.analysis.concentration.degeneracy import Degeneracies
        result = Degeneracies(degeneracies)
        result.to_yaml_file()
        typer.echo("Created degeneracies.yaml")

    @app.command(name="ccc", help="Calculate carrier concentrations.")
    def calc_carrier_concentrations(
        total_dos: Path = typer.Option(
            ..., "-t", "--total_dos",
            help="Path to total_dos.json."
        ),
        temperature: float = typer.Option(
            300.0, "-T", "--T",
            help="Temperature in K."
        ),
    ):
        """Calculate carrier concentrations as functions of Fermi level."""
        dos = loadfn(str(total_dos))
        result = api.calc_carrier_concentrations(dos, temperature)
        result.to_json_file()
        typer.echo("Created con_by_Ef.json")

    @app.command(name="cdc", help="Calculate defect concentrations.")
    def calc_defect_concentrations(
        defect_energy_summary: Path = typer.Option(
            ..., "-d", "--defect_energy_summary",
            help="Path to defect_energy_summary.json."
        ),
        label: str = typer.Option(
            ..., "-l", "--label",
            help="Label in chemical potential diagram."
        ),
        degeneracies: Path = typer.Option(
            ..., "--degeneracies",
            help="Path to degeneracies.yaml."
        ),
        total_dos: Path = typer.Option(
            ..., "-t", "--total_dos",
            help="Path to total_dos.json."
        ),
        temperature: float = typer.Option(
            300.0, "-T", "--T",
            help="Temperature in K."
        ),
        with_corrections: bool = typer.Option(
            True, "--with_corrections/--no_corrections",
            help="Include corrections."
        ),
        allow_shallow: bool = typer.Option(
            False, "--allow_shallow",
            help="Allow shallow defects."
        ),
        con_by_Ef: Optional[Path] = typer.Option(
            None, "--con_by_Ef",
            help="Previous concentration for quenching."
        ),
        net_abs_ratio: float = typer.Option(
            1e-5, "--net_abs_ratio",
            help="Net charge abs ratio for equilibrium."
        ),
    ):
        """Calculate defect concentrations."""
        from pydefect.analysis.concentration.degeneracy import Degeneracies

        summary = loadfn(str(defect_energy_summary))
        deg = Degeneracies.from_yaml(str(degeneracies))
        dos = loadfn(str(total_dos))
        prev_con = loadfn(str(con_by_Ef)) if con_by_Ef else None

        result = api.calc_defect_concentrations(
            defect_energy_summary=summary,
            label=label,
            degeneracies=deg,
            total_dos=dos,
            temperature=temperature,
            with_corrections=with_corrections,
            allow_shallow=allow_shallow,
            prev_con_by_Ef=prev_con,
            net_abs_ratio=net_abs_ratio,
        )
        result.to_json_file()
        typer.echo("Created con_by_Ef.json")

    @app.command(name="pcc", help="Plot carrier concentrations.")
    def plot_carrier_concentrations(
        con_by_Ef: List[Path] = typer.Option(
            ..., "-c", "--con_by_Ef",
            help="con_by_Ef.json files."
        ),
        concentration_ranges: Optional[List[float]] = typer.Option(
            None, "-cr", "--concentration_ranges",
            help="Concentration ranges (exponents)."
        ),
        energy_ranges: Optional[List[float]] = typer.Option(
            None, "-er", "--energy_ranges",
            help="Energy ranges."
        ),
    ):
        """Plot carrier concentrations."""
        cons = [loadfn(str(c)) for c in con_by_Ef]
        api.plot_carrier_concentrations(
            cons,
            concentration_ranges=concentration_ranges,
            energy_ranges=energy_ranges,
        )
        typer.echo("Created carrier_concentrations.pdf")

    @app.command(name="pdc", help="Plot defect concentrations.")
    def plot_defect_concentrations(
        con_by_Ef: Path = typer.Option(
            ..., "-c", "--con_by_Ef",
            help="con_by_Ef.json file."
        ),
    ):
        """Plot defect concentrations."""
        con = loadfn(str(con_by_Ef))
        api.plot_defect_concentrations(con)
        typer.echo("Created defect_concentrations.pdf")

    @app.command(name="cccdc", help="Calculate CCD correction energy.")
    def calc_ccd_correction(
        unitcell: Path = typer.Option(
            ..., "-u", "--unitcell",
            help="Path to unitcell.yaml."
        ),
        charge_diff: int = typer.Option(
            ..., "-cd", "--charge_diff",
            help="Charge difference."
        ),
        disp_ratio: float = typer.Option(
            ..., "-d", "--disp_ratio",
            help="Displacement ratio."
        ),
        calc_results: Path = typer.Option(
            ..., "-c", "--calc_results",
            help="calc_results.json at fixed structure."
        ),
        no_disp_calc_results: Path = typer.Option(
            ..., "-ndc", "--no_disp_calc_results",
            help="calc_results.json at relaxed structure."
        ),
        no_disp_defect_entry: Path = typer.Option(
            ..., "-ndde", "--no_disp_defect_entry",
            help="defect_entry.json at relaxed structure."
        ),
    ):
        """Calculate config coordinate correction energy."""
        from pydefect.analysis.unitcell.models import Unitcell

        unitcell_obj = Unitcell.from_yaml(str(unitcell))
        cr = loadfn(str(calc_results))
        no_disp_cr = loadfn(str(no_disp_calc_results))
        no_disp_de = loadfn(str(no_disp_defect_entry))

        correction = api.calc_ccd_correction(
            unitcell=unitcell_obj,
            charge_diff=charge_diff,
            disp_ratio=disp_ratio,
            calc_results=cr,
            no_disp_calc_results=no_disp_cr,
            no_disp_defect_entry=no_disp_de,
        )
        typer.echo(f"CCD correction: {correction:.6f} eV")
