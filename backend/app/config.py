import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEVELOPMENT_SECRET = "sentinelai_super_secret_jwt_key_2026_change_in_production_32bytes_min"


class Settings(BaseSettings):
    """System configuration settings loaded from environment variables."""

    # General Application Settings
    APP_NAME: str = "SentinelAI"
    APP_ENV: str = "development"
    OPERATING_MODE: str = Field(default="DEMO", description="Operating Mode: DEMO, LAB, or PRODUCTION")
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    PROJECT_VERSION: str = "1.0.0"
    SECRET_KEY: str = INSECURE_DEVELOPMENT_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "sentinel_admin"
    POSTGRES_PASSWORD: str = "sentinel_secure_pass_2026"
    POSTGRES_DB: str = "sentinelai_db"
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
    """Stops accidental production deployments with known development secrets."""
    if settings.APP_ENV.lower() != "production":
        return
    if settings.SECRET_KEY == INSECURE_DEVELOPMENT_SECRET or "CHANGE_ME" in settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        raise RuntimeError("Production requires a unique SECRET_KEY of at least 32 characters.")
    if any(origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1") for origin in settings.CORS_ORIGINS):
        raise RuntimeError("Production CORS_ORIGINS must not use localhost entries.")
