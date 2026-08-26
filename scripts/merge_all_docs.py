import os
import subprocess

def main():
    root_dir = os.path.abspath(".")
    docs_dir = os.path.join(root_dir, "docs")
    output_file = os.path.join(docs_dir, "DOCUMENTATION.md")

    # Get all markdown files in docs/
    doc_files = sorted([f for f in os.listdir(docs_dir) if f.endswith(".md") and f != "DOCUMENTATION.md"])
    print(f"Found {len(doc_files)} markdown files in docs/ to merge.")

    # Write unified document
    with open(output_file, "w", encoding="utf-8", errors="ignore") as outfile:
        outfile.write("# Aegivanta Platform – Master Unified Documentation\n\n")
        outfile.write("> **Comprehensive single-file documentation for Aegivanta Enterprise Security Operations Platform.**\n\n")
        outfile.write("## 📑 Table of Contents\n\n")

        # Table of contents
        for idx, fname in enumerate(doc_files, 1):
            title = fname.replace(".md", "").replace("_", " ")
            anchor = fname.lower().replace(".md", "").replace("_", "-").replace(" ", "-")
            outfile.write(f"- [{title}](#{anchor})\n")

        outfile.write("\n---\n\n")

        # Append each file content with clear headings and separators
        for fname in doc_files:
            fpath = os.path.join(docs_dir, fname)
            title = fname.replace(".md", "").replace("_", " ")
            anchor = fname.lower().replace(".md", "").replace("_", "-").replace(" ", "-")
            
            outfile.write(f"\n\n<a id=\"{anchor}\"></a>\n\n")
            outfile.write(f"# 📄 {title}\n\n")
            outfile.write(f"*Source: `{fname}`*\n\n")
            outfile.write("---\n\n")

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as infile:
                    content = infile.read().strip()
                    outfile.write(content)
            except Exception as e:
                outfile.write(f"*(Error reading content: {e})*")
            
            outfile.write("\n\n---\n")

    print(f"Master documentation successfully written to {output_file} ({os.path.getsize(output_file)} bytes).")

    # Now remove individual markdown files
    for fname in doc_files:
        fpath = os.path.join(docs_dir, fname)
        rel_path = os.path.relpath(fpath, root_dir)
        subprocess.run(["git", "rm", "-f", rel_path], capture_output=True)
        if os.path.exists(fpath):
            os.remove(fpath)

    print("All individual documentation files removed.")
    remaining = [f for f in os.listdir(docs_dir)]
    print(f"Remaining in docs/: {remaining}")

if __name__ == "__main__":
    main()
