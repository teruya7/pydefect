# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Supercell-related CLI commands."""

from pathlib import Path
from typing import List, Optional

import typer
from pymatgen.core import IStructure

from pydefect import api


def supercell(
    app: typer.Typer,
    unitcell: Path,
    matrix: Optional[List[int]],
    min_atoms: int,
    max_atoms: int,
    no_symmetry_analysis: bool,
    sites_yaml: Optional[Path],
):
    """Create supercell from unitcell structure."""
    from pydefect.cli.main_tools import sanitize_matrix

    structure = IStructure.from_file(str(unitcell))
    matrix_sanitized = sanitize_matrix(matrix) if matrix else None

    supercell_info, supercell_structure = api.make_supercell(
        unitcell=structure,
        matrix=matrix_sanitized,
        min_num_atoms=min_atoms,
        max_num_atoms=max_atoms,
        analyze_symmetry=not no_symmetry_analysis,
        sites_yaml_filename=str(sites_yaml) if sites_yaml else None,
    )

    supercell_structure.to(filename="SPOSCAR")
    supercell_info.to_json_file()
    typer.echo("Created SPOSCAR and supercell_info.json")


def register_commands(app: typer.Typer):
    """Register supercell commands to the app."""

    @app.command(name="s", help="Make supercell and SPOSCAR file.")
    def _supercell(
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
        supercell(app, unitcell, matrix, min_atoms, max_atoms,
                  no_symmetry_analysis, sites_yaml)
