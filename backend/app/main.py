import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func

from backend.app.config import settings, validate_production_settings
from backend.app.core.logging import logger
from backend.app.core.middleware import RequestTimingAndAuditMiddleware
from backend.app.core.exceptions import SentinelAIException
from backend.app.database import init_db, AsyncSessionFactory
from backend.app.models.user import User
from backend.app.models.incident import Incident
from backend.app.models.model_registry import ModelRegistry
from backend.app.models.audit_log import AuditLog
from backend.app.models.training_job import TrainingJob
from backend.app.security import hash_password, verify_password

# Import Routers
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.users import router as users_router
from backend.app.api.v1.predict import router as predict_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.logs import router as logs_router
from backend.app.api.v1.train import router as train_router
from backend.app.api.v1.websockets import router as websockets_router
from backend.app.api.v1.incidents import router as incidents_router
from backend.app.api.v1.assets import router as assets_router
from backend.app.api.v1.alerts import router as alerts_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.monitoring import router as monitoring_router
from backend.app.api.v1.threat_intel import router as threat_intel_router
from backend.app.api.v1.investigations import router as investigations_router
from backend.app.api.v1.playbooks import router as playbooks_router
from backend.app.api.v1.hunting import router as hunting_router
from backend.app.api.v1.predictive import router as predictive_router
from backend.app.api.v1.threat_graph import router as threat_graph_router
from backend.app.api.v1.campaigns import router as campaigns_router
from backend.app.api.v1.response import router as response_router
from backend.app.api.v1.attack_coverage import router as attack_coverage_router
from backend.app.api.v1.soc_metrics import router as soc_metrics_router


from dotenv import load_dotenv
load_dotenv()

import secrets
import json

def get_default_users():
    def _get_required_user_password(env_var: str) -> str:
        pwd = os.environ.get(env_var)
        if not pwd:
            is_prod = (
                settings.APP_ENV.lower() == "production"
                or settings.OPERATING_MODE.upper() == "PRODUCTION"
                or settings.ENVIRONMENT.lower() == "production"
            )
            if is_prod:
                raise RuntimeError(
                    f"Security Error: Environment variable '{env_var}' is required in production to seed default accounts.\n"
                    f"Set {env_var} in your .env or environment variables."
                )
            # Non-production: still require an explicit password — no silent defaults.
            raise RuntimeError(
                f"Configuration Error: '{env_var}' is not set. "
                f"Add it to your .env file. "
                f"Example development values are in .env.example."
            )
        return pwd

    return [
        (
            "admin",
            "admin@sentinelai.io",
            _get_required_user_password("SENTINEL_ADMIN_PASSWORD"),
            "System Administrator",
            "admin"
        ),
        (
            "analyst",
            "analyst@sentinelai.io",
            _get_required_user_password("SENTINEL_ANALYST_PASSWORD"),
            "Senior Security Analyst",
            "analyst"
        ),
        (
            "viewer",
            "viewer@sentinelai.io",
            _get_required_user_password("SENTINEL_VIEWER_PASSWORD"),
            "Security Operations Viewer",
            "viewer"
        ),
    ]

