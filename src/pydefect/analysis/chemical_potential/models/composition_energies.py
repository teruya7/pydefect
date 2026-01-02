# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Composition energy and phase diagram data classes."""

from dataclasses import dataclass
from typing import Dict, Optional, Union, List, Set, Tuple

import yaml
from monty.json import MSONable
from monty.serialization import loadfn
from pydefect.error import PydefectError
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDEntry
from pymatgen.core import Composition
from tabulate import tabulate
from vise.util.mix_in import ToYamlFileMixIn


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
    """Dictionary mapping Composition to CompositionEnergy."""

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
    """Base class for energy dictionaries."""

    def to_yaml(self) -> str:
        return yaml.dump(dict(self))

    @classmethod
    def from_yaml(cls, filename: str = None):
        return cls(loadfn(filename or cls._yaml_filename()))


class StandardEnergies(CpdAbstractEnergies):
    """Standard reference energies for elements."""
    pass


def atomic_fractions(comp: Union[Composition, str], elements: List[str]
                     ) -> List[float]:
    """Calculate atomic fractions for given elements."""
    return [Composition(comp).fractional_composition[e] for e in elements]


def comp_to_element_set(comp: Union[Composition, str]) -> Set[str]:
    """Convert composition to set of element symbols."""
    return {str(e) for e in Composition(comp).elements}


def target_element_chem_pot(comp: Union[Composition, str],
                            energy_per_atom: float,
                            target_element: str,
                            other_elem_chem_pot: Dict[str, float]) -> float:
    """Calculate chemical potential of target element from composition."""
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
    """Formation energies relative to elemental references."""

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

    def host_composition_energies(self, elements: List[str]) -> Dict[str, float]:
        return {formula: energy for formula, energy in self.items()
                if comp_to_element_set(formula).issubset(elements)}

    def comp_energies_with_element(self, element: str) -> Dict[str, float]:
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


class NoElementEnergyError(PydefectError):
    """Raised when element energy is not found."""
    pass
