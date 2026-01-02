# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
import numpy as np
import pytest

from pydefect.analysis.concentration.concentration import \
    ConcentrationByFermiLevel, Concentration, CarrierConcentration, \
    DefectConcentration
from pydefect.analysis.concentration.models import Degeneracies, Degeneracy
from pydefect.analysis.concentration.distribution_function import fermi_dirac
from pydefect.analysis.concentration.concentration import \
    MakeConcentrations, VBDos, CBDos, TotalDos, \
    redistribute_concentration
from pydefect.analysis.defect_formation_energy.models import ChargeEnergies, SingleChargeEnergies
from tests.helpers.assertion import assert_msonable

vb_dos = VBDos(energies=[-1.0, 0.0], doses=[1.0, 1.0])
cb_dos = CBDos(energies=[1.0, 2.0], doses=[1.0, 1.0])


def test_dos_carrier_type():
    assert vb_dos.carrier_type == "p"
    assert cb_dos.carrier_type == "n"


def test_vb_dos():
    actual = vb_dos.carrier_concentration(0.0, 1000)
    expected = 0.5 + fermi_dirac(1.0, 1000)
    assert actual == expected


def test_cb_dos():
    actual = cb_dos.carrier_concentration(1.0, 1000)
    expected = 0.5 + fermi_dirac(1.0, 1000)
    assert actual == expected


single_energies = SingleChargeEnergies([(0, 0.0)])


con_by_Ef = ConcentrationByFermiLevel(
    T=1000.0,
    concentrations=[
        Concentration(Ef=1.0,
                      carrier=CarrierConcentration(p=9.124767654106573e-06,
                                                   n=9.124767653346825e-06),
                      defects=[DefectConcentration(name='Va_O1',
                                                   charges=[0],
                                                   concentrations=[1.0],
                                                   )])],
    equilibrium_concentration=None,
    pinning_levels={"Va_O1": [None, None]})


def test_concentration_by_fermi_level_msonable():
    assert_msonable(con_by_Ef)


def test_carrier_calculator():
    dos_data = TotalDos(energies=list(np.linspace(-3.0, 3.0, 7)),
                        dos=[1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0],
                        volume=10**24,
                        vbm=0.0,
                        cbm=1.0)
    charge_energies = ChargeEnergies({"Va_O1": SingleChargeEnergies([(0, 0.0)])},
                                     e_min=0.0,
                                     e_max=1.0)

    degeneracies = Degeneracies({"Va_O1": {0: Degeneracy(1, 1)}})

    make_concentration = MakeConcentrations(
        total_dos=dos_data,
        charge_energies=charge_energies,
        degeneracies=degeneracies,
        T=1000.0)

    assert make_concentration.carrier_calculator.vb_dos == VBDos(energies=[-3.0, -2.0, -1.0, 0.0],
                                              doses=[1.0, 1.0, 1.0, 1.0])
    assert make_concentration.carrier_calculator.cb_dos == CBDos(energies=[1.0, 2.0, 3.0],
                                              doses=[0.0, 1.0, 1.0])

    actual = make_concentration.make_concentrations_by_fermi_level(Efs=[1.0])
    assert actual == con_by_Ef


def test_redistribute_concentration():
    actual = redistribute_concentration([1.0, 3.0], total=20.0)
    expected = [5.0, 15.0]
    assert actual == expected

