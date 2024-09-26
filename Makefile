# Constants
VENV := $(shell poetry env info --path)
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Variables for input and output directories
INPUT_FOLDER := ./data  # Update this path as needed
OUTPUT_DIR := ./reports  # Update this path as needed
METADATA_FILE := ./reports/meta_data.json

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
size-check: check
	@echo "Running the PDF document size analysis script..."
	@poetry run python pre-processing/doc-size-analysis.py \
		--input_folder $(INPUT_FOLDER) \
		--output_dir $(OUTPUT_DIR) || { echo "Pre-processing failed"; exit 1; }
	@echo "Pre-processing completed successfully"

# Run the OCR check  script
ocr-check: check
	@echo "Running the OCR check script..."
	@poetry run python pre-processing/ocr-check.py \
		--input_folder $(INPUT_FOLDER) \
		--output_dir $(OUTPUT_DIR) || { echo "Pre-processing failed"; exit 1; }
	@echo "OCR analysis completed successfully"

# OCR target
ocr:
	@echo "Running OCR on specified PDFs..."
	@poetry run python pre-processing/run-ocr.py \
		--metadata_file $(METADATA_FILE) \
		--output_dir $(OUTPUT_DIR) \
		--language eng
	@echo "OCR processing completed."

	
# OCR target (In-Place Processing)
ocr-inplace:
	@echo "Running OCR on specified PDFs (in-place)..."
	@poetry run python pre-processing/run-ocr.py \
		--metadata_file $(METADATA_FILE) \
		--in-place \
		--language eng
	@echo "OCR processing completed."

# Clean virtual environment and temporary files
clean:
	@echo "Cleaning up virtual environment and temporary files..."
	@poetry env remove --all 2>/dev/null || true
	@rm -rf $(VENV) __pycache__ .pytest_cache .mypy_cache

# Install dependencies
install:
	@echo "Installing dependencies..."
	@poetry install
