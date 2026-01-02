# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from itertools import product
from typing import List

import numpy as np
from pydefect.analysis.corrections.efnv import calculate_max_inscribed_radius as calc_max_sphere_radius
from pymatgen.electronic_structure.core import Spin
from pymatgen.io.vasp import Chgcar


class RadialDist:
    """Radial distribution of charge density from partial charge file.

    Calculates histograms of charge density vs distance from defect center.

    Attributes:
        data: Spin-resolved charge data.
        dim: Grid dimensions.
        lattice: Crystal lattice.
        center: Center coordinates.
        radius: Maximum sphere radius.

    Example:
        >>> from pymatgen.io.vasp import Chgcar
        >>> parchg = Chgcar.from_file("PARCHG")
        >>> dist = RadialDist(parchg, [0.5, 0.5, 0.5])
        >>> hist = dist.histogram(Spin.up)
    """
    def __init__(self, parchg: Chgcar, center_coords: List[float]):
        """Initialize RadialDist.

        Args:
            parchg: PARCHG file from VASP.
            center_coords: Defect center fractional coordinates.
        """
        self.data = parchg.spin_data
        self.dim = parchg.dim
        self.lattice = parchg.structure.lattice
        self.center = center_coords
        self.radius = calc_max_sphere_radius(self.lattice.matrix)
        self._distances_data = None  # lazy evaluation

    @property
    def distances_data(self):
        """Lazy-evaluated distance data from center."""
        if self._distances_data is None:
            grid_points = [[grid_x / self.dim[0], grid_y / self.dim[1], grid_z / self.dim[2]]
                           for (grid_x, grid_y, grid_z) in
                           product(*[list(range(dim_size)) for dim_size in self.dim])]

            # Use boolean indexing to find charges within the desired distance.
            # data[:, 0]: shifted_coords
            # data[:, 1]: distances
            # data[:, 2]: sequential indices
            # data[:, 3]: images
            self._distances_data = np.array(self.lattice.get_points_in_sphere(
                grid_points, self.center, self.radius))

        return self._distances_data

    def histogram(self, spin: Spin, nbins: int = 15):
        inds = self.distances_data[:, 1] <= self.radius
        dists = self.distances_data[inds, 1]
        data_inds = np.rint(np.mod(list(self.distances_data[inds, 0]), 1) *
                            np.tile(self.dim, (len(dists), 1))).astype(int)

        vals = [self.data[spin][x, y, z] for x, y, z in data_inds]

        hist, edges = np.histogram(dists, nbins,
                                   range=[0, self.radius], weights=vals)
        hist_numbers, _ = np.histogram(dists, nbins, range=[0, self.radius])
        mesh_distance = edges[1] - edges[0]

        hist_data = np.zeros((nbins, 2))
        hist_data[:, 0] = [sum(edges[i:i + 2]) / 2 for i in range(nbins)]

        # 4pi * r^2 * rho
        integrated_volume = 4 * np.pi * hist_data[:, 0] ** 2
        density = hist / hist_numbers / self.lattice.volume
        hist_data[:, 1] = integrated_volume * density

        half_point = None
        for bin_idx in range(hist_data[:, 1].size):
            if sum(hist_data[:bin_idx + 1, 1]) > 0.5:
                # Obtain from the calculation of the area of a trapezoid
                x0 = hist_data[bin_idx - 1, 0]
                y0 = hist_data[bin_idx, 1]
                y1 = hist_data[bin_idx + 1, 1]
                half_point = (0.5 - sum(hist_data[:bin_idx, 1]) * mesh_distance) \
                    * 2 / (y0 + y1) + x0
                break

        summed = sum(hist_data[:, 1]) * mesh_distance
        return hist_data, half_point, summed


