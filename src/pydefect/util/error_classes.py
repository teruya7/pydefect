# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.


class PydefectError(Exception):
    """Base exception for pydefect errors.

    Example:
        >>> raise PydefectError("Generic pydefect error")
    """
    pass


class SupercellError(PydefectError):
    """Error during supercell generation."""
    pass


class NotPrimitiveError(PydefectError):
    """Input structure is not a primitive cell."""
    pass


class NoCalculatedPotentialSiteError(PydefectError):
    """No calculated potential sites found for correction."""
    pass


class CpdNotSupportedError(Exception):
    """Chemical potential diagram not supported for this system."""
    pass
