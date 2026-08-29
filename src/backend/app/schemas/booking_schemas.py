import uuid
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field

class PricingCalculationRequest(BaseModel):
    article_id: uuid.UUID
    date_debut: date
    date_fin: date

class PricingBreakdownResponse(BaseModel):
    nombre_jours: int
    prix_par_jour_base: float
    total_brut_sans_remise: float
    remise_pourcentage: int
    type_tarif_applique: str
    total_location_mad: float
    frais_service_plateforme_mad: float
    commission_pourcentage: int
    gains_net_loueur_mad: float
    montant_caution_mad: float
    total_a_payer_a_la_remise_mad: float

class BookingCreateRequest(BaseModel):
    article_id: uuid.UUID
    date_debut: date
    date_fin: date
    mode_paiement: Optional[str] = "cash_on_delivery" # cash_on_delivery, cmi
    mode_caution: Optional[str] = "cash"
    message_loueur: Optional[str] = None

class BookingStatusUpdateRequest(BaseModel):
    nouveau_statut: str # confirme_cod, en_cours, termine, annule, litige
    motif_annulation: Optional[str] = None
    notes_litige: Optional[str] = None

class BookingItemResponse(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    locataire_id: uuid.UUID
    loueur_id: uuid.UUID
    article_titre: str
    article_photos: List[str]
    date_debut: date
    date_fin: date
    nombre_jours: int
    prix_total: float
    montant_caution: float
    frais_service: float
    statut_reservation: str
    mode_paiement: str
    mode_caution: str
    cree_le: datetime

    class Config:
        from_attributes = True

class BookingDetailResponse(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    locataire_id: uuid.UUID
    loueur_id: uuid.UUID
    article: Dict[str, Any]
    locataire: Dict[str, Any]
    loueur: Dict[str, Any]
    date_debut: date
    date_fin: date
    nombre_jours: int
    prix_total: float
    montant_caution: float
    frais_service: float
    statut_reservation: str
    mode_paiement: str
    mode_caution: str
    bail_signe_le: Optional[datetime] = None
    cree_le: datetime
