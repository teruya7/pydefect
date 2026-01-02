---
description: Code style conventions for pydefect (naming, types, imports)
---

# Code Style Workflow

Quick reference for pydefect code conventions.

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | `snake_case` | `defect_energy`, `site_index` |
| Constants | `UPPER_SNAKE_CASE` | `BOLTZMANN_CONSTANT` |
| Classes | `PascalCase` | `DefectStructureComparator` |
| Private | `_leading_underscore` | `_mpl_defaults` |

## Type Hints

Always add type hints to function signatures:

```python
def make_correction(structure: Structure,
                    charge: int,
                    dielectric: np.ndarray) -> Correction:
    ...
```

## Import Order

```python
# 1. Standard library
from dataclasses import dataclass
from typing import List, Optional

# 2. Third-party
from monty.json import MSONable
from pymatgen.core import Structure

# 3. Local (absolute)
from pydefect.analyzer.calc_results import CalcResults

# 4. Relative (same package)
from .defect_structure_comparator import DefectStructureComparator
```

## Physical Units

Always document units in docstrings:
- Energy: eV
- Distance: Å (Angstrom)
- Temperature: K (Kelvin)

## Checklist

// turbo-all
1. Check naming conventions
2. Add type hints to new functions
3. Sort imports: `isort <file>`
4. Format code: `black <file>`
5. Check style: `flake8 <file>`

## Reference

Full guide: [docs/source/code_style_guide.md](../../docs/source/code_style_guide.md)
