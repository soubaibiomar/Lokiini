import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lokiini / MatOS API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://lokiini_user:lokiini_secure_pass_2026@postgres:5432/lokiini_db"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    MEILISEARCH_URL: str = os.getenv("MEILISEARCH_URL", "http://meilisearch:7700")
    MEILISEARCH_MASTER_KEY: str = os.getenv("MEILISEARCH_MASTER_KEY", "lokiini_meili_master_key_2026")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "lokiini_jwt_super_secret_key_morocco_2026_cndp")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    DEFAULT_CURRENCY: str = "MAD"
    PLATFORM_COMMISSION_PCT: float = 0.15 # 15% pour particuliers, 7% pour pros

    # Didit KYC & Webhooks
    DIDIT_API_KEY: str = os.getenv("DIDIT_API_KEY", "didit_demo_api_key_morocco")
    DIDIT_WEBHOOK_SECRET: str = os.getenv("DIDIT_WEBHOOK_SECRET", "didit_webhook_secret_hmac_2026")
    DIDIT_API_URL: str = os.getenv("DIDIT_API_URL", "https://api.didit.me/v1")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost")

settings = Settings()
