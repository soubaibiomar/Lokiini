import pytest
import asyncio
import sys
import uuid
import hmac
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock
from fastapi import HTTPException
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.didit_service import didit_service
from app.services.kyc_lifecycle import (
    KYCStatus,
    KYCTransitionError,
    apply_provider_status,
    map_provider_status,
    transition,
)
from app.services.risk_service import risk_service
from app.schemas.kyc_schemas import DiditWebhookPayload, KYCInitiateRequest, KYCStatusResponse
from app.core.config import settings
from pydantic import ValidationError

def test_didit_demo_configuration_does_not_approve_or_create_a_session(monkeypatch):
    """A placeholder Didit key must fail closed instead of returning a mock session."""
    import asyncio
    monkeypatch.setattr(didit_service, "api_key", "didit_demo_key")
    user_id = str(uuid.uuid4())
    with pytest.raises(RuntimeError):
        asyncio.run(didit_service.initiate_verification_session(user_id, "test@lokiini.ma", "+212661000001"))



def test_didit_v3_session_contract_sends_no_user_pii(monkeypatch):
    calls = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "session_id": "provider-session",
                "session_token": "provider-token",
                "url": "https://verify.didit.me/provider-session",
                "status": "Not Started",
            }

    class FakeClient:
        def __init__(self, **kwargs):
            calls["client"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, url, *, json, headers):
            calls.update(url=url, payload=json, headers=headers)
            return FakeResponse()

    monkeypatch.setattr("httpx.AsyncClient", FakeClient)
    monkeypatch.setattr(didit_service, "api_key", "real-provider-key")
    monkeypatch.setattr(didit_service, "api_url", "https://verification.didit.me/v3")
    monkeypatch.setattr(settings, "DIDIT_WORKFLOW_ID", "workflow-id")
    result = asyncio.run(didit_service.initiate_verification_session(
        str(uuid.uuid4()), email="private@example.ma", phone="+212600000000"
    ))

    assert calls["url"] == "https://verification.didit.me/v3/session/"
    assert calls["payload"].keys() == {"vendor_data", "workflow_id"}
    assert calls["headers"]["x-api-key"] == "real-provider-key"
    assert result["provider_status"] == "Not Started"

def test_hmac_webhook_signature_verification(monkeypatch):
    """Test HMAC-SHA256 signature validation."""
    secret = "real-test-webhook-secret-with-sufficient-entropy"
    monkeypatch.setattr(didit_service, "webhook_secret", secret)
    payload = json.dumps({"event": "session.approved", "vendor_data": str(uuid.uuid4()), "status": "approved"}).encode("utf-8")
    
    valid_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    assert didit_service.verify_webhook_signature(payload, valid_sig) is True

    invalid_sig = "fake_signature_hex_1234567890abcdef"
    assert didit_service.verify_webhook_signature(payload, invalid_sig) is False
    assert didit_service.verify_webhook_signature(payload, None) is False


def test_v3_canonical_signature_and_timestamp(monkeypatch):
    secret = "real-test-webhook-secret-with-sufficient-entropy"
    monkeypatch.setattr(didit_service, "webhook_secret", secret)
    data = {"status": "Approved", "vendor_data": "utilisateur-é", "timestamp": 2_000}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    signature = hmac.new(secret.encode(), canonical, hashlib.sha256).hexdigest()
    raw = json.dumps(data).encode()
    assert didit_service.verify_webhook_signature(
        raw, signature, timestamp_header="2000", parsed_payload=data, now=2001
    )
    assert not didit_service.verify_webhook_signature(
        raw, signature, timestamp_header="2000", parsed_payload=data, now=2301
    )

def test_placeholder_webhook_secret_is_rejected():
    payload = b'{}'
    signature = hmac.new(b"test-only-didit-webhook-secret", payload, hashlib.sha256).hexdigest()
    assert didit_service.verify_webhook_signature(payload, signature) is False


def test_only_exact_provider_approval_verifies():
    assert map_provider_status("Approved") == KYCStatus.VERIFIED
    assert map_provider_status("completed") == KYCStatus.REQUIRES_ACTION
    assert map_provider_status("Completed") == KYCStatus.REQUIRES_ACTION
    assert map_provider_status("In Review") == KYCStatus.IN_REVIEW
    assert map_provider_status("Resubmitted") == KYCStatus.REQUIRES_ACTION
    assert map_provider_status("Abandoned") == KYCStatus.REQUIRES_ACTION


def test_provider_status_is_separate_from_internal_status():
    user = SimpleNamespace(
        statut_verification="pending",
        kyc_provider_status="In Progress",
        verifie_le=None,
    )
    result = apply_provider_status(user, "Approved")
    assert result == KYCStatus.VERIFIED
    assert user.statut_verification == "verified"
    assert user.kyc_provider_status == "Approved"
    assert user.verifie_le is not None


