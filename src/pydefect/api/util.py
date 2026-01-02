# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for utility functions."""

from monty.serialization import loadfn


def print_json(
    filename: str,
    use_repr: bool = False,
) -> str:
    """Print the contents of a JSON/YAML file.

    Args:
        filename: Path to JSON or YAML file.
        use_repr: If True, use __repr__ instead of __str__.

    Returns:
        String representation of the object.

    Example:
        >>> from pydefect import api
        >>> content = api.print_json("supercell_info.json")
        >>> print(content)
    """
    obj = loadfn(filename)
    return obj.__repr__() if use_repr else obj.__str__()
