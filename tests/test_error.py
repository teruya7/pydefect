# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Tests for pydefect.error module."""

import pytest
from pydefect.error import PydefectError


class TestPydefectError:
    """Tests for the PydefectError exception class."""

    def test_is_exception_subclass(self):
        """Test that PydefectError is a subclass of Exception."""
        assert issubclass(PydefectError, Exception)

    def test_can_be_raised(self):
        """Test that PydefectError can be raised and caught."""
        with pytest.raises(PydefectError):
            raise PydefectError("test error message")

    def test_message_preserved(self):
        """Test that error message is preserved."""
        message = "This is a test error message"
        try:
            raise PydefectError(message)
        except PydefectError as e:
            assert str(e) == message

    def test_empty_message(self):
        """Test PydefectError with empty message."""
        with pytest.raises(PydefectError):
            raise PydefectError()

    def test_exception_args(self):
        """Test that exception args are accessible."""
        msg = "error message"
        try:
            raise PydefectError(msg)
        except PydefectError as e:
            assert e.args == (msg,)

    def test_can_be_caught_as_exception(self):
        """Test that PydefectError can be caught as generic Exception."""
        with pytest.raises(Exception):
            raise PydefectError("test")