def test_invalid_internal_transition_is_rejected():
    user = SimpleNamespace(statut_verification="rejected", kyc_provider_status="Declined", verifie_le=None)
    with pytest.raises(KYCTransitionError):
        transition(user, KYCStatus.NOT_STARTED)


def test_client_cannot_choose_kyc_subject_or_status():
    with pytest.raises(ValidationError):
        KYCInitiateRequest.model_validate({"user_id": str(uuid.uuid4())})
    with pytest.raises(ValidationError):
        KYCInitiateRequest.model_validate({"status": "verified"})


def test_provider_error_does_not_change_internal_status(monkeypatch):
    from app.routers.kyc import initiate_kyc_session

    user = SimpleNamespace(
        id=uuid.uuid4(),
        statut_verification="requires_action",
        didit_session_id="existing-session",
        kyc_last_event_id="existing-event",
        kyc_provider_status="Abandoned",
        verifie_le=None,
    )
    db = SimpleNamespace(commit=AsyncMock())
    monkeypatch.setattr(
        didit_service,
        "initiate_verification_session",
        AsyncMock(side_effect=RuntimeError("provider unavailable")),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(initiate_kyc_session(None, user, db))
    assert exc.value.status_code == 503
    assert user.statut_verification == "requires_action"
    assert user.didit_session_id == "existing-session"
    db.commit.assert_not_awaited()


def test_webhook_schema_discards_biometric_decision_material():
    payload = DiditWebhookPayload.model_validate({
        "event_id": str(uuid.uuid4()),
        "webhook_type": "status.updated",
        "timestamp": 2_000,
        "session_id": str(uuid.uuid4()),
        "vendor_data": str(uuid.uuid4()),
        "status": "Approved",
        "decision": {"liveness_checks": [{"score": 99.9, "portrait_image": "base64"}]},
    })
    assert "decision" not in payload.model_dump()


def test_public_kyc_status_has_no_fake_score_or_provider_payload():
    fields = KYCStatusResponse.model_fields
    assert "kyc_liveness_score" not in fields
    assert "provider_status" not in fields

def test_risk_service_high_risk():
    """Test classification of high risk items (BTP, heavy deposit, high daily rate)."""
    # 1. BTP category
    r1 = risk_service.evaluate_risk(categorie="btp", prix_par_jour=200, montant_caution=1500)
    assert r1["niveau_risque"] == "eleve"
    assert r1["kyc_obligatoire"] is True
    assert r1["caution_obligatoire"] is True

    # 2. Heavy deposit >= 3000 MAD
    r2 = risk_service.evaluate_risk(categorie="outdoor", prix_par_jour=100, montant_caution=3500)
    assert r2["niveau_risque"] == "eleve"

    # 3. High daily rate >= 500 MAD
    r3 = risk_service.evaluate_risk(categorie="tools", prix_par_jour=600, montant_caution=1000)
    assert r3["niveau_risque"] == "eleve"

def test_risk_service_medium_risk():
    """Test classification of medium risk items (500 - 3000 MAD deposit or >=150 MAD daily)."""
    r1 = risk_service.evaluate_risk(categorie="tools", prix_par_jour=180, montant_caution=1200)
    assert r1["niveau_risque"] == "moyen"
    assert r1["kyc_obligatoire"] is True
    assert r1["caution_obligatoire"] is False

    r2 = risk_service.evaluate_risk(categorie="cleaning", prix_par_jour=100, montant_caution=600)
    assert r2["niveau_risque"] == "moyen"
    assert r2["kyc_obligatoire"] is True

def test_risk_service_low_risk():
    """Test classification of low risk everyday items (<500 MAD deposit and <150 MAD daily)."""
    r1 = risk_service.evaluate_risk(categorie="small_tools", prix_par_jour=50, montant_caution=200)
    assert r1["niveau_risque"] == "faible"
    assert r1["kyc_obligatoire"] is False
    assert r1["caution_obligatoire"] is False

def test_kyc_routes_integrity():
    """Test that all Phase 2 KYC endpoints are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]
    
    assert "/api/v1/auth/kyc/initier" in paths or "/api/v1/kyc/initier" in paths
    assert "/api/v1/auth/kyc/document" in paths or "/api/v1/kyc/document" in paths
    assert "/api/v1/auth/kyc/selfie" in paths or "/api/v1/kyc/selfie" in paths
    assert "/api/v1/auth/kyc/webhook/didit" in paths or "/api/v1/kyc/webhook/didit" in paths
    assert "/api/v1/auth/kyc/statut/{user_id}" in paths or "/api/v1/kyc/statut/{user_id}" in paths
    assert "/api/v1/kyc/verify" in paths

    initiate_schema = paths["/api/v1/auth/kyc/initier"]["post"]
    assert "user_id" not in json.dumps(initiate_schema)
    assert "liveness_score" not in json.dumps(paths)
