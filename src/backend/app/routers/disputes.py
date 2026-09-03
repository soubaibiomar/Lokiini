import hashlib
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.authorization import is_admin, require_resource_access
from app.core.config import settings
from app.core.database import get_db
from app.models.models import (
    Conversation, DepositRecord, DisputeEvidence, InspectionEvidence, Litige,
    Message, Remise, Reservation, User,
)
from app.routers.auth import get_current_user
from app.schemas.dispute_schemas import (
    DisputeContextResponse, DisputeCreateRequest, DisputeDecisionRequest,
    DisputeEvidenceResponse, DisputeInspectionContext,
    DisputeInspectionEvidenceContext, DisputeMessageContext, DisputeResponse,
    LegacyDisputeCreateRequest,
)
from app.services.booking_state_machine import BookingAction, BookingActor, booking_state_machine
from app.services.dispute_lifecycle import (
    DisputeAction, DisputeActor, DisputeDecision, DisputeStatus,
    DisputeTransitionError, transition,
)
from app.services.payment_lifecycle import (
    DEPOSIT_TRANSITIONS, DepositStatus, FinancialTransitionError,
    validate_deposit_capture, validate_transition,
)
from app.services.notification_service import NotificationEvent, notify


router = APIRouter(prefix="/disputes", tags=["Disputes"])
compatibility_router = APIRouter(tags=["Disputes"])

