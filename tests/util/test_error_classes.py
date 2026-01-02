# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Tests for pydefect.util.error_classes module."""

import pytest
from pydefect.util.error_classes import (
    PydefectError,
    SupercellError,
    NotPrimitiveError,
    NoCalculatedPotentialSiteError,
    CpdNotSupportedError
)


class TestPydefectError:
    """Tests for PydefectError base exception."""

    def test_is_exception_subclass(self):
        """Test that PydefectError inherits from Exception."""
        assert issubclass(PydefectError, Exception)

    def test_can_be_raised(self):
        """Test that PydefectError can be raised."""
        with pytest.raises(PydefectError):
            raise PydefectError("test")


class TestSupercellError:
    """Tests for SupercellError exception."""

    def test_inherits_from_pydefect_error(self):
        """Test that SupercellError inherits from PydefectError."""
        assert issubclass(SupercellError, PydefectError)

    def test_can_be_raised(self):
        """Test that SupercellError can be raised."""
        with pytest.raises(SupercellError):
            raise SupercellError("supercell error")

    def test_can_be_caught_as_pydefect_error(self):
        """Test that SupercellError can be caught as PydefectError."""
        with pytest.raises(PydefectError):
            raise SupercellError("test")


class TestNotPrimitiveError:
    """Tests for NotPrimitiveError exception."""

    def test_inherits_from_pydefect_error(self):
        """Test that NotPrimitiveError inherits from PydefectError."""
        assert issubclass(NotPrimitiveError, PydefectError)

    def test_can_be_raised(self):
        """Test that NotPrimitiveError can be raised."""
        with pytest.raises(NotPrimitiveError):
            raise NotPrimitiveError("not primitive")

    def test_can_be_caught_as_pydefect_error(self):
        """Test that NotPrimitiveError can be caught as PydefectError."""
        with pytest.raises(PydefectError):
            raise NotPrimitiveError("test")


class TestNoCalculatedPotentialSiteError:
    """Tests for NoCalculatedPotentialSiteError exception."""

    def test_inherits_from_pydefect_error(self):
        """Test that NoCalculatedPotentialSiteError inherits from PydefectError."""
        assert issubclass(NoCalculatedPotentialSiteError, PydefectError)

    def test_can_be_raised(self):
        """Test that NoCalculatedPotentialSiteError can be raised."""
        with pytest.raises(NoCalculatedPotentialSiteError):
            raise NoCalculatedPotentialSiteError("no potential site")

    def test_can_be_caught_as_pydefect_error(self):
        """Test that NoCalculatedPotentialSiteError can be caught as PydefectError."""
        with pytest.raises(PydefectError):
            raise NoCalculatedPotentialSiteError("test")


class TestCpdNotSupportedError:
    """Tests for CpdNotSupportedError exception."""

    def test_inherits_from_exception(self):
        """Test that CpdNotSupportedError inherits from Exception (not PydefectError)."""
        assert issubclass(CpdNotSupportedError, Exception)
        # Note: CpdNotSupportedError does NOT inherit from PydefectError
        assert not issubclass(CpdNotSupportedError, PydefectError)

    def test_can_be_raised(self):
        """Test that CpdNotSupportedError can be raised."""
        with pytest.raises(CpdNotSupportedError):
            raise CpdNotSupportedError("cpd not supported")


class TestErrorHierarchy:
    """Tests for the error class hierarchy."""

    @pytest.mark.parametrize("error_class", [
        SupercellError,
        NotPrimitiveError,
        NoCalculatedPotentialSiteError
    ])
    def test_pydefect_error_subclasses(self, error_class):
        """Test that specific errors are PydefectError subclasses."""
        assert issubclass(error_class, PydefectError)
        error = error_class("test message")
        assert isinstance(error, PydefectError)
        assert isinstance(error, Exception)
