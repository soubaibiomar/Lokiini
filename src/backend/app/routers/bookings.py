import uuid
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from app.core.database import get_db
from app.models.models import Article, Reservation, Booking, User
from app.schemas.booking_schemas import (
    PricingCalculationRequest, PricingBreakdownResponse,
    BookingCreateRequest, BookingStatusUpdateRequest,
    BookingItemResponse, BookingDetailResponse
)
from app.services.pricing_service import pricing_service
from app.services.booking_state_machine import booking_state_machine
from app.routers.auth import get_current_user

router = APIRouter(tags=["Réservations, Tarification Dégressive & Machine à États"])

# 1. Calculateur de prix dégressif
@router.post("/reservations/calculer-prix", response_model=PricingBreakdownResponse)
@router.post("/bookings/calculate-pricing", response_model=PricingBreakdownResponse)
async def calculate_booking_pricing(
    payload: PricingCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calcule le devis complet avec application des remises de durée (3j/7j/30j) et commissions."""
    result = await db.execute(select(Article).where(Article.id == payload.article_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    loueur_res = await db.execute(select(User).where(User.id == article.loueur_id))
    loueur = loueur_res.scalars().first()
    is_pro = (loueur.user_role == "pro_owner") if loueur else False

    breakdown = pricing_service.compute_pricing_breakdown(
        prix_par_jour=float(article.prix_par_jour),
        prix_par_semaine=float(article.prix_par_semaine) if article.prix_par_semaine else None,
        prix_par_mois=float(article.prix_par_mois) if article.prix_par_mois else None,
        montant_caution=float(article.montant_caution),
        start_date=payload.date_debut,
        end_date=payload.date_fin,
        is_pro_owner=is_pro
    )
    return breakdown

# 2. Création d'une réservation
@router.post("/reservations/creer", status_code=status.HTTP_201_CREATED)
@router.post("/bookings/create", status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crée une nouvelle demande de réservation avec contrôle de disponibilité calendaire."""
    # 1. Récupération de l'article
    result = await db.execute(select(Article).where(Article.id == payload.article_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    if article.loueur_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas louer votre propre matériel."
        )

    # 2. Vérification KYC si requis pour cet article
    if article.kyc_requis and current_user.statut_verification != "approuve":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "KYC_REQUIRED",
                "message": "La vérification biométrique Didit est obligatoire pour louer ce matériel."
            }
        )

    # 3. Contrôle anti-chevauchement calendaire
    conflict_query = select(Reservation).where(
        Reservation.article_id == payload.article_id,
        Reservation.statut_reservation.in_(["confirme_cod", "en_cours"]),
        or_(
            and_(Reservation.date_debut <= payload.date_fin, Reservation.date_fin >= payload.date_debut)
        )
    )
    conflict_res = await db.execute(conflict_query)
    if conflict_res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "DATES_UNAVAILABLE", "message": "Ce matériel est déjà réservé sur les dates sélectionnées."}
        )

    # 4. Calcul de la tarification
    loueur_res = await db.execute(select(User).where(User.id == article.loueur_id))
    loueur = loueur_res.scalars().first()
    is_pro = (loueur.user_role == "pro_owner") if loueur else False

    pricing = pricing_service.compute_pricing_breakdown(
        prix_par_jour=float(article.prix_par_jour),
        prix_par_semaine=float(article.prix_par_semaine) if article.prix_par_semaine else None,
        prix_par_mois=float(article.prix_par_mois) if article.prix_par_mois else None,
        montant_caution=float(article.montant_caution),
        start_date=payload.date_debut,
        end_date=payload.date_fin,
        is_pro_owner=is_pro
    )

    # 5. Création en base
    booking_id = uuid.uuid4()
    reservation = Reservation(
        id=booking_id,
        article_id=article.id,
        locataire_id=current_user.id,
        loueur_id=article.loueur_id,
        date_debut=payload.date_debut,
        date_fin=payload.date_fin,
        nombre_jours=pricing["nombre_jours"],
        prix_total=pricing["total_location_mad"],
        montant_caution=pricing["montant_caution_mad"],
        frais_service=pricing["frais_service_plateforme_mad"],
        statut_reservation="en_attente_approbation",
        mode_paiement=payload.mode_paiement or "cash_on_delivery",
        mode_caution=payload.mode_caution or "cash",
        notes_conditions=payload.message_loueur,
        cree_le=datetime.utcnow()
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)

    return {
        "statut": "succes",
        "message": "Demande de réservation envoyée au loueur.",
        "reservation_id": str(reservation.id),
        "statut_reservation": reservation.statut_reservation,
        "total_location_mad": float(reservation.prix_total),
        "montant_caution_mad": float(reservation.montant_caution)
    }

