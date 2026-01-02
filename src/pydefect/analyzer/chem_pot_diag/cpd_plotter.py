# -*- coding: utf-8 -*-
from abc import abstractmethod, ABC
from typing import Optional, List

import numpy as np
from numpy import concatenate, clip, dot, arctan2
from numpy.linalg import det
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from vise.util.sort_coords import sort_coords

from pydefect.analyzer.chem_pot_diag.chem_pot_diag import ChemPotDiag
from vise.util.string import latexify



class CpdMplSettings:
    """Matplotlib settings for chemical potential diagrams.

    Attributes:
        rc_params: Matplotlib rcParams for fonts.
        grid_2d: Style dict for 2D grid lines.
        label: Style dict for composition labels.
        alphabet_label: Style dict for vertex labels.
        target_comp_text_color: Color for target composition.
        comp_text_color: Color for other compositions.
        simplex_2d: Style dict for 2D simplex lines.

    Example:
        >>> settings = CpdMplSettings()
        >>> print(settings.target_comp_text_color)
        blue
    """
    def __init__(self):
        """Initialize default matplotlib settings."""
        # Avoid type 3 font, http://phyletica.org/matplotlib-fonts/
        # https://stackoverflow.com/questions/34387893/output-matplotlib-figure-to-svg-with-text-as-text-not-curves
        self.rc_params = {'pdf.fonttype':  42, 'ps.fonttype': 42,
                          'svg.fonttype': "none"}

        self.grid_2d = {"color": 'black',
                        "alpha": 0.8,  # grid opacity
                        "linestyle": 'dashed',
                        "linewidth": 0.5}

        # Default zorder
        # Patch / PatchCollection	1
        # Line2D / LineCollection	2
        # Text	3
        # Big number of zorder is needed as it increases with num of simplexes
        self.label = {"size": 'smaller', "zorder": 100}

        self.alphabet_label = {"color": "blue", "weight": "bold", "zorder": 101}

        self.target_comp_text_color = "blue"
        self.comp_text_color = "black"

        self.simplex_2d = {"color": "black", "linewidth": 2, "zorder": 1}


class ChemPotDiagMplPlotter(ABC):
    """Base class for chemical potential diagram plotters.

    Attributes:
        cpd: ChemPotDiag data object.

    Example:
        >>> plotter = ChemPotDiag2DMplPlotter(cpd)
        >>> plt = plotter.draw_diagram()
        >>> plt.savefig("cpd.pdf")
    """
    def __init__(self,
                 cpd: ChemPotDiag,
                 mpl_defaults: Optional[CpdMplSettings] = CpdMplSettings()):
        """Initialize chemical potential diagram plotter.

        Args:
            cpd: ChemPotDiag object to plot.
            mpl_defaults: Matplotlib settings. Uses defaults if None.
        """
        self.cpd = cpd

        self._mpl_defaults = mpl_defaults
        self._add_ax()

    @abstractmethod
    def _add_ax(self):
        pass

    def draw_diagram(self, title: Optional[str] = None) -> plt:
        plt.rcParams.update(self._mpl_defaults.rc_params)
        self._plot()
        self._add_alphabet_labels()
        self._set_title(title)
        self._set_lims()
        self._set_labels()
        self._set_grid()
        plt.tight_layout()

        return plt

    @abstractmethod
    def _set_lims(self):
        pass

    @abstractmethod
    def _set_labels(self):
        pass

    @abstractmethod
    def _set_grid(self):
        pass

    def _plot(self):
        for comp, position in self.cpd.comp_centers.items():
            self.draw_simplex(comp)
            self._ax.text(*position,
                          latexify(comp),
                          color=self._text_color(comp),
                          **self._mpl_defaults.label,
                          **self._text_kwargs)

    @abstractmethod
    def draw_simplex(self, formula):
        pass

    @property
    @abstractmethod
    def _text_kwargs(self):
        pass

    def _text_color(self, formula):
        if self.cpd.target_coords and formula == self.cpd.target:
            return self._mpl_defaults.target_comp_text_color
        return self._mpl_defaults.comp_text_color

    def _set_title(self, title):
        if not title:
            title = f"Chemical potential diagram of {self.cpd.chemical_system}"
        self._ax.set_title(title)

    def _add_alphabet_labels(self):
        if self.cpd.target:
            for label, vertex_coords in self.cpd.target_coords.items():
                self._ax.text(*transpose(vertex_coords), label,
                              **self._mpl_defaults.alphabet_label)


class ChemPotDiag2DMplPlotter(ChemPotDiagMplPlotter):
    """2D chemical potential diagram plotter.

    Example:
        >>> plotter = ChemPotDiag2DMplPlotter(cpd)
        >>> plt = plotter.draw_diagram()
    """

    def _add_ax(self):
        self._ax = plt.figure().add_subplot(111)

    @property
    def _text_kwargs(self):
        return {}

    def _set_lims(self):
        self._ax.set_xlim(self.cpd.min_range, 0)
        self._ax.set_ylim(self.cpd.min_range, 0)
        self._ax.set_aspect('equal', adjustable='box')

    def _set_labels(self):
        vertex_elements = self.cpd.vertex_elements
        self._ax.set_xlabel(f"Chemical potential of {vertex_elements[0]}")
        self._ax.set_ylabel(f"Chemical potential of {vertex_elements[1]}")

    def _set_grid(self):
        self._ax.grid(**self._mpl_defaults.grid_2d)

    def draw_simplex(self, formula):
        vertex_coords = self.cpd.polygons[formula]
        plt.plot(*transpose(vertex_coords), **self._mpl_defaults.simplex_2d)


class ChemPotDiag3DMplPlotter(ChemPotDiagMplPlotter):
    """3D chemical potential diagram plotter.

    Example:
        >>> plotter = ChemPotDiag3DMplPlotter(cpd)
        >>> plt = plotter.draw_diagram()
    """
    def _add_ax(self):
        self._ax = plt.figure().add_subplot(111, projection='3d')

    @property
    def _text_kwargs(self):
        return {"ha": "center", "va": "center"}

    def _set_lims(self):
        self._ax.set_xlim3d(self.cpd.min_range, 0)
        self._ax.set_ylim3d(0, self.cpd.min_range)
        self._ax.set_zlim3d(self.cpd.min_range, 0)

    def _set_labels(self):
        label = [f"Chemical potential of {e}" for e in self.cpd.vertex_elements]
        self._ax.set_xlabel(label[0])
        self._ax.set_ylabel(label[1])
        self._ax.set_zlabel(label[2])

    def _set_grid(self):
        pass

    def draw_simplex(self, formula):
        vertex_coords = self.cpd.polygons[formula]
        atomic_fractions = self.cpd.atomic_fractions(formula)

        face = Poly3DCollection([sort_coords(np.array(vertex_coords))])
        face.set_color(self._3d_simplex_color(atomic_fractions))
        face.set_edgecolor("black")
        self._ax.add_collection3d(face)

    @staticmethod
    def _3d_simplex_color(atomic_fractions):
        return [(f + 1.5) / 2.5 for f in atomic_fractions]


def transpose(target_list: List[List[float]]) -> List[List[float]]:
    return np.array(target_list).transpose().tolist()
