# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for supercell CLI commands."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.main import app


runner = CliRunner()


class TestSupercellCommand:
    """Tests for the 's' supercell command."""

    def test_supercell_help(self):
        """Test that supercell --help works."""
        result = runner.invoke(app, ["s", "--help"])
        assert result.exit_code == 0
        assert "Make supercell" in result.stdout

    def test_supercell_requires_unitcell(self):
        """Test that supercell requires --unitcell option."""
        result = runner.invoke(app, ["s"])
        assert result.exit_code != 0

    def test_supercell_shows_options(self):
        """Test that supercell shows expected options."""
        result = runner.invoke(app, ["s", "--help"])
        assert "--unitcell" in result.stdout or "-p" in result.stdout
        assert "--min_atoms" in result.stdout
        assert "--max_atoms" in result.stdout
