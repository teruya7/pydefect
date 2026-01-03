# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for chemical potential API functions."""

import pytest

from pydefect import api
from pydefect.analysis.chemical_potential.models import (
    CompositionEnergies, RelativeEnergies
)


class TestMakeStandardAndRelativeEnergies:
    """Tests for api.make_standard_and_relative_energies function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_standard_and_relative_energies')
        assert callable(api.make_standard_and_relative_energies)


class TestMakeChemPotDiag:
    """Tests for api.make_chem_pot_diag function."""

    def test_function_exists(self):
        """Test that the function exists and is callable."""
        assert hasattr(api, 'make_chem_pot_diag')
        assert callable(api.make_chem_pot_diag)
