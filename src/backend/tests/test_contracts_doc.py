import asyncio
from datetime import date
from types import SimpleNamespace

import pytest
import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.contract_generator_service import contract_generator_service
from app.schemas.contract_schemas import ContractSignRequest

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
    assert "Dahir formant Code des obligations et des contrats" in doc["contract_text"]
    assert "Yassine Alaoui" in doc["contract_text"]
    assert "Atlas BTP SARL" in doc["contract_text"]
    assert "001234567000088" in doc["contract_text"]
    assert "1250.0 MAD" in doc["contract_text"]
    assert len(doc["contract_sha256"]) == 64

def test_generated_contract_does_not_claim_qualified_signature_or_certificate():
    booking = {
        "id": str(uuid.uuid4()), "nombre_jours": 2,
        "date_debut": "2026-09-01", "date_fin": "2026-09-02",
        "prix_total": 400.0, "montant_caution": 1000.0,
        "payment_method": "cash_cod", "deposit_method": "cash",
    }
    doc = contract_generator_service.generate_lease_contract(
        booking,
        {"titre": "Perceuse", "categorie": "tools", "description": "Avec coffret"},
        {"nom_complet": "Locataire"},
        {"nom_complet": "Propriétaire"},
    )
    assert "ne constitue pas" in doc["important_conditions"][-1]
    assert "CIN Certifiée Didit" not in doc["contract_text"]
    assert "certifiée conforme" not in doc["contract_text"]
    assert "RFC 3161" not in doc["contract_text"]

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


def test_confirmed_contract_response_uses_real_reservation_fields():
    from app.routers.contracts import get_booking_contract

    booking_id = uuid.uuid4()
    renter_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    article_id = uuid.uuid4()
    booking = SimpleNamespace(
        id=booking_id, locataire_id=renter_id, loueur_id=owner_id, article_id=article_id,
        statut="confirmee", total_days=3, date_debut=date(2026, 9, 2),
        date_fin=date(2026, 9, 4), prix_total=600,
        montant_caution=1500, payment_method="cash_cod", contrat_pdf_url=None,
    )
    article = SimpleNamespace(id=article_id, titre="Perceuse", categorie="tools", description="Avec coffret")
    renter = SimpleNamespace(
        id=renter_id, nom_complet="Locataire", cin_number=None, company_ice=None,
        company_name=None, telephone=None, city="Rabat", user_role="renter",
    )
    owner = SimpleNamespace(
        id=owner_id, nom_complet="Propriétaire", cin_number=None, company_ice=None,
        company_name=None, telephone=None, city="Salé", user_role="owner",
    )

    class Result:
        def __init__(self, value): self.value = value
        def scalars(self): return self
        def first(self): return self.value

    class FakeDb:
        def __init__(self): self.values = iter([booking, article, renter, owner])
        async def execute(self, _query): return Result(next(self.values))

    response = asyncio.run(get_booking_contract(booking_id, current_user=renter, db=FakeDb()))
    assert response.booking_status == "confirmee"
    assert response.number_of_days == 3
    assert response.owner.name == "Propriétaire"
    assert response.renter.name == "Locataire"
    assert response.signature_available is False
    assert response.completed is False
