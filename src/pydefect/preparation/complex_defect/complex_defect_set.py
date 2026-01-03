# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
try:
    from collections import Iterable
except ImportError:
    from collections.abc import Iterable

from dataclasses import dataclass
from typing import List, Dict, Optional, Iterator

from monty.serialization import loadfn


@dataclass
class ComplexDefect:
    """Complex multi-site defect specification.

    Example:
        >>> defect = ComplexDefect("Va-pair", {0: None, 5: None}, [-2, 0, 2])
    """
    name: str
    replaced_sites: Dict[int, Optional[str]]
    charges: list

    # @classmethod
    # def from_dict(cls, d):
    #     return cls(name=d["name"], replaced_sites=, charges=tuple(d["charges"]))

    @property
    def str_list(self):
        return ["_".join([self.name, str(charge)]) for charge in self.charges]

    @property
    def charge_list(self):
        return [charge for charge in self.charges]


class ComplexDefectSet(Iterable):
    """Collection of complex multi-site defects.

    Attributes:
        defects: List of ComplexDefect objects.

    Example:
        >>> defect_set = ComplexDefectSet.from_yaml("complex_defect_in.yaml")
        >>> for defect in defect_set:
        ...     print(defect.name)
    """
    def __init__(self, defects: List[ComplexDefect]):
        """Initialize ComplexDefectSet.

        Args:
            defects: List of ComplexDefect objects.
        """
        self.defects = defects

    def __iter__(self) -> Iterator:
        yield from self.defects

    @classmethod
    def from_yaml(cls, filename: str = "defect_in.yaml") -> "ComplexDefectSet":
        d = loadfn(filename)
        names = []
        for name, dd in d.items():
            names.append(ComplexDefect(name=name, **dd))
        return cls(names)


