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

# Switchboard Setup Guide

## Local Development Setup

### Prerequisites
1. Install required software:
   ```bash
   # Install pyenv for Python version management
   brew install pyenv   # Mac
   # OR
   curl https://pyenv.run | bash   # Linux

   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Set up Python environment:
   ```bash
   pyenv install 3.12
   pyenv local 3.12
   poetry env use 3.12
   poetry install
   ```

3. Install Docker Desktop (Mac/Windows) or Docker Engine (Linux)

### Local Development
1. Clone repository:
   ```bash
   git clone https://github.com/d4bl/switchboard.git
   cd switchboard/app
   ```

2. Start services:
   ```bash
   make up
   ```

3. Access:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/docs
   - Elasticsearch: http://localhost:9200

   

## AWS Deployment Setup

### 1. EC2 Instance Setup
1. Launch EC2 instance:
   - Ubuntu Server 22.04 LTS
   - t2.large minimum (4GB RAM, 2 vCPU)
   - 30GB SSD storage

2. Security Group settings:
   - Allow SSH (22) from your IP
   - Allow HTTP (80) from anywhere
   - Allow Custom TCP:
     - 3000 (Frontend)
     - 8000 (API)
     - 9200 (Elasticsearch)

3. Create and download key pair (e.g., switchboard-final.pem)
   ```bash
   chmod 400 ~/switchboard-final.pem
   ```

### 2. AWS CLI Setup
1. Install AWS CLI:
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. Configure AWS:
   ```bash
   aws configure
   # Enter your:
   # - AWS Access Key ID
   # - AWS Secret Access Key
   # - Default region (e.g., us-east-1)
   ```

### 3. EC2 Instance Configuration
1. Update instance ID in Makefile:

makefile:app/Makefile
startLine: 6
endLine: 11


2. Update PEM path in Makefile to match your key location

### 4. Initial Deployment
1. First-time setup on EC2:
   ```bash
   # SSH into instance
   ssh -i ~/switchboard-final.pem ubuntu@YOUR_EC2_IP
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. Deploy from your local machine:
   ```bash
   make deploy
   ```

### 5. Maintenance & Updates
- Update deployment: `make deploy-files`
- View logs: `ssh -i ~/switchboard-final.pem ubuntu@YOUR_EC2_IP 'cd ~/switchboard/app && sudo docker-compose logs -f'`
- Clean EC2: `make clean-ec2`

## Data Management

### Elasticsearch Snapshots
1. Initialize repository:
   ```bash
   make init-snapshots
   ```

2. Create snapshot:
   ```bash
   make snapshot
   ```

### Document Processing
1. Place PDF files in `data/` directory
2. Run ingestion:
   ```bash
   make ingest
   ```

## Troubleshooting

### Common Issues
1. Elasticsearch fails to start:
   ```bash
   # On Linux host
   sudo sysctl -w vm.max_map_count=262144
   ```

2. Permission issues:
   ```bash
   sudo chown -R 1000:1000 data/
   ```

3. Port conflicts:
   ```bash
   # Check ports
   sudo lsof -i :3000
   sudo lsof -i :8000
   sudo lsof -i :9200
   ```

### Logs
- All services: `make logs`
- Specific service: `docker-compose logs -f api`

## Security Notes
- Update security group rules to restrict access
- Enable Elasticsearch security in production
- Use HTTPS in production
- Regularly update dependencies