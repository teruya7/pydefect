# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.

from pydefect.analysis.defect_formation_energy.models import (
    FormationEnergyInfo, DefectFormationEnergy,
    FormationEnergySummary, FormationEnergyCollection,
)
from pydefect.analysis.defect_formation_energy.defect_formation_energy import \
    calculate_formation_energy_summary
from pydefect.analysis.chemical_potential.models import TargetVertices, TargetVertex


def test_make_defect_energy_summary(mocker):
    energy1 = DefectFormationEnergy(0.0, {"PC correction": 2.0}, False)
    energy2 = DefectFormationEnergy(1.0, {"PC correction": 3.0}, True)
    defect_infos = [FormationEnergyInfo("Va_Mg1", 0, {"Mg": -1}, energy1),
                    FormationEnergyInfo("Va_Mg1", 1, {"Mg": -1}, energy2)]
    target_vertices = TargetVertices(
        target="MgO", vertices={"A": TargetVertex({"Mg": 5.0})})

    unitcell = mocker.Mock()
    unitcell.vbm = 1.0
    unitcell.cbm = 11.0

    perf_be_state = mocker.Mock()
    perf_be_state.vbm_info.energy = 0.0
    perf_be_state.cbm_info.energy = 12.0

    actual = calculate_formation_energy_summary(defect_infos, target_vertices, unitcell,
                                                perf_be_state)

    formation_energies = {"Va_Mg1": FormationEnergyCollection(
        atom_io={"Mg": -1}, charges=[0, 1], formation_energies=[energy1, energy2])}

    expected = FormationEnergySummary(title=unitcell.system,
                                      formation_energies=formation_energies,
                                      rel_chem_pots={"A": {"Mg": 5.0}},
                                      cbm=10.0,
                                      supercell_vbm=-1.0,
                                      supercell_cbm=11.0)
    assert actual == expected
