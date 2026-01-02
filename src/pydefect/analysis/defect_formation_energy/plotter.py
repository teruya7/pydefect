# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Formation energy plotting utilities."""
from itertools import cycle
from typing import List, Optional, Tuple

from adjustText import adjust_text
from labellines import labelLines
from matplotlib import pyplot as plt
from pydefect.analysis.defect_formation_energy.models import FormationEnergySummary
from pydefect.analysis.transition_levels.transition_levels import make_transition_levels
from pydefect.defaults import defaults
from vise.util.matplotlib import float_to_int_formatter


class PlotSettings:
    """Matplotlib settings for formation energy plots.

    Configures colors, line widths, and font sizes for visualization.

    Attributes:
        colors: Color cycle for defect lines.
        line_width: Width of energy lines.
        thin_line_width: Width of thin/secondary lines.
        circle_size: Size of markers.
        tick_label_size: Font size for tick labels.
        title_font_size: Font size for titles.
        label_font_size: Font size for axis labels.
        defect_name_size: Font size for defect names.
        charge_size: Font size for charge labels.
        vline: Dict of vertical line style settings.

    Example:
        >>> settings = PlotSettings(
        ...     line_width=2.0,
        ...     title_font_size=18
        ... )
    """
    def __init__(self,
                 colors: Optional[List[str]] = None,
                 line_width: float = 1.0,
                 thin_line_width: float = 0.3,
                 vline_width: float = 0.5,
                 vline_color: str = "black",
                 vline_style: str = "-.",
                 vline_alpha: float = 0.7,
                 circle_size: int = 15,
                 tick_label_size: Optional[int] = 12,
                 title_font_size: Optional[int] = 15,
                 label_font_size: Optional[int] = 15,
                 defect_name_size: Optional[int] = 12,
                 charge_size: Optional[int] = 12):
        """Initialize PlotSettings.

        Args:
            colors: List of colors for defects. Uses defaults if None.
            line_width: Line width for energy lines.
            thin_line_width: Width for secondary lines.
            vline_width: Width for vertical lines.
            vline_color: Color for vertical lines.
            vline_style: Line style for vertical lines.
            vline_alpha: Transparency for vertical lines.
            circle_size: Marker size.
            tick_label_size: Font size for ticks.
            title_font_size: Font size for title.
            label_font_size: Font size for axis labels.
            defect_name_size: Font size for defect names.
            charge_size: Font size for charges.
        """
        self.colors = cycle(colors) if colors else defaults.defect_energy_colors
        self.line_width = line_width
        self.thin_line_width = thin_line_width
        self.circle_size = circle_size
        self.tick_label_size = tick_label_size
        self.title_font_size = title_font_size
        self.label_font_size = label_font_size
        self.defect_name_size = defect_name_size
        self.charge_size = charge_size

        self.vline = {"linewidth": vline_width,
                      "color":     vline_color,
                      "linestyle": vline_style,
                      "alpha": vline_alpha}


