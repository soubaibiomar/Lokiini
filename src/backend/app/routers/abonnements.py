import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Utilisateur, Abonnement
from app.routers.auth import get_current_user
from app.schemas.schemas import PlanResponse

router = APIRouter(tags=["Abonnements & Tarifs"])

PLANS_DISPONIBLES = [
    {
        "id": "gratuit",
        "nom": "Gratuit (Découverte)",
        "prix_mad": 0.0,
        "taux_commission": 15.0,
        "fonctionnalites": [
            "15% de commission par transaction",
            "Paiement Cash à la livraison (COD)",
            "États des lieux photo/vidéo scellés",
            "Support standard par email"
        ]
    },
    {
        "id": "premium",
        "nom": "Premium Particulier",
        "prix_mad": 49.0,
        "taux_commission": 10.0,
        "fonctionnalites": [
            "10% de commission réduite",
            "Option de livraison express partenaire",
            "Vérification KYC Didit prioritaire",
            "Badge de confiance VIP sur le profil"
        ]
    },
    {
        "id": "pro",
        "nom": "Pro BTP & Événementiel",
        "prix_mad": 299.0,
        "taux_commission": 7.0,
        "fonctionnalites": [
            "7% de commission super-réduite",
            "Multi-chantiers & gestion de flotte",
            "Facturation B2B automatisée avec ICE",
            "Support dédié WhatsApp 24/7"
        ]
    },
    {
        "id": "entreprise",
        "nom": "Entreprise / Grands Comptes",
        "prix_mad": 990.0,
        "taux_commission": 3.0,
        "fonctionnalites": [
            "3% à 5% de commission négociée",
            "Accès API & intégration ERP",
            "Gestionnaire de compte dédié",
            "Assurance dommages tous risques incluse"
        ]
    }
]

class UpgradeRequest(BaseModel):
    plan_id: str # 'gratuit', 'premium', 'pro', 'entreprise'

@router.get("/abonnements/plans", response_model=List[PlanResponse])
@router.get("/tarifs/plans", response_model=List[PlanResponse])
async def lister_plans():
    """Consulte la grille tarifaire complète des abonnements Lokiini."""
    return [PlanResponse(**p) for p in PLANS_DISPONIBLES]


@router.get("/abonnements/moi")
async def mon_abonnement(
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Consulte le plan d'abonnement actif de l'utilisateur."""
    plan_info = next((p for p in PLANS_DISPONIBLES if p["nom"].lower().startswith(current_user.plan_abonnement.lower())), PLANS_DISPONIBLES[0])

    return {
        "plan": current_user.plan_abonnement,
        "prix_mad": plan_info["prix_mad"],
        "taux_commission_pct": plan_info["taux_commission"],
        "valable_jusqu": current_user.abonnement_valable_jusqu,
        "fonctionnalites": plan_info["fonctionnalites"],
        "actif": True
    }


@router.post("/abonnements/upgrade")
async def passer_au_plan_superieur(
    payload: UpgradeRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mise à niveau instantanée de l'abonnement."""
    plan_cible = next((p for p in PLANS_DISPONIBLES if p["id"] == payload.plan_id.lower()), None)
    if not plan_cible:
        raise HTTPException(status_code=400, detail="Identifiant de plan invalide.")

    nom_simplifie = payload.plan_id.capitalize()
    if nom_simplifie == "Gratuit":
        current_user.plan_abonnement = "Gratuit"
        current_user.abonnement_valable_jusqu = None
    else:
        current_user.plan_abonnement = nom_simplifie
        current_user.abonnement_valable_jusqu = datetime.utcnow() + timedelta(days=30)

    # Enregistrer dans la table abonnements
    ab = Abonnement(
        utilisateur_id=current_user.id,
        plan=current_user.plan_abonnement,
        taux_commission=plan_cible["taux_commission"],
        prix_mad=plan_cible["prix_mad"],
        debute_le=datetime.utcnow(),
        expire_le=current_user.abonnement_valable_jusqu,
        statut="actif",
        fonctionnalites=plan_cible["fonctionnalites"]
    )
    db.add(ab)
    await db.commit()
    await db.refresh(current_user)

    return {
        "statut": "succes",
        "nouveau_plan": current_user.plan_abonnement,
        "taux_commission": plan_cible["taux_commission"],
        "valable_jusqu": current_user.abonnement_valable_jusqu,
        "message": f"Félicitations ! Vous êtes désormais sur le forfait {current_user.plan_abonnement}."
    }


@router.post("/abonnements/annuler")
async def annuler_abonnement(
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Annule le renouvellement de l'abonnement récurrent."""
    current_user.plan_abonnement = "Gratuit"
    current_user.abonnement_valable_jusqu = None
    await db.commit()
    return {"statut": "succes", "message": "Votre abonnement a été réinitialisé vers la formule Gratuite."}
