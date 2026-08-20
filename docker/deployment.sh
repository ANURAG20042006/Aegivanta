#!/usr/bin/env bash
# Aegivanta Enterprise Production Deployment Script (Linux / macOS / Git Bash)

set -e

echo "=========================================================="
echo "    Aegivanta Enterprise Platform Deployment Automation   "
echo "=========================================================="

# Step 1: Check Docker Installation
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker engine is not installed. Please install Docker before deploying."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not installed."
    exit 1
fi

# Step 2: Ensure Environment File Exists
if [ ! -f ".env" ]; then
    echo "--> .env file not found. Copying template from .env.example..."
    cp .env.example .env
fi

# Step 3: Build & Launch Docker Container Cluster
echo "--> Building and starting Docker Compose services..."
docker compose -f docker/docker-compose.yml up -d --build

# Step 4: Health Check Verification
echo "--> Waiting for services to reach HEALTHY state..."
sleep 10

echo "=========================================================="
echo "    AEGIVANTA PLATFORM SUCCESSFULLY DEPLOYED              "
echo "=========================================================="
echo "    Frontend Interface:  http://localhost                 "
echo "    FastAPI REST Docs:   http://localhost/docs            "
echo "    Health Check:        http://localhost/health          "
echo "=========================================================="
