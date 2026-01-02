# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from pydefect.analysis.calculation.calc_results import CalcResults
from pymatgen.io.vasp import Vasprun, Outcar


def make_calc_results_from_vasp(vasprun: Vasprun,
                                outcar: Outcar) -> CalcResults:
    """Create CalcResults from VASP output files.

    Args:
        vasprun: Parsed vasprun.xml file.
        outcar: Parsed OUTCAR file.

    Returns:
        CalcResults with structure, energy, and potentials.

    Example:
        >>> from pymatgen.io.vasp import Vasprun, Outcar
        >>> vasprun = Vasprun("vasprun.xml")
        >>> outcar = Outcar("OUTCAR")
        >>> results = make_calc_results_from_vasp(vasprun, outcar)
        >>> results.to_json_file()
    """
    return CalcResults(structure=vasprun.final_structure,
                       energy=outcar.final_energy,
                       magnetization=outcar.total_mag or 0.0,
                       potentials=[-p for p in outcar.electrostatic_potential],
                       electronic_conv=vasprun.converged_electronic,
                       ionic_conv=vasprun.converged_ionic)
