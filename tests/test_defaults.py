# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Tests for pydefect.defaults module."""

import pytest
from pydefect.defaults import defaults, Defaults


class TestDefaults:
    """Tests for the Defaults class and defaults singleton."""

    def test_singleton_pattern(self):
        """Test that Defaults follows singleton pattern."""
        d1 = Defaults()
        d2 = Defaults()
        assert d1 is d2

    def test_defaults_is_instance(self):
        """Test that defaults is an instance of Defaults."""
        # Defaults is a singleton, so we check the class name
        assert defaults.__class__.__name__ == "Defaults"

    def test_symmetry_length_tolerance(self):
        """Test symmetry_length_tolerance default value."""
        assert defaults.symmetry_length_tolerance == 0.1

    def test_symmetry_angle_tolerance(self):
        """Test symmetry_angle_tolerance default value."""
        assert defaults.symmetry_angle_tolerance == 5.0

    def test_ewald_accuracy(self):
        """Test ewald_accuracy default value."""
        assert defaults.ewald_accuracy == 15.0

    def test_e_above_hull(self):
        """Test e_above_hull default value."""
        assert defaults.e_above_hull == 1e-5

    def test_cutoff_distance_factor(self):
        """Test cutoff_distance_factor default value."""
        assert defaults.cutoff_distance_factor == 1.3

    def test_show_structure_cutoff(self):
        """Test show_structure_cutoff default value."""
        assert defaults.show_structure_cutoff == 5.0

    def test_displace_distance(self):
        """Test displace_distance default value."""
        assert defaults.displace_distance == 0.2

    def test_dist_tol(self):
        """Test dist_tol default value."""
        assert defaults.dist_tol == 1.0

    def test_ele_neg_diff(self):
        """Test ele_neg_diff default value."""
        assert defaults.ele_neg_diff == 2.0

    def test_similar_orb_criterion(self):
        """Test similar_orb_criterion default value."""
        assert defaults.similar_orb_criterion == 0.2

    def test_similar_energy_criterion(self):
        """Test similar_energy_criterion default value."""
        assert defaults.similar_energy_criterion == 0.5

    def test_state_occupied_threshold(self):
        """Test state_occupied_threshold default value."""
        assert defaults.state_occupied_threshold == 0.20

    def test_state_unoccupied_threshold(self):
        """Test state_unoccupied_threshold is complement of occupied."""
        assert defaults.state_unoccupied_threshold == 1 - defaults.state_occupied_threshold
        assert defaults.state_unoccupied_threshold == 0.80

    def test_eigval_range(self):
        """Test eigval_range default value."""
        assert defaults.eigval_range == 1.0

    def test_abs_strange_energy(self):
        """Test abs_strange_energy default value."""
        assert defaults.abs_strange_energy == 100.0

    def test_localized_orbital_radius(self):
        """Test localized_orbital_radius default value."""
        assert defaults.localized_orbital_radius == 3.0

    def test_localized_orbital_fraction_wrt_uniform(self):
        """Test localized_orbital_fraction_wrt_uniform default value."""
        assert defaults.localized_orbital_fraction_wrt_uniform == 0.7

    def test_defect_energy_colors_is_cycle(self):
        """Test that defect_energy_colors returns a cycle iterator."""
        from itertools import cycle
        colors = defaults.defect_energy_colors
        # Get first color
        first = next(colors)
        assert isinstance(first, str)
        assert first.startswith("xkcd:")

    def test_defect_energy_colors_contains_expected(self):
        """Test that defect_energy_colors contains expected colors."""
        colors = defaults.defect_energy_colors
        color_list = [next(colors) for _ in range(13)]
        assert "xkcd:blue" in color_list
        assert "xkcd:red" in color_list
        assert "xkcd:black" in color_list
