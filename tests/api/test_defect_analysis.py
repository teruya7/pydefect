# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for defect analysis API functions."""

import pytest

from pydefect import api


class TestMakeDefectStructureInfo:
    """Tests for api.make_defect_structure_info function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_defect_structure_info')
        assert callable(api.make_defect_structure_info)

    def test_make_dsi_basic(self, structures):
        """Test defect structure info creation."""
        perfect, initial, final = structures
        
        result = api.make_defect_structure_info(
            perfect_structure=perfect,
            initial_defect_structure=initial,
            final_defect_structure=final,
        )
        
        assert result is not None
        assert hasattr(result, 'site_diff')
        assert hasattr(result, 'displacements')


class TestMakeDefectEnergyInfo:
    """Tests for api.make_defect_energy_info function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_defect_energy_info')
        assert callable(api.make_defect_energy_info)


class TestPlotDefectEnergy:
    """Tests for api.plot_defect_energy function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'plot_defect_energy')
        assert callable(api.plot_defect_energy)
