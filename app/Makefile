# app/Makefile

# Variables
# Check if docker-compose exists, otherwise use 'docker compose'
DOCKER_COMPOSE := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")
INGEST_COMPOSE_FILE = docker-compose.ingest.yml
EC2_IP := $(shell aws ec2 describe-instances \
    --instance-ids i-09769d9810bdeae42 \
    --query 'Reservations[*].Instances[*].PublicIpAddress' \
    --output text)
EC2_HOST = ubuntu@$(EC2_IP)
PEM_PATH := ~/switchboard-final.pem
PROJECT_NAME = switchboard

# Default target
.DEFAULT_GOAL := help

.PHONY: help ingest deploy snapshot list-snapshots init-snapshots setup-ec2 clean-ec2 check-deployment deep-clean-ec2 check-es check-api check-frontend check-all check-security-group check-network-acls list-instances check-elastic-ips check-services restart-ssh check-ports reboot-instance force-restart-instance terminate-unused release-elastic-ip check-costs check-cleanup start-switchboard allocate-ip check-status check-ip check-instance check-account create-instance recover-instance debug-ssh

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

# EC2 connection details
EC2_USER := ubuntu
EC2_KEY := $(PEM_PATH)
APP_DIR := /home/ubuntu/switchboard

# Setup EC2 instance
setup-ec2:
	@echo "🚀 Setting up EC2 instance..."
	ssh -i $(PEM_PATH) $(EC2_USER)@$(EC2_IP) '\
		sudo apt-get update && \
		sudo apt-get install -y docker.io docker-compose git && \
		sudo systemctl start docker && \
		sudo systemctl enable docker && \
		sudo usermod -aG docker $$USER && \
		mkdir -p $(APP_DIR)/app'

# Clean EC2 instance
clean-ec2:
	@echo "🧹 Performing deep cleanup of EC2 instance..."
	ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_HOST) '\
		echo "Stopping all containers..." && \
		sudo docker-compose down || true && \
		echo "Removing all containers..." && \
		sudo docker rm -f $$(sudo docker ps -aq) || true && \
		echo "Removing all images..." && \
		sudo docker rmi -f $$(sudo docker images -q) || true && \
		echo "Pruning system..." && \
		sudo docker system prune -af --volumes && \
		echo "Cleaning up Docker build cache..." && \
		sudo docker builder prune -af && \
		echo "Removing Docker data directory..." && \
		sudo systemctl stop docker && \
		sudo rm -rf /var/lib/docker/* && \
		sudo rm -rf /var/lib/docker/buildkit && \
		echo "Cleaning up system packages..." && \
		sudo apt-get clean && \
		sudo apt-get autoremove -y && \
		echo "Restarting Docker..." && \
		sudo systemctl start docker && \
		echo "Cleanup complete!"'

# Add this new command after clean-ec2
deep-clean-ec2:
	@echo "🧹 Performing DEEP cleanup of EC2 instance..."
	ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_HOST) '\
		echo "Stopping all services..." && \
		sudo docker-compose down || true && \
		sudo systemctl stop docker && \
		echo "Removing all Docker resources..." && \
		sudo docker system prune -af --volumes && \
		sudo docker builder prune -af && \
		echo "Cleaning up file system..." && \
		sudo rm -rf /var/lib/docker/* && \
		sudo rm -rf $(APP_DIR)/* && \
		sudo rm -rf /tmp/* && \
		sudo rm -rf /var/tmp/* && \
		sudo rm -rf /var/log/*.gz && \
		sudo rm -rf /var/log/*.[0-9] && \
		sudo rm -rf /var/log/*.[0-9].gz && \
		echo "Cleaning package cache..." && \
		sudo apt-get clean && \
		sudo apt-get autoremove -y && \
		sudo journalctl --vacuum-time=1d && \
		echo "Restarting services..." && \
		sudo systemctl start docker && \
		echo "Creating fresh app directory..." && \
		mkdir -p $(APP_DIR)/app && \
		echo "Deep cleanup complete!"'

