# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
"""Concentration plotting functions."""

from collections import defaultdict
from typing import List

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pydefect.analysis.concentration.models import ConcentrationByFermiLevel
from vise.util.matplotlib import float_to_int_formatter


def plot_carrier_concentrations(ccs: List[ConcentrationByFermiLevel],
                      concentration_ranges: List[float] = None,
                      energy_ranges: List[float] = None):
    """Plot multiple carrier concentration curves.

    Args:
        ccs: List of ConcentrationByFermiLevel objects.
        concentration_ranges: Optional y-axis range as [log10_min, log10_max].
        energy_ranges: Optional x-axis range as [E_min, E_max].

    Example:
        >>> plot_multiple_pns(concentrations)
        >>> plt.savefig("carrier_concentration.pdf")
    """
    from matplotlib import pyplot as plt
    ax = plt.gca()
    for cc, style in zip(ccs, ["-", "-.", "--", ":"]):
        plot_single_carrier_concentration(cc, ax, style)

    if concentration_ranges:
        ax.set_ylim([10 ** i for i in concentration_ranges])

    if energy_ranges:
        ax.set_xlim(energy_ranges)

    plt.xlabel("Fermi level (eV)")
    plt.ylabel("Concentration")
    plt.legend()


def plot_single_carrier_concentration(cc: ConcentrationByFermiLevel, ax: Axes, style: str = "-"):
    """Plot p and n carrier concentrations vs Fermi level.

    Args:
        cc: ConcentrationByFermiLevel data.
        ax: Matplotlib axes to plot on.
        style: Line style string.
    """
    Efs, ps, ns = [], [], []
    for c in cc.concentrations:
        Efs.append(c.Ef)
        ps.append(c.carrier.p)
        ns.append(c.carrier.n)

    ax.set_yscale("log")
    ax.plot(Efs, ps, color="red", linestyle=style, label=cc.T)
    ax.plot(Efs, ns, color="blue", linestyle=style)
    ax.legend()


class DefectConcentrationMplPlotter:
    """Matplotlib plotter for defect concentrations.

    Plots defect concentrations vs Fermi level.

    Attributes:
        con_by_Ef: ConcentrationByFermiLevel data.
        plt: Matplotlib pyplot module.
        ax: Current axes.
    """
    def __init__(self,
                 con_by_Ef: ConcentrationByFermiLevel,
                 **plot_settings):
        """Initialize DefectConcentrationMplPlotter.

        Args:
            con_by_Ef: Concentration data by Fermi level.
            **plot_settings: Additional plot settings.
        """
        self.con_by_Ef = con_by_Ef
        self.plt = plt
        self.ax = plt.gca()

    def construct_plot(self):
        """Build the complete plot."""
        self._plot_defect_concentration()
        self._set_scale()
        self._set_labels()
        self._set_legend()
        self._set_formatter()

    def _plot_defect_concentration(self):
        Efs, ddd = [], defaultdict(list)
        for cc in self.con_by_Ef.concentrations:
            Efs.append(cc.Ef)
            for defect in cc.defects:
                ddd[defect.name].append(defect.total_concentration)

        for name, dd in ddd.items():
            self.ax.plot(Efs, dd, label=name)

    def _set_scale(self):
        self.ax.set_yscale("log")

    def _set_labels(self):
        self.plt.xlabel(f"Fermi level (eV)")
        self.plt.ylabel("Concentration (cm$^{-3}$)")

    def _set_formatter(self):
        axis = self.plt.gca()
        axis.xaxis.set_major_formatter(float_to_int_formatter)

    def _set_legend(self):
        self.ax.legend(bbox_to_anchor=(0.9, 0.5), loc='center left')