# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
"""Degeneracy data classes."""

from dataclasses import dataclass
from typing import Dict, MutableMapping

from monty.json import MSONable
from ruamel.yaml.scalarint import ScalarInt
from vise.util.mix_in import ToYamlFileMixIn


@dataclass
class Degeneracy(MSONable):
    """Degeneracy factors for a defect charge state.

    Attributes:
        site: Site degeneracy (number of equivalent sites).
        spin: Spin degeneracy (2S+1).
        initial_site_sym: Initial site symmetry before relaxation.
        final_site_sym: Final site symmetry after relaxation.

    Example:
        >>> deg = Degeneracy(site=4, spin=2)
        >>> print(deg.degeneracy)
        8
    """
    site: int
    spin: int
    initial_site_sym: str = None
    final_site_sym: str = None

    @property
    def degeneracy(self) -> int:
        """Get total degeneracy (site * spin)."""
        return self.site * self.spin


@dataclass
class Degeneracies(MutableMapping, ToYamlFileMixIn):
    """Collection of degeneracy data for all defects.

    Dictionary-like mapping of defect name -> charge -> Degeneracy.

    Attributes:
        d: Dict mapping defect name to charge to Degeneracy.
    """
    d: Dict[str, Dict[int, Degeneracy]]

    def __iter__(self):
        return self.d.__iter__()

    def __len__(self) -> int:
        return len(self.d)

    def __getitem__(self, k):
        return self.d[k]

    def __delitem__(self, v) -> None:
        self.d.pop(v)

    def __setitem__(self, k, v) -> None:
        self.d[k] = v

    def as_dict(self):
        """Convert to dictionary for serialization."""
        result = {}
        for defect_name, charges in self.d.items():
            result[defect_name] = {}
            for charge, degeneracy in charges.items():
                deg_dict = degeneracy.as_dict()
                deg_dict.pop("@class")
                deg_dict.pop("@module")
                deg_dict.pop("@version")
                if isinstance(charge, ScalarInt):
                    charge = int(charge)
                result[defect_name][charge] = deg_dict
        return result

    @classmethod
    def from_dict(cls, d):
        """Create from dictionary."""
        result = cls(d)
        for defect_name, charges in result.items():
            for charge, deg_dict in charges.items():
                result[defect_name][charge] = Degeneracy.from_dict(deg_dict)
        return result
