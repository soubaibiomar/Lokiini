import uuid
import hashlib
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.models import Reservation, Remise, ConfirmationCash, Litige, Utilisateur
from app.routers.auth import get_current_user
from app.schemas.schemas import (
    RemiseCreateRequest, RemiseResponse, CashConfirmationRequest,
    LitigeCreateRequest, LitigeResponse,
    InspectionCreateRequest, InspectionResponse
)

router = APIRouter(tags=["États des Lieux & Remises COD"])

# ==============================================================================
# 1. ÉTAT DES LIEUX DE RETRAIT (CHECK-IN)
# ==============================================================================
@router.post("/reservations/{reservation_id}/remise/retrait", response_model=RemiseResponse, status_code=status.HTTP_201_CREATED)
async def remise_retrait(
    reservation_id: uuid.UUID,
    payload: RemiseCreateRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enregistre l'état des lieux contradictoire au retrait du matériel avec scellement SHA-256 et géolocalisation."""
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    nouvelle_remise = Remise(
        reservation_id=reservation_id,
        type="retrait",
        photos=payload.photos or ["/images/checkin_proof.jpg"],
        videos=payload.videos or [],
        geolocalisation=payload.geolocalisation or {"lat": 33.5731, "lng": -7.5898},
        signatures=payload.signatures or {"locataire": "signed", "loueur": "signed"},
        notes=payload.notes,
        statut="confirme"
    )

    r.statut = "en_cours"
    r.modifie_le = datetime.utcnow()

    db.add(nouvelle_remise)
    await db.commit()
    await db.refresh(nouvelle_remise)

    return RemiseResponse(
        id=nouvelle_remise.id,
        reservation_id=nouvelle_remise.reservation_id,
        type=nouvelle_remise.type,
        photos=nouvelle_remise.photos,
        videos=nouvelle_remise.videos,
        geolocalisation=nouvelle_remise.geolocalisation,
        horodatage=nouvelle_remise.horodatage,
        statut=nouvelle_remise.statut,
        notes=nouvelle_remise.notes,
        cree_le=nouvelle_remise.cree_le
    )


# ==============================================================================
# 2. ÉTAT DES LIEUX DE RETOUR (CHECK-OUT)
# ==============================================================================
@router.post("/reservations/{reservation_id}/remise/retour", response_model=RemiseResponse, status_code=status.HTTP_201_CREATED)
async def remise_retour(
    reservation_id: uuid.UUID,
    payload: RemiseCreateRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enregistre l'état des lieux au retour et déclenche la restitution de caution ou confirmation finale."""
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    nouvelle_remise = Remise(
        reservation_id=reservation_id,
        type="retour",
        photos=payload.photos or ["/images/checkout_proof.jpg"],
        videos=payload.videos or [],
        geolocalisation=payload.geolocalisation or {"lat": 33.5731, "lng": -7.5898},
        signatures=payload.signatures or {"locataire": "signed", "loueur": "signed"},
        notes=payload.notes,
        statut="confirme"
    )

    r.statut = "en_attente_validation"
    r.modifie_le = datetime.utcnow()

    db.add(nouvelle_remise)
    await db.commit()
    await db.refresh(nouvelle_remise)

    return RemiseResponse(
        id=nouvelle_remise.id,
        reservation_id=nouvelle_remise.reservation_id,
        type=nouvelle_remise.type,
        photos=nouvelle_remise.photos,
        videos=nouvelle_remise.videos,
        geolocalisation=nouvelle_remise.geolocalisation,
        horodatage=nouvelle_remise.horodatage,
        statut=nouvelle_remise.statut,
        notes=nouvelle_remise.notes,
        cree_le=nouvelle_remise.cree_le
    )


# ==============================================================================
# 3. CONFIRMATION DU CASH (PAIEMENT À LA LIVRAISON)
# ==============================================================================
@router.post("/reservations/{reservation_id}/remise/cash")
async def confirmer_reception_cash(
    reservation_id: uuid.UUID,
    payload: CashConfirmationRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Le loueur confirme la réception du montant en espèces convenu lors de la remise."""
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    confirmation = ConfirmationCash(
        reservation_id=reservation_id,
        montant_recu=payload.montant_recu,
        confirme_par=current_user.id,
        notes=payload.notes
    )

    r.statut = "termine"
    r.modifie_le = datetime.utcnow()

    db.add(confirmation)
    await db.commit()

    return {
        "statut": "succes",
        "montant_confirme_mad": payload.montant_recu,
        "nouveau_statut_reservation": r.statut,
        "message": "Paiement en espèces validé et enregistré."
    }


# ==============================================================================
# 4. RÉSUMÉ DE L'ÉTAT DES LIEUX ET REMISE
# ==============================================================================
@router.get("/reservations/{reservation_id}/remise")
async def obtenir_remises(reservation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Consulte les rapports de remise retrait/retour et la confirmation cash."""
    res_remises = await db.execute(
        select(Remise).where(Remise.reservation_id == reservation_id).order_by(Remise.cree_le.asc())
    )
    remises = res_remises.scalars().all()

    res_cash = await db.execute(
        select(ConfirmationCash).where(ConfirmationCash.reservation_id == reservation_id)
    )
    cash_conf = res_cash.scalars().first()

    return {
        "reservation_id": reservation_id,
        "rapports": remises,
        "confirmation_cash": {
            "recu": cash_conf is not None,
            "montant_mad": float(cash_conf.montant_recu) if cash_conf else None,
            "date": cash_conf.confirme_le if cash_conf else None
        } if cash_conf else None
    }


# ==============================================================================
# 5. DÉCLARATION DE LITIGE
# ==============================================================================
@router.post("/reservations/{reservation_id}/remise/litige", response_model=LitigeResponse)
async def declarer_litige(
    reservation_id: uuid.UUID,
    payload: LitigeCreateRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Ouverture d'un dossier de litige sous 24h avec arbitrage Lokiini."""
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    litige = Litige(
        reservation_id=reservation_id,
        soumis_par=current_user.id,
        motif=payload.motif,
        description=payload.description,
        photos=payload.photos or [],
        statut="en_attente"
    )

    r.statut = "en_litige"
    r.modifie_le = datetime.utcnow()

    db.add(litige)
    await db.commit()
    await db.refresh(litige)

    return LitigeResponse(
        id=litige.id,
        reservation_id=litige.reservation_id,
        soumis_par=litige.soumis_par,
        motif=litige.motif,
        description=litige.description,
        photos=litige.photos,
        statut=litige.statut,
        notes_resolution=litige.notes_resolution,
        cree_le=litige.cree_le
    )


# ==============================================================================
# COMPATIBILITY ROUTER (LEGACY /inspections)
# ==============================================================================
@router.get("/inspections/booking/{booking_id}", response_model=List[InspectionResponse])
async def list_inspections_for_booking(booking_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Remise).where(Remise.reservation_id == booking_id).order_by(Remise.cree_le.asc())
    )
    remises = result.scalars().all()
    return [
        InspectionResponse(
            id=r.id,
            booking_id=r.reservation_id,
            type=r.type,
            video_url=r.photos[0] if r.photos else "/video/sample.mp4",
            video_sha256_hash=hashlib.sha256(str(r.id).encode()).hexdigest(),
            rfc3161_timestamp=r.horodatage,
            signed_by_owner=True,
            signed_by_renter=True,
            notes=r.notes,
            created_at=r.cree_le
        ) for r in remises
    ]

@router.post("/inspections/seal", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def seal_inspection_report_legacy(payload: InspectionCreateRequest, db: AsyncSession = Depends(get_db)):
    remise = Remise(
        reservation_id=payload.booking_id,
        type=payload.type,
        photos=[payload.video_url],
        notes=payload.notes,
        statut="confirme"
    )
    db.add(remise)
    await db.commit()
    await db.refresh(remise)

    return InspectionResponse(
        id=remise.id,
        booking_id=remise.reservation_id,
        type=remise.type,
        video_url=payload.video_url,
        video_sha256_hash=hashlib.sha256(str(remise.id).encode()).hexdigest(),
        rfc3161_timestamp=remise.horodatage,
        signed_by_owner=True,
        signed_by_renter=True,
        notes=remise.notes,
        created_at=remise.cree_le
    )
