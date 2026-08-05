# SentinelAI Installation & Local Setup Guide

This guide provides step-by-step instructions for installing and running SentinelAI on Windows, Linux, and macOS.

---

## Prerequisites
Ensure the following software packages are installed:
- **Python**: Version 3.11 or higher (`python --version`)
- **Node.js**: Version 18 or 20 (`node -v`) & npm (`npm -v`)
- **Docker & Docker Compose** (Optional for containerized setup)
- **Git** (`git --version`)

---

## Method 1: Bare-Metal Setup (Development Mode)

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/sentinelai.git
cd sentinelai
```

### Step 2: Set Up Backend Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on Linux / macOS
source venv/bin/activate

# Install Backend & ML Dependencies
pip install -r backend/requirements.txt
```

### Step 3: Run ML Model Training Pipeline
Initialize the preprocessor and train all 12 ML/DL models locally:
```bash
python -m ml.train_pipeline
```
*Trained model artifacts will be saved to `ml/artifacts/best_model.joblib`.*

### Step 4: Start FastAPI Backend Application
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
*FastAPI server will run at [http://localhost:8000](http://localhost:8000). Interactive Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).*

### Step 5: Set Up & Launch React Frontend
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*Vite development server will launch at [http://localhost:5173](http://localhost:5173).*

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
- **Frontend Dashboard**: Open `http://localhost:5173` or `http://localhost:80`. Login using `admin` / `AdminSecure2026!`, `analyst` / `AnalystSecure2026!`, or `viewer` / `ViewerSecure2026!`.
