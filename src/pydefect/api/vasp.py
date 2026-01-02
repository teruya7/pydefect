# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for VASP-specific functionality.

This module provides functions for creating pydefect objects
from VASP calculation outputs.
"""

from pathlib import Path
from typing import List, Optional, Union

from pymatgen.core import Structure
from pymatgen.io.vasp import Vasprun, Outcar, Procar, Chgcar

from pydefect.analyzer.calculation.calc_results import CalcResults
from pydefect.analyzer.unitcell.unitcell import Unitcell
from pydefect.analyzer.chemical_potential.chem_pot_diag import CompositionEnergy, CompositionEnergies
from pydefect.analyzer.unitcell.make_unitcell import make_unitcell_from_vasp as _make_unitcell
from pydefect.analyzer.calculation.make_calc_results import make_calc_results_from_vasp as _make_calc_results
from pydefect.input_maker.make_local_extrema import make_local_extrema_from_volumetric_data
from pydefect.analyzer.band_edge.make_perfect_band_edge_state import (
    make_perfect_band_edge_state_from_vasp as _make_perfect_band_edge_state,
)
from pydefect.analyzer.band_edge.make_band_edge_orbital_infos import (
    make_band_edge_orbital_infos as _make_band_edge_orbital_infos,
)
from pydefect.input_maker.defect_entries_maker import DefectEntriesMaker
from pydefect.input_maker.defect_set import DefectSet
from pydefect.input_maker.local_extrema import VolumetricDataAnalyzeParams, VolumetricDataLocalExtrema
from pydefect.input_maker.supercell_info import SupercellInfo


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


def make_calc_results_from_vasp(
    vasprun: Vasprun,
    outcar: Outcar,
) -> CalcResults:
    """Create CalcResults from VASP outputs.

    Args:
        vasprun: Vasprun object from calculation.
        outcar: Outcar object from calculation.

    Returns:
        CalcResults object containing structure, energy, and convergence info.

    Example:
        >>> from pydefect import api
        >>> calc_results = api.make_calc_results_from_vasp(
        ...     Vasprun("vasprun.xml", parse_potcar_file=False),
        ...     Outcar("OUTCAR"),
        ... )
        >>> calc_results.to_json_file()
    """
    return _make_calc_results(vasprun=vasprun, outcar=outcar)


def make_composition_energies(
    directories: List[Path],
    existing_composition_energies: Optional[CompositionEnergies] = None,
) -> CompositionEnergies:
    """Collect composition energies from multiple VASP calculations.

    Args:
        directories: List of directories containing VASP calculations.
        existing_composition_energies: Optional existing CompositionEnergies
            to update (lower energies will overwrite).

    Returns:
        CompositionEnergies object.

    Example:
        >>> from pydefect import api
        >>> comp_energies = api.make_composition_energies(
        ...     [Path("MgO"), Path("Mg"), Path("O2")]
        ... )
        >>> comp_energies.to_yaml_file()
    """
    from vise.defaults import defaults

    if existing_composition_energies:
        composition_energies = existing_composition_energies
    else:
        composition_energies = CompositionEnergies()

    for _dir in directories:
        outcar = Outcar(_dir / defaults.outcar)
        composition = Structure.from_file(_dir / defaults.contcar).composition
        energy = float(outcar.final_energy)
        ce = CompositionEnergy(energy, str(_dir))

        if composition in composition_energies:
            original = composition_energies[composition]
            if ce.energy > original.energy:
                continue  # Skip if new energy is higher

        composition_energies[composition] = ce

    return composition_energies


def make_local_extrema(
    volumetric_data: Union[Chgcar, List[Chgcar]],
    threshold_frac: Optional[float] = None,
    threshold_abs: Optional[float] = None,
    min_dist: float = 0.5,
    tol: float = 0.5,
    radius: float = 0.4,
    find_max: bool = False,
    supercell_info: Optional[SupercellInfo] = None,
) -> VolumetricDataLocalExtrema:
    """Find local extrema in volumetric data for interstitial sites.

    Args:
        volumetric_data: Chgcar or list of Chgcar to analyze.
        threshold_frac: Fractional threshold for extrema detection.
        threshold_abs: Absolute threshold for extrema detection.
        min_dist: Minimum distance between extrema.
        tol: Tolerance for grouping equivalent sites.
        radius: Radius for local extrema search.
        find_max: If True, find maxima instead of minima.
        supercell_info: Optional SupercellInfo for structure reference.

    Returns:
        LocalExtrema object containing found sites.

    Example:
        >>> from pydefect import api
        >>> from pymatgen.io.vasp import Chgcar
        >>> extrema = api.make_local_extrema(Chgcar.from_file("CHGCAR"))
        >>> extrema.to_json_file()
    """
    if isinstance(volumetric_data, list):
        vd = volumetric_data[0]
        for v in volumetric_data[1:]:
            vd += v
    else:
        vd = volumetric_data

    params = VolumetricDataAnalyzeParams(
        threshold_frac, threshold_abs, min_dist, tol, radius
    )

    return make_local_extrema_from_volumetric_data(
        volumetric_data=vd,
        params=params,
        info=supercell_info,
        find_min=not find_max,
    )


def make_defect_entries(
    supercell_info: SupercellInfo,
    defect_set: DefectSet,
):
    """Create defect entries from supercell info and defect set.

    Args:
        supercell_info: SupercellInfo object.
        defect_set: DefectSet object.

    Returns:
        List of DefectEntry objects.

    Example:
        >>> from pydefect import api
        >>> entries = api.make_defect_entries(supercell_info, defect_set)
        >>> for entry in entries:
        ...     entry.to_json_file(f"{entry.full_name}/defect_entry.json")
    """
    maker = DefectEntriesMaker(supercell_info, defect_set)
    return maker.defect_entries


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
