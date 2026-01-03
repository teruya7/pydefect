# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for band edge API functions."""

import pytest

from pydefect import api


class TestMakePerfectBandEdgeState:
    """Tests for api.make_perfect_band_edge_state function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_perfect_band_edge_state')
        assert callable(api.make_perfect_band_edge_state)


class TestMakeBandEdgeOrbitalInfos:
    """Tests for api.make_band_edge_orbital_infos function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_band_edge_orbital_infos')
        assert callable(api.make_band_edge_orbital_infos)


class TestMakeBandEdgeStates:
    """Tests for api.make_band_edge_states function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_band_edge_states')
        assert callable(api.make_band_edge_states)
