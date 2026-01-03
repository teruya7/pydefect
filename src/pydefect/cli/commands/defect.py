# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Defect-related CLI commands (ds, de, dsi, dei, des, pe, cs)."""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect import api
from pydefect.defaults import defaults

logger = get_logger(__name__)


def register_commands(app: typer.Typer):
    """Register defect analysis commands to the app."""

    @app.command(name="ds", help="Make defect_in.yaml file.")
    def defect_set(
        oxi_states: Optional[List[str]] = typer.Option(
            None, "-o", "--oxi_states",
            help="Oxidation states, e.g., Mg 2 O -2."
        ),
        dopants: Optional[List[str]] = typer.Option(
            None, "-d", "--dopants",
            help="Dopant element names, e.g., Al Ga."
        ),
        keywords: Optional[List[str]] = typer.Option(
            None, "-k", "--keywords",
            help="Keywords to filter defects (regex supported)."
        ),
    ):
        """Create defect set configuration file."""
        def parse_oxi_states(values):
            if not values:
                return None
            result = {}
            for i in range(0, len(values), 2):
                result[values[i]] = int(values[i + 1])
            return result

        oxi_dict = parse_oxi_states(oxi_states)
        supercell_info = loadfn("supercell_info.json")

        defect_set_obj = api.make_defect_set(
            supercell_info=supercell_info,
            oxi_states=oxi_dict,
            dopants=dopants,
            keywords=keywords,
        )

        defect_set_obj.to_yaml()
        typer.echo("Created defect_in.yaml")

    @app.command(name="dsi", help="Analyze defect structure.")
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
            defaults.dist_tol, "-dt", "--dist_tolerance",
            help="Distance tolerance in Angstrom."
        ),
        symprec: float = typer.Option(
            defaults.symmetry_length_tolerance, "--symprec",
            help="Symmetry precision for spglib."
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
        """Analyze defect structure to get displacement and symmetry info."""
        supercell_info = loadfn(str(supercell_info_path))
        file_name = "defect_structure_info.json"

        for _dir in dirs:
            try:
                calc_results = loadfn(_dir / "calc_results.json")
                defect_entry = loadfn(_dir / "defect_entry.json")

                info = api.make_defect_structure_info(
                    perfect_structure=supercell_info.structure,
                    initial_defect_structure=defect_entry.structure,
                    final_defect_structure=calc_results.structure,
                    dist_tol=dist_tolerance,
                    symprec=symprec,
                )

                info.to_json_file(str(_dir / file_name))
                typer.echo(f"  {_dir}: Created {file_name}")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        typer.echo("Done.")

    @app.command(name="dei", help="Calculate defect energy information.")
    def defect_energy_infos(
        dirs: List[Path] = typer.Option(
            ..., "-d", "--dirs",
            help="Directories with defect calculations."
        ),
        unitcell: Path = typer.Option(
            ..., "-u", "--unitcell",
            help="Path to unitcell.yaml."
        ),
        perfect_calc_results: Path = typer.Option(
            ..., "-pcr", "--perfect_calc_results",
            help="Path to perfect calc_results.json."
        ),
        std_energies: Path = typer.Option(
            ..., "-s", "--std_energies",
            help="Path to standard_energies.yaml."
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
        """Calculate defect energy information for multiple directories."""
        from pydefect.analysis.chemical_potential.models import StandardEnergies
        from pydefect.analysis.corrections.models import NoCorrection

        unitcell_obj = loadfn(str(unitcell))
        pcr = loadfn(str(perfect_calc_results))
        std = StandardEnergies.from_yaml(str(std_energies))
        file_name = "defect_energy_info.yaml"

        for _dir in dirs:
            try:
                calc_results = loadfn(_dir / "calc_results.json")
                defect_entry = loadfn(_dir / "defect_entry.json")

                try:
                    correction = loadfn(_dir / "correction.json")
                except FileNotFoundError:
                    correction = NoCorrection()

                info = api.make_defect_energy_info(
                    defect_entry=defect_entry,
                    calc_results=calc_results,
                    correction=correction,
                    perfect_calc_results=pcr,
                    unitcell=unitcell_obj,
                    standard_energies=std,
                )

                info.to_yaml_file(str(_dir / file_name))
                typer.echo(f"  {_dir}: Created {file_name}")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        typer.echo("Done.")

    @app.command(name="des", help="Create defect energy summary.")
    def defect_energy_summary(
        dirs: List[Path] = typer.Option(
            ..., "-d", "--dirs",
            help="Directories with defect_energy_info.yaml."
        ),
        unitcell: Path = typer.Option(
            ..., "-u", "--unitcell",
            help="Path to unitcell.yaml."
        ),
        p_state: Path = typer.Option(
            ..., "-pbes", "--p_state",
            help="Path to perfect_band_edge_state.json."
        ),
        target_vertices_yaml: Path = typer.Option(
            ..., "-t", "--target_vertices_yaml",
            help="Path to target_vertices.yaml."
        ),
        verbose: bool = typer.Option(
            False, "-v", "--verbose",
            help="Show traceback on errors."
        ),
    ):
        """Create defect energy summary from multiple defect calculations."""
        from pydefect.analysis.chemical_potential.models import TargetVertices

        unitcell_obj = loadfn(str(unitcell))
        p_state_obj = loadfn(str(p_state))
        target_vertices = TargetVertices.from_yaml(str(target_vertices_yaml))
        infos = []

        for _dir in dirs:
            try:
                energy_info = loadfn(_dir / "defect_energy_info.yaml")
                str_info = loadfn(_dir / "defect_structure_info.json")
                infos.append((energy_info, str_info))
            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        summary = api.make_defect_energy_summary(
            defect_energy_infos=infos,
            target_vertices=target_vertices,
            unitcell=unitcell_obj,
            perfect_band_edge_state=p_state_obj,
        )

        summary.to_json_file()
        typer.echo("Created defect_energy_summary.json")

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
        no_calc_results_check: bool = typer.Option(
            False, "-nccr", "--no_calc_results_check",
            help="Skip calc_results.json check."
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
                calc_results = loadfn(_dir / "calc_results.json")
                defect_entry = loadfn(_dir / "defect_entry.json")
                str_info = loadfn(_dir / "defect_structure_info.json")
                infos.append((calc_results, defect_entry, str_info))
            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        summary = api.make_calc_summary(infos, pcr)

        summary.to_json_file()
        typer.echo("Created calc_summary.json")

    @app.command(name="pe", help="Plot defect formation energy.")
    def plot_defect_energy(
        defect_energy_summary_path: Path = typer.Option(
            ..., "-d", "--defect_energy_summary",
            help="defect_energy_summary.json file."
        ),
        label: str = typer.Option(
            ..., "-l", "--label",
            help="Label for this chemical potential condition."
        ),
        allow_shallow: bool = typer.Option(
            False, "--allow_shallow",
            help="Allow shallow defects."
        ),
        no_corrections: bool = typer.Option(
            False, "--no_corrections",
            help="Disable corrections."
        ),
        y_range: Optional[List[float]] = typer.Option(
            None, "-y", "--y_range",
            help="Y-axis range (min max)."
        ),
        no_label_line: bool = typer.Option(
            False, "--no_label_line",
            help="Don't put labels on lines."
        ),
        no_add_charges: bool = typer.Option(
            False, "--no_add_charges",
            help="Don't show charges."
        ),
        plot_all_energies: bool = typer.Option(
            False, "--plot_all_energies",
            help="Plot all charge states."
        ),
    ):
        """Plot defect formation energies as a function of Fermi level."""
        summary = loadfn(str(defect_energy_summary_path))

        api.plot_defect_energy(
            summary,
            label=label,
            y_range=list(y_range) if y_range else None,
            add_charges=not no_add_charges,
            plot_all_energies=plot_all_energies,
            with_corrections=not no_corrections,
            allow_shallow=allow_shallow,
            label_line=not no_label_line,
        )
        typer.echo("Created defect_formation_energy.pdf")


def register_vasp_commands(app: typer.Typer):
    """Register VASP-specific defect commands (de)."""

    @app.command(name="de", help="Create defect entry directories.")
    def defect_entries():
        """Create defect entry directories from supercell_info and defect_set."""
        supercell_info = loadfn("supercell_info.json")
        defect_set_yaml = loadfn("defect_in.yaml")

        api.make_defect_entries(supercell_info, defect_set_yaml)
        typer.echo("Created defect entry directories")
