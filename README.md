# Switchboard: Email Document Analysis Platform

A specialized platform for analyzing large collections of email documents, built for Data for Black Lives (D4BL). Switchboard makes email archives searchable and analyzable through advanced text processing and a modern web interface.

## Quick Access
- **Production Site**: https://switchboard.miski.studio/
- **Local Development**: http://localhost

## Core Features

### 1. Document Processing & Ingestion
- **Email PDF Processing**
  - Handles large collections of email PDFs
  - Automatic OCR for scanned documents
  - Extracts text content while preserving email structure
  - Processes metadata (From, To, Subject, Date)
  - Supports batch ingestion via S3 or local files

- **OCR Capabilities**
  - Automatic detection of scanned PDFs
  - OCR processing using Tesseract
  - Handles both text and scanned PDFs in the same collection
  - Preserves document structure during OCR
  - Pre-processes images for better OCR accuracy

### 2. Search & Analysis
- **Semantic Search**
  - Full-text search across all documents
  - Relevance-based result ranking
  - Highlighted text matches in context
  - Real-time search as you type

- **Document Management**
  - Pin important documents for quick access
  - Add annotations to documents
  - Track document relevance scores
  - View full document content with formatted email headers

### 3. User Interface
- **Modern Web Interface**
  - Clean, intuitive search interface
  - Document preview with highlights
  - Pinned documents bar for quick access
  - Annotation system for notes and comments

## Technical Architecture

### Components
1. **Backend (Python/FastAPI)**
   - FastAPI for API endpoints
   - Elasticsearch client for search
   - JWT-based authentication
   - Environment-based configuration
   - OCR processing pipeline

2. **Search Engine**
   - Elasticsearch OSS 7.10.2
   - Custom mapping for email documents
   - Optimized for text search
   - Configurable relevance scoring

3. **Frontend (Nuxt 3/Vue.js)**
   - Modern reactive interface
   - Real-time search updates
   - Document state management
   - Mobile-responsive design

4. **Infrastructure**
   - Docker containerization
   - Nginx reverse proxy
   - Let's Encrypt SSL (production)
   - AWS EC2 hosting

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Make
- At least 4GB RAM (8GB recommended for OCR processing)
- Sufficient disk space for document storage

### System Dependencies
All dependencies are handled by Docker, including:
- Tesseract OCR engine
- PDF processing libraries
- Python OCR dependencies
- Image processing tools

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/d4bl/switchboard.git
   cd switchboard/app
   ```

2. Start development environment:
   ```bash
   make rebuild
   ```

3. Access the application:
   - Web Interface: http://localhost
   - API: http://localhost/api
   - API Docs: http://localhost/api/docs

### Production Deployment
1. Configure AWS and domain:
   - Point domain to EC2 instance
   - Configure SSL certificates
   - Set up security groups

2. Deploy:
   ```bash
   make deploy
   ```

3. Verify deployment:
   ```bash
   make check-deployment
   ```

## Document Processing Pipeline

### 1. Data Preparation
- Place email PDFs in data directory
- Organize by collection if needed
- Ensure consistent file naming
- No need to separate scanned and digital PDFs

### 2. Document Processing
- **Text Extraction**
  - Automatic detection of PDF type (scanned vs digital)
  - Direct text extraction for digital PDFs
  - OCR processing for scanned documents
  - Preservation of email structure and formatting

- **OCR Pipeline**
  - Image preprocessing for better quality
  - Tesseract OCR for text extraction
  - Post-processing to maintain email format
  - Quality checks on OCR output

### 3. Ingestion Process
- **Local Ingestion**
  ```bash
  make ingest
  ```
- **S3 Ingestion**
  - Configure AWS credentials
  - Set S3 bucket in configuration
  - Run ingestion command

### 4. Search Index Creation
- Automatic index creation
- Custom mappings for email fields
- Optimized for search performance
- Full-text indexing of OCR'd content

## Configuration

### Development
- `docker-compose.yml` - Development setup
- `nginx/development.conf` - Development server
- `.env.development` - Development variables

### Production
- `docker-compose.production.yml` - Production setup
- `nginx/production.conf` - Production server with SSL
- `.env.production` - Production variables

## Common Tasks

### Managing Documents
1. **Adding New Documents**
   - Add PDFs to data directory
   - Run ingestion process
   - Verify in search interface

2. **Updating Existing Documents**
   - Replace PDFs in data directory
   - Re-run ingestion for updates
   - Check index statistics

### System Maintenance
1. **Checking System Status**
   ```bash
   make check-deployment  # Production
   make check-rebuild    # Development
   ```

2. **Viewing Logs**
   ```bash
   make logs
   ```

3. **Restarting Services**
   ```bash
   make rebuild  # Development
   make deploy   # Production
   ```

## Troubleshooting

### Common Issues
1. **Search Not Working**
   - Check Elasticsearch status
   - Verify index exists
   - Check API connectivity

2. **OCR Issues**
   - Verify Tesseract installation in container
   - Check PDF quality and resolution
   - Monitor OCR processing logs
   - Try reprocessing problematic documents
   - Check container memory limits

3. **Deployment Issues**
   - Verify AWS credentials
   - Check SSL certificates
   - Review nginx logs

4. **Performance Issues**
   - Monitor Elasticsearch memory
   - Check system resources
   - Review request logs
   - Adjust OCR batch size if needed

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test locally with `make rebuild`
5. Submit a pull request

## License
Copyright © 2024 Data for Black Lives

## Acknowledgments
Built by Miski Studio for Data for Black Lives