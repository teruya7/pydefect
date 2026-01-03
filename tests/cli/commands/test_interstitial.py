# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for interstitial CLI commands (ai, pi)."""

import pytest
from typer.testing import CliRunner

from pydefect.cli.main import app


runner = CliRunner()


class TestAppendInterstitial:
    """Tests for the 'ai' command."""

    def test_ai_help(self):
        """Test that ai --help works."""
        result = runner.invoke(app, ["ai", "--help"])
        assert result.exit_code == 0
        assert "interstitial" in result.stdout.lower()

    def test_ai_shows_options(self):
        """Test that ai shows expected options."""
        result = runner.invoke(app, ["ai", "--help"])
        assert "--supercell_info" in result.stdout or "-s" in result.stdout
        assert "--base_structure" in result.stdout or "-p" in result.stdout
        assert "--frac_coords" in result.stdout or "-c" in result.stdout


class TestPopInterstitial:
    """Tests for the 'pi' command."""

    def test_pi_help(self):
        """Test that pi --help works."""
        result = runner.invoke(app, ["pi", "--help"])
        assert result.exit_code == 0
        assert "interstitial" in result.stdout.lower() or "remove" in result.stdout.lower()

    def test_pi_shows_options(self):
        """Test that pi shows expected options."""
        result = runner.invoke(app, ["pi", "--help"])
        assert "--supercell_info" in result.stdout or "-s" in result.stdout
        assert "--index" in result.stdout or "-i" in result.stdout
        assert "--pop_all" in result.stdout
