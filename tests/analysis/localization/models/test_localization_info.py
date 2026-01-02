# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Tests for ChargeLocalizationInfo (models/localization_info.py)."""
import numpy as np
import pytest
from pydefect.analysis.localization.models import (
    ChargeLocalizationInfo,
    RadialChargeDist,
)
from pymatgen.electronic_structure.core import Spin
from tests.helpers.assertion import assert_json_roundtrip


@pytest.fixture
def radial_charge_dist():
    return RadialChargeDist(
        defect_center=(0.1, 0.1, 0.1),
        density_profile=[0.4, 0.4, 0.2],
    )


@pytest.fixture
def charge_localization_info(radial_charge_dist):
    radial_charge_dist_down = RadialChargeDist(
        defect_center=(0.1, 0.1, 0.1),
        density_profile=[0.3, 0.5, 0.2],
    )

    return ChargeLocalizationInfo(
        distance_bins=[0.0, 1.0, 2.0, 2.5],
        band_indices=[10],
        radial_distributions=[[radial_charge_dist, radial_charge_dist_down]],
        uniform_density=0.5,
    )


def test_radial_charge_dist_json_roundtrip(radial_charge_dist, tmpdir):
    assert_json_roundtrip(radial_charge_dist, tmpdir)


def test_charge_localization_info_json_roundtrip(charge_localization_info, tmpdir):
    assert_json_roundtrip(charge_localization_info, tmpdir)


def test_integrated_charge_distribution(charge_localization_info):
    actual = charge_localization_info.integrated_charge_distribution(10, Spin.up)
    expected = np.array([0.4 * 1.0 ** 3,
                         0.4 * (2.0 ** 3 - 1.0 ** 3),
                         0.2 * (2.5 ** 3 - 2.0 ** 3)]) * 4 / 3 * np.pi
    np.testing.assert_array_almost_equal(actual, expected)


def test_localization_radius(charge_localization_info):
    actual = charge_localization_info.localization_radius(10, Spin.up)
    assert actual == 0.2984155182973037


def test_uniform_localization_radius(charge_localization_info):
    assert charge_localization_info.uniform_localization_radius == 0.6203504908994001


def test_str(charge_localization_info):
    print(charge_localization_info)
    expected = """ -- charge localization info
Uniform charge radius is  0.620
Band index  Spin  Radius  Center
11          up    0.298   ( 0.100,  0.100,  0.100)
11          down  0.398   ( 0.100,  0.100,  0.100)"""
    assert charge_localization_info.__str__() == expected


def test_plot_distribution(charge_localization_info):
    plt = charge_localization_info.plot_distribution()
    plt.show()


def test_find_localized_orbitals(charge_localization_info):
    actual = charge_localization_info.find_localized_orbitals(0.3, 1.0)
    expected = [[10], []]
    assert actual == expected

    actual = charge_localization_info.find_localized_orbitals(0.4, 1.0)
    expected = [[10], [10]]
    assert actual == expected

    actual = charge_localization_info.find_localized_orbitals(0.4, 0.398 / 0.62 - 0.001)
    expected = [[10], []]
    assert actual == expected
