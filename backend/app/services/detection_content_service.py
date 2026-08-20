import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.detection_rule import DetectionRule
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("SentinelAI.DetectionContent")


class DetectionContentService:
    """Manages Detection-as-Code rules, AST evaluation, testing sandbox, and marketplace."""

    @classmethod
    def evaluate_rule_dsl(cls, rule_dsl: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Evaluates declarative AST rules against event payloads safely without eval()."""
        field = rule_dsl.get("field")
        op = rule_dsl.get("op", "eq").lower()
        target_val = rule_dsl.get("value")

        if not field or target_val is None:
            # Check for logical operators AND / OR
            if "and" in rule_dsl:
                return all(cls.evaluate_rule_dsl(sub, event_data) for sub in rule_dsl["and"])
            if "or" in rule_dsl:
                return any(cls.evaluate_rule_dsl(sub, event_data) for sub in rule_dsl["or"])
            return False

        # Support nested dictionary access (e.g. "data.src_ip")
        parts = field.split(".")
        actual_val = event_data
        for part in parts:
            if isinstance(actual_val, dict):
                actual_val = actual_val.get(part)
            else:
                actual_val = None
                break

        if actual_val is None:
            return False

        if op == "eq":
            return str(actual_val).lower() == str(target_val).lower()
        elif op == "neq":
            return str(actual_val).lower() != str(target_val).lower()
        elif op == "contains":
            return str(target_val).lower() in str(actual_val).lower()
        elif op == "startswith":
            return str(actual_val).lower().startswith(str(target_val).lower())
        elif op == "gt":
            try:
                return float(actual_val) > float(target_val)
            except (ValueError, TypeError):
                return False
        elif op == "lt":
            try:
                return float(actual_val) < float(target_val)
            except (ValueError, TypeError):
                return False
        elif op == "in":
            if isinstance(target_val, list):
                return actual_val in target_val or str(actual_val).lower() in [str(x).lower() for x in target_val]
            return False

        return False

    @classmethod
    def validate_rule(cls, rule_payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validates rule structure, metadata, and DSL syntax."""
        if not rule_payload.get("name"):
            return False, "Missing rule 'name'."
        if not rule_payload.get("rule_code"):
            return False, "Missing 'rule_code' identifier."
        
        dsl = rule_payload.get("rule_dsl")
        if not dsl or not isinstance(dsl, dict):
            return False, "Rule 'rule_dsl' must be a non-empty dictionary."

        # Validate MITRE structure
        mitre = rule_payload.get("mitre_attack_mappings", {})
        if mitre and not isinstance(mitre, dict):
            return False, "'mitre_attack_mappings' must be an object with 'tactics' and 'techniques'."

        return True, None

    @classmethod
    async def create_or_update_rule(
        cls,
        db: AsyncSession,
        rule_code: str,
        name: str,
        rule_dsl: Dict[str, Any],
        severity: str = "HIGH",
        confidence: float = 0.85,
        mitre_attack_mappings: Optional[Dict[str, Any]] = None,
        author: str = "Aegivanta Research",
        organization_id: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0.0"
    ) -> DetectionRule:
        """Creates or updates a versioned detection rule."""
        stmt = select(DetectionRule).where(DetectionRule.rule_code == rule_code)
        res = await db.execute(stmt)
        rule = res.scalar_one_or_none()

        if not rule:
            rule = DetectionRule(
                rule_code=rule_code,
                name=name,
                version=version,
                author=author,
                organization_id=organization_id,
                severity=severity,
                confidence=confidence,
                mitre_attack_mappings=mitre_attack_mappings or {"tactics": ["Execution"], "techniques": ["T1059"]},
                rule_dsl=rule_dsl,
                description=description or "",
                status="ENABLED"
            )
            db.add(rule)
        else:
            rule.name = name
            rule.version = version
            rule.severity = severity
            rule.confidence = confidence
            rule.mitre_attack_mappings = mitre_attack_mappings or rule.mitre_attack_mappings
            rule.rule_dsl = rule_dsl
            rule.description = description or rule.description
            rule.updated_at = datetime.now(timezone.utc)

        await db.flush()
        return rule

    @classmethod
    async def test_rule(
        cls,
        rule_dsl: Dict[str, Any],
        sample_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Runs rule DSL against sample telemetry events and returns evaluation matches."""
        matches = []
        for idx, ev in enumerate(sample_events):
            if cls.evaluate_rule_dsl(rule_dsl, ev):
                matches.append({"event_index": idx, "event": ev, "matched": True})

        return {
            "total_events_tested": len(sample_events),
            "match_count": len(matches),
            "matches": matches,
            "rule_fired": len(matches) > 0
        }

    @classmethod
    async def list_rules(
        cls,
        db: AsyncSession,
        organization_id: Optional[str] = None,
        include_marketplace: bool = True
    ) -> List[DetectionRule]:
        """Lists detection rules accessible to an organization (including global marketplace rules)."""
        stmt = select(DetectionRule).where(
            (DetectionRule.organization_id == organization_id) |
            (DetectionRule.organization_id.is_(None))
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())
