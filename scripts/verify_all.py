import os
import subprocess
import urllib.request

def main():
    print("=" * 70)
    print("1. REPOSITORY ROOT LISTING")
    print("=" * 70)
    for item in sorted(os.listdir(".")):
        if item in [".git", ".venv", ".pytest_cache"]:
            continue
        is_dir = os.path.isdir(item)
        kind = "<DIR>" if is_dir else f"{os.path.getsize(item):>10} B"
        print(f"{kind:<14} {item}")

    print("\n" + "=" * 70)
    print("2. DOCS DIRECTORY CONTENT")
    print("=" * 70)
    for item in sorted(os.listdir("docs")):
        full_p = os.path.join("docs", item)
        size_bytes = os.path.getsize(full_p)
        size_mb = size_bytes / (1024 * 1024)
        print(f"{item}: {size_mb:.2f} MB ({size_bytes:,} bytes)")

    print("\n" + "=" * 70)
    print("3. GIT REPOSITORY STATUS & COMMITS")
    print("=" * 70)
    res = subprocess.run(["git", "status"], capture_output=True, text=True)
    print(res.stdout.strip())
    print("\nRecent Commits:")
    log_res = subprocess.run(["git", "log", "-4", "--oneline"], capture_output=True, text=True)
    print(log_res.stdout.strip())

    print("\n" + "=" * 70)
    print("4. LIVE PLATFORM HEALTH CHECK")
    print("=" * 70)
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/docs", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"Backend API Docs  (http://127.0.0.1:8000/docs):  Status {r.status} OK")
    except Exception as e:
        print(f"Backend API: {e}")

    try:
        req = urllib.request.Request("http://localhost:5173/", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"Frontend Dev App (http://localhost:5173/):       Status {r.status} OK")
    except Exception as e:
        print(f"Frontend App: {e}")

if __name__ == "__main__":
    main()
