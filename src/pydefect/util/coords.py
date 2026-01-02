# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from typing import List, Union

from vise.util.typing import Coords


def pretty_coords(coords: Union[List[float], Coords]) -> str:
    """Format coordinates as prettified string.

    Args:
        coords: Fractional or Cartesian coordinates.

    Returns:
        Formatted coordinate string, e.g., "( 0.500,  0.250,  0.000)".

    Example:
        >>> pretty_coords([0.5, 0.25, 0.0])
        '( 0.500,  0.250,  0.000)'
    """
    return f'({", ".join([f"{coord:6.3f}" for coord in coords])})'
