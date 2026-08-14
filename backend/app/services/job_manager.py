"""
backend/app/services/job_manager.py
===================================
Resilient Background Job Manager with Failure Isolation & Exponential Backoff.
Ensures telemetry pipelines, threat feeds, and monitoring workers operate without cascading failure.
"""

from datetime import datetime, timezone
import asyncio
import uuid
import logging
from typing import Dict, Any, Callable, Awaitable, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.job import BackgroundJob
from backend.app.database import AsyncSessionFactory

logger = logging.getLogger("SentinelAI")


class JobManager:
    """Manages background async jobs with execution tracing and isolation."""

    @staticmethod
    async def run_job(
        job_type: str,
        task_func: Callable[[AsyncSession], Awaitable[Any]],
        max_retries: int = 3,
        parameters: Optional[Dict[str, Any]] = None
    ) -> BackgroundJob:
        """
        Executes a background task with failure isolation, retry, and database tracking.
        Never allows unhandled exceptions to crash the calling process.
        """
        job_id = str(uuid.uuid4())
        now_utc = datetime.now(timezone.utc)

        async with AsyncSessionFactory() as db:
            job = BackgroundJob(
                id=job_id,
                job_type=job_type,
                status="RUNNING",
                started_at=now_utc,
                retry_count=0,
                max_retries=max_retries,
                parameters=parameters or {}
            )
            db.add(job)
            await db.commit()

        # Retry Loop with Exponential Backoff
        attempt = 0
        last_error = None
        result_data = None

        while attempt < max_retries:
            try:
                async with AsyncSessionFactory() as session:
                    result_data = await task_func(session)
                    await session.commit()

                # Mark Completed
                async with AsyncSessionFactory() as db:
                    res = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
                    j = res.scalar_one_or_none()
                    if j:
                        j.status = "COMPLETED"
                        j.completed_at = datetime.now(timezone.utc)
                        j.result = result_data if isinstance(result_data, dict) else {"status": "SUCCESS"}
                        await db.commit()
                        await db.refresh(j)
                        return j
            except Exception as exc:
                attempt += 1
                last_error = str(exc)
                logger.warning(f"Background job {job_type} (ID: {job_id}) attempt {attempt} failed: {exc}")
                if attempt < max_retries:
                    backoff = min(10.0, 0.5 * (2 ** attempt))
                    await asyncio.sleep(backoff)

        # Mark Failed
        async with AsyncSessionFactory() as db:
            res = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
            j = res.scalar_one_or_none()
            if j:
                j.status = "FAILED"
                j.completed_at = datetime.now(timezone.utc)
                j.retry_count = attempt
                j.error_message = last_error
                await db.commit()
                await db.refresh(j)
                return j

        return job

    @staticmethod
    async def list_jobs(limit: int = 50, db: AsyncSession = None) -> list:
        """Lists recent background job execution logs."""
        stmt = select(BackgroundJob).order_by(desc(BackgroundJob.started_at)).limit(limit)
        res = await db.execute(stmt)
        return res.scalars().all()
