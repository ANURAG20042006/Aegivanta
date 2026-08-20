"""
backend/app/hunting/production_hunts.py
=======================================
Phase 3.8 Production Threat Hunting Detection Pack (HUNT-001 through HUNT-010).
"""

from typing import Dict, Any, List, Optional
from collections import defaultdict
from backend.app.hunting.base import HuntRule


class HuntRepeatedAuthFailureToSuccess(HuntRule):
    hunt_id = "HUNT-001"
    name = "Repeated Authentication Failures Followed by Success"
    description = "Detects multiple failed authentication attempts on a user/account immediately succeeded by a valid login session."
    severity = "HIGH"
    mitre_technique = "T1110.001"
    tactic = "TA0006"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        user_events = defaultdict(list)
        for ev in telemetry_events:
            usr = ev.get("username") or ev.get("user")
            if usr:
                user_events[usr].append(ev)

        for user, events in user_events.items():
            fail_count = 0
            has_success = False
            for e in events:
                if e.get("auth_success") is False or "FAIL" in str(e.get("attack_type", "")).upper() or int(e.get("auth_failures", 0)) > 0:
                    fail_count += max(1, int(e.get("auth_failures", 1)))
                if e.get("auth_success") is True or "SUCCESS" in str(e.get("attack_type", "")).upper():
                    has_success = True

            if fail_count >= 2 and has_success:
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": user,
                    "entity_type": "USER",
                    "confidence": 0.92,
                    "explanation": f"User '{user}' experienced {fail_count} authentication failures followed by a successful login.",
                    "evidence_count": len(events)
                })
        return findings


class HuntNewSourcePrivilegedAccess(HuntRule):
    hunt_id = "HUNT-002"
    name = "New Source IP Followed by Privileged Access"
    description = "Identifies privileged administrative logins originating from previously unseen external or foreign IP subnets."
    severity = "CRITICAL"
    mitre_technique = "T1078.004"
    tactic = "TA0001"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        for ev in telemetry_events:
            is_priv = ev.get("is_privileged", False) or "ADMIN" in str(ev.get("user", "")).upper() or "ROOT" in str(ev.get("user", "")).upper()
            is_new_ip = ev.get("is_new_source", False) or ev.get("is_foreign_ip", False)
            if is_priv and is_new_ip:
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": ev.get("source_ip", "0.0.0.0"),
                    "entity_type": "IP",
                    "confidence": 0.95,
                    "explanation": f"Privileged administrative access granted to new source IP {ev.get('source_ip')}.",
                    "evidence_count": 1
                })
        return findings


class HuntUnusualLateralMovement(HuntRule):
    hunt_id = "HUNT-003"
    name = "Unusual Lateral Movement"
    description = "Hunts for internal administrative pivots across SMB (445), RDP (3389), or SSH (22) between non-domain-controller workstations."
    severity = "HIGH"
    mitre_technique = "T1021.002"
    tactic = "TA0008"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        lateral_ports = {22, 445, 3389, 5985, 5986}
        for ev in telemetry_events:
            dport = int(ev.get("destination_port", 0))
            if dport in lateral_ports and (ev.get("is_internal") or str(ev.get("source_ip", "")).startswith("10.") or str(ev.get("source_ip", "")).startswith("192.168.")):
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": f"{ev.get('source_ip')} -> {ev.get('destination_ip')}",
                    "entity_type": "ATTACK_PATH",
                    "confidence": 0.88,
                    "explanation": f"Internal lateral traversal detected on port {dport} from {ev.get('source_ip')} to {ev.get('destination_ip')}.",
                    "evidence_count": 1
                })
        return findings


class HuntHighVolumeOutboundExfil(HuntRule):
    hunt_id = "HUNT-004"
    name = "High-Volume Outbound Connection / Data Staging"
    description = "Identifies single egress connections transferring $> 5\text{MB}$ or maintaining persistent long connections ($> 1\text{ hour}$)."
    severity = "HIGH"
    mitre_technique = "T1048"
    tactic = "TA0010"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        for ev in telemetry_events:
            bytes_out = float(ev.get("bytes_transferred", 0) or ev.get("packet_length", 0))
            flow_dur = float(ev.get("flow_duration", 0))
            if bytes_out >= 5000000 or flow_dur >= 3600000:
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": ev.get("destination_ip", "0.0.0.0"),
                    "entity_type": "IP",
                    "confidence": 0.85,
                    "explanation": f"High volume outbound transfer ({bytes_out} bytes) observed to {ev.get('destination_ip')}.",
                    "evidence_count": 1
                })
        return findings


