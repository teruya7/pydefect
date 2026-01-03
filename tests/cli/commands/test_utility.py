# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for utility CLI commands."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.main_util import app as util_app
from pydefect.cli.vasp.main_vasp_util import app as vasp_util_app


util_runner = CliRunner()
vasp_util_runner = CliRunner()


# Utility commands tests

class TestPrintCommand:
    """Tests for the 'print' command."""

    def test_print_help(self):
        """Test that print --help works."""
        result = util_runner.invoke(util_app, ["print", "--help"])
        assert result.exit_code == 0
        assert "print" in result.stdout.lower() or "json" in result.stdout.lower()


class TestDefectVestaFile:
    """Tests for the 'dvf' command."""

    def test_dvf_help(self):
        """Test that dvf --help works."""
        result = util_runner.invoke(util_app, ["dvf", "--help"])
        assert result.exit_code == 0
        assert "vesta" in result.stdout.lower()


class TestShowUValues:
    """Tests for the 'u' command."""

    def test_u_help(self):
        """Test that u --help works."""
        result = util_runner.invoke(util_app, ["u", "--help"])
        assert result.exit_code == 0
        assert "u value" in result.stdout.lower() or "show" in result.stdout.lower()


class TestShowPinningLevels:
    """Tests for the 'pl' command."""

    def test_pl_help(self):
        """Test that pl --help works."""
        result = util_runner.invoke(util_app, ["pl", "--help"])
        assert result.exit_code == 0
        assert "pinning" in result.stdout.lower()


class TestAddInterstitialsFromLocalExtrema:
    """Tests for the 'ai' add interstitials command."""

    def test_ai_help(self):
        """Test that ai --help works."""
        result = util_runner.invoke(util_app, ["ai", "--help"])
        assert result.exit_code == 0
        assert "interstitial" in result.stdout.lower()


class TestCompositionEnergiesFromMp:
    """Tests for the 'cefm' command."""

    def test_cefm_help(self):
        """Test that cefm --help works."""
        result = util_runner.invoke(util_app, ["cefm", "--help"])
        assert result.exit_code == 0
        assert "composition" in result.stdout.lower() or "materials" in result.stdout.lower()


class TestGkfoCommand:
    """Tests for the 'gkfo' command."""

    def test_gkfo_help(self):
        """Test that gkfo --help works."""
        result = util_runner.invoke(util_app, ["gkfo", "--help"])
        assert result.exit_code == 0
        assert "gkfo" in result.stdout.lower() or "correction" in result.stdout.lower()


# VASP Utility commands tests

class TestCalcChargeState:
    """Tests for the 'ccs' command."""

    def test_ccs_help(self):
        """Test that ccs --help works."""
        result = vasp_util_runner.invoke(vasp_util_app, ["ccs", "--help"])
        assert result.exit_code == 0
        assert "charge" in result.stdout.lower()


class TestMakeDefectEntry:
    """Tests for the 'de' command."""

    def test_de_help(self):
        """Test that de --help works."""
        result = vasp_util_runner.invoke(vasp_util_app, ["de", "--help"])
        assert result.exit_code == 0
        assert "defect" in result.stdout.lower() or "entry" in result.stdout.lower()


class TestParchgDir:
    """Tests for the 'pd' command."""

    def test_pd_help(self):
        """Test that pd --help works."""
        result = vasp_util_runner.invoke(vasp_util_app, ["pd", "--help"])
        assert result.exit_code == 0
        assert "parchg" in result.stdout.lower()


class TestRefineDefectPoscar:
    """Tests for the 'rdp' command."""

    def test_rdp_help(self):
        """Test that rdp --help works."""
        result = vasp_util_runner.invoke(vasp_util_app, ["rdp", "--help"])
        assert result.exit_code == 0
        assert "refine" in result.stdout.lower() or "poscar" in result.stdout.lower()


class TestCalcGrids:
    """Tests for the 'cg' command."""

    def test_cg_help(self):
        """Test that cg --help works."""
        result = vasp_util_runner.invoke(vasp_util_app, ["cg", "--help"])
        assert result.exit_code == 0
        assert "grid" in result.stdout.lower()


class TestCalcDefectChargeInfo:
    """Tests for the 'cdc' command."""

    def test_cdc_help(self):
        """Test that cdc --help works."""
        result = vasp_util_runner.invoke(vasp_util_app, ["cdc", "--help"])
        assert result.exit_code == 0
        assert "charge" in result.stdout.lower() or "parchg" in result.stdout.lower()


class TestMakeTotalDos:
    """Tests for the 'mtd' command."""

    def test_mtd_help(self):
        """Test that mtd --help works."""
        result = vasp_util_runner.invoke(vasp_util_app, ["mtd", "--help"])
        assert result.exit_code == 0
        assert "dos" in result.stdout.lower()
