# Contributing to pydefect

Thank you for your interest in contributing to pydefect!

## Development Setup

1. Clone the repository
2. Install in development mode: `pip install -e .`
3. Run tests: `pytest tests/`

## Style Guides

pydefect has comprehensive style documentation:

| Guide | Description |
|-------|-------------|
| [Docstring Style Guide](docs/source/style_guide.md) | Google style docstrings |
| [Code Style Guide](docs/source/code_style_guide.md) | Naming, types, imports |
| [Architecture Guide](docs/source/architecture_guide.md) | Module design and patterns |


#### Quick Summary

| Element | Required Sections |
|---------|------------------|
| Class | Summary, Attributes, Example |
| Function | Summary, Args, Returns, Example |
| Dataclass | Summary, Attributes |

#### Minimal Example

```python
def calculate_energy(structure: Structure, charge: int) -> float:
    """Calculate formation energy for a defect.

    Args:
        structure: Defect structure.
        charge: Defect charge state.

    Returns:
        Formation energy in eV.

    Example:
        >>> energy = calculate_energy(defect_structure, 2)
    """
```

### Code Formatting

- Use type hints for function parameters and returns
- Follow PEP 8 naming conventions
- Maximum line length: 88 characters (Black default)

## Pull Request Process

1. Create a feature branch from `main`
2. Add tests for new functionality
3. Ensure all tests pass: `pytest tests/`
4. Update docstrings following the style guide
5. Submit PR with clear description

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/pydefect

# Run specific test file
pytest tests/analyzer/test_calc_results.py
```

## Questions?

Open an issue for questions or suggestions.
