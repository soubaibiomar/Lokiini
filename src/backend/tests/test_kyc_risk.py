import pytest
import sys
import uuid
import hmac
import hashlib
import json
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.didit_service import didit_service
from app.services.risk_service import risk_service
from app.schemas.kyc_schemas import KYCInitiateResponse, KYCStatusResponse
from app.core.config import settings

def test_didit_session_initiation_mock():
    """Test Didit session generation with token and verification URL."""
    import asyncio
    user_id = str(uuid.uuid4())
    res = asyncio.run(didit_service.initiate_verification_session(user_id, "test@lokiini.ma", "+212661000001"))
    
    assert "session_id" in res
    assert "verification_url" in res
    assert res["status"] == "initiated"
    assert user_id.replace("-", "")[:8] in res["session_id"]

def test_hmac_webhook_signature_verification():
    """Test HMAC-SHA256 signature validation."""
    secret = settings.DIDIT_WEBHOOK_SECRET
    payload = json.dumps({"event": "session.approved", "vendor_data": str(uuid.uuid4()), "status": "approved"}).encode("utf-8")
    
    valid_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    assert didit_service.verify_webhook_signature(payload, valid_sig) is True

    invalid_sig = "fake_signature_hex_1234567890abcdef"
    assert didit_service.verify_webhook_signature(payload, invalid_sig) is False
    assert didit_service.verify_webhook_signature(payload, None) is False

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
