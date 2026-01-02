# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
"""Charge localization information for defect states."""
from dataclasses import dataclass
from typing import List

import numpy as np
from matplotlib import pyplot as plt
from monty.json import MSONable
from pydefect.analysis.localization.models.charge_distribution import RadialChargeDist
from pydefect.defaults import defaults
from pydefect.utils.formatting import pretty_coords
from pymatgen.electronic_structure.core import Spin
from tabulate import tabulate
from vise.util.mix_in import ToJsonFileMixIn


@dataclass
class ChargeLocalizationInfo(MSONable, ToJsonFileMixIn):
    """Charge localization information for defect states.

    Analyzes how localized defect-induced states are by examining
    radial charge density distributions from PARCHG files.

    Attributes:
        distance_bins: Radial distance bins (Å), last value is max radius.
        band_indices: Band indices analyzed.
        radial_distributions: [band, spin] -> RadialChargeDist.
        uniform_density: Uniform charge density reference (e/Å³).

    Example:
        >>> info = ChargeLocalizationInfo.from_json_file()
        >>> info.find_localized_orbitals()
        [[10, 11], []]
    """
    distance_bins: List[float]  # the last value is the radius
    band_indices: List[int]
    radial_distributions: List[List[RadialChargeDist]]  # [band-idx, spin]
    uniform_density: float

    def density_distribution(self, band_idx: int, spin: Spin):
        """Get density distribution for a specific band and spin.

        Args:
            band_idx: Band index.
            spin: Spin channel (up or down).

        Returns:
            List of density values at each radial bin.
        """
        spin_idx = 0 if spin == Spin.up else 1
        band_pos = np.argwhere(np.array(self.band_indices) == band_idx)[0][0]
        return self.radial_distributions[band_pos][spin_idx].density_profile

    def integrated_charge_distribution(self, band_idx: int, spin: Spin):
        """Get integrated charge distribution for a band and spin.

        Args:
            band_idx: Band index.
            spin: Spin channel.

        Returns:
            List of integrated charge values at each radial shell.
        """
        density = self.density_distribution(band_idx, spin)
        volumes = (np.array(self.distance_bins[1:]) ** 3
                   - np.array(self.distance_bins[:-1]) ** 3) * 4 / 3 * np.pi
        return list(density * volumes)

    @property
    def uniform_localization_radius(self):
        """Localization radius for uniformly distributed charge.

        Returns:
            Radius containing half the charge for uniform distribution.
        """
        return (3 * 0.5 / (4 * np.pi * self.uniform_density)) ** (1.0 / 3.0)

    @property
    def is_spin_polarized(self):
        """Check if calculation is spin-polarized."""
        return len(self.radial_distributions[0]) == 2

    def localization_radius(self, band_idx: int, spin: Spin):
        """Calculate radius containing half of the charge.

        Args:
            band_idx: Band index.
            spin: Spin channel.

        Returns:
            Radius (Å) containing 50% of the charge.

        Raises:
            ValueError: If radius could not be determined.
        """
        charge_sum = 0.0
        dist = self.integrated_charge_distribution(band_idx, spin)
        for charge_val, start_radius, end_radius in zip(
                dist, self.distance_bins[:-1], self.distance_bins[1:]):
            charge_sum += charge_val
            if charge_sum > 0.5:
                return start_radius + (end_radius - start_radius) * (
                    charge_val + 0.5 - charge_sum) / charge_val

        raise ValueError("Radius containing 0.5 e- could not be found.")

    def __str__(self):
        uniform_radius = f"{self.uniform_localization_radius:6.3f}"
        all_lines = [" -- charge localization info",
                     f"Uniform charge radius is {uniform_radius}"]
        lines = [["Band index", "Spin", "Radius", "Center"]]
        for band_idx, c_dist in zip(self.band_indices, self.radial_distributions):
            self._add_band_info(band_idx, c_dist, lines, Spin.up)
            if self.is_spin_polarized:
                self._add_band_info(band_idx, c_dist, lines, Spin.down)

        all_lines.append(tabulate(lines, tablefmt="plain"))
        return "\n".join(all_lines)

    def _add_band_info(self, band_idx, c_dist, lines, spin):
        try:
            radius = f"{self.localization_radius(band_idx, spin):6.3f}"
        except ValueError:
            radius = "None"
        spin_idx = 0 if spin == Spin.up else 1
        spin_str = "up" if spin == Spin.up else "down"
        center = pretty_coords(c_dist[spin_idx].defect_center)
        lines.append([band_idx + 1, spin_str, radius, center])

    @property
    def bin_midpoints(self):
        """Calculate middle points of distance bins."""
        result = []
        for start_radius, end_radius in zip(
                self.distance_bins[:-1], self.distance_bins[1:]):
            result.append((start_radius + end_radius) / 2)
        return result

    def plot_distribution(self):
        """Plot radial charge density distribution.

        Returns:
            matplotlib.pyplot object for further customization.
        """
        plt.xlim([0, self.distance_bins[-1]])
        for charge_dist, band_idx in zip(self.radial_distributions, self.band_indices):
            for dist, spin_label in zip(charge_dist, ["up", "down"]):
                plt.plot(self.bin_midpoints[:-1],
                         dist.density_profile[:-1], label=f"{band_idx} {spin_label}")
        ax = plt.gca()
        ax.legend(loc='upper right')
        return plt

    def find_localized_orbitals(self,
                                radius: float = defaults.localized_orbital_radius,
                                fraction_wrt_uniform: float
                                = defaults.localized_orbital_fraction_wrt_uniform):
        """Identify localized orbitals based on charge distribution.

        Args:
            radius: Maximum localization radius threshold (Å).
            fraction_wrt_uniform: Maximum ratio to uniform radius.

        Returns:
            List of localized band indices per spin channel.
        """
        result = [[] for _spin_idx in range(len(self.radial_distributions[0]))]
        for charge_dist, band_idx in zip(self.radial_distributions, self.band_indices):
            for spin_idx, (dist, spin) in enumerate(zip(charge_dist,
                                                        [Spin.up, Spin.down])):
                try:
                    loc_radius = self.localization_radius(band_idx, spin)
                    loc_fraction = loc_radius / self.uniform_localization_radius
                    if loc_radius < radius and loc_fraction < fraction_wrt_uniform:
                        result[spin_idx].append(band_idx)
                except ValueError:
                    pass

        return result


# Backward compatibility aliases
DefectChargeInfo = ChargeLocalizationInfo
AveChargeDensityDist = RadialChargeDist
