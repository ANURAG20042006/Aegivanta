"""
backend/app/services/threat_intel_service.py
============================================
Threat Intelligence Engine: Normalized IOC Repository,
Pluggable Threat Feeds, and Non-Destructive Event Enrichment.
"""

import ipaddress
import re
import json
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.threat_intel import ThreatIndicator, ThreatFeed
from backend.app.core.logging import logger


def normalize_ioc(raw_value: str, ioc_type: str) -> Tuple[bool, str, str]:
    """
    Validates and normalizes raw Indicator of Compromise (IOC) strings.
    Returns: (is_valid: bool, normalized_value: str, detected_type: str)
    """
    if not raw_value or not isinstance(raw_value, str):
        return False, "", ioc_type

    val = raw_value.strip()
    ioc_type_lower = (ioc_type or "").strip().lower()

    # 1. IP Addresses (IPv4 / IPv6)
    if ioc_type_lower in ["ipv4", "ipv6", "ip", ""]:
        try:
            ip_obj = ipaddress.ip_address(val)
            detected = "ipv6" if ip_obj.version == 6 else "ipv4"
            return True, ip_obj.exploded.lower(), detected
        except ValueError:
            if ioc_type_lower in ["ipv4", "ipv6"]:
                return False, "", ioc_type_lower

    # 2. Domain / Hostname
    if ioc_type_lower in ["domain", "hostname", "host", ""]:
        domain_val = val
        if "://" in domain_val:
            domain_val = urlparse(domain_val).hostname or domain_val
        domain_val = domain_val.split(":")[0].strip().lower().rstrip(".")
        if re.match(r"^(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$", domain_val):
            return True, domain_val, "domain"

    # 3. URL
    if ioc_type_lower in ["url", ""]:
        val_lower = val.lower()
        if val_lower.startswith("http://") or val_lower.startswith("https://"):
            parsed = urlparse(val)
            if parsed.hostname:
                normalized_url = f"{parsed.scheme.lower()}://{parsed.hostname.lower()}{parsed.path}"
                if parsed.query:
                    normalized_url += f"?{parsed.query}"
                return True, normalized_url, "url"

    # 4. Cryptographic Hash (SHA-256, MD5)
    if ioc_type_lower in ["sha256", "md5", "hash", ""]:
        hex_val = val.lower()
        if re.match(r"^[a-f0-9]{64}$", hex_val):
            return True, hex_val, "sha256"
        if re.match(r"^[a-f0-9]{32}$", hex_val):
            return True, hex_val, "md5"

    return False, "", ioc_type_lower or "unknown"


# ==============================================================================
# PLUGGABLE THREAT FEED PROVIDERS
# ==============================================================================

class ThreatFeedProvider(ABC):
    """Abstract interface for threat intelligence feed ingestors."""

    @abstractmethod
    async def fetch_and_parse(self, feed: ThreatFeed) -> List[Dict[str, Any]]:
        """Fetches remote or local feed content, parses records into raw indicator dicts."""
        pass


class StaticListProvider(ThreatFeedProvider):
    """Parses predefined or local static threat indicators."""

    async def fetch_and_parse(self, feed: ThreatFeed) -> List[Dict[str, Any]]:
        if not feed.feed_url:
            return []
        try:
            items = json.loads(feed.feed_url)
            return items if isinstance(items, list) else []
        except Exception:
            return []


class GenericJsonProvider(ThreatFeedProvider):
    """Fetches and parses standard JSON threat intelligence endpoints."""

    async def fetch_and_parse(self, feed: ThreatFeed) -> List[Dict[str, Any]]:
        import httpx
        if not feed.feed_url:
            return []
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(feed.feed_url)
            data = res.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "indicators" in data:
                return data["indicators"]
            return []


class GenericCsvProvider(ThreatFeedProvider):
    """Fetches and parses CSV threat indicator feeds."""

    async def fetch_and_parse(self, feed: ThreatFeed) -> List[Dict[str, Any]]:
        import httpx
        import csv
        import io
        if not feed.feed_url:
            return []
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(feed.feed_url)
            reader = csv.DictReader(io.StringIO(res.text))
            return [row for row in reader]


