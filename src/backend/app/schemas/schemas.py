import uuid
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    city: Optional[str] = "Casablanca"
    user_role: Optional[str] = "renter"
    company_name: Optional[str] = None
    company_ice: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_kyc_verified: bool
    kyc_liveness_score: float
    created_at: datetime

    class Config:
        from_attributes = True

# Equipment Schemas
class EquipmentBase(BaseModel):
    title: str
    description: str
    category: str
    city: str
    address: Optional[str] = None
    daily_price_mad: float
    deposit_amount_mad: float
    is_available: Optional[bool] = True
    discount_pct: Optional[int] = 0
    specs_json: Optional[Dict[str, Any]] = {}
    images_urls: Optional[List[str]] = []

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentResponse(EquipmentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Booking & Pricing Calculation Schemas
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
    deposit_hold_mad: float # Caution bloquée sans débit
    currency: str = "MAD"

class BookingCreateRequest(BaseModel):
    equipment_id: uuid.UUID
    start_date: date
    end_date: date
    renter_id: Optional[uuid.UUID] = None
    payment_method: Optional[str] = "cmi_card" # cmi_card or cashplus

class BookingResponse(BaseModel):
    id: uuid.UUID
    equipment_id: uuid.UUID
    renter_id: uuid.UUID
    start_date: date
    end_date: date
    total_days: int
    daily_rate_applied_mad: Optional[float] = None
    rental_total_mad: float
    platform_commission_mad: float
    deposit_hold_mad: float
    booking_status: str
    cmi_status: str
    cmi_auth_token: Optional[str] = None
    cmi_trans_id: Optional[str] = None
    contract_pdf_url: Optional[str] = None
    contract_sha256: Optional[str] = None
    equipment_title: Optional[str] = None
    equipment_city: Optional[str] = None
    equipment_image: Optional[str] = None
    renter_name: Optional[str] = None
    owner_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BookingStatusUpdateRequest(BaseModel):
    booking_status: Optional[str] = None # confirmed, in_progress, completed, cancelled, disputed
    cmi_status: Optional[str] = None # held, released, captured

# KYC Verification Schemas
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

# Inspection Report Schema
class InspectionCreateRequest(BaseModel):
    booking_id: uuid.UUID
    type: str # check_in or check_out
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

# Auth Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
