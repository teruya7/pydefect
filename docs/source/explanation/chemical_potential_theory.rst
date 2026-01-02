Chemical Potential Theory
=========================

Understanding chemical potentials in defect calculations.

Definition
----------

The chemical potential :math:`\mu_i` represents the energy cost to add or remove
an atom of species :math:`i` from the system. In defect calculations, chemical
potentials determine the atomic reservoir conditions.

Equilibrium Conditions
----------------------

Chemical potentials are constrained by thermodynamic equilibrium:

1. **Stability of host compound**:

   For MgAl₂O₄:
   
   .. math::
   
      \mu_{Mg} + 2\mu_{Al} + 4\mu_O = \Delta H_f[\text{MgAl}_2\text{O}_4]

2. **Competition with other phases**:

   The host must be stable against decomposition:
   
   .. math::
   
      \mu_{Mg} + \mu_O &\leq \Delta H_f[\text{MgO}] \\
      2\mu_{Al} + 3\mu_O &\leq \Delta H_f[\text{Al}_2\text{O}_3]

Chemical Potential Diagram
--------------------------

The chemical potential diagram (CPD) visualizes the stable region of the host
compound in chemical potential space.

.. image:: /_images/cpd_MgAl2O4.png
   :width: 400px
   :align: center

Key features:

- **Vertices**: Equilibrium points where host coexists with competing phases
- **Edges**: Two-phase equilibria
- **Interior**: Single-phase stability region

Physical Interpretation
-----------------------

- **O-rich conditions** (vertex C, D): Oxidizing atmosphere, high oxygen partial pressure
- **O-poor conditions** (vertex A, B): Reducing atmosphere, low oxygen partial pressure
- **Metal-rich conditions**: Higher metal chemical potentials

Impact on Defects
-----------------

Chemical potentials directly affect defect formation energies:

- O-rich conditions favor oxygen interstitials, suppress oxygen vacancies
- O-poor conditions favor oxygen vacancies, suppress oxygen interstitials
- Metal-rich conditions favor metal interstitials

References
----------

1. S. B. Zhang and J. E. Northrup, Phys. Rev. Lett. 67, 2339 (1991)
2. K. Reuter and M. Scheffler, Phys. Rev. B 65, 035406 (2001)
