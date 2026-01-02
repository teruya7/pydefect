# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import yaml
from monty.json import MSONable, MontyDecoder
from pydefect.analyzer.defect_structure.defect_structure_comparator import \
    DefectStructureComparator
from pydefect.utils.formatting import pretty_coords
from pymatgen.core import IStructure
from vise.util.mix_in import ToJsonFileMixIn
from vise.util.structure_symmetrizer import StructureSymmetrizer
from vise.util.typing import Coords


@dataclass(frozen=True)
class PerturbedSite(MSONable):
    """Information about a perturbed atomic site.

    Tracks displacement of an atom from its ideal position during
    defect structure relaxation or intentional perturbation.

    Attributes:
        element: Element symbol of the perturbed atom.
        distance: Distance from defect center in Angstroms.
        initial_coords: Original fractional coordinates before perturbation.
        perturbed_coords: Fractional coordinates after perturbation.
        displacement: Magnitude of displacement in Angstroms.

    Example:
        >>> site = PerturbedSite(
        ...     element="O",
        ...     distance=2.5,
        ...     initial_coords=(0.5, 0.5, 0.5),
        ...     perturbed_coords=(0.51, 0.49, 0.5),
        ...     displacement=0.1
        ... )
        >>> print(site)
           O 2.50 ( 0.500,  0.500,  0.500) -> ( 0.510,  0.490,  0.500)    0.10
    """
    element: str
    distance: float
    initial_coords: Coords
    perturbed_coords: Coords
    displacement: float

    @classmethod
    def from_dict(cls, d):
        return cls(element=d["element"],
                   distance=d["distance"],
                   initial_coords=tuple(d["initial_coords"]),
                   perturbed_coords=tuple(d["perturbed_coords"]),
                   displacement=d["displacement"])

    def __str__(self):
        elem = f"{self.element:>4}"
        dist = f"{self.distance:4.2f}"
        ini_coords = pretty_coords(self.initial_coords)
        p_coords = pretty_coords(self.perturbed_coords)
        disp = f"{self.displacement:7.2f}"
        return f"{elem} {dist} {ini_coords} -> {p_coords} {disp}"


@dataclass(frozen=True)
class DefectEntry(MSONable, ToJsonFileMixIn):
    """Complete specification of a defect for calculation.

    Contains all information needed to set up a defect calculation,
    including the structure, charge state, and symmetry information.

    Attributes:
        name: Defect name following convention (e.g., "Va_O1" for oxygen
            vacancy at site O1, "Mg_i1" for Mg interstitial).
        charge: Charge state of the defect. Positive for holes,
            negative for electrons.
        structure: Initial defect structure for calculation.
        site_symmetry: Point group symmetry of the defect site.
        defect_center: Fractional coordinates of defect center.
        perturbed_structure: Optional structure with site perturbations
            to break symmetry and find lower-energy configurations.
        perturbed_sites: Information about which sites were perturbed.
        perturbed_site_symmetry: Site symmetry after perturbation.

    Example:
        >>> from pymatgen.core import Structure
        >>> structure = Structure.from_file("defect_POSCAR")
        >>> entry = DefectEntry(
        ...     name="Va_O1",
        ...     charge=2,
        ...     structure=structure,
        ...     site_symmetry="Oh",
        ...     defect_center=(0.5, 0.5, 0.5)
        ... )
        >>> entry.to_json_file("defect_entry.json")
    """
    name: str
    charge: int
    structure: IStructure
    site_symmetry: str
    defect_center: Coords
    perturbed_structure: Optional[IStructure] = None
    perturbed_sites: Optional[Tuple[PerturbedSite, ...]] = None
    perturbed_site_symmetry: Optional[str] = None

    @classmethod
    def from_dict(cls, d):
        d = {k: MontyDecoder().process_decoded(v) for k, v in d.items() if not k.startswith("@")}
        if d["perturbed_sites"]:
            d["perturbed_sites"] = tuple([MontyDecoder().process_decoded(d) for d in d["perturbed_sites"]])
        d["defect_center"] = tuple(d["defect_center"])
        return cls(**d)

    @property
    def anchor_atom_index(self) -> int:
        """ Returns an index of atom that is the farthest from the defect.

         Only the first occurrence is returned when using argmax.
         docs.scipy.org/doc/numpy-1.15.0/reference/generated/numpy.argmax.html
         """
        lattice = self.structure.lattice
        all_coords = self.structure.frac_coords
        dist_set = lattice.get_all_distances(self.defect_center, all_coords)[0]
        return int(np.argmax(dist_set))

    @property
    def anchor_atom_coords(self) -> np.ndarray:
        return self.structure[self.anchor_atom_index].frac_coords

    @property
    def perturbed_site_indices(self):
        """Return indices of sites that were perturbed."""
        result = []
        for site_idx, (original_site, perturbed_site) in enumerate(
                zip(self.structure, self.perturbed_structure)):
            if (original_site.frac_coords != perturbed_site.frac_coords).any():
                result.append(site_idx)
        return result

    @property
    def full_name(self):
        return "_".join([self.name, str(self.charge)])

    def to_prior_info(self, filename):
        d = {"charge": int(self.charge)}
        Path(filename).write_text(yaml.dump(d))

    def __str__(self):
        result = f""" -- defect entry info
name: {self.full_name}
site symmetry: {self.site_symmetry}
defect center: ({", ".join([f"{coord:6.3f}" for coord in self.defect_center])})
perturbed sites:
elem dist   initial_coords             perturbed_coords         displacement
"""
        if self.perturbed_sites:
            result += "\n".join([perturbed_site.__str__() 
                                 for perturbed_site in self.perturbed_sites])

        return result


def make_defect_entry(name: str,
                      charge: int,
                      perfect_structure: IStructure,
                      defect_structure: IStructure):
    """Create DefectEntry from structure comparison."""
    analyzer = DefectStructureComparator(perfect_structure, defect_structure)

    species = []
    frac_coords = []
    for defect_idx, perfect_idx in enumerate(analyzer.perfect_to_defect_indices):
        if perfect_idx is None:
            site = defect_structure[defect_idx]
        else:
            site = perfect_structure[perfect_idx]
        species.append(site.specie)
        frac_coords.append(site.frac_coords)

    initial_structure = IStructure(perfect_structure.lattice,
                                   species, frac_coords)
    symmetrizer = StructureSymmetrizer(initial_structure)

    return DefectEntry(name=name,
                       charge=charge,
                       structure=initial_structure,
                       site_symmetry=symmetrizer.point_group,
                       defect_center=tuple(analyzer.defect_center_coord))
