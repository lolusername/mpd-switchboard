# Constants
VENV := $(shell poetry env info --path)
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Variables for input and output directories
INPUT_FOLDER := ./data        # Update this path as needed
OUTPUT_DIR := ./reports       # Update this path as needed
METADATA_FILE := ./reports/meta_data.json
DF_CORPORA := ./df_corpora    # New variable for the output file
EMAIL_ANALYSIS_DIR := $(OUTPUT_DIR)/email_analysis

# Group all PHONY targets
.PHONY: check setup preprocess clean install help redact ocr create-df email-analysis

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

# Run the OCR check script
ocr-check: check
	@echo "Running the OCR check script..."
	@poetry run python pre-processing/ocr-check.py \
		--input_folder $(INPUT_FOLDER) \
		--output_dir $(OUTPUT_DIR) || { echo "OCR check failed"; exit 1; }
	@echo "OCR analysis completed successfully"

# OCR target with parameter for in-place processing
ocr:
	@echo "Running OCR on specified PDFs..."
	@if [ "$(INPLACE)" = "true" ]; then \
		poetry run python pre-processing/run-ocr.py \
			--metadata_file $(METADATA_FILE) \
			--in-place \
			--language eng || { echo "OCR processing failed"; exit 1; }; \
		echo "OCR processing completed (in-place)."; \
	else \
		poetry run python pre-processing/run-ocr.py \
			--metadata_file $(METADATA_FILE) \
			--output_dir $(OUTPUT_DIR) \
			--language eng || { echo "OCR processing failed"; exit 1; }; \
		echo "OCR processing completed."; \
	fi

# Redact PDFs with parameter for dry run
redact:
	@echo "Running PDF redaction..."
	@if [ "$(MODE)" = "dry-run" ]; then \
		poetry run python pre-processing/redact.py \
			--input_folder $(INPUT_FOLDER) \
			--output_folder $(OUTPUT_DIR) \
			--dry_run \
			--log_file $(OUTPUT_DIR)/sensitive_data_log.txt || { echo "Dry-run redaction failed"; exit 1; }; \
		echo "Dry-run redaction completed. Check the log at $(OUTPUT_DIR)/sensitive_data_log.txt"; \
	else \
		poetry run python pre-processing/redact.py \
			--input_folder $(INPUT_FOLDER) \
			--output_folder $(OUTPUT_DIR) \
			--log_file $(OUTPUT_DIR)/sensitive_data_log.txt || { echo "Redaction failed"; exit 1; }; \
		echo "PDF redaction completed. Redacted files are saved to $(OUTPUT_DIR) and logs are available at $(OUTPUT_DIR)/sensitive_data_log.txt"; \
	fi

# Clean virtual environment and temporary files
clean:
	@echo "Cleaning up virtual environment and temporary files..."
	@poetry env remove --all 2>/dev/null || true
	@rm -rf $(VENV) __pycache__ .pytest_cache .mypy_cache

# Install dependencies
install:
	@echo "Installing dependencies..."
	@poetry install

# New target for creating the DataFrame
create-df: check
	@echo "Creating DataFrame from PDF documents..."
	@poetry run python pre-processing/create_df.py \
		--input_folder $(INPUT_FOLDER) \
		--output_file $(DF_CORPORA) || { echo "DataFrame creation failed"; exit 1; }
	@echo "DataFrame creation completed successfully"

# Email network analysis target
email-analysis: check
	@echo "Running email network analysis on PDF documents..."
	@mkdir -p ./reports/email_analysis
	@if [ "$(TEST)" = "true" ]; then \
		poetry run python3 pre-processing/generate_email_report.py \
			--pdf_dir ./data \
			--output_dir ./reports/email_analysis \
			--verbose \
			--test-run || { echo "Email network analysis failed"; exit 1; }; \
	else \
		poetry run python3 pre-processing/generate_email_report.py \
			--pdf_dir ./data \
			--output_dir ./reports/email_analysis \
			--verbose || { echo "Email network analysis failed"; exit 1; }; \
	fi
	@echo "Email network analysis completed. Results saved to ./reports/email_analysis"