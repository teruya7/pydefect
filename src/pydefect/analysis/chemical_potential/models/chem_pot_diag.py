# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Chemical potential diagram data classes."""

from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Dict, Optional, List

import numpy as np
import yaml
from monty.json import MSONable
from monty.serialization import loadfn
from pydefect.error import PydefectError
from pymatgen.core import Composition
from vise.util.logger import get_logger
from vise.util.mix_in import ToYamlFileMixIn, ToJsonFileMixIn

logger = get_logger(__name__)


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
    """Collection of labeled target vertices."""
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

    Attributes:
        vertex_elements: Element symbols defining the diagram axes.
        polygons: Dict mapping composition to vertex coordinates.
        target: Target composition formula (e.g., "MgO").
        target_vertices_dict: Dict of labeled TargetVertex objects.
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
    """Change element ordering in chemical potential diagram."""
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


class UnstableTargetError(PydefectError):
    """Raised when target compound is unstable."""
    pass
