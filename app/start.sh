#!/bin/bash

# Start Elasticsearch
sudo -u elasticsearch /usr/share/elasticsearch/bin/elasticsearch -d

# Wait for Elasticsearch
while ! curl -s http://localhost:9200/_cluster/health > /dev/null; do
    echo "Waiting for Elasticsearch..."
    sleep 5
done

# Start the API in background
cd /app
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the frontend
cd /app/frontend
node server/index.mjs 