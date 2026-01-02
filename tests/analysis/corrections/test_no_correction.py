# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
"""Tests for pydefect.analysis.corrections.no_correction module."""

import pytest
from pydefect.analysis.corrections.models import NoCorrection
from pydefect.analysis.corrections.models import Correction


class TestNoCorrection:
    """Tests for the NoCorrection class."""

    def test_correction_energy(self):
        """Test that correction_energy returns 0.0."""
        nc = NoCorrection()
        assert nc.correction_energy == 0.0

    def test_correction_energy_type(self):
        """Test that correction_energy returns a float."""
        nc = NoCorrection()
        assert isinstance(nc.correction_energy, float)

    def test_correction_dict(self):
        """Test that correction_dict returns an empty dictionary."""
        nc = NoCorrection()
        assert nc.correction_dict == {}

    def test_correction_dict_type(self):
        """Test that correction_dict returns a dict."""
        nc = NoCorrection()
        assert isinstance(nc.correction_dict, dict)

    def test_inherits_from_correction(self):
        """Test that NoCorrection inherits from Correction."""
        assert issubclass(NoCorrection, Correction)
        nc = NoCorrection()
        assert isinstance(nc, Correction)

    def test_msonable(self):
        """Test that NoCorrection is MSONable."""
        from monty.json import MSONable
        nc = NoCorrection()
        assert isinstance(nc, MSONable)

    def test_as_dict(self):
        """Test that NoCorrection can be serialized to dict."""
        nc = NoCorrection()
        d = nc.as_dict()
        assert "@module" in d
        assert "@class" in d
        assert d["@class"] == "NoCorrection"

    def test_from_dict(self):
        """Test that NoCorrection can be deserialized from dict."""
        nc = NoCorrection()
        d = nc.as_dict()
        reconstructed = NoCorrection.from_dict(d)
        assert isinstance(reconstructed, NoCorrection)
        assert reconstructed.correction_energy == nc.correction_energy
        assert reconstructed.correction_dict == nc.correction_dict

    def test_json_roundtrip(self, tmp_path):
        """Test JSON file round-trip."""
        nc = NoCorrection()
        json_file = tmp_path / "no_correction.json"
        nc.to_json_file(str(json_file))

        loaded = Correction.from_json_file(str(json_file))
        assert isinstance(loaded, NoCorrection)
        assert loaded.correction_energy == 0.0
        assert loaded.correction_dict == {}
