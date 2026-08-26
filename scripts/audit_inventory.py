import os
import re
from collections import defaultdict

KEYWORDS = [
    'EXP-2026', 'experiment_id', 'dataset_hash', 'dataset_identifier', 'dataset_total_samples',
    'train_samples', 'test_samples', 'smote', 'StratifiedKFold', 'n_splits',
    'champion_model', 'best_model', 'model_version', 'artifact_path', 'artifact_manifest',
    'provenance', 'metadata', 'SHAP', 'LIME', 'explainability',
    'latency', 'accuracy', 'F1', 'ROC-AUC', 'FPR',
    'production', 'benchmark', 'synthetic', 'mock', 'simulated',
    'demo', 'seeded', 'fabricated', 'FedRAMP', 'SOC 2',
    'ISO 27001', 'HIPAA', 'PCI DSS', 'SentinelAI', 'SENTINELAI',
    'Aegivanta', 'AEGIVANTA', 'aegivanta'
]

findings = defaultdict(list)
EXCLUDE = {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', 'exports', 'archive/exports'}

def run():
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not any(ex in os.path.join(root, d) for ex in EXCLUDE)]
        if any(ex in root for ex in ['exports', '.git', '.venv', 'node_modules']):
            continue
        for f in files:
            if f.endswith(('.py', '.json', '.csv', '.md', '.yml', '.yaml', '.ts', '.tsx')):
                fp = os.path.normpath(os.path.join(root, f))
                try:
                    content = open(fp, 'r', encoding='utf-8', errors='ignore').read()
                except Exception:
                    continue
                for kw in KEYWORDS:
                    pattern = rf'\b{re.escape(kw)}\b' if not any(c in kw for c in ['-', ' ']) else re.escape(kw)
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        findings[kw].append((fp, len(matches)))

    print("=== Keyword Occurrence Summary ===")
    for kw in KEYWORDS:
        files = findings[kw]
        print(f"{kw:25}: in {len(files):3} files ({sum(cnt for _, cnt in files):5} matches)")

if __name__ == "__main__":
    run()
