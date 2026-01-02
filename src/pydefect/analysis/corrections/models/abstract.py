# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Abstract base class for electrostatic corrections."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from monty.json import MSONable
from monty.serialization import loadfn


class Correction(ABC, MSONable):
    """Abstract base class for electrostatic corrections.

    Provides interface for correction implementations like EFNV and GKFO.
    All correction classes should inherit from this.

    Methods:
        to_json_file: Save correction to JSON file.
        from_json_file: Load correction from JSON file.

    Example:
        >>> correction = ExtendedFnvCorrection.from_json_file()
        >>> print(correction.correction_energy)
    """
    def to_json_file(self, filename: str = "correction.json") -> None:
        """Save correction data to JSON file.

        Args:
            filename: Output filename.
        """
        Path(filename).write_text(self.to_json())

    @classmethod
    def from_json_file(cls, filename: str = "correction.json"):
        """Load correction from JSON file.

        Args:
            filename: Input filename.

        Returns:
            Correction object.
        """
        return loadfn(filename)
