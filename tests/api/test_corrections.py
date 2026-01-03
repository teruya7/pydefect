# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for corrections API functions."""

import pytest

from pydefect import api


class TestMakeEfnvCorrection:
    """Tests for api.make_efnv_correction function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_efnv_correction')
        assert callable(api.make_efnv_correction)


class TestMakeGkfoCorrection:
    """Tests for api.make_gkfo_correction function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_gkfo_correction')
        assert callable(api.make_gkfo_correction)
