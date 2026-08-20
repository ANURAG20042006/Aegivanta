# Contributing to SentinelAI

Thank you for your interest in contributing to **SentinelAI – Intelligent Network Intrusion Detection & Threat Analytics Platform**! 

We welcome bug reports, feature requests, pull requests, and documentation improvements.

---

## 🛠️ Development Setup

1. **Fork & Clone Repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/SENTINELAI.git
   cd SENTINELAI
   ```

2. **Backend Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

---

## 🧪 Running Verification Tests

Before submitting a pull request, ensure all tests pass:

```bash
# Run Backend Integration Tests
python -m tests.integration_test_runner

# Build Frontend Bundle
cd frontend
npm run build
```

---

## 📝 Commit & Pull Request Guidelines

- Use clear, descriptive commit messages following the Conventional Commits format (e.g. `feat: ...`, `fix: ...`, `docs: ...`).
- Ensure no hardcoded API keys or credentials are committed.
- Keep pull requests focused on a single issue or feature.
