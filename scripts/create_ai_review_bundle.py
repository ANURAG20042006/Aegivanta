"""
scripts/create_ai_review_bundle.py
==================================
Creates an all-in-one AI review package and self-contained document for uploading
to ChatGPT, Claude, or other AI platforms for Phase 1 verification.
"""

import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ZIP = ROOT / "sentinelai_phase1_ai_review_package.zip"
EXPORT_MD = ROOT / "SENTINELAI_PHASE1_AI_REVIEW.md"

EXCLUDE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".gemini", "catboost_info"}
EXCLUDE_EXTS = {".pyc", ".pyd", ".DS_Store", ".zip"}

def make_zip():
    print(f"Creating review zip at {EXPORT_ZIP}...")
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
    print(f"Successfully created zip: {EXPORT_ZIP.stat().st_size / (1024*1024):.2f} MB")

def make_single_file_summary():
    print(f"Creating unified AI review document at {EXPORT_MD}...")
    
    sections = []
    sections.append("# SENTINELAI — PHASE 1 SOC PLATFORM COMPREHENSIVE AI REVIEW PACKAGE\n")
    sections.append("This document contains the complete technical summary, architectural design, database schemas, API contracts, risk engine, correlation engine, and verification test proofs for SentinelAI Phase 1.\n")
    
    # 1. Read README.md
    readme_path = ROOT / "README.md"
    if readme_path.exists():
        sections.append("## 1. Project Overview & Architecture (from README.md)\n")
        sections.append(readme_path.read_text(encoding="utf-8"))
        sections.append("\n---\n")

    # 2. Read SOC_OPERATIONS.md
    soc_ops = ROOT / "docs" / "SOC_OPERATIONS.md"
    if soc_ops.exists():
        sections.append("## 2. SOC Operations & Policies Manual (from docs/SOC_OPERATIONS.md)\n")
        sections.append(soc_ops.read_text(encoding="utf-8"))
        sections.append("\n---\n")

    # 3. Read Provenance
    prov_path = ROOT / "results" / "EXP-2026-002" / "provenance.json"
    if prov_path.exists():
        sections.append("## 3. Experiment Provenance (EXP-2026-002 CatBoost Champion)\n```json\n")
        sections.append(prov_path.read_text(encoding="utf-8"))
        sections.append("\n```\n\n---\n")

    # 4. Core Backend Phase 1 Files
    key_files = [
        "backend/app/services/risk_engine.py",
        "backend/app/services/correlation_engine.py",
        "backend/app/models/protected_asset.py",
        "backend/app/models/alert.py",
        "backend/app/models/security_event.py",
        "backend/app/models/incident_timeline.py",
        "backend/app/api/v1/assets.py",
        "backend/app/api/v1/alerts.py",
        "backend/app/api/v1/incidents.py",
        "tests/integration/test_complete_soc_pipeline.py",
    ]

    sections.append("## 4. Phase 1 Core Backend Implementation & Test Suites\n")
    for kf in key_files:
        fpath = ROOT / kf
        if fpath.exists():
            sections.append(f"### File: `{kf}`\n```python\n")
            sections.append(fpath.read_text(encoding="utf-8"))
            sections.append("\n```\n\n")

    EXPORT_MD.write_text("\n".join(sections), encoding="utf-8")
    print(f"Successfully generated review markdown: {EXPORT_MD} ({EXPORT_MD.stat().st_size / 1024:.2f} KB)")

if __name__ == "__main__":
    make_zip()
    make_single_file_summary()
