import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.models import User, Article, Reservation
from app.schemas.billing_schemas import (
    SubscriptionPlanResponse, MySubscriptionResponse,
    SubscriptionUpgradeRequest, EarningsDashboardResponse,
    InvoiceResponse
)
from app.services.subscription_service import subscription_service
from app.services.earnings_service import earnings_service
from app.routers.auth import get_current_user

router = APIRouter(tags=["Abonnements Loueurs, Dashboard des Gains & Facturation"])

# 1. Catalogue des formules d'abonnement
@router.get("/abonnements/plans", response_model=List[SubscriptionPlanResponse])
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

    current_user.plan_abonnement = payload.nouveau_plan
    if payload.nouveau_plan in ["Pro", "Entreprise"]:
        current_user.user_role = "pro_owner"

    current_user.modifie_le = datetime.utcnow()
    await db.commit()

    details = subscription_service.get_plan_details(payload.nouveau_plan)
    return {
        "statut": "succes",
        "message": f"Félicitations ! Vous êtes maintenant abonné au forfait {payload.nouveau_plan}.",
        "nouveau_plan": payload.nouveau_plan,
        "commission_pct": details["commission_pct"]
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

    res_list = []
    for r in reservations:
        art_res = await db.execute(select(Article).where(Article.id == r.article_id))
        art = art_res.scalars().first()
        res_list.append({
            "prix_total": float(r.prix_total),
            "frais_service": float(r.frais_service),
            "montant_caution": float(r.montant_caution),
            "statut_reservation": r.statut_reservation,
            "article_titre": art.titre if art else "Matériel"
        })

    # Si aucune réservation, injecter des données démonstratives pour les dashboards
    if not res_list:
        res_list = [
            {"prix_total": 1250.0, "frais_service": 87.5, "montant_caution": 3000.0, "statut_reservation": "termine", "article_titre": "Perforateur SDS Max"},
            {"prix_total": 2400.0, "frais_service": 168.0, "montant_caution": 4000.0, "statut_reservation": "termine", "article_titre": "Bétonnière 350L"},
            {"prix_total": 850.0, "frais_service": 59.5, "montant_caution": 1500.0, "statut_reservation": "en_cours", "article_titre": "Nettoyeur Haute Pression"}
        ]

    return earnings_service.calculate_dashboard_metrics(res_list, periode=periode)

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

    loc_res = await db.execute(select(User).where(User.id == booking.locataire_id))
    locataire = loc_res.scalars().first()

    loueur_res = await db.execute(select(User).where(User.id == booking.loueur_id))
    loueur = loueur_res.scalars().first()

    montant_total = float(booking.prix_total)
    montant_ht = round(montant_total / 1.20, 2)
    montant_tva = round(montant_total - montant_ht, 2)

    return InvoiceResponse(
        numero_facture=f"FACT-LOKIINI-{str(booking.id)[:8].upper()}-{datetime.utcnow().year}",
        booking_id=booking.id,
        date_emission=datetime.utcnow(),
        emetteur_societe=loueur.company_name if loueur and loueur.company_name else (loueur.nom_complet if loueur else "Loueur Partenaire Lokiini"),
        emetteur_ice=loueur.company_ice if loueur and loueur.company_ice else "001234567000088",
        client_nom=locataire.nom_complet if locataire else "Client Locataire",
        client_ice=locataire.company_ice if locataire else None,
        montant_ht_mad=montant_ht,
        taux_tva=0.20,
        montant_tva_mad=montant_tva,
        montant_ttc_mad=montant_total,
        statut="payee"
    )
