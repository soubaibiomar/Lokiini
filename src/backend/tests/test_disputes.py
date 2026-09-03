import asyncio
import hashlib
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from starlette.datastructures import Headers, UploadFile

from app.core.config import settings
from app.main import app
from app.routers.disputes import get_dispute, submit_dispute_for_review, upload_dispute_evidence
from app.routers.webhooks import _reconcile_related_records
from app.schemas.dispute_schemas import DisputeDecisionRequest
from app.schemas.payment_schemas import PaymentWebhookPayload
from app.services.dispute_lifecycle import (
    DisputeAction, DisputeActor, DisputeStatus, DisputeTransitionError, transition,
)


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return self

    def first(self):
        return self.value

    def all(self):
        return self.value if isinstance(self.value, list) else [self.value]


class _SequenceDatabase:
    def __init__(self, *values):
        self.results = iter(_ScalarResult(value) for value in values)
        self.added = []

    async def execute(self, _query):
        return next(self.results)

    def add(self, item):
        self.added.append(item)

    async def commit(self):
        return None

    async def refresh(self, _item):
        return None


def test_dispute_state_machine_accepts_only_explicit_sequence():
    assert transition("open", DisputeAction.ADD_EVIDENCE, DisputeActor.PARTICIPANT) == DisputeStatus.EVIDENCE_COLLECTION
    assert transition("evidence_collection", DisputeAction.SUBMIT_FOR_REVIEW, DisputeActor.PARTICIPANT) == DisputeStatus.UNDER_REVIEW
    assert transition("under_review", DisputeAction.RECORD_DECISION, DisputeActor.ADMIN) == DisputeStatus.DECISION
    assert transition("decision", DisputeAction.CONFIRM_RESOLUTION, DisputeActor.SYSTEM) == DisputeStatus.RESOLVED
    with pytest.raises(DisputeTransitionError):
        transition("open", DisputeAction.RECORD_DECISION, DisputeActor.ADMIN)
    with pytest.raises(DisputeTransitionError):
        transition("under_review", DisputeAction.RECORD_DECISION, DisputeActor.PARTICIPANT)
    with pytest.raises(DisputeTransitionError):
        transition("resolved", DisputeAction.ADD_EVIDENCE, DisputeActor.PARTICIPANT)


def test_outsider_cannot_read_a_dispute():
    dispute = SimpleNamespace(
        id=uuid.uuid4(), renter_id=uuid.uuid4(), owner_id=uuid.uuid4(),
    )
    outsider = SimpleNamespace(id=uuid.uuid4(), user_role="renter")
    with pytest.raises(HTTPException) as failure:
        asyncio.run(get_dispute(dispute.id, current_user=outsider, db=_SequenceDatabase(dispute)))
    assert failure.value.status_code == 403


def test_only_partial_capture_accepts_a_decided_amount():
    partial = DisputeDecisionRequest(
        decision_code="partial_deposit_capture",
        decision_summary="Une retenue partielle est décidée sur les éléments examinés.",
        deposit_capture_amount_mad=500,
    )
    assert partial.deposit_capture_amount_mad == 500
    with pytest.raises(ValidationError):
        DisputeDecisionRequest(
            decision_code="partial_deposit_capture",
            decision_summary="Une retenue partielle est décidée sur les éléments examinés.",
        )
    with pytest.raises(ValidationError):
        DisputeDecisionRequest(
            decision_code="release_deposit",
            decision_summary="La libération du dépôt est décidée sur les éléments examinés.",
            deposit_capture_amount_mad=500,
        )


def test_dispute_original_evidence_is_privately_stored_and_hashed(tmp_path, monkeypatch):
    renter_id, owner_id = uuid.uuid4(), uuid.uuid4()
    dispute = SimpleNamespace(
        id=uuid.uuid4(), reservation_id=uuid.uuid4(), equipment_id=uuid.uuid4(),
        renter_id=renter_id, owner_id=owner_id, statut="open", modifie_le=None,
        evidence_submitted_by_renter=False, evidence_submitted_by_owner=False,
    )
    user = SimpleNamespace(id=renter_id, user_role="renter")
    database = _SequenceDatabase(dispute)
    monkeypatch.setattr(settings, "DISPUTE_EVIDENCE_DIR", str(tmp_path))
    original = b"%PDF-1.7\n" + b"original-dispute-evidence" * 50
    upload = UploadFile(
        filename="documents/constat.pdf", file=BytesIO(original),
        headers=Headers({"content-type": "application/pdf"}),
    )

    response = asyncio.run(upload_dispute_evidence(
        dispute_id=dispute.id, evidence_file=upload, current_user=user, db=database,
    ))

    assert response.sha256_hash == hashlib.sha256(original).hexdigest()
    assert response.dispute_id == dispute.id
    assert response.reservation_id == dispute.reservation_id
    assert response.renter_id == renter_id
    assert response.owner_id == owner_id
    assert response.uploaded_by_id == renter_id
    assert dispute.statut == "evidence_collection"
    stored = database.added[0]
    assert (tmp_path / stored.storage_key).read_bytes() == original


