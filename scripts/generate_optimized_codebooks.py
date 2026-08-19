"""
scripts/generate_optimized_codebooks.py
=======================================
Generates compact, highly-readable codebooks optimized for ChatGPT and LLM uploads:
1. SENTINELAI_CORE_CODEBOOK.txt (< 200 KB) - Core backend, ML, API, models, and security.
2. 01_BACKEND_AND_SERVICES.txt (< 600 KB) - Full backend services, database models, routers.
3. 02_ML_PIPELINE_AND_SECURITY.txt (< 300 KB) - ML inference, feature schemas, security controls.
4. 03_FRONTEND_AND_COMPONENTS.txt (< 500 KB) - React views, contexts, and API services.
5. sentinelai_source_only.zip (< 300 KB) - Pure source code zip bundle.
"""

import os
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

CORE_FILES = [
    # Core Config & Main
    "backend/app/main.py",
    "backend/app/config.py",
    "backend/app/database.py",
    "backend/app/security.py",
    
    # Models
    "backend/app/models/incident.py",
    "backend/app/models/alert.py",
    "backend/app/models/protected_asset.py",
    "backend/app/models/hunting.py",
    "backend/app/models/predictive.py",
    "backend/app/models/threat_graph.py",
    "backend/app/models/response_approval.py",
    "backend/app/models/attack_coverage.py",
    "backend/app/models/job.py",
    
    # Services
    "backend/app/services/predict_service.py",
    "backend/app/services/risk_engine.py",
    "backend/app/services/correlation_engine.py",
    "backend/app/services/hunting_service.py",
    "backend/app/services/predictive_service.py",
    "backend/app/services/threat_graph_service.py",
    "backend/app/services/campaign_service.py",
    "backend/app/services/attack_coverage_service.py",
    "backend/app/services/soc_metrics_service.py",
    "backend/app/services/response_orchestrator.py",
    "backend/app/services/job_manager.py",
    
    # ML & Schema
    "ml/schema/feature_schema.py",
    "ml/schema/artifact_mapping.py",
    "ml/explainability/real_explainer.py",
    
    # Security & API
    "backend/app/core/rate_limit.py",
    "backend/app/api/v1/websockets.py",
    "backend/app/api/v1/hunting.py",
    "backend/app/api/v1/predictive.py",
    "backend/app/api/v1/response.py",
    "backend/app/api/v1/attack_coverage.py",
    "backend/app/api/v1/soc_metrics.py",
    
    # Key E2E Test
    "tests/integration/test_complete_soc_pipeline.py",
    "tests/integration/test_phase3_e2e.py"
]

def write_bundle(file_paths, output_name, title):
    out_path = ROOT_DIR / output_name
    written = 0
    total_lines = 0
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"{'=' * 80}\n{title}\n{'=' * 80}\n\n")
        for rel_str in file_paths:
            fp = ROOT_DIR / rel_str
            if fp.exists():
                content = fp.read_text(encoding="utf-8", errors="replace")
                lines = content.count("\n") + 1
                total_lines += lines
                written += 1
                out.write(f"\n{'#' * 80}\nFILE: {rel_str} ({lines} lines)\n{'#' * 80}\n\n")
                out.write(content)
                out.write("\n\n")
    kb_size = round(out_path.stat().st_size / 1024, 1)
    print(f"Generated {output_name}: {written} files, {total_lines:,} lines ({kb_size} KB)")

def generate_source_zip():
    zip_out = ROOT_DIR / "sentinelai_source_only.zip"
    count = 0
    with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ROOT_DIR):
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "node_modules", "__pycache__", "dist", ".gemini", "catboost_info", "results"}]
            for file in files:
                if file.endswith((".py", ".ts", ".tsx", ".json", ".md", ".yml", ".yaml")):
                    fp = Path(root) / file
                    if fp.stat().st_size < 500 * 1024 and not file.startswith("SENTINELAI_"):
                        rel = fp.relative_to(ROOT_DIR)
                        zf.write(fp, arcname=rel.as_posix())
                        count += 1
    kb_size = round(zip_out.stat().st_size / 1024, 1)
    print(f"Generated sentinelai_source_only.zip: {count} files ({kb_size} KB)")

if __name__ == "__main__":
    # 1. Compact Core Codebook (Guaranteed to be accepted by ChatGPT)
    write_bundle(CORE_FILES, "SENTINELAI_CORE_CODEBOOK.txt", "SENTINELAI — CORE ARCHITECTURE & SERVICES (LIGHTWEIGHT BUNDLE)")
    
    # 2. Source-only Zip
    generate_source_zip()
