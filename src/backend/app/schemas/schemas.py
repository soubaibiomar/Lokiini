import uuid
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# ==============================================================================
# 1. UTILISATEURS / AUTH & KYC
# ==============================================================================
class UserBase(BaseModel):
    email: EmailStr
    telephone: str
    nom_complet: str
    ville: Optional[str] = "Casablanca"
    role: Optional[str] = "particulier"
    company_name: Optional[str] = None
    company_ice: Optional[str] = None

class UserCreate(UserBase):
    mot_de_passe: str

class UserLogin(BaseModel):
    email_ou_telephone: str
    mot_de_passe: str

class UserResponse(UserBase):
    id: uuid.UUID
    avatar_url: Optional[str] = None
    statut_verification: str
    verifie_le: Optional[datetime] = None
    note: float
    date_inscription: datetime
    temps_reponse_minutes: int
    plan_abonnement: str
    abonnement_valable_jusqu: Optional[datetime] = None
    cree_le: datetime

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    nom_complet: Optional[str] = None
    telephone: Optional[str] = None
    avatar_url: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    company_name: Optional[str] = None
    company_ice: Optional[str] = None

class UserPublicProfile(BaseModel):
    id: uuid.UUID
    nom: str
    note: float
    badge_verifie: bool
    date_inscription: datetime
    temps_reponse: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserResponse

# KYC Didit Schemas
class KYCInitResponse(BaseModel):
    session_id: str
    didit_session_token: str
    message: str

class KYCDocumentRequest(BaseModel):
    session_id: str
    type_document: str = "cin" # 'cin' | 'passeport'
    image_document_base64: str

class KYCSelfieRequest(BaseModel):
    session_id: str
    image_selfie_base64: str

class KYCVerificationResult(BaseModel):
    statut: str # 'en_attente' | 'approuve' | 'rejete' | 'revision_manuelle'
    liveness_score: Optional[float] = None
    message: str


# ==============================================================================
# 2. ARTICLES / ANNONCES
# ==============================================================================
class ArticleBase(BaseModel):
    categorie: str # 'outils', 'electronique', 'musique', 'evenementiel', 'outdoor', 'velos', 'btp'
    titre: str
    description: str
    photos: Optional[List[str]] = []
    prix_par_jour: float
    montant_caution: Optional[float] = 0.00
    niveau_risque: Optional[str] = "faible" # 'faible', 'moyen', 'eleve'
    ville: Optional[str] = "Casablanca"
    adresse: Optional[str] = None
    localisation: Optional[Dict[str, float]] = {"lat": 33.5731, "lng": -7.5898}
    calendrier_disponibilite: Optional[Dict[str, Any]] = {"dates_bloquees": []}
    specs: Optional[Dict[str, Any]] = {}

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    prix_par_jour: Optional[float] = None
    montant_caution: Optional[float] = None
    statut: Optional[str] = None
    calendrier_disponibilite: Optional[Dict[str, Any]] = None
    specs: Optional[Dict[str, Any]] = None

class ArticleResponse(ArticleBase):
    id: uuid.UUID
    loueur_id: uuid.UUID
    statut: str
    nb_vues: int
    cree_le: datetime
    loueur: Optional[UserPublicProfile] = None

    class Config:
        from_attributes = True

class ArticleSearchQuery(BaseModel):
    q: Optional[str] = None
    categorie: Optional[str] = None
    prix_min: Optional[float] = None
    prix_max: Optional[float] = None
    ville: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    rayon_km: Optional[float] = 50.0
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    uniquement_verifies: Optional[bool] = False
    tri_par: Optional[str] = "plus_recent" # 'prix_asc', 'prix_desc', 'distance', 'note', 'plus_recent'
    page: int = 1
    limite: int = 12


# ==============================================================================
# 3. RÉSERVATIONS (Cash on Delivery / COD)
# ==============================================================================
class ReservationCreate(BaseModel):
    article_id: uuid.UUID
    date_debut: date
    date_fin: date
    option_livraison: Optional[str] = "retrait_sur_place" # 'retrait_sur_place' | 'livraison_premium'
    adresse_retrait: Optional[str] = None

