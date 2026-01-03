# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Site difference between defect and perfect structures."""

from dataclasses import dataclass
from typing import List, Tuple

from monty.json import MSONable
from vise.util.typing import Coords

# Type alias for site information: (index, element, coords)
SiteInfo = Tuple[int, str, Coords]


@dataclass
class SiteDiff(MSONable):
    """Difference in atomic sites between structures.

    Records which atoms were removed, inserted, or substituted.

    Attributes:
        removed: List of (index, element, coords) for vacancies.
        inserted: List of (index, element, coords) for interstitials.
        removed_by_sub: Sites removed due to substitution.
        inserted_by_sub: Sites inserted due to substitution.
    """
    removed: List[SiteInfo]
    inserted: List[SiteInfo]
    removed_by_sub: List[SiteInfo]
    inserted_by_sub: List[SiteInfo]

    @classmethod
    def from_dict(cls, data):
        """Create SiteDiff from dictionary representation."""
        result = super().from_dict(data)
        removed = []
        inserted = []
        removed_by_sub = []
        inserted_by_sub = []

        for site_info in result.removed:
            removed.append((site_info[0], site_info[1], tuple(site_info[2])))
        for site_info in result.inserted:
            inserted.append((site_info[0], site_info[1], tuple(site_info[2])))
        for site_info in result.removed_by_sub:
            removed_by_sub.append((site_info[0], site_info[1], tuple(site_info[2])))
        for site_info in result.inserted_by_sub:
            inserted_by_sub.append((site_info[0], site_info[1], tuple(site_info[2])))

        return cls(removed, inserted, removed_by_sub, inserted_by_sub)

    @property
    def is_complex_defect(self):
        return (len(self.removed) + len(self.inserted)
                + len(self.removed_by_sub)) != 1

    @property
    def is_vacancy(self):
        return (len(self.removed) == 1 and len(self.inserted) == 0 and
                len(self.removed_by_sub) == 0 and len(self.inserted_by_sub) == 0)

    @property
    def is_interstitial(self):
        return (len(self.removed) == 0 and len(self.inserted) == 1 and
                len(self.removed_by_sub) == 0 and len(self.inserted_by_sub) == 0)

    @property
    def is_substituted(self):
        return (len(self.removed) == 0 and len(self.inserted) == 0 and
                len(self.removed_by_sub) == 1 and len(self.inserted_by_sub) == 1)

    @property
    def is_no_diff(self):
        return not (self.removed or self.inserted
                    or self.removed_by_sub or self.inserted_by_sub)
