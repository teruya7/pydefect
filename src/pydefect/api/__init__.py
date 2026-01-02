# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Pydefect API - Clean programmatic interface for pydefect functionality.

This module provides a high-level API for pydefect functionality,
allowing users to access all features programmatically without CLI.
"""

from pydefect.api.supercell import (
    make_supercell,
)
from pydefect.api.unitcell import (
    make_unitcell_from_vasp,
)
from pydefect.api.chemical_potential import (
    make_composition_energies,
    make_standard_and_relative_energies,
    make_chem_pot_diag,
)
from pydefect.api.defect import (
    make_defect_set,
    make_defect_entries,
    append_interstitial,
    pop_interstitial,
    make_local_extrema,
    make_defect_structure_info,
    make_defect_vesta_file,
    make_defect_energy_info,
    make_defect_energy_summary,
    plot_defect_energy,
)
from pydefect.api.band_edge import (
    make_perfect_band_edge_state,
    make_band_edge_orbital_infos,
    make_band_edge_states,
)
from pydefect.api.calculation import (
    make_calc_results_from_vasp,
    make_calc_summary,
)
from pydefect.api.corrections import (
    make_efnv_correction,
    make_gkfo_correction,
)
from pydefect.api.util import (
    print_json,
)

__all__ = [
    # supercell
    "make_supercell",
    # unitcell
    "make_unitcell_from_vasp",
    # chemical_potential
    "make_composition_energies",
    "make_standard_and_relative_energies",
    "make_chem_pot_diag",
    # defect
    "make_defect_set",
    "make_defect_entries",
    "append_interstitial",
    "pop_interstitial",
    "make_local_extrema",
    "make_defect_structure_info",
    "make_defect_vesta_file",
    "make_defect_energy_info",
    "make_defect_energy_summary",
    "plot_defect_energy",
    # band_edge
    "make_perfect_band_edge_state",
    "make_band_edge_orbital_infos",
    "make_band_edge_states",
    # calculation
    "make_calc_results_from_vasp",
    "make_calc_summary",
    # corrections
    "make_efnv_correction",
    "make_gkfo_correction",
    # util
    "print_json",
]
