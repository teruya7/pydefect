# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
import string
import sys
from copy import deepcopy
from dataclasses import dataclass, asdict
from itertools import product
from typing import Dict, Optional, Union, List, Set, Tuple

import numpy as np
import yaml
from monty.json import MSONable
from monty.serialization import loadfn
from pydefect.error import PydefectError
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDEntry
from pymatgen.core import Composition
from scipy.spatial.qhull import HalfspaceIntersection
from tabulate import tabulate
from vise.util.logger import get_logger
from vise.util.mix_in import ToYamlFileMixIn, ToJsonFileMixIn

AtoZ = list(string.ascii_uppercase)
LargeMinusNumber = -1e5

logger = get_logger(__name__)


@dataclass
class CompositionEnergy(MSONable):
    """Energy data for a single composition.

    Attributes:
        energy: Total energy in eV.
        source: Source identifier (e.g., directory path or MP ID).
    """
    energy: float
    source: str = None


class CompositionEnergies(ToYamlFileMixIn, dict):
    """Dictionary mapping Composition to CompositionEnergy.

    This class stores formation energies for multiple compositions,
    used for constructing chemical potential diagrams.

    Keys:
        Composition: pymatgen Composition object.

    Values:
        CompositionEnergy: Energy and source information.

    Example:
        >>> comp_energies = CompositionEnergies.from_yaml("composition_energies.yaml")
        >>> std, rel = comp_energies.std_rel_energies
    """
    def to_yaml(self) -> str:
        """Convert to YAML string representation."""
        yaml_dict = {}
        for composition, comp_energy in self.items():
            formula_key = str(composition.iupac_formula).replace(" ", "")
            energy_data = {"energy": comp_energy.energy, "source": str(comp_energy.source)}
            yaml_dict[formula_key] = energy_data
        return yaml.dump(yaml_dict)

    @classmethod
    def from_yaml(cls, filename: str = None):
        """Load CompositionEnergies from YAML file."""
        yaml_filename = filename or cls._yaml_filename()
        loaded_data = loadfn(yaml_filename)
        composition_energies = {}
        for formula, energy_data in loaded_data.items():
            source = energy_data.get('source', None)
            composition = Composition(formula)
            composition_energies[composition] = CompositionEnergy(energy_data["energy"], source)
        return cls(composition_energies)

    @classmethod
    def from_dict(cls, data: Dict[str, float]):
        """Create from simple formula-to-energy dictionary."""
        comp_energies = {Composition(formula): CompositionEnergy(energy) 
                         for formula, energy in data.items()}
        return cls(comp_energies)

    @property
    def elements(self):
        """Set of all elements present in compositions."""
        result = set()
        for composition in self:
            result.update(set([str(element) for element in composition.elements]))
        return sorted(result)

    @property
    def std_rel_energies(self) -> Tuple["StandardEnergies", "RelativeEnergies"]:
        """Calculate standard and relative energies."""
        standard_energies = StandardEnergies()
        abs_energies_per_atom = {composition.reduced_formula: comp_energy.energy / composition.num_atoms
                                 for composition, comp_energy in self.items()}
        std_energies_list = []
        for vertex_element in self.elements:
            # This target is needed as some reduced formulas shows molecule
            # ones such as H2 and O2.
            reduced_formula = Composition({vertex_element: 1.0}).reduced_formula
            candidates = filter(lambda x: x[0] == reduced_formula,
                                abs_energies_per_atom.items())
            try:
                min_abs_energy = min([abs_energy_per_atom[1]
                                      for abs_energy_per_atom in candidates])
            except ValueError:
                print(f"Element {vertex_element} does not exist in "
                      f"CompositionEnergies.")
                raise NoElementEnergyError
            standard_energies[vertex_element] = min_abs_energy
            std_energies_list.append(min_abs_energy)

        relative_energies = RelativeEnergies(**{element: 0.0 for element in self.elements})
        for formula, abs_energy_per_atom in abs_energies_per_atom.items():
            if Composition(formula).is_element:
                continue
            fractions = atomic_fractions(formula, self.elements)
            energy_offset = sum([frac * ref_energy for frac, ref_energy in zip(fractions, std_energies_list)])
            relative_energies[formula] = abs_energy_per_atom - energy_offset

        return standard_energies, relative_energies

    def to_phase_diagram(self, elements=None):
        """Convert to pymatgen PhaseDiagram."""
        entries = []
        for composition, comp_energy in self.items():
            entries.append(PDEntry(composition, comp_energy.energy))
        if elements is None:
            elements = set()
            for composition in self:
                elements.update(composition.elements)
        return PhaseDiagram(entries=entries, elements=list(elements))


