import os
import secrets
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_RUNTIME_DEV_SECRET = secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """System configuration settings loaded from environment variables."""

    # General Application Settings
    APP_NAME: str = "SentinelAI"
    APP_ENV: str = Field(default="development", description="Application Environment: development, staging, production")
    OPERATING_MODE: str = Field(default="DEMO", description="Operating Mode: DEMO, LAB, or PRODUCTION")
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    PROJECT_VERSION: str = "1.0.0"
    SECRET_KEY: str = Field(default_factory=lambda: os.environ.get("SECRET_KEY", _RUNTIME_DEV_SECRET))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = Field(default_factory=lambda: os.environ.get("POSTGRES_USER", "sentinel_admin"))
    POSTGRES_PASSWORD: str = Field(default_factory=lambda: os.environ.get("POSTGRES_PASSWORD", ""))
    POSTGRES_DB: str = Field(default_factory=lambda: os.environ.get("POSTGRES_DB", "sentinelai_db"))
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./sentinelai.db",
        description="Async Database Connection URL"
    )

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # ML Engine Settings
    MODEL_ARTIFACTS_DIR: str = "ml/artifacts"
    DEFAULT_MODEL_NAME: str = "Random Forest"
    BATCH_SIZE: int = 128
    SHAP_EXPLAINER_BACKGROUND_SAMPLES: int = 100

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # WebSockets Settings
    WEBSOCKET_BROADCAST_INTERVAL_MS: int = 1000

    # SOC Platform Phase 1 Feature Flag
    SOC_PHASE1_ENABLED: bool = Field(
        default=True, 
        description="Feature flag for Phase 1 SOC capabilities: Protected Assets, Alerts, Dynamic Risk Scoring, and Correlation."
    )

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/sentinelai.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate singleton settings instance
settings = Settings()


def validate_production_settings() -> None:
    """Stops accidental production deployments with insecure development configurations."""
    valid_modes = ["DEMO", "LAB", "PRODUCTION"]
    mode_upper = settings.OPERATING_MODE.upper()
    if mode_upper not in valid_modes:
        raise RuntimeError(f"Invalid OPERATING_MODE '{settings.OPERATING_MODE}'. Valid choices: {valid_modes}")

    is_production = (settings.APP_ENV.lower() == "production" or mode_upper == "PRODUCTION")
    if not is_production:
        return

    if not os.environ.get("SECRET_KEY") or len(settings.SECRET_KEY) < 32:
        raise RuntimeError("Production requires a unique SECRET_KEY of at least 32 characters in environment variables.")

    if not os.environ.get("POSTGRES_PASSWORD"):
        raise RuntimeError("Production requires POSTGRES_PASSWORD environment variable to be set.")

    if not os.environ.get("SENTINEL_ADMIN_PASSWORD"):
        raise RuntimeError("Production requires SENTINEL_ADMIN_PASSWORD environment variable to be set.")

    if not os.environ.get("SENTINEL_ANALYST_PASSWORD"):
        raise RuntimeError("Production requires SENTINEL_ANALYST_PASSWORD environment variable to be set.")

    if not os.environ.get("SENTINEL_VIEWER_PASSWORD"):
        raise RuntimeError("Production requires SENTINEL_VIEWER_PASSWORD environment variable to be set.")

    if settings.DEBUG:
        raise RuntimeError("Production requires DEBUG=False.")

    if any(origin == "*" or origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1") for origin in settings.CORS_ORIGINS):
        raise RuntimeError("Production CORS_ORIGINS must not use wildcard '*' or localhost entries.")
