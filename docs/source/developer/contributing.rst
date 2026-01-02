Contributing to pydefect
========================

Thank you for your interest in contributing!

Development Setup
-----------------

1. Clone the repository:

.. code-block:: bash

    git clone https://github.com/kumagai-group/pydefect.git
    cd pydefect

2. Install in development mode:

.. code-block:: bash

    pip install -e .

3. Run tests:

.. code-block:: bash

    pytest tests/

Code Style
----------

See the following guides:

- :doc:`style_guide` - Docstring conventions
- :doc:`code_style_guide` - Naming, types, imports
- :doc:`architecture_guide` - Module design patterns

Pull Request Process
--------------------

1. Create a feature branch from ``main``
2. Add tests for new functionality
3. Ensure all tests pass
4. Update docstrings following the style guide
5. Submit PR with clear description

Testing
-------

.. code-block:: bash

    # Run all tests
    pytest tests/

    # Run with coverage
    pytest tests/ --cov=src/pydefect

    # Run specific test file
    pytest tests/analyzer/test_calc_results.py
