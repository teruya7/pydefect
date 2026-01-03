# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Utility Typer commands.

Commands for printing JSON/YAML files and creating VESTA files.

Example:
    $ pydefect util print calc_results.json
    $ pydefect util defect_vesta -d Va_O1_0
"""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from vise.util.logger import get_logger

from pydefect.cli.typer_app import app, util_app
from pydefect import api

logger = get_logger(__name__)


@util_app.command(name="print", help="Print JSON/YAML file contents.")
def print_json(
    files: List[Path] = typer.Argument(
        ...,
        help="JSON or YAML files to print."
    ),
    use_repr: bool = typer.Option(
        False, "--repr", "-r",
        help="Use __repr__ instead of __str__."
    ),
):
    """Print contents of JSON/YAML files."""
    for filename in files:
        typer.echo("-" * 80)
        typer.echo(f"file: {filename}")
        # Use API layer
        content = api.print_json(str(filename), use_repr=use_repr)
        typer.echo(content)


@util_app.command(name="defect_vesta", help="Create VESTA files for defect visualization.")
def defect_vesta(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect_structure_info.json."
    ),
    cutoff: float = typer.Option(
        5.0, "-c", "--cutoff",
        help="Cutoff distance for showing atoms."
    ),
    min_displace: float = typer.Option(
        0.1, "--min_displace",
        help="Minimum displacement to show arrows."
    ),
    arrow_factor: float = typer.Option(
        3.0, "--arrow_factor",
        help="Scaling factor for arrows."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Create VESTA visualization files for defect structures."""
    for _dir in dirs:
        try:
            # Load file (CLI responsibility)
            dsi = loadfn(_dir / "defect_structure_info.json")
            defect_entry = loadfn(_dir / "defect_entry.json")
            title = defect_entry.name

            # Call API (pure logic)
            vesta = api.make_defect_vesta_file(
                defect_structure_info=dsi,
                cutoff=cutoff,
                min_displace_w_arrows=min_displace,
                arrow_factor=arrow_factor,
                title=title,
            )

            # Write output (CLI responsibility)
            vesta.initial_vesta.write_file(str(_dir / "initial.vesta"))
            vesta.final_vesta.write_file(str(_dir / "final.vesta"))
            typer.echo(f"  {_dir}: Created initial.vesta and final.vesta")

        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    typer.echo("Done.")


# --- pydefect_util commands ---

@util_app.command(name="u_values", help="Show U values from defect energies.")
def show_u_values(
    defect_energy_summary: Path = typer.Option(
        ..., "-d", "--defect_energy_summary",
        help="Path to defect_energy_summary.json."
    ),
    with_corrections: bool = typer.Option(
        True, "--with_corrections/--no_corrections",
        help="Include corrections."
    ),
    allow_shallow: bool = typer.Option(
        False, "--allow_shallow",
        help="Allow shallow defects."
    ),
):
    """Show U values from defect energy summary."""
    from pydefect.analysis.formation_energy.u_values import u_values_from_defect_energies
    from tabulate import tabulate

    des = loadfn(str(defect_energy_summary))
    u_values = u_values_from_defect_energies(
        des.defect_energies, with_corrections, allow_shallow
    )
    result = []
    for name, u_vas in u_values.items():
        for charges, u_val in u_vas.items():
            result.append([name, charges, u_val])
    if result:
        logger.info("The U values are as follows:")
        print(tabulate(result))
    else:
        logger.info("No U values are obtained.")


@util_app.command(name="pinning_levels", help="Show pinning levels.")
def show_pinning_levels(
    defect_energy_summary: Path = typer.Option(
        ..., "-d", "--defect_energy_summary",
        help="Path to defect_energy_summary.json."
    ),
    label: str = typer.Option(
        ..., "-l", "--label",
        help="Chemical potential label."
    ),
    with_corrections: bool = typer.Option(
        True, "--with_corrections/--no_corrections",
        help="Include corrections."
    ),
    allow_shallow: bool = typer.Option(
        False, "--allow_shallow",
        help="Allow shallow defects."
    ),
):
    """Show pinning levels from defect energy summary."""
    from pydefect.analysis.formation_energy.pinning_levels import pinning_levels_from_charge_energies

    des = loadfn(str(defect_energy_summary))
    charge_energies = des.charge_energies(
        label, allow_shallow, with_corrections, (0.0, des.cbm)
    )
    print(pinning_levels_from_charge_energies(charge_energies))


@util_app.command(name="add_interstitials", help="Add interstitials from local extrema.")
def add_interstitials_from_local_extrema(
    local_extrema: Path = typer.Option(
        "volumetric_data_local_extrema.json", "-l", "--local_extrema",
        help="Path to local_extrema.json."
    ),
    supercell_info: Path = typer.Option(
        "supercell_info.json", "-s", "--supercell_info",
        help="Path to supercell_info.json."
    ),
    indices: List[int] = typer.Option(
        ..., "-i", "--indices",
        help="Indices of interstitial sites to add."
    ),
):
    """Add interstitials from local extrema to supercell_info."""
    le = loadfn(str(local_extrema))
    si = loadfn(str(supercell_info))
    result = le.append_sites_to_supercell_info(si, list(indices))
    result.to_json_file()
    typer.echo("Updated supercell_info.json")


