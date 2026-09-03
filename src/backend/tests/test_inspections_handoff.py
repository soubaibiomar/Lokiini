import asyncio
import hashlib
import uuid
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from starlette.datastructures import Headers, UploadFile

from app.core.config import settings
from app.main import app
from app.routers.inspections import _assert_booking_state, upload_inspection_evidence
from app.schemas.inspection_schemas import StructuredInspectionCreateRequest


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return self

    def first(self):
        return self.value


class _UploadDatabase:
    def __init__(self, booking, equipment):
        self.results = iter((_ScalarResult(booking), _ScalarResult(equipment)))
        self.added = []

    async def execute(self, _query):
        return next(self.results)

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        return None

    async def refresh(self, _item):
        return None


def _participants_and_booking(status="prete_remise"):
    renter_id, owner_id, equipment_id, booking_id = (uuid.uuid4() for _ in range(4))
    current_user = SimpleNamespace(id=renter_id, user_role="renter")
    booking = SimpleNamespace(
        id=booking_id, article_id=equipment_id, locataire_id=renter_id,
        loueur_id=owner_id, statut=status,
    )
    equipment = SimpleNamespace(id=equipment_id, niveau_risque="faible")
    return current_user, booking, equipment


def test_original_file_is_stored_and_hashed_from_its_bytes(tmp_path, monkeypatch):
    current_user, booking, equipment = _participants_and_booking()
    database = _UploadDatabase(booking, equipment)
    monkeypatch.setattr(settings, "INSPECTION_EVIDENCE_DIR", str(tmp_path))
    original = b"\x89PNG\r\n\x1a\n" + b"real-original-pixels" * 100
    upload = UploadFile(
        filename="camera/original.png", file=BytesIO(original),
        headers=Headers({"content-type": "image/png"}),
    )

    response = asyncio.run(upload_inspection_evidence(
        booking_id=booking.id, inspection_type="check_in", evidence_file=upload,
        current_user=current_user, db=database,
    ))

    assert response.sha256_hash == hashlib.sha256(original).hexdigest()
    assert response.reservation_id == booking.id
    assert response.equipment_id == equipment.id
    assert response.renter_id == booking.locataire_id
    assert response.owner_id == booking.loueur_id
    assert response.uploaded_by_id == current_user.id
    assert response.inspection_type == "check_in"
    assert response.stored_at is not None
    stored = database.added[0]
    assert (tmp_path / stored.storage_key).read_bytes() == original


def test_declared_image_with_invalid_bytes_is_rejected_and_not_stored(tmp_path, monkeypatch):
    current_user, booking, equipment = _participants_and_booking()
    database = _UploadDatabase(booking, equipment)
    monkeypatch.setattr(settings, "INSPECTION_EVIDENCE_DIR", str(tmp_path))
    upload = UploadFile(
        filename="not-an-image.png", file=BytesIO(b"not a png"),
        headers=Headers({"content-type": "image/png"}),
    )

    with pytest.raises(HTTPException) as failure:
        asyncio.run(upload_inspection_evidence(
            booking_id=booking.id, inspection_type="check_in", evidence_file=upload,
            current_user=current_user, db=database,
        ))

    assert failure.value.status_code == 415
    assert failure.value.detail["code"] == "INSPECTION_MEDIA_CONTENT_INVALID"
    assert database.added == []
    assert list(tmp_path.rglob("*.*")) == []


@pytest.mark.parametrize("status", ["brouillon", "en_cours", "termine"])
def test_check_in_rejects_invalid_booking_states(status):
    with pytest.raises(HTTPException) as failure:
        _assert_booking_state(SimpleNamespace(statut=status), "check_in")
    assert failure.value.status_code == 409
    assert failure.value.detail["code"] == "INSPECTION_STATE_INVALID"


@pytest.mark.parametrize("inspection_type,status", [
    ("check_in", "prete_remise"),
    ("check_out", "en_cours"),
    ("check_out", "en_attente_validation"),
])
def test_inspection_accepts_only_its_valid_lifecycle_states(inspection_type, status):
    _assert_booking_state(SimpleNamespace(statut=status), inspection_type)


def test_structured_inspection_requires_confirmation_and_a_valid_meter():
    base = {
        "booking_id": uuid.uuid4(), "inspection_type": "check_out",
        "evidence_ids": [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()],
        "condition": "good", "meter_type": "hours", "meter_reading": 120,
        "confirmed": True,
    }
    assert StructuredInspectionCreateRequest(**base).meter_reading == 120
    with pytest.raises(ValidationError):
        StructuredInspectionCreateRequest(**{**base, "confirmed": False})
    with pytest.raises(ValidationError):
        StructuredInspectionCreateRequest(**{**base, "meter_reading": None})


def test_authoritative_inspection_routes_replace_fake_seal_contract():
    paths = app.openapi()["paths"]
    assert "/api/v1/inspections/evidence" in paths
    assert "/api/v1/inspections" in paths
    assert "/api/v1/inspections/{inspection_id}/confirm" in paths
    assert "/api/v1/inspections/bookings/{booking_id}" in paths
    assert "/api/v1/inspections/seal" not in paths
    assert "/api/v1/remises/check-in" not in paths


def test_live_inspection_code_makes_no_false_timestamp_or_signature_claims():
    backend_dir = Path(__file__).resolve().parents[1]
    repo_dir = (
        backend_dir.parent.parent
        if (backend_dir.parent.parent / "src" / "frontend").exists()
        else None
    )
    router = (backend_dir / "app/routers/inspections.py").read_text(encoding="utf-8")
    schemas = (backend_dir / "app/schemas/inspection_schemas.py").read_text(encoding="utf-8")
    assert "inspection_seal_service" not in router
    assert "rfc3161" not in router.lower()
    assert "rfc3161" not in schemas.lower()
    assert not (backend_dir / "app/services/inspection_seal_service.py").exists()
    if repo_dir:
        modal = (repo_dir / "src/frontend/web/src/components/InspectionModal.jsx").read_text(encoding="utf-8")
        assert "REC LIVE" not in modal
        assert "Hachage SHA-256 continu" not in modal
