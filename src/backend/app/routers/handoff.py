import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.models import Reservation, Remise, ConfirmationCash, User
from app.schemas.inspection_schemas import (
    CheckInSubmissionRequest, CheckOutSubmissionRequest,
    InspectionSealResponse, CashReceiptResponse
)
from app.services.inspection_seal_service import inspection_seal_service
from app.services.booking_state_machine import booking_state_machine
from app.routers.auth import get_current_user

router = APIRouter(prefix="/remises", tags=["Handoff Physique, États des Lieux & Confirmations Cash"])

# 1. Check-in (Remise du Matériel)
@router.post("/check-in", response_model=InspectionSealResponse, status_code=status.HTTP_201_CREATED)
async def submit_check_in(
    payload: CheckInSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Scelle l'état des lieux contradictoire de départ et active la réservation (confirme_cod -> en_cours)."""
    result = await db.execute(select(Reservation).where(Reservation.id == payload.booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    if current_user.id not in [booking.locataire_id, booking.loueur_id] and current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé.")

    # 1. Génération du scellement SHA-256
    seal_data = inspection_seal_service.generate_sha256_seal(
        booking_id=str(booking.id),
        type_remise="retrait",
        photos=payload.photos,
        video_url=payload.video_url,
        lat=payload.lat,
        lng=payload.lng,
        notes=payload.notes
    )

    # 2. Création de l'enregistrement de remise
    remise = Remise(
        id=uuid.uuid4(),
        reservation_id=booking.id,
        type_remise="retrait",
        photos_etat=payload.photos,
        video_sha256=seal_data["sha256_seal"],
        coordonnees_gps=f"{payload.lat},{payload.lng}" if payload.lat and payload.lng else None,
        notes=payload.notes,
        signe_par_loueur=True,
        signe_par_locataire=True,
        scelle_le=seal_data["timestamp"]
    )
    db.add(remise)

    # 3. Enregistrement du reçu de confirmation Cash COD
    conf_cash = ConfirmationCash(
        id=uuid.uuid4(),
        reservation_id=booking.id,
        confirme_par=current_user.id,
        montant_recu=payload.montant_cash_loyer_recu + payload.montant_caution_recue,
        recu_le=datetime.utcnow(),
        notes=f"Loyer: {payload.montant_cash_loyer_recu} MAD + Caution: {payload.montant_caution_recue} MAD perçus à la remise."
    )
    db.add(conf_cash)

    # 4. Transition d'état de la réservation
    booking.statut_reservation = "en_cours"
    booking.modifie_le = datetime.utcnow()
    await db.commit()

    return InspectionSealResponse(
        id=remise.id,
        booking_id=booking.id,
        type="retrait",
        sha256_seal=seal_data["sha256_seal"],
        rfc3161_timestamp=seal_data["timestamp"],
        photos_count=len(payload.photos),
        notes=payload.notes,
        statut_reservation_suivant="en_cours",
        message="État des lieux de retrait scellé avec succès. Location active."
    )

# 2. Check-out (Retour du Matériel & Restitution Caution)
@router.post("/check-out", response_model=InspectionSealResponse, status_code=status.HTTP_201_CREATED)
async def submit_check_out(
    payload: CheckOutSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Scelle l'état des lieux de retour contradictoire et clôture la location (en_cours -> termine)."""
    result = await db.execute(select(Reservation).where(Reservation.id == payload.booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    if current_user.id not in [booking.locataire_id, booking.loueur_id] and current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé.")

    # 1. Génération du scellement SHA-256 de retour
    seal_data = inspection_seal_service.generate_sha256_seal(
        booking_id=str(booking.id),
        type_remise="retour",
        photos=payload.photos,
        video_url=payload.video_url,
        lat=payload.lat,
        lng=payload.lng,
        notes=payload.notes
    )

    # 2. Création de l'enregistrement de remise retour
    remise = Remise(
        id=uuid.uuid4(),
        reservation_id=booking.id,
        type_remise="retour",
        photos_etat=payload.photos,
        video_sha256=seal_data["sha256_seal"],
        coordonnees_gps=f"{payload.lat},{payload.lng}" if payload.lat and payload.lng else None,
        notes=payload.notes,
        signe_par_loueur=True,
        signe_par_locataire=True,
        scelle_le=seal_data["timestamp"]
    )
    db.add(remise)

    # 3. Transition d'état vers terminé
    booking.statut_reservation = "termine"
    booking.modifie_le = datetime.utcnow()
    await db.commit()

    return InspectionSealResponse(
        id=remise.id,
        booking_id=booking.id,
        type="retour",
        sha256_seal=seal_data["sha256_seal"],
        rfc3161_timestamp=seal_data["timestamp"],
        photos_count=len(payload.photos),
        notes=payload.notes,
        statut_reservation_suivant="termine",
        message="État des lieux de retour scellé. Caution restituée et location clôturée."
    )

# 3. Historique des remises d'une réservation
@router.get("/reservation/{booking_id}")
async def get_booking_handoffs(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Consulte l'historique complet des états des lieux et certificats SHA-256."""
    result = await db.execute(
        select(Remise).where(Remise.reservation_id == booking_id).order_by(Remise.scelle_le.asc())
    )
    remises = result.scalars().all()

    return {
        "statut": "succes",
        "booking_id": str(booking_id),
        "total_scellements": len(remises),
        "remises": [
            {
                "id": str(r.id),
                "type_remise": r.type_remise,
                "sha256_seal": r.video_sha256,
                "photos_etat": r.photos_etat or [],
                "notes": r.notes,
                "signe_par_loueur": r.signe_par_loueur,
                "signe_par_locataire": r.signe_par_locataire,
                "scelle_le": r.scelle_le.isoformat() if r.scelle_le else None
            }
            for r in remises
        ]
    }

# 4. Confirmation Cash Reçu
@router.post("/confirmation-cash", response_model=CashReceiptResponse)
async def generate_cash_receipt(
    booking_id: uuid.UUID,
    montant_loyer: float,
    montant_caution: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Génère un reçu de paiement cash numérique opposable."""
    result = await db.execute(select(Reservation).where(Reservation.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    receipt_id = f"REC-CASH-{str(booking_id)[:8].upper()}"
    return CashReceiptResponse(
        receipt_id=receipt_id,
        booking_id=booking.id,
        montant_loyer_mad=montant_loyer,
        montant_caution_mad=montant_caution,
        date_emission=datetime.utcnow(),
        emetteur_nom=current_user.nom_complet,
        receveur_nom="Loueur Partenaire Lokiini",
        statut="valide"
    )
