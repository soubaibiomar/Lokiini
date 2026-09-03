from enum import Enum
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    PROJECT_NAME: str = "Lokiini / MatOS API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: RuntimeEnvironment = RuntimeEnvironment.DEVELOPMENT
    DEBUG: bool = False

    DATABASE_URL: str = Field(min_length=1)
    REDIS_URL: str = "redis://redis:6379/0"
    MEILISEARCH_URL: str = "http://meilisearch:7700"
    MEILISEARCH_MASTER_KEY: str = Field(min_length=16)

    # Firebase is the sole identity provider. These variables are backend-only.
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_SESSION_COOKIE_NAME: str = "lokiini_session"
    FIREBASE_SESSION_DAYS: int = Field(default=5, ge=1, le=14)
    SESSION_COOKIE_SECURE: bool = False
    CORS_ALLOWED_ORIGINS: str = "http://localhost,http://localhost:3001"

    DEFAULT_CURRENCY: str = "MAD"
    PLATFORM_COMMISSION_PCT: float = 0.15
    EQUIPMENT_MEDIA_DIR: str = "/app/media/equipment"
    EQUIPMENT_MEDIA_MAX_BYTES: int = Field(default=8 * 1024 * 1024, ge=1024, le=20 * 1024 * 1024)
    INSPECTION_EVIDENCE_DIR: str = "/app/media/inspection-evidence"
    INSPECTION_PHOTO_MAX_BYTES: int = Field(default=12 * 1024 * 1024, ge=1024, le=25 * 1024 * 1024)
    INSPECTION_VIDEO_MAX_BYTES: int = Field(default=100 * 1024 * 1024, ge=1024, le=250 * 1024 * 1024)
    DISPUTE_EVIDENCE_DIR: str = "/app/media/dispute-evidence"
    DISPUTE_EVIDENCE_MAX_BYTES: int = Field(default=25 * 1024 * 1024, ge=1024, le=100 * 1024 * 1024)

    DIDIT_API_KEY: Optional[str] = None
    DIDIT_WEBHOOK_SECRET: Optional[str] = None
    DIDIT_WORKFLOW_ID: Optional[str] = None
    DIDIT_API_URL: str = "https://verification.didit.me/v3"
    API_BASE_URL: str = "http://localhost"

    # Internal integration only. Keep n8n off the public production gateway.
    N8N_WEBHOOK_BASE_URL: str = "http://n8n:5678/webhook"
    N8N_WEBHOOK_AUTH_TOKEN: Optional[str] = None

    # Reserved for disabled payment integrations; never expose these to Vite.
    CMI_CLIENT_ID: Optional[str] = None
    CMI_STORE_KEY: Optional[str] = None
    CASHPLUS_API_KEY: Optional[str] = None
    PAYMENT_WEBHOOK_SECRET: Optional[str] = None
    PAYMENT_WEBHOOK_TOLERANCE_SECONDS: int = Field(default=300, ge=30, le=900)

    @model_validator(mode="after")
    def validate_environment_security(self) -> "Settings":
        didit_values = (self.DIDIT_API_KEY, self.DIDIT_WEBHOOK_SECRET, self.DIDIT_WORKFLOW_ID)
        if any(didit_values) and not all(didit_values):
            raise ValueError("DIDIT_API_KEY, DIDIT_WEBHOOK_SECRET and DIDIT_WORKFLOW_ID must be configured together")

        if bool(self.CMI_CLIENT_ID) != bool(self.CMI_STORE_KEY):
            raise ValueError("CMI_CLIENT_ID and CMI_STORE_KEY must be configured together")
        if (self.CMI_CLIENT_ID or self.CASHPLUS_API_KEY) and not self.PAYMENT_WEBHOOK_SECRET:
            raise ValueError("PAYMENT_WEBHOOK_SECRET is required when a payment provider is configured")
        if self.PAYMENT_WEBHOOK_SECRET and len(self.PAYMENT_WEBHOOK_SECRET) < 32:
            raise ValueError("PAYMENT_WEBHOOK_SECRET must contain at least 32 characters")

        if self.ENVIRONMENT == RuntimeEnvironment.DEVELOPMENT:
            return self

        forbidden_markers = (
            "change-me",
            "changeme",
            "replace-me",
            "example",
            "default",
            "demo",
            "secure_pass_2026",
            "master_key_2026",
            "super_secret_key",
        )
        secret_values = {
            "DATABASE_URL": self.DATABASE_URL,
            "MEILISEARCH_MASTER_KEY": self.MEILISEARCH_MASTER_KEY,
            "DIDIT_API_KEY": self.DIDIT_API_KEY,
            "DIDIT_WEBHOOK_SECRET": self.DIDIT_WEBHOOK_SECRET,
            "DIDIT_WORKFLOW_ID": self.DIDIT_WORKFLOW_ID,
            "N8N_WEBHOOK_AUTH_TOKEN": self.N8N_WEBHOOK_AUTH_TOKEN,
            "CMI_STORE_KEY": self.CMI_STORE_KEY,
            "CASHPLUS_API_KEY": self.CASHPLUS_API_KEY,
            "PAYMENT_WEBHOOK_SECRET": self.PAYMENT_WEBHOOK_SECRET,
        }
        for name, value in secret_values.items():
            if value and any(marker in value.lower() for marker in forbidden_markers):
                raise ValueError(f"{name} contains a known placeholder or unsafe default")

        if not self.SESSION_COOKIE_SECURE:
            raise ValueError("SESSION_COOKIE_SECURE must be true outside development")
        if self.DEBUG:
            raise ValueError("DEBUG must be false outside development")
        if not self.API_BASE_URL.lower().startswith("https://"):
            raise ValueError("API_BASE_URL must use HTTPS outside development")
        if not self.cors_origins or any(
            not origin.lower().startswith("https://")
            or "localhost" in origin
            or "127.0.0.1" in origin
            for origin in self.cors_origins
        ):
            raise ValueError("CORS_ALLOWED_ORIGINS must contain only HTTPS origins outside development")
        if not self.FIREBASE_PROJECT_ID:
            raise ValueError("FIREBASE_PROJECT_ID is required outside development")
        if not self.DIDIT_API_KEY or not self.DIDIT_WEBHOOK_SECRET or not self.DIDIT_WORKFLOW_ID:
            raise ValueError("Didit credentials are required outside development")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