# Deploy to EC2
deploy:
	@if [ -z "$(EC2_IP)" ]; then \
		echo "❌ Error: EC2_IP is empty. Instance might be stopped."; \
		echo "Try running: make force-restart-instance"; \
		exit 1; \
	fi
	@echo "🧹 Cleaning up EC2 instance..."
	ssh -i $(EC2_KEY) ubuntu@$(EC2_IP) "sudo systemctl restart docker && sudo docker system prune -af"
	@echo "✅ Cleanup complete"
	@echo "🔑 Testing SSH connection..."
	ssh -i $(EC2_KEY) ubuntu@$(EC2_IP) "echo '✅ SSH connection successful!'"
	@echo "📦 Deploying application..."
	# First, ensure .env exists or copy from .env.production
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.production..."; \
		cp .env.production .env; \
	fi
	# Deploy the application files
	rsync -avz --timeout=60 --progress -e "ssh -i $(EC2_KEY)" \
		--exclude 'node_modules' \
		--exclude '.git' \
		--exclude 'data' \
		--exclude 'snapshots' \
		--exclude '*.pyc' \
		--exclude '__pycache__' \
		./ ubuntu@$(EC2_IP):/home/ubuntu/switchboard/app/
	@echo "🚀 Starting services..."
	ssh -i $(EC2_KEY) ubuntu@$(EC2_IP) "cd /home/ubuntu/switchboard/app && \
		if [ ! -f .env ]; then cp .env.production .env; fi && \
		sudo docker-compose down && \
		sudo docker-compose up -d --build --force-recreate"
	@echo "✨ Deployment complete! Application is running at http://$(EC2_IP)"

# Update reboot command with SSH service check
reboot-instance:
	@echo "🔄 Rebooting EC2 instance..."
	@aws ec2 reboot-instances --instance-ids i-09769d9810bdeae42
	@echo "⏳ Waiting for instance to reboot (this will take a minute)..."
	@sleep 90
	@echo "🔍 Checking instance status..."
	@aws ec2 describe-instance-status \
		--instance-ids i-09769d9810bdeae42 \
		--query 'InstanceStatuses[0].InstanceStatus.Status' \
		--output text
	@echo "🔄 Attempting to restart SSH service..."
	@aws ec2 send-command \
		--instance-ids i-09769d9810bdeae42 \
		--document-name "AWS-RunShellScript" \
		--parameters commands=['sudo systemctl restart ssh'] \
		--output text || echo "⚠️  Could not restart SSH service via SSM"
	@echo "✅ Instance should be back online. Try SSH again."

# Add this command to force stop/start the instance with AZ flexibility
force-restart-instance:
	@echo "🛑 Stopping EC2 instance..."
	@aws ec2 stop-instances --instance-ids i-09769d9810bdeae42
	@echo "⏳ Waiting for instance to stop..."
	@aws ec2 wait instance-stopped --instance-ids i-09769d9810bdeae42
	@echo "🚀 Starting instance..."
	@aws ec2 start-instances --instance-ids i-09769d9810bdeae42
	@echo "⏳ Waiting for instance to start (this may take a few minutes)..."
	@aws ec2 wait instance-running --instance-ids i-09769d9810bdeae42 || \
		(echo "❌ Failed to start instance. Attempting recovery..." && \
		aws ec2 start-instances --instance-ids i-09769d9810bdeae42 && \
		aws ec2 wait instance-running --instance-ids i-09769d9810bdeae42)
	@echo "⏳ Giving services time to start..."
	@sleep 60
	@echo "✅ Instance restarted. New IP address:"
	@aws ec2 describe-instances \
		--instance-ids i-09769d9810bdeae42 \
		--query 'Reservations[*].Instances[*].PublicIpAddress' \
		--output text

# Add a simple SSH test command
test-ssh:
	@echo "Testing SSH connection with verbose output..."
	ssh -v -i $(PEM_PATH) -o ConnectTimeout=10 -o StrictHostKeyChecking=no $(EC2_USER)@$(EC2_IP) "echo 'SSH connection successful!'"

