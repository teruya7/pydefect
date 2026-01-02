# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""Pydefect API - Clean programmatic interface for pydefect functionality.

This module provides a high-level API for pydefect functionality,
allowing users to access all features programmatically without CLI.
"""

from pydefect.api.structure import (
    make_supercell,
    make_defect_set,
    append_interstitial,
    pop_interstitial,
    make_local_extrema,
    make_defect_entries,
)
from pydefect.api.energies import (
    make_chem_pot_diag,
    make_standard_and_relative_energies,
    make_defect_energy_info,
    make_defect_energy_summary,
    make_composition_energies,
)
from pydefect.api.corrections import (
    make_efnv_correction,
    make_gkfo_correction,
)
from pydefect.api.analysis import (
    make_defect_structure_info,
    make_band_edge_states,
    make_calc_summary,
    plot_defect_energy,
    make_unitcell_from_vasp,
    make_calc_results_from_vasp,
    make_perfect_band_edge_state,
    make_band_edge_orbital_infos,
)
from pydefect.api.util import (
    print_json,
    make_defect_vesta_file,
)

__all__ = [
    # structure
    "make_supercell",
    "make_defect_set",
    "append_interstitial",
    "pop_interstitial",
    "make_local_extrema",
    "make_defect_entries",
    # energies
    "make_chem_pot_diag",
    "make_standard_and_relative_energies",
    "make_defect_energy_info",
    "make_defect_energy_summary",
    "make_composition_energies",
    # corrections
    "make_efnv_correction",
    "make_gkfo_correction",
    # analysis
    "make_defect_structure_info",
    "make_band_edge_states",
    "make_calc_summary",
    "plot_defect_energy",
    "make_unitcell_from_vasp",
    "make_calc_results_from_vasp",
    "make_perfect_band_edge_state",
    "make_band_edge_orbital_infos",
    # util
    "print_json",
    "make_defect_vesta_file",
]
