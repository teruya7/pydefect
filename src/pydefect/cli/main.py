# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Main pydefect CLI entry point - Typer-based.

This module provides the main CLI commands for pydefect.

Commands:
    s, sre, cv, pc, ai, pi, ds, dsi, efnv, bes, dei, des, cs, pe

Example:
    $ pydefect --help
    $ pydefect s -p POSCAR --min_atoms 50
"""

import typer
from pydefect import __version__

# Main pydefect app
app = typer.Typer(
    name="pydefect",
    help="pydefect: A package for first-principles point defect calculations with VASP.",
    add_completion=False,
)


def version_callback(value: bool):
    if value:
        typer.echo(f"pydefect version: {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        None, "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit."
    ),
):
    """pydefect: A package for first-principles point defect calculations."""
    pass


def _register_commands():
    """Register all commands from the commands directory."""
    from pydefect.cli.commands import supercell
    from pydefect.cli.commands import chemical_potential
    from pydefect.cli.commands import interstitial
    from pydefect.cli.commands import defect
    from pydefect.cli.commands import corrections
    from pydefect.cli.commands import band_edge

    supercell.register_commands(app)
    chemical_potential.register_commands(app)
    interstitial.register_commands(app)
    defect.register_commands(app)
    corrections.register_commands(app)
    band_edge.register_commands(app)


# Register commands at import time
_register_commands()


def main():
    """Entry point for pydefect CLI."""
    app()


if __name__ == "__main__":
    main()