class ReservationResponse(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    locataire_id: uuid.UUID
    loueur_id: uuid.UUID
    date_debut: date
    date_fin: date
    prix_total: float
    montant_caution: float
    option_livraison: str
    adresse_retrait: Optional[str] = None
    statut: str
    contrat_pdf_url: Optional[str] = None
    contrat_signe: bool
    contrat_signe_le: Optional[datetime] = None
    cree_le: datetime
    article_titre: Optional[str] = None
    article_photo: Optional[str] = None
    locataire_nom: Optional[str] = None
    loueur_nom: Optional[str] = None

    class Config:
        from_attributes = True

class ReservationStatusUpdate(BaseModel):
    statut: str # 'confirme_cod', 'en_cours', 'termine', 'annule'

class ContractSignRequest(BaseModel):
    signature_base64: str
    date_signature: Optional[datetime] = None


# ==============================================================================
# 4. ÉTATS DES LIEUX (REMISES) & CONFIRMATION CASH
# ==============================================================================
class RemiseCreateRequest(BaseModel):
    type: str # 'retrait' | 'retour'
    photos: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    geolocalisation: Optional[Dict[str, float]] = {}
    signatures: Optional[Dict[str, str]] = {} # {"locataire": "base64", "loueur": "base64"}
    notes: Optional[str] = None

class RemiseResponse(BaseModel):
    id: uuid.UUID
    reservation_id: uuid.UUID
    type: str
    photos: List[str]
    videos: List[str]
    geolocalisation: Dict[str, Any]
    horodatage: datetime
    statut: str
    notes: Optional[str] = None
    cree_le: datetime

    class Config:
        from_attributes = True

class CashConfirmationRequest(BaseModel):
    montant_recu: float
    notes: Optional[str] = None

class LitigeCreateRequest(BaseModel):
    motif: str
    description: str
    photos: Optional[List[str]] = []

class LitigeResponse(BaseModel):
    id: uuid.UUID
    reservation_id: uuid.UUID
    soumis_par: uuid.UUID
    motif: str
    description: str
    photos: List[str]
    statut: str
    notes_resolution: Optional[str] = None
    cree_le: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# 5. MESSAGERIE & NOTIFICATIONS
# ==============================================================================
class MessageCreate(BaseModel):
    conversation_id: Optional[uuid.UUID] = None
    reservation_id: Optional[uuid.UUID] = None
    destinataire_id: Optional[uuid.UUID] = None
    contenu: str

class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    expediteur_id: uuid.UUID
    contenu: str
    lu: bool
    cree_le: datetime

# Price Calculation Schemas
class PriceCalculationRequest(BaseModel):
    equipment_id: uuid.UUID
    start_date: date
    end_date: date

class PriceCalculationResponse(BaseModel):
    total_days: int
    daily_base_price_mad: float
    discount_percentage: int
    discounted_daily_rate_mad: float
    subtotal_rental_mad: float
    platform_commission_mad: float
    total_due_renter_mad: float
    deposit_hold_mad: float
    currency: str = "MAD"

# KYC Submission Schemas
class KYCSubmissionRequest(BaseModel):
    cin_number: str
    cin_front_base64: Optional[str] = None
    cin_back_base64: Optional[str] = None
    video_selfie_base64: Optional[str] = None

class KYCSubmissionResponse(BaseModel):
    is_verified: bool
    liveness_score: float
    message: str
    audit_proof_cndp: str

# Inspection Schemas
class InspectionCreateRequest(BaseModel):
    booking_id: uuid.UUID
    type: str
    video_url: str
    notes: Optional[str] = None

class InspectionResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    type: str
    video_url: str
    video_sha256_hash: str
    rfc3161_timestamp: datetime
    signed_by_owner: bool
    signed_by_renter: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Aliases for compatibility
UserBase = UserBase
EquipmentBase = ArticleBase
EquipmentCreate = ArticleCreate
EquipmentResponse = ArticleResponse
BookingCreateRequest = ReservationCreate
BookingResponse = ReservationResponse
BookingStatusUpdateRequest = ReservationStatusUpdate

class ConversationResponse(BaseModel):
    id: uuid.UUID
    reservation_id: Optional[uuid.UUID] = None
    dernier_message: Optional[str] = None
    non_lus_count: int = 0
    autre_participant: Optional[Dict[str, Any]] = None
    dernier_message_le: datetime

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    titre: str
    corps: str
    data: Dict[str, Any]
    lu: bool
    cree_le: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# 6. ABONNEMENTS & AVIS
# ==============================================================================
class PlanResponse(BaseModel):
    id: str
    nom: str
    prix_mad: float
    taux_commission: float
    fonctionnalites: List[str]

class ReviewCreate(BaseModel):
    reservation_id: uuid.UUID
    note: int = Field(..., ge=1, le=5)
    commentaire: Optional[str] = None

class ReviewResponse(BaseModel):
    id: uuid.UUID
    reservation_id: uuid.UUID
    avisateur_id: uuid.UUID
    avise_id: uuid.UUID
    note: int
    commentaire: Optional[str] = None
    nom_avisateur: Optional[str] = None
    cree_le: datetime

    class Config:
        from_attributes = True