class FormationEnergyPlotterBase:
    """Base class for defect formation energy plots.

    Prepares data for plotting defect energies vs Fermi level.

    Attributes:
        charge_energies: FermiLevelDependentEnergies for plotting.
        with_corrections: Whether corrections are applied.
    """
    def __init__(self,
                 formation_energy_summary: FormationEnergySummary,
                 chem_pot_label: str,
                 allow_shallow: bool,
                 with_corrections: bool,
                 name_style: Optional[str],
                 x_range: Optional[Tuple[float, float]] = None,
                 y_range: Optional[Tuple[float, float]] = None,
                 vline_threshold: float = 0.02,
                 x_unit: Optional[str] = "eV",
                 y_unit: Optional[str] = "eV",
                 **plot_settings):
        """Initialize formation energy plotter.

        Args:
            formation_energy_summary: FormationEnergySummary object.
            chem_pot_label: Label for chemical potential vertex.
            allow_shallow: If True, include shallow defects.
            with_corrections: If True, apply energy corrections.
            name_style: Name formatting style (e.g., "mpl").
            x_range: Fermi level range (min, max) in eV.
            y_range: Energy range (min, max) in eV.
            vline_threshold: Threshold for vertical lines.
            x_unit: Unit label for x-axis.
            y_unit: Unit label for y-axis.
            **plot_settings: Additional matplotlib settings.
        """
        self._title = formation_energy_summary.latexified_title
        self._supercell_vbm = formation_energy_summary.supercell_vbm
        self._supercell_cbm = formation_energy_summary.supercell_cbm
        self._x_range = x_range or (0, formation_energy_summary.cbm)
        formation_energy_summary.e_min = self._x_range[0]
        formation_energy_summary.e_max = self._x_range[1]

        fermi_level_energies = formation_energy_summary.get_fermi_level_energies(
            chem_pot_label, allow_shallow, with_corrections, self._x_range)
        tls = make_transition_levels(fermi_level_energies.cross_point_dicts,
                                     formation_energy_summary.cbm,
                                     self._supercell_vbm,
                                     self._supercell_cbm)
        tls.to_json_file()

        # Run again to change name to mpl style.
        fermi_level_energies = formation_energy_summary.get_fermi_level_energies(
            chem_pot_label, allow_shallow, with_corrections, self._x_range,
            name_style)
        self.charge_energies = fermi_level_energies
        self.with_corrections = with_corrections
        self._cross_points = fermi_level_energies.cross_point_dicts
        self._e_min_max_energies_dict = fermi_level_energies.e_min_max_energies_dict
        self._y_range = y_range or fermi_level_energies.energy_range(space=0.2)
        self._vline_threshold = vline_threshold
        self._x_unit = x_unit
        self._y_unit = y_unit
        self._formation_energies = \
            formation_energy_summary.filter_shallow_defects(allow_shallow)


