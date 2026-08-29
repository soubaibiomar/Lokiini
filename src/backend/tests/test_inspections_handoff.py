import pytest
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.inspection_seal_service import inspection_seal_service
from app.schemas.inspection_schemas import (
    CheckInSubmissionRequest, CheckOutSubmissionRequest,
    InspectionSealResponse, CashReceiptResponse
)

def test_deterministic_sha256_seal_generation():
    """Test deterministic calculation of SHA-256 seal."""
    booking_id = str(uuid.uuid4())
    ts = datetime(2026, 9, 1, 10, 30, 0)
    photos = ["https://lokiini.ma/p1.jpg", "https://lokiini.ma/p2.jpg"]
    
    seal1 = inspection_seal_service.generate_sha256_seal(
        booking_id=booking_id,
        type_remise="retrait",
        photos=photos,
        video_url="https://lokiini.ma/video.mp4",
        lat=33.5731,
        lng=-7.5898,
        notes="Matériel propre et fonctionnel",
        timestamp=ts
    )
    
    seal2 = inspection_seal_service.generate_sha256_seal(
        booking_id=booking_id,
        type_remise="retrait",
        photos=photos,
        video_url="https://lokiini.ma/video.mp4",
        lat=33.5731,
        lng=-7.5898,
        notes="Matériel propre et fonctionnel",
        timestamp=ts
    )
    
    assert seal1["sha256_seal"] == seal2["sha256_seal"]
    assert len(seal1["sha256_seal"]) == 64

def test_sha256_seal_tamper_detection():
    """Test that altering photos or notes produces a completely different hash."""
    booking_id = str(uuid.uuid4())
    ts = datetime(2026, 9, 1, 10, 30, 0)
    
    s_original = inspection_seal_service.generate_sha256_seal(
        booking_id=booking_id,
        type_remise="retrait",
        photos=["https://lokiini.ma/p1.jpg"],
        notes="Original",
        timestamp=ts
    )
    
    s_altered = inspection_seal_service.generate_sha256_seal(
        booking_id=booking_id,
        type_remise="retrait",
        photos=["https://lokiini.ma/p1.jpg"],
        notes="Altered note", # Tampered note
        timestamp=ts
    )
    
    assert s_original["sha256_seal"] != s_altered["sha256_seal"]

def test_check_in_submission_schema():
    """Test CheckInSubmissionRequest validation."""
    req = CheckInSubmissionRequest(
        booking_id=uuid.uuid4(),
        photos=["https://lokiini.ma/p1.jpg", "https://lokiini.ma/p2.jpg"],
        lat=33.5731,
        lng=-7.5898,
        montant_cash_loyer_recu=500.0,
        montant_caution_recue=2000.0,
        notes="Remis en mains propres au locataire"
    )
    assert len(req.photos) == 2
    assert req.montant_cash_loyer_recu == 500.0
    assert req.montant_caution_recue == 2000.0

def test_cash_receipt_schema():
    """Test CashReceiptResponse structure."""
    rec = CashReceiptResponse(
        receipt_id="REC-CASH-12345678",
        booking_id=uuid.uuid4(),
        montant_loyer_mad=350.0,
        montant_caution_mad=1500.0,
        date_emission=datetime.utcnow(),
        emetteur_nom="Yassine Alaoui",
        receveur_nom="Omar BTP Loueur"
    )
    assert rec.receipt_id == "REC-CASH-12345678"
    assert rec.montant_loyer_mad == 350.0
    assert rec.statut == "valide"

def test_handoff_routes_integrity():
    """Test that all Phase 5 handoff and inspection routes are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]
    
    assert "/api/v1/remises/check-in" in paths
    assert "/api/v1/remises/check-out" in paths
    assert "/api/v1/remises/reservation/{booking_id}" in paths
    assert "/api/v1/remises/confirmation-cash" in paths
    assert "/api/v1/inspections/seal" in paths
