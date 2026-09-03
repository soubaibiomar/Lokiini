import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


DisputeReason = Literal[
    "equipment_condition", "missing_accessory", "late_return",
    "handover_problem", "payment_issue", "cancellation", "other",
]
DisputeDecisionCode = Literal[
    "no_financial_adjustment", "release_deposit",
    "partial_deposit_capture", "full_deposit_capture",
]


class DisputeCreateRequest(BaseModel):
    booking_id: uuid.UUID
    reason_code: DisputeReason
    description: str = Field(min_length=20, max_length=5000)


class LegacyDisputeCreateRequest(BaseModel):
    motif: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=5000)
    photos: list[str] = Field(default_factory=list)


class DisputeEvidenceResponse(BaseModel):
    id: uuid.UUID
    dispute_id: uuid.UUID
    reservation_id: uuid.UUID
    equipment_id: uuid.UUID
    renter_id: uuid.UUID
    owner_id: uuid.UUID
    uploaded_by_id: uuid.UUID
    media_kind: Literal["photo", "video", "document"]
    original_filename: str
    content_type: str
    size_bytes: int
    sha256_hash: str
    stored_at: datetime
    file_url: str


class DisputeResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    equipment_id: uuid.UUID
    renter_id: uuid.UUID
    owner_id: uuid.UUID
    submitted_by_id: uuid.UUID
    reason_code: str
    description: str
    status: str
    decision_code: Optional[str] = None
    deposit_capture_amount_mad: Optional[float] = None
    deposit_action_status: Optional[str] = None
    decision_summary: Optional[str] = None
    evidence_submitted_by_renter: bool
    evidence_submitted_by_owner: bool
    renter_submitted_at: Optional[datetime] = None
    owner_submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    decided_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    evidence: list[DisputeEvidenceResponse] = Field(default_factory=list)


class DisputeDecisionRequest(BaseModel):
    decision_code: DisputeDecisionCode
    decision_summary: str = Field(min_length=20, max_length=5000)
    deposit_capture_amount_mad: Optional[float] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_capture_amount(self):
        partial = self.decision_code == "partial_deposit_capture"
        if partial and self.deposit_capture_amount_mad is None:
            raise ValueError("A partial deposit capture requires an amount")
        if not partial and self.deposit_capture_amount_mad is not None:
            raise ValueError("A capture amount is accepted only for a partial deposit capture")
        return self


class DisputeInspectionEvidenceContext(BaseModel):
    id: uuid.UUID
    media_kind: str
    original_filename: str
    sha256_hash: str
    stored_at: datetime
    file_url: str


class DisputeInspectionContext(BaseModel):
    id: uuid.UUID
    inspection_type: str
    condition: Optional[str] = None
    existing_damage: Optional[str] = None
    accessories: list[str] = Field(default_factory=list)
    serial_number: Optional[str] = None
    meter_type: Optional[str] = None
    meter_reading: Optional[float] = None
    notes: Optional[str] = None
    status: str
    recorded_at: datetime
    evidence: list[DisputeInspectionEvidenceContext] = Field(default_factory=list)


class DisputeMessageContext(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    created_at: datetime


class DisputeContextResponse(BaseModel):
    inspections: list[DisputeInspectionContext]
    messages: list[DisputeMessageContext]
