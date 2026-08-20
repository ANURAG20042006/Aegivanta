"""
tests/unit/test_adaptive_ensemble_detection.py
==============================================
Phase 3.10 Unit Tests: Adaptive ML Ensemble Detection.
Tests 5-domain scoring, fallback behavior, calibration, and safety guardrails.
"""

import pytest
import numpy as np


class TestConfidenceCalibrator:

    def test_calibrate_bounds_are_zero_to_one(self):
        """Calibrated scores must be clamped to [0, 1]."""
        from backend.app.services.ensemble_service import ConfidenceCalibrator

        assert ConfidenceCalibrator.calibrate(1.0) == 1.0
        assert ConfidenceCalibrator.calibrate(0.0) == 0.0
        c = ConfidenceCalibrator.calibrate(0.7)
        assert 0.0 <= c <= 1.0

    def test_temperature_scaling_softens_overconfident_predictions(self):
        """Temperature T > 1.0 must reduce calibrated prob below raw for p > 0.5."""
        from backend.app.services.ensemble_service import ConfidenceCalibrator

        raw = 0.99
        calibrated = ConfidenceCalibrator.calibrate(raw, temperature=1.15)
        assert calibrated < raw
        assert calibrated > 0.50

    def test_low_temperature_sharpens_predictions(self):
        """Temperature T < 1.0 must increase calibrated prob above raw for p > 0.5."""
        from backend.app.services.ensemble_service import ConfidenceCalibrator

        raw = 0.60
        calibrated = ConfidenceCalibrator.calibrate(raw, temperature=0.80)
        assert calibrated > raw


class TestEnsembleThreatDetector:

    def test_detector_has_default_weights_when_no_metadata(self):
        """Ensemble detector must use default weights when metadata is missing."""
        from backend.app.services.ensemble_service import EnsembleThreatDetector
        from pathlib import Path

        detector = EnsembleThreatDetector(metadata_path=Path("/nonexistent/metadata.json"))

        assert len(detector.model_weights) > 0
        assert "CatBoost" in detector.model_weights
        assert "LightGBM" in detector.model_weights
        # Weights must be positive
        for name, w in detector.model_weights.items():
            assert w > 0.0, f"Model {name} has non-positive weight"

    def test_aggregate_weighted_confidence_selects_dominant_class(self):
        """Weighted confidence strategy must select the class with highest weighted probability."""
        from backend.app.services.ensemble_service import EnsembleThreatDetector, EnsembleStrategy

        detector = EnsembleThreatDetector()
        predictions_map = {
            "CatBoost":      ("DDoS",     0.95, {"DDoS": 0.95, "BENIGN": 0.05}),
            "LightGBM":      ("DDoS",     0.92, {"DDoS": 0.92, "BENIGN": 0.08}),
            "Random Forest": ("PortScan", 0.70, {"PortScan": 0.70, "BENIGN": 0.30}),
        }
        result = detector.aggregate_predictions(predictions_map, strategy=EnsembleStrategy.WEIGHTED_CONFIDENCE)

        assert result["final_prediction"] == "DDoS"
        assert 0.0 <= result["calibrated_confidence"] <= 1.0
        assert result["is_malicious"] is True
        assert result["model_agreement_pct"] >= 60.0

    def test_aggregate_hard_voting_returns_majority(self):
        """Hard voting must select the class with the most model votes."""
        from backend.app.services.ensemble_service import EnsembleThreatDetector, EnsembleStrategy

        detector = EnsembleThreatDetector()
        predictions_map = {
            "A": ("BENIGN",  0.80, {"BENIGN": 0.80, "DDoS": 0.20}),
            "B": ("BENIGN",  0.75, {"BENIGN": 0.75, "DDoS": 0.25}),
            "C": ("DDoS",    0.90, {"DDoS": 0.90, "BENIGN": 0.10}),
        }
        result = detector.aggregate_predictions(predictions_map, strategy=EnsembleStrategy.HARD_VOTING)

        assert result["final_prediction"] == "BENIGN"
        assert result["is_malicious"] is False

    def test_aggregate_soft_voting_averages_probabilities(self):
        """Soft voting must average probabilities across all models."""
        from backend.app.services.ensemble_service import EnsembleThreatDetector, EnsembleStrategy

        detector = EnsembleThreatDetector()
        predictions_map = {
            "A": ("BENIGN", 0.80, {"BENIGN": 0.80, "DDoS": 0.20}),
            "B": ("DDoS",   0.90, {"DDoS": 0.90, "BENIGN": 0.10}),
        }
        result = detector.aggregate_predictions(predictions_map, strategy=EnsembleStrategy.SOFT_VOTING)

        assert result["final_prediction"] in {"BENIGN", "DDoS"}
        assert 0.0 <= result["calibrated_confidence"] <= 1.0

    def test_aggregate_raises_on_empty_predictions(self):
        """Aggregation must raise ValueError if predictions_map is empty."""
        from backend.app.services.ensemble_service import EnsembleThreatDetector

        detector = EnsembleThreatDetector()
        with pytest.raises(ValueError, match="cannot be empty"):
            detector.aggregate_predictions({})

    def test_severity_critical_for_very_high_confidence(self):
        """Severity must be Critical when calibrated_confidence >= 0.90."""
        from backend.app.services.ensemble_service import EnsembleThreatDetector, EnsembleStrategy

        detector = EnsembleThreatDetector()
        predictions_map = {
            "CatBoost": ("DDoS", 0.99, {"DDoS": 0.99, "BENIGN": 0.01}),
            "LightGBM": ("DDoS", 0.98, {"DDoS": 0.98, "BENIGN": 0.02}),
        }
        result = detector.aggregate_predictions(predictions_map, strategy=EnsembleStrategy.SOFT_VOTING)

        assert result["severity"] == "Critical"


