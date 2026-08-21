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
from backend.app.api.v1.telemetry import router as telemetry_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.adaptive_ml import router as adaptive_ml_router
from backend.app.api.v1.organizations import router as organizations_router
from backend.app.api.v1.tenants import router as tenants_router
from backend.app.api.v1.api_keys import router as api_keys_router
from backend.app.api.v1.subscriptions import router as subscriptions_router
from backend.app.api.v1.billing_webhooks import router as billing_webhooks_router
from backend.app.api.v1.onboarding import router as onboarding_router
from backend.app.api.v1.sensors import router as sensors_router
from backend.app.api.v1.integrations import router as integrations_router
from backend.app.api.v1.identity import router as identity_router
from backend.app.api.v1.scim import router as scim_router
from backend.app.api.v1.security_policies import router as security_policies_router
from backend.app.api.v1.security_posture import router as security_posture_router
from backend.app.api.v1.customer_security_events import router as customer_security_events_router
from backend.app.api.v1.detection_rules import router as detection_rules_router
from backend.app.api.v1.ai_copilot import router as ai_copilot_router
from backend.app.api.v1.compliance import router as compliance_router
from backend.app.api.v1.detection_quality import router as detection_quality_router
from backend.app.api.v1.alert_intelligence import router as alert_intelligence_router
from backend.app.api.v1.incident_workflow import router as incident_workflow_router
from backend.app.api.v1.investigation_search import router as investigation_search_router
from backend.app.api.v1.security_value import router as security_value_router
from backend.app.api.v1.autonomous_response import router as autonomous_response_router
from backend.app.api.v1.security_validation import router as security_validation_router
from backend.app.api.v1.security_simulations import router as security_simulations_router
from backend.app.api.v1.security_intelligence import router as security_intelligence_router
from backend.app.api.v1.threat_intelligence_platform import router as threat_intelligence_platform_router
from backend.app.api.v1.threat_hunting_workbench import router as threat_hunting_workbench_router
from backend.app.api.v1.soar_v2 import router as soar_v2_router
from backend.app.api.v1.ai_security_intelligence import router as ai_security_intelligence_router
from backend.app.api.v1.cloud_security import router as cloud_security_router
from backend.app.api.v1.endpoint_xdr import router as endpoint_xdr_router
from backend.app.api.v1.integration_ecosystem import router as integration_ecosystem_router

from backend.app.api.v1.global_ops import router as global_ops_router
from backend.app.api.v1.continuous_security_validation import router as continuous_security_validation_router
from backend.app.api.v1.soc_cases import router as soc_cases_router
from backend.app.api.v1.threat_hunting_v2 import router as threat_hunting_v2_router
from backend.app.api.v1.ai_analyst_v2 import router as ai_analyst_v2_router
from backend.app.api.v1.sre_ops import router as sre_ops_router
from backend.app.api.v1.security_scorecard import router as security_scorecard_router
from backend.app.api.v1.enterprise_iam import router as enterprise_iam_router
from backend.app.api.v1.supply_chain import router as supply_chain_router
from backend.app.api.v1.llm_security import router as llm_security_router
from backend.app.api.v1.attack_surface import router as attack_surface_router
from backend.app.api.v1.threat_intel_v2 import router as threat_intel_v2_router
from backend.app.api.v1.deception import router as deception_router
from backend.app.api.v1.vulnerability_mgmt import router as vulnerability_mgmt_router


























from dotenv import load_dotenv
load_dotenv()

import secrets
import json

