# Contributing to Aegivanta

Thank you for your interest in contributing to **Aegivanta** — an Enterprise AI-Powered Security Operations Platform. We welcome contributions from security engineers, ML practitioners, DevSecOps professionals, and open-source developers.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Test Requirements](#test-requirements)
- [Security Vulnerabilities](#security-vulnerabilities)
- [Commit Message Convention](#commit-message-convention)

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this standard. Please report unacceptable behavior to **security@aegivanta.io**.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Aegivanta.git
   cd Aegivanta
   ```
3. **Set up the upstream remote**:
   ```bash
   git remote add upstream https://github.com/ANURAG20042006/Aegivanta.git
   ```

---

## Development Setup

### Prerequisites

| Tool | Required Version |
|------|-----------------|
| Python | `3.11+` |
| Node.js | `20 LTS` |
| Git | `2.40+` |

### Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env and set required passwords

# Run the test suite
pytest -q
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## How to Contribute

### Reporting Bugs

Please use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md). Include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behaviour
- Python / Node.js version
- Relevant log output

### Suggesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md). Describe:
- The problem your feature solves
- Your proposed solution
- Alternative approaches considered

### Contributing Code

1. Create a **feature branch** from `master`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Make your changes following the [Coding Standards](#coding-standards).
3. Write or update tests — **all PRs require passing tests**.
4. Commit with the [conventional commit format](#commit-message-convention).
5. Push and open a **Pull Request**.

---

## Pull Request Process

1. Ensure the full test suite passes: `pytest -q` and `npm run build`.
2. Update documentation if your change affects API contracts or architecture.
3. Add a clear description of **what changed** and **why**.
4. Link any related issues (`Closes #123`).
5. Request review from a maintainer via `@ANURAG20042006`.
6. PRs require **at least 1 approving review** before merge.
7. Squash-merge is preferred to keep `master` history clean.

---

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guidelines.
- Use **type hints** on all function signatures.
- Write **async** functions for all database and IO operations.
- Use `logger.info("message: %s", variable)` — no f-string log calls.
- Pydantic models for all API request/response schemas.
- Services must be stateless — no in-module state.

### TypeScript (Frontend)

- Strict TypeScript (`"strict": true` in `tsconfig.json`).
- Functional React components with proper `useCallback`/`useMemo` memoization.
- No `any` types — use proper type definitions.
- Tailwind CSS for all styling — no inline CSS.

---

## Test Requirements

Every PR must include tests:

| Change Type | Required Tests |
|-------------|---------------|
| New API endpoint | Integration test in `tests/integration/` |
| New service method | Unit test in `tests/unit/` |
| Security control | Security test in `tests/security/` |
| ML/model change | ML integrity test in `tests/ml/` |
| Bug fix | Regression test preventing recurrence |

Run the full suite before submitting:

```bash
pytest -q                  # Backend: must show 0 failures
cd frontend && npm run build  # Frontend: must exit code 0
```

---

## Security Vulnerabilities

**Do NOT open public GitHub Issues for security vulnerabilities.**

Please report security issues privately via **[SECURITY.md](SECURITY.md)**.

---

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

[optional body]
[optional footer]
```

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation change |
| `test` | Adding/updating tests |
| `refactor` | Code restructuring (no behaviour change) |
| `perf` | Performance improvement |
| `chore` | Build system, CI, dependencies |
| `security` | Security fix or hardening |

**Examples:**
```
feat(soar): add playbook dry-run simulation mode
fix(auth): prevent timing attack in JWT verification
security(tenant): enforce X-Tenant-ID membership validation
test(ml): add leakage-proof test for preprocessing pipeline
```

---

## Recognition

All contributors are recognized in our release notes. Thank you for helping make enterprise security operations better for everyone. 🛡️
