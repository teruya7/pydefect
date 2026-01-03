# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for chemical potential CLI commands (sre, cv, pc)."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.main import app


runner = CliRunner()


class TestStandardAndRelativeEnergies:
    """Tests for the 'sre' command."""

    def test_sre_help(self):
        """Test that sre --help works."""
        result = runner.invoke(app, ["sre", "--help"])
        assert result.exit_code == 0
        assert "energies" in result.stdout.lower()

    def test_sre_shows_options(self):
        """Test that sre shows expected options."""
        result = runner.invoke(app, ["sre", "--help"])
        assert "--composition_energies_yaml" in result.stdout or "-y" in result.stdout


class TestCpdAndVertices:
    """Tests for the 'cv' command."""

    def test_cv_help(self):
        """Test that cv --help works."""
        result = runner.invoke(app, ["cv", "--help"])
        assert result.exit_code == 0
        assert "diagram" in result.stdout.lower() or "chemical" in result.stdout.lower()

    def test_cv_shows_options(self):
        """Test that cv shows expected options."""
        result = runner.invoke(app, ["cv", "--help"])
        assert "--rel_energy_yaml" in result.stdout or "-y" in result.stdout


class TestPlotCpd:
    """Tests for the 'pc' command."""

    def test_pc_help(self):
        """Test that pc --help works."""
        result = runner.invoke(app, ["pc", "--help"])
        assert result.exit_code == 0
        assert "plot" in result.stdout.lower() or "diagram" in result.stdout.lower()

    def test_pc_shows_options(self):
        """Test that pc shows expected options."""
        result = runner.invoke(app, ["pc", "--help"])
        assert "--chem_pot_diag" in result.stdout or "-cpd" in result.stdout
