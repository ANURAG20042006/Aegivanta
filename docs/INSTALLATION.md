# SentinelAI Installation & Local Setup Guide

This guide provides step-by-step instructions for installing and running SentinelAI on Windows, Linux, and macOS.

---

## Prerequisites
Ensure the following software packages are installed:
- **Python**: Version 3.11 (tested on Python 3.11.5; see `.python-version`)
- **Node.js**: Version 18, 20, or 22 & npm
- **Docker & Docker Compose** (Optional for containerized setup)
- **Git** (`git --version`)

---

## Method 1: Bare-Metal Setup (Development Mode)

### Step 1: Clone Repository
```bash
git clone https://github.com/ANURAG20042006/SENTINELAI.git
cd SENTINELAI
```

### Step 2: Set Up Backend Virtual Environment
```bash
# Create virtual environment using Python 3.11
py -3.11 -m venv .venv

# Activate on Windows
.\.venv\Scripts\activate

# Activate on Linux / macOS
source .venv/bin/activate

# Install locked dependencies for a 100% reproducible environment
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
```

### Step 3: Run ML Model Training Pipeline
Initialize the preprocessor and train all ML/DL models locally:
```bash
python -m ml.train_pipeline
```
*Trained champion model artifacts will be saved to `ml/artifacts/best_model.joblib`.*

### Step 4: Start FastAPI Backend Application
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
*FastAPI server will run at [http://localhost:8000](http://localhost:8000). Interactive Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).*

### Step 5: Set Up & Launch React Frontend
Open a new terminal window:
```bash
cd frontend
npm ci
npm run dev
```
*Vite development server will launch at [http://localhost:5173](http://localhost:5173).*

### Step 6: Automated Testing & Build Verification
```bash
# Run backend test suite (isolated SQLite database in tempdir)
python -m pytest -q

# Run frontend production build
cd frontend
npm run build
```

---

## Method 2: Docker Containerized Setup (Production Mode)

### Step 1: Copy Environment Variables
```bash
cp .env.example .env
```

### Step 2: Execute Deployment Script
```bash
# On Linux / macOS
chmod +x docker/deployment.sh
./docker/deployment.sh

# On Windows PowerShell
.\docker\deployment.ps1
```

---

## Verification & Troubleshooting
- **Backend Health Check**: Open `http://localhost:8000/health`. Should return `{"status": "HEALTHY"}`.
- **Frontend Dashboard**: Open `http://localhost:5173` or `http://localhost:80`. Login using `admin`, `analyst`, or `viewer` roles with their configured passwords (defined via environment variables or seeder defaults in `.env`).
