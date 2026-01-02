# -*- coding: utf-8 -*-
#  Copyright (c) 2023 Kumagai group.
from numpy import exp
from scipy.constants import physical_constants


k = physical_constants["Boltzmann constant in eV/K"][0]


def fermi_dirac(delta_E: float, T: float):  # delta_E is in eV.
    """Calculate Fermi-Dirac distribution function.

    Args:
        delta_E: Energy difference from Fermi level (eV).
        T: Temperature (K).

    Returns:
        Fermi-Dirac occupation probability (0 to 1).

    Example:
        >>> fermi_dirac(0.0, 300)
        0.5
    """
    return 1. / (exp(delta_E / (k * T)) + 1.)


def boltzmann_dist(delta_E: float, T: float):
    """Calculate Boltzmann distribution function.

    Args:
        delta_E: Energy difference (eV).
        T: Temperature (K).

    Returns:
        Boltzmann probability factor.
    """
    return exp(- delta_E / (k * T))

