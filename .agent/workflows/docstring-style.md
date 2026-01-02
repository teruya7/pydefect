---
description: Add or update Google style docstrings in pydefect
---

# Docstring Style Workflow

This workflow guides you through adding or updating docstrings in pydefect.

## Required Sections by Element Type

### Class (non-dataclass)
1. One-line summary
2. `Attributes:` - Public attributes
3. `Example:` - Usage example
4. `__init__` method must have `Args:` docstring

### Dataclass
1. One-line summary  
2. `Attributes:` - Document all fields (replaces Args)
3. `Example:` - Usage example

### Function/Method
1. One-line summary
2. `Args:` - All parameters with types
3. `Returns:` - Return value description
4. `Example:` - Usage example
5. `Raises:` - (if applicable) Exceptions raised

## Template: Standard Class

```python
class ClassName:
    """One-line summary of class purpose.

    Extended description if needed.

    Attributes:
        attr1: Description of first attribute.
        attr2: Description of second attribute.

    Example:
        >>> obj = ClassName(param1, param2)
        >>> result = obj.method()
    """
    def __init__(self, param1: Type1, param2: Type2):
        """Initialize ClassName.

        Args:
            param1: Description of param1.
            param2: Description of param2.
        """
```

## Template: Function

```python
def function_name(arg1: Type1, arg2: Type2 = default) -> ReturnType:
    """One-line summary of function purpose.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2. Defaults to X.

    Returns:
        Description of return value.

    Example:
        >>> result = function_name(val1, val2)
    """
```

## Checklist

// turbo-all
1. Run validation: `pydocstyle --convention=google <file>`
2. Check Example is runnable (or at least syntactically correct)
3. Verify all Args match function signature
4. Ensure units are specified (eV, Å, K, etc.)
5. Run tests: `pytest tests/ -q`

## Reference

Full guide: [docs/source/style_guide.md](../../docs/source/style_guide.md)
