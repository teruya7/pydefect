# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for band edge CLI commands (bes)."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.main import app


runner = CliRunner()


class TestBandEdgeStates:
    """Tests for the 'bes' command."""

    def test_bes_help(self):
        """Test that bes --help works."""
        result = runner.invoke(app, ["bes", "--help"])
        assert result.exit_code == 0
        assert "band" in result.stdout.lower() or "edge" in result.stdout.lower()

    def test_bes_shows_options(self):
        """Test that bes shows expected options."""
        result = runner.invoke(app, ["bes", "--help"])
        assert "--dirs" in result.stdout or "-d" in result.stdout
        assert "--p_state" in result.stdout or "-pbes" in result.stdout
