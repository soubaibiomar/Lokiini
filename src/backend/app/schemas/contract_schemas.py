import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ContractSignRequest(BaseModel):
    consentement_explicite: bool = Field(..., description="Le signataire certifie avoir lu et accepté les termes du bail DOC.")
    signature_data_base64: Optional[str] = None
    ip_address: Optional[str] = "127.0.0.1"

class ContractResponse(BaseModel):
    booking_id: uuid.UUID
    contract_number: str
    contract_text: str
    contract_sha256: str
    applicable_law: str
    est_signe_locataire: bool
    est_signe_loueur: bool
    signe_le: Optional[datetime] = None
    genere_le: datetime

class SignatureCertificateResponse(BaseModel):
    certificate_id: str
    contract_number: str
    booking_id: uuid.UUID
    contract_sha256: str
    signataire_locataire: str
    signataire_loueur: str
    date_scellement: datetime
    conforme_loi_53_05: bool = True
    autorite_certification: str = "Lokiini Digital Trust Engine MAROC"
