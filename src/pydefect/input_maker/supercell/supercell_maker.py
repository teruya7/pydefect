# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

from typing import Optional, List

import numpy as np
from numpy.linalg import det
from pydefect.defaults import defaults
from pydefect.input_maker.supercell.supercell import Supercell, TetragonalSupercells, \
    Supercells
from pydefect.input_maker.supercell.supercell_info import SupercellInfo
from pydefect.error import NotPrimitiveError, SupercellError
from pymatgen.core import IStructure
from vise.util.centering import Centering
from vise.util.logger import get_logger
from vise.util.structure_symmetrizer import StructureSymmetrizer, Site

logger = get_logger(__name__)


class SupercellMaker:
    """Create supercell and supercell info from primitive structure.

    Generates an isotropic supercell within size constraints and
    analyzes symmetry-equivalent sites. The supercell is created from
    the conventional cell to maintain symmetry information.

    Attributes:
        supercell: Generated Supercell object containing the supercell
            structure and transformation matrix.
        supercell_info: SupercellInfo with detailed site analysis and
            symmetry information.
        sg_symbol: Space group symbol (e.g., "Fm-3m").
        conv_structure: Conventional unit cell structure.
        conv_multiplicity: Ratio of conventional to primitive cell.
        conv_trans_mat: Transformation matrix from primitive to conventional.

    Example:
        >>> from pymatgen.core import Structure
        >>> primitive = Structure.from_file("POSCAR")
        >>> maker = SupercellMaker(
        ...     primitive_structure=primitive,
        ...     min_num_atoms=50,
        ...     max_num_atoms=100
        ... )
        >>> print(maker.supercell.structure)
        >>> maker.supercell_info.to_json_file()
    """
    def __init__(self,
                 primitive_structure: IStructure,
                 # matrix_to_conv_cell
                 matrix: Optional[List[List[int]]] = None,
                 symprec: float = defaults.symmetry_length_tolerance,
                 angle_tolerance: float = defaults.symmetry_angle_tolerance,
                 raise_error: bool = False,
                 **supercell_kwargs):
        """Initialize SupercellMaker.

        Args:
            primitive_structure: Primitive unit cell structure.
            matrix: Optional 3x3 transformation matrix to conventional cell.
            symprec: Symmetry tolerance for length in Å.
            angle_tolerance: Symmetry tolerance for angles in degrees.
            raise_error: If True, raise error when structure is not primitive.
            **supercell_kwargs: Arguments passed to Supercells generator
                (min_num_atoms, max_num_atoms, etc.).
        """
        self.primitive_structure = primitive_structure
        self.symmetrizer = StructureSymmetrizer(primitive_structure,
                                                symprec=symprec,
                                                angle_tolerance=angle_tolerance)
        if primitive_structure != self.symmetrizer.primitive:
            logger.warning(
                "The input structure differs from the primitive one, possibly "
                "due to the symprec value used in pydefect and during the unit "
                "cell conversion. Please reconstruct the unit cell using vise. "
                "Proceed only if you understand the implications.")
            logger.warning("\n".join([
                "Input lattice:",
                f"{primitive_structure.lattice}", "",
                "Primitive structure lattice:",
                f"{self.symmetrizer.primitive.lattice}", "",
                "Input structure:",
                f"{primitive_structure}", "",
                "Primitive structure:",
                f"{self.symmetrizer.primitive}"]))
            if raise_error:
                raise NotPrimitiveError

        self.sg_symbol = self.symmetrizer.spglib_sym_data.international
        self.conv_structure = self.symmetrizer.conventional
        crystal_system, center = str(self.symmetrizer.bravais)

        centering = Centering(center)
        self.conv_multiplicity = centering.conv_multiplicity
        self.conv_trans_mat = centering.primitive_to_conv

        self._matrix = matrix
        self._supercell_kwargs = supercell_kwargs

        self._generate_supercell(crystal_system)
        self._generate_supercell_info()

    def _generate_supercell(self, crystal_system):
        """Generate supercell from conventional cell."""
        if self._matrix:
            self.supercell = Supercell(self.conv_structure, self._matrix)
        else:
            if crystal_system == "t":
                supercells = TetragonalSupercells(self.conv_structure,
                                                  **self._supercell_kwargs)
            else:
                supercells = Supercells(self.conv_structure,
                                        **self._supercell_kwargs)

            self.supercell = supercells.most_isotropic_supercell

    def _generate_supercell_info(self):
        """Generate supercell info with equivalent sites."""
        multiplicity = int(round(det(self.transformation_matrix)))

        sites = {}
        for site_name, site in self.symmetrizer.sites.items():
            equivalent_atoms = []
            for atom_index in site.equivalent_atoms:
                equivalent_atoms.extend(
                    list(range(atom_index * multiplicity, (atom_index + 1) * multiplicity)))
            sites[site_name] = Site(element=site.element,
                                    wyckoff_letter=site.wyckoff_letter,
                                    site_symmetry=site.site_symmetry,
                                    equivalent_atoms=equivalent_atoms)

        self.supercell_info = \
            SupercellInfo(structure=self.supercell.structure,
                          space_group=self.sg_symbol,
                          transformation_matrix=self.transformation_matrix,
                          sites=sites,
                          unitcell_structure=self.primitive_structure)

    @property
    def transformation_matrix(self) -> List[List[int]]:
        """Get transformation matrix from primitive to supercell.

        Note: The definition of transformation_matrix differs from spglib.
        This maintains consistency with pymatgen conventions.
        See: https://spglib.github.io/spglib/definition.html

        Returns:
            3x3 integer transformation matrix as nested list.
        """
        matrix = np.dot(self.supercell.matrix, self.conv_trans_mat).astype(int)
        return matrix.tolist()

