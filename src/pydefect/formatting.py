# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Formatting utilities for human-readable output."""

from typing import List, Union, Dict, Any

from pymatgen.core import Element
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


# --- Defect name formatting ---

def remove_digits(name: str) -> str:
    """Remove digits from name.

    Example:
        >>> remove_digits("O1")
        'O'
    """
    return ''.join([char for char in name if not char.isdigit()])


def only_digits(name: str) -> str:
    """Extract only digits from name.

    Example:
        >>> only_digits("O1")
        '1'
    """
    return ''.join([char for char in name if char.isdigit()])


_elements = [str(e) for e in Element]
_e_va = _elements + ["Va"]
_e_i = _elements + ["i"]


def defect_mpl_name(name: str) -> str:
    """ "Va_O1" -> "$V_{{\rm O}1}$"
        "Mg_i1" -> "${\rm Mg}_{i1}$" """
    in_name, out_name = name.split("_")
    if in_name in _elements:
        in_name = "{\\rm " + in_name + "}"
    elif in_name == "Va":
        in_name = "V"

    r_out_name = remove_digits(out_name)
    if r_out_name in _elements:
        out_name = "{{\\rm " + r_out_name + "}" + only_digits(out_name) + "}"
    else:
        out_name = "{" + out_name + "}"

    return f"${in_name}_{out_name}$"


def typical_defect_name(name: str) -> bool:
    """Check if name follows typical defect naming convention.

    Args:
        name: Defect name (e.g., "Va_O1", "Mg_i1").

    Returns:
        True if name is typical defect format.
    """
    parts = name.split("_")
    if len(parts) == 2:
        _in, _out = parts
        if _in in _e_va and remove_digits(_out) in _e_i:
            return True
    return False


def prettify_names(d: Dict[str, Any], style) -> Dict[str, Any]:
    """Convert defect names to display format.

    Args:
        d: Dict with defect names as keys.
        style: Output style ('mpl' or None).

    Returns:
        Dict with prettified names as keys.
    """
    result = {}
    out_names = [name.split("_")[1] for name in d.keys()]
    for name, value in d.items():
        in_name, out_name = name.split("_")
        reduced_out_name = remove_digits(out_name)
        out_name = reduced_out_name if f"{reduced_out_name}2" not in out_names else out_name
        _name = "_".join([in_name, out_name])
        if _name in result:
            raise ValueError("The prettified names are conflicted. "
                             "Change the defect names, please.")
        if style is None:
            pass
        elif style == "mpl":
            _name = defect_mpl_name(_name)
        else:
            raise ValueError(f"Style {style} is not adequate. Set mpl or None.")
        result[_name] = value
    return result