FEED_PROVIDERS: Dict[str, ThreatFeedProvider] = {
    "static_list": StaticListProvider(),
    "generic_json": GenericJsonProvider(),
    "generic_csv": GenericCsvProvider()
}


# ==============================================================================
# CORE THREAT INTEL SERVICE
# ==============================================================================

class ThreatIntelService:
    """Core Threat Intelligence Ingestion & Non-Destructive Event Enrichment Service."""

    @staticmethod
    async def enrich_telemetry(
        source_ip: str,
        destination_ip: Optional[str],
        domain: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Queries threat intelligence indicators against event IP addresses and domains.
        Returns non-destructive enrichment metadata without altering raw ML classification.
        """
        candidates: List[str] = []
        if source_ip:
            is_v, norm_src, _ = normalize_ioc(source_ip, "ipv4")
            if is_v:
                candidates.append(norm_src)
            candidates.append(source_ip.strip())

        if destination_ip:
            is_v, norm_dst, _ = normalize_ioc(destination_ip, "ipv4")
            if is_v:
                candidates.append(norm_dst)
            candidates.append(destination_ip.strip())

        if domain:
            is_v, norm_dom, _ = normalize_ioc(domain, "domain")
            if is_v:
                candidates.append(norm_dom)

        if not candidates:
            return {"is_match": False, "matched_iocs": []}

        # Query database for exact normalized matches
        query = select(ThreatIndicator).where(
            ThreatIndicator.normalized_value.in_(candidates),
            ThreatIndicator.is_active == True
        )
        res = await db.execute(query)
        indicators = res.scalars().all()

        if not indicators:
            return {"is_match": False, "matched_iocs": []}

        matched_list = []
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        for ind in indicators:
            ind.hit_count = (ind.hit_count or 0) + 1
            ind.last_seen = now
            matched_list.append({
                "indicator_id": ind.id,
                "ioc_type": ind.ioc_type,
                "normalized_value": ind.normalized_value,
                "threat_type": ind.threat_type,
                "severity": ind.severity,
                "confidence": ind.confidence,
                "source": ind.source,
                "tags": ind.tags or []
            })

        await db.flush()

        # Highest severity from matches
        severities = [m["severity"] for m in matched_list]
        top_severity = "CRITICAL" if "CRITICAL" in severities else ("HIGH" if "HIGH" in severities else "MEDIUM")

        return {
            "is_match": True,
            "match_count": len(matched_list),
            "top_severity": top_severity,
            "matched_iocs": matched_list
        }

    @staticmethod
    async def ingest_feed(feed: ThreatFeed, db: AsyncSession) -> int:
        """
        Executes a threat feed sync, normalizes indicators, deduplicates records,
        and saves indicators to the database with provenance attribution.
        """
        provider = FEED_PROVIDERS.get(feed.provider_type, GenericJsonProvider())
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        feed.last_sync_status = "RUNNING"
        feed.last_synced_at = now

        try:
            records = await provider.fetch_and_parse(feed)
            imported_count = 0

            for rec in records:
                raw_val = rec.get("value") or rec.get("ioc") or rec.get("indicator")
                raw_type = rec.get("type") or rec.get("ioc_type", "")
                if not raw_val:
                    continue

                is_valid, norm_val, det_type = normalize_ioc(raw_val, raw_type)
                if not is_valid:
                    continue

                # Check if indicator already exists
                q = select(ThreatIndicator).where(ThreatIndicator.normalized_value == norm_val)
                existing_res = await db.execute(q)
                existing = existing_res.scalar_one_or_none()

                if existing:
                    existing.last_seen = now
                    existing.is_active = True
                    existing.hit_count = (existing.hit_count or 0)
                else:
                    new_ind = ThreatIndicator(
                        ioc_type=det_type,
                        raw_value=raw_val,
                        normalized_value=norm_val,
                        threat_type=rec.get("threat_type", "malicious_host"),
                        severity=rec.get("severity", "HIGH"),
                        confidence=float(rec.get("confidence", 0.85)),
                        source=feed.feed_name,
                        description=rec.get("description", f"Imported from {feed.feed_name}"),
                        tags=rec.get("tags", []),
                        first_seen=now,
                        last_seen=now,
                        is_active=True
                    )
                    db.add(new_ind)
                    imported_count += 1

            feed.last_sync_status = "SUCCESS"
            feed.indicators_imported = (feed.indicators_imported or 0) + imported_count
            feed.last_error = None
            await db.flush()
            return imported_count

        except Exception as exc:
            feed.last_sync_status = "FAILED"
            feed.last_error = str(exc)
            logger.error(f"Threat feed '{feed.feed_name}' ingestion failed: {exc}")
            await db.flush()
            return 0

    @staticmethod
    async def prune_expired_iocs(
        db: AsyncSession,
        max_age_days: int = 90,
        min_confidence: float = 0.20,
        purge_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates indicator TTLs, aging timestamps, and confidence scores.
        Transitions expired indicators to EXPIRED/ARCHIVED status or purges them.
        """
        from datetime import timedelta
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cutoff_date = now - timedelta(days=max_age_days)

        # 1. Query active indicators eligible for expiration
        query = select(ThreatIndicator).where(ThreatIndicator.is_active == True)
        res = await db.execute(query)
        active_indicators = res.scalars().all()

        pruned_count = 0
        archived_count = 0
        purged_count = 0

        for ind in active_indicators:
            is_expired = False
            reason = ""

            # Rule A: Explicit expiration timestamp passed
            if ind.expires_at and ind.expires_at < now:
                is_expired = True
                reason = "EXPIRED_TTL"
            # Rule B: Stale indicator older than max_age_days without fresh sightings
            elif ind.last_seen and ind.last_seen < cutoff_date:
                is_expired = True
                reason = "STALE_MAX_AGE"
            # Rule C: Confidence score decayed below threshold
            elif ind.confidence is not None and ind.confidence < min_confidence:
                is_expired = True
                reason = "LOW_CONFIDENCE"

            if is_expired:
                if purge_deleted:
                    await db.delete(ind)
                    purged_count += 1
                else:
                    ind.is_active = False
                    ind.lifecycle_status = "ARCHIVED" if reason == "STALE_MAX_AGE" else "EXPIRED"
                    archived_count += 1
                pruned_count += 1

        await db.flush()
        logger.info(f"IOC Lifecycle Pruning complete: {pruned_count} pruned ({archived_count} archived, {purged_count} purged).")

        return {
            "total_evaluated": len(active_indicators),
            "pruned_count": pruned_count,
            "archived_count": archived_count,
            "purged_count": purged_count,
            "active_remaining": len(active_indicators) - pruned_count
        }

    @staticmethod
    async def get_lifecycle_metrics(db: AsyncSession) -> Dict[str, Any]:
        """Returns comprehensive threat indicator lifecycle distribution statistics."""
        from sqlalchemy import func
        
        # Total counts by status
        stmt_active = select(func.count(ThreatIndicator.id)).where(ThreatIndicator.is_active == True)
        res_active = await db.execute(stmt_active)
        active_count = res_active.scalar() or 0

        stmt_total = select(func.count(ThreatIndicator.id))
        res_total = await db.execute(stmt_total)
        total_count = res_total.scalar() or 0

        stmt_expired = select(func.count(ThreatIndicator.id)).where(ThreatIndicator.lifecycle_status == "EXPIRED")
        res_expired = await db.execute(stmt_expired)
        expired_count = res_expired.scalar() or 0

        stmt_archived = select(func.count(ThreatIndicator.id)).where(ThreatIndicator.lifecycle_status == "ARCHIVED")
        res_archived = await db.execute(stmt_archived)
        archived_count = res_archived.scalar() or 0

        return {
            "total_indicators": total_count,
            "active_indicators": active_count,
            "expired_indicators": expired_count,
            "archived_indicators": archived_count,
            "healthy_ratio": round(active_count / max(total_count, 1), 4)
        }

