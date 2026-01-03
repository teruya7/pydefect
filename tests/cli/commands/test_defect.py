# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for defect CLI commands (ds, dsi, dei, des, cs, pe)."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.main import app


runner = CliRunner()


class TestDefectSet:
    """Tests for the 'ds' command."""

    def test_ds_help(self):
        """Test that ds --help works."""
        result = runner.invoke(app, ["ds", "--help"])
        assert result.exit_code == 0
        assert "defect" in result.stdout.lower()

    def test_ds_shows_options(self):
        """Test that ds shows expected options."""
        result = runner.invoke(app, ["ds", "--help"])
        assert "--oxi_states" in result.stdout or "-o" in result.stdout
        assert "--dopants" in result.stdout or "-d" in result.stdout


class TestDefectStructureInfo:
    """Tests for the 'dsi' command."""

    def test_dsi_help(self):
        """Test that dsi --help works."""
        result = runner.invoke(app, ["dsi", "--help"])
        assert result.exit_code == 0
        assert "defect" in result.stdout.lower() or "structure" in result.stdout.lower()

    def test_dsi_shows_options(self):
        """Test that dsi shows expected options."""
        result = runner.invoke(app, ["dsi", "--help"])
        assert "--dirs" in result.stdout or "-d" in result.stdout
        assert "--supercell_info" in result.stdout or "-s" in result.stdout


class TestDefectEnergyInfos:
    """Tests for the 'dei' command."""

    def test_dei_help(self):
        """Test that dei --help works."""
        result = runner.invoke(app, ["dei", "--help"])
        assert result.exit_code == 0
        assert "energy" in result.stdout.lower()

    def test_dei_shows_options(self):
        """Test that dei shows expected options."""
        result = runner.invoke(app, ["dei", "--help"])
        assert "--dirs" in result.stdout or "-d" in result.stdout
        assert "--unitcell" in result.stdout or "-u" in result.stdout


class TestDefectEnergySummary:
    """Tests for the 'des' command."""

    def test_des_help(self):
        """Test that des --help works."""
        result = runner.invoke(app, ["des", "--help"])
        assert result.exit_code == 0
        assert "summary" in result.stdout.lower() or "energy" in result.stdout.lower()


class TestCalcSummary:
    """Tests for the 'cs' command."""

    def test_cs_help(self):
        """Test that cs --help works."""
        result = runner.invoke(app, ["cs", "--help"])
        assert result.exit_code == 0
        assert "summary" in result.stdout.lower() or "calc" in result.stdout.lower()


class TestPlotDefectEnergy:
    """Tests for the 'pe' command."""

    def test_pe_help(self):
        """Test that pe --help works."""
        result = runner.invoke(app, ["pe", "--help"])
        assert result.exit_code == 0
        assert "plot" in result.stdout.lower() or "energy" in result.stdout.lower()

    def test_pe_shows_options(self):
        """Test that pe shows expected options."""
        result = runner.invoke(app, ["pe", "--help"])
        assert "--defect_energy_summary" in result.stdout or "-d" in result.stdout
        assert "--label" in result.stdout or "-l" in result.stdout
