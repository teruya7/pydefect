# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

from copy import deepcopy
from functools import reduce
from itertools import product
from typing import List, Tuple

import numpy as np
from numpy.linalg import det
from pydefect.error import SupercellError
from pymatgen.core import IStructure


class Supercell:
    """A supercell structure with transformation matrix.

    Attributes:
        matrix: 3x3 transformation matrix.
        structure: Supercell structure.
        lattice: Supercell lattice.

    Example:
        >>> from pymatgen.core import Structure
        >>> unitcell = Structure.from_file("POSCAR")
        >>> supercell = Supercell(unitcell, [[2, 0, 0], [0, 2, 0], [0, 0, 2]])
        >>> print(len(supercell.structure))
        64
    """
    def __init__(self, input_structure: IStructure, matrix: List[List[int]]):
        """Initialize Supercell.

        Args:
            input_structure: Input unit cell structure.
            matrix: 3x3 transformation matrix (list of lists).
        """
        self.matrix = matrix
        self.structure = input_structure * matrix
        self.lattice = self.structure.lattice

    @property
    def isotropy(self):
        lengths = self.structure.lattice.lengths
        average = np.average(lengths)
        return sum([abs(length - average) for length in lengths]) / 3 / average

    @property
    def average_angle(self):
        return sum(self.structure.lattice.angles) / 3


class Supercells:
    """Generator of supercell candidates.

    Creates supercells within atom count constraints and
    finds the most isotropic one.

    Attributes:
        input_structure: Input unit cell structure.
        supercells: List of Supercell candidates.

    Example:
        >>> from pymatgen.core import Structure
        >>> unitcell = Structure.from_file("POSCAR")
        >>> supercells = Supercells(unitcell, min_num_atoms=50, max_num_atoms=100)
        >>> best = supercells.most_isotropic_supercell
        >>> print(len(best.structure))
        64
    """
    def __init__(self,
                 input_structure: IStructure,
                 min_num_atoms: int = 50,
                 max_num_atoms: int = 250):
        """Initialize Supercells generator.

        Args:
            input_structure: Input unit cell structure.
            min_num_atoms: Minimum number of atoms in the supercell.
            max_num_atoms: Maximum number of atoms in the supercell.
        """
        self.input_structure = input_structure
        min_det = min_num_atoms / len(input_structure) - 1e-5
        max_det = max_num_atoms / len(input_structure) + 1e-5

        self.supercells = []
        matrix = np.eye(3, dtype=int)
        for _iteration in range(50):
            if det(matrix) > max_det:
                break
            if det(matrix) > min_det:
                self.supercells.append(Supercell(input_structure,
                                                 matrix.tolist()))
            matrix = self.incremented_matrix(matrix)

    def incremented_matrix(self, matrix: np.ndarray):
        """Increment transformation matrix along shortest axis."""
        lattice_lengths = (self.input_structure * matrix).lattice.lengths
        min_length = min(lattice_lengths)
        shortest_axes = [axis for axis, length in enumerate(lattice_lengths) 
                         if length == min_length]
        new_matrix = deepcopy(matrix)
        for axis in shortest_axes:
            new_matrix[axis][axis] += 1
        return new_matrix

    @property
    def most_isotropic_supercell(self):
        try:
            return min(self.supercells, key=lambda s: s.isotropy)
        except ValueError:
            raise SupercellError


class RhombohedralSupercells(Supercells):
    def incremented_matrix(self, matrix: np.ndarray):
        alpha = (self.input_structure * matrix).lattice.angles[0]

        fan_out = np.array([[1,  1, -1], [-1,  1,  1], [1, -1,  1]])
        close_in = np.array([[1, 0, 1], [1, 1, 0], [0, 1, 1]])

        if alpha < 90:
            return np.dot(matrix, fan_out)
        else:
            return np.dot(matrix, close_in)


class TetragonalSupercells(Supercells):
    def incremented_matrix(self, matrix: np.ndarray):
        a, _, c = (self.input_structure * matrix).lattice.lengths
        new_matrix = deepcopy(matrix)
        if a > c:
            new_matrix[2][2] += 1
            return new_matrix
        else:
            ab_submatrix_det = round(det(matrix[0:2, 0:2]))
            x, y = self.next_x_y_combination(ab_submatrix_det)
            new_matrix[0:2, 0:2] = self.matrix_from_x_y(x, y)
            return new_matrix

    @staticmethod
    def matrix_from_x_y(x: int, y: int) -> np.ndarray:
        """ """
        assert x >= 1
        assert y >= 0

        expand_matrix = np.array([[x, 0], [0, x]])
        if y == 0:
            rot_matrix = np.eye(2)
        elif y == 1:
            rot_matrix = np.array([[1, 1], [-1, 1]])
        else:
            matrix_list = [np.array([[1, 1], [-1, 1]])] * y
            rot_matrix = reduce(np.dot, matrix_list)

        return np.dot(expand_matrix, rot_matrix)

    @staticmethod
    def next_x_y_combination(current_det: int) -> Tuple[int, int]:
        """Find x, y with minimum of x ** 2 * 2^y larger than current_det."""
        xy_to_det = {(expansion, rotation): expansion * expansion * 2 ** rotation
                     for expansion, rotation in product(range(1, 10), range(8))}
        larger_det_pairs = {xy: det_val for xy, det_val in xy_to_det.items() 
                            if det_val > current_det}
        return next(iter(sorted(larger_det_pairs, key=lambda xy: xy_to_det[xy])))


