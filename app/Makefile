# app/Makefile

# Variables
DOCKER_COMPOSE = docker-compose
INGEST_COMPOSE_FILE = docker-compose.ingest.yml

# Default target
.DEFAULT_GOAL := help

.PHONY: help ingest

help:
	@echo "Available commands:"
	@echo "  ingest  - Run the PDF ingestion process"
	@echo "  help    - Show this help message"

ingest:
	$(DOCKER_COMPOSE) -f $(INGEST_COMPOSE_FILE) run --rm ingest

# Rebuild and restart all containers
rebuild:
	docker-compose down
	docker-compose build
	docker-compose up -d

# Start containers
up:
	docker-compose up -d

# Stop containers
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Build without starting
build:
	docker-compose build

# Rebuild specific service
rebuild-service:
	docker-compose build $(service)
	docker-compose up -d $(service)

# Clean everything
clean:
	docker-compose down -v
	docker system prune -f