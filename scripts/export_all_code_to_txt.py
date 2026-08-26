"""
scripts/export_all_code_to_txt.py
=================================
Concatenates all readable source code, tests, schemas, configs, manifests,
and reports into a single structured, easily readable TXT file.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_TXT = PROJECT_ROOT / "AEGIVANTA_COMPLETE_CODEBASE.txt"

EXCLUDE_DIRS = {
    ".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".gemini", "scratch"
}

ALLOWED_EXTENSIONS = {
    ".py", ".md", ".json", ".sql", ".yaml", ".yml", ".ini", ".env", ".ts", ".tsx", ".js", ".jsx", ".css", ".html"
}

EXCLUDE_FILES = {
    "AEGIVANTA_COMPLETE_CODEBASE.txt",
    "package-lock.json"
}


def export_codebase():
    print(f"--> Exporting complete codebase from: {PROJECT_ROOT}")
    total_files = 0
    total_lines = 0

    with open(OUTPUT_TXT, "w", encoding="utf-8", errors="replace") as out:
        out.write("=" * 100 + "\n")
        out.write("  AEGIVANTA / SENTINELAI — COMPLETE SOURCE CODE & ARTIFACT COMPILATION\n")
        out.write(f"  Generated on: {PROJECT_ROOT}\n")
        out.write("=" * 100 + "\n\n")

        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = sorted([d for d in dirs if d not in EXCLUDE_DIRS])

            for file in sorted(files):
                file_path = Path(root) / file
                if file_path.suffix.lower() not in ALLOWED_EXTENSIONS or file in EXCLUDE_FILES:
                    continue

                rel_path = file_path.relative_to(PROJECT_ROOT)
                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                except Exception as e:
                    print(f"Skipping binary/unreadable file: {rel_path} ({e})")
                    continue

                file_lines = len(content.splitlines())
                total_lines += file_lines
                total_files += 1

                out.write("\n" + "=" * 100 + "\n")
                out.write(f"FILE: {rel_path.as_posix()} | Lines: {file_lines}\n")
                out.write("=" * 100 + "\n\n")
                out.write(content)
                out.write("\n")

    size_mb = round(OUTPUT_TXT.stat().st_size / (1024 * 1024), 2)
    print(f"--> Successfully created: {OUTPUT_TXT.name}")
    print(f"--> Total Files Merged: {total_files}")
    print(f"--> Total Lines of Code: {total_lines:,}")
    print(f"--> File Size: {size_mb} MB")


if __name__ == "__main__":
    export_codebase()
