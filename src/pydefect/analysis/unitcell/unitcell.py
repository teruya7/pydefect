# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Create Unitcell from VASP output files."""

from pydefect.analysis.unitcell.models import Unitcell
from pymatgen.io.vasp import Vasprun, Outcar
from vise.analyzer.vasp.band_edge_properties import VaspBandEdgeProperties


def create_unitcell_from_vasp(vasprun_band: Vasprun,
                               outcar_band: Outcar,
                               outcar_dielectric_clamped: Outcar,
                               outcar_dielectric_ionic: Outcar,
                               system_name: str = None) -> Unitcell:
    """Create Unitcell from VASP output files.

    Args:
        vasprun_band: vasprun.xml from band calculation.
        outcar_band: OUTCAR from band calculation.
        outcar_dielectric_clamped: OUTCAR from clamped dielectric calculation.
        outcar_dielectric_ionic: OUTCAR from ionic dielectric calculation.
        system_name: Optional system name override.

    Returns:
        Unitcell with band edges and dielectric constants.

    Example:
        >>> unitcell = create_unitcell_from_vasp(
        ...     vasprun_band, outcar_band,
        ...     outcar_diele_clamped, outcar_diele_ionic
        ... )
        >>> unitcell.to_yaml_file()
    """
    name = (system_name or
            vasprun_band.final_structure.composition.reduced_formula)
    outcar_dielectric_clamped.read_lepsilon()
    outcar_dielectric_ionic.read_lepsilon_ionic()
    band_edge_properties = VaspBandEdgeProperties(vasprun_band, outcar_band)
    vbm, cbm = band_edge_properties.vbm_cbm

    return Unitcell(
        system=name,
        vbm=float(vbm), cbm=float(cbm),
        ele_dielectric_const=outcar_dielectric_clamped.dielectric_tensor,
        ion_dielectric_const=outcar_dielectric_ionic.dielectric_ionic_tensor)


# Backward compatibility alias
make_unitcell_from_vasp = create_unitcell_from_vasp
