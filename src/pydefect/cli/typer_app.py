# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Typer-based CLI for pydefect.

This module provides the main Typer application and command groups.

Example:
    $ pydefect --help
    $ pydefect supercell -p POSCAR --min_atoms 50
"""

import typer
from pydefect import __version__

# Main app
app = typer.Typer(
    name="pydefect",
    help="pydefect: A package for first-principles point defect calculations with VASP.",
    add_completion=False,
)

# Sub-apps for command groups
util_app = typer.Typer(help="Utility commands")

app.add_typer(util_app, name="util")


def version_callback(value: bool):
    if value:
        typer.echo(f"pydefect version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit."
    ),
):
    """pydefect: A package for first-principles point defect calculations."""
    pass


def typer_main():
    """Entry point for Typer CLI."""
    # Import commands here to avoid circular imports
    # Domain-based CLI modules
    from pydefect.cli import supercell  # noqa: F401
    from pydefect.cli import unitcell  # noqa: F401
    from pydefect.cli import defect  # noqa: F401
    from pydefect.cli import chemical_potential  # noqa: F401
    from pydefect.cli import band_edge  # noqa: F401
    from pydefect.cli import calculation  # noqa: F401
    from pydefect.cli import corrections  # noqa: F401
    from pydefect.cli import util  # noqa: F401
    app()


if __name__ == "__main__":
    typer_main()
