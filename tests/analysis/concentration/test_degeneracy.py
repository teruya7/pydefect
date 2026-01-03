# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
from pathlib import Path

import pytest
from ruamel.yaml.scalarint import ScalarInt

from pydefect.analysis.calculation.models import CalcResults
from pydefect.analysis.concentration.models import Degeneracies, Degeneracy
from pydefect.analysis.concentration.degeneracy import \
    MakeDegeneracy
from pydefect.analysis.formation_energy.models import DefectEnergyInfo
from pydefect.analysis.defect_structure.models import DefectStructureInfo

degeneracies = Degeneracies({"Va_O1": {0: Degeneracy(1, 1, "1", "1")}})


def test_degeneracies():
    assert degeneracies["Va_O1"] == {0: Degeneracy(1, 1, "1", "1")}


def test_degeneracies_yaml_round_trip(tmpdir):
    tmpdir.chdir()
    text = """Va_O1:
  0:
    final_site_sym: '1'
    initial_site_sym: '1'
    site: 1
    spin: 1
"""
    Path("degeneracies.yaml").write_text(text)
    actual = Degeneracies.from_yaml("degeneracies.yaml")
    assert isinstance(actual["Va_O1"][0], Degeneracy)


def test_make_degeneracy(mocker, tmpdir):
    make_deg = MakeDegeneracy("Pm-3m")
    assert make_deg.mag_to_spin_degeneracy(mag=0.09) == 1
    assert make_deg.mag_to_spin_degeneracy(mag=-1.0) == 3
    with pytest.raises(ValueError):
        make_deg.mag_to_spin_degeneracy(mag=0.89)

    m_energy_info = mocker.Mock(DefectEnergyInfo)
    m_energy_info.name, m_energy_info.charge = "Va_O1", ScalarInt(0)

    m_calc_results = mocker.Mock(CalcResults)
    m_calc_results.magnetization = 1.0

    m_structure_info = mocker.Mock(DefectStructureInfo)
    m_structure_info.initial_site_sym = "4mmm"
    m_structure_info.final_site_sym = "2mm"

    assert make_deg.degeneracies == Degeneracies({})
    make_deg.add_degeneracy(m_energy_info, m_calc_results, m_structure_info)
    assert make_deg.degeneracies["Va_O1"][0] == Degeneracy(12, 3, "4mmm", "2mm")


# Additional tests for improved coverage

class TestDegeneracy:
    """Tests for Degeneracy dataclass."""

    def test_degeneracy_property(self):
        """Test that degeneracy property returns site * spin."""
        deg = Degeneracy(site=4, spin=3)
        assert deg.degeneracy == 12

    def test_degeneracy_property_with_1(self):
        """Test degeneracy with site=1, spin=1."""
        deg = Degeneracy(site=1, spin=1)
        assert deg.degeneracy == 1

    def test_degeneracy_with_sym_info(self):
        """Test Degeneracy with symmetry info."""
        deg = Degeneracy(site=2, spin=3, initial_site_sym="mmm", final_site_sym="mm2")
        assert deg.site == 2
        assert deg.spin == 3
        assert deg.initial_site_sym == "mmm"
        assert deg.final_site_sym == "mm2"
        assert deg.degeneracy == 6


class TestDegeneracies:
    """Tests for Degeneracies class (MutableMapping)."""

    def test_len(self):
        """Test __len__ method."""
        degs = Degeneracies({"Va_O1": {0: Degeneracy(1, 1)}, "Va_Mg1": {0: Degeneracy(2, 1)}})
        assert len(degs) == 2

    def test_iter(self):
        """Test __iter__ method."""
        degs = Degeneracies({"Va_O1": {0: Degeneracy(1, 1)}, "Va_Mg1": {0: Degeneracy(2, 1)}})
        keys = list(degs)
        assert "Va_O1" in keys
        assert "Va_Mg1" in keys

    def test_getitem(self):
        """Test __getitem__ method."""
        degs = Degeneracies({"Va_O1": {0: Degeneracy(1, 1)}})
        assert degs["Va_O1"] == {0: Degeneracy(1, 1)}

    def test_setitem(self):
        """Test __setitem__ method."""
        degs = Degeneracies({})
        degs["Va_O1"] = {0: Degeneracy(1, 1)}
        assert "Va_O1" in degs

    def test_delitem(self):
        """Test __delitem__ method."""
        degs = Degeneracies({"Va_O1": {0: Degeneracy(1, 1)}})
        del degs["Va_O1"]
        assert len(degs) == 0

    def test_as_dict(self):
        """Test as_dict method returns proper structure."""
        deg = Degeneracy(site=2, spin=3, initial_site_sym="mmm", final_site_sym="mm2")
        degs = Degeneracies({"Va_O1": {0: deg}})
        d = degs.as_dict()
        assert "Va_O1" in d
        assert 0 in d["Va_O1"]
        assert d["Va_O1"][0]["site"] == 2
        assert d["Va_O1"][0]["spin"] == 3

    def test_from_dict(self):
        """Test from_dict method."""
        d = {"Va_O1": {0: {"site": 2, "spin": 3, "initial_site_sym": "mmm", "final_site_sym": "mm2"}}}
        degs = Degeneracies.from_dict(d)
        assert isinstance(degs["Va_O1"][0], Degeneracy)
        assert degs["Va_O1"][0].degeneracy == 6