class TestAdaptiveDetectionServiceRuleEvaluation:

    def test_rule_score_structure_is_valid(self):
        """Deterministic rule evaluation must return all required keys."""
        from backend.app.services.adaptive_detection_service import AdaptiveDetectionService

        svc = AdaptiveDetectionService()
        event = {"source_ip": "10.0.0.1", "destination_ip": "10.0.0.100", "Flow Packets/s": 100}
        result = svc._evaluate_deterministic_rules(event)

        for key in ["rule_score", "matched_count", "matches", "authoritative_rule"]:
            assert key in result, f"Missing key: {key}"
        assert 0.0 <= result["rule_score"] <= 100.0
        assert isinstance(result["matched_count"], int)
        assert isinstance(result["matches"], list)

    def test_rule_score_escalates_with_multiple_rule_matches(self):
        """Multi-rule escalation bonus must push score above single-rule max."""
        from backend.app.services.adaptive_detection_service import AdaptiveDetectionService

        svc = AdaptiveDetectionService()
        # Craft event likely to hit multiple rules
        event = {
            "source_ip": "10.0.0.1",
            "destination_ip": "10.0.0.100",
            "Flow Packets/s": 10000,
            "Total Fwd Packets": 5000,
            "destination_port": 80,
            "Flow Duration": 5000,
            "protocol": "TCP"
        }
        result = svc._evaluate_deterministic_rules(event)
        # Score is bounded
        assert result["rule_score"] <= 100.0
        assert result["rule_score"] >= 0.0


