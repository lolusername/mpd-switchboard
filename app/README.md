# Switchboard

A document processing and search platform that makes your PDFs searchable and analyzable.

## What It Does
- Processes PDF documents (including scanned ones)
- Makes text searchable and analyzable 
- Provides a web interface to search and explore documents
- Runs on Docker for easy deployment

## Tech Stack
- Python 3.12 (backend)
- FastAPI (API)
- Elasticsearch 8.12.2 (search)
- Nuxt.js (frontend)
- Docker & Docker Compose

## Quick Start

1. Prerequisites:
   - Python 3.12
   - Node.js 20+
   - Docker 20+
   - Poetry

2. Clone and setup:
   git clone https://github.com/yourusername/switchboard.git
   cd switchboard/app
   poetry install
   cd frontend && npm install

3. Start services:
   # Start everything
   make up

   # Or individual services
   make rebuild-service service=api
   make rebuild-service service=frontend

4. Access:
   - Web UI: http://localhost:3000 
   - API Docs: http://localhost:8000/docs
   - Elasticsearch: http://localhost:9200

## Development

Project Structure:
app/
├── api/                 # FastAPI backend
├── frontend/           # Nuxt.js frontend
├── elasticsearch-init/ # Search setup
├── docker-compose.yml  # Container config
└── Makefile           # Build commands

Common Commands:
- make logs            # View logs
- make rebuild        # Rebuild everything
- make clean          # Clean up
- make deploy-files   # Deploy to EC2

Making Changes:
- Backend: Edit files in api/, changes auto-reload
- Frontend: Edit files in frontend/, changes hot-reload
- Search: Edit elasticsearch-init/, then rebuild that service

## Document Processing

1. Upload PDFs to /data directory
2. System automatically:
   - Extracts text (using pdfminer.six)
   - Runs OCR if needed (using Tesseract)
   - Indexes in Elasticsearch
   - Makes searchable via API/UI

## Deployment

1. Configure AWS:
   - Update EC2 host in environment
   - Ensure security groups allow ports 3000, 8000, 9200

2. Deploy:
   make deploy-files

## Configuration
- Environment: .env file
- Elasticsearch: docker-compose.yml
- API: api/config.py
- Frontend: frontend/.env

## Troubleshooting

Common issues:
- Port conflicts: Check if 3000, 8000, or 9200 are in use
- Memory errors: Increase Docker memory limit
- Elasticsearch fails: Check vm.max_map_count setting, check if index exists

## Security
- API uses CORS protection
- Elasticsearch security enabled
- Regular dependency updates
- Secure deployment practices