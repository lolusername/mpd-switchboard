# app/Makefile

# Variables
DOCKER_COMPOSE = docker-compose
INGEST_COMPOSE_FILE = docker-compose.ingest.yml
EC2_IP := $(shell aws ec2 describe-instances \
    --instance-ids i-02915630dfcbc43d0 \
    --query 'Reservations[*].Instances[*].PublicIpAddress' \
    --output text)
EC2_HOST = ubuntu@$(EC2_IP)
PEM_PATH = ~/switchboard-final.pem
PROJECT_NAME = switchboard
ELASTIC_IP ?= $(shell aws ec2 describe-addresses --query 'Addresses[0].PublicIp' --output text)
export ELASTIC_IP  # Export for docker-compose
INSTANCE_ID = i-02915630dfcbc43d0
AWS = aws
MAX_WAIT_SECONDS = 30  # 5 minutes timeout
SLEEP_INTERVAL = 10     # Check every 10 seconds

# Default target
.DEFAULT_GOAL := help

.PHONY: help ingest deploy snapshot list-snapshots init-snapshots sync-snapshot

help:
	@echo "Available commands:"
	@echo "  ingest         - Run the PDF ingestion process"
	@echo "  deploy        - Deploy to EC2"
	@echo "  deploy-files  - Deploy only updated files to EC2"
	@echo "  help          - Show this help message"

ingest:
	$(DOCKER_COMPOSE) -f $(INGEST_COMPOSE_FILE) run --rm ingest

# Deployment commands
deploy: ensure-security-group
	@echo "🚀 Starting deployment..."
	@echo "🔍 Checking instance status..."
	@aws ec2 describe-instance-status \
		--instance-ids $(INSTANCE_ID) \
		--include-all-instances \
		--query 'InstanceStatuses[0].InstanceState.Name' \
		--output text | grep -q "running" || \
		(echo "⚠️ EC2 instance not running. Starting instance..." && \
		$(MAKE) restart-instance)

	@echo "⏳ Waiting for SSH to be available..."
	@for i in $$(seq 1 30); do \
		if ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no -i $(PEM_PATH) $(EC2_HOST) 'exit' 2>/dev/null; then \
			echo "✅ SSH connection established"; \
			break; \
		fi; \
		if [ $$i -eq 15 ]; then \
			echo "⚠️ SSH failing, trying security group refresh..."; \
			aws ec2 revoke-security-group-ingress \
				--group-id sg-0a3e50fdb3ac8927a \
				--protocol tcp \
				--port 22 \
				--cidr $$(curl -s ifconfig.me)/32 || true; \
			aws ec2 authorize-security-group-ingress \
				--group-id sg-0a3e50fdb3ac8927a \
				--protocol tcp \
				--port 22 \
				--cidr $$(curl -s ifconfig.me)/32; \
		fi; \
		echo "Attempting to connect ($$i/30)..."; \
		sleep 10; \
		if [ $$i -eq 30 ]; then \
			echo "⚠️ SSH connection failed. Restarting instance..."; \
			$(MAKE) restart-instance; \
			sleep 30; \
		fi; \
	done

	@echo "🎁 Creating deployment package..."
	cd .. && zip -r $(PROJECT_NAME).zip app/ \
		--exclude "*/node_modules/*" \
		--exclude "*/.nuxt/*" \
		--exclude "*/.output/*" \
		--exclude "*/dist/*"
	
	@echo "📤 Uploading to EC2..."
	cd .. && scp -i $(PEM_PATH) $(PROJECT_NAME).zip $(EC2_HOST):~
	
	@echo "🔄 Extracting and setting up..."
	ssh -i $(PEM_PATH) $(EC2_HOST) '\
		unzip -o ~/$(PROJECT_NAME).zip && \
		cd ~/switchboard/app && \
		sudo systemctl restart docker && \
		sleep 5 && \
		sudo docker-compose down && \
		sudo docker system prune -af --volumes && \
		sudo docker-compose up -d --build'
	
	@echo "🧹 Cleaning up..."
	cd .. && rm $(PROJECT_NAME).zip