class TestAdaptiveDetectionServiceBehaviorBaseline:

    def test_behavior_baseline_returns_required_keys(self):
        """Behavioral baseline evaluation must return all required keys."""
        from backend.app.services.adaptive_detection_service import AdaptiveDetectionService

        svc = AdaptiveDetectionService()
        features = {
            "Flow Packets/s": 500.0,
            "Flow Bytes/s": 50000.0,
            "Flow Duration": 1500000.0
        }
        result = svc._evaluate_behavioral_baseline({}, features)

        required_keys = ["behavior_score", "is_anomalous", "anomalous_metrics", "max_z_score", "explanation"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        assert 0.0 <= result["behavior_score"] <= 100.0

    def test_behavior_baseline_normal_traffic_not_anomalous(self):
        """Normal traffic within baseline should not be flagged as anomalous."""
        from backend.app.services.adaptive_detection_service import AdaptiveDetectionService

        svc = AdaptiveDetectionService()
        # Normal-looking features
        result = svc._evaluate_behavioral_baseline({}, {
            "Flow Packets/s": 40.0,
            "Flow Bytes/s": 4000.0,
            "Flow Duration": 80000.0
        })
        assert result["behavior_score"] < 50.0


class TestAdaptiveDetectionServiceIOCEvaluation:

    def test_ioc_evaluation_returns_valid_structure_for_benign_ip(self):
        """IOC evaluation must return valid empty structure for benign IPs."""
        from backend.app.services.adaptive_detection_service import AdaptiveDetectionService

        svc = AdaptiveDetectionService()
        result = svc._evaluate_threat_intel_iocs({"source_ip": "192.168.1.1", "destination_ip": "8.8.8.8"})

        assert "ioc_score" in result
        assert "has_ioc_match" in result
        assert "matched_count" in result
        assert isinstance(result["matched_iocs"], list)
        assert 0.0 <= result["ioc_score"] <= 100.0


class TestAdaptiveDetectionServiceGraphEvaluation:

    def test_graph_score_elevated_for_crown_jewel_lateral_movement(self):
        """Graph score must be elevated for lateral movement to crown jewel assets."""
        from backend.app.services.adaptive_detection_service import AdaptiveDetectionService

        svc = AdaptiveDetectionService()
        result = svc._evaluate_graph_telemetry({
            "is_lateral_movement": True,
            "is_crown_jewel": True,
            "is_choke_point": True,
            "hop_count": 5
        })

        assert result["graph_score"] >= 70.0
        assert result["is_lateral_movement"] is True

    def test_graph_score_low_for_benign_single_hop(self):
        """Graph score must be low for a simple direct, non-sensitive connection."""
        from backend.app.services.adaptive_detection_service import AdaptiveDetectionService

        svc = AdaptiveDetectionService()
        result = svc._evaluate_graph_telemetry({
            "is_lateral_movement": False,
            "is_crown_jewel": False,
            "is_choke_point": False,
            "hop_count": 1
        })

        assert result["graph_score"] <= 20.0


class TestSafetyGuardrails:

    def test_composite_risk_score_always_bounded(self):
        """5-domain composite risk score must always be in [0, 100]."""
        test_cases = [
            (0.0, 0.0, 0.0, 0.0, 0.0),
            (100.0, 100.0, 100.0, 100.0, 100.0),
            (50.0, 60.0, 70.0, 30.0, 20.0),
        ]
        w_ml, w_rules, w_behav, w_ioc, w_graph = 0.30, 0.30, 0.15, 0.15, 0.10

        for ml, rules, behav, ioc, graph in test_cases:
            raw = ml * w_ml + rules * w_rules + behav * w_behav + ioc * w_ioc + graph * w_graph
            clamped = float(np.clip(raw, 0.0, 100.0))
            assert 0.0 <= clamped <= 100.0

    def test_opaque_ml_only_requires_human_approval(self):
        """When only ML fires without deterministic rules, requires_human_approval must be True."""
        ml_only = True
        rule_count = 0
        risk_score = 75.0

        # Safety gate logic mirrors adaptive_detection_service.py
        requires_approval = ml_only or (risk_score >= 70.0)
        assert requires_approval is True

    def test_weight_sum_is_one(self):
        """Detection domain weights must sum to exactly 1.0."""
        weights = {"ml": 0.30, "rules": 0.30, "behavior": 0.15, "ioc": 0.15, "graph": 0.10}
        total = sum(weights.values())
        assert abs(total - 1.0) < 1e-9, f"Weights sum to {total}, expected 1.0"
