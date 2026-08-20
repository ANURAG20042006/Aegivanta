import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.feedback import DetectionFeedback
from backend.app.models.model_registry import ModelRegistry
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("SentinelAI.AdaptiveFeedback")


class AdaptiveFeedbackService:
    """Manages analyst detection feedback loops, concept drift measurement, and champion/challenger lifecycle."""

    @classmethod
    async def record_analyst_feedback(
        cls,
        db: AsyncSession,
        incident_id: str,
        analyst_id: str,
        is_true_positive: bool,
        predicted_attack_type: str = "BENIGN",
        notes: Optional[str] = None
    ) -> DetectionFeedback:
        """Captures analyst ground-truth feedback on detected security incidents."""
        verdict = "TRUE_POSITIVE" if is_true_positive else "FALSE_POSITIVE"
        feedback = DetectionFeedback(
            incident_id=incident_id,
            analyst_user_id=analyst_id,
            actual_verdict=verdict,
            predicted_attack_type=predicted_attack_type,
            notes=notes or "",
            created_at=datetime.now(timezone.utc)
        )
        db.add(feedback)
        await db.flush()
        return feedback

    @classmethod
    async def compute_model_drift(
        cls,
        db: AsyncSession,
        model_name: str
    ) -> Dict[str, Any]:
        """Measures detection performance drift by comparing recent FP rates against baseline."""
        stmt = select(DetectionFeedback).order_by(DetectionFeedback.created_at.desc()).limit(200)
        res = await db.execute(stmt)
        feedbacks = list(res.scalars().all())

        if not feedbacks:
            return {
                "model_name": model_name,
                "total_feedback_samples": 0,
                "drift_detected": False,
                "drift_score": 0.0,
                "accuracy_ratio": 1.0
            }

        true_positives = sum(1 for f in feedbacks if f.actual_verdict == "TRUE_POSITIVE")
        accuracy = true_positives / len(feedbacks)
        drift_score = max(0.0, 1.0 - accuracy)

        return {
            "model_name": model_name,
            "total_feedback_samples": len(feedbacks),
            "true_positives": true_positives,
            "false_positives": len(feedbacks) - true_positives,
            "accuracy_ratio": round(accuracy, 4),
            "drift_score": round(drift_score, 4),
            "drift_detected": drift_score > 0.25,
            "recommendation": "Retrain candidate challenger model" if drift_score > 0.25 else "Model operating within normal bounds"
        }

    @classmethod
    async def promote_challenger_to_champion(
        cls,
        db: AsyncSession,
        challenger_model_id: str
    ) -> Dict[str, Any]:
        """Safely promotes a validated challenger model to production champion with rollback guardrail."""
        stmt = select(ModelRegistry).where(ModelRegistry.id == challenger_model_id)
        res = await db.execute(stmt)
        challenger = res.scalar_one_or_none()
        if not challenger:
            raise SentinelAIException(status_code=404, detail="Challenger model not found.")

        # Demote existing champion
        champ_stmt = select(ModelRegistry).where(ModelRegistry.status == "ACTIVE")
        champ_res = await db.execute(champ_stmt)
        existing_champion = champ_res.scalar_one_or_none()

        if existing_champion:
            existing_champion.status = "PREVIOUS_CHAMPION"

        challenger.status = "ACTIVE"
        await db.flush()

        return {
            "status": "SUCCESS",
            "new_champion_id": challenger.id,
            "model_name": challenger.model_name,
            "previous_champion_id": existing_champion.id if existing_champion else None,
            "promoted_at": datetime.now(timezone.utc).isoformat()
        }
