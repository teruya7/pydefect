# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from collections.abc import Set
from pathlib import Path
from typing import Iterator, List, Set as typeSet

import yaml
from monty.json import MSONable
from monty.serialization import loadfn
from pydefect.preparation.defect.models.simple import filter_defect, SimpleDefect


class DefectSet(MSONable, Set):
    """Set of defect configurations for calculations.

    Collection of SimpleDefect objects representing defects
    to be calculated with their charge states.

    Attributes:
        defects: Set of SimpleDefect objects.

    Example:
        >>> defect_set = DefectSet.from_yaml("defect_in.yaml")
        >>> for defect in defect_set:
        ...     print(defect.name, defect.charges)
    """
    def __init__(self, defects: typeSet[SimpleDefect]):
        """Initialize DefectSet.

        Args:
            defects: Set of SimpleDefect objects.
        """
        self.defects = defects

    def __contains__(self, defect: object) -> bool:
        return defect in self.defects

    def __len__(self) -> int:
        return len(self.defects)

    def __iter__(self) -> Iterator:
        yield from self.defects

    def to_yaml(self, filename: str = "defect_in.yaml") -> None:
        d = {defect.name: list(defect.charges) for defect in self.defects}
        Path(filename).write_text(yaml.dump(d, default_flow_style=None))

    @classmethod
    def from_yaml(cls, filename: str = "defect_in.yaml") -> "DefectSet":
        d = loadfn(filename)
        names = set()
        for name, charges in d.items():
            in_name, out_name = name.split("_")
            names.add(SimpleDefect(in_name, out_name, tuple(charges)))
        return cls(names)


def filter_defect_set(defect_set: DefectSet, keywords: List[str]):
    result = set()
    for defect in defect_set:
        screened = filter_defect(defect, keywords)
        if screened:
            result.add(screened)
    return DefectSet(result)


# Backward compatibility alias
screen_defect_set = filter_defect_set
