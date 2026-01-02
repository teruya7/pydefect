# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from itertools import combinations
from typing import Dict

from pydefect.analyzer.defect_energy import DefectEnergies


def u_values_from_defect_energies(defect_energy_dict: Dict[str, DefectEnergies],
                                  correction: bool = False,
                                  allow_shallow: bool = False) -> dict:
    """Calculate U values from defect energies dictionary.

    Args:
        defect_energy_dict: Dict mapping defect name to DefectEnergies.
        correction: If True, include correction energy.
        allow_shallow: If True, include shallow defects.

    Returns:
        Dict mapping defect name to U values dict.

    Example:
        >>> u_vals = u_values_from_defect_energies(defect_energies)
        >>> print(u_vals["Va_O"])
    """
    return {name: calc_u_values(defect_energy, correction, allow_shallow)
            for name, defect_energy in defect_energy_dict.items()}


def calc_u_values(defect_energies: DefectEnergies, correction, allow_shallow):
    """Calculate Hubbard U values from three consecutive charge states.

    The U value is E(q-1) + E(q+1) - 2*E(q) for consecutive charges.

    Args:
        defect_energies: DefectEnergies object for a single defect.
        correction: If True, include correction energy.
        allow_shallow: If True, include shallow defects.

    Returns:
        Dict mapping charge triples to U values.
    """
    result = {}

    pair = list(zip(defect_energies.charges, defect_energies.defect_energies))
    if allow_shallow is False:
        pair = [[charge, defect_en] for (charge, defect_en) in pair 
                if defect_en.is_shallow is not True]

    for triple in combinations(pair, 3):
        sorted_triple = sorted(triple, key=lambda item: item[0])
        charges = tuple(item[0] for item in sorted_triple)
        net_charge = charges[0] + charges[2] - charges[1] * 2
        charge_diff = charges[1] - charges[0]
        if net_charge != 0 or charge_diff != 1:
            continue
        energies = [item[1].energy(correction) for item in sorted_triple]
        result[charges] = energies[0] + energies[2] - energies[1] * 2
    return result