def get_default_users():
    def _get_required_user_password(primary_var: str, legacy_var: str) -> str:
        pwd = os.environ.get(primary_var) or os.environ.get(legacy_var)
        if not pwd:
            is_prod = (
                settings.APP_ENV.lower() == "production"
                or settings.OPERATING_MODE.upper() == "PRODUCTION"
                or settings.ENVIRONMENT.lower() == "production"
            )
            if is_prod:
                raise RuntimeError(
                    f"Security Error: Environment variable '{primary_var}' (or '{legacy_var}') is required in production to seed default accounts.\n"
                    f"Set {primary_var} in your .env or environment variables."
                )
            # Non-production: still require an explicit password — no silent defaults.
            raise RuntimeError(
                f"Configuration Error: '{primary_var}' is not set. "
                f"Add it to your .env file. "
                f"Example development values are in .env.example."
            )
        return pwd

    return [
        (
            "admin",
            "admin@aegivanta.io",
            _get_required_user_password("AEGIVANTA_ADMIN_PASSWORD", "SENTINEL_ADMIN_PASSWORD"),
            "System Administrator",
            "admin"
        ),
        (
            "analyst",
            "analyst@aegivanta.io",
            _get_required_user_password("AEGIVANTA_ANALYST_PASSWORD", "SENTINEL_ANALYST_PASSWORD"),
            "Senior Security Analyst",
            "analyst"
        ),
        (
            "viewer",
            "viewer@aegivanta.io",
            _get_required_user_password("AEGIVANTA_VIEWER_PASSWORD", "SENTINEL_VIEWER_PASSWORD"),
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
    logger.info("Initializing Aegivanta Backend Application Lifespan...")
    validate_production_settings()
    await initialize_application()

    yield
    logger.info("Shutting down Aegivanta Backend Application...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI-Powered Security Operations Platform API",
    version=settings.PROJECT_VERSION,
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
app.include_router(telemetry_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(adaptive_ml_router, prefix=settings.API_V1_STR)
app.include_router(organizations_router, prefix=settings.API_V1_STR)
app.include_router(tenants_router, prefix=settings.API_V1_STR)
app.include_router(api_keys_router, prefix=settings.API_V1_STR)
app.include_router(subscriptions_router, prefix=settings.API_V1_STR)
app.include_router(billing_webhooks_router, prefix=settings.API_V1_STR)
app.include_router(onboarding_router, prefix=settings.API_V1_STR)
app.include_router(sensors_router, prefix=settings.API_V1_STR)
app.include_router(integrations_router, prefix=settings.API_V1_STR)
app.include_router(identity_router, prefix=settings.API_V1_STR)
app.include_router(scim_router, prefix=settings.API_V1_STR)
app.include_router(security_policies_router, prefix=settings.API_V1_STR)
app.include_router(security_posture_router, prefix=settings.API_V1_STR)
app.include_router(customer_security_events_router, prefix=settings.API_V1_STR)
app.include_router(detection_rules_router, prefix=settings.API_V1_STR)
app.include_router(ai_copilot_router, prefix=settings.API_V1_STR)
app.include_router(compliance_router, prefix=settings.API_V1_STR)
app.include_router(detection_quality_router, prefix=settings.API_V1_STR)
app.include_router(alert_intelligence_router, prefix=settings.API_V1_STR)
app.include_router(incident_workflow_router, prefix=settings.API_V1_STR)
app.include_router(investigation_search_router, prefix=settings.API_V1_STR)
app.include_router(security_value_router, prefix=settings.API_V1_STR)
app.include_router(autonomous_response_router, prefix=settings.API_V1_STR)
app.include_router(security_validation_router, prefix=settings.API_V1_STR)
app.include_router(security_simulations_router, prefix=settings.API_V1_STR)
app.include_router(security_intelligence_router, prefix=settings.API_V1_STR)
app.include_router(threat_intelligence_platform_router, prefix=settings.API_V1_STR)
app.include_router(threat_hunting_workbench_router, prefix=settings.API_V1_STR)
app.include_router(soar_v2_router, prefix=settings.API_V1_STR)
app.include_router(ai_security_intelligence_router, prefix=settings.API_V1_STR)
app.include_router(cloud_security_router, prefix=settings.API_V1_STR)
app.include_router(endpoint_xdr_router, prefix=settings.API_V1_STR)
app.include_router(integration_ecosystem_router, prefix=settings.API_V1_STR)
app.include_router(global_ops_router, prefix=settings.API_V1_STR)
app.include_router(continuous_security_validation_router, prefix=settings.API_V1_STR)
app.include_router(soc_cases_router, prefix=settings.API_V1_STR)
app.include_router(threat_hunting_v2_router, prefix=settings.API_V1_STR)
app.include_router(ai_analyst_v2_router, prefix=settings.API_V1_STR)
app.include_router(sre_ops_router, prefix=settings.API_V1_STR)
app.include_router(security_scorecard_router, prefix=settings.API_V1_STR)
app.include_router(enterprise_iam_router, prefix=settings.API_V1_STR)
app.include_router(supply_chain_router, prefix=settings.API_V1_STR)
app.include_router(llm_security_router, prefix=settings.API_V1_STR)
app.include_router(attack_surface_router, prefix=settings.API_V1_STR)
app.include_router(threat_intel_v2_router, prefix=settings.API_V1_STR)
app.include_router(deception_router, prefix=settings.API_V1_STR)
app.include_router(vulnerability_mgmt_router, prefix=settings.API_V1_STR)
app.include_router(health_router, prefix=settings.API_V1_STR)






















# ---------------------------------------------------------------------------
# Phase 3.12: Prometheus /metrics endpoint
# ---------------------------------------------------------------------------
from fastapi.responses import Response as FastAPIResponse
from backend.app.observability.metrics import get_metrics_response, PROMETHEUS_AVAILABLE
from backend.app.observability.structured_logging import configure_structured_logging

# Initialize structured JSON logging at startup
configure_structured_logging(level="INFO", service_name="SentinelAI")


@app.get(
    "/metrics",
    include_in_schema=False,
    summary="Prometheus metrics endpoint",
    description="Exposes Prometheus-format metrics for scraping. Restricted to internal monitoring."
)
async def prometheus_metrics():
    """Prometheus /metrics scrape endpoint."""
    content, content_type = get_metrics_response()
    return FastAPIResponse(content=content, media_type=content_type)
