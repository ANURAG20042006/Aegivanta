"""
backend/app/services/adaptive_detection_service.py
==================================================
Phase 3.10 Advanced Adaptive ML Detection Intelligence Layer.
Unifies ML model ensemble (CatBoost, LightGBM, Random Forest, XGBoost, Decision Tree),
deterministic detection rules (authoritative), statistical behavioral baselines,
threat intelligence IOCs, and attack graph telemetry into explainable 5-domain detection scores.
Enforces safety guardrails so opaque ML outputs never trigger destructive actions without approval.
"""

import time
import math
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.config import settings
from backend.app.detection.rules.production_rules import detection_registry
from backend.app.services.ensemble_service import EnsembleThreatDetector, ConfidenceCalibrator, EnsembleStrategy
from backend.app.services.behavior_baseline_service import BehaviorBaselineEngine
from backend.app.services.threat_intel_service import GLOBAL_IOC_CACHE as fast_ioc_cache
from backend.app.services.soc_event_broadcaster import soc_broadcaster
from backend.app.services.predict_service import PredictService
from ml.dataset.cicids2017_schema import ATTACK_CLASSES
from ml.schema.feature_schema import DEFAULT_FEATURE_SCHEMA, validate_input_vector
from ml.monitoring.drift_detector import AccumulatedWindowDriftDetector

logger = logging.getLogger("SentinelAI")


