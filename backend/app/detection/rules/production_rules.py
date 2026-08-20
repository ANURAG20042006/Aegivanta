"""
backend/app/detection/rules/production_rules.py
================================================
Phase 3.6 Production Detection Rules (RULE-001 through RULE-010).
Deterministic, evidence-backed security detection rules mapped to MITRE ATT&CK techniques.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import math

from backend.app.detection.rules.base import DetectionRule


class RuleRepeatedAuthFailures(DetectionRule):
    """RULE-001: Repeated authentication failures from a single source."""
    rule_id = "RULE-001"
    name = "Repeated Authentication Failures"
    description = "Detects multiple failed authentication attempts exceeding the brute-force threshold."
    severity = "HIGH"
    mitre_techniques = ["T1110.001", "T1110.003"]  # Password Guessing, Password Spraying

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        att_type = str(event.get("attack_type", "")).upper()
        fail_count = int(event.get("auth_failures", 0) or (context.get("auth_failures", 0) if context else 0))
        is_auth_attack = "BRUTE" in att_type or "AUTH" in att_type or event.get("event_type") == "AUTH_FAILURE"

        if is_auth_attack or fail_count >= 5:
            conf = min(0.60 + (fail_count * 0.05), 0.98) if fail_count > 0 else 0.88
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": conf,
                "severity": self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"Observed {max(fail_count, 5)} repeated authentication failures from {event.get('source_ip')}.",
                "evidence": {
                    "source_ip": event.get("source_ip"),
                    "destination_ip": event.get("destination_ip"),
                    "failure_count": max(fail_count, 5),
                    "attack_type": event.get("attack_type")
                }
            }
        return None


class RuleImpossibleAuthPattern(DetectionRule):
    """RULE-002: Impossible authentication pattern / concurrent geographically dispersed logins."""
    rule_id = "RULE-002"
    name = "Impossible Authentication Pattern"
    description = "Detects rapid authentications for the same user across impossible geographic or network distances."
    severity = "CRITICAL"
    mitre_techniques = ["T1078.004", "T1078"]  # Valid Accounts: Cloud Accounts

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        is_impossible = bool(event.get("impossible_travel") or (context and context.get("impossible_travel")))
        speed_kmh = float(event.get("calculated_travel_speed_kmh", 0.0) or (context.get("travel_speed_kmh", 0.0) if context else 0.0))

        if is_impossible or speed_kmh > 1000.0:
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": 0.95,
                "severity": self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"User {event.get('user_id', 'unknown')} logged in from disparate locations within impossible transit window ({speed_kmh:.1f} km/h).",
                "evidence": {
                    "user_id": event.get("user_id"),
                    "source_ip": event.get("source_ip"),
                    "speed_kmh": speed_kmh,
                    "locations": event.get("locations", [])
                }
            }
        return None


class RuleIOCMatchedTelemetry(DetectionRule):
    """RULE-003: Active threat intelligence indicator matched in flow telemetry."""
    rule_id = "RULE-003"
    name = "IOC Matched Against Telemetry"
    description = "Matches network flow endpoints against verified Threat Intelligence IOC feeds."
    severity = "HIGH"
    mitre_techniques = ["T1071.001", "T1566"]  # Web Protocols, Phishing

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        has_ti_match = bool(event.get("threat_intel_match") or event.get("matched_iocs") or (context and context.get("matched_iocs")))
        matched_iocs = event.get("matched_iocs") or (context.get("matched_iocs") if context else [])

        if has_ti_match or len(matched_iocs) > 0:
            top_ioc = matched_iocs[0] if matched_iocs else {}
            ioc_val = top_ioc.get("value") or event.get("destination_ip") or event.get("source_ip")
            ioc_sev = top_ioc.get("severity", "HIGH")
            ioc_conf = float(top_ioc.get("confidence", 0.90))

            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": ioc_conf,
                "severity": ioc_sev if ioc_sev in ["CRITICAL", "HIGH"] else self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"Telemetry matched known malicious indicator: {ioc_val}.",
                "evidence": {
                    "matched_indicator": ioc_val,
                    "threat_type": top_ioc.get("threat_type", "C2_SERVER"),
                    "feed_source": top_ioc.get("feed_name", "SentinelAI Threat Intelligence Feed"),
                    "source_ip": event.get("source_ip"),
                    "destination_ip": event.get("destination_ip")
                }
            }
        return None


class RuleSuspiciousLateralMovement(DetectionRule):
    """RULE-004: Suspicious lateral movement sequence across internal administrative ports."""
    rule_id = "RULE-004"
    name = "Suspicious Lateral Movement Sequence"
    description = "Detects unauthorized lateral traversal over administrative protocols (SMB, RDP, SSH, WinRM)."
    severity = "HIGH"
    mitre_techniques = ["T1021.002", "T1021.001", "T1021.004", "T1021.006"]

    LATERAL_PORTS = {445, 139, 3389, 22, 5985, 5986, 135}

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        dst_port = int(event.get("destination_port") or event.get("dst_port") or 0)
        is_lateral_flag = bool(event.get("is_lateral_movement") or (context and context.get("is_lateral_movement")))
        is_mal = bool(event.get("is_malicious", False))

        if (dst_port in self.LATERAL_PORTS and is_mal) or is_lateral_flag:
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": 0.90,
                "severity": "CRITICAL" if dst_port in [445, 3389] else self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"Suspicious administrative protocol pivot on port {dst_port} between {event.get('source_ip')} and {event.get('destination_ip')}.",
                "evidence": {
                    "source_ip": event.get("source_ip"),
                    "destination_ip": event.get("destination_ip"),
                    "port": dst_port,
                    "protocol": event.get("protocol", "TCP")
                }
            }
        return None


class RuleHighRiskMultiHopAttackPath(DetectionRule):
    """RULE-005: High-risk multi-hop attack path."""
    rule_id = "RULE-005"
    name = "High-Risk Multi-Hop Attack Path"
    description = "Detects correlated attack trajectories spanning 3 or more consecutive internal network hops."
    severity = "CRITICAL"
    mitre_techniques = ["T1021", "T1570"]  # Remote Services, Lateral Tool Transfer

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        hop_count = int(event.get("hop_count", 0) or (context.get("hop_count", 0) if context else 0))
        cum_risk = float(event.get("cumulative_risk_score", 0.0) or (context.get("cumulative_risk_score", 0.0) if context else 0.0))

        if hop_count >= 3 or (hop_count >= 2 and cum_risk >= 80.0):
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": 0.94,
                "severity": self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"Detected multi-hop attack trajectory spanning {hop_count} hops with cumulative risk {cum_risk:.1f}%.",
                "evidence": {
                    "hop_count": hop_count,
                    "cumulative_risk": cum_risk,
                    "node_sequence": event.get("node_sequence") or (context.get("node_sequence") if context else [])
                }
            }
        return None


class RuleCrownJewelExposure(DetectionRule):
    """RULE-006: Crown-jewel asset exposure through attack graph."""
    rule_id = "RULE-006"
    name = "Crown-Jewel Asset Exposure"
    description = "Identifies attack paths or compromised nodes within immediate reachability of Tier-1 Crown Jewel assets."
    severity = "CRITICAL"
    mitre_techniques = ["T1087", "T1078.001"]  # Account Discovery, Database Credentials

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        crown_jewel_index = float(event.get("crown_jewel_exposure_index", 0.0) or (context.get("crown_jewel_exposure_index", 0.0) if context else 0.0))
        critical_assets_exposed = int(event.get("critical_assets_exposed", 0) or (context.get("critical_assets_exposed", 0) if context else 0))

        if crown_jewel_index >= 50.0 or critical_assets_exposed >= 1:
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": 0.96,
                "severity": self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"Critical Crown Jewel assets exposed in blast radius (Exposure Index: {crown_jewel_index:.1f}).",
                "evidence": {
                    "crown_jewel_exposure_index": crown_jewel_index,
                    "critical_assets_count": critical_assets_exposed,
                    "origin_node": event.get("origin_node_id") or event.get("source_ip")
                }
            }
        return None


class RuleAbnormalOutboundConnection(DetectionRule):
    """RULE-007: Abnormal outbound high-volume connection pattern."""
    rule_id = "RULE-007"
    name = "Abnormal Outbound Connection Pattern"
    description = "Detects anomalous high-volume or long-duration outbound egress indicative of data exfiltration or C2 beaconing."
    severity = "HIGH"
    mitre_techniques = ["T1048", "T1041"]  # Exfiltration Over Alternative Protocol, Exfiltration Over C2

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        duration = float(event.get("flow_duration", 0.0))
        bytes_sent = float(event.get("total_bytes", 0.0) or event.get("packet_length", 0.0))
        is_exfil = "EXFIL" in str(event.get("attack_type", "")).upper() or bool(event.get("is_outbound_anomaly"))

        if is_exfil or (duration > 3600.0 and bytes_sent > 10_000_000):
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": 0.87,
                "severity": self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"Abnormal outbound flow detected: duration={duration:.1f}s, bytes={bytes_sent:.0f}.",
                "evidence": {
                    "source_ip": event.get("source_ip"),
                    "destination_ip": event.get("destination_ip"),
                    "flow_duration": duration,
                    "bytes_transferred": bytes_sent
                }
            }
        return None


class RulePotentialCredentialAbuse(DetectionRule):
    """RULE-008: Potential credential abuse or privilege escalation."""
    rule_id = "RULE-008"
    name = "Potential Credential Abuse"
    description = "Detects Kerberos pass-the-ticket, token manipulation, or abnormal administrative credential pivoting."
    severity = "CRITICAL"
    mitre_techniques = ["T1558", "T1078"]  # Steal or Forge Kerberos Tickets, Valid Accounts

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        port = int(event.get("destination_port", 0) or 0)
        att_type = str(event.get("attack_type", "")).upper()
        is_cred_abuse = "KERBEROS" in att_type or "CREDENTIAL" in att_type or port == 88

        if is_cred_abuse and bool(event.get("is_malicious", False)):
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": 0.92,
                "severity": self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"Detected potential Kerberos ticket or credential manipulation on port {port}.",
                "evidence": {
                    "port": port,
                    "attack_type": event.get("attack_type"),
                    "source_ip": event.get("source_ip"),
                    "destination_ip": event.get("destination_ip")
                }
            }
        return None


class RuleRepeatedPolicyViolation(DetectionRule):
    """RULE-009: Repeated security policy violation or unauthorized port probing."""
    rule_id = "RULE-009"
    name = "Repeated Security Policy Violation"
    description = "Detects systematic unauthorized port scanning or policy rule infractions across protected subnets."
    severity = "MEDIUM"
    mitre_techniques = ["T1046", "T1595.001"]  # Network Service Discovery, Active Scanning

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        att_type = str(event.get("attack_type", "")).upper()
        is_scan = "PORTSCAN" in att_type or "PROBE" in att_type or "SCAN" in att_type

        if is_scan:
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": 0.85,
                "severity": self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"Unauthorized network scanning/reconnaissance detected from {event.get('source_ip')}.",
                "evidence": {
                    "source_ip": event.get("source_ip"),
                    "destination_ip": event.get("destination_ip"),
                    "attack_type": event.get("attack_type")
                }
            }
        return None


class RuleHighVelocityEventBurst(DetectionRule):
    """RULE-010: High-velocity suspicious event burst / Denial of Service."""
    rule_id = "RULE-010"
    name = "High-Velocity Suspicious Event Burst"
    description = "Detects abnormal packet volume bursts indicative of DoS/DDoS or automated exploit floods."
    severity = "HIGH"
    mitre_techniques = ["T1498", "T1499"]  # Network Denial of Service, Endpoint DoS

    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        att_type = str(event.get("attack_type", "")).upper()
        is_dos = "DOS" in att_type or "DDOS" in att_type or "FLOOD" in att_type
        rate = float(event.get("flow_rate_packets_per_sec", 0.0) or (context.get("rate_pps", 0.0) if context else 0.0))

        if is_dos or rate > 1000.0:
            return {
                "rule_id": self.rule_id,
                "rule_name": self.name,
                "matched": True,
                "confidence": 0.95,
                "severity": "CRITICAL" if "DDOS" in att_type else self.severity,
                "mitre_techniques": self.mitre_techniques,
                "description": f"High-velocity event burst / Denial of Service detected from {event.get('source_ip')}.",
                "evidence": {
                    "attack_type": event.get("attack_type"),
                    "source_ip": event.get("source_ip"),
                    "destination_ip": event.get("destination_ip"),
                    "rate_pps": rate
                }
            }
        return None


class DetectionRuleRegistry:
    """Registry maintaining active production detection rules."""

    def __init__(self):
        self._rules: Dict[str, DetectionRule] = {
            "RULE-001": RuleRepeatedAuthFailures(),
            "RULE-002": RuleImpossibleAuthPattern(),
            "RULE-003": RuleIOCMatchedTelemetry(),
            "RULE-004": RuleSuspiciousLateralMovement(),
            "RULE-005": RuleHighRiskMultiHopAttackPath(),
            "RULE-006": RuleCrownJewelExposure(),
            "RULE-007": RuleAbnormalOutboundConnection(),
            "RULE-008": RulePotentialCredentialAbuse(),
            "RULE-009": RuleRepeatedPolicyViolation(),
            "RULE-010": RuleHighVelocityEventBurst(),
        }

    def get_all_rules(self) -> List[DetectionRule]:
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> Optional[DetectionRule]:
        return self._rules.get(rule_id)

    def evaluate_all(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Evaluates all registered rules against the event and returns all positive matches."""
        matches = []
        for rule in self._rules.values():
            match = rule.evaluate(event, context)
            if match and match.get("matched"):
                matches.append(match)
        return matches


# Global instance
detection_registry = DetectionRuleRegistry()
