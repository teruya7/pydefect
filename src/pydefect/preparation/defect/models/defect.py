# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

import re
from dataclasses import dataclass
from typing import List, Optional

from monty.json import MSONable


@dataclass(frozen=True)
class Defect(MSONable):
    """Base class for defect representation.

    Attributes:
        name: Defect name (e.g., "Va_O1", "Mg_Al").
        charges: Tuple of charge states to calculate.

    Example:
        >>> defect = Defect("Va_O1", (0, 1, 2))
    """
    name: str
    charges: tuple

    @classmethod
    def from_dict(cls, d):
        return cls(name=d["name"], charges=tuple(d["charges"]))

    @property
    def str_list(self):
        return ["_".join([self.name, str(charge)]) for charge in self.charges]

    @property
    def charge_list(self):
        return [charge for charge in self.charges]


class SimpleDefect(Defect):
    """Simple defect with in/out atom specification.

    Represents vacancy, interstitial, or substitution.

    Attributes:
        in_atom: Element being removed (None for vacancy).
        out_atom: Site name (e.g., "O1", "Mg1").
        charge_list: List of charge states.

    Example:
        >>> defect = SimpleDefect("Mg", "O1", [-2, -1, 0])
    """
    def __init__(self, in_atom, out_atom, charge_list):
        """Initialize SimpleDefect.

        Args:
            in_atom: Element inserted (None or "Va" for vacancy).
            out_atom: Site being replaced (e.g., "O1").
            charge_list: List of charge states to calculate.
        """
        if in_atom is None:
            in_atom = "Va"
        super().__init__("_".join([in_atom, out_atom]), tuple(charge_list))

    @property
    def in_atom(self):
        result = self.name.split("_")[0]
        if result == "Va":
            return
        return result

    @property
    def out_atom(self):
        return self.name.split("_")[1]

    @classmethod
    def from_dict(cls, d):
        _d = {k: v for k, v in d.items() if "@" not in k}
        return cls(**_d)


def filter_defect(defect: SimpleDefect, keywords: List[str]
                         ) -> Optional[SimpleDefect]:
    charges = []
    for charge in defect.charges:
        full_name = "_".join([defect.name, str(charge)])
        if any([re.search(keyword, full_name) for keyword in keywords]):
            charges.append(charge)
    if charges:
        return SimpleDefect(defect.in_atom, defect.out_atom, tuple(charges))
    else:
        return


# Backward compatibility alias
screen_simple_defect = filter_defect
