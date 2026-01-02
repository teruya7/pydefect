# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
from pydefect.analysis.corrections.models import Correction


class NoCorrection(Correction):
    """Null correction for neutral defects or testing.

    Returns zero correction energy for cases where no
    electrostatic correction is needed.

    Example:
        >>> no_corr = NoCorrection()
        >>> print(no_corr.correction_energy)
        0.0
    """
    @property
    def correction_energy(self) -> float:
        """Get correction energy (always 0.0)."""
        return 0.0

    @property
    def correction_dict(self) -> dict:
        """Get correction breakdown (empty dict)."""
        return {}
