# Docstring Style Guide

This guide defines the docstring conventions for the pydefect project, following Google style.

## Overview

All code in pydefect uses **Google style docstrings**. This ensures consistent, readable documentation that integrates well with Sphinx autodoc.

## Quick Reference

| Element | Required Sections |
|---------|------------------|
| Module | One-line summary, Example |
| Class | Summary, Attributes, Example |
| `__init__` | Args (unless dataclass) |
| Function/Method | Summary, Args, Returns, Example |
| Dataclass | Summary, Attributes (replaces Args) |

---

## Class Docstrings

### Standard Class

```python
class DefectStructureComparator:
    """Compare defect and perfect structures to identify defect sites.

    Maps atoms between the defect and perfect structures to find vacancies,
    interstitials, and substitutions.

    Attributes:
        dist_tol: Distance tolerance for site matching in Angstroms.
        perfect_to_defect_indices: Mapping from perfect to defect indices.
        defect_to_perfect_indices: Mapping from defect to perfect indices.

    Example:
        >>> from pymatgen.core import Structure
        >>> perfect = Structure.from_file("perfect.vasp")
        >>> defect = Structure.from_file("defect.vasp")
        >>> comparator = DefectStructureComparator(defect, perfect)
        >>> print(comparator.removed_indices)
        [42]
    """
    def __init__(self,
                 defect_structure: IStructure,
                 perfect_structure: IStructure,
                 dist_tol: float = defaults.dist_tol):
        """Initialize DefectStructureComparator.

        Args:
            defect_structure: Structure containing the defect.
            perfect_structure: Reference perfect supercell structure.
            dist_tol: Distance tolerance for site matching in Angstroms.
        """
```

### Dataclass

For dataclasses, use `Attributes` in the class docstring. No separate `__init__` docstring is needed.

```python
@dataclass
class CalcResults(MSONable, ToJsonFileMixIn):
    """Results from a DFT calculation.

    Stores structure, energy, and convergence information.

    Attributes:
        structure: Relaxed structure from calculation.
        energy: Total energy in eV.
        magnetization: Total magnetization in μB.
        potentials: Electrostatic potentials at atomic sites.
        electronic_conv: Whether SCF converged.
        ionic_conv: Whether ionic relaxation converged.

    Example:
        >>> results = CalcResults.from_json_file("calc_results.json")
        >>> print(results.energy)
        -150.5
    """
    structure: IStructure
    energy: float
    magnetization: float
    potentials: List[float]
    electronic_conv: Optional[bool] = None
    ionic_conv: Optional[bool] = None
```

---

## Function Docstrings

```python
def make_efnv_correction(defect_entry: DefectEntry,
                         calc_results: CalcResults,
                         perfect_calc_results: CalcResults,
                         dielectric_tensor: np.ndarray) -> ExtendedFnvCorrection:
    """Create EFNV electrostatic correction for charged defects.

    Calculates the extended Freysoldt-Neugebauer-Van de Walle correction
    using Ewald summation with an anisotropic dielectric tensor.

    Args:
        defect_entry: DefectEntry with defect information.
        calc_results: CalcResults from defect calculation.
        perfect_calc_results: CalcResults from perfect supercell.
        dielectric_tensor: 3x3 dielectric tensor.

    Returns:
        ExtendedFnvCorrection object with correction energy.

    Raises:
        ValueError: If structures are incompatible.

    Example:
        >>> correction = make_efnv_correction(
        ...     defect_entry, defect_results, perfect_results, dielectric
        ... )
        >>> print(correction.correction_energy)
        0.15
    """
```

---

## Section Descriptions

### Args
- List each parameter with type and description
- Include default value meaning if not obvious
- Use consistent formatting: `param_name: Description.`

### Returns
- Describe what is returned
- For complex returns, describe structure

### Raises
- List exceptions that may be raised
- Include conditions that trigger each exception

### Attributes
- List public attributes accessible on the instance
- Include type and description
- Private attributes (starting with `_`) are optional

### Example
- Provide runnable code when possible
- Show typical usage patterns
- Include expected output for clarity

---

## Special Cases

### Plotter Classes

```python
class DefectEnergyMplPlotter(DefectEnergyPlotter):
    """Matplotlib plotter for defect formation energies.

    Creates publication-quality defect energy diagrams.

    Attributes:
        plt: Matplotlib pyplot module.

    Example:
        >>> plotter = DefectEnergyMplPlotter(
        ...     defect_energy_summary=summary,
        ...     chem_pot_label="A",
        ...     allow_shallow=False,
        ...     with_corrections=True
        ... )
        >>> plotter.construct_plot()
        >>> plotter.plt.savefig("defect_energy.pdf")
    """
```

### Settings Classes

```python
class EigenvalueMplSettings:
    """Matplotlib settings for eigenvalue plots.

    Attributes:
        colors: Color iterator for plot elements.
        line_width: Width of data lines.
        circle_size: Size of scatter markers.
        vline: Style dict for band edge lines.

    Example:
        >>> settings = EigenvalueMplSettings(circle_size=15)
    """
```

### Exception Classes

```python
class PydefectError(Exception):
    """Base exception for pydefect errors.

    Example:
        >>> raise PydefectError("Something went wrong")
    """
```

---

## Best Practices

1. **Be Concise**: First line should be a complete sentence under 80 characters
2. **Use Imperative Mood**: "Calculate..." not "Calculates..."
3. **Document Units**: Always specify units (eV, Å, K, etc.)
4. **Provide Context**: Explain *why*, not just *what*
5. **Keep Examples Simple**: Show the common case, not edge cases
6. **Update When Changing**: Docstrings must stay in sync with code

---

## Validation

Use `pydocstyle` to check compliance:

```bash
pydocstyle --convention=google src/pydefect/
```

---

## References

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Napoleon Extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
