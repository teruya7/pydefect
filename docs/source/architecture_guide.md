# Architecture Guide

This guide describes the architecture and design patterns used in pydefect.

## Project Structure

```
pydefect/
├── src/pydefect/
│   ├── analyzer/           # Analysis and post-processing
│   │   ├── corrections/    # Electrostatic corrections (EFNV, GKFO)
│   │   ├── chem_pot_diag/  # Chemical potential diagrams
│   │   └── concentration/  # Defect concentration calculations
│   ├── cli/                # Command-line interface (Typer)
│   ├── database/           # Reference data (electronegativities, etc.)
│   ├── input_maker/        # Input file generation
│   ├── util/               # Utility functions and tools
│   ├── api.py              # Public programmatic API
│   ├── defaults.py         # Global configuration
│   └── error.py            # Base exception class
├── tests/                  # Test suite (mirrors src structure)
└── docs/                   # Documentation (Sphinx)
```

---

## Module Responsibilities

### `analyzer/` - Post-processing and Analysis

| Module | Responsibility |
|--------|---------------|
| `calc_results.py` | Store DFT calculation results |
| `defect_energy.py` | Formation energy data structures |
| `defect_structure_info.py` | Defect structure analysis |
| `defect_structure_comparator.py` | Compare defect/perfect structures |
| `band_edge_states.py` | Band edge orbital analysis |
| `unitcell.py` | Unit cell properties (dielectric, band edges) |

### `analyzer/corrections/` - Electrostatic Corrections

| Module | Responsibility |
|--------|---------------|
| `efnv_correction.py` | Extended FNV correction data |
| `make_efnv_correction.py` | Create EFNV corrections |
| `gkfo_correction.py` | GKFO optical correction |
| `ewald.py` | Anisotropic Ewald summation |

### `input_maker/` - Input Generation

| Module | Responsibility |
|--------|---------------|
| `supercell_maker.py` | Generate isotropic supercells |
| `supercell_info.py` | Store supercell metadata |
| `defect_set.py` | Define defects to calculate |
| `defect_entry.py` | Individual defect structures |
| `defect_entries_maker.py` | Generate defect entries |

### `cli/` - Command-Line Interface

| Module | Responsibility |
|--------|---------------|
| `typer_app.py` | Main CLI application |
| `vasp.py` | VASP-specific commands |
| `structure.py` | Structure manipulation commands |
| `energies.py` | Energy calculation commands |
| `corrections.py` | Correction commands |

---

## Design Patterns

### 1. Data Classes for Immutable Data

Use `@dataclass` for data containers without complex logic:

```python
@dataclass
class CalcResults(MSONable, ToJsonFileMixIn):
    """Results from a DFT calculation."""
    structure: IStructure
    energy: float
    magnetization: float
    potentials: List[float]
    electronic_conv: Optional[bool] = None
    ionic_conv: Optional[bool] = None
```

**When to use:**
- Data is primarily stored, not heavily processed
- Serialization to JSON/YAML is needed
- Immutability is desired (`frozen=True`)

### 2. Maker Pattern for Complex Object Creation

Use `*Maker` classes when object creation has complex logic:

```python
class SupercellMaker:
    """Create supercell and supercell info from primitive structure."""
    
    def __init__(self, primitive_structure, **kwargs):
        # Complex logic: symmetry analysis, optimization
        self.supercell = self._create_optimal_supercell()
        self.supercell_info = self._analyze_sites()
```

**When to use:**
- Multiple steps or decisions in object creation
- Need to store intermediate results
- Factory method would be too complex

### 3. Plotter Pattern for Visualization

Separate data preparation from matplotlib specifics:

```python
class DefectEnergyPlotter:
    """Base class: Prepares data for plotting."""
    def __init__(self, defect_energy_summary, ...):
        self.charge_energies = ...  # Data preparation

class DefectEnergyMplPlotter(DefectEnergyPlotter):
    """Matplotlib implementation."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plt = plt
    
    def construct_plot(self):
        self._add_energies()
        self._set_labels()
        ...
```

