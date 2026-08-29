import uuid
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, EmailStr, Field

T = TypeVar("T")

# ==============================================================================
# STANDARD ENVELOPE RESPONSES
# ==============================================================================
class MetaData(BaseModel):
    page: Optional[int] = None
    limite: Optional[int] = None
    total_count: Optional[int] = None

class StandardResponse(BaseModel, Generic[T]):
    statut: str = "succes"
    donnees: Optional[T] = None
    meta: Optional[MetaData] = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class StandardErrorResponse(BaseModel):
    statut: str = "erreur"
    erreur: ErrorDetail

# ==============================================================================
# AUTH & USER SCHEMAS
# ==============================================================================
class UserBase(BaseModel):
    full_name: str
    email: str
    phone_number: str
    city: Optional[str] = "Casablanca"
    user_role: Optional[str] = "renter"
    company_name: Optional[str] = None
    company_ice: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    company_name: Optional[str] = None
    company_ice: Optional[str] = None
    user_role: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: uuid.UUID
    is_kyc_verified: bool = False
    kyc_liveness_score: float = 0.0
    avatar_url: Optional[str] = None
    note: float = 5.0
    temps_reponse_minutes: int = 30
    plan_abonnement: str = "Gratuit"
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserResponse] = None

# ==============================================================================
# KYC & DIDIT SCHEMAS
# ==============================================================================
class KYCSubmissionRequest(BaseModel):
    cin_number: str
    document_front_base64: Optional[str] = None
    document_back_base64: Optional[str] = None
    live_selfie_base64: Optional[str] = None

class KYCSubmissionResponse(BaseModel):
    is_verified: bool
    liveness_score: float
    message: str
    audit_proof_cndp: str

class KYCSessionResponse(BaseModel):
    session_id: str
    didit_session_token: str
    verification_url: str
    status: str = "initiated"

class KYCStatusResponse(BaseModel):
    user_id: uuid.UUID
    statut_verification: str
    kyc_liveness_score: float
    verifie_le: Optional[datetime] = None

# ==============================================================================
# EQUIPMENT / ARTICLE SCHEMAS
# ==============================================================================
class EquipmentBase(BaseModel):
    title: str
    description: str
    category: str
    city: str
    address: Optional[str] = None
    daily_price_mad: float
    deposit_amount_mad: float
    niveau_risque: Optional[str] = "faible"
    is_available: Optional[bool] = True
    discount_pct: Optional[int] = 0
    specs_json: Optional[Dict[str, Any]] = {}
    images_urls: Optional[List[str]] = []

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    daily_price_mad: Optional[float] = None
    deposit_amount_mad: Optional[float] = None
    niveau_risque: Optional[str] = None
    is_available: Optional[bool] = None
    discount_pct: Optional[int] = None
    specs_json: Optional[Dict[str, Any]] = None
    images_urls: Optional[List[str]] = None
    statut: Optional[str] = None

class EquipmentResponse(EquipmentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    is_verified: bool = True
    statut: str = "actif"
    nb_vues: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# ==============================================================================
# PRICING & BOOKING SCHEMAS
# ==============================================================================
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
    deposit_hold_mad: float # Caution cash
    currency: str = "MAD"

class BookingCreateRequest(BaseModel):
    equipment_id: uuid.UUID
    start_date: date
    end_date: date
    renter_id: Optional[uuid.UUID] = None
    option_livraison: Optional[str] = "retrait_sur_place" # retrait_sur_place, livraison_premium
    adresse_retrait: Optional[str] = None
    payment_method: Optional[str] = "cash_cod" # cash_cod, cmi_card, cashplus

class BookingStatusUpdateRequest(BaseModel):
    status: str

class BookingResponse(BaseModel):
    id: uuid.UUID
    equipment_id: uuid.UUID
    renter_id: uuid.UUID
    loueur_id: Optional[uuid.UUID] = None
    start_date: date
    end_date: date
    total_days: int
    daily_rate_applied_mad: Optional[float] = None
    rental_total_mad: float
    platform_commission_mad: float
    deposit_hold_mad: float
    option_livraison: Optional[str] = "retrait_sur_place"
    payment_method: Optional[str] = "cash_cod"
    booking_status: str
    cmi_status: Optional[str] = "pending_cod"
    cmi_auth_token: Optional[str] = None
    cmi_trans_id: Optional[str] = None
    contract_pdf_url: Optional[str] = None
    contract_sha256: Optional[str] = None
    contract_signe: Optional[bool] = False
    equipment_title: Optional[str] = None
    equipment_city: Optional[str] = None
    equipment_image: Optional[str] = None
    renter_name: Optional[str] = None
    owner_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==============================================================================
# HANDOFF / INSPECTION & CASH CONFIRMATION SCHEMAS
# ==============================================================================
class HandoffSubmissionRequest(BaseModel):
    booking_id: uuid.UUID
    type: str # retrait, retour, check_in, check_out
    video_url: Optional[str] = "https://lokiini.ma/videos/inspection_sample.mp4"
    photos: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    notes: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    signed_by_owner: Optional[bool] = True
    signed_by_renter: Optional[bool] = True

# Alias
InspectionCreateRequest = HandoffSubmissionRequest

class InspectionResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    type: str
    video_url: Optional[str] = None
    video_sha256_hash: Optional[str] = None
    rfc3161_timestamp: Optional[datetime] = None
    signed_by_owner: Optional[bool] = False
    signed_by_renter: Optional[bool] = False
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CashConfirmationRequest(BaseModel):
    montant_recu: float
    notes: Optional[str] = None

class DisputeSubmissionRequest(BaseModel):
    motif: str
    description: str
    photos: Optional[List[str]] = []

# ==============================================================================
# MESSAGING & REVIEWS SCHEMAS
# ==============================================================================
class MessageSendRequest(BaseModel):
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

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: uuid.UUID
    reservation_id: Optional[uuid.UUID] = None
    participant1_id: uuid.UUID
    participant2_id: uuid.UUID
    dernier_message_le: datetime
    dernier_message: Optional[str] = None
    non_lus_count: Optional[int] = 0

    class Config:
        from_attributes = True

class ReviewCreateRequest(BaseModel):
    booking_id: uuid.UUID
    target_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    reviewer_id: uuid.UUID
    target_id: uuid.UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==============================================================================
# ABONNEMENTS / PLANS SCHEMAS
# ==============================================================================
class PlanDetail(BaseModel):
    id: str
    nom: str
    prix_mad: float
    taux_commission: float
    fonctionnalites: List[str]

class UserAbonnementResponse(BaseModel):
    plan: str
    taux_commission: float
    prix_mad: float
    debute_le: Optional[datetime] = None
    expire_le: Optional[datetime] = None
    statut: str = "actif"
    fonctionnalites: List[str] = []
