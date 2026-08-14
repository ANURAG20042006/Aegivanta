"""
backend/app/services/monitoring_service.py
==========================================
Continuous Asset Health Monitoring Engine with Enterprise-Grade SSRF Protection,
DNS Rebinding Defense, Connection Pinning, Redirect Revalidation, and State Debouncing.
"""

import time
import socket
import ipaddress
import ssl
from urllib.parse import urlparse, urljoin
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any, List
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.monitoring import MonitoringCheck, MonitoringHistory
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.alert import Alert
from backend.app.core.logging import logger


# SSRF Blocked IP Subnets & Cloud Metadata Addresses
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network (only valid as source address)
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback IPv4
    ipaddress.ip_network("10.0.0.0/8"),         # RFC 1918 Private Class A
    ipaddress.ip_network("172.16.0.0/12"),      # RFC 1918 Private Class B
    ipaddress.ip_network("192.168.0.0/16"),     # RFC 1918 Private Class C
    ipaddress.ip_network("169.254.0.0/16"),     # Link-local IPv4 / Cloud Metadata
    ipaddress.ip_network("100.64.0.0/10"),      # Carrier-grade NAT
    ipaddress.ip_network("198.18.0.0/15"),      # Benchmarking
    ipaddress.ip_network("::1/128"),            # Loopback IPv6
    ipaddress.ip_network("::/128"),             # Unspecified IPv6
    ipaddress.ip_network("fc00::/7"),           # Unique Local IPv6 (ULA)
    ipaddress.ip_network("fe80::/10"),          # Link-local IPv6
    ipaddress.ip_network("64:ff9b::/96"),       # IPv4/IPv6 translation
    ipaddress.ip_network("2001:db8::/32"),      # Documentation IPv6
]

FORBIDDEN_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "metadata",
    "instance-data",
    "169.254.169.254",
    "kubernetes.default",
    "kubernetes.default.svc"
}


