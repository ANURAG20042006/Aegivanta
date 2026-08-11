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
from backend.app.security import hash_password

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


DEFAULT_USERS = [
    ("admin", "admin@sentinelai.local", "AdminSecure2026!", "System Administrator", "admin"),
    ("analyst", "analyst@sentinelai.local", "AnalystSecure2026!", "Senior Security Analyst", "analyst"),
    ("viewer", "viewer@sentinelai.local", "ViewerSecure2026!", "Security Operations Viewer", "viewer"),
]

DEFAULT_MODELS = [
    ("Random Forest", "Classical", 0.9885, 0.9872, 0.9890, 0.9854, 0.994, True, "ml/artifacts/random_forest.joblib"),
    ("XGBoost", "Boosting", 0.9912, 0.9901, 0.9920, 0.9882, 0.997, False, "ml/artifacts/xgboost.joblib"),
    ("LightGBM", "Boosting", 0.9895, 0.9880, 0.9899, 0.9861, 0.995, False, "ml/artifacts/lightgbm.joblib"),
    ("CatBoost", "Boosting", 0.9905, 0.9892, 0.9910, 0.9874, 0.996, False, "ml/artifacts/catboost.joblib"),
    ("Decision Tree", "Classical", 0.9740, 0.9721, 0.9750, 0.9692, 0.981, False, "ml/artifacts/decision_tree.joblib"),
    ("Logistic Regression", "Classical", 0.9250, 0.9210, 0.9280, 0.9142, 0.950, False, "ml/artifacts/logistic_regression.joblib"),
    ("SVM", "Classical", 0.9520, 0.9490, 0.9550, 0.9431, 0.972, False, "ml/artifacts/svm.joblib"),
    ("KNN", "Classical", 0.9610, 0.9580, 0.9630, 0.9531, 0.978, False, "ml/artifacts/knn.joblib"),
    ("Naive Bayes", "Classical", 0.8840, 0.8790, 0.8890, 0.8692, 0.921, False, "ml/artifacts/naive_bayes.joblib"),
    ("1D-CNN", "DeepLearning", 0.9860, 0.9845, 0.9870, 0.9820, 0.992, False, "ml/artifacts/1d-cnn.joblib"),
    ("LSTM", "DeepLearning", 0.9875, 0.9860, 0.9880, 0.9840, 0.993, False, "ml/artifacts/lstm.joblib"),
    ("Autoencoder", "DeepLearning", 0.9790, 0.9770, 0.9800, 0.9740, 0.987, False, "ml/artifacts/autoencoder.joblib"),
]


async def initialize_application() -> None:
    """Creates the schema and seeds required records for a new installation."""
    await init_db()

    async with AsyncSessionFactory() as db:
        user_exists = (await db.execute(select(User.id).limit(1))).scalar_one_or_none()
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
                for username, email, raw_password, full_name, role in DEFAULT_USERS
            ])

        model_exists = (await db.execute(select(ModelRegistry.id).limit(1))).scalar_one_or_none()
        if not model_exists:
            logger.info("Seeding ML model registry benchmark records...")
            db.add_all([
                ModelRegistry(
                    model_name=model_name,
                    model_type=model_type,
                    accuracy=accuracy,
                    f1_score=f1_score,
                    precision_score=precision_score,
                    recall_score=recall_score,
                    roc_auc=roc_auc,
                    is_active=is_active,
                    artifact_path=artifact_path,
                )
                for model_name, model_type, accuracy, f1_score, precision_score, recall_score, roc_auc, is_active, artifact_path in DEFAULT_MODELS
            ])

        registry_paths = {model[0]: model[-1] for model in DEFAULT_MODELS}
        existing_models = (await db.execute(select(ModelRegistry))).scalars().all()
        registry_paths_updated = False
        for model in existing_models:
            expected_path = registry_paths.get(model.model_name)
            if expected_path and model.artifact_path != expected_path:
                model.artifact_path = expected_path
                registry_paths_updated = True

        if not user_exists or not model_exists or registry_paths_updated:
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


# Custom Exception Handler
@app.exception_handler(SentinelAIException)
async def custom_sentinel_exception_handler(request: Request, exc: SentinelAIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail
        },
        headers=exc.headers
    )


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0"
    }


# Include Routers
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
