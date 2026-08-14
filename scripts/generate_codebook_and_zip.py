"""
scripts/generate_codebook_and_zip.py
====================================
Generates:
1. SENTINELAI_WHOLE_CODEBOOK.txt - Complete textual representation of every source code file.
2. sentinelai_phase3_full_codebase.zip - Complete clean ZIP archive of the repository.
"""

import os
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CODEBOOK_OUT = ROOT_DIR / "SENTINELAI_WHOLE_CODEBOOK.txt"
ZIP_OUT = ROOT_DIR / "sentinelai_phase3_full_codebase.zip"

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    ".gemini",
    "catboost_info"
}

EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyd",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".zip",
    ".tfevents"
}

ALLOWED_EXTENSIONS_FOR_CODEBOOK = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".css",
    ".html",
    ".md",
    ".ini",
    ".txt",
    ".yaml",
    ".yml"
}

def generate_codebook():
    print(f"Generating complete codebook: {CODEBOOK_OUT}...")
    total_files = 0
    total_lines = 0

    with open(CODEBOOK_OUT, "w", encoding="utf-8") as out:
        out.write("=" * 80 + "\n")
        out.write("SENTINELAI — COMPLETE SOURCE CODEBOOK (PHASE 1, PHASE 2 & PHASE 3)\n")
        out.write("=" * 80 + "\n\n")

        for root, dirs, files in os.walk(ROOT_DIR):
            # Filter directories in place
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

            for file in sorted(files):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT_DIR)

                if file == "SENTINELAI_WHOLE_CODEBOOK.txt" or file == "SENTINELAI_FULL_CODEBOOK.txt":
                    continue
                if file_path.suffix.lower() not in ALLOWED_EXTENSIONS_FOR_CODEBOOK:
                    continue
                if file_path.stat().st_size > 2 * 1024 * 1024:  # skip files > 2MB (e.g. huge artifacts)
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    lines = content.count("\n") + 1
                    total_files += 1
                    total_lines += lines

                    out.write("\n" + "#" * 80 + "\n")
                    out.write(f"FILE: {rel_path.as_posix()}\n")
                    out.write(f"LINES: {lines} | BYTES: {file_path.stat().st_size}\n")
                    out.write("#" * 80 + "\n\n")
                    out.write(content)
                    out.write("\n\n")
                except Exception as e:
                    print(f"Skipping {rel_path}: {e}")

    print(f"Codebook generated: {total_files} files, {total_lines:,} total lines written to {CODEBOOK_OUT}")


def generate_zip():
    print(f"Generating clean ZIP archive: {ZIP_OUT}...")
    file_count = 0

    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ROOT_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

            for file in sorted(files):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT_DIR)

                if file.endswith(".zip") or file.endswith(".db"):
                    continue
                if file_path.suffix.lower() in EXCLUDED_EXTENSIONS:
                    continue

                try:
                    zf.write(file_path, arcname=rel_path.as_posix())
                    file_count += 1
                except Exception as e:
                    print(f"Error zipping {rel_path}: {e}")

    zip_size_mb = ZIP_OUT.stat().st_size / (1024 * 1024)
    print(f"ZIP bundle created: {file_count} files ({zip_size_mb:.2f} MB) at {ZIP_OUT}")


if __name__ == "__main__":
    generate_codebook()
    generate_zip()
