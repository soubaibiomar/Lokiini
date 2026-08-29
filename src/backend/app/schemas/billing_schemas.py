import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class SubscriptionPlanResponse(BaseModel):
    nom: str
    prix_mensuel_mad: float
    max_annonces: int
    commission_pct: float
    badge: Optional[str] = None
    facturation_ice: bool
    description: str

class MySubscriptionResponse(BaseModel):
    plan_actuel: str
    prix_mensuel_mad: float
    commission_pct: float
    max_annonces: int
    annonces_actives_count: int
    badge: Optional[str] = None
    renouvellement_le: Optional[datetime] = None

class SubscriptionUpgradeRequest(BaseModel):
    nouveau_plan: str # Gratuit, Premium, Pro, Entreprise

class EarningsDashboardResponse(BaseModel):
    periode: str # jour, semaine, mois, annee
    total_gains_bruts_mad: float
    total_commissions_plateforme_mad: float
    total_gains_nets_mad: float
    total_cautions_restituees_mad: float
    nombre_locations_terminees: int
    taux_occupation_pct: float
    top_articles_rentables: List[Dict[str, Any]]

class InvoiceResponse(BaseModel):
    numero_facture: str
    booking_id: uuid.UUID
    date_emission: datetime
    emetteur_societe: str
    emetteur_ice: str
    client_nom: str
    client_ice: Optional[str] = None
    montant_ht_mad: float
    taux_tva: float = 0.20
    montant_tva_mad: float
    montant_ttc_mad: float
    statut: str = "payee"
