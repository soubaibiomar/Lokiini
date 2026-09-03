import asyncio
import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import pytest
from app.main import app
from app.schemas.equipment_schemas import EquipmentCreateRequest


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = (
    BACKEND_DIR.parent.parent
    if (BACKEND_DIR.parent.parent / "src" / "frontend").exists()
    else None
)


def test_openapi_documents_structured_errors_for_every_operation():
    schema = app.openapi()
    assert "APIErrorResponse" in schema["components"]["schemas"]
    for path_item in schema["paths"].values():
        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            assert operation["responses"]["403"]["content"]["application/json"]["schema"]["$ref"].endswith(
                "/APIErrorResponse"
            )


def test_request_id_is_preserved_and_returned():
    with TestClient(app) as client:
        response = client.get("/api/v1/health", headers={"X-Request-ID": "contract-test-request"})
        unauthorized = client.get("/api/v1/auth/me", headers={"X-Request-ID": "auth-test-request"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "contract-test-request"
    assert unauthorized.status_code == 401
    assert unauthorized.headers["X-Request-ID"] == "auth-test-request"
    assert unauthorized.json() == {
        "statut": "erreur",
        "erreur": {
            "code": "AUTH_REQUIRED",
            "message": "Authentification requise.",
            "details": None,
        },
        "request_id": "auth-test-request",
    }


def test_exported_frontend_contract_matches_fastapi():
    if not REPO_DIR:
        pytest.skip("frontend not mounted in container")
    exported = REPO_DIR / "src/frontend/shared/api/openapi.json"
    assert exported.exists(), "Run scripts/export_openapi.py before committing API changes"
    assert json.loads(exported.read_text(encoding="utf-8")) == app.openapi()


def test_web_api_layer_has_no_direct_fetch_or_silent_error_fallbacks():
    if not REPO_DIR:
        pytest.skip("frontend not mounted in container")
    api_source = (REPO_DIR / "src/frontend/web/src/services/api.js").read_text(encoding="utf-8")
    assert "fetch(" not in api_source
    assert "catch (" not in api_source
    assert "return null" not in api_source
    assert "return []" not in api_source


def test_equipment_openapi_payload_maps_to_real_model_fields(monkeypatch):
    from app.routers import equipment

    class FakeDb:
        article = None

        def add(self, article):
            self.article = article

        async def commit(self):
            return None

        async def refresh(self, _article):
            return None

    db = FakeDb()
    monkeypatch.setattr(equipment.meilisearch_service, "index_article", AsyncMock())
    payload = EquipmentCreateRequest(
        titre="Perceuse professionnelle",
        description="Perceuse de chantier avec coffret",
        categorie="tools",
        prix_par_jour=100,
        montant_caution=500,
        photos=["https://example.test/perceuse.jpg"],
        specs={"puissance": "800W"},
        city="Rabat",
        adresse_approximative="Agdal",
    )
    result = asyncio.run(equipment.create_equipment(
        payload,
        SimpleNamespace(id=uuid.uuid4()),
        db,
    ))
    assert result["statut"] == "succes"
    assert db.article.titre == payload.titre
    assert db.article.specs_json == payload.specs
    assert db.article.adresse == "Agdal"
    assert db.article.localisation is None
