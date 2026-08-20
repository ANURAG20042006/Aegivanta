"""
backend/app/services/feedback_service.py
========================================
Phase 3.10 Analyst Feedback Loop Service.
Captures analyst triage feedback (TRUE_POSITIVE, FALSE_POSITIVE, BENIGN, UNKNOWN),
calculates empirical analyst accuracy metrics, and compiles curated retraining datasets.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.models.feedback import DetectionFeedback, VALID_FEEDBACK_VERDICTS
from backend.app.models.incident import Incident
from backend.app.services.soc_event_broadcaster import soc_broadcaster

logger = logging.getLogger("SentinelAI")


class FeedbackService:
    """
    Production-grade Analyst Feedback Service.
    Enforces validated human-in-the-loop annotations and training dataset generation.
    """

    @staticmethod
    async def record_feedback(
        db: AsyncSession,
        predicted_attack_type: str,
        actual_verdict: str,
        predicted_confidence: Optional[float] = None,
        incident_id: Optional[str] = None,
        detection_id: Optional[str] = None,
        flow_id: Optional[str] = None,
        corrected_attack_type: Optional[str] = None,
        analyst_user_id: Optional[str] = None,
        analyst_username: Optional[str] = None,
        notes: Optional[str] = None,
        feature_snapshot: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Records an analyst triage feedback observation with validation."""
        verdict = actual_verdict.upper()
        if verdict not in VALID_FEEDBACK_VERDICTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid feedback verdict '{actual_verdict}'. Must be one of: {VALID_FEEDBACK_VERDICTS}"
            )

        feedback = DetectionFeedback(
            predicted_attack_type=predicted_attack_type,
            predicted_confidence=predicted_confidence,
            actual_verdict=verdict,
            incident_id=incident_id,
            detection_id=detection_id,
            flow_id=flow_id,
            corrected_attack_type=corrected_attack_type,
            analyst_user_id=analyst_user_id,
            analyst_username=analyst_username,
            notes=notes,
            feature_snapshot=feature_snapshot,
            is_used_for_retraining=False,
            created_at=datetime.now(timezone.utc)
        )
        db.add(feedback)

        # If incident_id provided, annotate the incident
        if incident_id:
            inc_query = select(Incident).where(Incident.id == incident_id)
            inc_res = await db.execute(inc_query)
            incident = inc_res.scalar_one_or_none()
            if incident:
                if verdict == "FALSE_POSITIVE":
                    incident.status = "RESOLVED"
                    incident.description = f"{incident.description} [Marked as FALSE_POSITIVE by {analyst_username or 'analyst'}]"
                elif verdict == "TRUE_POSITIVE":
                    incident.status = "INVESTIGATING"

        await db.commit()
        await db.refresh(feedback)

        # Broadcast feedback event to SOC stream
        await soc_broadcaster.broadcast(
            category="INVESTIGATION_UPDATE",
            severity="INFORMATIONAL",
            title="Analyst Feedback Submitted",
            description=f"Analyst {analyst_username or 'User'} classified prediction '{predicted_attack_type}' as {verdict}.",
            details={
                "feedback_id": feedback.id,
                "verdict": verdict,
                "incident_id": incident_id,
                "predicted": predicted_attack_type
            }
        )

        return {
            "status": "SUCCESS",
            "feedback_id": feedback.id,
            "verdict": feedback.actual_verdict,
            "created_at": feedback.created_at.isoformat()
        }

    @staticmethod
    async def get_feedback_stats(db: AsyncSession) -> Dict[str, Any]:
        """Calculates real-time analyst feedback metrics and confusion counts."""
        query = select(DetectionFeedback.actual_verdict, func.count(DetectionFeedback.id)).group_by(DetectionFeedback.actual_verdict)
        res = await db.execute(query)
        rows = res.all()

        counts = {v: 0 for v in VALID_FEEDBACK_VERDICTS}
        total = 0
        for verdict, count in rows:
            if verdict in counts:
                counts[verdict] = count
            total += count

        tp = counts.get("TRUE_POSITIVE", 0)
        fp = counts.get("FALSE_POSITIVE", 0)
        benign = counts.get("BENIGN", 0)
        unknown = counts.get("UNKNOWN", 0)

        precision = round(tp / max(tp + fp, 1), 4) if (tp + fp) > 0 else 1.0
        fpr = round(fp / max(fp + benign, 1), 4) if (fp + benign) > 0 else 0.0

        return {
            "total_feedback_count": total,
            "verdict_distribution": counts,
            "analyst_precision": precision,
            "analyst_measured_fpr": fpr,
            "true_positive_rate": round(tp / max(total, 1), 4) if total > 0 else 0.0,
            "false_positive_rate": fpr,
            "pending_retraining_samples": total
        }

    @staticmethod
    async def list_feedback(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        verdict: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists recorded analyst feedback items with pagination and filtering."""
        query = select(DetectionFeedback).order_by(DetectionFeedback.created_at.desc()).limit(limit).offset(offset)
        if verdict:
            query = query.where(DetectionFeedback.actual_verdict == verdict.upper())

        res = await db.execute(query)
        items = res.scalars().all()

        return [
            {
                "id": f.id,
                "incident_id": f.incident_id,
                "detection_id": f.detection_id,
                "flow_id": f.flow_id,
                "predicted_attack_type": f.predicted_attack_type,
                "predicted_confidence": f.predicted_confidence,
                "actual_verdict": f.actual_verdict,
                "corrected_attack_type": f.corrected_attack_type,
                "analyst_username": f.analyst_username,
                "notes": f.notes,
                "is_used_for_retraining": f.is_used_for_retraining,
                "created_at": f.created_at.isoformat() if f.created_at else None
            }
            for f in items
        ]

    @staticmethod
    async def export_retraining_dataset(db: AsyncSession) -> Dict[str, Any]:
        """Compiles validated feedback records into a supervised training dataset structure."""
        query = select(DetectionFeedback).where(
            DetectionFeedback.feature_snapshot.is_not(None),
            DetectionFeedback.actual_verdict.in_(["TRUE_POSITIVE", "FALSE_POSITIVE", "BENIGN"])
        )
        res = await db.execute(query)
        records = res.scalars().all()

        samples = []
        for r in records:
            label = r.corrected_attack_type if r.corrected_attack_type else (
                r.predicted_attack_type if r.actual_verdict == "TRUE_POSITIVE" else "BENIGN"
            )
            samples.append({
                "features": r.feature_snapshot,
                "label": label,
                "verdict": r.actual_verdict,
                "feedback_id": r.id
            })

        return {
            "total_samples": len(samples),
            "dataset_version": f"feedback-curated-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "samples": samples
        }