class CpdAbstractEnergies(ToYamlFileMixIn, dict):
    """
    keys: str (composition name)
    values: float (energy per atom)
    """
    def to_yaml(self) -> str:
        return yaml.dump(dict(self))

    @classmethod
    def from_yaml(cls, filename: str = None):
        return cls(loadfn(filename or cls._yaml_filename()))


class StandardEnergies(CpdAbstractEnergies):
    pass


def atomic_fractions(comp: Union[Composition, str], elements: List[str]
                     ) -> List[float]:
    """Calculate atomic fractions for given elements.

    Args:
        comp: Composition string or object.
        elements: List of element symbols.

    Returns:
        List of fractional compositions for each element.
    """
    return [Composition(comp).fractional_composition[e] for e in elements]


def comp_to_element_set(comp: Union[Composition, str]) -> Set[str]:
    return {str(e) for e in Composition(comp).elements}


def target_element_chem_pot(comp: Union[Composition, str],
                            energy_per_atom: float,
                            target_element: str,
                            other_elem_chem_pot: Dict[str, float]) -> float:
    assert comp_to_element_set(comp) \
           <= set(other_elem_chem_pot) | {target_element}
    other_element_val = 0.0
    for element, frac in Composition(comp).fractional_composition.items():
        if target_element == str(element):
            target_frac = frac
            continue
        other_element_val += other_elem_chem_pot[str(element)] * frac
    return (energy_per_atom - other_element_val) / target_frac


class RelativeEnergies(CpdAbstractEnergies):
    @property
    def phase_diagram(self) -> PhaseDiagram:
        entries = [PDEntry(Composition(comp_name), e)
                   for comp_name, e in self.items()]
        return PhaseDiagram(entries=entries)

    @property
    def unstable_compounds(self):
        result = {}
        phase_diagram = self.phase_diagram
        for uc in phase_diagram.unstable_entries:
            result[uc] = phase_diagram.get_decomp_and_e_above_hull(uc)
        return result

    @property
    def unstable_comp_info(self):
        result = []
        for comp, (decomp, e_above_hull) in self.unstable_compounds.items():
            decomp_list = " ".join([f"{d.composition} ({ratio:.3f})"
                                    for d, ratio in decomp.items()])
            result.append([comp.composition, e_above_hull, decomp_list])
        headers = ["composition", "E above hull", "decompose to (ratio)"]
        return tabulate(result, headers=headers, floatfmt=".2f")

    @property
    def all_element_set(self) -> Set[str]:
        return set().union(*[comp_to_element_set(c) for c in self])

    def host_composition_energies(self, elements: List[str]
                                  ) -> Dict[str, float]:
        return {formula: energy for formula, energy in self.items()
                if comp_to_element_set(formula).issubset(elements)}

    def comp_energies_with_element(self,
                                   element: str) -> Dict[str, float]:
        return {formula: energy for formula, energy in self.items()
                if element in comp_to_element_set(formula)}

    def impurity_chem_pot(self, impurity_element: str,
                          host_elements_chem_pot: Dict[str, float]
                          ) -> Tuple[float, str]:
        impurity_chem_pot = {impurity_element: 0.0}
        comp_energies = self.comp_energies_with_element(impurity_element)

        for formula, energy_per_atom in comp_energies.items():
            impurity_chem_pot[formula] = target_element_chem_pot(
                formula, energy_per_atom, impurity_element,
                host_elements_chem_pot)

        competing_phase_formula = min(impurity_chem_pot,
                                      key=impurity_chem_pot.get)
        chem_pot = impurity_chem_pot[competing_phase_formula]
        return chem_pot, competing_phase_formula


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
        # If this is too small, the creation of cpd may fail.
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