deploy-files: clean-ec2
	@echo "📤 Uploading updated files to EC2 at $(EC2_HOST)..."
	# Copy .env file with correct IP
	echo "ELASTIC_IP=$(ELASTIC_IP)" > .env
	rsync -avz --exclude 'node_modules' \
		--exclude '.nuxt' \
		--exclude '.output' \
		--exclude 'dist' \
		-e "ssh -i $(PEM_PATH)" \
		./ $(EC2_HOST):~/switchboard/app/
	
	@echo "🔄 Setting up Docker and rebuilding..."
	$(MAKE) setup-docker
	
	@echo "✅ Deployment complete!"

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

clean-ec2:
	@echo "🧹 Cleaning up EC2 instance..."
	ssh -i $(PEM_PATH) $(EC2_HOST) '\
		cd ~/switchboard/app && \
		sudo docker-compose down && \
		sudo docker system prune -af --volumes && \
		sudo docker volume prune -f && \
		sudo docker builder prune -af && \
		sudo rm -rf /var/lib/docker/overlay2/* && \
		sudo rm -rf /var/lib/docker/buildkit && \
		sudo systemctl restart docker && \
		sudo rm -rf ~/switchboard/app/frontend/node_modules && \
		sudo rm -rf ~/switchboard/app/frontend/.nuxt && \
		sudo rm -rf ~/switchboard/app/frontend/.output'
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

# Add this new command
restart-instance:
	@echo "🛑 Stopping EC2 instance $(INSTANCE_ID)..."
	$(AWS) ec2 stop-instances --instance-ids $(INSTANCE_ID)
	
	@echo "⏳ Waiting for instance to stop (timeout: $(MAX_WAIT_SECONDS)s)..."
	@for i in $$(seq 1 $$(($(MAX_WAIT_SECONDS)/$(SLEEP_INTERVAL)))); do \
		STATUS=$$($(AWS) ec2 describe-instances \
			--instance-ids $(INSTANCE_ID) \
			--query 'Reservations[].Instances[].State.Name' \
			--output text); \
		echo "Current status: $$STATUS"; \
		if [ "$$STATUS" = "stopped" ]; then \
			break; \
		elif [ $$i -eq $$(($(MAX_WAIT_SECONDS)/$(SLEEP_INTERVAL))) ]; then \
			echo "⚠️  Timeout reached. Forcing stop..."; \
			$(AWS) ec2 stop-instances --instance-ids $(INSTANCE_ID) --force; \
			sleep 30; \
		fi; \
		sleep $(SLEEP_INTERVAL); \
	done
	
	@echo "🟢 Starting EC2 instance..."
	$(AWS) ec2 start-instances --instance-ids $(INSTANCE_ID)
	
	@echo "⏳ Waiting for instance to start..."
	$(AWS) ec2 wait instance-running --instance-ids $(INSTANCE_ID)
	
	@echo "🔍 Checking instance status..."
	@$(AWS) ec2 describe-instance-status \
		--instance-ids $(INSTANCE_ID) \
		--include-all-instances
	
	@echo "📝 Fetching system logs..."
	@$(AWS) ec2 get-console-output \
		--instance-id $(INSTANCE_ID)
	
	@echo "🌐 New IP address:"
	@$(AWS) ec2 describe-instances \
		--instance-ids $(INSTANCE_ID) \
		--query 'Reservations[].Instances[].PublicIpAddress' \
		--output text

# Add this new command
setup-docker:
	@echo "🔧 Setting up Docker permissions..."
	ssh -i $(PEM_PATH) $(EC2_HOST) '\
		sudo usermod -aG docker ubuntu && \
		newgrp docker && \
		cd ~/switchboard/app && \
		docker-compose down && \
		docker system prune -af --volumes && \
		docker-compose up -d'
	
	@echo "⏳ Waiting for services to start..."
	sleep 10
	
	@echo "🔍 Checking container status..."
	ssh -i $(PEM_PATH) $(EC2_HOST) 'docker ps'
	
	@echo "✅ Docker setup complete!"

