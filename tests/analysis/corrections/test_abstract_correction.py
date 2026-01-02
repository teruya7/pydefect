# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Tests for pydefect.analysis.corrections.abstract_correction module."""

import pytest
from pathlib import Path
from pydefect.analysis.corrections.models import Correction


class ConcreteCorrection(Correction):
    """Concrete implementation of Correction for testing purposes."""

    def __init__(self, value: float = 1.0):
        self.value = value

    @property
    def correction_energy(self) -> float:
        return self.value

    @property
    def correction_dict(self) -> dict:
        return {"test": self.value}


class TestCorrection:
    """Tests for the abstract Correction class."""

    def test_to_json_file(self, tmp_path):
        """Test that Correction can be serialized to a JSON file."""
        corr = ConcreteCorrection(2.5)
        json_file = tmp_path / "test_correction.json"
        corr.to_json_file(str(json_file))

        assert json_file.exists()
        content = json_file.read_text()
        assert "2.5" in content
        assert "ConcreteCorrection" in content

    def test_to_json_file_default_filename(self, tmp_path, monkeypatch):
        """Test to_json_file with default filename."""
        monkeypatch.chdir(tmp_path)
        corr = ConcreteCorrection(1.0)
        corr.to_json_file()

        assert (tmp_path / "correction.json").exists()

    def test_from_json_file(self, tmp_path):
        """Test that Correction can be deserialized from a JSON file."""
        corr = ConcreteCorrection(3.14)
        json_file = tmp_path / "test_correction.json"
        corr.to_json_file(str(json_file))

        loaded = Correction.from_json_file(str(json_file))
        assert isinstance(loaded, ConcreteCorrection)
        assert loaded.value == 3.14

    def test_from_json_file_default_filename(self, tmp_path, monkeypatch):
        """Test from_json_file with default filename."""
        monkeypatch.chdir(tmp_path)
        corr = ConcreteCorrection(5.0)
        corr.to_json_file()

        loaded = Correction.from_json_file()
        assert loaded.value == 5.0

    def test_msonable_inheritance(self):
        """Test that Correction is MSONable."""
        from monty.json import MSONable
        assert issubclass(Correction, MSONable)

    def test_round_trip(self, tmp_path):
        """Test complete round-trip serialization."""
        original = ConcreteCorrection(123.456)
        json_file = tmp_path / "roundtrip.json"

        original.to_json_file(str(json_file))
        loaded = Correction.from_json_file(str(json_file))

        assert original.value == loaded.value
        assert original.correction_energy == loaded.correction_energy
        assert original.correction_dict == loaded.correction_dict
