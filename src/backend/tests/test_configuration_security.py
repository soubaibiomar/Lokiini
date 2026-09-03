from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def production_settings(**overrides):
    values = {
        "ENVIRONMENT": "production",
        "DEBUG": False,
        "DATABASE_URL": "postgresql+asyncpg://app:" + ("a" * 32) + "@postgres:5432/lokiini",
        "MEILISEARCH_MASTER_KEY": "b" * 64,
        "FIREBASE_PROJECT_ID": "lokiini-production",
        "SESSION_COOKIE_SECURE": True,
        "CORS_ALLOWED_ORIGINS": "https://lokiini.ma",
        "API_BASE_URL": "https://lokiini.ma",
        "DIDIT_API_KEY": "c" * 32,
        "DIDIT_WEBHOOK_SECRET": "d" * 64,
        "DIDIT_WORKFLOW_ID": "11111111-2222-3333-4444-555555555555",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_production_configuration_accepts_explicit_secure_values():
    settings = production_settings()
    assert settings.ENVIRONMENT.value == "production"
    assert settings.SESSION_COOKIE_SECURE is True


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("SESSION_COOKIE_SECURE", False),
        ("DEBUG", True),
        ("API_BASE_URL", "http://lokiini.ma"),
        ("CORS_ALLOWED_ORIGINS", "http://localhost:3001"),
        ("FIREBASE_PROJECT_ID", ""),
        ("MEILISEARCH_MASTER_KEY", "change-me-in-production"),
    ],
)
def test_production_rejects_unsafe_or_missing_configuration(name, value):
    with pytest.raises(ValidationError):
        production_settings(**{name: value})


def test_didit_credentials_and_workflow_must_be_configured_together():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://app:dev@postgres:5432/lokiini",
            MEILISEARCH_MASTER_KEY="development-key-material",
            DIDIT_API_KEY="configured-without-webhook-secret",
            DIDIT_WEBHOOK_SECRET="",
        )


def test_payment_credentials_require_a_signed_webhook_secret():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://app:dev@postgres:5432/lokiini",
            MEILISEARCH_MASTER_KEY="development-key-material",
            CMI_CLIENT_ID="merchant-id",
            CMI_STORE_KEY="merchant-store-key",
            PAYMENT_WEBHOOK_SECRET="",
        )

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            DATABASE_URL="postgresql+asyncpg://app:dev@postgres:5432/lokiini",
            MEILISEARCH_MASTER_KEY="development-key-material",
            PAYMENT_WEBHOOK_SECRET="too-short",
        )


def test_frontend_examples_contain_only_public_prefixed_variables():
    backend_dir = Path(__file__).resolve().parents[1]
    repo_dir = (
        backend_dir.parent.parent
        if (backend_dir.parent.parent / "src" / "frontend").exists()
        else None
    )
    if not repo_dir:
        pytest.skip("frontend not mounted in container")
    examples = [
        repo_dir / "src/frontend/web/.env.example",
        repo_dir / "src/frontend/mobile/.env.example",
    ]
    for example in examples:
        for line in example.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            name = line.split("=", 1)[0]
            assert name.startswith(("VITE_", "EXPO_PUBLIC_"))

