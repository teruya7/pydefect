# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for calc_results and unitcell API functions."""

import pytest

from pydefect import api


class TestMakeCalcResultsFromVasp:
    """Tests for api.make_calc_results_from_vasp function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_calc_results_from_vasp')
        assert callable(api.make_calc_results_from_vasp)


class TestMakeCalcSummary:
    """Tests for api.make_calc_summary function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_calc_summary')
        assert callable(api.make_calc_summary)


class TestMakeUnitcellFromVasp:
    """Tests for api.make_unitcell_from_vasp function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_unitcell_from_vasp')
        assert callable(api.make_unitcell_from_vasp)


class TestPrintJson:
    """Tests for api.print_json function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'print_json')
        assert callable(api.print_json)