# Local development commands
rebuild:
	@echo "🔧 Setting up system requirements..."
	@if [ "$(shell uname)" = "Darwin" ]; then \
		docker run -it --rm --privileged --pid=host debian nsenter -t 1 -m -u -n -i sh -c "sysctl -w vm.max_map_count=262144" || true; \
	else \
		sudo sysctl -w vm.max_map_count=262144 || true; \
	fi
	@echo "🔄 Rebuilding containers..."
	$(DOCKER_COMPOSE) down || true
	$(DOCKER_COMPOSE) rm -f || true
	$(DOCKER_COMPOSE) build --no-cache
	@echo "🚀 Starting services..."
	$(DOCKER_COMPOSE) up -d --force-recreate --no-deps --remove-orphans

# Add this command to check logs
check-rebuild:
	@echo "Checking container logs..."
	@echo "\nElasticsearch logs:"
	$(DOCKER_COMPOSE) logs elasticsearch
	@echo "\nAPI logs:"
	$(DOCKER_COMPOSE) logs api
	@echo "\nFrontend logs:"
	$(DOCKER_COMPOSE) logs frontend

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

# Add this to your Makefile
check-deployment:
	@echo "Checking deployment status..."
	@echo "\nContainer Status:"
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "sudo docker ps"
	@echo "\nFrontend Logs:"
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "sudo docker logs switchboard_frontend --tail 20"
	@echo "\nAPI Logs:"
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "sudo docker logs switchboard_api --tail 20"
	@echo "\nPublic IP:"
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "curl -s http://169.254.169.254/latest/meta-data/public-ipv4"
	@echo "\nListening Ports:"
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "sudo netstat -tulpn | grep LISTEN"

# Add these debug commands
check-es:
	@echo "Elasticsearch Logs:"
	$(DOCKER_COMPOSE) logs elasticsearch

check-api:
	@echo "API Logs:"
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "sudo docker logs switchboard_api"

check-frontend:
	@echo "Frontend Logs:"
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "sudo docker logs switchboard_frontend"

check-all:
	@echo "Container Status:"
	@ssh -i $(EC2_KEY) $(EC2_USER)@$(EC2_IP) "sudo docker ps -a"
	@make check-es
	@make check-api
	@make check-frontend

# Add this command to check EC2 status
check-ec2:
	@echo "Checking EC2 instance status..."
	@aws ec2 describe-instances \
		--instance-ids i-09769d9810bdeae42 \
		--query 'Reservations[*].Instances[*].{State:State.Name,IP:PublicIpAddress,AZ:Placement.AvailabilityZone}' \
		--output table || echo "⚠️  Error: Instance not found or AWS CLI not configured properly"

# Add this command to check security group rules
check-security-group:
	@echo "Checking security group rules..."
	@aws ec2 describe-security-groups \
		--group-ids $(shell aws ec2 describe-instances \
			--instance-ids i-09769d9810bdeae42 \
			--query 'Reservations[*].Instances[*].SecurityGroups[*].GroupId' \
			--output text) \
		--query 'SecurityGroups[*].IpPermissions[?ToPort==`22`]'

# Add this command to check network ACLs
check-network-acls:
	@echo "Checking Network ACLs..."
	@aws ec2 describe-network-acls \
		--filters Name=vpc-id,Values=$(shell aws ec2 describe-instances \
			--instance-ids i-09769d9810bdeae42 \
			--query 'Reservations[*].Instances[*].VpcId' \
			--output text)

# Add this command to list all EC2 instances
list-instances:
	@echo "Listing all EC2 instances..."
	@aws ec2 describe-instances \
		--query 'Reservations[*].Instances[*].{ID:InstanceId,Name:Tags[?Key==`Name`].Value|[0],State:State.Name,IP:PublicIpAddress,Type:InstanceType,LaunchTime:LaunchTime}' \
		--output table

# Add this command to check Elastic IP associations
check-elastic-ips:
	@echo "Checking Elastic IP associations..."
	@aws ec2 describe-addresses \
		--query 'Addresses[*].{PublicIP:PublicIp,InstanceId:InstanceId,AllocationId:AllocationId}' \
		--output table

# Add this command to check running services
check-services:
	@echo "🔍 Checking running services on EC2..."
	@aws ssm send-command \
		--instance-ids i-09769d9810bdeae42 \
		--document-name "AWS-RunShellScript" \
		--parameters commands=['sudo systemctl list-units --type=service --state=running'] \
		--output text

