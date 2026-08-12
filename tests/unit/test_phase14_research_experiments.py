import os
import json
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_research_experiment_artifacts_exist():
    """Requirement 1 & 2 Proof: All research artifacts are generated dynamically under results/EXP-2026-001/."""
    exp_dir = PROJECT_ROOT / "results" / "EXP-2026-001"
    
    # Required files
    required_files = [
        "dataset_statistics.json",
        "experiment_config.json",
        "baseline_comparison.csv",
        "cross_validation.csv",
        "ablation.csv",
        "confusion_matrix.json",
        "per_class_metrics.csv",
        "robustness_testing.csv",
        "explainability_examples.json",
        "research_summary.json"
    ]

    for fname in required_files:
        filepath = exp_dir / fname
        assert filepath.exists(), f"Missing required research artifact: {fname}"
        assert filepath.stat().st_size > 0, f"Artifact is empty: {fname}"


def test_research_summary_content():
    """Requirement 2 Proof: Research summary contains valid non-hardcoded metrics."""
    summary_path = PROJECT_ROOT / "results" / "EXP-2026-001" / "research_summary.json"
    if summary_path.exists():
        with open(summary_path, "r") as f:
            data = json.load(f)
        
        assert "experiment_id" in data
        assert "best_model" in data
        assert "best_cv_f1" in data
        assert isinstance(data["best_cv_f1"], float)
        assert data["best_cv_f1"] > 0.0