# Add this new command after the list-snapshots command
sync-snapshot:
	@echo "🔍 Checking EC2 instance status..."
	@aws ec2 describe-instance-status \
		--instance-ids $(INSTANCE_ID) \
		--include-all-instances \
		--query 'InstanceStatuses[0].InstanceState.Name' \
		--output text | grep -q "running" || \
		(echo "⚠️ EC2 instance not running. Starting instance..." && \
		$(MAKE) restart-instance)

	@echo "🔄 Restarting Docker service on EC2..."
	ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no -i $(PEM_PATH) $(EC2_HOST) '\
		sudo systemctl restart docker && \
		sleep 5 && \
		sudo systemctl status docker'

	$(eval SNAPSHOT_NAME := snapshot_$(shell date +%Y%m%d_%H%M%S))
	@echo "🧹 Creating local snapshot $(SNAPSHOT_NAME)..."
	mkdir -p ./snapshots
	@curl -X PUT "localhost:9200/_snapshot/switchboard_backup" \
		-H "Content-Type: application/json" \
		-d '{"type": "fs", "settings": {"location": "/usr/share/elasticsearch/snapshots"}}'
	
	@curl -X PUT "localhost:9200/_snapshot/switchboard_backup/$(SNAPSHOT_NAME)?wait_for_completion=true" \
		-H "Content-Type: application/json" \
		-d '{"indices": "pdf_documents","ignore_unavailable": true,"include_global_state": false}'
	
	@echo "📤 Preparing EC2 for snapshot transfer..."
	ssh -o ConnectTimeout=10 -i $(PEM_PATH) $(EC2_HOST) 'cd ~/switchboard/app && rm -rf snapshots/* && mkdir -p snapshots && chmod 777 snapshots'
	
	@echo "📤 Copying snapshots to EC2..."
	rsync -avz --delete --progress -e "ssh -i $(PEM_PATH)" ./snapshots/ $(EC2_HOST):~/switchboard/app/snapshots/
	
	@echo "🔄 Syncing snapshots..."
	rsync -avz --delete --chmod=Du=rwx,Dg=rx,Do=rx,Fu=rw,Fg=r,Fo=r \
		-e "ssh -i $(PEM_PATH)" \
		./snapshots/ $(EC2_HOST):~/switchboard/app/snapshots/
	
	@echo "🔄 Registering and restoring snapshot on EC2..."
	ssh -i $(PEM_PATH) $(EC2_HOST) '\
		cd ~/switchboard/app && \
		docker-compose down && \
		sudo chown -R 1000:1000 snapshots/ && \
		sudo chmod -R 777 snapshots/ && \
		docker-compose up -d elasticsearch && \
		echo "Waiting for Elasticsearch to start..." && \
		sleep 60 && \
		while ! curl -s "localhost:9200/_cluster/health" | grep -q "green\|yellow"; do \
			echo "Waiting for Elasticsearch health check..." && \
			sleep 10; \
		done && \
		echo "Registering repository..." && \
		curl -X PUT "localhost:9200/_snapshot/switchboard_backup" \
			-H "Content-Type: application/json" \
			-d '"'"'{"type": "fs", "settings": {"location": "/usr/share/elasticsearch/snapshots"}}'"'"' && \
		sleep 10 && \
		echo "Verifying snapshot files..." && \
		ls -la snapshots/ && \
		echo "Listing snapshots in repository..." && \
		curl -s "localhost:9200/_snapshot/switchboard_backup/_all" && \
		echo "\nRestoring latest snapshot..." && \
		LATEST_SNAPSHOT=$(ls -t snapshots/indices | head -n1) && \
		echo "Using snapshot: $LATEST_SNAPSHOT" && \
		curl -X POST "localhost:9200/_snapshot/switchboard_backup/$LATEST_SNAPSHOT/_restore?wait_for_completion=true" \
			-H "Content-Type: application/json" \
			-d '"'"'{"indices": "pdf_documents","include_global_state": false,"include_aliases": true}'"'"' && \
		docker-compose up -d'
	
	@echo "✅ Snapshot sync complete!"

ensure-security-group:
	@echo "🔒 Ensuring security group is configured..."
	@aws ec2 describe-security-groups \
		--group-ids sg-0a3e50fdb3ac8927a \
		--query 'SecurityGroups[0].IpPermissions[?FromPort==`22`]' \
		--output text || \
	aws ec2 authorize-security-group-ingress \
		--group-id sg-0a3e50fdb3ac8927a \
		--protocol tcp \
		--port 22 \
		--cidr $$(curl -s ifconfig.me)/32
