# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
import re
from typing import Dict, Any

from pymatgen.core import Element


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


elements = [str(e) for e in Element]
e_va = elements + ["Va"]
e_i = elements + ["i"]


def defect_mpl_name(name: str) -> str:
    """ "Va_O1" -> "$V_{{\\rm O}1}$"
        "Mg_i1" -> "${\\rm Mg}_{i1}$" """
    in_name, out_name = name.split("_")
    if in_name in elements:
        in_name = "{\\rm " + in_name + "}"
    elif in_name == "Va":
        in_name = "V"

    r_out_name = remove_digits(out_name)
    if r_out_name in elements:
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
        if _in in e_va and remove_digits(_out) in e_i:
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


# def defect_html_title_name(fullname):
#     x = fullname.split("_")
#     if len(x) == 2:
#         in_name, out_name = x
#     elif len(x) == 3:
#         in_name, out_name, charge = x
#     else:
#         raise ValueError
#
#     if in_name == "Va":
#         in_name = html.I("V")
#     else:
#         in_name = html.Span(in_name)
#
#     result = [in_name, html.Sub(out_name)]
#     if len(x) == 3:
#         result.append(html.Sup(charge))
#     return result