async def initialize_application() -> None:
    """Creates the schema and seeds required records for a new installation."""
    await init_db()

    async with AsyncSessionFactory() as db:
        user_exists = (await db.execute(select(User.id).limit(1))).scalar_one_or_none()
        default_users = get_default_users()
        if not user_exists:
            logger.info("Seeding default user accounts...")
            db.add_all([
                User(
                    username=username,
                    email=email,
                    password_hash=hash_password(raw_password),
                    full_name=full_name,
                    role=role,
                    is_active=True,
                )
                for username, email, raw_password, full_name, role in default_users
            ])
            await db.commit()
        else:
            # Update password hashes for default accounts if needed
            for username, _, raw_password, _, _ in default_users:
                usr = (await db.execute(select(User).where(User.username == username))).scalar_one_or_none()
                if usr and not verify_password(raw_password, usr.password_hash):
                    usr.password_hash = hash_password(raw_password)
                    db.add(usr)
            await db.commit()

        model_exists = (await db.execute(select(ModelRegistry.id).limit(1))).scalar_one_or_none()
        if not model_exists:
            # Seed from ml/artifacts/metadata.json if generated, otherwise create baseline registry entry
            meta_path = Path("ml/artifacts/metadata.json")
            if meta_path.exists():
                try:
                    from ml.schema.artifact_mapping import resolve_model_artifact_path
                    with meta_path.open("r", encoding="utf-8") as f:
                        meta_data = json.load(f)
                    for item in meta_data.get("leaderboard", []):
                        m_name = item["model_name"]
                        art_path, art_type, actual_sha256, exists = resolve_model_artifact_path(m_name)
                        if not exists:
                            logger.warning("Model artifact for '%s' missing at '%s'; registry seeding skipped.", m_name, art_path)
                            continue
                        is_champ = (m_name == "CatBoost")
                        db.add(ModelRegistry(
                            model_name=m_name,
                            model_version=f"{m_name.lower().replace(' ', '_')}-v1.0",
                            model_type=item["model_type"],
                            accuracy=item.get("cv_accuracy_mean"),
                            f1_score=item.get("cv_f1_mean"),
                            precision_score=item.get("cv_precision_mean"),
                            recall_score=item.get("cv_recall_mean"),
                            roc_auc=item.get("cv_roc_auc"),
                            is_active=is_champ,
                            status="ACTIVE" if is_champ else "BENCHMARK",
                            artifact_path=str(art_path).replace("\\", "/"),
                            artifact_type=art_type,
                            artifact_sha256=actual_sha256
                        ))
                    logger.info("Seeded ModelRegistry from actual training metadata.json and verified artifacts")
                except Exception as e:
                    logger.warning("Unable to seed ModelRegistry from metadata.json: %s", e)

        # Ensure active model is always registered if empty
        active_cnt = (await db.execute(select(func.count(ModelRegistry.id)).where(ModelRegistry.is_active == True))).scalar_one()
        if active_cnt == 0:
            cb_model = (await db.execute(select(ModelRegistry).where(ModelRegistry.model_name == "CatBoost"))).scalar_one_or_none()
            if cb_model:
                cb_model.is_active = True
                cb_model.status = "ACTIVE"
                db.add(cb_model)

        await db.commit()

        # Seed rich operational dataset for demo/development environments
        if settings.OPERATING_MODE.upper() in ["DEMO", "LAB"] or settings.APP_ENV.lower() == "development":
            from backend.app.seed_data import seed_demo_operational_data
            await seed_demo_operational_data(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan context manager."""
    logger.info("Initializing SentinelAI Backend Application Lifespan...")
    validate_production_settings()
    await initialize_application()

    yield
    logger.info("Shutting down SentinelAI Backend Application...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Network Intrusion Detection & Threat Analytics API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Audit Middleware
app.add_middleware(RequestTimingAndAuditMiddleware)


# Custom Exception Handlers
@app.exception_handler(SentinelAIException)
async def custom_sentinel_exception_handler(request: Request, exc: SentinelAIException):
    req_id = getattr(request.state, "request_id", None)
    content = {
        "error": True,
        "status_code": exc.status_code,
        "detail": exc.detail
    }
    if req_id:
        content["request_id"] = req_id
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error("Unhandled server exception [RequestID: %s]: %s", req_id, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "An internal server error occurred.",
            "request_id": req_id
        }
    )


# Include Routers
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(predict_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(logs_router, prefix=settings.API_V1_STR)
app.include_router(train_router, prefix=settings.API_V1_STR)
app.include_router(websockets_router)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(assets_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(monitoring_router, prefix=settings.API_V1_STR)
app.include_router(threat_intel_router, prefix=settings.API_V1_STR)
app.include_router(investigations_router, prefix=settings.API_V1_STR)
app.include_router(playbooks_router, prefix=settings.API_V1_STR)
app.include_router(hunting_router, prefix=settings.API_V1_STR)
app.include_router(predictive_router, prefix=settings.API_V1_STR)
app.include_router(threat_graph_router, prefix=settings.API_V1_STR)
app.include_router(campaigns_router, prefix=settings.API_V1_STR)
app.include_router(response_router, prefix=settings.API_V1_STR)
app.include_router(attack_coverage_router, prefix=settings.API_V1_STR)
app.include_router(soc_metrics_router, prefix=settings.API_V1_STR)
app.include_router(health_router, prefix=settings.API_V1_STR)
