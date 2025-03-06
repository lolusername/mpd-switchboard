# Switchboard: Document Analysis Platform

A comprehensive platform for analyzing document collections through advanced text processing, network analysis, and interactive visualizations. Built by Miski Studio to help researchers, journalists, and community members understand complex document collections.

# Switchboard: Document Analysis Platform

## Quick Access
- **Live Demo**: https://switchboard.miski.studio/
- **Default Login**: 
  - Username: admin
  - Password: admin123

## Using the Platform

### Home Page Features
1. **Dashboard Overview**
   - Email Communications Stats
     - Total emails processed
     - Breakdown of internal (DC.gov) vs external communications
   - Media Communications Stats
     - Total media outlet emails
     - Top media outlet statistics
     - Active media outlets count

2. **Interactive Visualizations**
   - Entity Relationship Network: Shows connections between different entities
   - Email Domain Communication Flow: Heat map showing communication patterns
   - Email Domain Distribution: Bar chart of email domain frequencies
   - Hidden Debug Visualizations (Press Shift + D):
     - Topic UMAP Analysis
     - Topic t-SNE Analysis
     - Topic Similarity Network

### Search Interface
1. **Basic Search**
   - Enter search terms (minimum 3 characters)
   - Results show highlighted matches in context
   - Navigate through pages of results
   - Each result shows:
     - Document title
     - Relevant excerpts with highlighted matches
     - Relevance score

2. **Document Management**
   - Pin important documents for quick access
     - Click the pin icon to save documents
     - Pinned documents appear in a bar at the top
     - Click pinned documents to quickly access them
   - View full document content by clicking any result
   - Add annotations to documents
     - Use the notes field at the bottom of document view
     - Notes are automatically saved

3. **Search Tips**
   - Use specific terms for better results
   - Results are sorted by relevance
   - Hover over highlighted text to see context
   - Use the sidebar for quick navigation between features

### Navigation
- Use the sidebar to switch between dashboard and search
- Logout button located at the bottom of the dashboard


## Project Structure
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

1. Start services:
   ```bash
   make up
   ```

2. Access:
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

## License
Developed by Miski Studio / Atilio Barreda II



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


## AWS Deployment Guide

### Prerequisites
1. AWS Account with EC2 access
2. A domain name you can configure (for SSL)
3. SSH key pair for EC2 access

### Step 1: Launch EC2 Instance
1. Launch a t2.medium Ubuntu instance (Ubuntu 22.04 LTS)
2. Configure Security Group:
   - Allow SSH (Port 22) from your IP
   - Allow HTTP (Port 80) from anywhere
   - Allow HTTPS (Port 443) from anywhere

### Step 2: Configure Domain & SSL
1. Add an A record in your domain's DNS settings:
   ```
   Type: A
   Name: switchboard (or your subdomain)
   Value: Your-EC2-IP
   TTL: 3600 (or lowest available)
   ```

### Step 3: Local Setup
1. Clone this repository
2. Copy your EC2 key to `~/switchboard-final.pem`
3. Set correct permissions:
   ```bash
   chmod 400 ~/switchboard-final.pem
   ```
4. Update the Makefile EC2 configuration:
   ```makefile
   EC2_IP = your-ec2-ip
   EC2_USER = ubuntu
   EC2_KEY = ~/switchboard-final.pem
   ```

### Step 4: Initial Deployment
1. Install Docker on EC2:
   ```bash
   ssh -i ~/switchboard-final.pem ubuntu@your-ec2-ip
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   ```

2. Deploy the application:
   ```bash
   make ssl-setup  # Set up SSL certificate
   make deploy     # Deploy the application
   ```

### Step 5: Verify Deployment
1. Check deployment status:
   ```bash
   make domain-check
   ```
2. Visit your domain (e.g., https://switchboard.yourdomain.com)

### Maintenance Commands
- `make ssl-status`: Check SSL certificate status
- `make ssl-renew`: Renew SSL certificate
- `make deploy`: Redeploy application
- `make domain-check`: Verify domain and SSL setup

### Troubleshooting
If deployment fails:
1. Check container status:
   ```bash
   ssh -i ~/switchboard-final.pem ubuntu@your-ec2-ip "cd /home/ubuntu/switchboard/app && sudo docker-compose ps"
   ```
2. View container logs:
   ```bash
   ssh -i ~/switchboard-final.pem ubuntu@your-ec2-ip "cd /home/ubuntu/switchboard/app && sudo docker-compose logs"
   ```
3. Verify SSL certificate:
   ```bash
   make ssl-status
   ```

### Security Notes
- The deployment uses Let's Encrypt for SSL certificates
- Certificates auto-renew every 90 days
- Always keep your EC2 security group restricted to necessary ports
- Regularly update dependencies and system packages
