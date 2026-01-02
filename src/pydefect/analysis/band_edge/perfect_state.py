# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from pydefect.analysis.band_edge.models import PerfectBandEdgeState, EdgeInfo, \
    OrbitalInfo
from pydefect.analysis.band_edge.orbital_infos import \
    calc_orbital_character
from pymatgen.electronic_structure.core import Spin
from vise.defaults import defaults as v_defaults
from pymatgen.io.vasp import Procar, Vasprun, Outcar
from vise.analyzer.vasp.band_edge_properties import VaspBandEdgeProperties


def make_perfect_band_edge_state_from_vasp(
        procar: Procar, vasprun: Vasprun, outcar: Outcar
) -> PerfectBandEdgeState:
    """Create PerfectBandEdgeState from VASP output.

    Args:
        procar: Parsed PROCAR file.
        vasprun: Parsed vasprun.xml file.
        outcar: Parsed OUTCAR file.

    Returns:
        PerfectBandEdgeState with VBM and CBM info.

    Example:
        >>> procar = Procar("PROCAR")
        >>> vasprun = Vasprun("vasprun.xml")
        >>> outcar = Outcar("OUTCAR")
        >>> p_state = make_perfect_band_edge_state_from_vasp(procar, vasprun, outcar)
        >>> p_state.to_json_file()
    """
    band_edge_prop = VaspBandEdgeProperties(vasprun, outcar,
                                            v_defaults.integer_criterion)
    orbital_data, structure = procar.data, vasprun.final_structure
    vbm_info = create_edge_info_from_vasp(band_edge_prop.vbm_info, orbital_data, structure, vasprun)
    cbm_info = create_edge_info_from_vasp(band_edge_prop.cbm_info, orbital_data, structure, vasprun)
    return PerfectBandEdgeState(vbm_info, cbm_info)


def create_edge_info_from_vasp(edge_info, orbital_data, structure, vasprun) -> EdgeInfo:
    """Create EdgeInfo from VASP band edge properties.

    Args:
        edge_info: Band edge info from VaspBandEdgeProperties.
        orbital_data: Orbital projections from PROCAR.
        structure: Structure from vasprun.
        vasprun: Parsed vasprun.xml.

    Returns:
        EdgeInfo with orbital decomposition.
    """
    orbitals = calc_orbital_character(
        orbital_data, structure, Spin.up, edge_info.kpoint_index, edge_info.band_index)
    energy, occupation = vasprun.eigenvalues[Spin.up][edge_info.kpoint_index, edge_info.band_index, :]
    orb_info = OrbitalInfo(energy=energy, occupation=occupation, orbitals=orbitals)
    return EdgeInfo(edge_info.band_index, tuple(edge_info.kpoint_coords), orb_info)
