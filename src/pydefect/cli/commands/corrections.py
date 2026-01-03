# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Correction-related CLI commands (efnv, gkfo)."""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect import api

logger = get_logger(__name__)


def register_commands(app: typer.Typer):
    """Register correction commands to the main app (efnv)."""

    @app.command(name="efnv", help="Generate extended FNV correction files.")
    def efnv(
        dirs: List[Path] = typer.Option(
            ..., "-d", "--dirs",
            help="Directories with defect calculations."
        ),
        perfect_calc_results: Path = typer.Option(
            ..., "-pcr", "--perfect_calc_results",
            help="Path to perfect calc_results.json."
        ),
        unitcell: Path = typer.Option(
            ..., "-u", "--unitcell",
            help="Path to unitcell.yaml."
        ),
        radius: Optional[float] = typer.Option(
            None, "-r", "--radius",
            help="Defect region radius in Angstrom."
        ),
        calc_all_sites: bool = typer.Option(
            False, "--calc_all_sites",
            help="Calculate potential at all sites."
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
        """Generate extended FNV correction for charged defects."""
        from pydefect.analysis.unitcell.models import Unitcell
        from pydefect.analysis.corrections.plotter import SitePotentialMplPlotter

        unitcell_obj = Unitcell.from_yaml(str(unitcell))
        pcr = loadfn(str(perfect_calc_results))
        file_name = "correction.json"

        for _dir in dirs:
            try:
                calc_results = loadfn(_dir / "calc_results.json")
                defect_entry = loadfn(_dir / "defect_entry.json")

                efnv_corr = api.make_efnv_correction(
                    charge=defect_entry.charge,
                    calc_results=calc_results,
                    perfect_calc_results=pcr,
                    dielectric_tensor=unitcell_obj.dielectric_constant,
                    defect_region_radius=radius,
                    calc_all_sites=calc_all_sites,
                )

                efnv_corr.to_json_file(_dir / file_name)

                title = defect_entry.full_name
                plotter = SitePotentialMplPlotter.from_efnv_corr(
                    title=title, efnv_correction=efnv_corr
                )
                plotter.construct_plot()
                plotter.plt.savefig(fname=_dir / "correction.pdf")
                plotter.plt.clf()

                typer.echo(f"  {_dir}: Created {file_name} and correction.pdf")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        typer.echo("Done.")


def register_util_commands(app: typer.Typer):
    """Register correction utility commands (gkfo)."""

    @app.command(name="gkfo", help="Generate GKFO correction files.")
    def gkfo(
        initial_efnv_correction: Path = typer.Option(
            ..., "-iefnv", "--initial_efnv_correction",
            help="Path to initial efnv correction.json."
        ),
        initial_calc_results: Path = typer.Option(
            ..., "-icr", "--initial_calc_results",
            help="Path to initial calc_results.json."
        ),
        final_calc_results: Path = typer.Option(
            ..., "-fcr", "--final_calc_results",
            help="Path to final calc_results.json."
        ),
        unitcell: Path = typer.Option(
            ..., "-u", "--unitcell",
            help="Path to unitcell.yaml."
        ),
        charge_diff: int = typer.Option(
            ..., "-cd", "--charge_diff",
            help="Charge difference (final - initial)."
        ),
    ):
        """Generate GKFO correction for charge state transitions."""
        from pydefect.analysis.unitcell.models import Unitcell
        from pydefect.analysis.corrections.plotter import SitePotentialMplPlotter

        unitcell_obj = Unitcell.from_yaml(str(unitcell))
        efnv_corr = loadfn(str(initial_efnv_correction))
        fcr = loadfn(str(final_calc_results))
        icr = loadfn(str(initial_calc_results))

        gkfo_corr = api.make_gkfo_correction(
            efnv_correction=efnv_corr,
            additional_charge=charge_diff,
            final_calc_results=fcr,
            initial_calc_results=icr,
            diele_tensor=unitcell_obj.dielectric_constant,
            ion_clamped_diele_tensor=unitcell_obj.ele_dielectric_const,
        )

        print(gkfo_corr)
        gkfo_corr.to_json_file("gkfo_correction.json")

        plotter = SitePotentialMplPlotter.from_gkfo_corr(
            title="GKFO correction", gkfo_correction=gkfo_corr
        )
        plotter.construct_plot()
        plotter.plt.savefig(fname="gkfo_correction.pdf")
        plotter.plt.clf()

        typer.echo("Created gkfo_correction.json and gkfo_correction.pdf")
