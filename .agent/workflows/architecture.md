---
description: Architecture patterns and module design for pydefect
---

# Architecture Workflow

Quick reference for pydefect design patterns and module structure.

## Module Structure

```
pydefect/
├── analyzer/           # Post-processing (corrections, energies)
│   ├── corrections/    # EFNV, GKFO corrections
│   ├── chem_pot_diag/  # Chemical potential diagrams
│   └── concentration/  # Defect concentrations
├── input_maker/        # Input generation (supercells, defects)
├── cli/                # Command-line interface
├── util/               # Utilities
├── api.py              # Public API
└── defaults.py         # Global configuration
```

## Design Patterns

### 1. Dataclass for Data Containers

```python
@dataclass
class CalcResults(MSONable, ToJsonFileMixIn):
    structure: IStructure
    energy: float
    # Use for immutable data with serialization
```

### 2. Maker Pattern for Complex Creation

```python
class SupercellMaker:
    def __init__(self, primitive_structure, ...):
        self.supercell = self._create_optimal_supercell()
        self.supercell_info = self._analyze_sites()
    # Use when creation has complex logic
```

### 3. Plotter Pattern for Visualization

```python
class DefectEnergyPlotter:          # Base: data preparation
class DefectEnergyMplPlotter(DefectEnergyPlotter):  # Impl: matplotlib
    def construct_plot(self): ...
    # Separate data prep from rendering
```

### 4. Mix-in for Serialization

```python
from vise.util.mix_in import ToJsonFileMixIn, ToYamlFileMixIn
# Adds .to_json_file(), .from_json_file(), etc.
```

## Adding New Features

### New Correction Method:
1. Create `analyzer/corrections/new_correction.py` (data)
2. Create `analyzer/corrections/make_new_correction.py` (factory)
3. Add CLI command in `cli/corrections.py`

### New Plotter:
1. Create `PlotterBase` for data preparation
2. Create `MplPlotter(PlotterBase)` for matplotlib
3. Add `construct_plot()` method

## Serialization

| Format | Use Case | Method |
|--------|----------|--------|
| JSON | Complex objects | `to_json_file()` |
| YAML | Human-editable | `to_yaml()` |

## Reference

Full guide: [docs/source/architecture_guide.md](../../docs/source/architecture_guide.md)
