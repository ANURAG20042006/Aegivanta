import os
import shutil
import subprocess

def main():
    root_dir = os.path.abspath(".")
    docs_dir = os.path.join(root_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # Folders to search for markdown files to consolidate into docs/
    search_dirs = [
        os.path.join(docs_dir, "phases"),
        os.path.join(docs_dir, "specifications"),
        os.path.join(docs_dir, "audits"),
        os.path.join(docs_dir, "architecture"),
        os.path.join(docs_dir, "guides"),
        os.path.join(docs_dir, "reports"),
        os.path.join(docs_dir, "security"),
        os.path.join(docs_dir, "api"),
        os.path.join(docs_dir, "archive"),
        os.path.join(root_dir, "archive"),
    ]

    # Specific renames to resolve collisions when flattening into docs/
    rename_map = {
        os.path.join(docs_dir, "architecture", "ARCHITECTURE.md"): "ARCHITECTURE_DETAIL.md",
        os.path.join(docs_dir, "guides", "DEPLOYMENT.md"): "DEPLOYMENT_GUIDE.md",
        os.path.join(docs_dir, "archive", "README.md"): "ARCHIVE_README.md",
        os.path.join(docs_dir, "security", "SECURITY.md"): "SECURITY_HARDENING.md",
        os.path.join(docs_dir, "specifications", "FINAL_API_DOCUMENTATION.md"): "FINAL_API_SPECIFICATION.md",
        os.path.join(docs_dir, "specifications", "FINAL_ARCHITECTURE.md"): "FINAL_ARCHITECTURE_SPECIFICATION.md",
        os.path.join(docs_dir, "specifications", "FINAL_SECURITY_ARCHITECTURE.md"): "FINAL_SECURITY_ARCHITECTURE_SPECIFICATION.md",
        os.path.join(docs_dir, "reports", "PRODUCTION_READINESS_REPORT.md"): "PRODUCTION_READINESS_AUDIT.md",
        os.path.join(docs_dir, "specifications", "FINAL_DEPLOYMENT_GUIDE.md"): "FINAL_DEPLOYMENT_SPECIFICATION.md",
        os.path.join(docs_dir, "specifications", "FINAL_OPERATIONS_RUNBOOK.md"): "FINAL_OPERATIONS_SPECIFICATION.md",
        os.path.join(docs_dir, "specifications", "FINAL_DISASTER_RECOVERY.md"): "FINAL_DISASTER_RECOVERY_SPECIFICATION.md",
        os.path.join(docs_dir, "specifications", "FINAL_PRODUCTION_READINESS.md"): "FINAL_PRODUCTION_READINESS_SPECIFICATION.md",
        os.path.join(docs_dir, "specifications", "FINAL_VALIDATION_REPORT.md"): "FINAL_VALIDATION_SPECIFICATION.md",
        os.path.join(docs_dir, "specifications", "FINAL_THREAT_MODEL.md"): "FINAL_THREAT_MODEL_SPECIFICATION.md",
        os.path.join(docs_dir, "guides", "CONTRIBUTING.md"): "CONTRIBUTING_GUIDE.md",
    }

    moves = []

    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        for root, dirs, files in os.walk(sdir):
            for file in files:
                if not file.endswith(".md"):
                    continue
                src_path = os.path.join(root, file)
                
                # Check if specific collision rename applies
                if src_path in rename_map:
                    target_name = rename_map[src_path]
                else:
                    target_name = file

                dest_path = os.path.join(docs_dir, target_name)

                # Avoid moving if already at dest
                if os.path.abspath(src_path) == os.path.abspath(dest_path):
                    continue

                # If another collision exists, add a suffix
                if os.path.exists(dest_path) and os.path.abspath(src_path) != os.path.abspath(dest_path):
                    base, ext = os.path.splitext(target_name)
                    rel_dir = os.path.basename(root)
                    target_name = f"{base}_{rel_dir}{ext}"
                    dest_path = os.path.join(docs_dir, target_name)

                moves.append((src_path, dest_path, target_name))

    print(f"Total files to move into docs/: {len(moves)}")

    for src_path, dest_path, target_name in moves:
        rel_src = os.path.relpath(src_path, root_dir)
        rel_dest = os.path.relpath(dest_path, root_dir)

        # Check if tracked by git
        res = subprocess.run(["git", "ls-files", "--error-unmatch", rel_src], capture_output=True, text=True)
        if res.returncode == 0:
            git_res = subprocess.run(["git", "mv", "-f", rel_src, rel_dest], capture_output=True, text=True)
            if git_res.returncode != 0:
                print(f"git mv failed for {rel_src}: {git_res.stderr.strip()}, falling back to shutil.move")
                shutil.move(src_path, dest_path)
        else:
            shutil.move(src_path, dest_path)

    print("Finished moving all files into docs/.")

    # Remove empty subdirectories under docs/
    for item in os.listdir(docs_dir):
        subpath = os.path.join(docs_dir, item)
        if os.path.isdir(subpath):
            try:
                shutil.rmtree(subpath)
                print(f"Removed subdirectory: {item}")
            except Exception as e:
                print(f"Could not remove {item}: {e}")

    # Count total md files in docs/
    all_docs = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    print(f"Total .md files now in docs/: {len(all_docs)}")

if __name__ == "__main__":
    main()
