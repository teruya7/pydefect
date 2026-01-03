# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""pydefect_util CLI entry point - Typer-based.

This module provides utility CLI commands.

Commands:
    cefm, u, pl, ai, dvf, gkfo, md, ccc, cdc, pcc, pdc, cccdc

Example:
    $ pydefect_util --help
    $ pydefect_util gkfo -iefnv correction.json -icr calc_results.json
"""

import typer
from pydefect import __version__

# pydefect_util app
app = typer.Typer(
    name="pydefect_util",
    help="pydefect utility commands.",
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
    """pydefect_util: Utility commands."""
    pass


def _register_commands():
    """Register all utility commands from the commands directory."""
    from pydefect.cli.commands import utility
    from pydefect.cli.commands import corrections
    from pydefect.cli.commands import concentration

    utility.register_util_commands(app)
    corrections.register_util_commands(app)
    concentration.register_util_commands(app)


# Register commands at import time
_register_commands()


def main():
    """Entry point for pydefect_util CLI."""
    app()


if __name__ == "__main__":
    main()

