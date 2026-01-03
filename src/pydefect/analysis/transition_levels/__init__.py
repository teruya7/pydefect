# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
"""Transition levels analysis module.

Public API:
- Models: TransitionLevel, TransitionLevels
- Functions: calculate_transition_levels, calculate_pinning_levels
- Plotting: PlotData, TransitionLevelsPlotter, create_plot_data
"""

# Data models
from pydefect.analysis.transition_levels.models import (
    TransitionLevel,
    TransitionLevels,
)

# Calculation functions
from pydefect.analysis.transition_levels.transition_levels import (
    calculate_transition_levels,
    # Backward compatibility
    make_transition_levels,
)

# Pinning levels
from pydefect.analysis.transition_levels.pinning import (
    calculate_pinning_levels,
    # Backward compatibility
    pinning_levels_from_charge_energies,
)

# Plotting
from pydefect.analysis.transition_levels.plotter import (
    PlotData,
    TransitionLevelsPlotter,
    create_plot_data,
    # Backward compatibility
    MplTLData,
    make_mpl_tl_data,
    TransitionLevelsMplPlotter,
)

__all__ = [
    # Models
    "TransitionLevel",
    "TransitionLevels",
    # Functions
    "calculate_transition_levels",
    "calculate_pinning_levels",
    # Plotting
    "PlotData",
    "TransitionLevelsPlotter",
    "create_plot_data",
    # Backward compatibility
    "make_transition_levels",
    "pinning_levels_from_charge_energies",
    "MplTLData",
    "make_mpl_tl_data",
    "TransitionLevelsMplPlotter",
]