class FormationEnergyMplPlotter(FormationEnergyPlotterBase):
    """Matplotlib plotter for defect formation energies.

    Creates publication-quality defect energy diagrams.

    Attributes:
        plt: Matplotlib pyplot module.

    Example:
        >>> plotter = FormationEnergyMplPlotter(
        ...     formation_energy_summary=summary,
        ...     chem_pot_label="A",
        ...     allow_shallow=False,
        ...     with_corrections=True
        ... )
        >>> plotter.construct_plot()
        >>> plotter.plt.savefig("formation_energy.pdf")
    """
    def __init__(self,
                 label_line: bool = True,
                 add_charges: bool = True,
                 add_thin_lines: bool = True,
                 **kwargs):
        """Initialize matplotlib plotter.

        Args:
            label_line: If True, add labels on lines.
            add_charges: If True, show charge states.
            add_thin_lines: If True, add thin background lines.
            **kwargs: Arguments passed to FormationEnergyPlotterBase.
        """
        super().__init__(name_style="mpl", **kwargs)
        self._mpl_defaults = kwargs.get("mpl_defaults", PlotSettings())
        self._label_line = label_line
        self._add_charges = add_charges
        self._add_thin_lines = add_thin_lines
        self.plt = plt
        self._texts = []

    def construct_plot(self):
        """Construct the complete formation energy plot."""
        self._add_energies()
        self._add_band_edges()
        self._set_x_range()
        self._set_y_range()
        self._set_labels()
        self._set_title()
        self._set_formatter()

        if self._add_charges:
            adjust_text(self._texts, force_points=(1.0, 2.5))

        if self._label_line:
            labelLines(plt.gca().get_lines(),
                       align=False,
                       fontsize=self._mpl_defaults.defect_name_size)
        else:
            ax = self.plt.gca()
            ax.legend(bbox_to_anchor=(1, 0.5), loc='center left')

        self.plt.tight_layout()

    def _add_energies(self):
        """Add defect energy lines to plot."""
        for defect_name, cross_point in self._cross_points.items():
            color = next(self._mpl_defaults.colors)
            self.plt.plot(*cross_point.t_all_sorted_points, color=color,
                          linewidth=self._mpl_defaults.line_width,
                          label=defect_name)
            if cross_point.t_inner_cross_points:
                self.plt.scatter(*cross_point.t_inner_cross_points, marker="o",
                                 color=color, s=self._mpl_defaults.circle_size)
            if self._add_charges:
                self._texts.extend(
                    [self.plt.text(x_pos, y_pos, charge, color=color,
                                   fontsize=self._mpl_defaults.charge_size)
                     for charge, (x_pos, y_pos) in cross_point.annotated_charge_positions.items()])

            if self._add_thin_lines:
                for energy_segment in self._e_min_max_energies_dict[defect_name]:
                    self.plt.plot(self._x_range, energy_segment, color=color,
                                  linewidth=self._mpl_defaults.thin_line_width)

    def _set_x_range(self):
        self.plt.xlim(self._x_range)

    def _set_y_range(self):
        if self._y_range:
            self.plt.ylim(self._y_range[0], self._y_range[1])

    def _set_labels(self):
        self.plt.xlabel(f"Fermi level ({self._x_unit})",
                        size=self._mpl_defaults.label_font_size)
        self.plt.ylabel(f"Energy ({self._y_unit})",
                        size=self._mpl_defaults.label_font_size)

    def _set_title(self):
        self.plt.title(self._title, size=self._mpl_defaults.title_font_size)

    def _set_formatter(self):
        axis = self.plt.gca()
        axis.yaxis.set_major_formatter(float_to_int_formatter)
        axis.tick_params(labelsize=self._mpl_defaults.tick_label_size)

    def _add_band_edges(self):
        if self._supercell_vbm > self._vline_threshold:
            self.plt.axvline(x=self._supercell_vbm,
                             **self._mpl_defaults.vline)
            plt.text(self._supercell_vbm, self._y_range[1], 'supercell VBM',
                     size=8, ha='center', va='center', rotation='vertical',
                     backgroundcolor='white')
        if self._supercell_cbm < self._x_range[1] - self._vline_threshold:
            self.plt.axvline(x=self._supercell_cbm,
                             **self._mpl_defaults.vline)
            plt.text(self._supercell_cbm, self._y_range[1], 'supercell',
                     size=8, ha='center', va='center', rotation='vertical',
                     backgroundcolor='white')


# Backward compatibility aliases
DefectEnergiesMplSettings = PlotSettings


class DefectEnergyPlotter(FormationEnergyPlotterBase):
    """Backward compatible alias for FormationEnergyPlotterBase."""

    def __init__(self, defect_energy_summary=None, formation_energy_summary=None, **kwargs):
        summary = formation_energy_summary if formation_energy_summary is not None else defect_energy_summary
        super().__init__(formation_energy_summary=summary, **kwargs)


class DefectEnergyMplPlotter(FormationEnergyMplPlotter):
    """Backward compatible alias for FormationEnergyMplPlotter."""

    def __init__(self, defect_energy_summary=None, formation_energy_summary=None, **kwargs):
        summary = formation_energy_summary if formation_energy_summary is not None else defect_energy_summary
        if 'name_style' not in kwargs:
            kwargs['name_style'] = 'mpl'
        # Call FormationEnergyPlotterBase.__init__ directly to avoid name_style duplication
        FormationEnergyPlotterBase.__init__(self, formation_energy_summary=summary, **kwargs)
        self._mpl_defaults = kwargs.get("mpl_defaults", PlotSettings())
        self._label_line = kwargs.get("label_line", True)
        self._add_charges = kwargs.get("add_charges", True)
        self._add_thin_lines = kwargs.get("add_thin_lines", True)
        self.plt = plt
        self._texts = []