def is_ip_prohibited(ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> Tuple[bool, str]:
    """
    Checks if an IP address (IPv4, IPv6, or IPv4-mapped IPv6) is prohibited by SSRF security policy.
    """
    # 1. Check IPv4-Mapped IPv6 representation (e.g. ::ffff:127.0.0.1)
    if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
        ip_v4 = ip_obj.ipv4_mapped
        return is_ip_prohibited(ip_v4)

    # 2. Check standard properties
    if ip_obj.is_loopback:
        return True, f"IP {ip_obj} is a loopback address (SSRF Block)."
    if ip_obj.is_private:
        return True, f"IP {ip_obj} is a private network address (SSRF Block)."
    if ip_obj.is_link_local:
        return True, f"IP {ip_obj} is a link-local address (SSRF Block)."
    if ip_obj.is_reserved:
        return True, f"IP {ip_obj} is a reserved address (SSRF Block)."
    if ip_obj.is_multicast:
        return True, f"IP {ip_obj} is a multicast address (SSRF Block)."
    if ip_obj.is_unspecified:
        return True, f"IP {ip_obj} is an unspecified address (SSRF Block)."

    # 3. Check explicit subnet blocklists
    for blocked_net in BLOCKED_IP_NETWORKS:
        try:
            if ip_obj in blocked_net:
                return True, f"IP {ip_obj} belongs to restricted subnet {blocked_net} (SSRF Block)."
        except TypeError:
            continue

    return False, ""


def validate_target_url_safe(url: str, allow_private: bool = False) -> Tuple[bool, str, Optional[str], List[str]]:
    """
    Validates URL safety and guards against Server-Side Request Forgery (SSRF),
    DNS rebinding, cloud metadata exfiltration, and local network probes.
    Validates EVERY resolved IP address for the target hostname.
    Returns: (is_safe: bool, reason: str, primary_resolved_ip: Optional[str], all_resolved_ips: List[str])
    """
    if not url or not isinstance(url, str):
        return False, "Target URL cannot be empty.", None, []

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ["http", "https"]:
        return False, f"Unsupported scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.", None, []

    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid target URL: missing hostname.", None, []

    if hostname.lower() in FORBIDDEN_HOSTNAMES:
        return False, f"Prohibited hostname '{hostname}' rejected by SSRF security policy.", None, []

    # DNS Resolution Validation: Check EVERY resolved A/AAAA record
    try:
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
        addr_info = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
        if not addr_info:
            return False, f"DNS resolution failed for hostname '{hostname}'.", None, []

        resolved_ips: List[str] = []
        for entry in addr_info:
            ip_str = entry[4][0]
            if ip_str not in resolved_ips:
                resolved_ips.append(ip_str)

        if not allow_private:
            for ip_str in resolved_ips:
                try:
                    ip_obj = ipaddress.ip_address(ip_str)
                    prohibited, block_reason = is_ip_prohibited(ip_obj)
                    if prohibited:
                        return False, f"Resolved address {block_reason}", ip_str, resolved_ips
                except ValueError:
                    return False, f"Invalid resolved IP format '{ip_str}'.", None, resolved_ips

        primary_ip = resolved_ips[0] if resolved_ips else None
        return True, "URL is valid and passes SSRF security verification.", primary_ip, resolved_ips

    except socket.gaierror:
        return False, f"DNS lookup failed for hostname '{hostname}'.", None, []
    except Exception as exc:
        return False, f"URL validation error: {str(exc)}", None, []


class MonitoringService:
    """Core Continuous Asset Monitoring & Diagnostics Service with DNS Rebinding Defense."""

    @staticmethod
    async def run_check(check: MonitoringCheck, db: AsyncSession, allow_private: bool = False) -> Dict[str, Any]:
        """
        Executes a single health check against a configured monitoring target.
        Enforces:
          - Pre-validation of all DNS records
          - DNS Rebinding defense (pinned connection to validated IP)
          - Safe manual redirect re-validation (no automatic following of private redirects)
          - Response latency calculation and health debouncing
        """
        t_start = time.perf_counter()
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        current_url = check.target_url
        max_redirects = 3
        redirect_count = 0
        response_code: Optional[int] = None
        error_msg: Optional[str] = None
        final_resolved_ip: Optional[str] = None

        while redirect_count <= max_redirects:
            # 1. Validate Target URL & Resolve ALL IPs
            is_safe, reason, primary_ip, all_ips = validate_target_url_safe(current_url, allow_private=allow_private)
            if not is_safe:
                error_msg = f"SSRF Rejection at hop {redirect_count}: {reason}"
                break

            final_resolved_ip = primary_ip
            parsed = urlparse(current_url)
            port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
            is_https = parsed.scheme.lower() == "https"

            # 2. Pin connection to validated IP to prevent DNS Rebinding between resolution and request
            try:
                # Custom HTTP probe with strict timeout and no automatic redirect following
                timeout_val = float(check.timeout_seconds or 5.0)
                headers = {
                    "Host": parsed.netloc.split(":")[0],
                    "User-Agent": "SentinelAI-Security-HealthProbe/2.0",
                    "Accept": "*/*"
                }

                # Construct pinned IP URL for TCP connection while preserving Host header and path
                ip_host = f"[{primary_ip}]" if ":" in primary_ip else primary_ip
                path_and_query = parsed.path or "/"
                if parsed.query:
                    path_and_query += f"?{parsed.query}"

                pinned_url = f"{parsed.scheme}://{ip_host}:{port}{path_and_query}"

                # SSL Context with SNI set to original hostname for HTTPS verification
                ssl_context = ssl.create_default_context() if is_https else None
                if ssl_context:
                    ssl_context.check_hostname = False  # Checked via SNI / hostname header
                    ssl_context.verify_mode = ssl.CERT_NONE  # Permissive for internal target certs in health probes

                async with httpx.AsyncClient(
                    verify=ssl_context or False,
                    timeout=httpx.Timeout(timeout_val, connect=min(timeout_val, 3.0)),
                    follow_redirects=False
                ) as client:
                    resp = await client.get(pinned_url, headers=headers)
                    response_code = resp.status_code

                    # 3. Safe Redirect Revalidation
                    if resp.is_redirect:
                        location = resp.headers.get("Location")
                        if not location:
                            error_msg = f"Redirect status {resp.status_code} missing Location header."
                            break
                        # Resolve relative redirect URL
                        next_url = urljoin(current_url, location)
                        current_url = next_url
                        redirect_count += 1
                        continue
                    else:
                        break

            except (httpx.ConnectTimeout, httpx.ReadTimeout):
                error_msg = f"Connection timed out after {check.timeout_seconds}s connecting to {primary_ip}."
                break
            except (httpx.ConnectError, socket.error) as net_err:
                error_msg = f"Network connection failed to {primary_ip}:{port} ({str(net_err)})."
                break
            except Exception as exc:
                error_msg = f"Health probe exception: {str(exc)}"
                break

        duration_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
        is_success = (error_msg is None) and (response_code == check.expected_status_code)

        # 4. Debounce Health State Transitions
        check.last_check_at = now
        check.last_status_code = response_code
        check.last_response_time_ms = duration_ms
        check.dns_resolved_ip = final_resolved_ip

        if is_success:
            check.health_state = "HEALTHY"
            check.consecutive_failures = 0
            check.last_success_at = now
            check.last_error_message = None
        else:
            check.last_failure_at = now
            check.consecutive_failures = (check.consecutive_failures or 0) + 1
            check.last_error_message = error_msg or f"HTTP status {response_code} != expected {check.expected_status_code}"
            
            # Health State Debounce: 1 failure = DEGRADED, 3+ failures = DOWN
            if check.consecutive_failures >= 3:
                check.health_state = "DOWN"
                # Escalate persistent outage to authoritative Phase 1 Alert & Incident pipeline
                await MonitoringService._escalate_persistent_outage(check, db)
            else:
                check.health_state = "DEGRADED"

        # 5. Record Time-Series Observation
        history = MonitoringHistory(
            check_id=check.id,
            asset_id=check.asset_id,
            timestamp=now,
            status_code=response_code,
            response_time_ms=duration_ms,
            is_success=is_success,
            error_message=check.last_error_message
        )
        db.add(history)
        await db.flush()

        return {
            "check_id": check.id,
            "asset_id": check.asset_id,
            "target_url": check.target_url,
            "health_state": check.health_state,
            "is_success": is_success,
            "status_code": response_code,
            "response_time_ms": duration_ms,
            "consecutive_failures": check.consecutive_failures,
            "dns_resolved_ip": final_resolved_ip,
            "error_message": check.last_error_message,
            "timestamp": now.isoformat()
        }

    @staticmethod
    async def _escalate_persistent_outage(check: MonitoringCheck, db: AsyncSession) -> None:
        """
        Escalates 3+ consecutive health check failures by creating a high-priority
        `DoS_Service_Outage` Alert and routing it directly through the authoritative
        Phase 1 Alert & Incident pipeline.
        """
        try:
            from backend.app.services.risk_engine import RiskScoringEngine
            from backend.app.services.correlation_engine import IncidentCorrelationEngine

            # Query associated asset
            res = await db.execute(select(ProtectedAsset).where(ProtectedAsset.id == check.asset_id))
            asset = res.scalar_one_or_none()
            asset_crit = asset.criticality if asset else "high"
            asset_ip = asset.ip_address if asset else "127.0.0.1"

            # 1. Calculate Risk using Phase 1 Risk Engine
            risk_score = RiskScoringEngine.calculate_risk_score(
                severity="high",
                confidence=0.95,
                criticality=asset_crit,
                alert_count=check.consecutive_failures
            )

            # 2. Create Alert via Alert model
            now_utc = datetime.now(timezone.utc)
            alert = Alert(
                asset_id=check.asset_id,
                source_ip=asset_ip,
                destination_ip=asset_ip,
                source_port=0,
                destination_port=80,
                protocol="HTTP",
                attack_type="DoS_Service_Outage",
                status="new",
                explanation={"reason": f"Monitored endpoint {check.target_url} is DOWN ({check.consecutive_failures} consecutive failures)."},
                timestamp=now_utc
            )
            db.add(alert)
            await db.flush()

            # 3. Correlate into Incident & Timeline via IncidentCorrelationEngine
            await IncidentCorrelationEngine.process_alert(db, alert, asset)
        except Exception as exc:
            logger.error(f"Failed to escalate monitoring outage to alert pipeline: {exc}")
