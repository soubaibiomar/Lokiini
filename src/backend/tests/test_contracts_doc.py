import pytest
import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.contract_generator_service import contract_generator_service
from app.services.signature_service import signature_service
from app.schemas.contract_schemas import ContractSignRequest, SignatureCertificateResponse

def test_contract_generator_doc_articles():
    """Test that contract generator outputs mandatory DOC articles and mentions."""
    booking = {
        "id": str(uuid.uuid4()),
        "nombre_jours": 5,
        "date_debut": "2026-09-01",
        "date_fin": "2026-09-05",
        "prix_total": 1250.0,
        "montant_caution": 3000.0
    }
    article = {
        "titre": "Perforateur Burineur SDS Max Bosch",
        "categorie": "tools",
        "description": "Perforateur professionnel avec coffret de forets"
    }
    renter = {
        "nom_complet": "Yassine Alaoui",
        "cin_number": "BE123456",
        "telephone": "+212661000001",
        "city": "Casablanca"
    }
    owner = {
        "nom_complet": "Atlas BTP SARL",
        "company_ice": "001234567000088",
        "telephone": "+212522000000",
        "city": "Casablanca"
    }

    doc = contract_generator_service.generate_lease_contract(booking, article, renter, owner)
    
    assert "BAIL-LOKIINI-" in doc["contract_number"]
    assert "Articles 627 et suivants du Dahir" in doc["contract_text"]
    assert "Yassine Alaoui" in doc["contract_text"]
    assert "Atlas BTP SARL" in doc["contract_text"]
    assert "001234567000088" in doc["contract_text"]
    assert "1250.0 MAD" in doc["contract_text"]
    assert len(doc["contract_sha256"]) == 64

def test_signature_service_seal():
    """Test Loi 53-05 digital signature sealing."""
    contract_hash = "a" * 64
    user_id = str(uuid.uuid4())
    
    sig = signature_service.seal_signature(
        contract_sha256=contract_hash,
        user_id=user_id,
        user_role="locataire",
        ip_address="196.12.34.56"
    )
    
    assert "signature_seal" in sig
    assert len(sig["signature_seal"]) == 64
    assert sig["manifest"]["signatory_user_id"] == user_id
    assert "Loi 53-05" in sig["manifest"]["compliance_law"]

def test_contract_sign_schema_validation():
    """Test ContractSignRequest consent requirement."""
    req = ContractSignRequest(
        consentement_explicite=True,
        ip_address="41.140.10.5"
    )
    assert req.consentement_explicite is True
    assert req.ip_address == "41.140.10.5"

def test_contracts_routes_integrity():
    """Test that all Phase 6 contract routes are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]
    
    assert "/api/v1/contrats/{booking_id}" in paths or "/api/v1/contracts/{booking_id}" in paths
    assert "/api/v1/contrats/{booking_id}/signer" in paths or "/api/v1/contracts/{booking_id}/sign" in paths
    assert "/api/v1/contrats/{booking_id}/certificat" in paths or "/api/v1/contracts/{booking_id}/certificate" in paths
