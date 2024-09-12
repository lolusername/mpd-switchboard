# Constants
VENV := $(shell poetry env info --path)
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Group all PHONY targets
.PHONY: check setup preprocess clean install help

# Ensure pyenv and poetry are available
check:
	@command -v pyenv >/dev/null 2>&1 || { echo >&2 "pyenv is not installed. Please install it."; exit 1; }
	@command -v poetry >/dev/null 2>&1 || { echo >&2 "poetry is not installed. Please install it."; exit 1; }

# Setup Python environment using Poetry
setup: check
	@echo "Setting up Python environment with Poetry..."
	@poetry install
	@echo "Environment setup complete. Use 'poetry shell' to activate."

# Run the pre-processing PDF script
preprocess: check
	@echo "Running the PDF pre-processing script..."
	@poetry run python pre-processing/app.py || { echo "Pre-processing failed"; exit 1; }
	@echo "Pre-processing completed successfully"

# Clean virtual environment and temporary files
clean:
	@echo "Cleaning up virtual environment and temporary files..."
	@poetry env remove --all 2>/dev/null || true
	@rm -rf $(VENV) __pycache__ .pytest_cache .mypy_cache

# Install dependencies
install:
	@echo "Installing dependencies..."
	@poetry install


# Help command to display available tasks
help:
	@echo "Available commands:"
	@echo "  setup           Set up the project (creates Poetry environment and installs dependencies)"
	@echo "  preprocess      Run the pre-processing step for the PDF reports"
	@echo "  clean           Clean up the environment and temporary files"
	@echo "  install         Install dependencies from the pyproject.toml file"

# Default target
.DEFAULT_GOAL := help