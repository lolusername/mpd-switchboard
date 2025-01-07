# Switchboard: Document Analysis Platform

A comprehensive platform for analyzing document collections through advanced text processing, network analysis, and interactive visualizations. Built by Miski Studio for Data for Black Lives (D4BL) to help researchers, journalists, and community members understand complex document collections.

## Project Structure

```
switchboard/
├── app/                    # Main application
│   ├── api/               # FastAPI backend
│   ├── frontend/          # Nuxt.js frontend
│   ├── elasticsearch-init/ # Search initialization
│   └── docker-compose.yml # Container configuration
├── pre-processing/        # Document preparation tools
│   ├── scripts/          # Processing scripts
│   └── Makefile          # Processing automation
├── data/                  # Document storage
│   ├── raw/              # Original documents
│   ├── processed/        # OCR'd documents
│   └── redacted/         # Redacted documents
└── reports/              # Analysis outputs
    ├── meta_data.json    # Document metadata
    ├── email_analysis/   # Communication patterns
    └── sensitive_data_log.txt # Redaction records
```

## Key Features

- 📄 Advanced Document Processing
  - Automated OCR and text extraction
  - Multi-format document support
  - Batch processing with progress tracking
  - Memory-efficient handling of large documents

- 🔍 Intelligent Search & Analysis
  - Full-text search across all documents
  - Entity recognition and relationship mapping
  - Advanced topic modeling with BERTopic
  - Communication pattern analysis

- 🔒 Privacy & Security
  - Automatic PII detection and redaction
  - Role-based access controls
  - Audit logging
  - GDPR-compliant data handling

- 📊 Interactive Visualizations
  - Entity relationship networks
  - Communication pattern analysis
  - Topic clustering and evolution
  - Domain interaction heatmaps

## Tech Stack

### Backend
- Python 3.12+
- FastAPI
- Elasticsearch 8.12.2
- SpaCy & BERTopic for NLP

### Frontend
- Nuxt.js
- D3.js for visualizations
- TailwindCSS
- TypeScript

### Processing Pipeline
- Tesseract OCR
- pdfminer-six
- BERT-based models
- Custom NER models

## Quick Start

1. Prerequisites:
   - Python 3.12+
   - Node.js 20+
   - Docker 20+
   - Poetry
   - Make

2. Clone and setup:
   ```bash
   git clone https://github.com/d4bl/switchboard.git
   cd switchboard/app
   poetry install
   cd frontend && npm install
   ```

3. Start services:
   ```bash
   make up
   ```

4. Access:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Elasticsearch: http://localhost:9200

## Document Processing Pipeline

1. Document Standardization
   - Converts various PDF formats
   - Normalizes text content
   - Handles batch processing

2. OCR Processing
   - Detects and processes non-searchable PDFs
   - Multi-language support
   - Progress tracking

3. Automated Redaction
   - NER for sensitive data
   - Pattern matching for PII
   - Verification through dry-runs

4. Network Analysis
   - Maps communication patterns
   - Identifies key relationships
   - Generates visualizations

## System Requirements

### Hardware Recommendations
- CPU: 4+ cores for OCR
- RAM: 16GB+ recommended
- Storage: 3x input data size
- SSD recommended

### Software Dependencies
- Docker & Docker Compose
- Tesseract 4.0+
- Elasticsearch 8.12.2
- Python 3.12+

## Contributing

We welcome contributions! Key areas:
- Improved entity recognition
- Additional visualizations
- Performance optimizations
- Documentation improvements


## Make Commands

### Setup & Installation
- `make check` - Verifies pyenv and poetry are installed
- `make setup` - Sets up Python environment using Poetry
- `make install` - Installs project dependencies
- `make clean` - Removes virtual environment and temporary files

### Document Analysis
- `make size-check` - Analyzes PDF document sizes and generates report
- `make ocr-check` - Identifies which PDFs need OCR processing
- `make create-df` - Creates DataFrame from PDF documents for analysis

### Processing
- `make ocr [INPLACE=true]` - Runs OCR on PDFs
  - Use INPLACE=true to modify files in place
  - Default: Creates new files in output directory
  
- `make redact [MODE=dry-run]` - Handles document redaction
  - Use MODE=dry-run to test without modifying files
  - Default: Performs actual redaction
  - Saves logs to ./reports/sensitive_data_log.txt

### Analysis Tools
- `make email-analysis [TEST=true]` - Analyzes email communication patterns
  - Use TEST=true for test run
  - Outputs network graphs and statistics
  - Saves results to ./reports/email_analysis/

### Directory Structure
- Input files go in ./data
- Processed files saved to ./reports
- Analysis outputs in ./reports/email_analysis
- Metadata stored in ./reports/meta_data.json

## License
Copyright © 2024 Data for Black Lives (D4BL)
Developed by Miski Studio / Atilio Barreda II

All rights reserved. This software and associated documentation files are the proprietary property of Data for Black Lives (D4BL). No part of this software may be reproduced, distributed, or transmitted in any form or by any means without the prior written permission of Data for Black Lives (D4BL).