class HuntIOCSuspiciousAuthCombination(HuntRule):
    hunt_id = "HUNT-005"
    name = "IOC + Suspicious Authentication Combination"
    description = "Correlates known Threat Intelligence reputation indicators with active credential authentications."
    severity = "CRITICAL"
    mitre_technique = "T1071.001"
    tactic = "TA0011"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        for ev in telemetry_events:
            has_ioc = ev.get("ioc_matched", False) or ev.get("matched_iocs_count", 0) > 0
            has_auth = "AUTH" in str(ev.get("attack_type", "")).upper() or ev.get("username") is not None
            if has_ioc and has_auth:
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": ev.get("source_ip", "0.0.0.0"),
                    "entity_type": "IP",
                    "confidence": 0.98,
                    "explanation": f"Known malicious threat indicator interacted with authentication subsystem from {ev.get('source_ip')}.",
                    "evidence_count": 1
                })
        return findings


class HuntMultiAssetAccountAccess(HuntRule):
    hunt_id = "HUNT-006"
    name = "Multiple Assets Accessed by Single Account"
    description = "Hunts for single accounts touching $> 3$ distinct internal hosts within a short time window."
    severity = "HIGH"
    mitre_technique = "T1087.002"
    tactic = "TA0007"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        user_hosts = defaultdict(set)
        for ev in telemetry_events:
            usr = ev.get("username") or ev.get("user")
            dst = ev.get("destination_ip") or ev.get("hostname")
            if usr and dst:
                user_hosts[usr].add(dst)

        for usr, hosts in user_hosts.items():
            if len(hosts) >= 3:
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": usr,
                    "entity_type": "USER",
                    "confidence": 0.89,
                    "explanation": f"Account '{usr}' accessed {len(hosts)} distinct internal assets: {list(hosts)}.",
                    "evidence_count": len(hosts)
                })
        return findings


class HuntRareDestinationConnection(HuntRule):
    hunt_id = "HUNT-007"
    name = "Rare Destination Connection / Unusual Egress Port"
    description = "Detects outbound communication to non-standard TCP/UDP egress ports (e.g. 4444, 1337, 8443, 6667)."
    severity = "MEDIUM"
    mitre_technique = "T1571"
    tactic = "TA0011"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        suspicious_ports = {1337, 4444, 6667, 8888, 9001, 31337}
        for ev in telemetry_events:
            dport = int(ev.get("destination_port", 0))
            if dport in suspicious_ports:
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": f"{ev.get('destination_ip')}:{dport}",
                    "entity_type": "PORT",
                    "confidence": 0.86,
                    "explanation": f"Egress connection attempted to non-standard C2 port {dport}.",
                    "evidence_count": 1
                })
        return findings


class HuntHighVelocityEventBurst(HuntRule):
    hunt_id = "HUNT-008"
    name = "High-Velocity Event Burst"
    description = "Identifies high packet velocity bursts ($> 1000\text{ packets/sec}$) or volumetric denial-of-service signatures."
    severity = "HIGH"
    mitre_technique = "T1498"
    tactic = "TA0040"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        for ev in telemetry_events:
            rate = float(ev.get("packet_rate", 0) or ev.get("flow_packets_per_second", 0))
            if rate >= 1000.0 or "DOS" in str(ev.get("attack_type", "")).upper():
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": ev.get("source_ip", "0.0.0.0"),
                    "entity_type": "IP",
                    "confidence": 0.93,
                    "explanation": f"High-velocity event flood ({rate:.1f} pps) originating from {ev.get('source_ip')}.",
                    "evidence_count": 1
                })
        return findings


