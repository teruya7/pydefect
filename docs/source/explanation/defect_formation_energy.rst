Defect Formation Energy
=======================

This page explains the theoretical background of defect formation energy calculations.

Definition
----------

The formation energy of a defect :math:`D` in charge state :math:`q` is defined as:

.. math::

   E_f[D^q] = E[D^q] - E[\text{perfect}] + \sum_i n_i \mu_i + q(\varepsilon_{\text{VBM}} + E_F) + E_{\text{corr}}

where:

- :math:`E[D^q]`: Total energy of supercell with defect
- :math:`E[\text{perfect}]`: Total energy of perfect supercell
- :math:`n_i`: Number of atoms of species :math:`i` removed (+) or added (-)
- :math:`\mu_i`: Chemical potential of species :math:`i`
- :math:`\varepsilon_{\text{VBM}}`: Valence band maximum energy
- :math:`E_F`: Fermi level relative to VBM
- :math:`E_{\text{corr}}`: Electrostatic correction

Physical Meaning
----------------

The formation energy represents the energy cost to create a defect in the crystal.

- **Positive formation energy**: Defect is energetically unfavorable
- **Negative formation energy**: Defect forms spontaneously (high concentration expected)

Charge State
------------

Point defects can exist in multiple charge states. For example:

- Oxygen vacancy: :math:`V_O^{0}`, :math:`V_O^{+1}`, :math:`V_O^{+2}`
- Mg vacancy: :math:`V_{Mg}^{0}`, :math:`V_{Mg}^{-1}`, :math:`V_{Mg}^{-2}`

The stable charge state depends on the Fermi level position:

- **Low Fermi level (p-type)**: Donors prefer positive charges
- **High Fermi level (n-type)**: Acceptors prefer negative charges

Transition Levels
-----------------

The thermodynamic transition level :math:`\varepsilon(q/q')` is the Fermi level
at which two charge states have equal formation energy:

.. math::

   \varepsilon(q/q') = \frac{E_f[D^{q'}] - E_f[D^q]}{q - q'}

This determines whether a defect acts as a deep or shallow trap.

References
----------

1. C. Freysoldt et al., Rev. Mod. Phys. 86, 253 (2014)
2. S. Lany and A. Zunger, Phys. Rev. B 78, 235104 (2008)
