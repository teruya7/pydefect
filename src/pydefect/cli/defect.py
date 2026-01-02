# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Defect-related CLI commands.

Commands for defect set creation, structure analysis, and energy calculations.

Example:
    $ pydefect defect_set -d Al
    $ pydefect defect_structure_info -d Va_O1_0
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from pymatgen.core import Structure
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app
from pydefect import api

logger = get_logger(__name__)


# Callback for --oxi_states to parse "Mg 2 O -2" format
def parse_oxi_states(values: Optional[List[str]]) -> Optional[dict]:
    if not values:
        return None
    result = {}
    for i in range(0, len(values), 2):
        result[values[i]] = int(values[i + 1])
    return result


@app.command(name="defect_set", help="Make defect_in.yaml file.")
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
    oxi_dict = parse_oxi_states(oxi_states)

    # Load file (CLI responsibility)
    supercell_info = loadfn("supercell_info.json")

    # Call API (pure logic)
    defect_set_obj = api.make_defect_set(
        supercell_info=supercell_info,
        oxi_states=oxi_dict,
        dopants=dopants,
        keywords=keywords,
    )

    # Write output (CLI responsibility)
    defect_set_obj.to_yaml()
    typer.echo("Created defect_in.yaml")


@app.command(name="defect_entries", help="Create defect entry directories.")
def defect_entries():
    """Create defect entry directories from supercell_info and defect_set."""
    # Load files (CLI responsibility)
    supercell_info = loadfn("supercell_info.json")
    defect_set_yaml = loadfn("defect_in.yaml")

    # Call API (pure logic)
    api.make_defect_entries(supercell_info, defect_set_yaml)
    typer.echo("Created defect entry directories")


@app.command(name="append_interstitial", help="Append interstitial to supercell_info.")
def append_interstitial(
    supercell_info_path: Path = typer.Option(
        "supercell_info.json", "-s", "--supercell_info",
        help="Path to supercell_info.json."
    ),
    base_structure: Path = typer.Option(
        ..., "-p", "--base_structure",
        help="Structure file for fractional coordinates."
    ),
    frac_coords: List[float] = typer.Option(
        ..., "-c", "--frac_coords",
        help="Fractional coordinates (3 values)."
    ),
    info: str = typer.Option(
        "None", "-i", "--info",
        help="Description of interstitial site."
    ),
):
    """Append interstitial site to supercell_info."""
    # Load files (CLI responsibility)
    supercell_info = loadfn(str(supercell_info_path))
    structure = Structure.from_file(str(base_structure))

    # Call API (pure logic)
    result = api.append_interstitial(
        supercell_info=supercell_info,
        base_structure=structure,
        frac_coords=list(frac_coords),
        info=info if info != "None" else None,
    )

    # Write output (CLI responsibility)
    result.to_json_file()
    typer.echo("Updated supercell_info.json")


@app.command(name="pop_interstitial", help="Remove interstitial from supercell_info.")
def pop_interstitial(
    supercell_info_path: Path = typer.Option(
        "supercell_info.json", "-s", "--supercell_info",
        help="Path to supercell_info.json."
    ),
    index: Optional[int] = typer.Option(
        None, "-i", "--index",
        help="Interstitial index to remove (1-based)."
    ),
    pop_all: bool = typer.Option(
        False, "--pop_all",
        help="Remove all interstitials."
    ),
):
    """Remove interstitial site(s) from supercell_info."""
    logger.info("Be careful that the interstitials indices are changed.")

    # Load file (CLI responsibility)
    supercell_info = loadfn(str(supercell_info_path))

    # Call API (pure logic)
    result = api.pop_interstitial(
        supercell_info=supercell_info,
        index=index,
        pop_all=pop_all,
    )

    # Write output (CLI responsibility)
    result.to_json_file()
    typer.echo("Updated supercell_info.json")


