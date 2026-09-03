import uuid
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class InspectionRequirementsResponse(BaseModel):
    booking_id: uuid.UUID
    inspection_type: Literal["check_in", "check_out"]
    minimum_photos: int = 3
    video_required: bool
    photo_max_bytes: int
    video_max_bytes: int
    allowed_booking_statuses: List[str]


class InspectionEvidenceResponse(BaseModel):
    id: uuid.UUID
    reservation_id: uuid.UUID
    equipment_id: uuid.UUID
    renter_id: uuid.UUID
    owner_id: uuid.UUID
    uploaded_by_id: uuid.UUID
    inspection_type: Literal["check_in", "check_out"]
    media_kind: Literal["photo", "video"]
    original_filename: str
    content_type: str
    size_bytes: int
    sha256_hash: str
    stored_at: datetime
    file_url: str


class StructuredInspectionCreateRequest(BaseModel):
    booking_id: uuid.UUID
    inspection_type: Literal["check_in", "check_out"]
    evidence_ids: List[uuid.UUID] = Field(..., min_length=3, max_length=11)
    condition: Literal["excellent", "good", "fair", "damaged"]
    existing_damage: Optional[str] = Field(default=None, max_length=3000)
    accessories: List[str] = Field(default_factory=list, max_length=30)
    serial_number: Optional[str] = Field(default=None, max_length=150)
    meter_type: Literal["none", "odometer", "hours"] = "none"
    meter_reading: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=3000)
    confirmed: bool

    @model_validator(mode="after")
    def validate_meter_and_confirmation(self):
        if self.meter_type == "none" and self.meter_reading is not None:
            raise ValueError("meter_reading requires odometer or hours")
        if self.meter_type != "none" and self.meter_reading is None:
            raise ValueError("meter_reading is required for the selected meter type")
        if not self.confirmed:
            raise ValueError("Inspection confirmation is required")
        return self


class InspectionDetailResponse(BaseModel):
    id: uuid.UUID
    reservation_id: uuid.UUID
    equipment_id: uuid.UUID
    renter_id: uuid.UUID
    owner_id: uuid.UUID
    submitted_by_id: Optional[uuid.UUID] = None
    inspection_type: str
    condition: Optional[str] = None
    existing_damage: Optional[str] = None
    accessories: List[str] = Field(default_factory=list)
    serial_number: Optional[str] = None
    meter_type: Optional[str] = None
    meter_reading: Optional[float] = None
    notes: Optional[str] = None
    status: str
    confirmed_by_owner: bool
    confirmed_by_renter: bool
    recorded_at: datetime
    confirmed_at: Optional[datetime] = None
    evidence: List[InspectionEvidenceResponse] = Field(default_factory=list)

class CheckInSubmissionRequest(BaseModel):
    booking_id: uuid.UUID
    photos: List[str] = Field(..., min_length=1, description="Au moins 1 photo multi-angles")
    video_url: Optional[str] = None
    notes: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    montant_cash_loyer_recu: float = Field(..., ge=0)
    montant_caution_recue: float = Field(..., ge=0)

class CheckOutSubmissionRequest(BaseModel):
    booking_id: uuid.UUID
    photos: List[str] = Field(..., min_length=1)
    video_url: Optional[str] = None
    notes: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    montant_caution_restituee: float = Field(..., ge=0)
    montant_retenue_degradations: Optional[float] = 0.0

class HandoffSubmissionRequest(BaseModel):
    booking_id: uuid.UUID
    type: str
    video_url: Optional[str] = None
    photos: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    signed_by_owner: bool = False
    signed_by_renter: bool = False


InspectionCreateRequest = HandoffSubmissionRequest


class RemiseCreateRequest(BaseModel):
    photos: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    geolocalisation: Optional[Dict[str, Any]] = None
    signatures: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class RemiseResponse(BaseModel):
    id: uuid.UUID
    reservation_id: uuid.UUID
    type: str
    photos: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    geolocalisation: Optional[Dict[str, Any]] = None
    horodatage: Optional[datetime] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    cree_le: Optional[datetime] = None

    class Config:
        from_attributes = True


class CashConfirmationRequest(BaseModel):
    montant_recu: float = Field(..., ge=0)
    notes: Optional[str] = None
