# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""pydefect_vasp CLI entry point - Typer-based.

This module provides VASP-specific CLI commands.

Commands:
    u, mp, mce, le, de, cr, pbes, beoi

Example:
    $ pydefect_vasp --help
    $ pydefect_vasp u -vb vasprun.xml -ob OUTCAR -odc OUTCAR -odi OUTCAR
"""

import typer
from pydefect import __version__

# pydefect_vasp app
app = typer.Typer(
    name="pydefect_vasp",
    help="pydefect VASP-specific commands for creating and analyzing VASP input/output.",
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
    """pydefect_vasp: VASP-specific commands."""
    pass


def _register_commands():
    """Register all VASP commands from the commands directory."""
    from pydefect.cli.commands import unitcell
    from pydefect.cli.commands import interstitial
    from pydefect.cli.commands import defect
    from pydefect.cli.commands import band_edge

    unitcell.register_vasp_commands(app)
    interstitial.register_vasp_commands(app)
    defect.register_vasp_commands(app)
    band_edge.register_vasp_commands(app)


# Register commands at import time
_register_commands()


def main():
    """Entry point for pydefect_vasp CLI."""
    app()


if __name__ == "__main__":
    main()