class AdaptiveDetectionService:
    """
    Production-grade Adaptive ML Detection Intelligence Service.
    Coordinates multi-signal intelligence while maintaining deterministic rule authority.
    """

    _instance: Optional["AdaptiveDetectionService"] = None

    def __init__(self):
        self.ensemble_detector = EnsembleThreatDetector()
        self.drift_detector = AccumulatedWindowDriftDetector(window_size=50)
        self.weights = {
            "ml": 0.30,
            "rules": 0.30,
            "behavior": 0.15,
            "ioc": 0.15,
            "graph": 0.10
        }

    @classmethod
    def get_instance(cls) -> "AdaptiveDetectionService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _extract_ml_features(self, features_dict: Dict[str, Any]) -> Tuple[np.ndarray, List[str]]:
        """Validates and flattens input feature dictionary into scaled numpy vector."""
        is_valid, err_msg = validate_input_vector(features_dict)
        if not is_valid:
            logger.warning("Feature validation warning in adaptive detector: %s", err_msg)

        keys = list(DEFAULT_FEATURE_SCHEMA.keys())
        raw_vals = [float(features_dict.get(k, 0.0) or 0.0) for k in keys]
        return np.array(raw_vals, dtype=np.float32).reshape(1, -1), keys

    async def _evaluate_ml_ensemble(
        self,
        features_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes tree and boosting ensemble models (CatBoost, LightGBM, Random Forest, XGBoost, Decision Tree).
        Calculates calibrated probabilities, model votes, and ML score (0-100).
        """
        models_to_run = ["CatBoost", "LightGBM", "Random Forest", "Decision Tree"]
        predictions_map: Dict[str, Tuple[str, float, Dict[str, float]]] = {}
        individual_model_outputs: Dict[str, Any] = {}

        for model_name in models_to_run:
            try:
                model, preprocessor = PredictService._load_artifacts(model_name)
                df_raw = pd.DataFrame([features_dict])
                
                # Transform using preprocessor
                if hasattr(preprocessor, "transform"):
                    X_transformed = preprocessor.transform(df_raw)
                else:
                    X_transformed = np.array([[float(features_dict.get(k, 0.0) or 0.0) for k in DEFAULT_FEATURE_SCHEMA.keys()]])

                if hasattr(model, "predict_proba"):
                    probs = model.predict_proba(X_transformed)[0]
                    classes = getattr(model, "classes_", ATTACK_CLASSES)
                    class_probs = {str(c): float(p) for c, p in zip(classes, probs)}
                    pred_idx = int(np.argmax(probs))
                    pred_class = str(classes[pred_idx]) if pred_idx < len(classes) else "BENIGN"
                    max_prob = float(probs[pred_idx])
                elif hasattr(model, "predict"):
                    pred = model.predict(X_transformed)[0]
                    pred_class = str(pred)
                    max_prob = 0.90 if pred_class != "BENIGN" else 0.10
                    class_probs = {pred_class: max_prob, "BENIGN": 1.0 - max_prob}
                else:
                    pred_class = "BENIGN"
                    max_prob = 0.50
                    class_probs = {"BENIGN": 0.50}

                calibrated_conf = ConfidenceCalibrator.calibrate(max_prob)
                predictions_map[model_name] = (pred_class, calibrated_conf, class_probs)
                individual_model_outputs[model_name] = {
                    "predicted_class": pred_class,
                    "confidence": calibrated_conf,
                    "is_malicious": pred_class != "BENIGN"
                }
            except Exception as e:
                logger.debug("Model %s evaluation fallback: %s", model_name, e)
                # Fallback heuristic based on flow attributes
                fwd_pkts = float(features_dict.get("Total Fwd Packets", 0.0) or 0.0)
                bwd_pkts = float(features_dict.get("Total Backward Packets", 0.0) or 0.0)
                flow_duration = float(features_dict.get("Flow Duration", 0.0) or 0.0)
                
                fallback_class = "BENIGN"
                fallback_conf = 0.60
                if fwd_pkts > 500 or flow_duration > 1000000:
                    fallback_class = "DDoS"
                    fallback_conf = 0.85
                elif fwd_pkts > 50 and bwd_pkts == 0:
                    fallback_class = "PortScan"
                    fallback_conf = 0.80

                predictions_map[model_name] = (fallback_class, fallback_conf, {fallback_class: fallback_conf, "BENIGN": 1.0 - fallback_conf})
                individual_model_outputs[model_name] = {
                    "predicted_class": fallback_class,
                    "confidence": fallback_conf,
                    "is_malicious": fallback_class != "BENIGN",
                    "note": "heuristic_fallback"
                }

        # Aggregate ensemble
        aggregated = self.ensemble_detector.aggregate_predictions(
            predictions_map,
            strategy=EnsembleStrategy.WEIGHTED_CONFIDENCE
        )

        malicious_models = sum(1 for m, v in individual_model_outputs.items() if v["is_malicious"])
        total_models = max(len(individual_model_outputs), 1)
        model_agreement_pct = round((malicious_models / total_models) * 100.0, 1)

        # ML score calculation (0 to 100)
        top_conf = float(aggregated.get("calibrated_confidence", 0.5))
        is_attack = aggregated.get("final_prediction", "BENIGN") != "BENIGN"
        if is_attack:
            ml_score = round(top_conf * 100.0, 2)
        else:
            ml_score = round((1.0 - top_conf) * 20.0, 2)  # Low residual benign noise score

        return {
            "ml_score": float(np.clip(ml_score, 0.0, 100.0)),
            "ensemble_prediction": aggregated.get("final_prediction", "BENIGN"),
            "ensemble_confidence": float(aggregated.get("calibrated_confidence", 0.5)),
            "model_agreement_pct": model_agreement_pct,
            "individual_models": individual_model_outputs,
            "strategy": aggregated.get("ensemble_strategy", EnsembleStrategy.WEIGHTED_CONFIDENCE)
        }

    def _evaluate_deterministic_rules(
        self,
        event_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates authoritative deterministic detection rules.
        Deterministic rules are explainable and mathematically bounded.
        """
        matches = detection_registry.evaluate_all(event_dict)
        if not matches:
            return {
                "rule_score": 0.0,
                "matched_count": 0,
                "matches": [],
                "authoritative_rule": None
            }

        severity_weights = {
            "CRITICAL": 95.0,
            "HIGH": 80.0,
            "MEDIUM": 55.0,
            "LOW": 25.0,
            "INFORMATIONAL": 10.0
        }

        max_score = 0.0
        highest_rule = None
        serialized_matches = []

        for rule, details in matches:
            score = severity_weights.get(rule.severity.upper(), 50.0)
            if score > max_score:
                max_score = score
                highest_rule = rule

            serialized_matches.append({
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "severity": rule.severity,
                "attack_type": rule.attack_type,
                "mitre_technique": getattr(rule, "mitre_technique", None),
                "details": details
            })

        # Add multi-rule match escalation (up to +15.0 pts)
        escalation = min(15.0, (len(matches) - 1) * 5.0)
        final_rule_score = min(100.0, max_score + escalation)

        return {
            "rule_score": round(final_rule_score, 2),
            "matched_count": len(matches),
            "matches": serialized_matches,
            "authoritative_rule": highest_rule.name if highest_rule else None
        }

    def _evaluate_behavioral_baseline(
        self,
        event_dict: Dict[str, Any],
        features_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Computes statistical behavioral baseline deviation (Z-score & rolling standard deviations).
        """
        packet_rate = float(features_dict.get("Flow Packets/s", 0.0) or 0.0)
        byte_rate = float(features_dict.get("Flow Bytes/s", 0.0) or 0.0)
        duration = float(features_dict.get("Flow Duration", 0.0) or 0.0)

        # Baseline reference expectations for enterprise server/workstation traffic
        pkt_dev = BehaviorBaselineEngine.calculate_deviation("Flow Packets/s", packet_rate, baseline_mean=50.0, baseline_std=30.0, threshold_z=2.5)
        byte_dev = BehaviorBaselineEngine.calculate_deviation("Flow Bytes/s", byte_rate, baseline_mean=5000.0, baseline_std=3000.0, threshold_z=2.5)
        dur_dev = BehaviorBaselineEngine.calculate_deviation("Flow Duration", duration, baseline_mean=100000.0, baseline_std=50000.0, threshold_z=3.0)

        deviations = [pkt_dev, byte_dev, dur_dev]
        max_anomaly_score = max(d["anomaly_score"] for d in deviations)
        anomalous_metrics = [d["metric_name"] for d in deviations if d["is_anomalous"]]

        explanation = "; ".join(d["explanation"] for d in deviations if d["is_anomalous"])
        if not explanation:
            explanation = "All monitored flow metrics are within normal statistical behavioral baselines."

        return {
            "behavior_score": round(max_anomaly_score, 2),
            "is_anomalous": len(anomalous_metrics) > 0,
            "anomalous_metrics": anomalous_metrics,
            "max_z_score": max(d["z_score"] for d in deviations),
            "explanation": explanation,
            "metrics": {d["metric_name"]: d for d in deviations}
        }

    def _evaluate_threat_intel_iocs(
        self,
        event_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Checks real-time Fast IOC Cache for source IP, destination IP, domains, and hashes.
        """
        src_ip = event_dict.get("source_ip") or event_dict.get("src_ip")
        dst_ip = event_dict.get("destination_ip") or event_dict.get("dst_ip")
        domain = event_dict.get("domain") or event_dict.get("hostname")
        file_hash = event_dict.get("file_hash") or event_dict.get("sha256")

        matched_iocs = []
        max_ioc_score = 0.0

        # IP lookups
        for ip_val in filter(None, [src_ip, dst_ip]):
            ip_str = str(ip_val).strip()
            if not ip_str:
                continue
            match = fast_ioc_cache.match_ip(ip_str)
            if match:
                conf = float(match.get("confidence", 80.0) or 80.0)
                severity = match.get("severity", "HIGH").upper()
                sev_mult = 1.0 if severity == "CRITICAL" else (0.85 if severity == "HIGH" else 0.6)
                score = min(100.0, conf * sev_mult)
                if score > max_ioc_score:
                    max_ioc_score = score
                matched_iocs.append({
                    "value": ip_str,
                    "type": "ip",
                    "feed": match.get("feed_name", "ThreatIntel"),
                    "severity": severity,
                    "threat_type": match.get("threat_type", "Malicious Indicator")
                })

        # Domain / hash lookups
        for indicator_val, indicator_type in [(domain, "domain"), (file_hash, "hash")]:
            if not indicator_val:
                continue
            ioc_str = str(indicator_val).strip()
            if not ioc_str:
                continue
            match = fast_ioc_cache.match_domain_or_hash(ioc_str)
            if match:
                conf = float(match.get("confidence", 80.0) or 80.0)
                severity = match.get("severity", "HIGH").upper()
                sev_mult = 1.0 if severity == "CRITICAL" else (0.85 if severity == "HIGH" else 0.6)
                score = min(100.0, conf * sev_mult)
                if score > max_ioc_score:
                    max_ioc_score = score
                matched_iocs.append({
                    "value": ioc_str,
                    "type": indicator_type,
                    "feed": match.get("feed_name", "ThreatIntel"),
                    "severity": severity,
                    "threat_type": match.get("threat_type", "Malicious Indicator")
                })

        return {
            "ioc_score": round(max_ioc_score, 2),
            "has_ioc_match": len(matched_iocs) > 0,
            "matched_count": len(matched_iocs),
            "matched_iocs": matched_iocs
        }

    def _evaluate_graph_telemetry(
        self,
        event_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates graph proximity, lateral movement telemetry, and crown jewel exposure.
        """
        is_lateral = bool(event_dict.get("is_lateral_movement", False))
        hop_count = int(event_dict.get("hop_count", 1) or 1)
        is_crown_jewel = bool(event_dict.get("is_crown_jewel", False))
        choke_point = bool(event_dict.get("is_choke_point", False))

        graph_score = 0.0
        factors = []

        if is_crown_jewel:
            graph_score += 45.0
            factors.append("Target is a Crown-Jewel Asset")
        if is_lateral:
            graph_score += 35.0
            factors.append("Multi-hop lateral movement detected")
        if choke_point:
            graph_score += 20.0
            factors.append("Critical choke point traversed")
        if hop_count > 2:
            graph_score += min(20.0, hop_count * 5.0)
            factors.append(f"Traversed {hop_count} hops across attack path")

        return {
            "graph_score": round(min(100.0, graph_score), 2),
            "is_lateral_movement": is_lateral,
            "hop_count": hop_count,
            "is_crown_jewel": is_crown_jewel,
            "factors": factors
        }

    async def detect_adaptive_flow(
        self,
        features_dict: Dict[str, Any],
        context_event: Optional[Dict[str, Any]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Executes unified 5-domain adaptive threat detection.
        Synthesizes:
          - ML Score
          - Rule Score
          - Behavior Score
          - IOC Score
          - Graph Score
        into an explainable final confidence and risk rating with safety guardrails.
        """
        start_time = time.perf_counter()
        event_ctx = context_event or {}
        
        # 1. Multi-Model ML Ensemble
        ml_eval = await self._evaluate_ml_ensemble(features_dict)
        
        # 2. Authoritative Deterministic Rules
        # Merge telemetry fields into event dict for rule evaluation
        merged_event = {**features_dict, **event_ctx}
        rules_eval = self._evaluate_deterministic_rules(merged_event)
        
        # 3. Statistical Behavioral Baselines
        behavior_eval = self._evaluate_behavioral_baseline(merged_event, features_dict)
        
        # 4. Threat Intel IOC Matches
        ioc_eval = self._evaluate_threat_intel_iocs(merged_event)
        
        # 5. Attack Graph & Lateral Movement Telemetry
        graph_eval = self._evaluate_graph_telemetry(merged_event)

        # Domain Scores
        ml_score = ml_eval["ml_score"]
        rule_score = rules_eval["rule_score"]
        behavior_score = behavior_eval["behavior_score"]
        ioc_score = ioc_eval["ioc_score"]
        graph_score = graph_eval["graph_score"]

        # Synthesize Weighted Explainable Risk Score (0-100)
        # If deterministic rule matched with high confidence, give rule score higher weighting
        if rules_eval["matched_count"] > 0:
            w_ml, w_rules, w_behav, w_ioc, w_graph = 0.20, 0.40, 0.15, 0.15, 0.10
        elif ioc_eval["has_ioc_match"]:
            w_ml, w_rules, w_behav, w_ioc, w_graph = 0.25, 0.15, 0.15, 0.35, 0.10
        else:
            w_ml, w_rules, w_behav, w_ioc, w_graph = self.weights["ml"], self.weights["rules"], self.weights["behavior"], self.weights["ioc"], self.weights["graph"]

        composite_risk_score = (
            ml_score * w_ml +
            rule_score * w_rules +
            behavior_score * w_behav +
            ioc_score * w_ioc +
            graph_score * w_graph
        )
        composite_risk_score = round(float(np.clip(composite_risk_score, 0.0, 100.0)), 2)

        # Calibrated Final Confidence (0.0 to 1.0)
        if rules_eval["matched_count"] > 0 or ioc_eval["has_ioc_match"]:
            # High certainty due to deterministic / IOC signature
            raw_conf = max(ml_eval["ensemble_confidence"], 0.85)
        elif composite_risk_score >= 60.0:
            raw_conf = ml_eval["ensemble_confidence"]
        else:
            raw_conf = max(0.10, composite_risk_score / 100.0)

        final_confidence = round(float(np.clip(raw_conf, 0.0, 1.0)), 4)

        # Final Threat Verdict
        if rules_eval["matches"]:
            final_attack_type = rules_eval["matches"][0]["attack_type"]
            is_malicious = True
        elif ioc_eval["has_ioc_match"]:
            final_attack_type = ioc_eval["matched_iocs"][0]["threat_type"]
            is_malicious = True
        elif ml_eval["ensemble_prediction"] != "BENIGN":
            final_attack_type = ml_eval["ensemble_prediction"]
            is_malicious = True
        elif behavior_eval["is_anomalous"] and behavior_score >= 50.0:
            final_attack_type = "Statistical Anomaly"
            is_malicious = True
        else:
            final_attack_type = "BENIGN"
            is_malicious = False

        # Severity Mapping
        if composite_risk_score >= 80.0:
            severity = "CRITICAL"
        elif composite_risk_score >= 60.0:
            severity = "HIGH"
        elif composite_risk_score >= 35.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Model Safety Guardrail:
        # Destructive autonomous actions (host isolation, account disablement) MUST NEVER be triggered
        # purely by opaque ML without deterministic rule or human approval gate.
        is_opaque_ml_only = (ml_eval["ensemble_prediction"] != "BENIGN" and rules_eval["matched_count"] == 0 and not ioc_eval["has_ioc_match"])
        requires_human_approval = is_opaque_ml_only or (composite_risk_score >= 70.0 and severity == "CRITICAL")

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # Feed observation into drift detector
        vec, feature_names = self._extract_ml_features(features_dict)
        self.drift_detector.add_observation(
            feature_vector=vec,
            predicted_class=final_attack_type
        )

        return {
            "detection_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_malicious": is_malicious,
            "attack_type": final_attack_type,
            "severity": severity,
            "risk_score": composite_risk_score,
            "final_confidence": final_confidence,
            "latency_ms": latency_ms,
            "scores": {
                "ml_score": ml_score,
                "rule_score": rule_score,
                "behavior_score": behavior_score,
                "ioc_score": ioc_score,
                "graph_score": graph_score
            },
            "weights_applied": {
                "ml": w_ml,
                "rules": w_rules,
                "behavior": w_behav,
                "ioc": w_ioc,
                "graph": w_graph
            },
            "safety_guardrails": {
                "requires_human_approval": requires_human_approval,
                "is_opaque_ml_only": is_opaque_ml_only,
                "deterministic_rule_matched": rules_eval["matched_count"] > 0,
                "ioc_matched": ioc_eval["has_ioc_match"],
                "policy_mode": "GOVERNED_EXECUTION"
            },
            "telemetry_breakdown": {
                "ml_ensemble": ml_eval,
                "deterministic_rules": rules_eval,
                "behavioral_baseline": behavior_eval,
                "threat_intel": ioc_eval,
                "attack_graph": graph_eval
            }
        }


adaptive_detection_service = AdaptiveDetectionService.get_instance()
