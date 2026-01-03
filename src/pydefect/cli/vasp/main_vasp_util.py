# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""pydefect_vasp_util CLI entry point - Typer-based.

This module provides VASP utility commands.

Commands:
    ccs, de, pd, rdp, cg, cdc, mtd

Example:
    $ pydefect_vasp_util --help
    $ pydefect_vasp_util ccs -d Va_O1_0
"""

import typer
from pydefect import __version__

# pydefect_vasp_util app
app = typer.Typer(
    name="pydefect_vasp_util",
    help="pydefect VASP utility commands.",
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
    """pydefect_vasp_util: VASP utility commands."""
    pass


def _register_commands():
    """Register all VASP utility commands from the commands directory."""
    from pydefect.cli.commands import utility

    utility.register_vasp_util_commands(app)


# Register commands at import time
_register_commands()


def main():
    """Entry point for pydefect_vasp_util CLI."""
    app()


if __name__ == "__main__":
    main()

