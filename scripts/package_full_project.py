"""
scripts/package_full_project.py
===============================
Packages the entire Aegivanta repository (excluding .git, .venv, node_modules, and __pycache__)
into a single clean ZIP archive for external review, ChatGPT audit, or distribution.
"""

import os
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ZIP = PROJECT_ROOT / "aegivanta_complete_project.zip"

EXCLUDE_DIRS = {
    ".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".gemini", "scratch"
}

EXCLUDE_EXTENSIONS = {
    ".pyc", ".pyo", ".log"
}


def package_project():
    print(f"--> Packaging Aegivanta repository from: {PROJECT_ROOT}")
    total_files = 0

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in EXCLUDE_EXTENSIONS or file == OUTPUT_ZIP.name:
                    continue

                rel_path = file_path.relative_to(PROJECT_ROOT)
                zip_file.write(file_path, arcname=str(rel_path))
                total_files += 1

    zip_size_mb = round(OUTPUT_ZIP.stat().st_size / (1024 * 1024), 2)
    print(f"--> Successfully created archive: {OUTPUT_ZIP.name}")
    print(f"--> Total packaged files: {total_files}")
    print(f"--> Archive Size: {zip_size_mb} MB")


if __name__ == "__main__":
    package_project()
