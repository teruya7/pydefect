# -*- coding: utf-8 -*-
from itertools import combinations
from typing import List

from mp_api.client import MPRester

from pydefect.defaults import defaults
from vise.util.logger import get_logger


logger = get_logger(__name__)


class MpQuery:
    """Query Materials Project database for materials.

    Searches for stable materials in a given chemical system.

    Attributes:
        materials: List of MaterialsSummaryDoc from MP.

    Example:
        >>> query = MpQuery(["Mg", "O"])
        >>> for mat in query.materials:
        ...     print(mat.formula_pretty)
    """
    def __init__(self,
                 element_list: List[str],
                 e_above_hull: float = defaults.e_above_hull,
                 properties: List[str] = None):
        # API key is parsed via .pmgrc.yaml
        with MPRester() as m:
            # Due to mp_decode=True by default, class objects are restored.
            logger.info("Note that you're using the newer MPRester.")
            default_fields = ["material_id", "formula_pretty", "structure",
                              "symmetry", "band_gap", "total_magnetization",
                              "types_of_magnetic_species"]
            properties = properties or default_fields
            self.materials = m.materials.summary.search(
                chemsys=chemsys(element_list),
                energy_above_hull=(-1e-5, e_above_hull),
                fields=properties)


def chemsys(element_list: list) -> list:
    """Generate chemical system strings for MP query.

    Args:
        element_list: List of element symbols.

    Returns:
        List of hyphen-separated element combinations.
    """
    result = []
    for num_elements in range(1, len(element_list)+1):
        for comb in combinations(element_list, num_elements):
            result.append('-'.join(comb))

    return result
