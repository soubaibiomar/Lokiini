import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

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

class InspectionSealResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    type: str # check_in, check_out, retrait, retour
    sha256_seal: str
    rfc3161_timestamp: datetime
    photos_count: int
    notes: Optional[str] = None
    statut_reservation_suivant: str
    message: str

class CashReceiptResponse(BaseModel):
    receipt_id: str
    booking_id: uuid.UUID
    montant_loyer_mad: float
    montant_caution_mad: float
    date_emission: datetime
    emetteur_nom: str
    receveur_nom: str
    statut: str = "valide"
