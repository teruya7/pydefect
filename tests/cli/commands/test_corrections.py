# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for corrections CLI commands (efnv)."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.main import app


runner = CliRunner()


class TestEfnvCommand:
    """Tests for the 'efnv' command."""

    def test_efnv_help(self):
        """Test that efnv --help works."""
        result = runner.invoke(app, ["efnv", "--help"])
        assert result.exit_code == 0
        assert "correction" in result.stdout.lower() or "fnv" in result.stdout.lower()

    def test_efnv_shows_options(self):
        """Test that efnv shows expected options."""
        result = runner.invoke(app, ["efnv", "--help"])
        assert "--dirs" in result.stdout or "-d" in result.stdout
        assert "--perfect_calc_results" in result.stdout or "-pcr" in result.stdout
        assert "--unitcell" in result.stdout or "-u" in result.stdout
