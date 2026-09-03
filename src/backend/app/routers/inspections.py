import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.authorization import require_resource_access
from app.core.config import settings
from app.core.database import get_db
from app.models.models import Article, InspectionEvidence, Remise, Reservation, Utilisateur
from app.routers.auth import get_current_user
from app.schemas.inspection_schemas import (
    CashConfirmationRequest, CheckInSubmissionRequest, CheckOutSubmissionRequest,
    InspectionCreateRequest, InspectionDetailResponse,
    InspectionEvidenceResponse, InspectionRequirementsResponse,
    RemiseCreateRequest, StructuredInspectionCreateRequest,
)
from app.services.booking_state_machine import BookingAction, BookingActor, booking_state_machine
from app.services.notification_service import NotificationEvent, notify


router = APIRouter(tags=["Check-in & check-out inspections"])

INSPECTION_STATES = {
    "check_in": {"prete_remise"},
    "check_out": {"en_cours", "en_attente_validation"},
}
PHOTO_TYPES = {
    "image/jpeg": ("photo", ".jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/png": ("photo", ".png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": ("photo", ".webp", lambda data: len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"),
}
VIDEO_TYPES = {
    "video/mp4": ("video", ".mp4", lambda data: len(data) >= 12 and data[4:8] == b"ftyp"),
    "video/quicktime": ("video", ".mov", lambda data: len(data) >= 12 and data[4:8] == b"ftyp"),
    "video/webm": ("video", ".webm", lambda data: data.startswith(b"\x1aE\xdf\xa3")),
}
MEDIA_TYPES = {**PHOTO_TYPES, **VIDEO_TYPES}


def _api_error(code: int, error_code: str, message: str) -> HTTPException:
    return HTTPException(status_code=code, detail={"code": error_code, "message": message})


async def _booking(
    booking_id: uuid.UUID, current_user: Utilisateur, db: AsyncSession,
    *, for_update: bool = False,
) -> Reservation:
    query = select(Reservation).where(Reservation.id == booking_id)
    if for_update:
        query = query.with_for_update()
    result = await db.execute(query)
    booking = result.scalars().first()
    if not booking:
        raise _api_error(404, "BOOKING_NOT_FOUND", "Réservation introuvable.")
    require_resource_access(current_user, booking.locataire_id, booking.loueur_id)
    return booking


async def _equipment(booking: Reservation, db: AsyncSession) -> Article:
    result = await db.execute(select(Article).where(Article.id == booking.article_id))
    equipment = result.scalars().first()
    if not equipment:
        raise _api_error(409, "INSPECTION_EQUIPMENT_MISSING", "Le matériel de la réservation est introuvable.")
    return equipment


def _normalize_type(value: str) -> str:
    normalized = {"retrait": "check_in", "retour": "check_out"}.get(value, value)
    if normalized not in INSPECTION_STATES:
        raise _api_error(422, "INSPECTION_TYPE_INVALID", "Type d'inspection invalide.")
    return normalized


def _assert_booking_state(booking: Reservation, inspection_type: str) -> None:
    if booking.statut not in INSPECTION_STATES[inspection_type]:
        raise _api_error(
            409, "INSPECTION_STATE_INVALID",
            f"L'inspection {inspection_type} n'est pas disponible depuis le statut actuel.",
        )


def _evidence_response(item: InspectionEvidence) -> InspectionEvidenceResponse:
    return InspectionEvidenceResponse(
        id=item.id, reservation_id=item.reservation_id, equipment_id=item.equipment_id,
        renter_id=item.renter_id, owner_id=item.owner_id, uploaded_by_id=item.uploaded_by_id,
        inspection_type=item.inspection_type, media_kind=item.media_kind,
        original_filename=item.original_filename, content_type=item.content_type,
        size_bytes=item.size_bytes, sha256_hash=item.sha256_hash, stored_at=item.stored_at,
        file_url=f"{settings.API_V1_STR}/inspections/evidence/{item.id}/file",
    )


async def _inspection_response(item: Remise, db: AsyncSession) -> InspectionDetailResponse:
    result = await db.execute(
        select(InspectionEvidence).where(InspectionEvidence.inspection_id == item.id)
        .order_by(InspectionEvidence.stored_at.asc())
    )
    evidence = result.scalars().all()
    return InspectionDetailResponse(
        id=item.id, reservation_id=item.reservation_id, equipment_id=item.equipment_id,
        renter_id=item.renter_id, owner_id=item.owner_id, submitted_by_id=item.submitted_by_id,
        inspection_type=_normalize_type(item.type), condition=item.condition,
        existing_damage=item.existing_damage, accessories=item.accessories or [],
        serial_number=item.serial_number, meter_type=item.meter_type,
        meter_reading=float(item.meter_reading) if item.meter_reading is not None else None,
        notes=item.notes, status=item.statut,
        confirmed_by_owner=bool(item.signed_by_owner), confirmed_by_renter=bool(item.signed_by_renter),
        recorded_at=item.horodatage or item.cree_le, confirmed_at=item.confirmed_at,
        evidence=[_evidence_response(record) for record in evidence],
    )


@router.get("/inspections/bookings/{booking_id}/requirements", response_model=InspectionRequirementsResponse)
async def get_inspection_requirements(
    booking_id: uuid.UUID, inspection_type: str,
    current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    normalized_type = _normalize_type(inspection_type)
    booking = await _booking(booking_id, current_user, db)
    equipment = await _equipment(booking, db)
    return InspectionRequirementsResponse(
        booking_id=booking.id, inspection_type=normalized_type, minimum_photos=3,
        video_required=equipment.niveau_risque == "eleve",
        photo_max_bytes=settings.INSPECTION_PHOTO_MAX_BYTES,
        video_max_bytes=settings.INSPECTION_VIDEO_MAX_BYTES,
        allowed_booking_statuses=sorted(INSPECTION_STATES[normalized_type]),
    )


@router.post("/inspections/evidence", response_model=InspectionEvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_inspection_evidence(
    booking_id: uuid.UUID = Form(...), inspection_type: str = Form(...),
    evidence_file: UploadFile = File(...),
    current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    normalized_type = _normalize_type(inspection_type)
    booking = await _booking(booking_id, current_user, db)
    _assert_booking_state(booking, normalized_type)
    await _equipment(booking, db)

    media = MEDIA_TYPES.get((evidence_file.content_type or "").lower())
    if not media:
        raise _api_error(415, "INSPECTION_MEDIA_TYPE_UNSUPPORTED", "Formats acceptés : JPEG, PNG, WebP, MP4, MOV ou WebM.")
    media_kind, extension, signature_matches = media
    max_bytes = settings.INSPECTION_PHOTO_MAX_BYTES if media_kind == "photo" else settings.INSPECTION_VIDEO_MAX_BYTES
    evidence_id = uuid.uuid4()
    storage_root = Path(settings.INSPECTION_EVIDENCE_DIR).resolve()
    relative = Path(str(booking.id)) / normalized_type / f"{evidence_id.hex}{extension}"
    target = (storage_root / relative).resolve()
    if storage_root not in target.parents:
        raise _api_error(400, "INSPECTION_STORAGE_PATH_INVALID", "Chemin de stockage invalide.")
    target.parent.mkdir(parents=True, exist_ok=True)

    digest = hashlib.sha256()
    total_bytes = 0
    first_bytes = b""
    try:
        with target.open("wb") as destination:
            while chunk := await evidence_file.read(1024 * 1024):
                if not first_bytes:
                    first_bytes = chunk[:32]
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise _api_error(413, "INSPECTION_MEDIA_TOO_LARGE", "Le fichier dépasse la taille maximale autorisée.")
                digest.update(chunk)
                destination.write(chunk)
        if not first_bytes or not signature_matches(first_bytes):
            raise _api_error(415, "INSPECTION_MEDIA_CONTENT_INVALID", "Le contenu ne correspond pas au format déclaré.")
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        await evidence_file.close()

    safe_filename = Path((evidence_file.filename or f"evidence{extension}").replace("\\", "/")).name[:255]
    record = InspectionEvidence(
        id=evidence_id, reservation_id=booking.id, equipment_id=booking.article_id,
        renter_id=booking.locataire_id, owner_id=booking.loueur_id, uploaded_by_id=current_user.id,
        inspection_type=normalized_type, media_kind=media_kind,
        original_filename=safe_filename or f"evidence{extension}",
        storage_key=relative.as_posix(), content_type=evidence_file.content_type,
        size_bytes=total_bytes, sha256_hash=digest.hexdigest(),
        stored_at=datetime.now(timezone.utc),
    )
    db.add(record)
    try:
        await db.commit()
        await db.refresh(record)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return _evidence_response(record)


@router.get("/inspections/evidence/{evidence_id}/file", include_in_schema=False)
async def get_inspection_evidence_file(
    evidence_id: uuid.UUID, current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(InspectionEvidence).where(InspectionEvidence.id == evidence_id))
    evidence = result.scalars().first()
    if not evidence:
        raise _api_error(404, "INSPECTION_EVIDENCE_NOT_FOUND", "Preuve introuvable.")
    require_resource_access(current_user, evidence.renter_id, evidence.owner_id)
    storage_root = Path(settings.INSPECTION_EVIDENCE_DIR).resolve()
    target = (storage_root / evidence.storage_key).resolve()
    if storage_root not in target.parents or not target.is_file():
        raise _api_error(404, "INSPECTION_EVIDENCE_FILE_MISSING", "Fichier original introuvable.")
    return FileResponse(
        target, media_type=evidence.content_type, filename=evidence.original_filename,
        content_disposition_type="inline",
        headers={"Cache-Control": "private, no-store"},
    )


@router.delete("/inspections/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staged_inspection_evidence(
    evidence_id: uuid.UUID, current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(InspectionEvidence).where(InspectionEvidence.id == evidence_id))
    evidence = result.scalars().first()
    if not evidence:
        return None
    if evidence.uploaded_by_id != current_user.id:
        raise _api_error(403, "INSPECTION_EVIDENCE_DELETE_FORBIDDEN", "Suppression de cette preuve interdite.")
    if evidence.inspection_id:
        raise _api_error(409, "INSPECTION_EVIDENCE_IMMUTABLE", "Une preuve liée à une inspection ne peut plus être supprimée.")
    storage_root = Path(settings.INSPECTION_EVIDENCE_DIR).resolve()
    target = (storage_root / evidence.storage_key).resolve()
    if storage_root not in target.parents:
        raise _api_error(400, "INSPECTION_STORAGE_PATH_INVALID", "Chemin de stockage invalide.")
    await db.delete(evidence)
    await db.commit()
    target.unlink(missing_ok=True)
    return None


@router.post("/inspections", response_model=InspectionDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    payload: StructuredInspectionCreateRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=16, max_length=128),
    current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    booking = await _booking(payload.booking_id, current_user, db, for_update=True)
    _assert_booking_state(booking, payload.inspection_type)
    equipment = await _equipment(booking, db)
    existing_result = await db.execute(select(Remise).where(
        Remise.reservation_id == booking.id, Remise.type == payload.inspection_type,
    ))
    existing = existing_result.scalars().first()
    if existing:
        existing_key = (existing.signatures or {}).get("submission_idempotency_key")
        if existing_key == idempotency_key:
            return await _inspection_response(existing, db)
        raise _api_error(409, "INSPECTION_ALREADY_EXISTS", "Une inspection de ce type existe déjà pour cette réservation.")

    if payload.inspection_type == "check_out":
        check_in_result = await db.execute(select(Remise).where(
            Remise.reservation_id == booking.id,
            Remise.type.in_(["check_in", "retrait"]),
            Remise.statut.in_(["confirmed", "confirme"]),
        ))
        if not check_in_result.scalars().first():
            raise _api_error(409, "CHECK_IN_REQUIRED", "Le check-in confirmé est requis avant le check-out.")

    unique_evidence_ids = set(payload.evidence_ids)
    evidence_result = await db.execute(select(InspectionEvidence).where(InspectionEvidence.id.in_(unique_evidence_ids)))
    evidence = evidence_result.scalars().all()
    if len(evidence) != len(unique_evidence_ids) or any(
        item.reservation_id != booking.id
        or item.inspection_type != payload.inspection_type
        or item.uploaded_by_id != current_user.id
        or item.inspection_id
        for item in evidence
    ):
        raise _api_error(422, "INSPECTION_EVIDENCE_INVALID", "Une ou plusieurs preuves ne correspondent pas à cette inspection.")
    photo_count = sum(item.media_kind == "photo" for item in evidence)
    video_count = sum(item.media_kind == "video" for item in evidence)
    if photo_count < 3:
        raise _api_error(422, "INSPECTION_PHOTOS_REQUIRED", "Au moins trois photos sont requises.")
    if equipment.niveau_risque == "eleve" and video_count < 1:
        raise _api_error(422, "INSPECTION_VIDEO_REQUIRED", "Une vidéo est requise pour ce matériel.")

    if payload.inspection_type == "check_out" and payload.meter_type != "none":
        previous_result = await db.execute(select(Remise).where(
            Remise.reservation_id == booking.id, Remise.type.in_(["check_in", "retrait"]),
        ).order_by(Remise.cree_le.desc()).limit(1))
        previous = previous_result.scalars().first()
        if previous and previous.meter_type == payload.meter_type and previous.meter_reading is not None:
            if payload.meter_reading < float(previous.meter_reading):
                raise _api_error(422, "INSPECTION_METER_DECREASED", "Le relevé de retour ne peut pas être inférieur au relevé initial.")

    now = datetime.now(timezone.utc)
    inspection = Remise(
        reservation_id=booking.id, equipment_id=booking.article_id,
        renter_id=booking.locataire_id, owner_id=booking.loueur_id,
        submitted_by_id=current_user.id, type=payload.inspection_type,
        photos=[], videos=[], condition=payload.condition,
        existing_damage=(payload.existing_damage or "").strip() or None,
        accessories=[item.strip() for item in payload.accessories if item.strip()],
        serial_number=(payload.serial_number or "").strip() or None,
        meter_type=None if payload.meter_type == "none" else payload.meter_type,
        meter_reading=payload.meter_reading, notes=(payload.notes or "").strip() or None,
        signed_by_owner=current_user.id == booking.loueur_id,
        signed_by_renter=current_user.id == booking.locataire_id,
        statut="pending_counterparty", horodatage=now, cree_le=now,
        signatures={"submission_idempotency_key": idempotency_key},
    )
    db.add(inspection)
    await db.flush()
    for item in evidence:
        item.inspection_id = inspection.id
    inspection.photos = [f"{settings.API_V1_STR}/inspections/evidence/{item.id}/file" for item in evidence if item.media_kind == "photo"]
    inspection.videos = [f"{settings.API_V1_STR}/inspections/evidence/{item.id}/file" for item in evidence if item.media_kind == "video"]
    if payload.inspection_type == "check_out" and booking.statut == "en_cours":
        booking_state_machine.transition(booking, BookingAction.REQUEST_RETURN, BookingActor.SYSTEM)
    counterparty_id = booking.loueur_id if current_user.id == booking.locataire_id else booking.locataire_id
    inspection_label = "remise" if payload.inspection_type == "check_in" else "retour"
    notify(
        db,
        recipient_id=counterparty_id,
        event_type=NotificationEvent.INSPECTION_REQUIRED,
        title=f"Inspection de {inspection_label} à confirmer",
        body="L’autre partie a transmis son inspection. Consultez les éléments avant de confirmer.",
        booking_id=booking.id,
    )
    await db.commit()
    await db.refresh(inspection)
    return await _inspection_response(inspection, db)


@router.get("/inspections/bookings/{booking_id}", response_model=list[InspectionDetailResponse])
@router.get("/inspections/booking/{booking_id}", response_model=list[InspectionDetailResponse], include_in_schema=False)
async def list_inspections_for_booking(
    booking_id: uuid.UUID, current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _booking(booking_id, current_user, db)
    result = await db.execute(select(Remise).where(Remise.reservation_id == booking_id).order_by(Remise.cree_le.asc()))
    return [await _inspection_response(item, db) for item in result.scalars().all()]


@router.post("/inspections/{inspection_id}/confirm", response_model=InspectionDetailResponse)
async def confirm_inspection(
    inspection_id: uuid.UUID, current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Remise).where(Remise.id == inspection_id).with_for_update())
    inspection = result.scalars().first()
    if not inspection:
        raise _api_error(404, "INSPECTION_NOT_FOUND", "Inspection introuvable.")
    booking = await _booking(inspection.reservation_id, current_user, db)
    if current_user.id == booking.loueur_id:
        if inspection.signed_by_owner:
            raise _api_error(409, "INSPECTION_ALREADY_CONFIRMED", "Vous avez déjà confirmé cette inspection.")
        inspection.signed_by_owner = True
    elif current_user.id == booking.locataire_id:
        if inspection.signed_by_renter:
            raise _api_error(409, "INSPECTION_ALREADY_CONFIRMED", "Vous avez déjà confirmé cette inspection.")
        inspection.signed_by_renter = True
    else:
        raise _api_error(403, "INSPECTION_CONFIRM_FORBIDDEN", "Seules les deux parties peuvent confirmer l'inspection.")

    if inspection.signed_by_owner and inspection.signed_by_renter:
        inspection.statut = "confirmed"
        inspection.confirmed_at = datetime.now(timezone.utc)
        action = BookingAction.COMPLETE_HANDOVER if _normalize_type(inspection.type) == "check_in" else BookingAction.COMPLETE_RETURN
        booking_state_machine.transition(booking, action, BookingActor.SYSTEM)
    await db.commit()
    await db.refresh(inspection)
    return await _inspection_response(inspection, db)


async def _disabled_legacy_inspection(booking_id: uuid.UUID, current_user: Utilisateur, db: AsyncSession):
    await _booking(booking_id, current_user, db)
    raise _api_error(410, "INSPECTION_FLOW_REPLACED", "Utilisez le nouveau parcours d'inspection avec preuves importées.")


@router.post("/reservations/{reservation_id}/remise/retrait", include_in_schema=False)
async def legacy_check_in(reservation_id: uuid.UUID, payload: RemiseCreateRequest, current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _disabled_legacy_inspection(reservation_id, current_user, db)


@router.post("/reservations/{reservation_id}/remise/retour", include_in_schema=False)
async def legacy_check_out(reservation_id: uuid.UUID, payload: RemiseCreateRequest, current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _disabled_legacy_inspection(reservation_id, current_user, db)


@router.get("/reservations/{reservation_id}/remise", include_in_schema=False)
async def legacy_list(reservation_id: uuid.UUID, current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    reports = await list_inspections_for_booking(reservation_id, current_user, db)
    return {"reservation_id": reservation_id, "rapports": reports, "confirmation_cash": None}


@router.get("/remises/reservation/{booking_id}", include_in_schema=False)
async def legacy_handoff_list(booking_id: uuid.UUID, current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await legacy_list(booking_id, current_user, db)


@router.post("/reservations/{reservation_id}/remise/cash", include_in_schema=False)
async def legacy_cash(reservation_id: uuid.UUID, payload: CashConfirmationRequest, current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _booking(reservation_id, current_user, db)
    raise _api_error(503, "CASH_CONFIRMATION_UNAVAILABLE", "La confirmation vérifiable du paiement cash n'est pas disponible.")


@router.post("/remises/confirmation-cash", include_in_schema=False)
async def legacy_cash_receipt(
    booking_id: uuid.UUID, montant_loyer: float, montant_caution: float,
    current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await _booking(booking_id, current_user, db)
    raise _api_error(503, "CASH_CONFIRMATION_UNAVAILABLE", "La confirmation vérifiable du paiement cash n'est pas disponible.")


@router.post("/inspections/seal", include_in_schema=False)
async def legacy_seal(payload: InspectionCreateRequest, current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _disabled_legacy_inspection(payload.booking_id, current_user, db)


@router.post("/remises/check-in", include_in_schema=False)
async def legacy_compat_check_in(payload: CheckInSubmissionRequest, current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _disabled_legacy_inspection(payload.booking_id, current_user, db)


@router.post("/remises/check-out", include_in_schema=False)
async def legacy_compat_check_out(payload: CheckOutSubmissionRequest, current_user: Utilisateur = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _disabled_legacy_inspection(payload.booking_id, current_user, db)