# Add these commands to help with SSH issues
check-status:
	@echo "🔍 Checking switchboard status..."
	@echo "\nInstance Info:"
	@aws ec2 describe-instances \
		--instance-ids i-09769d9810bdeae42 \
		--query 'Reservations[*].Instances[*].{State:State.Name,IP:PublicIpAddress,AZ:Placement.AvailabilityZone}' \
		--output table || echo "⚠️  Error: Instance not found or AWS CLI not configured properly"

# Add this command to restart SSH
restart-ssh:
	@echo "🔄 Restarting SSH service on EC2..."
	@aws ssm send-command \
		--instance-ids i-09769d9810bdeae42 \
		--document-name "AWS-RunShellScript" \
		--parameters commands=['sudo systemctl restart ssh'] \
		--output text || echo "⚠️  Could not restart SSH service via SSM"

# Add this command to check ports
check-ports:
	@echo "👀 Checking listening ports on EC2..."
	@aws ssm send-command \
		--instance-ids i-09769d9810bdeae42 \
		--document-name "AWS-RunShellScript" \
		--parameters commands=['sudo netstat -tulpn | grep LISTEN'] \
		--output text

# Add these verification commands
check-cleanup:
	@echo "🔍 Checking cleanup status..."
	@echo "\n1. Instance Status:"
	@aws ec2 describe-instances \
		--query 'Reservations[*].Instances[*].{ID:InstanceId,Name:Tags[?Key==`Name`].Value|[0],State:State.Name}' \
		--output table
	@echo "\n2. Elastic IPs:"
	@aws ec2 describe-addresses \
		--query 'Addresses[*].{IP:PublicIp,Instance:InstanceId}' \
		--output table
	@echo "\n3. Cost-incurring Resources:"
	@aws ec2 describe-instances \
		--query 'Reservations[*].Instances[*].{ID:InstanceId,State:State.Name}' \
		--filters "Name=instance-state-name,Values=running,shutting-down,stopping,pending" \
		--output table || echo "✅ No running instances"

# Add these resource management commands
terminate-unused:
	@echo "🗑️ Terminating unused instance..."
	@aws ec2 terminate-instances --instance-ids i-0529228a96a6617ec
	@echo "✅ Unused instance termination initiated"

release-elastic-ip:
	@echo "🔄 Releasing Elastic IP..."
	@aws ec2 release-address --allocation-id eipalloc-031cfd33397f72236
	@echo "✅ Elastic IP released"

check-costs:
	@echo "Checking current resources..."
	@echo "\n📊 Running Instances:"
	@make list-instances
	@echo "\n🌐 Elastic IPs:"
	@make check-elastic-ips

# Add these resource management commands
start-switchboard:
	@echo "🚀 Starting switchboard instance..."
	@aws ec2 start-instances --instance-ids i-09769d9810bdeae42
	@echo "⏳ Waiting for instance to start..."
	@aws ec2 wait instance-running --instance-ids i-09769d9810bdeae42
	@echo "✅ Instance started! Run 'make check-ip' to see the new IP"

allocate-ip:
	@echo "🌐 Allocating new Elastic IP..."
	@aws ec2 allocate-address --domain vpc \
		--query 'AllocationId' --output text > .elastic-ip-id
	@echo "🔗 Associating Elastic IP with instance..."
	@aws ec2 associate-address \
		--instance-id i-09769d9810bdeae42 \
		--allocation-id $$(cat .elastic-ip-id)
	@rm .elastic-ip-id
	@echo "✅ Elastic IP allocated and associated!"

check-status:
	@echo "🔍 Checking switchboard status..."
	@echo "\nInstance Info:"
	@aws ec2 describe-instances \
		--instance-ids i-09769d9810bdeae42 \
		--query 'Reservations[*].Instances[*].{State:State.Name,IP:PublicIpAddress,AZ:Placement.AvailabilityZone}' \
		--output table || echo "⚠️  Error: Instance not found or AWS CLI not configured properly"

