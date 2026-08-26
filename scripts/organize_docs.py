import os
import shutil
import subprocess

def main():
    root_dir = os.path.abspath(".")
    docs_dir = os.path.join(root_dir, "docs")
    phases_dir = os.path.join(docs_dir, "phases")
    audits_dir = os.path.join(docs_dir, "audits")
    final_specs_dir = os.path.join(docs_dir, "specifications")
    exports_dir = os.path.join(root_dir, "archive", "exports")

    os.makedirs(phases_dir, exist_ok=True)
    os.makedirs(audits_dir, exist_ok=True)
    os.makedirs(final_specs_dir, exist_ok=True)
    os.makedirs(exports_dir, exist_ok=True)

    # Files that must remain in the root directory
    keep_in_root = {
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "requirements.txt",
        "requirements-lock.txt",
        "pytest.ini",
        "start_all.bat",
        ".gitignore",
        ".env",
        ".env.example",
        ".coderabbit.yaml",
        ".python-version",
        "sentinelai.db"
    }

    # Text export dumps
    export_files = {
        "aegivanta_backend_codebase.txt",
        "aegivanta_complete_codebase.txt",
        "aegivanta_documentation_pack.txt",
        "aegivanta_frontend_codebase.txt",
        "aegivanta_test_suite.txt",
        "aegivanta_codebase_bundle.zip"
    }

    root_files = [f for f in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, f))]
    print(f"Total files in root before organizing: {len(root_files)}")

    moves = []

    for filename in root_files:
        if filename in keep_in_root:
            continue

        src = os.path.join(root_dir, filename)

        if filename in export_files:
            dest = os.path.join(exports_dir, filename)
            moves.append((filename, src, dest, "archive/exports"))
        elif filename.startswith("PHASE"):
            dest = os.path.join(phases_dir, filename)
            moves.append((filename, src, dest, "docs/phases"))
        elif filename.startswith("FINAL_"):
            dest = os.path.join(final_specs_dir, filename)
            moves.append((filename, src, dest, "docs/specifications"))
        elif "AUDIT" in filename or "REPORT" in filename or filename.startswith("REMEDIATION_PLAN") or filename.startswith("DOCUMENTATION_TRUTH"):
            dest = os.path.join(audits_dir, filename)
            moves.append((filename, src, dest, "docs/audits"))
        elif filename.endswith(".md"):
            # Any remaining markdown file in root
            dest = os.path.join(docs_dir, filename)
            moves.append((filename, src, dest, "docs"))
        else:
            print(f"Skipping unclassified file: {filename}")

    print(f"Total files to move: {len(moves)}")

    # Execute moves using git mv if tracked, else shutil.move
    for filename, src, dest, target_folder in moves:
        # Check if tracked by git
        res = subprocess.run(["git", "ls-files", "--error-unmatch", filename], capture_output=True, text=True)
        if res.returncode == 0:
            # File is tracked by git
            rel_dest = os.path.relpath(dest, root_dir)
            git_res = subprocess.run(["git", "mv", "-f", filename, rel_dest], capture_output=True, text=True)
            if git_res.returncode != 0:
                print(f"git mv failed for {filename}: {git_res.stderr.strip()}, falling back to shutil.move")
                shutil.move(src, dest)
        else:
            # Untracked file
            shutil.move(src, dest)

    print("Move operation complete.")

    remaining_root_files = [f for f in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, f))]
    print(f"Remaining files in root: {len(remaining_root_files)}")
    for f in sorted(remaining_root_files):
        print(f" - {f}")

if __name__ == "__main__":
    main()