@dataclass
class TargetVertex(MSONable):
    """A vertex on the chemical potential diagram for the target compound.

    Attributes:
        chem_pot: Chemical potentials for each element at this vertex.
        competing_phases: Compositions of phases limiting this vertex.
        impurity_phases: Phases limiting impurity chemical potentials.
    """
    chem_pot: Dict[str, float]
    competing_phases: Optional[List[str]] = None
    impurity_phases: Optional[List[str]] = None


@dataclass
class TargetVertices(ToYamlFileMixIn):
    target: str
    vertices: Dict[str, TargetVertex]

    @property
    def chem_pots(self) -> Dict[str, Dict[str, float]]:
        """Get chemical potentials for each vertex."""
        return {label: vertex.chem_pot for label, vertex in self.vertices.items()}

    def to_yaml(self) -> str:
        """Convert to YAML string."""
        header = f"target: {self.target}"
        vertex_data = {label: asdict(vertex) for label, vertex in self.vertices.items()}
        return "\n".join([header, yaml.dump(vertex_data)])

    @classmethod
    def from_yaml(cls, filename: str = None):
        """Load from YAML file."""
        yaml_filename = filename or cls._yaml_filename()
        loaded_data = loadfn(yaml_filename)
        target = loaded_data.pop("target")
        vertices = {label: TargetVertex(**vertex_data) 
                    for label, vertex_data in loaded_data.items()}
        return cls(target=target, vertices=vertices)


@dataclass
class ChemPotDiag(MSONable, ToJsonFileMixIn):
    """Chemical potential diagram for a multi-element system.

    Contains polygonal regions for each stable phase and vertices
    for the target compound.

    Attributes:
        vertex_elements: Element symbols defining the diagram axes.
        polygons: Dict mapping composition to vertex coordinates.
        target: Target composition formula (e.g., "MgO").
        target_vertices_dict: Dict of labeled TargetVertex objects.

    Example:
        >>> cpd = ChemPotDiag.from_json("chem_pot_diag.json")
        >>> vertices = cpd.to_target_vertices
    """
    vertex_elements: List[str]
    polygons: Dict[str, List[List[float]]]
    target: str = None
    target_vertices_dict: Dict[str, TargetVertex] = None

    @property
    def target_coords(self):
        """Get target vertex coordinates for plotting."""
        if self.target_vertices_dict:
            return {label: [vertex.chem_pot[element] for element in self.vertex_elements]
                    for label, vertex in self.target_vertices_dict.items()}

    @property
    def min_range(self):
        return np.min(sum(self.polygons.values(), []))

    @property
    def dim(self):
        return len(self.vertex_elements)

    @property
    def comp_centers(self):
        """Calculate center coordinates for each composition."""
        return {composition: np.average(np.array(vertices), axis=0).tolist()
                for composition, vertices in self.polygons.items()}

    def atomic_fractions(self, composition: str):
        return [Composition(composition).get_atomic_fraction(e)
                for e in self.vertex_elements]

    @property
    def chemical_system(self) -> str:
        return "-".join([el for el in self.vertex_elements])

    @property
    def to_target_vertices(self):
        if self.target and self.target_vertices_dict:
            return TargetVertices(self.target, self.target_vertices_dict)
        logger.warning("Need to set target and target_vertices.")
        raise ValueError


def change_element_sequence(cpd: ChemPotDiag,
                            element_sequence: List[str] = None) -> ChemPotDiag:
    result = deepcopy(cpd)

    if element_sequence:
        if (set(cpd.vertex_elements) != set(element_sequence)
                or len(cpd.vertex_elements) != len(element_sequence)):
            raise ValueError(f"Original elements {cpd.vertex_elements}. "
                             f"Input elements {element_sequence}")
    else:
        if cpd.target:
            element_sequence = [str(e) for e in Composition(cpd.target).elements]
        else:
            return result

    element_indices = [cpd.vertex_elements.index(element) for element in element_sequence]
    for composition, polygon_vertices in cpd.polygons.items():
        result.polygons[composition] = [[vertex[idx] for idx in element_indices] 
                                         for vertex in polygon_vertices]

    result.vertex_elements = element_sequence
    return result


class NoElementEnergyError(PydefectError):
    pass


class UnstableTargetError(PydefectError):
    pass
