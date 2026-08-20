"""
backend/app/services/lateral_movement_service.py
================================================
Phase 3.5 Multi-Hop Lateral Movement Path Detection Engine.
Reconstructs causal lateral movement trajectories across host assets, computes hop velocity,
maps MITRE ATT&CK lateral techniques, and identifies critical isolation choke points.
"""

from datetime import datetime, timezone
import uuid
import math
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import defaultdict

from backend.app.core.logging import logger


LATERAL_PORT_TECHNIQUE_MAP = {
    445: ("T1021.002", "SMB / Windows Admin Shares", "CRITICAL"),
    139: ("T1021.002", "NetBIOS Session Service", "HIGH"),
    3389: ("T1021.001", "Remote Desktop Protocol (RDP)", "HIGH"),
    22: ("T1021.004", "SSH Remote Services", "MEDIUM"),
    5985: ("T1021.006", "Windows Remote Management (WinRM HTTP)", "HIGH"),
    5986: ("T1021.006", "Windows Remote Management (WinRM HTTPS)", "HIGH"),
    135: ("T1047", "Windows Management Instrumentation (WMI/RPC)", "HIGH"),
    88: ("T1558", "Kerberos Ticket Request / Pass-the-Ticket", "CRITICAL"),
    389: ("T1087.002", "LDAP Domain Account Discovery", "MEDIUM"),
    636: ("T1087.002", "LDAPS Domain Discovery", "MEDIUM"),
    1433: ("T1078.001", "MS-SQL Database Lateral Pivot", "HIGH"),
    3306: ("T1078.001", "MySQL Database Lateral Pivot", "HIGH"),
    5432: ("T1078.001", "PostgreSQL Database Lateral Pivot", "HIGH"),
    8080: ("T1570", "Lateral Tool Transfer / Internal Web Pivot", "MEDIUM"),
    8000: ("T1570", "Lateral Tool Transfer / Internal Web Pivot", "MEDIUM"),
}


