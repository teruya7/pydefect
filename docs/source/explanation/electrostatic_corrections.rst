Electrostatic Corrections
=========================

Finite-size corrections for charged defects in periodic supercells.

The Problem
-----------

Charged defects in periodic supercells suffer from artificial electrostatic
interactions:

1. **Self-interaction**: Defect interacts with its periodic images
2. **Jellium background**: Compensating uniform charge affects the potential
3. **Potential alignment**: Reference potential shifts with charge

These errors can be several eV for highly charged defects!

Extended FNV Correction (EFNV)
------------------------------

pydefect implements the Extended Freysoldt-Neugebauer-Van de Walle correction
(Kumagai-Oba method), which:

1. Models the defect as a point charge in an anisotropic dielectric
2. Uses Ewald summation for long-range interactions
3. Aligns potentials in the far-field region

The correction energy is:

.. math::

   E_{\text{corr}} = E_{\text{lat}}^{(1)} - E_{\text{lat}}^{(M)} + q \Delta V

where:

- :math:`E_{\text{lat}}^{(1)}`: Point charge self-energy (first-order)
- :math:`E_{\text{lat}}^{(M)}`: Madelung energy of periodic array
- :math:`\Delta V`: Potential alignment term

Site Potential Plot
-------------------

The potential difference between defect and perfect supercells should plateau
in the far-field region:

.. code-block:: text

    Potential
        |     ○ ○ ○ ○ ○ ○ ← Far-field plateau
        |   ○
        | ○
        |○
        |_________________ Distance from defect

The plateau value is used for potential alignment.

GKFO Correction
---------------

For optical transitions between charge states, pydefect also implements the
GKFO (Gake-Kumagai-Freysoldt-Oba) correction.

References
----------

1. Y. Kumagai and F. Oba, Phys. Rev. B 89, 195205 (2014)
2. A. Gake, Y. Kumagai, C. Freysoldt, and F. Oba, Phys. Rev. B 101, 020102(R) (2020)