REASON_LABELS = {
    "equipment_condition": "État du matériel",
    "missing_accessory": "Accessoire ou élément manquant",
    "late_return": "Délai de retour",
    "handover_problem": "Remise ou retour du matériel",
    "payment_issue": "Paiement ou dépôt",
    "cancellation": "Annulation",
    "other": "Autre situation",
}
MEDIA_TYPES = {
    "image/jpeg": ("photo", ".jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/png": ("photo", ".png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": ("photo", ".webp", lambda data: len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"),
    "video/mp4": ("video", ".mp4", lambda data: len(data) >= 12 and data[4:8] == b"ftyp"),
    "video/quicktime": ("video", ".mov", lambda data: len(data) >= 12 and data[4:8] == b"ftyp"),
    "video/webm": ("video", ".webm", lambda data: data.startswith(b"\x1aE\xdf\xa3")),
    "application/pdf": ("document", ".pdf", lambda data: data.startswith(b"%PDF-")),
}


def _error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _actor(current_user: User) -> DisputeActor:
    return DisputeActor.ADMIN if is_admin(current_user) else DisputeActor.PARTICIPANT


def _transition(dispute: Litige, action: DisputeAction, actor: DisputeActor) -> None:
    try:
        dispute.statut = transition(dispute.statut, action, actor).value
    except DisputeTransitionError as exc:
        raise _error(409, "DISPUTE_TRANSITION_INVALID", str(exc)) from exc
    dispute.modifie_le = datetime.now(timezone.utc)


async def _booking(
    booking_id: uuid.UUID, current_user: User, db: AsyncSession, *, for_update: bool = False,
) -> Reservation:
    query = select(Reservation).where(Reservation.id == booking_id)
    if for_update:
        query = query.with_for_update()
    result = await db.execute(query)
    booking = result.scalars().first()
    if not booking:
        raise _error(404, "BOOKING_NOT_FOUND", "Réservation introuvable.")
    require_resource_access(current_user, booking.locataire_id, booking.loueur_id)
    return booking


async def _dispute(
    dispute_id: uuid.UUID, current_user: User, db: AsyncSession, *, for_update: bool = False,
) -> Litige:
    query = select(Litige).where(Litige.id == dispute_id)
    if for_update:
        query = query.with_for_update()
    result = await db.execute(query)
    dispute = result.scalars().first()
    if not dispute:
        raise _error(404, "DISPUTE_NOT_FOUND", "Dossier introuvable.")
    require_resource_access(current_user, dispute.renter_id, dispute.owner_id)
    return dispute


def _evidence_response(item: DisputeEvidence) -> DisputeEvidenceResponse:
    return DisputeEvidenceResponse(
        id=item.id, dispute_id=item.dispute_id, reservation_id=item.reservation_id,
        equipment_id=item.equipment_id, renter_id=item.renter_id, owner_id=item.owner_id,
        uploaded_by_id=item.uploaded_by_id, media_kind=item.media_kind,
        original_filename=item.original_filename, content_type=item.content_type,
        size_bytes=item.size_bytes, sha256_hash=item.sha256_hash, stored_at=item.stored_at,
        file_url=f"{settings.API_V1_STR}/disputes/evidence/{item.id}/file",
    )


async def _response(dispute: Litige, db: AsyncSession) -> DisputeResponse:
    result = await db.execute(
        select(DisputeEvidence).where(DisputeEvidence.dispute_id == dispute.id)
        .order_by(DisputeEvidence.stored_at.asc())
    )
    return DisputeResponse(
        id=dispute.id, booking_id=dispute.reservation_id,
        equipment_id=dispute.equipment_id, renter_id=dispute.renter_id,
        owner_id=dispute.owner_id, submitted_by_id=dispute.soumis_par,
        reason_code=dispute.reason_code, description=dispute.description,
        status=dispute.statut, decision_code=dispute.decision_code,
        deposit_capture_amount_mad=(
            float(dispute.deposit_capture_amount_mad)
            if dispute.deposit_capture_amount_mad is not None else None
        ),
        deposit_action_status=dispute.deposit_action_status,
        decision_summary=dispute.notes_resolution,
        evidence_submitted_by_renter=bool(dispute.evidence_submitted_by_renter),
        evidence_submitted_by_owner=bool(dispute.evidence_submitted_by_owner),
        renter_submitted_at=dispute.renter_submitted_at,
        owner_submitted_at=dispute.owner_submitted_at,
        created_at=dispute.cree_le, updated_at=dispute.modifie_le,
        decided_at=dispute.decided_at, resolved_at=dispute.resolu_le,
        evidence=[_evidence_response(item) for item in result.scalars().all()],
    )


def _notify(db: AsyncSession, user_ids: set[uuid.UUID], title: str, body: str, dispute_id: uuid.UUID) -> None:
    for user_id in user_ids:
        notify(
            db,
            recipient_id=user_id,
            event_type=NotificationEvent.DISPUTE_UPDATED,
            title=title,
            body=body,
            dispute_id=dispute_id,
        )


@router.post("", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def create_dispute(
    payload: DisputeCreateRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=16, max_length=128),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    booking = await _booking(payload.booking_id, current_user, db, for_update=True)
    existing_result = await db.execute(select(Litige).where(
        Litige.reservation_id == booking.id, Litige.statut != DisputeStatus.RESOLVED.value,
    ))
    existing = existing_result.scalars().first()
    if existing:
        if existing.idempotency_key == idempotency_key:
            return await _response(existing, db)
        raise _error(409, "DISPUTE_ALREADY_OPEN", "Un dossier est déjà actif pour cette réservation.")

    actor = booking_state_machine.actor_for_user(current_user, booking)
    booking_state_machine.transition(booking, BookingAction.OPEN_DISPUTE, actor)
    now = datetime.now(timezone.utc)
    dispute = Litige(
        reservation_id=booking.id, equipment_id=booking.article_id,
        renter_id=booking.locataire_id, owner_id=booking.loueur_id,
        soumis_par=current_user.id, reason_code=payload.reason_code,
        motif=REASON_LABELS[payload.reason_code], description=payload.description.strip(),
        idempotency_key=idempotency_key, photos=[], statut=DisputeStatus.OPEN.value,
        evidence_submitted_by_renter=False, evidence_submitted_by_owner=False,
        cree_le=now, modifie_le=now,
    )
    db.add(dispute)
    await db.flush()
    _notify(
        db, {booking.locataire_id, booking.loueur_id} - {current_user.id},
        "Nouveau dossier à consulter",
        "Un dossier a été ouvert pour une réservation à laquelle vous participez.",
        dispute.id,
    )
    await db.commit()
    await db.refresh(dispute)
    return await _response(dispute, db)


@router.get("", response_model=list[DisputeResponse])
async def list_disputes(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    query = select(Litige).order_by(Litige.cree_le.desc())
    if not is_admin(current_user):
        query = query.where(or_(Litige.renter_id == current_user.id, Litige.owner_id == current_user.id))
    result = await db.execute(query)
    return [await _response(item, db) for item in result.scalars().all()]


@router.get("/{dispute_id}", response_model=DisputeResponse)
async def get_dispute(
    dispute_id: uuid.UUID, current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _response(await _dispute(dispute_id, current_user, db), db)


@router.post("/{dispute_id}/evidence", response_model=DisputeEvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_dispute_evidence(
    dispute_id: uuid.UUID, evidence_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    dispute = await _dispute(dispute_id, current_user, db, for_update=True)
    if dispute.statut not in {DisputeStatus.OPEN.value, DisputeStatus.EVIDENCE_COLLECTION.value}:
        raise _error(409, "DISPUTE_EVIDENCE_CLOSED", "La collecte de pièces est terminée pour ce dossier.")
    if not is_admin(current_user):
        already_submitted = (
            current_user.id == dispute.renter_id and dispute.evidence_submitted_by_renter
        ) or (
            current_user.id == dispute.owner_id and dispute.evidence_submitted_by_owner
        )
        if already_submitted:
            raise _error(409, "DISPUTE_CONTRIBUTION_SUBMITTED", "Votre contribution a déjà été transmise.")
    media = MEDIA_TYPES.get((evidence_file.content_type or "").lower())
    if not media:
        raise _error(415, "DISPUTE_EVIDENCE_TYPE_UNSUPPORTED", "Formats acceptés : JPEG, PNG, WebP, MP4, MOV, WebM ou PDF.")
    media_kind, extension, signature_matches = media
    evidence_id = uuid.uuid4()
    storage_root = Path(settings.DISPUTE_EVIDENCE_DIR).resolve()
    relative = Path(str(dispute.id)) / f"{evidence_id.hex}{extension}"
    target = (storage_root / relative).resolve()
    if storage_root not in target.parents:
        raise _error(400, "DISPUTE_STORAGE_PATH_INVALID", "Chemin de stockage invalide.")
    target.parent.mkdir(parents=True, exist_ok=True)
    digest, total_bytes, first_bytes = hashlib.sha256(), 0, b""
    try:
        with target.open("wb") as destination:
            while chunk := await evidence_file.read(1024 * 1024):
                if not first_bytes:
                    first_bytes = chunk[:32]
                total_bytes += len(chunk)
                if total_bytes > settings.DISPUTE_EVIDENCE_MAX_BYTES:
                    raise _error(413, "DISPUTE_EVIDENCE_TOO_LARGE", "Le fichier dépasse la taille maximale autorisée.")
                digest.update(chunk)
                destination.write(chunk)
        if not first_bytes or not signature_matches(first_bytes):
            raise _error(415, "DISPUTE_EVIDENCE_CONTENT_INVALID", "Le contenu ne correspond pas au format déclaré.")
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        await evidence_file.close()

    filename = Path((evidence_file.filename or f"evidence{extension}").replace("\\", "/")).name[:255]
    record = DisputeEvidence(
        id=evidence_id, dispute_id=dispute.id, reservation_id=dispute.reservation_id,
        equipment_id=dispute.equipment_id, renter_id=dispute.renter_id,
        owner_id=dispute.owner_id, uploaded_by_id=current_user.id,
        media_kind=media_kind, original_filename=filename or f"evidence{extension}",
        storage_key=relative.as_posix(), content_type=evidence_file.content_type,
        size_bytes=total_bytes, sha256_hash=digest.hexdigest(), stored_at=datetime.now(timezone.utc),
    )
    db.add(record)
    if dispute.statut == DisputeStatus.OPEN.value:
        _transition(dispute, DisputeAction.ADD_EVIDENCE, _actor(current_user))
    try:
        await db.commit()
        await db.refresh(record)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return _evidence_response(record)


@router.get("/evidence/{evidence_id}/file", include_in_schema=False)
async def get_dispute_evidence_file(
    evidence_id: uuid.UUID, current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(DisputeEvidence).where(DisputeEvidence.id == evidence_id))
    evidence = result.scalars().first()
    if not evidence:
        raise _error(404, "DISPUTE_EVIDENCE_NOT_FOUND", "Pièce introuvable.")
    require_resource_access(current_user, evidence.renter_id, evidence.owner_id)
    storage_root = Path(settings.DISPUTE_EVIDENCE_DIR).resolve()
    target = (storage_root / evidence.storage_key).resolve()
    if storage_root not in target.parents or not target.is_file():
        raise _error(404, "DISPUTE_EVIDENCE_FILE_MISSING", "Fichier original introuvable.")
    return FileResponse(
        target, media_type=evidence.content_type, filename=evidence.original_filename,
        content_disposition_type="inline", headers={"Cache-Control": "private, no-store"},
    )


@router.delete("/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dispute_evidence(
    evidence_id: uuid.UUID, current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(DisputeEvidence).where(DisputeEvidence.id == evidence_id).with_for_update())
    evidence = result.scalars().first()
    if not evidence:
        return None
    dispute = await _dispute(evidence.dispute_id, current_user, db, for_update=True)
    if evidence.uploaded_by_id != current_user.id and not is_admin(current_user):
        raise _error(403, "DISPUTE_EVIDENCE_DELETE_FORBIDDEN", "Vous ne pouvez pas supprimer cette pièce.")
    if dispute.statut not in {DisputeStatus.OPEN.value, DisputeStatus.EVIDENCE_COLLECTION.value}:
        raise _error(409, "DISPUTE_EVIDENCE_IMMUTABLE", "Les pièces soumises à l'examen ne peuvent plus être supprimées.")
    if not is_admin(current_user):
        submitted = (
            current_user.id == dispute.renter_id and dispute.evidence_submitted_by_renter
        ) or (
            current_user.id == dispute.owner_id and dispute.evidence_submitted_by_owner
        )
        if submitted:
            raise _error(409, "DISPUTE_EVIDENCE_IMMUTABLE", "Votre contribution transmise ne peut plus être modifiée.")
    storage_root = Path(settings.DISPUTE_EVIDENCE_DIR).resolve()
    target = (storage_root / evidence.storage_key).resolve()
    await db.delete(evidence)
    await db.commit()
    if storage_root in target.parents:
        target.unlink(missing_ok=True)
    return None


@router.post("/{dispute_id}/submit", response_model=DisputeResponse)
async def submit_dispute_for_review(
    dispute_id: uuid.UUID, current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dispute = await _dispute(dispute_id, current_user, db, for_update=True)
    actor = _actor(current_user)
    if dispute.statut == DisputeStatus.OPEN.value:
        _transition(dispute, DisputeAction.ADD_EVIDENCE, actor)
    now = datetime.now(timezone.utc)
    if is_admin(current_user):
        _transition(dispute, DisputeAction.SUBMIT_FOR_REVIEW, DisputeActor.ADMIN)
    elif current_user.id == dispute.renter_id:
        if dispute.evidence_submitted_by_renter:
            raise _error(409, "DISPUTE_CONTRIBUTION_SUBMITTED", "Votre contribution a déjà été transmise.")
        dispute.evidence_submitted_by_renter = True
        dispute.renter_submitted_at = now
    elif current_user.id == dispute.owner_id:
        if dispute.evidence_submitted_by_owner:
            raise _error(409, "DISPUTE_CONTRIBUTION_SUBMITTED", "Votre contribution a déjà été transmise.")
        dispute.evidence_submitted_by_owner = True
        dispute.owner_submitted_at = now
    if dispute.evidence_submitted_by_renter and dispute.evidence_submitted_by_owner:
        _transition(dispute, DisputeAction.SUBMIT_FOR_REVIEW, DisputeActor.PARTICIPANT)
        title = "Dossier transmis pour examen"
        body = "Les contributions des deux parties sont maintenant en cours d'examen."
    else:
        dispute.modifie_le = now
        title = "Contribution ajoutée au dossier"
        body = "Une partie a terminé sa contribution. La collecte reste ouverte pour l'autre partie."
    _notify(db, {dispute.renter_id, dispute.owner_id}, title, body, dispute.id)
    await db.commit()
    await db.refresh(dispute)
    return await _response(dispute, db)


@router.post("/{dispute_id}/decision", response_model=DisputeResponse)
async def record_dispute_decision(
    dispute_id: uuid.UUID, payload: DisputeDecisionRequest,
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    if not is_admin(current_user):
        raise _error(403, "DISPUTE_DECISION_FORBIDDEN", "La décision est réservée à l'équipe habilitée.")
    dispute = await _dispute(dispute_id, current_user, db, for_update=True)
    booking = await _booking(dispute.reservation_id, current_user, db, for_update=True)
    _transition(dispute, DisputeAction.RECORD_DECISION, DisputeActor.ADMIN)
    decision = DisputeDecision(payload.decision_code)
    now = datetime.now(timezone.utc)
    dispute.decision_code = decision.value
    dispute.notes_resolution = payload.decision_summary.strip()
    dispute.decided_by_id = current_user.id
    dispute.decided_at = now

    if decision == DisputeDecision.NO_FINANCIAL_ADJUSTMENT:
        dispute.deposit_capture_amount_mad = None
        dispute.deposit_action_status = "not_applicable"
        _transition(dispute, DisputeAction.CONFIRM_RESOLUTION, DisputeActor.ADMIN)
        dispute.resolu_le = now
        booking_state_machine.transition(booking, BookingAction.RESOLVE_DISPUTE, BookingActor.ADMIN)
    else:
        deposit_result = await db.execute(select(DepositRecord).where(
            DepositRecord.booking_id == booking.id,
        ).order_by(DepositRecord.created_at.desc()).limit(1).with_for_update())
        deposit = deposit_result.scalars().first()
        if not deposit or deposit.status != DepositStatus.AUTHORIZED.value or not deposit.provider_transaction_id:
            raise _error(409, "DEPOSIT_NOT_AUTHORIZED", "Aucun dépôt autorisé ne peut être traité pour cette réservation.")
        try:
            if decision == DisputeDecision.RELEASE_DEPOSIT:
                validate_transition(DepositStatus(deposit.status), DepositStatus.RELEASED, DEPOSIT_TRANSITIONS, "deposit")
                dispute.deposit_capture_amount_mad = None
            elif decision == DisputeDecision.PARTIAL_DEPOSIT_CAPTURE:
                amount = Decimal(str(payload.deposit_capture_amount_mad))
                validate_transition(DepositStatus(deposit.status), DepositStatus.PARTIALLY_CAPTURED, DEPOSIT_TRANSITIONS, "deposit")
                validate_deposit_capture(deposit.authorized_amount_mad, amount, DepositStatus.PARTIALLY_CAPTURED)
                dispute.deposit_capture_amount_mad = amount
            else:
                validate_transition(DepositStatus(deposit.status), DepositStatus.CAPTURED, DEPOSIT_TRANSITIONS, "deposit")
                validate_deposit_capture(deposit.authorized_amount_mad, deposit.authorized_amount_mad, DepositStatus.CAPTURED)
                dispute.deposit_capture_amount_mad = deposit.authorized_amount_mad
        except (ValueError, FinancialTransitionError) as exc:
            raise _error(409, "DISPUTE_DEPOSIT_DECISION_INVALID", str(exc)) from exc
        dispute.deposit_action_status = "pending_provider"

    _notify(
        db, {dispute.renter_id, dispute.owner_id}, "Décision du dossier enregistrée",
        "Une décision motivée est disponible. Le statut financier reste distinct et dépend de sa confirmation.",
        dispute.id,
    )
    await db.commit()
    await db.refresh(dispute)
    return await _response(dispute, db)


@router.get("/{dispute_id}/context", response_model=DisputeContextResponse)
async def get_dispute_context(
    dispute_id: uuid.UUID, current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dispute = await _dispute(dispute_id, current_user, db)
    inspection_result = await db.execute(
        select(Remise).where(Remise.reservation_id == dispute.reservation_id).order_by(Remise.cree_le.asc())
    )
    inspections = []
    for inspection in inspection_result.scalars().all():
        evidence_result = await db.execute(select(InspectionEvidence).where(
            InspectionEvidence.inspection_id == inspection.id,
        ).order_by(InspectionEvidence.stored_at.asc()))
        inspections.append(DisputeInspectionContext(
            id=inspection.id, inspection_type=inspection.type,
            condition=inspection.condition, existing_damage=inspection.existing_damage,
            accessories=inspection.accessories or [], serial_number=inspection.serial_number,
            meter_type=inspection.meter_type,
            meter_reading=float(inspection.meter_reading) if inspection.meter_reading is not None else None,
            notes=inspection.notes, status=inspection.statut,
            recorded_at=inspection.horodatage or inspection.cree_le,
            evidence=[DisputeInspectionEvidenceContext(
                id=item.id, media_kind=item.media_kind,
                original_filename=item.original_filename, sha256_hash=item.sha256_hash,
                stored_at=item.stored_at,
                file_url=f"{settings.API_V1_STR}/inspections/evidence/{item.id}/file",
            ) for item in evidence_result.scalars().all()],
        ))
    conversation_result = await db.execute(select(Conversation).where(
        Conversation.reservation_id == dispute.reservation_id,
    ))
    conversations = conversation_result.scalars().all()
    conversation_ids = [item.id for item in conversations]
    messages = []
    if conversation_ids:
        message_result = await db.execute(select(Message).where(
            Message.conversation_id.in_(conversation_ids),
        ).order_by(Message.cree_le.asc()))
        messages = [DisputeMessageContext(
            id=item.id, conversation_id=item.conversation_id,
            sender_id=item.expediteur_id, content=item.contenu, created_at=item.cree_le,
        ) for item in message_result.scalars().all()]
    return DisputeContextResponse(inspections=inspections, messages=messages)


@compatibility_router.post("/reservations/{reservation_id}/remise/litige", include_in_schema=False)
async def disabled_legacy_dispute(
    reservation_id: uuid.UUID, payload: LegacyDisputeCreateRequest,
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await _booking(reservation_id, current_user, db)
    raise _error(410, "DISPUTE_FLOW_REPLACED", "Utilisez le nouveau parcours de dossier avec pièces originales.")
