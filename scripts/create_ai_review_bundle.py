"""
scripts/create_ai_review_bundle.py
==================================
Creates an all-in-one AI review package (ZIP + Markdown) for uploading
to ChatGPT, Claude, Gemini, or other AI platforms for Phase 2 verification.
"""

import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ZIP = ROOT / "sentinelai_phase2_ai_review_package.zip"
EXPORT_MD = ROOT / "SENTINELAI_PHASE2_COMPREHENSIVE_REVIEW.md"

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    "dist", "build", ".gemini", "catboost_info", ".pytest_cache", ".vscode", ".idea"
}
EXCLUDE_EXTS = {".pyc", ".pyd", ".DS_Store", ".zip", ".db", ".sqlite3"}

def make_zip():
    print(f"--> Creating AI review zip package at {EXPORT_ZIP}...")
    with zipfile.ZipFile(EXPORT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                ext = Path(file).suffix
                if ext in EXCLUDE_EXTS or file.startswith("."):
                    continue
                full_path = Path(root) / file
                rel_path = full_path.relative_to(ROOT)
                zf.write(full_path, rel_path)
    print(f"--> Successfully created zip: {EXPORT_ZIP} ({EXPORT_ZIP.stat().st_size / (1024*1024):.2f} MB)")

def make_single_file_summary():
    print(f"--> Creating unified AI review markdown at {EXPORT_MD}...")
    
    sections = []
    sections.append("# SENTINELAI — PHASE 2 PRODUCTION SOC PLATFORM COMPREHENSIVE AI REVIEW\n")
    sections.append("This document contains the complete technical summary, architectural design, database schemas, API contracts, threat intelligence, continuous monitoring, SSRF defenses, behavioral anomaly engine, automated investigations, ATT&CK mappings, playbook safety, and verification test proofs for SentinelAI Phase 2.\n")
    
    # 1. Read Current Status
    status_path = ROOT / "docs" / "CURRENT_STATUS.md"
    if status_path.exists():
        sections.append("## 1. System Status & Verification Summary (docs/CURRENT_STATUS.md)\n")
        sections.append(status_path.read_text(encoding="utf-8"))
        sections.append("\n---\n")

    # 2. Read Phase 2 Architecture
    arch_path = ROOT / "docs" / "PHASE_2_ARCHITECTURE.md"
    if arch_path.exists():
        sections.append("## 2. Phase 2 Additive Architecture (docs/PHASE_2_ARCHITECTURE.md)\n")
        sections.append(arch_path.read_text(encoding="utf-8"))
        sections.append("\n---\n")

    # 3. Read Phase 2 Baseline
    base_path = ROOT / "docs" / "PHASE_2_BASELINE.md"
    if base_path.exists():
        sections.append("## 3. Dynamic Baseline & Test Regression (docs/PHASE_2_BASELINE.md)\n")
        sections.append(base_path.read_text(encoding="utf-8"))
        sections.append("\n---\n")

    # 4. Read Provenance
    prov_path = ROOT / "results" / "EXP-2026-002" / "provenance.json"
    if prov_path.exists():
        sections.append("## 4. Authoritative ML Provenance (EXP-2026-002 CatBoost Champion)\n```json\n")
        sections.append(prov_path.read_text(encoding="utf-8"))
        sections.append("\n```\n\n---\n")

    # 5. Core Backend Phase 2 Files
    key_files = [
        "backend/app/services/monitoring_service.py",
        "backend/app/services/threat_intel_service.py",
        "backend/app/services/anomaly_service.py",
        "backend/app/services/investigation_service.py",
        "backend/app/services/playbook_service.py",
        "backend/app/api/v1/monitoring.py",
        "backend/app/api/v1/threat_intel.py",
        "backend/app/api/v1/analytics.py",
        "backend/app/api/v1/investigations.py",
        "backend/app/api/v1/playbooks.py",
        "backend/app/models/monitoring.py",
        "backend/app/models/threat_intel.py",
        "backend/app/models/behavioral.py",
        "backend/app/models/investigation.py",
        "backend/app/models/playbook.py",
        "tests/integration/test_phase2_e2e_pipeline.py",
        "tests/unit/test_phase2_monitoring_ssrf.py",
        "tests/unit/test_phase2_anomaly_investigation.py",
    ]

    sections.append("## 5. Phase 2 Core Implementations & Test Proofs\n")
    for kf in key_files:
        fpath = ROOT / kf
        if fpath.exists():
            sections.append(f"### File: `{kf}`\n```python\n")
            sections.append(fpath.read_text(encoding="utf-8"))
            sections.append("\n```\n\n")

    EXPORT_MD.write_text("\n".join(sections), encoding="utf-8")
    print(f"--> Successfully generated review markdown: {EXPORT_MD} ({EXPORT_MD.stat().st_size / 1024:.2f} KB)")

if __name__ == "__main__":
    make_zip()
    make_single_file_summary()
