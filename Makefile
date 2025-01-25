# EC2 Configuration
EC2_IP = 52.23.77.209
EC2_USER = ubuntu
EC2_KEY = ~/switchboard-final.pem

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
.PHONY: check setup preprocess clean install help redact ocr create-df email-analysis deploy ingest-s3 ssl-setup ssl-renew ssl-status domain-check

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

# SSL and Domain Management
ssl-setup:
	@echo "🔒 Setting up SSL certificate for switchboard.miski.studio..."
	ssh -i $(EC2_KEY) ubuntu@$(EC2_IP) "\
		sudo docker-compose down && \
		sudo apt-get update && \
		sudo apt-get install -y certbot && \
		sudo certbot certonly --standalone \
			-d switchboard.miski.studio \
			--agree-tos \
			--non-interactive \
			--email admin@miski.studio"
	@echo "✅ SSL certificate installed"

ssl-renew:
	@echo "🔄 Renewing SSL certificate..."
	ssh -i $(EC2_KEY) ubuntu@$(EC2_IP) "\
		sudo docker-compose down && \
		sudo certbot renew && \
		sudo docker-compose up -d"
	@echo "✅ SSL certificate renewed"

ssl-status:
	@echo "📊 Checking SSL certificate status..."
	ssh -i $(EC2_KEY) ubuntu@$(EC2_IP) "\
		sudo certbot certificates"

domain-check:
	@echo "🌐 Checking domain DNS setup..."
	@echo "Testing DNS resolution for switchboard.miski.studio..."
	@host switchboard.miski.studio || echo "❌ DNS record not found"
	@echo "\nTesting SSL certificate..."
	@curl -sI https://switchboard.miski.studio | head -n 1 || echo "❌ HTTPS not responding"
	@echo "\nChecking port 80..."
	@curl -sI http://switchboard.miski.studio | head -n 1 || echo "❌ HTTP not responding"



# Ingest data from S3 to Elasticsearch
ingest-s3:
	@echo "🚀 Installing elasticdump if not present..."
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "sudo npm install -g elasticdump || true"
	@echo "📦 Running elasticdump to import data..."
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "elasticdump \
		--input=s3://d4bl-switchboard-data/pdf_documents.json \
		--output=http://localhost:9200/pdf_documents \
		--type=data \
		--limit=10000"
	@echo "✨ Import complete! Verifying index..."
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "curl -s http://localhost:9200/pdf_documents/_stats"