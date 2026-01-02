# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
"""U value calculation utilities."""
from itertools import combinations
from typing import Dict

from pydefect.analysis.defect_formation_energy.models import FormationEnergyCollection


def calculate_u_values(
        formation_energy_dict: Dict[str, FormationEnergyCollection],
        correction: bool = False,
        allow_shallow: bool = False
) -> dict:
    """Calculate U values from formation energies dictionary.

    Args:
        formation_energy_dict: Dict mapping defect name to FormationEnergyCollection.
        correction: If True, include correction energy.
        allow_shallow: If True, include shallow defects.

    Returns:
        Dict mapping defect name to U values dict.

    Example:
        >>> u_vals = calculate_u_values(formation_energies)
        >>> print(u_vals["Va_O"])
    """
    return {name: _calculate_single_u_value(energy_collection, correction, allow_shallow)
            for name, energy_collection in formation_energy_dict.items()}


def _calculate_single_u_value(
        energy_collection: FormationEnergyCollection,
        correction: bool,
        allow_shallow: bool
) -> dict:
    """Calculate Hubbard U values from three consecutive charge states.

    The U value is E(q-1) + E(q+1) - 2*E(q) for consecutive charges.

    Args:
        energy_collection: FormationEnergyCollection object for a single defect.
        correction: If True, include correction energy.
        allow_shallow: If True, include shallow defects.

    Returns:
        Dict mapping charge triples to U values.
    """
    result = {}

    pair = list(zip(energy_collection.charges, energy_collection.formation_energies))
    if allow_shallow is False:
        pair = [[charge, formation_en] for (charge, formation_en) in pair
                if formation_en.is_shallow is not True]

    for triple in combinations(pair, 3):
        sorted_triple = sorted(triple, key=lambda item: item[0])
        charges = tuple(item[0] for item in sorted_triple)
        net_charge = charges[0] + charges[2] - charges[1] * 2
        charge_diff = charges[1] - charges[0]
        if net_charge != 0 or charge_diff != 1:
            continue
        energies = [item[1].get_energy(correction) for item in sorted_triple]
        result[charges] = energies[0] + energies[2] - energies[1] * 2
    return result


# Backward compatibility aliases
u_values_from_defect_energies = calculate_u_values
calc_u_values = _calculate_single_u_value
