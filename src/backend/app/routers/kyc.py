import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.authorization import require_resource_access
from app.core.database import get_db
from app.models.models import User
from app.routers.auth import get_current_user
from app.schemas.kyc_schemas import (
    DiditWebhookPayload,
    KYCInitiateRequest,
    KYCInitiateResponse,
    KYCStatusResponse,
)
from app.services.didit_service import didit_service
from app.services.kyc_lifecycle import (
    KYCStatus,
    KYCTransitionError,
    apply_provider_status,
    normalize_internal_status,
    transition,
)
from app.services.notification_service import NotificationEvent, notify


router = APIRouter(tags=["KYC"])


@router.post("/auth/kyc/initier", response_model=KYCInitiateResponse)
@router.post("/kyc/initier", response_model=KYCInitiateResponse)
async def initiate_kyc_session(
    payload: Optional[KYCInitiateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a hosted provider session for the authenticated user only."""
    current_status = normalize_internal_status(current_user.statut_verification)
    if current_status == KYCStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "KYC_ALREADY_VERIFIED", "message": "L'identité est déjà vérifiée."},
        )
    if current_status in (KYCStatus.PENDING, KYCStatus.IN_REVIEW):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "KYC_IN_PROGRESS", "message": "Une vérification KYC est déjà en cours."},
        )

    try:
        session_data = await didit_service.initiate_verification_session(user_id=str(current_user.id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "KYC_UNAVAILABLE",
                "message": "Le fournisseur KYC est indisponible. Aucun résultat de vérification n'a été enregistré.",
            },
        )

    current_user.didit_session_id = session_data["session_id"]
    current_user.kyc_last_event_id = None
    transition(current_user, KYCStatus.PENDING, provider_status=session_data["provider_status"])
    await db.commit()

    return KYCInitiateResponse(
        session_id=session_data["session_id"],
        session_token=session_data["session_token"],
        verification_url=session_data["verification_url"],
        status=KYCStatus.PENDING,
    )


def _hosted_flow_only() -> None:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail={
            "code": "KYC_PROVIDER_FLOW_REQUIRED",
            "message": "Utilisez la session hébergée du fournisseur KYC; Lokiini n'accepte pas de données biométriques.",
        },
    )


@router.post("/auth/kyc/document", status_code=status.HTTP_410_GONE)
@router.post("/kyc/document", status_code=status.HTTP_410_GONE)
async def submit_kyc_document(current_user: User = Depends(get_current_user)):
    _hosted_flow_only()


@router.post("/auth/kyc/selfie", status_code=status.HTTP_410_GONE)
@router.post("/kyc/selfie", status_code=status.HTTP_410_GONE)
async def submit_kyc_selfie(current_user: User = Depends(get_current_user)):
    _hosted_flow_only()


@router.post("/auth/kyc/webhook/didit")
@router.post("/kyc/webhook/didit")
async def didit_webhook_callback(
    request: Request,
    x_signature_v2: Optional[str] = Header(None, alias="X-Signature-V2"),
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    x_timestamp: Optional[str] = Header(None, alias="X-Timestamp"),
    db: AsyncSession = Depends(get_db),
):
    """Apply a signed status event without persisting its biometric decision body."""
    raw_body = await request.body()
    try:
        data = json.loads(raw_body.decode("utf-8"))
        payload = DiditWebhookPayload.model_validate(data)
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "KYC_WEBHOOK_INVALID", "message": "Payload Didit invalide."},
        )

    signature_valid = False
    if x_timestamp and x_signature_v2:
        signature_valid = didit_service.verify_webhook_signature(
            raw_body,
            x_signature_v2,
            timestamp_header=x_timestamp,
            parsed_payload=data,
        )
    if x_timestamp and not signature_valid and x_signature:
        signature_valid = didit_service.verify_webhook_signature(
            raw_body,
            x_signature,
            timestamp_header=x_timestamp,
        )
    if not signature_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "KYC_HMAC_INVALID", "message": "Signature ou horodatage Didit invalide."},
        )
    if payload.session_kind not in (None, "user", "KYC"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "KYC_SESSION_KIND_INVALID", "message": "Le webhook ne concerne pas une session KYC."},
        )

    result = await db.execute(select(User).where(User.id == payload.vendor_data))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
    if user.didit_session_id != payload.session_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "KYC_SESSION_MISMATCH", "message": "La session Didit ne correspond pas à l'utilisateur."},
        )

    event_id = str(payload.event_id)
    if user.kyc_last_event_id == event_id:
        return {"accepted": True, "duplicate": True, "status": user.statut_verification}

    try:
        internal_status = apply_provider_status(user, payload.status)
    except KYCTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "KYC_TRANSITION_INVALID", "message": str(exc)},
        )
    user.kyc_last_event_id = event_id
    kyc_copy = {
        KYCStatus.PENDING: ("Vérification reçue", "Votre vérification d’identité est en attente de traitement."),
        KYCStatus.IN_REVIEW: ("Vérification en cours", "Votre vérification d’identité est en cours d’examen."),
        KYCStatus.VERIFIED: ("Identité vérifiée", "Votre identité a été vérifiée par le fournisseur configuré."),
        KYCStatus.REJECTED: ("Vérification non validée", "La vérification d’identité n’a pas été validée."),
        KYCStatus.REQUIRES_ACTION: ("Action de vérification requise", "Le fournisseur demande une action supplémentaire pour continuer."),
    }
    title, body = kyc_copy.get(
        internal_status,
        ("Statut de vérification mis à jour", "Le statut de votre vérification d’identité a été mis à jour."),
    )
    notify(
        db,
        recipient_id=user.id,
        event_type=NotificationEvent.KYC_UPDATED,
        title=title,
        body=body,
        user_id=user.id,
    )
    await db.commit()
    return {"accepted": True, "duplicate": False, "status": internal_status.value}


@router.get("/auth/kyc/statut/{user_id}", response_model=KYCStatusResponse)
@router.get("/kyc/statut/{user_id}", response_model=KYCStatusResponse)
async def get_kyc_status(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
    require_resource_access(current_user, user.id)
    return KYCStatusResponse(
        user_id=user.id,
        status=normalize_internal_status(user.statut_verification),
        verified_at=user.verifie_le,
        session_id=user.didit_session_id,
    )


@router.post("/kyc/verify", status_code=status.HTTP_410_GONE)
async def submit_kyc_verification_legacy(current_user: User = Depends(get_current_user)):
    _hosted_flow_only()
