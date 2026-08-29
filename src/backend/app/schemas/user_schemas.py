import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    telephone: str
    nom_complet: str
    avatar_url: Optional[str] = None
    statut_verification: str
    kyc_liveness_score: float
    note: float
    temps_reponse_minutes: int
    user_role: str
    company_name: Optional[str] = None
    company_ice: Optional[str] = None
    city: str
    plan_abonnement: str
    cree_le: datetime

    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    nom_complet: Optional[str] = None
    telephone: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    company_ice: Optional[str] = None
    city: Optional[str] = None

class PublicUserResponse(BaseModel):
    user_id: uuid.UUID
    nom: str
    note: float
    badge_verifie: bool
    date_inscription: datetime
    temps_reponse_minutes: int
    city: str
    total_annonces: Optional[int] = 0

class UserReviewSummary(BaseModel):
    id: uuid.UUID
    note: int
    commentaire: Optional[str] = None
    avisateur_nom: str
    cree_le: datetime

class UserEquipmentSummary(BaseModel):
    id: uuid.UUID
    titre: str
    categorie: str
    prix_par_jour: float
    montant_caution: float
    photos: List[str]
    statut: str
    city: str
