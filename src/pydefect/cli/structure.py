# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Structure-related Typer commands.

Commands for creating supercells, defect sets, and managing interstitials.

Example:
    $ pydefect supercell -p POSCAR --min_atoms 50
    $ pydefect defect_set -d Al
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from pymatgen.core import IStructure, Structure

from pydefect.cli.typer_app import app
from pydefect import api


# Callback for --oxi_states to parse "Mg 2 O -2" format
def parse_oxi_states(values: Optional[List[str]]) -> Optional[dict]:
    if not values:
        return None
    result = {}
    for i in range(0, len(values), 2):
        result[values[i]] = int(values[i + 1])
    return result


@app.command(name="supercell", help="Make supercell and SPOSCAR file.")
def supercell(
    unitcell: Path = typer.Option(
        ..., "-p", "--unitcell",
        help="Base structure file (standardized primitive cell)."
    ),
    matrix: Optional[List[int]] = typer.Option(
        None, "--matrix",
        help="Supercell matrix (1, 3, or 9 integers)."
    ),
    min_atoms: int = typer.Option(
        50, "--min_atoms",
        help="Minimum number of atoms."
    ),
    max_atoms: int = typer.Option(
        300, "--max_atoms",
        help="Maximum number of atoms."
    ),
    no_symmetry_analysis: bool = typer.Option(
        False, "--no_symmetry_analysis",
        help="Disable symmetry analysis (requires sites.yaml)."
    ),
    sites_yaml: Optional[Path] = typer.Option(
        None, "-s", "--sites_yaml_filename",
        help="sites.yaml for manual site specification."
    ),
):
    """Create supercell from unitcell structure."""
    from pydefect.cli.main_tools import sanitize_matrix

    # Load file (CLI responsibility)
    structure = IStructure.from_file(str(unitcell))
    matrix_sanitized = sanitize_matrix(matrix) if matrix else None

    # Call API (pure logic)
    supercell_info, supercell_structure = api.make_supercell(
        unitcell=structure,
        matrix=matrix_sanitized,
        min_num_atoms=min_atoms,
        max_num_atoms=max_atoms,
        analyze_symmetry=not no_symmetry_analysis,
        sites_yaml_filename=str(sites_yaml) if sites_yaml else None,
    )

    # Write output (CLI responsibility)
    supercell_structure.to(filename="SPOSCAR")
    supercell_info.to_json_file()
    typer.echo("Created SPOSCAR and supercell_info.json")


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


@app.command(name="pop", help="Remove interstitial from supercell_info.")
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
    from vise.util.logger import get_logger
    logger = get_logger(__name__)

    # Load file (CLI responsibility)
    supercell_info = loadfn(str(supercell_info_path))
    logger.info("Be careful that the interstitials indices are changed.")

    # Call API (pure logic)
    result = api.pop_interstitial(
        supercell_info=supercell_info,
        index=index,
        pop_all=pop_all,
    )

    # Write output (CLI responsibility)
    result.to_json_file()
    typer.echo("Updated supercell_info.json")
