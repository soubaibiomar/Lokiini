import uuid
import hashlib
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import Article, Reservation, Utilisateur, ConfirmationCash, Remise
from app.routers.auth import get_current_user
from app.schemas.schemas import (
    ReservationCreate, ReservationResponse, ReservationStatusUpdate, ContractSignRequest,
    PriceCalculationRequest, PriceCalculationResponse
)

router = APIRouter(tags=["Réservations & Contrats COD"])

# Calculation helper for discounts in Morocco
def calculate_rental_price(prix_par_jour: float, start_date: date, end_date: date) -> Dict[str, Any]:
    total_days = max(1, (end_date - start_date).days)
    discount_pct = 0
    if total_days >= 30:
        discount_pct = 30 # -30% au mois
    elif total_days >= 7:
        discount_pct = 15 # -15% à la semaine
    elif total_days >= 3:
        discount_pct = 5

    discounted_daily = prix_par_jour * (1 - discount_pct / 100.0)
    prix_total = round(discounted_daily * total_days, 2)
    commission = round(prix_total * 0.15, 2)

    return {
        "total_days": total_days,
        "daily_base_price": prix_par_jour,
        "discount_pct": discount_pct,
        "prix_total": prix_total,
        "commission": commission
    }


# ==============================================================================
# 1. CALCUL DE PRIX (PRICING ESTIMATOR)
# ==============================================================================
@router.post("/reservations/calcul-prix", response_model=PriceCalculationResponse)
@router.post("/bookings/calculate-price", response_model=PriceCalculationResponse)
async def calculer_prix_location(
    payload: PriceCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calcule le tarif exact avec réductions de durée et montant de la caution cash à prévoir."""
    result = await db.execute(select(Article).where(Article.id == payload.equipment_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    calc = calculate_rental_price(float(article.prix_par_jour), payload.start_date, payload.end_date)

    return PriceCalculationResponse(
        total_days=calc["total_days"],
        daily_base_price_mad=calc["daily_base_price"],
        discount_percentage=calc["discount_pct"],
        discounted_daily_rate_mad=round(calc["prix_total"] / calc["total_days"], 2),
        subtotal_rental_mad=calc["prix_total"],
        platform_commission_mad=calc["commission"],
        total_due_renter_mad=calc["prix_total"],
        deposit_hold_mad=float(article.montant_caution)
    )


# ==============================================================================
# 2. CRÉATION D'UNE RÉSERVATION (FLUX COD CASH)
# ==============================================================================
@router.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
@router.post("/bookings", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def creer_reservation_cod(
    payload: ReservationCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Initie une réservation Cash on Delivery (COD) avec génération du contrat numérique sous Dahir des Obligations et Contrats."""
    if payload.date_fin < payload.date_debut:
        raise HTTPException(status_code=400, detail="La date de fin ne peut pas être antérieure à la date de début.")

    # Récupération de l'article
    result = await db.execute(select(Article).where(Article.id == payload.article_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    if article.loueur_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas louer votre propre matériel.")

    # Vérification KYC si l'article est à risque élevé
    if article.niveau_risque == "eleve" and current_user.statut_verification != "approuve":
        statut_initial = "en_attente_verification"
    else:
        statut_initial = "en_attente_approbation"

    calc = calculate_rental_price(float(article.prix_par_jour), payload.date_debut, payload.date_fin)

    nouvelle_reservation = Reservation(
        article_id=article.id,
        locataire_id=current_user.id,
        loueur_id=article.loueur_id,
        date_debut=payload.date_debut,
        date_fin=payload.date_fin,
        prix_total=calc["prix_total"],
        montant_caution=article.montant_caution,
        option_livraison=payload.option_livraison or "retrait_sur_place",
        adresse_retrait=payload.adresse_retrait or article.adresse,
        statut=statut_initial,
        contrat_pdf_url=f"/contrats/contrat_bail_{uuid.uuid4().hex[:12]}.pdf",
        contrat_signe=False
    )

    db.add(nouvelle_reservation)
    await db.commit()
    await db.refresh(nouvelle_reservation)

    return ReservationResponse(
        id=nouvelle_reservation.id,
        article_id=nouvelle_reservation.article_id,
        locataire_id=nouvelle_reservation.locataire_id,
        loueur_id=nouvelle_reservation.loueur_id,
        date_debut=nouvelle_reservation.date_debut,
        date_fin=nouvelle_reservation.date_fin,
        prix_total=float(nouvelle_reservation.prix_total),
        montant_caution=float(nouvelle_reservation.montant_caution),
        option_livraison=nouvelle_reservation.option_livraison,
        adresse_retrait=nouvelle_reservation.adresse_retrait,
        statut=nouvelle_reservation.statut,
        contrat_pdf_url=nouvelle_reservation.contrat_pdf_url,
        contrat_signe=nouvelle_reservation.contrat_signe,
        contrat_signe_le=nouvelle_reservation.contrat_signe_le,
        cree_le=nouvelle_reservation.cree_le,
        article_titre=article.titre,
        article_photo=article.photos[0] if article.photos else None,
        locataire_nom=current_user.nom_complet,
        loueur_nom="Loueur Partenaire"
    )


# ==============================================================================
# 3. LISTE DE MES RÉSERVATIONS (LOCATAIRE & LOUEUR)
# ==============================================================================
@router.get("/reservations/moi", response_model=List[ReservationResponse])
@router.get("/bookings/my", response_model=List[ReservationResponse])
async def mes_reservations(
    role_vue: Optional[str] = Query("locataire", description="locataire ou loueur"),
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Liste toutes les réservations de l'utilisateur connecté."""
    if role_vue == "loueur":
        query = select(Reservation).where(Reservation.loueur_id == current_user.id)
    else:
        query = select(Reservation).where(Reservation.locataire_id == current_user.id)

    query = query.order_by(Reservation.cree_le.desc())
    result = await db.execute(query)
    reservations = result.scalars().all()

    reponses = []
    for r in reservations:
        reponses.append(ReservationResponse(
            id=r.id,
            article_id=r.article_id,
            locataire_id=r.locataire_id,
            loueur_id=r.loueur_id,
            date_debut=r.date_debut,
            date_fin=r.date_fin,
            prix_total=float(r.prix_total),
            montant_caution=float(r.montant_caution),
            option_livraison=r.option_livraison,
            adresse_retrait=r.adresse_retrait,
            statut=r.statut,
            contrat_pdf_url=r.contrat_pdf_url,
            contrat_signe=r.contrat_signe,
            contrat_signe_le=r.contrat_signe_le,
            cree_le=r.cree_le,
            article_titre=r.article.titre if r.article else "Article",
            article_photo=r.article.photos[0] if r.article and r.article.photos else None,
            locataire_nom=r.locataire.nom_complet if r.locataire else "Locataire",
            loueur_nom=r.loueur.nom_complet if r.loueur else "Loueur"
        ))
    return reponses


# ==============================================================================
# 4. DÉTAIL D'UNE RÉSERVATION
# ==============================================================================
@router.get("/reservations/{reservation_id}", response_model=ReservationResponse)
@router.get("/bookings/{reservation_id}", response_model=ReservationResponse)
async def detail_reservation(
    reservation_id: uuid.UUID,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Consulte le statut, le bail et le récapitulatif financier d'une réservation."""
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    return ReservationResponse(
        id=r.id,
        article_id=r.article_id,
        locataire_id=r.locataire_id,
        loueur_id=r.loueur_id,
        date_debut=r.date_debut,
        date_fin=r.date_fin,
        prix_total=float(r.prix_total),
        montant_caution=float(r.montant_caution),
        option_livraison=r.option_livraison,
        adresse_retrait=r.adresse_retrait,
        statut=r.statut,
        contrat_pdf_url=r.contrat_pdf_url,
        contrat_signe=r.contrat_signe,
        contrat_signe_le=r.contrat_signe_le,
        cree_le=r.cree_le,
        article_titre=r.article.titre if r.article else "Article",
        article_photo=r.article.photos[0] if r.article and r.article.photos else None,
        locataire_nom=r.locataire.nom_complet if r.locataire else "Locataire",
        loueur_nom=r.loueur.nom_complet if r.loueur else "Loueur"
    )


# ==============================================================================
# 5. MISE À JOUR DE STATUT & SIGNATURE CONTRAT
# ==============================================================================
@router.put("/reservations/{reservation_id}/statut")
async def modifier_statut_reservation(
    reservation_id: uuid.UUID,
    payload: ReservationStatusUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change l'état du cycle de vie de la réservation."""
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    r.statut = payload.statut
    r.modifie_le = datetime.utcnow()
    await db.commit()
    return {"statut": "succes", "nouveau_statut": r.statut}


@router.post("/reservations/{reservation_id}/contrat/signer")
async def signer_contrat_numerique(
    reservation_id: uuid.UUID,
    payload: ContractSignRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Applique la signature électronique horodatée sur le contrat de bail (Loi 53-05)."""
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    r.contrat_signe = True
    r.contrat_signe_le = datetime.utcnow()
    await db.commit()

    return {
        "statut": "succes",
        "contrat_signe": True,
        "date_signature": r.contrat_signe_le,
        "contrat_pdf_url": r.contrat_pdf_url,
        "message": "Contrat de location signé et certifié juridiquement."
    }


# ==============================================================================
# 6. DASHBOARD DU LOUEUR (GAINS & DEMANDES ENTRANTES)
# ==============================================================================
@router.get("/dashboard/demandes")
async def demandes_entrantes(
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Demandes de location entrantes en attente de validation par le loueur."""
    query = select(Reservation).where(
        Reservation.loueur_id == current_user.id,
        Reservation.statut.in_(["en_attente_approbation", "en_attente_verification"])
    ).order_by(Reservation.cree_le.desc())

    result = await db.execute(query)
    demandes = result.scalars().all()

    return [{
        "reservation_id": d.id,
        "article_titre": d.article.titre if d.article else "",
        "locataire_nom": d.locataire.nom_complet if d.locataire else "",
        "date_debut": d.date_debut,
        "date_fin": d.date_fin,
        "montant_cash_total": float(d.prix_total),
        "caution_cash": float(d.montant_caution),
        "statut": d.statut
    } for d in demandes]


@router.put("/dashboard/demandes/{reservation_id}")
async def traiter_demande(
    reservation_id: uuid.UUID,
    action: str = Query(..., description="approuver ou refuser"),
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approuve ou refuse une demande de location entrante."""
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id, Reservation.loueur_id == current_user.id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Demande introuvable.")

    if action == "approuver":
        r.statut = "confirme_cod"
    else:
        r.statut = "annule"

    r.modifie_le = datetime.utcnow()
    await db.commit()
    return {"statut": "succes", "action": action, "nouveau_statut": r.statut}


@router.get("/dashboard/gains")
async def tableau_de_bord_gains(
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Récapitulatif des gains, commissions et paiements cash attendus."""
    result = await db.execute(
        select(Reservation).where(
            Reservation.loueur_id == current_user.id,
            Reservation.statut.in_(["termine", "en_cours", "confirme_cod"])
        )
    )
    reservations = result.scalars().all()

    gains_encaisses = sum(float(r.prix_total) * 0.85 for r in reservations if r.statut == "termine")
    gains_en_cours = sum(float(r.prix_total) * 0.85 for r in reservations if r.statut in ["en_cours", "confirme_cod"])
    commissions_totales = sum(float(r.prix_total) * 0.15 for r in reservations)

    return {
        "gains_encaisses_mad": round(gains_encaisses, 2),
        "gains_en_attente_remise_mad": round(gains_en_cours, 2),
        "commissions_lokiini_mad": round(commissions_totales, 2),
        "nombre_locations_totales": len(reservations),
        "devise": "MAD"
    }
