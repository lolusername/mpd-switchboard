# app/Makefile

# Variables
# Check if docker-compose exists, otherwise use 'docker compose'
DOCKER_COMPOSE := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")
INGEST_COMPOSE_FILE = docker-compose.ingest.yml
EC2_IP := $(shell aws ec2 describe-instances \
    --instance-ids i-02915630dfcbc43d0 \
    --query 'Reservations[*].Instances[*].PublicIpAddress' \
    --output text)
EC2_HOST = ubuntu@$(EC2_IP)
PEM_PATH = ~/switchboard-final.pem
PROJECT_NAME = switchboard

# Default target
.DEFAULT_GOAL := help

.PHONY: help ingest deploy snapshot list-snapshots init-snapshots

help:
	@echo "Available commands:"
	@echo "  ingest         - Run the PDF ingestion process"
	@echo "  deploy        - Deploy to EC2"
	@echo "  deploy-files  - Deploy only updated files to EC2"
	@echo "  rebuild       - Rebuild and restart all containers"
	@echo "  up            - Start containers"
	@echo "  down          - Stop containers"
	@echo "  help          - Show this help message"

ingest:
	$(DOCKER_COMPOSE) -f $(INGEST_COMPOSE_FILE) run --rm ingest

# Deployment commands
deploy: clean-ec2
	@echo "🚀 Starting full deployment..."
	@echo "🎁 Creating deployment package..."
	cd .. && zip -r $(PROJECT_NAME).zip app/ \
		--exclude "*/node_modules/*" \
		--exclude "*/.nuxt/*" \
		--exclude "*/.output/*" \
		--exclude "*/dist/*"
	
	@echo "📤 Uploading to EC2..."
	cd .. && scp -i $(PEM_PATH) $(PROJECT_NAME).zip $(EC2_HOST):~
	
	@echo "🔄 Deploying on EC2..."
	ssh -i $(PEM_PATH) $(EC2_HOST) '\
		sudo systemctl stop unattended-upgrades && \
		sudo killall apt-get dpkg 2>/dev/null || true && \
		sudo apt-get update && \
		sudo apt-get install -y unzip && \
		unzip -o ~/$(PROJECT_NAME).zip && \
		cd app && \
		sudo docker-compose down && \
		sudo docker system prune -af --volumes && \
		sudo docker-compose up -d --build'
	
	@echo "🧹 Cleaning up..."
	cd .. && rm $(PROJECT_NAME).zip
	
	@echo "✅ Deployment complete!"

deploy-files: clean-ec2
	@echo "📤 Uploading updated files to EC2 at $(EC2_HOST)..."
	rsync -avz --exclude 'node_modules' \
		--exclude '.nuxt' \
		--exclude '.output' \
		--exclude 'dist' \
		-e "ssh -i $(PEM_PATH)" \
		./ $(EC2_HOST):~/switchboard/app/
	
	@echo "🔄 Rebuilding on EC2..."
	ssh -i $(PEM_PATH) $(EC2_HOST) '\
		cd ~/switchboard/app && \
		sudo docker-compose down && \
		sudo docker system prune -af --volumes && \
		sudo docker-compose up -d --build --force-recreate frontend'
	
	@echo "✅ File deployment complete!"

# Rebuild and restart all containers
rebuild:
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d

# Start containers
up:
	$(DOCKER_COMPOSE) up -d

# Stop containers
down:
	$(DOCKER_COMPOSE) down

# View logs
logs:
	$(DOCKER_COMPOSE) logs -f

# Build without starting
build:
	$(DOCKER_COMPOSE) build

# Rebuild specific service
rebuild-service:
	$(DOCKER_COMPOSE) build $(service)
	$(DOCKER_COMPOSE) up -d $(service)

# Clean everything
clean:
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) system prune -f

clean-ec2:
	@echo "🧹 Cleaning up EC2 instance..."
	ssh -i $(PEM_PATH) $(EC2_HOST) '\
		cd ~/switchboard/app && \
		sudo docker-compose down && \
		sudo docker system prune -af && \
		sudo docker volume prune -f && \
		sudo docker builder prune -af && \
		sudo rm -rf /var/lib/docker/buildkit && \
		sudo systemctl restart docker'
	@echo "✅ EC2 cleanup complete!"

# Initialize Elasticsearch snapshot repository
init-snapshots:
	@echo "📁 Initializing snapshot repository..."
	@curl -X PUT "localhost:9200/_snapshot/switchboard_backup" \
		-H "Content-Type: application/json" \
		-d '{"type": "fs", "settings": {"location": "/usr/share/elasticsearch/snapshots"}}'

# Create Elasticsearch snapshot
snapshot: init-snapshots
	@echo "📸 Creating Elasticsearch snapshot..."
	@curl -X PUT "localhost:9200/_snapshot/switchboard_backup/snapshot_$(shell date +%Y%m%d_%H%M%S)?wait_for_completion=true" \
		-H "Content-Type: application/json" \
		-d '{"indices": "pdf_documents","ignore_unavailable": true,"include_global_state": false}'
	@echo "✅ Snapshot created in ./snapshots"

# List all snapshots
list-snapshots:
	@echo "📋 Listing available snapshots..."
	@curl -X GET "localhost:9200/_snapshot/switchboard_backup/_all"