# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from pydefect.analysis.calculation.models import CalcResults
from pydefect.analysis.formation_energy.models import (
    DefectFormationEnergy, FormationEnergyInfo,
)
from pydefect.analysis.formation_energy.defect_formation_energy import (
    calculate_formation_energy_info, calculate_composition_change,
)
from pydefect.analysis.chemical_potential.models import StandardEnergies
from pydefect.analysis.corrections.models import Correction
from pydefect.makers.defect.defect_entry import DefectEntry
from pymatgen.core import IStructure, Lattice


def test_make_defect_energy_info(mocker):
    defect_entry = mocker.Mock(DefectEntry, autospec=True)
    defect_entry.name = "Va_Mg1"
    defect_entry.charge = -1

    calc_results = mocker.Mock(CalcResults, autospec=True)
    calc_results.structure = IStructure(Lattice.cubic(1.0), ["O"], [[0.0]*3])
    calc_results.energy = 10.0
    calc_results.electronic_conv = False

    correction = mocker.Mock(Correction, autospec=True)
    correction.correction_dict = {"a": 10.0}

    p_calc_results = mocker.Mock(CalcResults, autospec=True)
    p_calc_results.structure = IStructure(Lattice.cubic(1.0),
                                          ["Mg", "O"], [[0.0]*3]*2)
    p_calc_results.energy = 1.0

    standard_energies = StandardEnergies({"Mg": 10.0, "O": 20.0})

    unitcell = mocker.Mock()
    unitcell.vbm = 100.0

    actual = calculate_formation_energy_info(defect_entry, calc_results, correction,
                                             p_calc_results, standard_energies, unitcell)
    energy = DefectFormationEnergy(formation_energy=10.0 - 1.0 + 10 - 100.0,
                                   energy_corrections={"a": 10.0},
                                   is_shallow=None)
    expected = FormationEnergyInfo(name="Va_Mg1", charge=-1,
                                   atom_io={"Mg": -1}, formation_energy=energy)
    assert actual == expected


def test_num_atom_diff():
    s1 = IStructure(Lattice.cubic(1), ["H", "He"], [[0] * 3] * 2)
    s2 = IStructure(Lattice.cubic(1), ["H", "Li"], [[0] * 3] * 2)
    assert calculate_composition_change(s1, s2) == {"He": 1, "Li": -1}