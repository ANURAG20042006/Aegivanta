"""
scripts/generate_whole_codebook.py
==================================
Concatenates ALL project source code files into a single master file for easy uploading to ChatGPT.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "SENTINELAI_WHOLE_CODEBOOK.txt"

INCLUDED_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".css", ".html",
    ".json", ".yaml", ".yml", ".md", ".sh", ".bat", ".sql", ".dockerfile"
}
EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    "dist", "build", ".gemini", "catboost_info", ".pytest_cache", ".vscode", ".idea"
}
EXCLUDE_FILES = {
    "SENTINELAI_FULL_CODEBOOK.txt", "SENTINELAI_WHOLE_CODEBOOK.txt",
    "sentinelai_phase1_ai_review_package.zip", "sentinelai_phase2_ai_review_package.zip"
}

def generate_codebook():
    print(f"--> Generating full project codebook at {OUTPUT_FILE}...")
    total_files = 0
    total_lines = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("=" * 80 + "\n")
        out.write("SENTINELAI COMPLETE PROJECT CODEBOOK (PHASE 1 + PHASE 2)\n")
        out.write("All backend, frontend, ML pipeline, tests, scripts, and documentation files.\n")
        out.write("=" * 80 + "\n\n")

        for root, dirs, files in os.walk(ROOT):
            dirs[:] = sorted([d for d in dirs if d not in EXCLUDE_DIRS])
            for file in sorted(files):
                if file in EXCLUDE_FILES or file.startswith("."):
                    continue
                ext = Path(file).suffix.lower()
                if ext not in INCLUDED_EXTS and not file.endswith("Dockerfile"):
                    continue

                full_path = Path(root) / file
                rel_path = full_path.relative_to(ROOT)

                try:
                    content = full_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue

                lines = content.splitlines()
                total_files += 1
                total_lines += len(lines)

                out.write("\n" + "=" * 80 + "\n")
                out.write(f"FILE: {rel_path} ({len(lines)} lines)\n")
                out.write("=" * 80 + "\n\n")
                out.write(content + "\n")

    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"--> Done! Total Files: {total_files}, Total Lines: {total_lines:,}, File Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    generate_codebook()
