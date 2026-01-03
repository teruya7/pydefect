# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for structure_tools utilities."""

import pytest
import numpy as np
from pymatgen.core import Structure, Lattice

from pydefect.utils.structure_tools import Distances, Coordination


class TestDistances:
    """Tests for Distances class."""

    @pytest.fixture
    def simple_structure(self):
        """Create a simple cubic structure for testing."""
        lattice = Lattice.cubic(4.0)
        coords = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]
        return Structure(lattice, ["Mg", "O"], coords)

    def test_distances_basic(self, simple_structure):
        """Test basic distance calculation."""
        distances_obj = Distances(simple_structure, np.array([0.0, 0.0, 0.0]))
        dists = distances_obj.distances()
        
        assert len(dists) >= 1
        assert all(d >= 0 for d in dists)

    def test_distances_with_specie(self, simple_structure):
        """Test distance calculation for specific element."""
        distances_obj = Distances(simple_structure, np.array([0.0, 0.0, 0.0]))
        dists = distances_obj.distances(specie="O")
        
        # Should only have one finite distance (for O)
        finite_dists = [d for d in dists if d != float("inf")]
        assert len(finite_dists) >= 1

    def test_shortest_distance(self, simple_structure):
        """Test shortest distance property."""
        distances_obj = Distances(simple_structure, np.array([0.0, 0.0, 0.0]))
        shortest = distances_obj.shortest_distance
        
        assert shortest > 0

    def test_atom_idx_at_center(self, simple_structure):
        """Test finding atom at center."""
        distances_obj = Distances(simple_structure, np.array([0.0, 0.0, 0.0]))
        idx = distances_obj.atom_idx_at_center("Mg")
        
        assert idx == 0

    def test_atom_idx_at_center_not_found(self, simple_structure):
        """Test when no atom at center."""
        distances_obj = Distances(simple_structure, np.array([0.25, 0.25, 0.25]))
        idx = distances_obj.atom_idx_at_center("Mg")
        
        assert idx is None

    def test_coordination(self, simple_structure):
        """Test coordination calculation."""
        distances_obj = Distances(simple_structure, np.array([0.0, 0.0, 0.0]))
        coord = distances_obj.coordination()
        
        assert isinstance(coord, Coordination)
        assert hasattr(coord, 'distance_dict')
        assert hasattr(coord, 'cutoff')


class TestCoordination:
    """Tests for Coordination dataclass."""

    def test_coordination_basic(self):
        """Test basic Coordination creation."""
        coord = Coordination(
            distance_dict={"O": [2.0, 2.0, 2.0, 2.0]},
            cutoff=3.0,
            neighboring_atom_indices=[0, 1, 2, 3]
        )
        
        assert coord.cutoff == 3.0
        assert len(coord.neighboring_atom_indices) == 4

    def test_coordination_msonable(self):
        """Test that Coordination is MSONable."""
        coord = Coordination(
            distance_dict={"O": [2.0]},
            cutoff=3.0,
            neighboring_atom_indices=[0]
        )
        
        assert hasattr(coord, 'as_dict')