**Benefits:**
- Easy to add other backends (plotly, etc.)
- Data preparation is testable without matplotlib
- Consistent plotting API

### 4. Mix-in Classes for Serialization

Use mix-ins from `vise.util.mix_in`:

```python
from vise.util.mix_in import ToJsonFileMixIn, ToYamlFileMixIn

@dataclass
class CalcResults(MSONable, ToJsonFileMixIn):
    """Adds .to_json_file() and .from_json_file() methods."""
    ...

class CompositionEnergies(ToYamlFileMixIn, dict):
    """Adds .to_yaml() and .from_yaml() methods."""
    ...
```

---

## Data Flow

### Typical Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  VASP Output    │────▶│  CalcResults    │────▶│  DefectEnergy   │
│  (vasprun.xml)  │     │  (JSON file)    │     │  Summary        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │  Correction     │
                        │  (EFNV/GKFO)    │
                        └─────────────────┘
```

### Input Preparation

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  POSCAR         │────▶│  SupercellMaker │────▶│  SupercellInfo  │
│  (primitive)    │     │                 │     │  (JSON file)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  DefectSet      │────▶│  DefectEntries  │────▶│  DefectEntry    │
│  (YAML file)    │     │  Maker          │     │  directories    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Serialization Strategy

### JSON for Complex Objects

```python
# Objects with nested structures, numpy arrays
calc_results.to_json_file("calc_results.json")
correction.to_json_file("correction.json")
```

### YAML for Human-Editable Files

```python
# Configuration-like data, simple key-value
defect_set.to_yaml("defect_in.yaml")
composition_energies.to_yaml("composition_energies.yaml")
```

### MSONable for Pymatgen Compatibility

All data classes inherit from `MSONable` for JSON serialization:

```python
from monty.json import MSONable

@dataclass
class DefectEnergy(MSONable):
    # Automatically gets as_dict() and from_dict() methods
    ...
```

---

## Configuration

### Global Defaults

```python
from pydefect.defaults import defaults

# Access defaults
tolerance = defaults.dist_tol
accuracy = defaults.ewald_accuracy

# Override via pydefect.yaml in working directory
# symmetry_length_tolerance: 0.05
# ewald_accuracy: 20.0
```

### Defaults Class (Singleton)

```python
@singleton
class Defaults(DefaultsBase):
    """Global default settings."""
    
    def __init__(self):
        self._dist_tol = 1.0
        self._ewald_accuracy = 15.0
        # Load user overrides
        self.set_user_settings(yaml_filename="pydefect.yaml")
```

---

## Dependencies

### Core Dependencies

| Package | Usage |
|---------|-------|
| `pymatgen` | Crystal structures, symmetry |
| `monty` | Serialization (MSONable), utilities |
| `numpy` | Numerical computations |
| `scipy` | Ewald summation, optimization |
| `vise` | Logging, symmetry, mix-ins |

### Visualization

| Package | Usage |
|---------|-------|
| `matplotlib` | All plotting |
| `tabulate` | Text table formatting |

### CLI

| Package | Usage |
|---------|-------|
| `typer` | Command-line interface |

---

## Extension Points

### Adding a New Correction Method

1. Create `analyzer/corrections/new_correction.py`:
   ```python
   @dataclass
   class NewCorrection(Correction):
       # Data fields
       ...
   ```

2. Create `analyzer/corrections/make_new_correction.py`:
   ```python
   def make_new_correction(...) -> NewCorrection:
       ...
   ```

3. Add CLI command in `cli/corrections.py`

### Adding a New Plotter

1. Create base data class if needed
2. Create `PlotterBase` class for data preparation
3. Create `MplPlotter` subclass for matplotlib
4. Follow existing patterns (e.g., `DefectEnergyMplPlotter`)

---

## Testing Strategy

### Unit Tests
- Test individual functions and classes
- Mock external dependencies (VASP files, MP API)
- Located in `tests/` mirroring `src/` structure

### Integration Tests
- Test workflows end-to-end
- Use fixture data in `tests/*/data/`

### Fixtures
- Common test fixtures in `conftest.py`
- Shared structures, defect entries, etc.
