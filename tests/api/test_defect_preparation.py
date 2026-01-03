# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for defect preparation API functions."""

import pytest

from pydefect import api


class TestMakeDefectSet:
    """Tests for api.make_defect_set function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_defect_set')
        assert callable(api.make_defect_set)

    def test_make_defect_set_basic(self, supercell_info):
        """Test defect set creation."""
        result = api.make_defect_set(
            supercell_info=supercell_info,
            oxi_states={"H": 1, "He": 0},
        )
        
        assert result is not None
        assert hasattr(result, 'to_yaml')


class TestMakeDefectEntries:
    """Tests for api.make_defect_entries function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_defect_entries')
        assert callable(api.make_defect_entries)
