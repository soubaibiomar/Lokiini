import uuid
from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ContractSignRequest(BaseModel):
    consentement_explicite: bool = Field(..., description="Le signataire confirme avoir lu et accepté le contrat.")
    signature_data_base64: Optional[str] = None
    ip_address: Optional[str] = None


class ContractPartyResponse(BaseModel):
    user_id: uuid.UUID
    name: str
    city: Optional[str] = None
    company_name: Optional[str] = None
    company_ice: Optional[str] = None


class ContractEquipmentResponse(BaseModel):
    article_id: uuid.UUID
    title: str
    category: str
    description: str


class ContractResponse(BaseModel):
    booking_id: uuid.UUID
    booking_status: str
    contract_number: str
    contract_text: str
    contract_text_ar: Optional[str] = None
    contract_sha256: str
    applicable_law: str
    language: Literal["fr", "ar"] = "fr"
    available_languages: List[Literal["fr", "ar"]] = Field(default_factory=lambda: ["fr"])
    owner: ContractPartyResponse
    renter: ContractPartyResponse
    equipment: ContractEquipmentResponse
    start_date: date
    end_date: date
    number_of_days: int
    rental_price_mad: float
    deposit_amount_mad: float
    payment_method: str
    deposit_method: str
    responsibilities: List[str]
    important_conditions: List[str]
    signature_available: bool = False
    owner_signature_status: Literal["unavailable", "pending", "signed"] = "unavailable"
    renter_signature_status: Literal["unavailable", "pending", "signed"] = "unavailable"
    completed: bool = False
    document_url: Optional[str] = None
    est_signe_locataire: bool = False
    est_signe_loueur: bool = False
    signe_le: Optional[datetime] = None
    genere_le: datetime
