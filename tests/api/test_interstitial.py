# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for interstitial API functions."""

import pytest
from unittest.mock import MagicMock, patch
from pymatgen.core import Lattice, Structure

from pydefect import api


class TestAppendInterstitial:
    """Tests for api.append_interstitial function."""

    def test_append_interstitial_basic(self, supercell_info, ortho_conventional):
        """Test appending an interstitial site."""
        result = api.append_interstitial(
            supercell_info=supercell_info,
            base_structure=ortho_conventional,
            frac_coords=[0.5, 0.5, 0.5],
            info="test_site",
        )
        
        assert result is not None
        assert hasattr(result, 'interstitials')


class TestPopInterstitial:
    """Tests for api.pop_interstitial function."""

    def test_pop_interstitial_by_index(self, supercell_info):
        """Test removing an interstitial by index."""
        result = api.pop_interstitial(
            supercell_info=supercell_info,
            index=1,
        )
        
        assert result is not None

    def test_pop_interstitial_all(self, supercell_info):
        """Test removing all interstitials."""
        result = api.pop_interstitial(
            supercell_info=supercell_info,
            pop_all=True,
        )
        
        assert result is not None
        assert len(result.interstitials) == 0
