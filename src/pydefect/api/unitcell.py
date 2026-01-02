# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for unitcell creation from VASP outputs."""

from typing import Optional

from pymatgen.io.vasp import Vasprun, Outcar

from pydefect.analysis.unitcell.unitcell import Unitcell
from pydefect.analysis.unitcell.make_unitcell import make_unitcell_from_vasp as _make_unitcell


def make_unitcell_from_vasp(
    vasprun_band: Vasprun,
    outcar_band: Outcar,
    outcar_dielectric_clamped: Optional[Outcar] = None,
    outcar_dielectric_ionic: Optional[Outcar] = None,
    system_name: Optional[str] = None,
) -> Unitcell:
    """Create Unitcell object from VASP outputs.

    Args:
        vasprun_band: Vasprun from band structure calculation.
        outcar_band: Outcar from band structure calculation.
        outcar_dielectric_clamped: Outcar with clamped-ion dielectric tensor.
        outcar_dielectric_ionic: Outcar with ionic dielectric contribution.
        system_name: Optional name for the system.

    Returns:
        Unitcell object containing band edges and dielectric properties.

    Example:
        >>> from pydefect import api
        >>> from pymatgen.io.vasp import Vasprun, Outcar
        >>> unitcell = api.make_unitcell_from_vasp(
        ...     Vasprun("band/vasprun.xml"),
        ...     Outcar("band/OUTCAR"),
        ...     Outcar("dielectric/OUTCAR"),
        ... )
        >>> unitcell.to_yaml_file()
    """
    return _make_unitcell(
        vasprun_band=vasprun_band,
        outcar_band=outcar_band,
        outcar_dielectric_clamped=outcar_dielectric_clamped,
        outcar_dielectric_ionic=outcar_dielectric_ionic,
        system_name=system_name,
    )
