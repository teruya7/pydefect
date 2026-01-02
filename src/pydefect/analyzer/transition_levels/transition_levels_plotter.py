# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple

from pydefect.analyzer.transition_levels.transition_levels import TransitionLevels
from matplotlib import pyplot as plt


@dataclass
class MplTLData:
    """Data for matplotlib transition level plots.

    Attributes:
        labels: Defect name labels.
        charges: Charge states.
        tl_energy_widths: Energy widths per charge.
        piled_tl_energy_widths: Cumulative energy widths.

    Example:
        >>> data = make_mpl_tl_data(transition_levels)
        >>> print(data.labels)
    """
    labels: List[str]
    charges: List[int]
    tl_energy_widths: List[List[float]]
    piled_tl_energy_widths: List[List[float]]


def make_mpl_tl_data(transition_levels: TransitionLevels) -> MplTLData:
    """Create MplTLData from TransitionLevels.

    Args:
        transition_levels: TransitionLevels data.

    Returns:
        MplTLData for plotting.
    """
    labels = []
    tls = transition_levels.transition_levels
    charges = sum(sum([tl.charges for tl in tls], []), [])
    charge_set = list(range(max(charges), min(charges) - 1, -1))

    piled_tl_energy_widths = []
    for charge in charge_set:
        inner = []
        for tl in tls:
            for c, fl in zip(tl.charges, tl.fermi_levels):
                if tl.charges[0] == charge:
                    inner.append(tl.fermi_levels)

    return MplTLData(labels=labels,
                     charges=charge_set,
                     tl_energy_widths=[[1.0, 0.0], [1.0, 0.0], [1.0, 0.0],
                                           [0.0, 2.0], [0.0, 1.0]],
                     piled_tl_energy_widths=[[1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [3.0, 3.0]])


class TransitionLevelsMplPlotter:
    """Matplotlib plotter for transition level diagrams.

    Attributes:
        plt: Matplotlib pyplot module.

    Example:
        >>> plotter = TransitionLevelsMplPlotter(transition_levels)
        >>> plotter.plt.savefig("transition_levels.pdf")
    """

    def __init__(self,
                 transition_levels: TransitionLevels = None,
                 y_unit: Optional[str] = "eV"):
        """Initialize TransitionLevelsMplPlotter.

        Args:
            transition_levels: TransitionLevels data to plot.
            y_unit: Unit label for y-axis energy.
        """
        width = 0.35
#        for tl in transition_levels.transition_levels:
        tls_m2 = [0.0, 1.0]
        tls_m1 = [0.0, 1.0]
        tls_n = [1.0, 1.0]
        tls_p1 = [1.0, 0.0]
        tls_p2 = [1.0, 0.0]

        plt.bar(["Va_O1", "Va_Mg1"], tls_m2, width, label='-2')
        plt.bar(["Va_O1", "Va_Mg1"], tls_m1, width, label='-1', bottom=tls_m2)
        # plt.bar(["Va_O1", "Va_Mg1"], tls_n, width, label='0', bottom=)
#        plt.bar(["Va_O1", "Va_Mg1"], tls_p1, width, label='+1')
#        plt.bar(["Va_O1", "Va_Mg1"], tls_p2, width, label='+2')

        self.plt = plt