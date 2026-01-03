# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for concentration CLI commands (md, ccc, cdc, pcc, pdc, cccdc)."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.main_util import app


runner = CliRunner()


class TestMakeDegeneracies:
    """Tests for the 'md' command."""

    def test_md_help(self):
        """Test that md --help works."""
        result = runner.invoke(app, ["md", "--help"])
        assert result.exit_code == 0
        assert "degenerac" in result.stdout.lower()


class TestCalcCarrierConcentrations:
    """Tests for the 'ccc' command."""

    def test_ccc_help(self):
        """Test that ccc --help works."""
        result = runner.invoke(app, ["ccc", "--help"])
        assert result.exit_code == 0
        assert "carrier" in result.stdout.lower() or "concentration" in result.stdout.lower()


class TestCalcDefectConcentrations:
    """Tests for the 'cdc' command."""

    def test_cdc_help(self):
        """Test that cdc --help works."""
        result = runner.invoke(app, ["cdc", "--help"])
        assert result.exit_code == 0
        assert "defect" in result.stdout.lower() or "concentration" in result.stdout.lower()


class TestPlotCarrierConcentrations:
    """Tests for the 'pcc' command."""

    def test_pcc_help(self):
        """Test that pcc --help works."""
        result = runner.invoke(app, ["pcc", "--help"])
        assert result.exit_code == 0
        assert "plot" in result.stdout.lower() or "carrier" in result.stdout.lower()


class TestPlotDefectConcentrations:
    """Tests for the 'pdc' command."""

    def test_pdc_help(self):
        """Test that pdc --help works."""
        result = runner.invoke(app, ["pdc", "--help"])
        assert result.exit_code == 0
        assert "plot" in result.stdout.lower() or "defect" in result.stdout.lower()


class TestCalcCcdCorrection:
    """Tests for the 'cccdc' command."""

    def test_cccdc_help(self):
        """Test that cccdc --help works."""
        result = runner.invoke(app, ["cccdc", "--help"])
        assert result.exit_code == 0
        assert "ccd" in result.stdout.lower() or "correction" in result.stdout.lower()
