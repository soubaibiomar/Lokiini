import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.models import User, Article, Reservation, RentalPayment, OwnerPayout, DepositRecord
from app.schemas.billing_schemas import (
    SubscriptionPlanResponse, MySubscriptionResponse,
    SubscriptionUpgradeRequest, EarningsDashboardResponse,
    InvoiceResponse
)
from app.services.subscription_service import subscription_service
from app.services.earnings_service import earnings_service
from app.routers.auth import get_current_user
from app.core.authorization import require_resource_access

router = APIRouter(tags=["Abonnements Loueurs, Dashboard des Gains & Facturation"])

# 1. Catalogue des formules d'abonnement
@router.get("/abonnements/plans", response_model=List[SubscriptionPlanResponse])
@router.get("/tarifs/plans", response_model=List[SubscriptionPlanResponse])
async def list_subscription_plans():
    """Liste les 4 formules d'abonnement loueur disponibles sur Lokiini."""
    return subscription_service.get_all_plans()

# 2. Mon statut d'abonnement
@router.get("/abonnements/moi", response_model=MySubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Consulte le forfait actuel de l'utilisateur et le nombre d'annonces actives."""
    # Count active equipment listings
    eq_res = await db.execute(select(Article).where(Article.loueur_id == current_user.id, Article.statut == "actif"))
    active_count = len(eq_res.scalars().all())

    plan_name = current_user.plan_abonnement or "Gratuit"
    details = subscription_service.get_plan_details(plan_name)

    return MySubscriptionResponse(
        plan_actuel=details["nom"],
        prix_mensuel_mad=details["prix_mensuel_mad"],
        commission_pct=details["commission_pct"],
        max_annonces=details["max_annonces"],
        annonces_actives_count=active_count,
        badge=details["badge"],
        renouvellement_le=datetime.utcnow()
    )

# 3. Mettre à niveau son abonnement
@router.post("/abonnements/upgrade")
async def upgrade_subscription(
    payload: SubscriptionUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Met à niveau le forfait d'abonnement du loueur."""
    if payload.nouveau_plan not in subscription_service.PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan '{payload.nouveau_plan}' inconnu. Choix: {list(subscription_service.PLANS.keys())}"
        )

    if payload.nouveau_plan != "Gratuit":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "PAYMENT_UNAVAILABLE", "status": "pending", "message": "Le paiement des abonnements n'est pas disponible."}
        )

    current_user.plan_abonnement = "Gratuit"
    current_user.modifie_le = datetime.utcnow()
    await db.commit()
    return {"statut": "succes", "nouveau_plan": "Gratuit", "commission_pct": 15.0}


@router.post("/abonnements/annuler")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retains the legacy cancellation path in the authoritative billing domain."""
    current_user.plan_abonnement = "Gratuit"
    current_user.abonnement_valable_jusqu = None
    current_user.modifie_le = datetime.utcnow()
    await db.commit()
    return {
        "statut": "succes",
        "nouveau_plan": "Gratuit",
        "message": "Abonnement réinitialisé vers la formule Gratuite.",
    }

# 4. Tableau de bord des gains en MAD
@router.get("/dashboard/gains", response_model=EarningsDashboardResponse)
async def get_owner_earnings_dashboard(
    periode: str = Query("mois", pattern="^(jour|semaine|mois|annee)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calcule le tableau de bord financier des gains et commissions en MAD."""
    query = select(Reservation).where(Reservation.loueur_id == current_user.id)
    result = await db.execute(query)
    reservations = result.scalars().all()
    payout_result = await db.execute(select(OwnerPayout).where(OwnerPayout.owner_id == current_user.id))
    payouts = payout_result.scalars().all()
    booking_ids = [r.id for r in reservations]
    deposits = []
    if booking_ids:
        deposit_result = await db.execute(select(DepositRecord).where(DepositRecord.booking_id.in_(booking_ids)))
        deposits = deposit_result.scalars().all()

    res_list = []
    payouts_by_booking = {p.booking_id: p for p in payouts}
    for r in reservations:
        art_res = await db.execute(select(Article).where(Article.id == r.article_id))
        art = art_res.scalars().first()
        payout = payouts_by_booking.get(r.id)
        res_list.append({
            "rental_amount": float(payout.rental_amount_mad) if payout else 0,
            "platform_fee": float(payout.platform_fee_amount_mad) if payout else 0,
            "payout_amount": float(payout.payout_amount_mad) if payout else 0,
            "payout_status": payout.status if payout else "not_ready",
            "statut_reservation": r.statut,
            "article_titre": art.titre if art else "Matériel"
        })
    released_deposits = sum(
        float(d.released_amount_mad) for d in deposits if d.status == "released"
    )
    return earnings_service.calculate_dashboard_metrics(
        res_list, periode=periode, released_deposits_mad=released_deposits
    )

# 5. Facturation BTP & Fiscalité Marocaine
@router.get("/factures/{booking_id}", response_model=InvoiceResponse)
async def generate_invoice(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Génère la facture conforme avec mention de l'ICE et TVA à 20% sur la commission."""
    result = await db.execute(select(Reservation).where(Reservation.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")
    require_resource_access(current_user, booking.locataire_id, booking.loueur_id)
    payment_result = await db.execute(
        select(RentalPayment).where(
            RentalPayment.booking_id == booking.id,
            RentalPayment.status.in_(["succeeded", "partially_refunded"]),
        ).order_by(RentalPayment.created_at.desc()).limit(1)
    )
    if not payment_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "PAYMENT_NOT_CONFIRMED", "status": "pending", "message": "Aucun paiement confirmé ne permet d'émettre une facture."}
        )

    loc_res = await db.execute(select(User).where(User.id == booking.locataire_id))
    locataire = loc_res.scalars().first()

    loueur_res = await db.execute(select(User).where(User.id == booking.loueur_id))
    loueur = loueur_res.scalars().first()

    montant_total = float(booking.prix_total)
    montant_ht = round(montant_total / 1.20, 2)
    montant_tva = round(montant_total - montant_ht, 2)

    if not loueur or not loueur.company_ice:
        raise HTTPException(status_code=409, detail="ICE du loueur requis pour émettre la facture.")

    return InvoiceResponse(
        numero_facture=f"FACT-LOKIINI-{str(booking.id)[:8].upper()}-{datetime.utcnow().year}",
        booking_id=booking.id,
        date_emission=datetime.utcnow(),
        emetteur_societe=loueur.company_name or loueur.nom_complet,
        emetteur_ice=loueur.company_ice,
        client_nom=locataire.nom_complet if locataire else "Client",
        client_ice=locataire.company_ice if locataire else None,
        montant_ht_mad=montant_ht,
        taux_tva=0.20,
        montant_tva_mad=montant_tva,
        montant_ttc_mad=montant_total,
        statut="payee"
    )
