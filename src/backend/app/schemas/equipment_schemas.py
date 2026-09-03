import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class EquipmentCreateRequest(BaseModel):
    titre: str = Field(..., min_length=3, max_length=255)
    description: str
    categorie: str
    prix_par_jour: float = Field(..., gt=0)
    montant_caution: float = Field(..., ge=0)
    photos: List[str] = Field(default_factory=list, max_length=8)
    specs: Dict[str, Any] = Field(default_factory=dict)
    lat: Optional[float] = None
    lng: Optional[float] = None
    city: Optional[str] = "Casablanca"
    adresse_approximative: Optional[str] = None
    is_available: bool = True
    calendrier_disponibilite: Dict[str, Any] = Field(default_factory=dict)

class EquipmentUpdateRequest(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    categorie: Optional[str] = None
    prix_par_jour: Optional[float] = None
    montant_caution: Optional[float] = None
    photos: Optional[List[str]] = None
    specs: Optional[Dict[str, Any]] = None
    statut: Optional[str] = None # actif, indisponible, archive
    city: Optional[str] = None
    adresse_approximative: Optional[str] = None
    is_available: Optional[bool] = None
    calendrier_disponibilite: Optional[Dict[str, Any]] = None

class EquipmentResponse(BaseModel):
    id: uuid.UUID
    loueur_id: uuid.UUID
    titre: str
    description: str
    categorie: str
    prix_par_jour: float
    prix_par_semaine: Optional[float] = None
    prix_par_mois: Optional[float] = None
    montant_caution: float
    mode_caution: str
    niveau_risque: str
    kyc_requis: bool
    photos: List[str]
    specs: Dict[str, Any]
    city: str
    adresse_approximative: Optional[str] = None
    statut: str
    distance_km: Optional[float] = None
    loueur_nom: Optional[str] = None
    loueur_note: Optional[float] = 5.0
    loueur_statut_kyc: Optional[str] = "not_started"
    cree_le: datetime

    class Config:
        from_attributes = True

class CategoryCountResponse(BaseModel):
    categorie: str
    nom_affiche: str
    icone: str
    total_articles: int
