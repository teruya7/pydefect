# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for unitcell VASP CLI commands (u, cr, mce, mp)."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.vasp.main_vasp import app


runner = CliRunner()


class TestUnitcellCommand:
    """Tests for the 'u' unitcell command."""

    def test_u_help(self):
        """Test that u --help works."""
        result = runner.invoke(app, ["u", "--help"])
        assert result.exit_code == 0
        assert "unitcell" in result.stdout.lower() or "vasp" in result.stdout.lower()

    def test_u_shows_options(self):
        """Test that u shows expected options."""
        result = runner.invoke(app, ["u", "--help"])
        assert "--vasprun_band" in result.stdout or "-vb" in result.stdout
        assert "--outcar_band" in result.stdout or "-ob" in result.stdout


class TestCalcResultsCommand:
    """Tests for the 'cr' calc_results command."""

    def test_cr_help(self):
        """Test that cr --help works."""
        result = runner.invoke(app, ["cr", "--help"])
        assert result.exit_code == 0
        assert "calc" in result.stdout.lower() or "results" in result.stdout.lower()


class TestMakeCompositionEnergies:
    """Tests for the 'mce' command."""

    def test_mce_help(self):
        """Test that mce --help works."""
        result = runner.invoke(app, ["mce", "--help"])
        assert result.exit_code == 0
        assert "composition" in result.stdout.lower() or "energies" in result.stdout.lower()


class TestMakePoscars:
    """Tests for the 'mp' command."""

    def test_mp_help(self):
        """Test that mp --help works."""
        result = runner.invoke(app, ["mp", "--help"])
        assert result.exit_code == 0
        assert "materials" in result.stdout.lower() or "project" in result.stdout.lower()


class TestLocalExtrema:
    """Tests for the 'le' command."""

    def test_le_help(self):
        """Test that le --help works."""
        result = runner.invoke(app, ["le", "--help"])
        assert result.exit_code == 0
        assert "extrema" in result.stdout.lower() or "volumetric" in result.stdout.lower()


class TestDefectEntries:
    """Tests for the 'de' command."""

    def test_de_help(self):
        """Test that de --help works."""
        result = runner.invoke(app, ["de", "--help"])
        assert result.exit_code == 0
        assert "defect" in result.stdout.lower() or "entr" in result.stdout.lower()


class TestPerfectBandEdgeState:
    """Tests for the 'pbes' command."""

    def test_pbes_help(self):
        """Test that pbes --help works."""
        result = runner.invoke(app, ["pbes", "--help"])
        assert result.exit_code == 0
        assert "band" in result.stdout.lower() or "perfect" in result.stdout.lower()


class TestBandEdgeOrbitalInfos:
    """Tests for the 'beoi' command."""

    def test_beoi_help(self):
        """Test that beoi --help works."""
        result = runner.invoke(app, ["beoi", "--help"])
        assert result.exit_code == 0
        assert "orbital" in result.stdout.lower() or "band" in result.stdout.lower()
