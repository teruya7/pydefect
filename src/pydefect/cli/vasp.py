# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""VASP-specific Typer commands.

Commands for creating pydefect objects from VASP outputs.

Example:
    $ pydefect vasp unitcell -vb band/vasprun.xml -ob band/OUTCAR
    $ pydefect vasp calc_results -d Va_O1_0
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from pymatgen.core import Structure
from pymatgen.io.vasp import Vasprun, Outcar, Procar, Chgcar

from pydefect.cli.typer_app import vasp_app
from pydefect import api


@vasp_app.command(name="unitcell", help="Create unitcell from VASP outputs.")
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
    vr = Vasprun(str(vasprun_band), parse_potcar_file=False)
    oc_band = Outcar(str(outcar_band))
    oc_diel_clamp = Outcar(str(outcar_dielectric_clamped)) if outcar_dielectric_clamped else None
    oc_diel_ionic = Outcar(str(outcar_dielectric_ionic)) if outcar_dielectric_ionic else None

    unitcell = api.make_unitcell_from_vasp(
        vasprun_band=vr,
        outcar_band=oc_band,
        outcar_dielectric_clamped=oc_diel_clamp,
        outcar_dielectric_ionic=oc_diel_ionic,
        system_name=name,
    )
    unitcell.to_yaml_file()
    typer.echo("Created unitcell.yaml")


@vasp_app.command(name="calc_results", help="Create calc_results from VASP outputs.")
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
    from pydefect.cli.main_tools import parse_dirs
    from pydefect.analyzer.make_calc_results import make_calc_results_from_vasp
    from vise.defaults import defaults

    file_name = "calc_results.json"

    def _inner(_dir: Path):
        vr = Vasprun(_dir / defaults.vasprun, parse_potcar_file=False)
        oc = Outcar(_dir / defaults.outcar)
        cr = make_calc_results_from_vasp(vasprun=vr, outcar=oc)
        cr.to_json_file(str(_dir / file_name))

    parse_dirs(list(dirs), _inner, verbose, file_name)
    typer.echo("Created calc_results.json files")


@vasp_app.command(name="defect_entries", help="Create defect entry directories.")
def defect_entries():
    """Create defect entry directories from supercell_info and defect_set."""
    from vise.util.logger import get_logger
    logger = get_logger(__name__)

    supercell_info = loadfn("supercell_info.json")
    perfect = Path("perfect")

    try:
        perfect.mkdir()
        logger.info("Making perfect dir...")
        supercell_info.structure.to(filename=str(perfect / "POSCAR"))
    except FileExistsError:
        logger.info("perfect dir exists, skipped...")

    from pydefect.input_maker.defect_set import DefectSet
    defect_set = DefectSet.from_yaml()
    entries = api.make_defect_entries(supercell_info, defect_set)

    for entry in entries:
        dir_path = Path(entry.full_name)
        try:
            dir_path.mkdir()
            logger.info(f"Making {dir_path} dir...")
            if entry.perturbed_structure:
                entry.perturbed_structure.to(filename=str(dir_path / "POSCAR"))
            else:
                entry.structure.to(filename=str(dir_path / "POSCAR"))
            entry.to_json_file(filename=str(dir_path / "defect_entry.json"))
            entry.to_prior_info(filename=str(dir_path / "prior_info.yaml"))
        except FileExistsError:
            logger.info(f"{dir_path} dir exists, skipped...")

    typer.echo(f"Created {len(entries)} defect entry directories")


@vasp_app.command(name="perfect_band_edge_state",
                  help="Create perfect band edge state.")
def perfect_band_edge_state(
    dir_path: Path = typer.Option(
        ..., "-d", "--dir",
        help="Directory with perfect supercell calculation."
    ),
):
    """Create PerfectBandEdgeState from perfect supercell calculation."""
    from vise.defaults import defaults
    from pydefect.analyzer.eigenvalue_plotter import EigenvalueMplPlotter
    from pydefect.analyzer.make_band_edge_orbital_infos import make_band_edge_orbital_infos

    procar = Procar(dir_path / defaults.procar)
    vasprun = Vasprun(dir_path / defaults.vasprun, parse_potcar_file=False)
    outcar = Outcar(dir_path / defaults.outcar)

    p_state = api.make_perfect_band_edge_state(procar, vasprun, outcar)
    p_state.to_json_file(dir_path / "perfect_band_edge_state.json")

    vbm = p_state.vbm_info.energy
    cbm = p_state.cbm_info.energy
    orb_infos = make_band_edge_orbital_infos(procar, vasprun, vbm, cbm)
    orb_infos.to_json_file(dir_path / "band_edge_orbital_infos.json")

    plotter = EigenvalueMplPlotter(
        title="perfect", band_edge_orb_infos=orb_infos,
        supercell_vbm=vbm, supercell_cbm=cbm
    )
    plotter.construct_plot()
    plotter.plt.savefig(fname=dir_path / "eigenvalues.pdf")
    plotter.plt.clf()

    typer.echo("Created perfect_band_edge_state.json, band_edge_orbital_infos.json, eigenvalues.pdf")


@vasp_app.command(name="band_edge_orbital_infos",
                  help="Create band edge orbital infos and eigenvalue plots.")
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
        help="Y-axis range for eigenvalue plot."
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
    from pydefect.cli.main_tools import parse_dirs
    from pydefect.analyzer.eigenvalue_plotter import EigenvalueMplPlotter
    from pydefect.analyzer.make_band_edge_orbital_infos import make_band_edge_orbital_infos
    from vise.defaults import defaults

    p_state_obj = loadfn(str(p_state))
    supercell_vbm = p_state_obj.vbm_info.energy
    supercell_cbm = p_state_obj.cbm_info.energy
    file_name = "band_edge_orbital_infos.json"

    def _inner(_dir: Path):
        try:
            defect_entry = loadfn(_dir / "defect_entry.json")
            title = defect_entry.name
        except FileNotFoundError:
            title = "No name"

        procar = Procar(_dir / defaults.procar)
        vasprun = Vasprun(_dir / defaults.vasprun, parse_potcar_file=False)

        str_info = None
        if not no_participation_ratio:
            str_info = loadfn(_dir / "defect_structure_info.json")

        try:
            eigval_shift = loadfn(_dir / "eigenvalue_shift.yaml")["shift_value"]
        except FileNotFoundError:
            eigval_shift = 0.0

        orb_infos = make_band_edge_orbital_infos(
            procar, vasprun, supercell_vbm, supercell_cbm,
            str_info, eigval_shift=eigval_shift
        )
        orb_infos.to_json_file(_dir / file_name)

        plotter = EigenvalueMplPlotter(
            title=title, band_edge_orb_infos=orb_infos,
            supercell_vbm=supercell_vbm, supercell_cbm=supercell_cbm,
            y_range=y_range
        )
        plotter.construct_plot()
        plotter.plt.savefig(fname=_dir / "eigenvalues.pdf")
        plotter.plt.clf()

    parse_dirs(list(dirs), _inner, verbose, file_name)
    typer.echo("Created band_edge_orbital_infos.json and eigenvalues.pdf files")
