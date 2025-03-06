# Constants
PDF_DIR := ../data
TXT_DIR := ./txt_data
MIXED_DIR := ../data  # Can be changed to any directory containing both PDFs and TXTs
OUTPUT_DIR := ./viz/public/d3_data
PYTHON_VERSION := 3.10.13

.PHONY: help setup install run run-txt run-mixed test test-txt test-mixed clean viz

help:
	@echo "Available commands:"
	@echo "  setup         - Initial project setup (first time setup)"
	@echo "  install      - Install/update dependencies"
	@echo "  run          - Run full analysis on PDF directory"
	@echo "  run-txt      - Run full analysis on TXT directory"
	@echo "  run-mixed    - Run full analysis on directory with both PDFs and TXTs"
	@echo "  test         - Run test analysis on PDF directory (5 files)"
	@echo "  test-txt     - Run test analysis on TXT directory (5 files)"
	@echo "  test-mixed   - Run test analysis on mixed directory (5 files)"
	@echo "  clean        - Remove generated files and cache"
	@echo "  viz          - Launch visualization app"
	@echo "  help         - Show this help message"

setup:
	@command -v pyenv >/dev/null 2>&1 || { echo >&2 "pyenv is required. Please install it first."; exit 1; }
	@command -v poetry >/dev/null 2>&1 || { echo >&2 "poetry is required. Please install it first."; exit 1; }
	@echo "Installing Python $(PYTHON_VERSION) with pyenv..."
	@pyenv install --skip-existing $(PYTHON_VERSION)
	@pyenv local $(PYTHON_VERSION)
	@echo "Configuring Poetry to use Python $(PYTHON_VERSION)..."
	@poetry env use $$(pyenv which python)
	@$(MAKE) install

install:
	@echo "Installing Python dependencies..."
	@poetry install --no-root
	@echo "Installing spaCy model..."
	@poetry run python -m spacy download en_core_web_sm

run: install
	@echo "Running full analysis on PDF directory..."
	@mkdir -p $(OUTPUT_DIR)
	@poetry run python main.py \
		--pdf_dir $(PDF_DIR) \
		--output_dir $(OUTPUT_DIR)

run-txt: install
	@echo "Running full analysis on TXT directory..."
	@mkdir -p $(OUTPUT_DIR)
	@poetry run python main.py \
		--pdf_dir $(TXT_DIR) \
		--output_dir $(OUTPUT_DIR)

run-mixed: install
	@echo "Running full analysis on mixed directory..."
	@poetry run python main.py \
		--pdf_dir $(MIXED_DIR) \
		--output_dir $(OUTPUT_DIR)

test: install
	@echo "Running test analysis on PDF directory (5 files)..."
	@poetry run python main.py \
		--pdf_dir $(PDF_DIR) \
		--output_dir $(OUTPUT_DIR) \
		--test

test-txt: install
	@echo "Running test analysis on TXT directory (5 files)..."
	@poetry run python main.py \
		--pdf_dir $(TXT_DIR) \
		--output_dir $(OUTPUT_DIR) \
		--test

test-mixed: install
	@echo "Running test analysis on mixed directory (5 files)..."
	@poetry run python main.py \
		--pdf_dir $(MIXED_DIR) \
		--output_dir $(OUTPUT_DIR) \
		--test

clean:
	@rm -rf $(OUTPUT_DIR)/*
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete
	@poetry env remove --all 2>/dev/null || true

viz:
	@echo "Starting visualization app..."
	@cd viz && \
		rm -rf node_modules package-lock.json && \
		rm -rf public/data && \
		mkdir -p public && \
		npm install && \
		npm run dev 