check-ip:
	@echo "Current EC2 IP address:"
	@aws ec2 describe-instances \
		--instance-ids i-09769d9810bdeae42 \
		--query 'Reservations[*].Instances[*].PublicIpAddress' \
		--output text
	@echo "\nElastic IP associations:"
	@aws ec2 describe-addresses \
		--query 'Addresses[*].{PublicIP:PublicIp,InstanceId:InstanceId}' \
		--output table

# Add these verification commands
check-instance:
	@echo "🔍 Checking instance status..."
	@aws ec2 describe-instances \
		--instance-ids i-09769d9810bdeae42 \
		--query 'Reservations[*].Instances[*].{State:State.Name,Type:InstanceType,AZ:Placement.AvailabilityZone,StateReason:StateReason.Message}' \
		--output table || echo "⚠️  Instance might be terminated"

check-account:
	@echo "🔍 Checking AWS account status..."
	@aws ec2 describe-account-attributes \
		--query 'AccountAttributes[*].{Name:AttributeName,Value:AttributeValues[0].AttributeValue}' \
		--output table

create-instance:
	@echo "🚀 Creating new t2.micro instance..."
	@aws ec2 run-instances \
		--image-id ami-0c7217cdde317cfec \
		--instance-type t2.micro \
		--key-name switchboard \
		--security-group-ids sg-0123456789abcdef0 \
		--subnet-id subnet-0123456789abcdef0 \
		--tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=switchboard}]' \
		--output table

recover-instance:
	@echo "🚑 Attempting instance recovery..."
	@echo "1️⃣ Force stopping instance..."
	@aws ec2 stop-instances --instance-ids i-09769d9810bdeae42 --force
	@echo "⏳ Waiting for full stop (120 seconds)..."
	@sleep 120
	@echo "2️⃣ Checking instance state..."
	@aws ec2 describe-instances \
		--instance-ids i-09769d9810bdeae42 \
		--query 'Reservations[*].Instances[*].State.Name' \
		--output text
	@echo "3️⃣ Starting instance with recovery..."
	@aws ec2 start-instances --instance-ids i-09769d9810bdeae42
	@echo "⏳ Waiting up to 300 seconds for instance to start..."
	@for i in 1 2 3 4 5; do \
		echo "Attempt $$i of 5..."; \
		if aws ec2 wait instance-running --instance-ids i-09769d9810bdeae42 --max-attempts 12; then \
			echo "✅ Instance is running!"; \
			break; \
		fi; \
		echo "⚠️ Still waiting..."; \
		sleep 60; \
	done
	@echo "4️⃣ Getting instance status..."
	@aws ec2 describe-instance-status \
		--instance-ids i-09769d9810bdeae42 \
		--include-all-instances \
		--output table
	@echo "5️⃣ New IP address:"
	@aws ec2 describe-instances \
		--instance-ids i-09769d9810bdeae42 \
		--query 'Reservations[*].Instances[*].PublicIpAddress' \
		--output text
	@echo "6️⃣ Attempting to verify SSH (30 second timeout)..."
	@timeout 30 ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no -i $(PEM_PATH) ubuntu@$$(aws ec2 describe-instances --instance-ids i-09769d9810bdeae42 --query 'Reservations[*].Instances[*].PublicIpAddress' --output text) exit || echo "⚠️ SSH not responding yet"
	@echo "\n✅ Recovery process completed - check instance status with: make check-instance"

debug-ssh:
	@echo "🔍 Testing SSH with maximum verbosity..."
	@echo "Instance IP: $(EC2_IP)"
	@echo "Testing direct TCP connection to port 22..."
	@nc -zv $(EC2_IP) 22 || echo "❌ TCP connection failed"
	@echo "\nTesting SSH with maximum verbosity..."
	@ssh -vvv \
		-i $(PEM_PATH) \
		-o ConnectTimeout=10 \
		-o BatchMode=yes \
		-o StrictHostKeyChecking=no \
		-o UserKnownHostsFile=/dev/null \
		$(EC2_USER)@$(EC2_IP) "echo '✅ SSH connection successful!'" || \
		(echo "❌ SSH connection failed" && \
		echo "\nChecking security group..." && \
		aws ec2 describe-security-groups \
			--group-ids sg-0a71ed07217f87897 \
			--query 'SecurityGroups[*].IpPermissions' \
			--output table)