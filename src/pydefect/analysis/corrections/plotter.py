# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Site potential plotting functions."""

from itertools import groupby, cycle
from typing import Optional, List

from matplotlib import pyplot as plt
from pydefect.analysis.corrections.models import (
    ExtendedFnvCorrection,
    PotentialSite,
    GkfoCorrection,
)
from pydefect.defaults import defaults
from vise.util.matplotlib import float_to_int_formatter


class PotentialPlotterMplSettings:
    """Matplotlib settings for site potential plots.

    Configures colors, line styles, and fonts for potential visualization.

    Attributes:
        colors: Color cycle for different elements.
        line_width: Line width for data.
        circle_size: Marker size.
        tick_label_size: Font size for tick labels.
        title_font_size: Font size for titles.
        label_font_size: Font size for axis labels.
        vline: Vertical line style dict.
        hline: Horizontal line style dict.
        zero_line: Zero line style dict.

    Example:
        >>> settings = PotentialPlotterMplSettings(circle_size=20)
    """
    def __init__(self,
                 colors: Optional[List[str]] = None,
                 line_width: float = 1.0,
                 radius_line_width: float = 1.0,
                 radius_line_color: str = "black",
                 radius_line_style: str = "-.",
                 ave_pot_diff_line_width: float = 1.5,
                 ave_pot_diff_line_color: str = "red",
                 ave_pot_diff_line_style: str = ":",
                 circle_size: int = 15,
                 zero_line_width: float = 0.5,
                 zero_line_color: str = "black",
                 zero_line_style: str = ":",
                 tick_label_size: Optional[int] = 12,
                 title_font_size: Optional[int] = 15,
                 label_font_size: Optional[int] = 15):
        """Initialize PotentialPlotterMplSettings.

        Args:
            colors: List of colors. Uses defaults if None.
            line_width: Line width for data.
            radius_line_width: Width for radius indicator.
            radius_line_color: Color for radius line.
            radius_line_style: Style for radius line.
            ave_pot_diff_line_width: Width for average potential line.
            ave_pot_diff_line_color: Color for average line.
            ave_pot_diff_line_style: Style for average line.
            circle_size: Marker size.
            zero_line_width: Width for zero line.
            zero_line_color: Color for zero line.
            zero_line_style: Style for zero line.
            tick_label_size: Font size for ticks.
            title_font_size: Font size for title.
            label_font_size: Font size for labels.
        """
        self.colors = cycle(colors) if colors else defaults.defect_energy_colors
        self.line_width = line_width
        self.circle_size = circle_size
        self.tick_label_size = tick_label_size
        self.title_font_size = title_font_size
        self.label_font_size = label_font_size

        self.vline = {"linewidth": radius_line_width,
                      "color": radius_line_color,
                      "linestyle": radius_line_style}

        self.hline = {"linewidth": ave_pot_diff_line_width,
                      "color": ave_pot_diff_line_color,
                      "linestyle": ave_pot_diff_line_style}

        self.zero_line = {"linewidth": zero_line_width,
                          "color": zero_line_color,
                          "linestyle": zero_line_style}


class SitePotentialPlotter:
    """Base class for site potential plotting.

    Visualizes electrostatic potentials at atomic sites for
    defect correction analysis.

    Attributes:
        sites: List of PotentialSite objects.
        defect_region_radius: Radius of defect region in Angstroms.
        ave_pot_diff: Average potential difference for alignment.

    Example:
        >>> plotter = SitePotentialMplPlotter.from_efnv_corr(
        ...     title="Va_O1_2", efnv_correction=correction
        ... )
        >>> plotter.construct_plot()
    """
    def __init__(self,
                 title: str,
                 sites: List[PotentialSite],
                 defect_region_radius: Optional[float] = None,
                 ave_pot_diff: Optional[float] = None,
                 x_unit: Optional[str] = "Å",
                 y_unit: Optional[str] = "V",
                 **kwargs):
        """Initialize site potential plotter.

        Args:
            title: Plot title (typically defect name).
            sites: List of PotentialSite objects to plot.
            defect_region_radius: Defect region cutoff radius in Å.
            ave_pot_diff: Average potential difference in V.
            x_unit: Unit label for x-axis (distance).
            y_unit: Unit label for y-axis (potential).
            **kwargs: Additional settings.
        """
        self._title = title
        self.sites = sites
        self.defect_region_radius = defect_region_radius
        self.ave_pot_diff = ave_pot_diff

        self._x_unit = x_unit
        self._y_unit = y_unit

    @classmethod
    def from_efnv_corr(cls,
                       title,
                       efnv_correction: ExtendedFnvCorrection,
                       x_unit: Optional[str] = "Å",
                       y_unit: Optional[str] = "V",
                       **kwargs):
        return cls(title=title,
                   sites=efnv_correction.sites,
                   defect_region_radius=efnv_correction.defect_region_radius,
                   ave_pot_diff=efnv_correction.average_potential_diff,
                   x_unit=x_unit, y_unit=y_unit, **kwargs)

    @classmethod
    def from_gkfo_corr(cls,
                       title,
                       gkfo_correction: GkfoCorrection,
                       x_unit: Optional[str] = "Å",
                       y_unit: Optional[str] = "V"):
        efnv = gkfo_correction.init_efnv_correction
        ave_pot_diff = gkfo_correction.average_potential_diff_by_addition
        return cls(title=title,
                   sites=gkfo_correction.gkfo_sites,
                   defect_region_radius=efnv.defect_region_radius,
                   ave_pot_diff=ave_pot_diff,
                   x_unit=x_unit, y_unit=y_unit)



