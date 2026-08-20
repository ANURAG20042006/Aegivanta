# Aegivanta Enterprise Production Deployment Script (Windows PowerShell)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    Aegivanta Enterprise Platform Deployment Automation   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Step 1: Check Docker
try {
    docker --version | Out-Null
} catch {
    Write-Host "ERROR: Docker engine is not running or not installed." -ForegroundColor Red
    Exit 1
}

# Step 2: Environment File Setup
if (-not (Test-Path ".env")) {
    Write-Host "--> .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# Step 3: Build & Launch Container Stack
Write-Host "--> Launching Docker Compose Stack..." -ForegroundColor Green
docker compose -f docker/docker-compose.yml up -d --build

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    AEGIVANTA PLATFORM SUCCESSFULLY DEPLOYED              " -ForegroundColor Green
Write-Host "    Frontend Dashboard: http://localhost                  " -ForegroundColor Yellow
Write-Host "    Backend API Docs:   http://localhost/docs             " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