@util_app.command(name="degeneracies", help="Make degeneracies from defect calculations.")
def make_degeneracies(
    dirs: List[Path] = typer.Option(
        ..., "-d", "--dirs",
        help="Directories with defect calculations."
    ),
    supercell_info: Path = typer.Option(
        "supercell_info.json", "-s", "--supercell_info",
        help="Path to supercell_info.json."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose",
        help="Show traceback on errors."
    ),
):
    """Make degeneracies.yaml from defect calculations."""
    from pydefect.analysis.concentration.degeneracy import MakeDegeneracy

    si = loadfn(str(supercell_info))
    make_deg = MakeDegeneracy(si.space_group)

    for _dir in dirs:
        try:
            energy_info = loadfn(_dir / "defect_energy_info.yaml")
            calc_results = loadfn(_dir / "calc_results.json")
            defect_str_info = loadfn(_dir / "defect_structure_info.json")
            make_deg.add_degeneracy(energy_info, calc_results, defect_str_info)
        except Exception as e:
            if verbose:
                raise
            logger.warning(f"  {_dir}: {e}")

    make_deg.degeneracies.to_yaml_file()
    typer.echo("Created degeneracies.yaml")


# --- pydefect_vasp_util commands ---

@util_app.command(name="charge_state", help="Calculate charge state from VASP files.")
def calc_charge_state(
    dir: Path = typer.Option(
        ".", "-d", "--dir",
        help="Directory with POSCAR, POTCAR, INCAR."
    ),
):
    """Calculate charge state from VASP input files."""
    from pydefect.preparation.defect.vasp_utils import calculate_charge_state
    from pymatgen.io.vasp.inputs import Poscar, Potcar, Incar

    poscar = Poscar.from_file(dir / "POSCAR")
    potcar = Potcar.from_file(dir / "POTCAR")
    incar = Incar.from_file(dir / "INCAR")

    charge_state = calculate_charge_state(poscar, potcar, incar)
    typer.echo(f"Charge state: {charge_state}")


@util_app.command(name="refine_poscar", help="Refine defect POSCAR around anchor atom.")
def refine_defect_poscar(
    poscar: Path = typer.Option(
        ..., "-p", "--poscar",
        help="Path to POSCAR/CONTCAR to refine."
    ),
    defect_entry: Path = typer.Option(
        ..., "-d", "--defect_entry",
        help="Path to defect_entry.json."
    ),
    output: str = typer.Option(
        "POSCAR_refined", "-n", "--output",
        help="Output filename."
    ),
):
    """Refine defect structure around anchor atom."""
    from pydefect.analysis.structure.refine import refine_defect_structure
    from pymatgen.core import Structure

    structure = Structure.from_file(str(poscar))
    de = loadfn(str(defect_entry))

    result = refine_defect_structure(
        structure, de.anchor_atom_index, de.anchor_atom_coords
    )
    if result:
        result.to(filename=output)
        typer.echo(f"Created {output}")
    else:
        typer.echo("No refinement needed.")


@util_app.command(name="grids", help="Calculate grids from CHGCAR.")
def calc_grids(
    chgcar: Path = typer.Option(
        "CHGCAR", "-c", "--chgcar",
        help="Path to CHGCAR file."
    ),
):
    """Calculate grids from CHGCAR for correction."""
    from pydefect.analysis.corrections.models import Grids
    from pymatgen.io.vasp import Chgcar

    chg = Chgcar.from_file(str(chgcar))
    grids = Grids.from_chgcar(chg)
    grids.dump()
    typer.echo("Created grids.json")


@util_app.command(name="total_dos", help="Make total DOS from vasprun.xml.")
def make_total_dos(
    vasprun: Path = typer.Option(
        ..., "-v", "--vasprun",
        help="Path to vasprun.xml."
    ),
    outcar: Path = typer.Option(
        ..., "-o", "--outcar",
        help="Path to OUTCAR."
    ),
):
    """Make total_dos.json for concentration calculations."""
    from pydefect.analysis.concentration.make_concentration import TotalDos
    from pymatgen.io.vasp import Vasprun, Outcar
    from pymatgen.electronic_structure.core import Spin
    from vise.analyzer.vasp.band_edge_properties import VaspBandEdgeProperties

    vr = Vasprun(str(vasprun))
    oc = Outcar(str(outcar))

    if Spin.down in vr.complete_dos.densities:
        raise ValueError("Spin polarization is not supported yet.")

    band_edge = VaspBandEdgeProperties(vr, oc)
    vbm, cbm = band_edge.vbm_info.energy, band_edge.cbm_info.energy

    total_dos = TotalDos(
        vr.complete_dos.energies.tolist(),
        vr.complete_dos.densities[Spin.up].tolist(),
        vr.structures[0].volume,
        vbm, cbm
    )
    total_dos.to_json_file()
    typer.echo("Created total_dos.json")

