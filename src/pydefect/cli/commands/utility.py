# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Utility CLI commands (print, defect_vesta, u_values, pinning_levels, etc.)."""

from pathlib import Path
from typing import List, Optional

import typer
from monty.serialization import loadfn
from pymatgen.core import Structure
from pymatgen.io.vasp import Chgcar, Vasprun, Outcar
from vise.util.logger import get_logger

from pydefect import api
from pydefect.defaults import defaults

logger = get_logger(__name__)


def register_util_commands(app: typer.Typer):
    """Register utility commands."""

    @app.command(name="print", help="Print JSON/YAML file contents.")
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
        for filepath in files:
            typer.echo("-" * 80)
            typer.echo(f"file: {filepath}")
            obj = loadfn(str(filepath))
            if use_repr:
                typer.echo(obj.__repr__())
            else:
                typer.echo(obj.__str__())

    @app.command(name="dvf", help="Create VESTA file for defect visualization.")
    def defect_vesta_file(
        dirs: List[Path] = typer.Option(
            ..., "-d", "--dirs",
            help="Directories with defect_structure_info.json."
        ),
        cutoff: float = typer.Option(
            defaults.show_structure_cutoff, "--cutoff",
            help="Cutoff radius for atoms shown."
        ),
        min_displace_w_arrows: float = typer.Option(
            0.1, "--min_displace_w_arrows",
            help="Minimum displacement for arrows."
        ),
        arrow_factor: float = typer.Option(
            3.0, "--arrow_factor",
            help="Scaling factor for arrows."
        ),
        title: Optional[str] = typer.Option(
            None, "--title",
            help="Title in VESTA files."
        ),
        verbose: bool = typer.Option(
            False, "-v", "--verbose",
            help="Show traceback on errors."
        ),
    ):
        """Create VESTA visualization files for defect structures."""
        for _dir in dirs:
            try:
                dsi = loadfn(_dir / "defect_structure_info.json")
                
                api.make_defect_vesta_file(
                    defect_structure_info=dsi,
                    output_dir=_dir,
                    cutoff=cutoff,
                    min_displace_w_arrows=min_displace_w_arrows,
                    arrow_factor=arrow_factor,
                    title=title,
                )
                typer.echo(f"  {_dir}: Created VESTA file")

            except Exception as e:
                if verbose:
                    raise
                logger.warning(f"  {_dir}: {e}")

        typer.echo("Done.")

    @app.command(name="u", help="Show U values from defect energies.")
    def show_u_values(
        defect_energy_summary: Path = typer.Option(
            ..., "-d", "--defect_energy_summary",
            help="Path to defect_energy_summary.json."
        ),
        label: str = typer.Option(
            ..., "-l", "--label",
            help="Label in chemical potential diagram."
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
        summary = loadfn(str(defect_energy_summary))
        u_values = api.get_u_values(
            summary, label,
            with_corrections=with_corrections,
            allow_shallow=allow_shallow,
        )
        for name, u_val in u_values.items():
            typer.echo(f"{name}: {u_val:.3f} eV")

    @app.command(name="pl", help="Show pinning levels.")
    def show_pinning_levels(
        defect_energy_summary: Path = typer.Option(
            ..., "-d", "--defect_energy_summary",
            help="Path to defect_energy_summary.json."
        ),
        label: str = typer.Option(
            ..., "-l", "--label",
            help="Label in chemical potential diagram."
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
        summary = loadfn(str(defect_energy_summary))
        pinning = api.get_pinning_levels(
            summary, label,
            with_corrections=with_corrections,
            allow_shallow=allow_shallow,
        )
        typer.echo(f"Pinning levels: {pinning}")

    @app.command(name="ai", help="Add interstitials from local extrema.")
    def add_interstitials_from_local_extrema(
        local_extrema: Path = typer.Option(
            ..., "--local_extrema",
            help="volumetric_data_local_extrema.json file."
        ),
        supercell_info: Path = typer.Option(
            "supercell_info.json", "-s", "--supercell_info",
            help="Path to supercell_info.json."
        ),
        indices: List[int] = typer.Option(
            ..., "-i", "--indices",
            help="Indices of interstitial sites to add (1-based)."
        ),
    ):
        """Add interstitials via volumetric_data_local_extrema.json file."""
        extrema = loadfn(str(local_extrema))
        si = loadfn(str(supercell_info))

        result = api.add_interstitials_from_local_extrema(
            supercell_info=si,
            local_extrema=extrema,
            indices=list(indices),
        )
        result.to_json_file()
        typer.echo("Updated supercell_info.json")

    @app.command(name="cefm", help="Get composition energies from Materials Project.")
    def composition_energies_from_mp(
        elements: List[str] = typer.Option(
            ..., "-e", "--elements",
            help="Element symbols to query."
        ),
        atom_energy_yaml: Optional[Path] = typer.Option(
            None, "-a", "--atom_energy_yaml",
            help="Path to atom energy YAML for energy alignment."
        ),
    ):
        """Fetch composition energies from Materials Project."""
        from pydefect.api.materials_project import make_composition_energies_from_mp

        comp_energies = make_composition_energies_from_mp(
            elements=list(elements),
            atom_energy_yaml=str(atom_energy_yaml) if atom_energy_yaml else None,
        )
        comp_energies.to_yaml_file()
        typer.echo("Created composition_energies.yaml")


def register_vasp_util_commands(app: typer.Typer):
    """Register VASP utility commands (ccs, de, pd, rdp, cg, cdc, mtd)."""
    from pydefect.analysis.corrections.models import Grids

    @app.command(name="ccs", help="Calculate charge state from VASP files.")
    def calc_charge_state(
        dir_path: Path = typer.Option(
            ..., "-d", "--dir",
            help="Directory with POSCAR, POTCAR, INCAR."
        ),
    ):
        """Calculate defect charge states from INCAR, POSCAR and POTCAR."""
        charge = api.calc_charge_state_from_vasp(dir_path)
        typer.echo(f"Charge state: {charge}")

    @app.command(name="de", help="Make defect entry from VASP files.")
    def make_defect_entry(
        dir_path: Path = typer.Option(
            ..., "-d", "--dir",
            help="Directory with POSCAR, POTCAR, INCAR."
        ),
        name: str = typer.Option(
            ..., "-n", "--name",
            help="Name used for plotting energy diagram."
        ),
        perfect: Path = typer.Option(
            ..., "-p", "--perfect",
            help="Perfect supercell POSCAR file."
        ),
    ):
        """Make defect entry from INCAR, POSCAR and POTCAR."""
        perfect_structure = Structure.from_file(str(perfect))
        
        defect_entry = api.make_defect_entry_from_vasp(
            dir_path=dir_path,
            name=name,
            perfect_structure=perfect_structure,
        )
        
        defect_entry.to_json_file(str(dir_path / "defect_entry.json"))
        typer.echo(f"Created {dir_path}/defect_entry.json")

    @app.command(name="pd", help="Create PARCHG directory for band decomposition.")
    def parchg_dir(
        dir_path: Path = typer.Option(
            ..., "-d", "--dir",
            help="Directory with WAVECAR."
        ),
        ibands: Optional[List[int]] = typer.Option(
            None, "-i", "--ibands",
            help="Band indices (1-based)."
        ),
    ):
        """Create parchg directory with VASP files for PARCHG generation."""
        api.make_parchg_dir(
            dir_path=dir_path,
            ibands=list(ibands) if ibands else None,
        )
        typer.echo(f"Created parchg directory in {dir_path}")

    @app.command(name="rdp", help="Refine defect POSCAR around anchor atom.")
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
            ..., "-n", "--poscar_name",
            help="Output filename."
        ),
    ):
        """Refine defect structure POSCAR."""
        structure = Structure.from_file(str(poscar))
        de = loadfn(str(defect_entry))

        refined = api.refine_defect_poscar(
            structure=structure,
            defect_entry=de,
        )

        refined.to(filename=output)
        typer.echo(f"Created {output}")

    @app.command(name="cg", help="Calculate grids from CHGCAR.")
    def calc_grids(
        chgcar: Path = typer.Option(
            ..., "-c", "--chgcar",
            help="Path to CHGCAR file."
        ),
    ):
        """Calculate grids from CHGCAR for correction."""
        chg = Chgcar.from_file(str(chgcar))
        grids = api.calc_grids(chg)
        grids.to_json_file()
        typer.echo("Created grids.json")

    @app.command(name="cdc", help="Calculate defect charge info from PARCHG.")
    def calc_defect_charge_info(
        parchgs: List[Path] = typer.Option(
            ..., "-p", "--parchgs",
            help="PARCHG files."
        ),
        grids: Path = typer.Option(
            ..., "-g", "--grids",
            help="Path to grids.json."
        ),
        bin_interval: float = typer.Option(
            0.2, "-b", "--bin_interval",
            help="Bin interval."
        ),
    ):
        """Calculate defect charge distribution from PARCHG files."""
        parchg_list = [Chgcar.from_file(str(p)) for p in parchgs]
        grids_obj = Grids.from_file(str(grids))

        info = api.calc_defect_charge_info(
            parchgs=parchg_list,
            grids=grids_obj,
            bin_interval=bin_interval,
        )
        info.to_json_file()
        typer.echo("Created defect_charge_info.json")

    @app.command(name="mtd", help="Make total DOS from vasprun.xml.")
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
        """Make total_dos.json for defect and carrier density calculations."""
        vr = Vasprun(str(vasprun), parse_potcar_file=False)
        oc = Outcar(str(outcar))

        dos = api.make_total_dos(vr, oc)
        dos.to_json_file()
        typer.echo("Created total_dos.json")