def test_both_participants_finish_before_the_case_enters_review():
    renter_id, owner_id = uuid.uuid4(), uuid.uuid4()
    now = datetime.now(timezone.utc)
    dispute = SimpleNamespace(
        id=uuid.uuid4(), reservation_id=uuid.uuid4(), equipment_id=uuid.uuid4(),
        renter_id=renter_id, owner_id=owner_id, soumis_par=renter_id,
        reason_code="equipment_condition", description="Description factuelle suffisamment détaillée.",
        statut="open", decision_code=None, deposit_capture_amount_mad=None,
        deposit_action_status=None, notes_resolution=None,
        evidence_submitted_by_renter=False, evidence_submitted_by_owner=False,
        renter_submitted_at=None, owner_submitted_at=None,
        cree_le=now, modifie_le=now, decided_at=None, resolu_le=None,
    )
    renter = SimpleNamespace(id=renter_id, user_role="renter")
    owner = SimpleNamespace(id=owner_id, user_role="owner")

    asyncio.run(submit_dispute_for_review(
        dispute.id, current_user=renter, db=_SequenceDatabase(dispute, []),
    ))
    assert dispute.statut == "evidence_collection"
    assert dispute.evidence_submitted_by_renter is True
    assert dispute.evidence_submitted_by_owner is False

    asyncio.run(submit_dispute_for_review(
        dispute.id, current_user=owner, db=_SequenceDatabase(dispute, []),
    ))
    assert dispute.statut == "under_review"
    assert dispute.evidence_submitted_by_owner is True


def test_matching_provider_deposit_result_resolves_dispute_and_booking():
    booking_id = uuid.uuid4()
    dispute = SimpleNamespace(
        id=uuid.uuid4(), renter_id=uuid.uuid4(), owner_id=uuid.uuid4(),
        decision_code="partial_deposit_capture", deposit_capture_amount_mad=500,
        statut="decision", deposit_action_status="pending_provider",
        resolu_le=None, modifie_le=None,
    )
    booking = SimpleNamespace(statut="en_litige", modifie_le=None)
    deposit = SimpleNamespace(
        booking_id=booking_id, status="partially_captured",
        captured_amount_mad=500, authorized_amount_mad=2000,
    )
    database = _SequenceDatabase(dispute, booking)
    payload = PaymentWebhookPayload(
        event_id="evt-dispute-1", event_type="deposit.updated",
        provider_transaction_id="deposit-1", status="partially_captured", amount_mad=500,
    )

    asyncio.run(_reconcile_related_records(database, deposit, payload))

    assert dispute.statut == "resolved"
    assert dispute.deposit_action_status == "confirmed"
    assert dispute.resolu_le is not None
    assert booking.statut == "resolu"


def test_provider_cannot_confirm_a_different_dispute_outcome():
    dispute = SimpleNamespace(
        decision_code="release_deposit", deposit_capture_amount_mad=None,
        statut="decision", deposit_action_status="pending_provider",
    )
    deposit = SimpleNamespace(
        booking_id=uuid.uuid4(), status="captured",
        captured_amount_mad=2000, authorized_amount_mad=2000,
    )
    payload = PaymentWebhookPayload(
        event_id="evt-dispute-2", event_type="deposit.updated",
        provider_transaction_id="deposit-2", status="captured", amount_mad=2000,
    )
    with pytest.raises(HTTPException) as failure:
        asyncio.run(_reconcile_related_records(_SequenceDatabase(dispute), deposit, payload))
    assert failure.value.status_code == 409
    assert failure.value.detail["code"] == "DISPUTE_DEPOSIT_OUTCOME_MISMATCH"


def test_public_dispute_contract_is_first_class_and_legacy_urls_are_hidden():
    paths = app.openapi()["paths"]
    assert "/api/v1/disputes" in paths
    assert "/api/v1/disputes/{dispute_id}/evidence" in paths
    assert "/api/v1/disputes/{dispute_id}/context" in paths
    assert "/api/v1/disputes/{dispute_id}/submit" in paths
    assert "/api/v1/disputes/{dispute_id}/decision" in paths
    assert "/api/v1/reservations/{reservation_id}/remise/litige" not in paths


def test_user_frontend_has_no_dispute_decision_or_compensation_call():
    backend_dir = Path(__file__).resolve().parents[1]
    repo_dir = (
        backend_dir.parent.parent
        if (backend_dir.parent.parent / "src" / "frontend").exists()
        else None
    )
    if repo_dir:
        api_source = (repo_dir / "src/frontend/web/src/services/api.js").read_text(encoding="utf-8")
        assert "recordDisputeDecision" not in api_source
    router_source = (backend_dir / "app/routers/disputes.py").read_text(encoding="utf-8")
    assert "if not is_admin(current_user)" in router_source
    assert "pending_provider" in router_source
    assert "deposit.status =" not in router_source
