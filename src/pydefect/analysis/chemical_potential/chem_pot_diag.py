# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Chemical potential diagram maker."""

import string
import sys
from itertools import product
from typing import List

import numpy as np
from scipy.spatial.qhull import HalfspaceIntersection
from vise.util.logger import get_logger

from pydefect.analysis.chemical_potential.models import (
    RelativeEnergies,
    ChemPotDiag,
    TargetVertex,
    UnstableTargetError,
    atomic_fractions,
)

AtoZ = list(string.ascii_uppercase)
LargeMinusNumber = -1e5

logger = get_logger(__name__)


class ChemPotDiagMaker:
    """Factory class for creating ChemPotDiag objects.

    Constructs a chemical potential diagram from relative energies
    using half-space intersection algorithms.

    Attributes:
        relative_energies: RelativeEnergies containing formation energies.
        elements: List of elements for the diagram.
        target: Optional target composition formula.

    Example:
        >>> maker = ChemPotDiagMaker(rel_energies, ["Mg", "O"], target="MgO")
        >>> cpd = maker.chem_pot_diag
    """
    def __init__(self,
                 relative_energies: RelativeEnergies,
                 elements: List[str],
                 target: str = None):
        self.relative_energies = relative_energies
        self.host_composition_energies = \
            relative_energies.host_composition_energies(elements)
        self.elements = elements
        self.impurity_elements = \
            relative_energies.all_element_set.difference(elements)
        self.dim = len(elements)

        if target:
            try:
                assert target in relative_energies.keys()
            except AssertionError:
                logger.warning(f"Target {target} is not in relative energy "
                               f"compounds, so stop here.")
                sys.exit()
        self.target = target

    def _calc_vertices(self):
        half_spaces = []

        for formula, energy in self.host_composition_energies.items():
            half_spaces.append(
                atomic_fractions(formula, self.elements) + [-energy])

        for i in range(self.dim):
            upper_boundary, lower_boundary = [0.0] * self.dim, [0.0] * self.dim
            upper_boundary[i], lower_boundary[i] = 1.0, -1.0

            upper_boundary.append(0.0)
            lower_boundary.append(LargeMinusNumber)
            half_spaces.extend([upper_boundary, lower_boundary])

        feasible_point = np.array([LargeMinusNumber + 1.0] * self.dim,
                                  dtype=float)
        hs = HalfspaceIntersection(np.array(half_spaces), feasible_point)
        self.vertices: List[List[float]] = hs.intersections.tolist()

    def _does_composition_exist_in_cpd(self,
                                       coord: List[float],
                                       composition: str,
                                       energy: float) -> bool:
        atom_frac = atomic_fractions(composition, self.elements)
        diff = sum([x * y for x, y in zip(atom_frac, coord)]) - energy
        return abs(diff) < 1e-3

    def _min_energy_range(self, mul: float = 1.1):
        vertex_values = [x for x in sum(self.vertices, [])
                         if x != LargeMinusNumber]
        return min(vertex_values) * mul

    @property
    def chem_pot_diag(self):
        self._calc_vertices()
        host_energies = dict(**self.host_composition_energies)
        host_energies.update({element: 0.0 for element in self.elements})

        polygons = {}
        for comp, energy in host_energies.items():
            vertices = []
            for coord in self.vertices:
                if self._does_composition_exist_in_cpd(coord, comp, energy):
                    vertex = [round(c, ndigits=5) if c != LargeMinusNumber
                              else self._min_energy_range() for c in coord]
                    vertices.append(vertex)
            if vertices:
                polygons[comp] = vertices

        vertices = None

        if self.target:
            if self.target not in polygons:
                raise UnstableTargetError(f"""
                    The target compound is unstable with respect to the 
                    competing phases, and do not appear in the chemical 
                    potential diagram. Currently, pydefect can be used only
                    for stable compounds.""")

            target_vertices = []
            for coord in polygons[self.target]:
                competing_phases = []
                for comp, vertices in polygons.items():
                    if comp == self.target:
                        continue
                    if coord in vertices:
                        competing_phases.append(comp)

                impurity_phases = []
                host_chem_pots = dict(zip(self.elements, coord))
                impurity_chem_pots = {}
                for i_element in self.impurity_elements:
                    i_chem_pot, i_phase = \
                        self.relative_energies.impurity_chem_pot(
                            i_element, host_chem_pots)
                    impurity_chem_pots[i_element] = i_chem_pot
                    impurity_phases.append(i_phase)
                chem_pot = dict(**host_chem_pots, **impurity_chem_pots)
                target_vertices.append(TargetVertex(chem_pot,
                                                    competing_phases,
                                                    impurity_phases))

            AtoZZ = product([""] + AtoZ, AtoZ)
            vertices = {"".join(next(AtoZZ)): v for v in target_vertices}

        return ChemPotDiag(vertex_elements=self.elements,
                           polygons=polygons,
                           target=self.target,
                           target_vertices_dict=vertices)
