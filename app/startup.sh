#!/bin/bash
set -e  # Exit on any error

# Install dependencies
apt-get update
apt-get install -y docker.io git curl jq

# Start Docker service
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone the repository
git clone https://github.com/atiliob/switchboard.git /home/ubuntu/switchboard
cd /home/ubuntu/switchboard/app

# Start services and wait for health
docker-compose up -d

# Wait for services to be healthy
timeout 300 bash -c 'until docker-compose ps | grep -q "healthy"; do sleep 5; done' 