class SitePotentialMplPlotter(SitePotentialPlotter):
    """Matplotlib plotter for site potentials.

    Attributes:
        plt: Matplotlib pyplot module.

    Example:
        >>> plotter = SitePotentialMplPlotter.from_efnv_corr(
        ...     title="Va_O1_2", efnv_correction=correction
        ... )
        >>> plotter.construct_plot()
        >>> plotter.plt.savefig("site_potential.pdf")
    """
    def __init__(self, **kwargs):
        """Initialize matplotlib plotter.

        Args:
            **kwargs: Arguments passed to SitePotentialPlotter.
                Also accepts 'mpl_defaults' for PotentialPlotterMplSettings.
        """
        super().__init__(**kwargs)
        self._mpl_defaults = kwargs.get("mpl_defaults",
                                        PotentialPlotterMplSettings())
        self.plt = plt

    def construct_plot(self):
        self._add_potentials()
        self._add_lines()
        self._set_labels()
        self._set_x_range()
        self._set_title()
        self._set_formatter()
        self.plt.tight_layout()
#        self.plt.gca().legend(bbox_to_anchor=(1, 0.5), loc='center left')

    def _add_potentials(self):
        all_distances = []
        pc_pot_distances = []
        pc_potentials = []
        potential_diffs = []
        key = lambda x: x.specie
        for _, grouped_sites in groupby(sorted(self.sites, key=key), key=key):
            distances = []
            potentials = []
            for site in grouped_sites:
                distances.append(site.distance)
                all_distances.append(site.distance)
                potentials.append(site.potential)

                if site.pc_potential:
                    pc_pot_distances.append(site.distance)
                    pc_potentials.append(site.pc_potential)
                    potential_diffs.append(site.diff_pot)

            color = next(self._mpl_defaults.colors)
            self.plt.scatter(distances, potentials, marker="o", color=color,
                             label=str(site.specie))

        self._max_distance = max(all_distances)

        self.plt.scatter(pc_pot_distances, pc_potentials, marker="1",
                         color="b", label="point charge")
        self.plt.scatter(pc_pot_distances, potential_diffs, marker="+",
                         color="r", label="potential difference")

        self.plt.legend(bbox_to_anchor=(0, 1.05), loc='upper left',
                        borderaxespad=0, fontsize=8)

    def _add_lines(self):
        if self.defect_region_radius:
            self.plt.axvline(x=self.defect_region_radius,
                             **self._mpl_defaults.vline)
        if self.defect_region_radius and self.ave_pot_diff:
            self.plt.plot([self.defect_region_radius, self._max_distance * 1.1],
                          [self.ave_pot_diff, self.ave_pot_diff],
                          **self._mpl_defaults.hline)
        self.plt.axhline(y=0, **self._mpl_defaults.zero_line)

    def _set_x_range(self):
        self.plt.xlim(0, self._max_distance * 1.05)

    def _set_title(self):
        self.plt.title(self._title, size=self._mpl_defaults.title_font_size)

    def _set_labels(self):
        self.plt.xlabel(f"Distance from a defect ({self._x_unit})",
                        size=self._mpl_defaults.label_font_size)
        self.plt.ylabel(f"Potential ({self._y_unit})",
                        size=self._mpl_defaults.label_font_size)

    def _set_formatter(self):
        axis = self.plt.gca()
        axis.xaxis.set_major_formatter(float_to_int_formatter)
        axis.yaxis.set_major_formatter(float_to_int_formatter)
        axis.tick_params(labelsize=self._mpl_defaults.tick_label_size)