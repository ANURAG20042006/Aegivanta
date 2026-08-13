import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

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
from backend.app.api.v1.health import router as health_router


from dotenv import load_dotenv
load_dotenv()

import secrets
import json

def get_default_users():
    def _get_required_user_password(env_var: str) -> str:
        pwd = os.environ.get(env_var)
        if not pwd:
            raise RuntimeError(
                f"Security Error: Environment variable '{env_var}' is required to seed default accounts.\n"
                f"Set {env_var} in your .env or environment variables."
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
                    with meta_path.open("r", encoding="utf-8") as f:
                        meta_data = json.load(f)
                    for item in meta_data.get("leaderboard", []):
                        db.add(ModelRegistry(
                            model_name=item["model_name"],
                            model_version=f"{item['model_name'].lower().replace(' ', '_')}-v1.0",
                            model_type=item["model_type"],
                            accuracy=item.get("cv_accuracy_mean"),
                            f1_score=item.get("cv_f1_mean"),
                            precision_score=item.get("cv_precision_mean"),
                            recall_score=item.get("cv_recall_mean"),
                            roc_auc=item.get("cv_roc_auc"),
                            is_active=False,
                            artifact_path=f"ml/artifacts/{item['model_name'].lower().replace(' ', '_')}.joblib"
                        ))
                    logger.info("Seeded ModelRegistry from actual training metadata.json")
                except Exception as e:
                    logger.warning("Unable to seed ModelRegistry from metadata.json: %s", e)

        if not user_exists or not model_exists:
            await db.commit()


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
app.include_router(health_router, prefix=settings.API_V1_STR)
