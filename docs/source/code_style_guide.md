# Code Style Guide

This guide defines the coding conventions for the pydefect project.

## Overview

pydefect follows PEP 8 with specific conventions for scientific computing code.

---

## Naming Conventions

### Variables

| Type | Convention | Example |
|------|------------|---------|
| Local variables | `snake_case` | `defect_energy`, `site_index` |
| Constants | `UPPER_SNAKE_CASE` | `BOLTZMANN_CONSTANT`, `AtoZ` |
| Private attributes | `_leading_underscore` | `_mpl_defaults`, `_title` |
| Protected (internal) | `_single_underscore` | `_create_defect_structures` |

### Classes

```python
# Good: Clear, descriptive names
class DefectStructureComparator:
class ExtendedFnvCorrection:
class CalcResults:

# Avoid: Abbreviations that aren't universally known
class DSC:  # Bad
class EFNVCorr:  # Bad
```

### Functions and Methods

```python
# Good: Verb phrases for actions
def make_efnv_correction(...):
def calculate_formation_energy(...):
def get_defect_charge_state(...):

# Good: Noun phrases for factory functions
def from_json_file(cls, ...):
def from_yaml(cls, ...):

# Properties: Noun phrases
@property
def correction_energy(self):
    ...
```

### File Names

```python
# Good: Descriptive, matches main class/function
make_efnv_correction.py  # Contains make_efnv_correction()
defect_structure_info.py  # Contains DefectStructureInfo
calc_results.py  # Contains CalcResults

# Avoid
utils.py  # Too generic (use specific names)
helpers.py  # Too vague
```

---

## Type Hints

### Required Locations

```python
# Function signatures: Always use type hints
def make_correction(structure: Structure,
                    charge: int,
                    dielectric: np.ndarray) -> Correction:
    ...

# Class attributes in dataclasses
@dataclass
class DefectEnergy(MSONable):
    formation_energy: float
    energy_corrections: Dict[str, float] = None
    is_shallow: Optional[bool] = None
```

### Common Type Patterns

```python
from typing import List, Dict, Optional, Tuple, Union

# Optional parameters
def process(data: Structure, tolerance: Optional[float] = None):
    ...

# Union types (prefer Optional for None cases)
coord: Union[List[float], Tuple[float, float, float]]

# Collections
energies: List[float]
site_map: Dict[int, str]
coordinates: Tuple[float, float, float]

# NumPy arrays
import numpy as np
matrix: np.ndarray  # General array
lattice: np.ndarray  # 3x3 array (document shape in docstring)
```

---

## Imports

### Order (PEP 8 + isort)

```python
# 1. Standard library
from dataclasses import dataclass
from typing import List, Optional, Dict
import numpy as np

# 2. Third-party packages
from monty.json import MSONable
from pymatgen.core import Structure, Element

# 3. Local imports (absolute)
from pydefect.analyzer.calc_results import CalcResults
from pydefect.defaults import defaults

# 4. Relative imports (same package)
from .defect_structure_comparator import DefectStructureComparator
```

### Guidelines

```python
# Good: Explicit imports
from pydefect.analyzer.calc_results import CalcResults

# Avoid: Star imports
from pydefect.analyzer import *  # Bad

# Exception: pymatgen.core is commonly used
from pymatgen.core import Structure, Element, Composition
```

---

## Code Organization

### Class Structure

```python
class DefectAnalyzer:
    """Class docstring."""
    
    # 1. Class-level constants
    DEFAULT_TOLERANCE = 0.1
    
    # 2. __init__
    def __init__(self, ...):
        ...
    
    # 3. Properties (alphabetical)
    @property
    def energy(self) -> float:
        ...
    
    # 4. Public methods (logical order)
    def analyze(self):
        ...
    
    def export(self):
        ...
    
    # 5. Private methods (order of use)
    def _calculate_internal(self):
        ...
    
    # 6. Class methods and static methods (at end)
    @classmethod
    def from_file(cls, filename: str):
        ...
    
    @staticmethod
    def validate_input(data):
        ...
```

### Function Length

- Target: Under 50 lines per function
- Extract helper functions for complex logic
- Each function should do one thing well

---

## Scientific Computing Conventions

### Physical Units

```python
# Always document units in docstrings and variable names when helpful
energy_ev: float  # Energy in eV
distance_angstrom: float  # Distance in Å
temperature_K: float  # Temperature in Kelvin

# Or document in docstring
def calculate_energy(temperature: float) -> float:
    """Calculate thermal energy.
    
    Args:
        temperature: Temperature in Kelvin.
    
    Returns:
        Energy in eV.
    """
```

### NumPy Conventions

```python
# Use descriptive names for arrays
lattice_vectors = np.array(...)  # Not 'a' or 'mat'
dielectric_tensor = np.eye(3) * 10.0  # Not 'eps'

# Document array shapes in docstrings
def transform(matrix: np.ndarray) -> np.ndarray:
    """Transform coordinates.
    
    Args:
        matrix: 3x3 transformation matrix.
    
    Returns:
        Transformed 3x3 matrix.
    """
```

---

## Error Handling

### Custom Exceptions

```python
from pydefect.error import PydefectError

class SupercellError(PydefectError):
    """Error during supercell generation."""
    pass

# Usage
if not valid:
    raise SupercellError("Invalid transformation matrix")
```

### Logging

```python
from vise.util.logger import get_logger

logger = get_logger(__name__)

# Use appropriate levels
logger.debug("Detailed calculation info")
logger.info("Progress information")
logger.warning("Non-fatal issues")
logger.error("Errors that don't stop execution")
```

---

## Testing Conventions

### Test File Organization

```
tests/
├── analyzer/
│   ├── test_calc_results.py
│   ├── test_defect_energy.py
│   └── corrections/
│       └── test_efnv_correction.py
└── input_maker/
    └── test_supercell_maker.py
```

### Test Naming

```python
# Test function names: test_<what>_<condition>_<expected>
def test_energy_with_correction_returns_sum():
    ...

def test_from_file_missing_file_raises_error():
    ...

# Fixtures
@pytest.fixture
def simple_structure():
    return Structure(...)
```

---

## Formatting Tools

```bash
# Check formatting
black --check src/pydefect/

# Format code
black src/pydefect/

# Sort imports
isort src/pydefect/

# Check style
flake8 src/pydefect/
```

---

## Summary Checklist

- [ ] Variable names are descriptive and use `snake_case`
- [ ] Type hints on all function signatures
- [ ] Imports ordered correctly
- [ ] No star imports
- [ ] Physical units documented
- [ ] Functions under 50 lines
- [ ] Custom exceptions inherit from `PydefectError`
- [ ] Logger used instead of print statements
