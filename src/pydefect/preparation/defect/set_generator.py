# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from itertools import product
from typing import Dict, List

from pydefect.data.elements.element_data import oxidation_state, electronegativity
from pydefect.defaults import defaults
from pydefect.preparation.defect.models.simple import SimpleDefect
from pydefect.preparation.defect.models.set import DefectSet, filter_defect_set
from pydefect.preparation.supercell.models.supercell_info import SupercellInfo


class DefectSetGenerator:
    """Generate DefectSet based on oxidation states and dopants.

    Creates vacancies, substitutionals, and interstitials automatically.

    Attributes:
        defect_set: Generated DefectSet.

    Example:
        >>> from pydefect.preparation.supercell.models.supercell_info import SupercellInfo
        >>> supercell_info = SupercellInfo.from_json_file()
        >>> maker = DefectSetGenerator(supercell_info, dopants=["Al"])
        >>> maker.defect_set.to_yaml()
    """
    def __init__(self,
                 supercell_info: SupercellInfo,
                 overwritten_oxi_states: Dict[str, int] = None,
                 dopants: List[str] = None,
                 ele_neg_diff: float = defaults.ele_neg_diff,
                 keywords: List[str] = None):
        """Initialize DefectSetGenerator.

        Args:
            supercell_info: SupercellInfo for the host structure.
            overwritten_oxi_states: Override default oxidation states.
            dopants: List of dopant elements.
            ele_neg_diff: Electronegativity difference threshold.
            keywords: Filter keywords for defects.
        """
        self.supercell_info = supercell_info
        self._overwritten_oxi_states = overwritten_oxi_states or {}
        self._dopants = dopants or []
        self._ele_neg_diff = ele_neg_diff

        self._subs = self._dopants + self._host_elements

        defect_set = self._create_defect_set()
        if keywords:
            self.defect_set = filter_defect_set(defect_set, keywords)
        else:
            self.defect_set = defect_set

    def _oxidation_state(self, element):
        try:
            return self._overwritten_oxi_states[element]
        except KeyError:
            return oxidation_state(element)

    @property
    def _host_elements(self) -> List[str]:
        return [str(specie) for specie in
                set(self.supercell_info.structure.species)]

    def _create_defect_set(self):
        result = self._create_vacancy_set()
        result.update(self._create_substitutional_set())
        result.update(self._create_interstitial_set())
        return DefectSet(result)

    def _create_vacancy_set(self):
        result = set()
        for out_name, site in self.supercell_info.sites.items():
            minus_oxi_stat = - self._oxidation_state(site.element)
            result.add(SimpleDefect(None, out_name, charge_set(minus_oxi_stat)))

        return result

    def _create_substitutional_set(self):
        result = set()
        for in_name, (out_name, site) \
                in product(self._subs, self.supercell_info.sites.items()):
            host_element = site.element
            sub_en = electronegativity(in_name)
            host_en = electronegativity(host_element)
            are_same_elem = in_name == host_element
            if None in (sub_en, host_en) or are_same_elem or \
                    abs(sub_en - host_en) > self._ele_neg_diff:
                continue

            sub_oxi = self._oxidation_state(in_name)
            host_oxi = self._oxidation_state(host_element)
            oxi_diff = sub_oxi - host_oxi
            result.add(SimpleDefect(in_name, out_name, charge_set(oxi_diff)))

        return result

    def _create_interstitial_set(self):
        """Create interstitial defects for all dopant elements."""
        result = set()
        for dopant_element in self._subs:
            oxi_state = self._oxidation_state(dopant_element)
            for interstitial_idx in range(len(self.supercell_info.interstitials)):
                result.add(SimpleDefect(dopant_element, f"i{interstitial_idx + 1}",
                                        charge_set(oxi_state)))

        return result


def charge_set(oxidation_state: int) -> List[int]:
    """Generate candidate charge states for a defect.

    -1 (1) is included for positive (negative) odd oxidation states.
    E.g., charge_set(3) = [-1, 0, 1, 2, 3]
          charge_set(-3) = [-3, -2, -1, 0, 1]
          charge_set(2) = [0, 1, 2]
          charge_set(-4) = [-4, -3, -2, -1, 0]

    Args:
        oxidation_state: Expected oxidation state of the defect.

    Returns:
        List of candidate charge states.
    """
    if oxidation_state >= 0:
        charges = [charge for charge in range(oxidation_state + 1)]
        if oxidation_state % 2 == 1:
            charges.insert(0, -1)
    else:
        charges = [charge for charge in range(oxidation_state, 1)]
        if oxidation_state % 2 == 1:
            charges.append(1)

    return charges


# Backward compatibility alias
DefectSetMaker = DefectSetGenerator
