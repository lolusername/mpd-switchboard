#!/bin/bash
# Install git and docker
apt-get update
apt-get install -y docker.io git

# Start Docker service
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone the repository
git clone https://github.com/atiliob/switchboard.git /home/ubuntu/switchboard
cd /home/ubuntu/switchboard/app

# Start using docker-compose
docker-compose up -d 