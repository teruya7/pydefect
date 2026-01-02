# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
"""Tests for pydefect.analyzer.transition_levels_plotter module."""

import pytest
from unittest.mock import MagicMock, patch
from pydefect.analyzer.transition_levels_plotter import (
    MplTLData, make_mpl_tl_data, TransitionLevelsMplPlotter
)
from pydefect.analyzer.transition_levels import TransitionLevel, TransitionLevels


class TestMplTLData:
    """Tests for MplTLData dataclass."""

    def test_creation(self):
        """Test MplTLData can be created with required fields."""
        data = MplTLData(
            labels=["Va_O1", "Va_Mg1"],
            charges=[2, 1, 0, -1],
            tl_energy_widths=[[1.0, 0.0], [1.0, 0.0]],
            piled_tl_energy_widths=[[1.0, 0.0], [2.0, 0.0]]
        )
        assert data.labels == ["Va_O1", "Va_Mg1"]
        assert data.charges == [2, 1, 0, -1]

    def test_empty_labels(self):
        """Test MplTLData with empty labels."""
        data = MplTLData(
            labels=[],
            charges=[],
            tl_energy_widths=[],
            piled_tl_energy_widths=[]
        )
        assert data.labels == []
        assert len(data.charges) == 0


class TestMakeMplTlData:
    """Tests for make_mpl_tl_data function."""

    def test_make_mpl_tl_data_basic(self):
        """Test make_mpl_tl_data with basic TransitionLevels."""
        tl1 = TransitionLevel("Va_O1", [[2, 1], [1, 0]], [2.0, 3.0], [1.0, 2.0])
        tl2 = TransitionLevel("Va_Mg1", [[-2, -1]], [2.0], [1.0])
        tls = TransitionLevels([tl1, tl2], cbm=3.0, supercell_vbm=-0.5, supercell_cbm=0.5)

        result = make_mpl_tl_data(tls)

        assert isinstance(result, MplTLData)
        # Check charges are in descending order
        assert result.charges == sorted(result.charges, reverse=True)

    def test_make_mpl_tl_data_returns_mpl_tl_data(self):
        """Test that make_mpl_tl_data returns MplTLData instance."""
        tl1 = TransitionLevel("Va_O1", [[1, 0]], [1.5], [0.5])
        tls = TransitionLevels([tl1], cbm=2.0, supercell_vbm=-0.5, supercell_cbm=0.5)

        result = make_mpl_tl_data(tls)
        assert isinstance(result, MplTLData)
        assert isinstance(result.labels, list)
        assert isinstance(result.charges, list)
        assert isinstance(result.tl_energy_widths, list)
        assert isinstance(result.piled_tl_energy_widths, list)


class TestTransitionLevelsMplPlotter:
    """Tests for TransitionLevelsMplPlotter class."""

    def test_init_default(self):
        """Test TransitionLevelsMplPlotter initialization with defaults."""
        with patch('pydefect.analyzer.transition_levels_plotter.plt') as mock_plt:
            plotter = TransitionLevelsMplPlotter()
            assert plotter.plt is not None

    def test_init_with_y_unit(self):
        """Test TransitionLevelsMplPlotter initialization with y_unit."""
        with patch('pydefect.analyzer.transition_levels_plotter.plt') as mock_plt:
            plotter = TransitionLevelsMplPlotter(y_unit="meV")
            assert plotter.plt is not None

    def test_init_calls_bar(self):
        """Test that __init__ calls plt.bar for plotting."""
        with patch('pydefect.analyzer.transition_levels_plotter.plt') as mock_plt:
            plotter = TransitionLevelsMplPlotter()
            # plt.bar should be called at least once
            assert mock_plt.bar.called

    def test_plotter_has_plt_attribute(self):
        """Test that plotter exposes plt attribute."""
        with patch('pydefect.analyzer.transition_levels_plotter.plt') as mock_plt:
            plotter = TransitionLevelsMplPlotter()
            assert hasattr(plotter, 'plt')