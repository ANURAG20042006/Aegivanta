# SentinelAI — Clean-Environment Reproducibility Guide

**Target Version**: 1.0.0  
**Supported Python**: Python 3.11.x  

---

## 1. Clean Environment Setup Procedure

```bash
# 1. Clone the repository
git clone https://github.com/ANURAG20042006/SENTINELAI.git
cd SENTINELAI

# 2. Create isolated virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install exact runtime and test dependencies
pip install -r requirements.txt

# 6. Verify dependency installation
python scripts/verify_environment.py
```

---

## 2. Environment Configuration

Copy `.env.example` to `.env` and configure mandatory environment variables:

```bash
cp .env.example .env
```

Define the required secrets in `.env` or export them:

```ini
SENTINEL_ADMIN_PASSWORD="<YOUR_ADMIN_PASSWORD>"
SENTINEL_ANALYST_PASSWORD="<YOUR_ANALYST_PASSWORD>"
SENTINEL_VIEWER_PASSWORD="<YOUR_VIEWER_PASSWORD>"
POSTGRES_PASSWORD="<YOUR_POSTGRES_PASSWORD>"
SECRET_KEY="<GENERATED_64_CHAR_HEX_SECRET>"
```

Generate a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 3. Reproduction Command Suite

### 3.1 Run Complete Test Suite
```bash
python -m pytest -q
# Target: 0 collection errors, 0 failures, 0 unexpected errors
```

### 3.2 Train ML Pipeline & Generate Artifacts
```bash
python -m ml.train_pipeline
```

### 3.3 Execute Research Experiment Suite
```bash
python scripts/run_research_suite.py
```

### 3.4 Automated Integrity Audit
```bash
python scripts/final_integrity_audit.py
```

### 3.5 Frontend Production Asset Build
```bash
cd frontend
npm install
npm run build
```
