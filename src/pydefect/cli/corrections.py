# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Correction-related Typer commands.

Commands for EFNV and GKFO corrections.

Example:
    $ pydefect efnv -d Va_O1_0 Va_O1_1 -pcr perfect/calc_results.json -u unitcell.yaml
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api
from pydefect.analyzer.unitcell.unitcell import Unitcell
from pydefect.analyzer.corrections.site_potential_plotter import SitePotentialMplPlotter

logger = get_logger(__name__)


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
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Generate extended FNV correction for charged defects."""
    unitcell_obj = Unitcell.from_yaml(str(unitcell))
    pcr = loadfn(str(perfect_calc_results))
    file_name = "correction.json"

    for _dir in dirs:
        try:
            # Load files (CLI responsibility)
            calc_results = loadfn(_dir / "calc_results.json")
            defect_entry = loadfn(_dir / "defect_entry.json")

            # Call API (pure logic)
            efnv_corr = api.make_efnv_correction(
                charge=defect_entry.charge,
                calc_results=calc_results,
                perfect_calc_results=pcr,
                dielectric_tensor=unitcell_obj.dielectric_constant,
                defect_region_radius=radius,
                calc_all_sites=calc_all_sites,
            )

            # Write output (CLI responsibility)
            efnv_corr.to_json_file(_dir / file_name)

            # Plot (CLI responsibility)
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