# 3. Liste des réservations de l'utilisateur
@router.get("/reservations")
@router.get("/bookings")
async def list_user_bookings(
    role: str = Query("locataire", pattern="^(locataire|loueur|all)$"),
    statut: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Liste les réservations de l'utilisateur avec filtrage par rôle (locataire ou loueur)."""
    query = select(Reservation)

    if role == "locataire":
        query = query.where(Reservation.locataire_id == current_user.id)
    elif role == "loueur":
        query = query.where(Reservation.loueur_id == current_user.id)
    else:
        query = query.where(or_(Reservation.locataire_id == current_user.id, Reservation.loueur_id == current_user.id))

    if statut:
        query = query.where(Reservation.statut_reservation == statut)

    query = query.order_by(Reservation.cree_le.desc())
    result = await db.execute(query)
    reservations = result.scalars().all()

    items = []
    for r in reservations:
        art_res = await db.execute(select(Article).where(Article.id == r.article_id))
        art = art_res.scalars().first()

        items.append({
            "id": str(r.id),
            "article_id": str(r.article_id),
            "locataire_id": str(r.locataire_id),
            "loueur_id": str(r.loueur_id),
            "article_titre": art.titre if art else "Matériel Lokiini",
            "article_photos": art.photos if art else [],
            "date_debut": r.date_debut.isoformat(),
            "date_fin": r.date_fin.isoformat(),
            "nombre_jours": r.nombre_jours,
            "prix_total": float(r.prix_total),
            "montant_caution": float(r.montant_caution),
            "frais_service": float(r.frais_service),
            "statut_reservation": r.statut_reservation,
            "mode_paiement": r.mode_paiement,
            "mode_caution": r.mode_caution,
            "cree_le": r.cree_le.isoformat()
        })

    return {"statut": "succes", "total": len(items), "donnees": items}

# 4. Détail d'une réservation
@router.get("/reservations/{booking_id}")
@router.get("/bookings/{booking_id}")
async def get_booking_detail(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Consulte la fiche complète d'une réservation."""
    result = await db.execute(select(Reservation).where(Reservation.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    if current_user.id not in [booking.locataire_id, booking.loueur_id] and current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé à cette réservation.")

    art_res = await db.execute(select(Article).where(Article.id == booking.article_id))
    art = art_res.scalars().first()

    loc_res = await db.execute(select(User).where(User.id == booking.locataire_id))
    loc = loc_res.scalars().first()

    loueur_res = await db.execute(select(User).where(User.id == booking.loueur_id))
    loueur = loueur_res.scalars().first()

    return {
        "id": str(booking.id),
        "article_id": str(booking.article_id),
        "locataire_id": str(booking.locataire_id),
        "loueur_id": str(booking.loueur_id),
        "article": {
            "id": str(art.id) if art else None,
            "titre": art.titre if art else "Article",
            "photos": art.photos if art else [],
            "city": art.city if art else "Casablanca"
        },
        "locataire": {
            "id": str(loc.id) if loc else None,
            "nom": loc.nom_complet if loc else "Locataire",
            "statut_kyc": loc.statut_verification if loc else "en_attente"
        },
        "loueur": {
            "id": str(loueur.id) if loueur else None,
            "nom": loueur.nom_complet if loueur else "Loueur",
            "telephone": loueur.telephone if loueur else "+212600000000"
        },
        "date_debut": booking.date_debut.isoformat(),
        "date_fin": booking.date_fin.isoformat(),
        "nombre_jours": booking.nombre_jours,
        "prix_total": float(booking.prix_total),
        "montant_caution": float(booking.montant_caution),
        "frais_service": float(booking.frais_service),
        "statut_reservation": booking.statut_reservation,
        "mode_paiement": booking.mode_paiement,
        "mode_caution": booking.mode_caution,
        "bail_signe_le": booking.bail_signe_le.isoformat() if booking.bail_signe_le else None,
        "cree_le": booking.cree_le.isoformat()
    }

# 5. Changement de statut avec machine à états
@router.patch("/reservations/{booking_id}/statut")
@router.patch("/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: uuid.UUID,
    payload: BookingStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Met à jour le statut d'une réservation selon les règles inviolables de la machine à états."""
    result = await db.execute(select(Reservation).where(Reservation.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    if current_user.id not in [booking.locataire_id, booking.loueur_id] and current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé.")

    # Validation par la machine à états
    booking_state_machine.validate_transition(booking.statut_reservation, payload.nouveau_statut)

    booking.statut_reservation = payload.nouveau_statut
    booking.modifie_le = datetime.utcnow()
    await db.commit()

    return {
        "statut": "succes",
        "message": f"Statut mis à jour vers '{payload.nouveau_statut}'.",
        "reservation_id": str(booking.id),
        "nouveau_statut": booking.statut_reservation
    }
