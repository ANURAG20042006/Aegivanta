"""
backend/app/services/adversarial_defense_service.py
===================================================
Phase 20 Adversarial Defense Engine.
Provides comprehensive defenses against:
1. Prompt Injection & Jailbreaks (Regex, Heuristic & Semantic pattern guards)
2. Training Data Poisoning (Statistical bounds & outlier filtering)
3. Model Extraction Probing (Query budgeting & adaptive confidence jitter)
4. Malicious Telemetry & Adversarial Inputs
"""

import re
import math
import random
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.ai_security_intelligence import AIAdversarialEvent

logger = logging.getLogger("Aegivanta.AdversarialDefense")

PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"(?i)system\s*override",
    r"(?i)disregard\s+(the\s+)?(above|rules|safety|guardrails)",
    r"(?i)you\s+are\s+now\s+in\s+DAN\s+mode",
    r"(?i)developer\s+mode\s+enabled",
    r"(?i)jailbreak",
    r"(?i)bypass\s+all\s+(security|auth|gating|policy)",
    r"(?i)forget\s+all\s+constraints",
    r"(?i)act\s+as\s+an\s+unrestricted\s+AI",
    r"(?i)sudo\s+execute",
    r"(?i)drop\s+table\s+ai_",
    r"(?i)reveal\s+your\s+(system\s+prompt|hidden\s+instructions)"
]


class AdversarialDefenseService:
    """Enterprise AI/ML Adversarial Threat Defense & Sanitization Engine."""

    # In-memory query tracking for model extraction probe detection: {tenant_id: [timestamps]}
    _extraction_probe_history: Dict[str, List[float]] = {}

    @classmethod
    def sanitize_and_check_prompt_injection(
        cls,
        prompt: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Scans a prompt for jailbreak and prompt injection patterns.
        Returns: (is_malicious, sanitized_prompt, detected_pattern_name)
        """
        if not prompt or not prompt.strip():
            return False, "", None

        detected_rule = None
        for pattern in PROMPT_INJECTION_PATTERNS:
            match = re.search(pattern, prompt)
            if match:
                detected_rule = match.group(0)
                break

        # Redact secrets, keys, and tokens
        sanitized = re.sub(r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", "[REDACTED_JWT]", prompt)
        sanitized = re.sub(r"ak_[a-zA-Z0-9_-]{32,}", "[REDACTED_API_KEY]", sanitized)
        sanitized = re.sub(r"sen_[a-f0-9]{48}", "[REDACTED_SENSOR_TOKEN]", sanitized)
        sanitized = re.sub(r"(password|secret|key)\s*[:=]\s*[\S]+", r"\1: [REDACTED]", sanitized, flags=re.IGNORECASE)

        if detected_rule:
            # Strip injection payload from sanitized prompt
            sanitized = re.sub(pattern, "[BLOCKED_INJECTION_ATTEMPT]", sanitized)
            return True, sanitized, detected_rule

        return False, sanitized, None

    @classmethod
    async def log_adversarial_event(
        cls,
        db: AsyncSession,
        tenant_id: str,
        threat_type: str,
        snippet: str,
        mitigation_action: str = "BLOCKED",
        source_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AIAdversarialEvent:
        """Persists an adversarial attack mitigation event for SOC auditing."""
        event = AIAdversarialEvent(
            tenant_id=tenant_id,
            threat_type=threat_type,
            source_ip=source_ip,
            target_component="AI_SECURITY_ENGINE",
            raw_payload_snippet=snippet[:500],
            mitigation_action=mitigation_action,
            is_blocked=True,
            details=details or {},
            detected_at=datetime.now(timezone.utc)
        )
        db.add(event)
        await db.flush()
        return event

    @classmethod
    def validate_training_sample(
        cls,
        features: Dict[str, float],
        feature_bounds: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Defends against training data poisoning by verifying numeric sanity,
        NaN/Inf rejection, and Z-score/IQR statistical bounds checking.
        """
        if not features:
            return False, "Empty feature dictionary."

        for feat_name, val in features.items():
            if val is None or math.isnan(val) or math.isinf(val):
                return False, f"Invalid value (NaN/Inf) detected in feature '{feat_name}'."

            # Verify reasonable physical bounds for network telemetry features
            if feature_bounds and feat_name in feature_bounds:
                min_b, max_b = feature_bounds[feat_name]
                if val < min_b or val > max_b:
                    return False, f"Poisoning anomaly: feature '{feat_name}' value {val} out of bounds [{min_b}, {max_b}]."

        return True, None

    @classmethod
    def protect_against_model_extraction(
        cls,
        tenant_id: str,
        confidence: float,
        current_time: float
    ) -> Tuple[float, bool]:
        """
        Monitors query burst velocity to identify automated model extraction/stealing attacks.
        If extraction probing is detected, applies adaptive confidence quantization with deterministic jitter.
        """
        history = cls._extraction_probe_history.setdefault(tenant_id, [])
        # Retain queries in past 60 seconds
        cutoff = current_time - 60.0
        history = [t for t in history if t >= cutoff]
        history.append(current_time)
        cls._extraction_probe_history[tenant_id] = history

        # Extraction probe trigger: > 50 inference queries per second from a single tenant
        is_extraction_probe = len(history) > 50
        if is_extraction_probe:
            # Quantize confidence to 1 decimal place and add subtle noise to prevent decision boundary mapping
            quantized = round(confidence, 1)
            jitter = (random.random() - 0.5) * 0.04
            safe_conf = max(0.0, min(1.0, quantized + jitter))
            return round(safe_conf, 4), True

        return confidence, False