@app.command(name="defect_structure_info", help="Analyze defect structure.")
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
        1.0, "-dt", "--dist_tolerance",
        help="Distance tolerance in Angstrom."
    ),
    symprec: float = typer.Option(
        0.1, "--symprec",
        help="Symmetry precision for spglib."
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
            # Load files (CLI responsibility)
            calc_results = loadfn(_dir / "calc_results.json")
            defect_entry = loadfn(_dir / "defect_entry.json")

            # Call API (pure logic)
            info = api.make_defect_structure_info(
                perfect_structure=supercell_info.structure,
                initial_defect_structure=defect_entry.structure,
                final_defect_structure=calc_results.structure,
                dist_tol=dist_tolerance,
                symprec=symprec,
            )

            # Write output (CLI responsibility)
            info.to_json_file(str(_dir / file_name))
            typer.echo(f"  {_dir}: Created {file_name}")

        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


@app.command(name="defect_energy_infos", help="Calculate defect energy information.")
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
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Calculate defect energy information for multiple directories."""
    from pydefect.analysis.chemical_potential.chem_pot_diag import StandardEnergies
    from pydefect.analysis.corrections.no_correction import NoCorrection

    # Load common files (CLI responsibility)
    unitcell_obj = loadfn(str(unitcell))
    pcr = loadfn(str(perfect_calc_results))
    std = StandardEnergies.from_yaml(str(std_energies))
    file_name = "defect_energy_info.yaml"

    for _dir in dirs:
        try:
            # Load files (CLI responsibility)
            calc_results = loadfn(_dir / "calc_results.json")
            defect_entry = loadfn(_dir / "defect_entry.json")

            try:
                correction = loadfn(_dir / "correction.json")
            except FileNotFoundError:
                correction = NoCorrection()

            # Call API (pure logic)
            info = api.make_defect_energy_info(
                defect_entry=defect_entry,
                calc_results=calc_results,
                correction=correction,
                perfect_calc_results=pcr,
                unitcell=unitcell_obj,
                standard_energies=std,
            )

            # Write output (CLI responsibility)
            info.to_yaml_file(str(_dir / file_name))
            typer.echo(f"  {_dir}: Created {file_name}")

        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


@app.command(name="defect_energy_summary", help="Create defect energy summary.")
def defect_energy_summary(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect_energy_info.yaml."
    ),
    unitcell: Path = typer.Option(
        ..., "-u", "--unitcell",
        help="Path to unitcell.yaml."
    ),
    perfect_calc_results: Path = typer.Option(
        ..., "-pcr", "--perfect_calc_results",
        help="Path to perfect calc_results.json."
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
    from pydefect.analysis.chemical_potential.chem_pot_diag import TargetVertices

    # Load common files (CLI responsibility)
    unitcell_obj = loadfn(str(unitcell))
    pcr = loadfn(str(perfect_calc_results))
    target_vertices = TargetVertices.from_yaml(str(target_vertices_yaml))
    infos = []

    for _dir in dirs:
        try:
            # Load files (CLI responsibility)
            energy_info = loadfn(_dir / "defect_energy_info.yaml")
            str_info = loadfn(_dir / "defect_structure_info.json")
            infos.append((energy_info, str_info))
        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    # Call API (pure logic)
    summary = api.make_defect_energy_summary(
        defect_energy_infos=infos,
        target_vertices=target_vertices,
        unitcell=unitcell_obj,
        perfect_calc_results=pcr,
    )

    # Write output (CLI responsibility)
    summary.to_json_file()
    typer.echo("Created defect_energy_summary.json")


@app.command(name="plot_defect_energy", help="Plot defect formation energy.")
def plot_defect_energy(
    defect_energy_summary_path: Path = typer.Option(
        ..., "-d", "--defect_energy_summary",
        help="defect_energy_summary.json file."
    ),
    label: Optional[str] = typer.Option(
        None, "-l", "--label",
        help="Label for this chemical potential condition."
    ),
    y_range: Optional[List[float]] = typer.Option(
        None, "--y_range",
        help="Y-axis range (min max)."
    ),
    filtering_words: Optional[List[str]] = typer.Option(
        None, "--filtering_words",
        help="Words to filter defects."
    ),
    except_filtering_words: Optional[List[str]] = typer.Option(
        None, "--except_filtering_words",
        help="Words to exclude from filter."
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
    # Load file (CLI responsibility)
    summary = loadfn(str(defect_energy_summary_path))

    # Call API (pure logic)
    api.plot_defect_energy(
        summary,
        label=label,
        y_range=list(y_range) if y_range else None,
        filtering_words=list(filtering_words) if filtering_words else None,
        except_filtering_words=list(except_filtering_words) if except_filtering_words else None,
        add_charges=not no_add_charges,
        plot_all_energies=plot_all_energies,
    )
    typer.echo("Created defect_formation_energy.pdf")