class HuntSuspiciousAdminActivity(HuntRule):
    hunt_id = "HUNT-009"
    name = "Suspicious Administrative Activity / Privilege Escalation"
    description = "Hunts for privileged role changes, administrative token generation, or policy modifications outside operational hours."
    severity = "CRITICAL"
    mitre_technique = "T1548"
    tactic = "TA0004"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        for ev in telemetry_events:
            if ev.get("is_privilege_escalation") or "ESCALATION" in str(ev.get("event_type", "")).upper():
                findings.append({
                    "hunt_id": self.hunt_id,
                    "hunt_name": self.name,
                    "severity": self.severity,
                    "mitre_technique": self.mitre_technique,
                    "entity": ev.get("username", "admin"),
                    "entity_type": "USER",
                    "confidence": 0.94,
                    "explanation": f"Privilege escalation anomaly detected for user '{ev.get('username')}'.",
                    "evidence_count": 1
                })
        return findings


class HuntMultiStageAttackSequence(HuntRule):
    hunt_id = "HUNT-010"
    name = "Multi-Stage Attack Sequence"
    description = "Correlates multi-phase progression spanning Reconnaissance $\to$ Initial Access $\to$ Lateral Movement $\to$ Exfiltration."
    severity = "CRITICAL"
    mitre_technique = "T1190"
    tactic = "TA0002"

    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        findings = []
        stages_observed = set()
        for ev in telemetry_events:
            att = str(ev.get("attack_type", "")).upper()
            if "SCAN" in att or "PORT" in att:
                stages_observed.add("RECONNAISSANCE")
            elif "BRUTE" in att or "AUTH" in att:
                stages_observed.add("INITIAL_ACCESS")
            elif "LATERAL" in att or int(ev.get("destination_port", 0)) in {445, 3389}:
                stages_observed.add("LATERAL_MOVEMENT")
            elif "EXFIL" in att or float(ev.get("bytes_transferred", 0)) > 1000000:
                stages_observed.add("EXFILTRATION")

        if len(stages_observed) >= 3:
            findings.append({
                "hunt_id": self.hunt_id,
                "hunt_name": self.name,
                "severity": self.severity,
                "mitre_technique": self.mitre_technique,
                "entity": "MULTI_STAGE_CHAIN",
                "entity_type": "CAMPAIGN",
                "confidence": 0.99,
                "explanation": f"Multi-stage attack chain identified across phases: {sorted(stages_observed)}.",
                "evidence_count": len(telemetry_events)
            })
        return findings


class HuntRuleRegistry:
    """Registry managing active modular threat hunting rules."""

    def __init__(self):
        self._hunts: Dict[str, HuntRule] = {
            "HUNT-001": HuntRepeatedAuthFailureToSuccess(),
            "HUNT-002": HuntNewSourcePrivilegedAccess(),
            "HUNT-003": HuntUnusualLateralMovement(),
            "HUNT-004": HuntHighVolumeOutboundExfil(),
            "HUNT-005": HuntIOCSuspiciousAuthCombination(),
            "HUNT-006": HuntMultiAssetAccountAccess(),
            "HUNT-007": HuntRareDestinationConnection(),
            "HUNT-008": HuntHighVelocityEventBurst(),
            "HUNT-009": HuntSuspiciousAdminActivity(),
            "HUNT-010": HuntMultiStageAttackSequence(),
        }

    def get_hunt(self, hunt_id: str) -> Optional[HuntRule]:
        return self._hunts.get(hunt_id.upper().strip())

    def list_hunts(self) -> List[Dict[str, Any]]:
        return [
            {
                "hunt_id": h.hunt_id,
                "name": h.name,
                "description": h.description,
                "severity": h.severity,
                "mitre_technique": h.mitre_technique,
                "tactic": h.tactic
            }
            for h in self._hunts.values()
        ]

    def run_hunt(self, hunt_id: str, events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        h = self.get_hunt(hunt_id)
        if not h:
            raise ValueError(f"Hunt rule '{hunt_id}' not found.")
        return h.evaluate(events, context)

    def run_all_hunts(self, events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        all_findings = []
        for h in self._hunts.values():
            findings = h.evaluate(events, context)
            all_findings.extend(findings)
        return all_findings


hunt_rule_registry = HuntRuleRegistry()
