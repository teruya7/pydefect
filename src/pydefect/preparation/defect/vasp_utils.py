# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Calculate defect charge state from VASP input files."""
from pymatgen.io.vasp.inputs import Poscar, Incar, Potcar
from vise.util.logger import get_logger

logger = get_logger(__name__)


def calculate_charge_state(poscar: Poscar, potcar: Potcar, incar: Incar) -> int:
    """Calculate defect charge state from structure, potcar, and NELECT.

    Determines the defect charge by comparing NELECT with the
    neutral electron count calculated from POTCAR.

    Args:
        poscar: Parsed POSCAR file.
        potcar: Parsed POTCAR file.
        incar: Parsed INCAR file with NELECT.

    Returns:
        Defect charge state (negative of excess electrons).

    Raises:
        ValueError: If POSCAR and POTCAR element order differs.

    Example:
        >>> charge = calculate_charge_state(poscar, potcar, incar)
        >>> print(charge)
        2
    """
    nelect = incar.get("NELECT", None)
    if nelect is None:
        logger.info("Since NELECT is not written in INCAR, so 0 is returned.")
        return 0
    potcar_elements = [symbol.split("_")[0] for symbol in potcar.symbols]
    if poscar.site_symbols != potcar_elements:
        raise ValueError(f"Sequence of elements in POSCAR {poscar.site_symbols}"
                         f" and that in POTCAR {potcar.symbols} is different.")
    num_elect_neutral = sum([num_atom * pot.nelectrons
                             for num_atom, pot in zip(poscar.natoms, potcar)])
    excess_num_electrons = int(nelect - num_elect_neutral)
    return - excess_num_electrons


# Backward compatibility alias
get_defect.vasp_utils = calculate_charge_state
