# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for band edge analysis."""

from pymatgen.io.vasp import Vasprun, Procar, Outcar

from pydefect.analysis.band_edge.make_band_edge_states import (
    make_band_edge_states as _make_band_edge_states,
)
from pydefect.analysis.band_edge.make_perfect_band_edge_state import (
    make_perfect_band_edge_state_from_vasp as _make_perfect_band_edge_state,
)
from pydefect.analysis.band_edge.make_band_edge_orbital_infos import (
    make_band_edge_orbital_infos as _make_band_edge_orbital_infos,
)


def make_perfect_band_edge_state(
    procar: Procar,
    vasprun: Vasprun,
    outcar: Outcar,
):
    """Create PerfectBandEdgeState from VASP outputs.

    Args:
        procar: Procar object from perfect supercell.
        vasprun: Vasprun object from perfect supercell.
        outcar: Outcar object from perfect supercell.

    Returns:
        PerfectBandEdgeState object.

    Example:
        >>> from pydefect import api
        >>> p_state = api.make_perfect_band_edge_state(procar, vasprun, outcar)
        >>> p_state.to_json_file()
    """
    return _make_perfect_band_edge_state(procar, vasprun, outcar)


def make_band_edge_orbital_infos(
    procar: Procar,
    vasprun: Vasprun,
    supercell_vbm: float,
    supercell_cbm: float,
    defect_structure_info=None,
    eigval_shift: float = 0.0,
):
    """Create BandEdgeOrbitalInfos from VASP outputs.

    Args:
        procar: Procar object.
        vasprun: Vasprun object.
        supercell_vbm: VBM energy of supercell.
        supercell_cbm: CBM energy of supercell.
        defect_structure_info: Optional DefectStructureInfo.
        eigval_shift: Energy shift for eigenvalues.

    Returns:
        BandEdgeOrbitalInfos object.

    Example:
        >>> from pydefect import api
        >>> orb_infos = api.make_band_edge_orbital_infos(
        ...     procar, vasprun, vbm, cbm
        ... )
        >>> orb_infos.to_json_file()
    """
    return _make_band_edge_orbital_infos(
        procar, vasprun, supercell_vbm, supercell_cbm,
        defect_structure_info, eigval_shift=eigval_shift,
    )


def make_band_edge_states(
    band_edge_orbital_infos,
    perfect_band_edge_state,
    defect_charge_info=None,
):
    """Determine band edge states from orbital information.

    Args:
        band_edge_orbital_infos: BandEdgeOrbitalInfos object.
        perfect_band_edge_state: PerfectBandEdgeState from perfect calculation.
        defect_charge_info: Optional DefectChargeInfo object.

    Returns:
        BandEdgeStates object.

    Example:
        >>> from pydefect import api
        >>> states = api.make_band_edge_states(orb_infos, p_state)
        >>> states.to_json_file()
    """
    return _make_band_edge_states(
        band_edge_orbital_infos,
        perfect_band_edge_state,
        defect_charge_info,
    )
