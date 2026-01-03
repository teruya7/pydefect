# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for formatting utilities."""

import pytest

from pydefect.utils.formatting import (
    pretty_coords,
    remove_digits,
    only_digits,
    defect_mpl_name,
    typical_defect_name,
    prettify_names,
)


class TestPrettyCoords:
    """Tests for pretty_coords function."""

    def test_basic(self):
        """Test basic coordinate formatting."""
        result = pretty_coords([0.5, 0.25, 0.0])
        assert result == "( 0.500,  0.250,  0.000)"

    def test_negative_coords(self):
        """Test negative coordinate formatting."""
        result = pretty_coords([-0.5, 0.25, 0.0])
        assert "-0.500" in result

    def test_integer_like_coords(self):
        """Test integer-like coordinate formatting."""
        result = pretty_coords([1.0, 0.0, 0.0])
        assert "1.000" in result


class TestRemoveDigits:
    """Tests for remove_digits function."""

    def test_basic(self):
        """Test basic digit removal."""
        assert remove_digits("O1") == "O"
        assert remove_digits("Mg12") == "Mg"
        assert remove_digits("Va") == "Va"

    def test_no_digits(self):
        """Test string with no digits."""
        assert remove_digits("Mg") == "Mg"


class TestOnlyDigits:
    """Tests for only_digits function."""

    def test_basic(self):
        """Test basic digit extraction."""
        assert only_digits("O1") == "1"
        assert only_digits("Mg12") == "12"

    def test_no_digits(self):
        """Test string with no digits."""
        assert only_digits("Mg") == ""


class TestDefectMplName:
    """Tests for defect_mpl_name function."""

    def test_vacancy(self):
        """Test vacancy naming."""
        result = defect_mpl_name("Va_O1")
        assert "$" in result
        assert "V" in result

    def test_substitutional(self):
        """Test substitutional naming."""
        result = defect_mpl_name("Mg_O1")
        assert "$" in result

    def test_interstitial(self):
        """Test interstitial naming."""
        result = defect_mpl_name("Mg_i1")
        assert "$" in result


class TestTypicalDefectName:
    """Tests for typical_defect_name function."""

    def test_vacancy(self):
        """Test vacancy name detection."""
        assert typical_defect_name("Va_O1") is True
        assert typical_defect_name("Va_Mg2") is True

    def test_interstitial(self):
        """Test interstitial name detection."""
        assert typical_defect_name("Mg_i1") is True

    def test_substitutional(self):
        """Test substitutional name detection."""
        assert typical_defect_name("Mg_O1") is True

    def test_invalid(self):
        """Test invalid name detection."""
        assert typical_defect_name("invalid") is False
        assert typical_defect_name("X_Y_Z") is False


class TestPrettifyNames:
    """Tests for prettify_names function."""

    def test_mpl_style(self):
        """Test mpl style prettification."""
        d = {"Va_O1": 1.0}
        result = prettify_names(d, "mpl")
        assert "$" in list(result.keys())[0]

    def test_none_style(self):
        """Test None style (no prettification)."""
        d = {"Va_O1": 1.0}
        result = prettify_names(d, None)
        assert "Va" in list(result.keys())[0]

    def test_invalid_style(self):
        """Test invalid style raises error."""
        d = {"Va_O1": 1.0}
        with pytest.raises(ValueError):
            prettify_names(d, "invalid")
