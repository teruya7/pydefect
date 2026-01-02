.PHONY: install install-dev test test-cov lint format clean docs help

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install package in editable mode"
	@echo "  make install-dev  - Install with development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linter (ruff)"
	@echo "  make format       - Format code (ruff)"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make docs         - Build documentation"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest

test-cov:
	pytest --cov=src/pydefect --cov-report=html --cov-report=term-missing

# Linting and formatting
lint:
	ruff check src/pydefect tests

format:
	ruff format src/pydefect tests
	ruff check --fix src/pydefect tests

# Type checking
typecheck:
	mypy src/pydefect

# Documentation
docs:
	cd docs && make html

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Build package
build: clean
	python -m build

# Publish to PyPI (requires authentication)
publish: build
	python -m twine upload dist/*
