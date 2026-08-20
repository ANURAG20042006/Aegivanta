"""
backend/app/services/detection_correlation_service.py
=====================================================
Phase 3.6 Detection Correlation Engine.
Correlates security telemetry events, evaluates detection rules, enforces sliding temporal windows,
and groups related security signals into actionable, evidence-backed correlation clusters.
"""

from datetime import datetime, timezone, timedelta
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict

from backend.app.detection.rules.production_rules import detection_registry
from backend.app.services.risk_scoring_service import RiskScoringService

logger = logging.getLogger("SentinelAI")


class DetectionCorrelationEngine:
    """
    Continuous detection correlation engine that correlates security events,
    evaluates modular detection rules, manages temporal correlation windows,
    and aggregates multi-signal incident evidence.
    """

    def __init__(self, default_window_minutes: int = 15):
        self.default_window_minutes = default_window_minutes
        # In-memory sliding window cache: correlation_key -> List[event_dict]
        self._correlation_windows: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # Processed event set for idempotency: event_id -> processed_timestamp
        self._processed_events: Set[str] = set()

    def _generate_correlation_key(self, event: Dict[str, Any]) -> str:
        """
        Generates deterministic grouping key based on primary correlation signals:
        1. Explicit correlation_id if provided
        2. (source_ip, destination_ip)
        3. Matched IOC indicator
        4. User identity
        """
        if event.get("correlation_id"):
            return str(event["correlation_id"])
        
        src = (event.get("source_ip") or event.get("src_ip") or "0.0.0.0").strip()
        dst = (event.get("destination_ip") or event.get("dst_ip") or "0.0.0.0").strip()
        user = event.get("user_id") or event.get("username")
        
        matched_iocs = event.get("matched_iocs") or []
        if matched_iocs:
            ioc_val = matched_iocs[0].get("value")
            if ioc_val:
                return f"ioc_{ioc_val}"

        if user:
            return f"user_{user}_{src}"

        return f"flow_{src}_{dst}"

    def correlate_event(
        self,
        event: Dict[str, Any],
        window_minutes: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Ingests a single telemetry event, evaluates detection rules, correlates across
        the active temporal window, and returns a correlated detection bundle.
        """
        event_id = event.get("id") or event.get("event_id") or str(uuid.uuid4())
        
        # 1. Idempotency check: Skip duplicate events
        if event_id in self._processed_events:
            logger.debug("Skipping duplicate event ID: %s", event_id)
            return None
        self._processed_events.add(event_id)

        # 2. Parse event timestamp
        ts = event.get("timestamp")
        if isinstance(ts, str):
            try:
                ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                ts_dt = datetime.now(timezone.utc)
        elif isinstance(ts, datetime):
            ts_dt = ts
        else:
            ts_dt = datetime.now(timezone.utc)

        normalized_event = dict(event)
        normalized_event["id"] = event_id
        normalized_event["timestamp_dt"] = ts_dt

        # 3. Evaluate Modular Detection Rules
        rule_matches = detection_registry.evaluate_all(normalized_event)
        is_malicious = bool(normalized_event.get("is_malicious", False)) or len(rule_matches) > 0
        normalized_event["is_malicious"] = is_malicious
        normalized_event["rule_matches"] = rule_matches

        # If completely benign and no rule matched, store in window but don't elevate to incident
        key = self._generate_correlation_key(normalized_event)
        win_size = window_minutes or self.default_window_minutes
        cutoff = ts_dt - timedelta(minutes=win_size)

        # 4. Update sliding window & prune expired events
        window = self._correlation_windows[key]
        window.append(normalized_event)
        # Keep only events within window
        window = [ev for ev in window if ev["timestamp_dt"] >= cutoff]
        self._correlation_windows[key] = window

        # If malicious or rules triggered, build correlated detection bundle
        if is_malicious or len(rule_matches) > 0:
            return self._build_correlation_bundle(key, window)

        return None

    def _build_correlation_bundle(self, key: str, window: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates window events into a correlated detection cluster."""
        events_sorted = sorted(window, key=lambda x: x["timestamp_dt"])
        first_seen = events_sorted[0]["timestamp_dt"]
        last_seen = events_sorted[-1]["timestamp_dt"]

        event_ids = [ev["id"] for ev in events_sorted]
        
        # Aggregate entities
        entities: Set[str] = set()
        techniques: Set[str] = set()
        matched_rules: Dict[str, str] = {}
        ioc_matches: List[Dict[str, Any]] = []

        max_conf = 0.50
        highest_sev_rank = 1
        sev_ranking = {"INFORMATIONAL": 1, "LOW": 2, "MEDIUM": 3, "HIGH": 4, "CRITICAL": 5}
        rank_to_sev = {1: "INFORMATIONAL", 2: "LOW", 3: "MEDIUM", 4: "HIGH", 5: "CRITICAL"}

        for ev in events_sorted:
            if ev.get("source_ip"):
                entities.add(ev["source_ip"])
            if ev.get("destination_ip"):
                entities.add(ev["destination_ip"])
            if ev.get("user_id"):
                entities.add(f"user:{ev['user_id']}")
            if ev.get("asset_id"):
                entities.add(f"asset:{ev['asset_id']}")

            # Collect techniques and rule matches
            for rm in ev.get("rule_matches", []):
                matched_rules[rm["rule_id"]] = rm["rule_name"]
                techniques.update(rm.get("mitre_techniques", []))
                conf = float(rm.get("confidence", 0.85))
                if conf > max_conf:
                    max_conf = conf
                sev = rm.get("severity", "MEDIUM").upper()
                if sev_ranking.get(sev, 3) > highest_sev_rank:
                    highest_sev_rank = sev_ranking.get(sev, 3)

            # Check ML confidence
            ml_conf = float(ev.get("confidence") or ev.get("confidence_score") or 0.80)
            if ml_conf > max_conf:
                max_conf = ml_conf

            ml_sev = str(ev.get("severity", "MEDIUM")).upper()
            if sev_ranking.get(ml_sev, 3) > highest_sev_rank:
                highest_sev_rank = sev_ranking.get(ml_sev, 3)

            if ev.get("matched_iocs"):
                ioc_matches.extend(ev["matched_iocs"])

        overall_sev = rank_to_sev.get(highest_sev_rank, "HIGH")

        # 5. Calculate Deterministic Risk Score
        risk_score, risk_band, risk_components = RiskScoringService.calculate_incident_risk(
            severity=overall_sev,
            confidence=max_conf,
            ioc_match_count=len(ioc_matches),
            max_ioc_confidence=max([float(i.get("confidence", 0.9)) for i in ioc_matches], default=0.0),
            asset_criticality=events_sorted[-1].get("asset_criticality", "MEDIUM"),
            affected_asset_count=len([e for e in entities if e.startswith("asset:")]),
            event_count=len(events_sorted),
            has_lateral_movement=bool(events_sorted[-1].get("is_lateral_movement")),
            crown_jewel_index=float(events_sorted[-1].get("crown_jewel_exposure_index", 0.0))
        )

        correlation_id = f"CORR-{uuid.uuid4().hex[:8].upper()}"
        primary_attack_type = events_sorted[-1].get("attack_type") or (list(matched_rules.values())[0] if matched_rules else "Correlated Threat Activity")

        return {
            "correlation_id": correlation_id,
            "correlation_key": key,
            "event_ids": event_ids,
            "event_count": len(events_sorted),
            "first_seen": first_seen.isoformat(),
            "last_seen": last_seen.isoformat(),
            "entities": list(entities),
            "attack_type": primary_attack_type,
            "mitre_techniques": list(techniques),
            "matched_rules": [{"rule_id": k, "rule_name": v} for k, v in matched_rules.items()],
            "confidence": round(max_conf, 4),
            "severity": overall_sev,
            "risk_score": risk_score,
            "risk_band": risk_band,
            "risk_components": risk_components,
            "source_ip": events_sorted[-1].get("source_ip", "0.0.0.0"),
            "destination_ip": events_sorted[-1].get("destination_ip", "0.0.0.0"),
            "destination_port": int(events_sorted[-1].get("destination_port", 0) or 0),
            "protocol": events_sorted[-1].get("protocol", "TCP"),
            "asset_id": events_sorted[-1].get("asset_id"),
            "detection_reason": f"Correlated {len(events_sorted)} events matching {len(matched_rules)} detection rules across window."
        }

    def correlate_batch(
        self,
        events: List[Dict[str, Any]],
        window_minutes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Batch correlation across a chronological sequence of events."""
        bundles = []
        for ev in events:
            bundle = self.correlate_event(ev, window_minutes=window_minutes)
            if bundle:
                bundles.append(bundle)
        return bundles

    def reset(self):
        """Resets the in-memory window cache (for testing isolation)."""
        self._correlation_windows.clear()
        self._processed_events.clear()


# Global correlation engine instance
correlation_engine = DetectionCorrelationEngine()
