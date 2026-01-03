# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Typer-based VASP CLI for pydefect.

This module provides the pydefect_vasp command for VASP-specific operations.

Example:
    $ pydefect_vasp --help
    $ pydefect_vasp mp -e Mg Al O --e_above_hull 0.0005
"""

import typer
from pydefect import __version__

# VASP-specific app
vasp_app = typer.Typer(
    name="pydefect_vasp",
    help="pydefect VASP: VASP-specific commands for pydefect.",
    add_completion=False,
)


def version_callback(value: bool):
    if value:
        typer.echo(f"pydefect version: {__version__}")
        raise typer.Exit()


@vasp_app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit."
    ),
):
    """pydefect_vasp: VASP-specific commands for pydefect."""
    pass


def vasp_main():
    """Entry point for pydefect_vasp CLI."""
    # Import commands here to avoid circular imports
    from pydefect.cli import materials_project  # noqa: F401
    vasp_app()


if __name__ == "__main__":
    vasp_main()
