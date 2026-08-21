import os
import secrets
from typing import List, Optional, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_RUNTIME_DEV_SECRET = secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """
    System configuration settings loaded from environment variables (.env).

    ENVIRONMENT & SECURITY ARCHITECTURE:
    -----------------------------------
    1. Development Mode (Default for bare-metal & local test runs):
       - APP_ENV = "development", OPERATING_MODE = "DEMO"
       - Ephemeral runtime secrets and localhost CORS origins (5173, 3000) are permitted
         to provide a frictionless, zero-configuration local developer experience (DX).
    
    2. Production Mode (Enforced in Docker / Production deployments):
       - APP_ENV = "production", OPERATING_MODE = "PRODUCTION"
       - Fail-closed security boundary: validate_production_settings() is executed on startup.
       - Disallows default secrets, disallows localhost/wildcard CORS, and mandates
         strong passwords and production domains (e.g. https://sentinelai.io).
    """

    # General Application Settings
    APP_NAME: str = "Aegivanta"
    PROJECT_DESCRIPTION: str = "Enterprise AI-Powered Security Operations Platform"
    APP_ENV: str = Field(default="development", description="Application Environment: development, staging, production")
    OPERATING_MODE: str = Field(default="DEMO", description="Operating Mode: DEMO, LAB, or PRODUCTION")
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    PROJECT_VERSION: str = "34.0.0"









    SECRET_KEY: str = Field(default_factory=lambda: os.environ.get("SECRET_KEY", _RUNTIME_DEV_SECRET))








    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # User Accounts Passwords (must be supplied via environment / .env — no hard-coded defaults)
    AEGIVANTA_ADMIN_PASSWORD: Optional[str] = Field(
        default_factory=lambda: os.environ.get("AEGIVANTA_ADMIN_PASSWORD", os.environ.get("SENTINEL_ADMIN_PASSWORD")),
        description="Admin seed password. Required at startup (all environments)."
    )
    SENTINEL_ADMIN_PASSWORD: Optional[str] = Field(
        default=None,
        description="Legacy alias for Admin seed password."
    )
    AEGIVANTA_ANALYST_PASSWORD: Optional[str] = Field(
        default_factory=lambda: os.environ.get("AEGIVANTA_ANALYST_PASSWORD", os.environ.get("SENTINEL_ANALYST_PASSWORD")),
        description="Analyst seed password. Required at startup (all environments)."
    )
    SENTINEL_ANALYST_PASSWORD: Optional[str] = Field(
        default=None,
        description="Legacy alias for Analyst seed password."
    )
    AEGIVANTA_VIEWER_PASSWORD: Optional[str] = Field(
        default_factory=lambda: os.environ.get("AEGIVANTA_VIEWER_PASSWORD", os.environ.get("SENTINEL_VIEWER_PASSWORD")),
        description="Viewer seed password. Required at startup (all environments)."
    )
    SENTINEL_VIEWER_PASSWORD: Optional[str] = Field(
        default=None,
        description="Legacy alias for Viewer seed password."
    )

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = Field(default_factory=lambda: os.environ.get("AEGIVANTA_POSTGRES_USER", os.environ.get("POSTGRES_USER", "sentinel_admin")))
    POSTGRES_PASSWORD: str = Field(default_factory=lambda: os.environ.get("POSTGRES_PASSWORD", ""))
    POSTGRES_DB: str = Field(default_factory=lambda: os.environ.get("AEGIVANTA_POSTGRES_DB", os.environ.get("POSTGRES_DB", "sentinelai_db")))
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./sentinelai.db",
        description="Async Database Connection URL"
    )

    # Redis & Distributed Streaming Settings
    REDIS_HOST: str = Field(default_factory=lambda: os.environ.get("REDIS_HOST", "localhost"))
    REDIS_PORT: int = Field(default_factory=lambda: int(os.environ.get("REDIS_PORT", "6379")))
    REDIS_DB: int = Field(default_factory=lambda: int(os.environ.get("REDIS_DB", "0")))
    REDIS_PASSWORD: Optional[str] = Field(default_factory=lambda: os.environ.get("REDIS_PASSWORD", None))
    REDIS_SSL: bool = Field(default_factory=lambda: os.environ.get("REDIS_SSL", "false").lower() in ["1", "true", "yes"])
    REDIS_URL: str = Field(default_factory=lambda: os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    
    STREAM_TELEMETRY_KEY: str = Field(default_factory=lambda: os.environ.get("STREAM_TELEMETRY_KEY", "aegivanta:telemetry"))
    STREAM_CONSUMER_GROUP: str = Field(default_factory=lambda: os.environ.get("STREAM_CONSUMER_GROUP", "aegivanta:telemetry:group"))
    STREAM_DLQ_KEY: str = Field(default_factory=lambda: os.environ.get("STREAM_DLQ_KEY", "aegivanta:telemetry:dlq"))
    STREAM_PUBSUB_CHANNEL: str = Field(default_factory=lambda: os.environ.get("STREAM_PUBSUB_CHANNEL", "aegivanta:events"))
    STREAM_MAX_RETRIES: int = 3
    STREAM_IDEMPOTENCY_TTL_SECONDS: int = 86400  # 24 hours TTL for cross-worker deduplication

    # ML Engine Settings
    MODEL_ARTIFACTS_DIR: str = "ml/artifacts"
    DEFAULT_MODEL_NAME: str = "Random Forest"
    BATCH_SIZE: int = 128
    SHAP_EXPLAINER_BACKGROUND_SAMPLES: int = 100

    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: (
            ["https://aegivanta.io", "https://sentinelai.io"]
            if os.environ.get("APP_ENV", "").lower() == "production"
            or os.environ.get("OPERATING_MODE", "").upper() == "PRODUCTION"
            else [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://127.0.0.1:5173",
            ]
        ),
        description="Allowed CORS origins list"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean.startswith("[") and v_clean.endswith("]"):
                import json
                try:
                    return json.loads(v_clean)
                except Exception:
                    pass
            return [origin.strip() for origin in v_clean.split(",") if origin.strip()]
        elif isinstance(v, (list, tuple, set)):
            return list(v)
        return v

    # WebSockets Settings
    WEBSOCKET_BROADCAST_INTERVAL_MS: int = 1000

    # SOC Platform Phase 1 Feature Flag
    SOC_PHASE1_ENABLED: bool = Field(
        default=True, 
        description="Feature flag for Phase 1 SOC capabilities: Protected Assets, Alerts, Dynamic Risk Scoring, and Correlation."
    )

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/aegivanta.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate singleton settings instance
settings = Settings()


def validate_production_settings(custom_settings: "Settings" = None) -> None:
    """
    Validates that production environments have secure, non-default configuration.
    Fails safely with a RuntimeError if mandatory production secrets are missing or weak.
    """
    target_settings = custom_settings or settings
    valid_modes = ["DEMO", "LAB", "PRODUCTION"]
    mode_upper = target_settings.OPERATING_MODE.upper()
    if mode_upper not in valid_modes:
        raise RuntimeError(f"Invalid OPERATING_MODE '{target_settings.OPERATING_MODE}'. Valid choices: {valid_modes}")

    is_production = (
        target_settings.APP_ENV.lower() == "production"
        or mode_upper == "PRODUCTION"
        or target_settings.ENVIRONMENT.lower() == "production"
    )
    if not is_production:
        return

    # 1. SECRET_KEY validation in production
    secret_key = target_settings.SECRET_KEY if custom_settings else (os.environ.get("SECRET_KEY", "") or target_settings.SECRET_KEY)
    if not secret_key or len(secret_key) < 32:
        raise RuntimeError("Production requires a unique SECRET_KEY of at least 32 characters in environment variables.")

    insecure_keys = {"secret", "changeme", "sentinelai", "admin", "password", "123456", "default", "default_secret_key"}
    if secret_key.lower() in insecure_keys or any(secret_key.lower().startswith(k) for k in ["default_", "dev_", "test_"]):
        raise RuntimeError("Production SECRET_KEY cannot be a known insecure or default string.")

    # 2. Database Password validation
    pg_pass = target_settings.POSTGRES_PASSWORD if custom_settings else (os.environ.get("POSTGRES_PASSWORD", "") or target_settings.POSTGRES_PASSWORD)
    if not pg_pass or len(pg_pass) < 8:
        raise RuntimeError("Production requires POSTGRES_PASSWORD of at least 8 characters.")

    # 3. User Seed Passwords validation
    admin_pass = os.environ.get("AEGIVANTA_ADMIN_PASSWORD", "") or os.environ.get("SENTINEL_ADMIN_PASSWORD", "")
    if not admin_pass or len(admin_pass) < 8:
        raise RuntimeError("Production requires AEGIVANTA_ADMIN_PASSWORD (or SENTINEL_ADMIN_PASSWORD) of at least 8 characters in environment variables.")

    analyst_pass = os.environ.get("AEGIVANTA_ANALYST_PASSWORD", "") or os.environ.get("SENTINEL_ANALYST_PASSWORD", "")
    if not analyst_pass or len(analyst_pass) < 8:
        raise RuntimeError("Production requires AEGIVANTA_ANALYST_PASSWORD (or SENTINEL_ANALYST_PASSWORD) of at least 8 characters in environment variables.")

    viewer_pass = os.environ.get("AEGIVANTA_VIEWER_PASSWORD", "") or os.environ.get("SENTINEL_VIEWER_PASSWORD", "")
    if not viewer_pass or len(viewer_pass) < 8:
        raise RuntimeError("Production requires AEGIVANTA_VIEWER_PASSWORD (or SENTINEL_VIEWER_PASSWORD) of at least 8 characters in environment variables.")

    # 4. Debug Mode Check
    if target_settings.DEBUG:
        raise RuntimeError("Production requires DEBUG=False.")

    # 5. CORS Origins Check
    if any(origin == "*" or origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1") for origin in target_settings.CORS_ORIGINS):
        raise RuntimeError("Production CORS_ORIGINS must not use wildcard '*' or localhost entries.")
