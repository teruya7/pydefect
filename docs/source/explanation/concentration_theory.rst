Concentration Theory
====================

Calculating defect concentrations from formation energies.

Thermodynamic Equilibrium
-------------------------

At thermal equilibrium, defect concentrations follow Boltzmann statistics:

.. math::

   c[D^q] = N_D \cdot g_D \cdot \exp\left(-\frac{E_f[D^q]}{k_B T}\right)

where:

- :math:`N_D`: Concentration of available sites
- :math:`g_D`: Degeneracy factor (site × spin)
- :math:`E_f[D^q]`: Formation energy
- :math:`k_B T`: Thermal energy

Charge Neutrality
-----------------

The Fermi level is determined by the charge neutrality condition:

.. math::

   n - p + \sum_D \sum_q q \cdot c[D^q] = 0

where:

- :math:`n`: Electron concentration
- :math:`p`: Hole concentration

This equation is solved self-consistently with the defect formation energies.

Carrier Concentrations
----------------------

Electrons and holes are calculated from the density of states:

.. math::

   n &= \int_{E_{\text{CBM}}}^{\infty} D(E) f(E) dE \\
   p &= \int_{-\infty}^{E_{\text{VBM}}} D(E) [1 - f(E)] dE

where :math:`f(E)` is the Fermi-Dirac distribution.

Temperature Dependence
----------------------

Defect concentrations are highly temperature-dependent:

- **High temperature**: Higher concentrations, faster equilibration
- **Low temperature**: Lower concentrations, frozen-in defects

Quenching from high temperature can preserve high-temperature defect
distributions at lower temperatures.

References
----------

1. J. S. Park et al., Nat. Rev. Mater. 3, 194 (2018)
