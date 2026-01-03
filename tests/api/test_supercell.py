# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for supercell API functions."""

import pytest
from unittest.mock import MagicMock, patch
from pymatgen.core import Lattice, IStructure

from pydefect import api


class TestMakeSupercell:
    """Tests for api.make_supercell function."""

    def test_make_supercell_basic(self, simple_cubic):
        """Test basic supercell creation."""
        supercell_info, supercell = api.make_supercell(
            unitcell=simple_cubic,
            min_num_atoms=1,
            max_num_atoms=10,
        )
        
        assert supercell is not None
        assert hasattr(supercell_info, 'structure')

    def test_make_supercell_with_matrix(self, simple_cubic):
        """Test supercell creation with explicit matrix."""
        supercell_info, supercell = api.make_supercell(
            unitcell=simple_cubic,
            matrix=[[2, 0, 0], [0, 2, 0], [0, 0, 2]],
        )
        
        assert supercell is not None
        assert len(supercell) == 8  # 2x2x2 = 8 atoms
