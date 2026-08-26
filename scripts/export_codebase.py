"""
scripts/export_codebase.py
==========================
Bundles the Aegivanta codebase into:
1. Full unified bundle (txt and zip)
2. Modular category bundles (Backend, Frontend, Tests, Docs)
Optimized for feeding into ChatGPT, Claude, GPT-4o, Custom GPTs, and LLMs.
"""

import os
import zipfile
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git", ".venv", "node_modules", ".pytest_cache", "__pycache__",
    "catboost_info", "dist", "build", ".ralph", ".planning", "backups", "logs"
}

EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".db", ".sqlite", ".sqlite3", ".pkl",
    ".bin", ".exe", ".dll", ".so", ".dylib", ".ico", ".png", ".jpg",
    ".jpeg", ".svg", ".zip", ".tar", ".gz", ".lock"
}

ALLOWED_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".yml",
    ".yaml", ".sql", ".sh", ".bat", ".ps1", ".ini", ".env.example", ".dockerignore", "Dockerfile"
}


def should_include(file_path: Path) -> bool:
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False

    ext = file_path.suffix.lower()
    name = file_path.name.lower()

    if ext in EXCLUDE_EXTS:
        return False

    if ext in ALLOWED_EXTS or name in {"dockerfile", ".env.example", "pytest.ini", "requirements.txt"}:
        if file_path.stat().st_size > 500_000:
            return False
        return True

    return False


def write_bundle(file_list, output_txt_path, title):
    total_chars = 0
    with open(output_txt_path, "w", encoding="utf-8") as out:
        out.write(f"# {'=' * 77}\n")
        out.write(f"# AEGIVANTA — {title.upper()}\n")
        out.write(f"# Total Files: {len(file_list)}\n")
        out.write(f"# {'=' * 77}\n\n")

        for fp in file_list:
            rel_path = fp.relative_to(WORKSPACE_ROOT).as_posix()
            try:
                content = fp.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"# [Error reading file: {e}]"

            out.write(f"\n{'=' * 80}\n")
            out.write(f"FILE: {rel_path}\n")
            out.write(f"{'=' * 80}\n")
            out.write(content)
            out.write("\n\n")
            total_chars += len(content)

    print(f"[+] Generated: {output_txt_path.name} ({output_txt_path.stat().st_size / (1024 * 1024):.2f} MB, {len(file_list)} files)")


def build_codebase_bundles():
    all_files = []
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in sorted(files):
            fp = Path(root) / f
            if should_include(fp):
                all_files.append(fp)

    all_files.sort(key=lambda p: str(p.relative_to(WORKSPACE_ROOT)))

    backend_files = [f for f in all_files if "backend" in f.parts]
    frontend_files = [f for f in all_files if "frontend" in f.parts]
    test_files = [f for f in all_files if "tests" in f.parts]
    doc_files = [f for f in all_files if f.suffix == ".md" or "docs" in f.parts]

    # 1. Full Master Bundle
    write_bundle(all_files, WORKSPACE_ROOT / "aegivanta_complete_codebase.txt", "COMPLETE PLATFORM CODEBASE (V50.0.0)")

    # 2. Modular Sub-Bundles
    write_bundle(backend_files, WORKSPACE_ROOT / "aegivanta_backend_codebase.txt", "BACKEND SOURCE CODE")
    write_bundle(frontend_files, WORKSPACE_ROOT / "aegivanta_frontend_codebase.txt", "FRONTEND SOURCE CODE")
    write_bundle(test_files, WORKSPACE_ROOT / "aegivanta_test_suite.txt", "COMPLETE TEST SUITE")
    write_bundle(doc_files, WORKSPACE_ROOT / "aegivanta_documentation_pack.txt", "ARCHITECTURE & SPECIFICATION DOCS")

    # 3. Zip Archive of everything
    output_zip = WORKSPACE_ROOT / "aegivanta_codebase_bundle.zip"
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in all_files:
            rel_path = fp.relative_to(WORKSPACE_ROOT)
            zf.write(fp, arcname=rel_path)

    print(f"[+] Zip Archive: {output_zip.name} ({output_zip.stat().st_size / (1024 * 1024):.2f} MB)")


if __name__ == "__main__":
    build_codebase_bundles()
