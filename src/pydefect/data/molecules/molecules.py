# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

from pathlib import Path

import yaml
from vise.util.logger import get_logger

"""Molecule data for reference calculations.

Characteristic data is retrieved from
McQuarrie and Simon, Phys. Chem. A molecular approach.

Example:
    >>> from pydefect.data.molecules.molecules import MOLECULE_DATA
    >>> print(MOLECULE_DATA["O2"])
"""

logger = get_logger(__name__)

with open(Path(__file__).parent / "molecule_data.yaml", 'r') as f:
    MOLECULE_DATA = yaml.safe_load(f)


