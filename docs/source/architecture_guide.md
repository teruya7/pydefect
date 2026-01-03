# Architecture Guide

This guide describes the architecture and design patterns used in pydefect.

## Project Structure

```
pydefect/
├── src/pydefect/
│   ├── analysis/           # Analysis and post-processing
│   │   ├── chemical_potential/  # Chemical potential diagrams
│   │   ├── corrections/    # Electrostatic corrections (EFNV, GKFO)
│   │   ├── concentration/  # Defect concentration calculations
│   │   ├── defect_energy/  # Formation energy calculations
│   │   ├── structure/      # Structure analysis
│   │   └── unitcell/       # Unit cell properties
│   ├── preparation/        # Input file generation
│   │   ├── defect_set/     # Define defects to calculate
│   │   ├── interstitial/   # Interstitial site handling
│   │   └── supercell/      # Supercell generation
│   ├── api/                # Public programmatic API
│   ├── cli/                # Command-line interface (Typer)
│   │   ├── commands/       # Command implementations
│   │   └── vasp/           # VASP-specific entry points
│   ├── data/               # Reference data (electronegativities, etc.)
│   ├── utils/              # Utility functions and tools
│   ├── defaults.py         # Global configuration
│   └── error.py            # Base exception class
├── tests/                  # Test suite (mirrors src structure)
└── docs/                   # Documentation (Sphinx)
```

---

## Module Responsibilities

### `analysis/` - Post-processing and Analysis

| Directory | Responsibility |
|-----------|---------------|
| `chemical_potential/` | CPD construction, standard/relative energies |
| `corrections/` | EFNV, GKFO corrections |
| `concentration/` | Carrier and defect concentrations |
| `defect_energy/` | Formation energy calculations |
| `structure/` | Defect structure info, comparisons |
| `unitcell/` | Unit cell properties (dielectric, band edges) |
| `band_edge/` | Band edge orbital analysis |

### `preparation/` - Input Generation

| Directory | Responsibility |
|-----------|---------------|
| `supercell/` | Generate isotropic supercells |
| `defect_set/` | Define defects to calculate |
| `interstitial/` | Interstitial site handling |

### `api/` - Programmatic Interface

| Module | Responsibility |
|--------|---------------|
| `supercell.py` | `make_supercell()` |
| `chemical_potential.py` | `make_chem_pot_diag()` |
| `defect_preparation.py` | `make_defect_set()`, `make_defect_entries()` |
| `defect_analysis.py` | `make_defect_structure_info()`, `plot_defect_energy()` |
| `corrections.py` | `make_efnv_correction()`, `make_gkfo_correction()` |
| `band_edge.py` | `make_band_edge_states()` |

### `cli/` - Command-Line Interface

5 entry points using Typer:

| Entry Point | Module |
|------------|--------|
| `pydefect` | `cli/main.py` |
| `pydefect_vasp` | `cli/vasp/main_vasp.py` |
| `pydefect_util` | `cli/main_util.py` |
| `pydefect_vasp_util` | `cli/vasp/main_vasp_util.py` |
| `pydefect_print` | `cli/main_print_json.py` |

Commands are organized in `cli/commands/` by functionality.

---

## Design Patterns

### 1. API-First Design

All functionality is exposed through `pydefect.api`:

```python
from pydefect import api

# Same functionality as CLI
supercell_info, supercell = api.make_supercell(unitcell)
```

CLI commands are thin wrappers around API functions.

### 2. Data Classes with MSONable

Use `@dataclass` with `MSONable` for serialization:

```python
from dataclasses import dataclass
from monty.json import MSONable
from vise.util.mix_in import ToJsonFileMixIn

@dataclass
class CalcResults(MSONable, ToJsonFileMixIn):
    """Results from a DFT calculation."""
    structure: IStructure
    energy: float
    magnetization: float
    site_potentials: List[float]
```

### 3. Maker Pattern for Complex Creation

```python
class SupercellMaker:
    """Create supercell with symmetry analysis."""
    
    def __init__(self, primitive_structure, **kwargs):
        self.supercell = self._create_optimal_supercell()
        self.supercell_info = self._analyze_sites()
```

### 4. Plotter Pattern for Visualization

```python
class DefectEnergyPlotter:
    """Base: Prepares data for plotting."""

class DefectEnergyMplPlotter(DefectEnergyPlotter):
    """Matplotlib implementation."""
    def construct_plot(self):
        ...
```

---

## Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  POSCAR         │────▶│  SupercellMaker │────▶│  supercell_info │
│  (primitive)    │     │                 │     │  .json          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  defect_in.yaml │────▶│  DefectEntries  │────▶│  defect dirs    │
│                 │     │  Maker          │     │  (POSCAR, etc.) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Configuration

### pydefect.yaml

User overrides in working directory:

```yaml
symmetry_length_tolerance: 0.05
ewald_accuracy: 20.0
```

### Defaults Class

```python
from pydefect.defaults import defaults

tolerance = defaults.dist_tol
accuracy = defaults.ewald_accuracy
```