class LateralMovementDetector:
    """
    Analyzes temporal sequences of network flows and security incidents to identify
    multi-hop lateral movement chains across internal network segments.
    """

    @staticmethod
    def classify_port_technique(port: int, protocol: str = "TCP") -> Tuple[str, str, str]:
        """Maps destination port and protocol to MITRE ATT&CK technique."""
        if port in LATERAL_PORT_TECHNIQUE_MAP:
            return LATERAL_PORT_TECHNIQUE_MAP[port]
        if protocol.upper() == "SSH":
            return ("T1021.004", "SSH Remote Services", "MEDIUM")
        if protocol.upper() == "RDP":
            return ("T1021.001", "Remote Desktop Protocol (RDP)", "HIGH")
        if protocol.upper() == "SMB":
            return ("T1021.002", "SMB / Admin Shares", "CRITICAL")
        return ("T1021", "Generic Lateral Protocol Traversal", "MEDIUM")

    @staticmethod
    def detect_lateral_movement_chains(
        events: List[Dict[str, Any]],
        max_dwell_hours: float = 24.0,
        min_chain_length: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Reconstructs multi-hop lateral movement chains from a chronological list of events.
        Each event must contain: source_ip, destination_ip, timestamp, and optional destination_port, attack_type, risk_score.
        """
        if not events or len(events) < min_chain_length:
            return []

        # 1. Normalize and sort events chronologically
        normalized_events = []
        for idx, ev in enumerate(events):
            src = ev.get("source_ip") or ev.get("src_ip")
            dst = ev.get("destination_ip") or ev.get("dst_ip")
            if not src or not dst or src == dst:
                continue

            ts = ev.get("timestamp")
            if isinstance(ts, str):
                try:
                    ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    ts_dt = datetime.now(timezone.utc)
            elif isinstance(ts, datetime):
                ts_dt = ts
            else:
                ts_dt = datetime.now(timezone.utc)

            port = int(ev.get("destination_port") or ev.get("dst_port") or 445)
            proto = str(ev.get("protocol") or "TCP")
            risk = float(ev.get("risk_score") or ev.get("severity_score") or 65.0)
            is_mal = bool(ev.get("is_malicious", True))

            tech_id, tech_name, def_sev = LateralMovementDetector.classify_port_technique(port, proto)

            normalized_events.append({
                "event_id": ev.get("id") or ev.get("event_id") or f"ev-{idx}",
                "source_ip": src.strip(),
                "destination_ip": dst.strip(),
                "destination_port": port,
                "protocol": proto,
                "timestamp": ts_dt,
                "risk_score": risk,
                "is_malicious": is_mal,
                "technique_id": tech_id,
                "technique_name": tech_name,
                "severity": ev.get("severity") or def_sev
            })

        normalized_events.sort(key=lambda x: x["timestamp"])

        # 2. Build forward causal chains (A -> B -> C -> D)
        max_dwell_seconds = max_dwell_hours * 3600.0
        chains: List[List[Dict[str, Any]]] = []

        for i, ev in enumerate(normalized_events):
            # Try to extend existing chains
            extended = False
            for chain in chains:
                last_hop = chain[-1]
                # If current source equals previous destination and time delta within threshold
                if last_hop["destination_ip"] == ev["source_ip"]:
                    delta = (ev["timestamp"] - last_hop["timestamp"]).total_seconds()
                    if 0 <= delta <= max_dwell_seconds:
                        # Avoid cyclical loops in the same chain
                        visited_nodes = {h["source_ip"] for h in chain} | {h["destination_ip"] for h in chain}
                        if ev["destination_ip"] not in visited_nodes or ev["destination_ip"] == chain[0]["source_ip"]:
                            chain.append(ev)
                            extended = True
                            break

            if not extended:
                # Start potential new chain
                chains.append([ev])

        # 3. Filter chains by minimum length (>= min_chain_length hops)
        valid_chains = [c for c in chains if len(c) >= min_chain_length]

        # 4. Format and compute risk analytics per detected chain
        results = []
        for c in valid_chains:
            start_time = c[0]["timestamp"]
            end_time = c[-1]["timestamp"]
            total_duration = max((end_time - start_time).total_seconds(), 1.0)
            duration_hours = total_duration / 3600.0
            velocity = len(c) / max(duration_hours, 0.01)

            # Cumulative risk score: 1 - prod(1 - r_i/100)
            prob_safe = 1.0
            for hop in c:
                r_norm = min(max(hop["risk_score"] / 100.0, 0.1), 0.99)
                prob_safe *= (1.0 - r_norm)
            cum_risk = round((1.0 - prob_safe) * 100.0, 2)

            # Extract distinct nodes and techniques
            node_sequence = [c[0]["source_ip"]] + [hop["destination_ip"] for hop in c]
            techniques = list({f"{h['technique_id']}: {h['technique_name']}" for h in c})

            # Intermediate choke points (nodes connecting multi-hop path)
            chokepoints = list(dict.fromkeys([hop["source_ip"] for hop in c[1:]]))

            # Overall severity determination
            sev_levels = [h["severity"] for h in c]
            if "CRITICAL" in sev_levels or cum_risk >= 85.0:
                overall_sev = "CRITICAL"
            elif "HIGH" in sev_levels or cum_risk >= 65.0:
                overall_sev = "HIGH"
            else:
                overall_sev = "MEDIUM"

            chain_id = f"LM-{uuid.uuid4().hex[:8].upper()}"

            # Format hops
            formatted_hops = []
            for h_idx, h in enumerate(c):
                dwell = 0.0
                if h_idx > 0:
                    dwell = round((h["timestamp"] - c[h_idx - 1]["timestamp"]).total_seconds(), 2)
                formatted_hops.append({
                    "hop_number": h_idx + 1,
                    "source_ip": h["source_ip"],
                    "destination_ip": h["destination_ip"],
                    "port": h["destination_port"],
                    "protocol": h["protocol"],
                    "technique_id": h["technique_id"],
                    "technique_name": h["technique_name"],
                    "timestamp": h["timestamp"].isoformat(),
                    "dwell_time_seconds": dwell,
                    "risk_score": h["risk_score"],
                    "severity": h["severity"]
                })

            results.append({
                "chain_id": chain_id,
                "initial_compromise_host": c[0]["source_ip"],
                "target_host": c[-1]["destination_ip"],
                "hop_count": len(c),
                "node_sequence": node_sequence,
                "cumulative_risk_score": cum_risk,
                "severity": overall_sev,
                "total_duration_seconds": round(total_duration, 2),
                "velocity_hops_per_hour": round(velocity, 2),
                "mitre_techniques": techniques,
                "recommended_chokepoints": chokepoints,
                "hops": formatted_hops,
                "detected_at": datetime.now(timezone.utc).isoformat()
            })

        # Sort results by cumulative risk score descending
        results.sort(key=lambda x: x["cumulative_risk_score"], reverse=True)
        return results
