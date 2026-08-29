import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class KYCInitiateRequest(BaseModel):
    user_id: Optional[uuid.UUID] = None

class KYCInitiateResponse(BaseModel):
    session_id: str
    didit_session_token: str
    verification_url: str
    status: str = "initiated"

class KYCDocumentRequest(BaseModel):
    session_id: str
    image_document_base64: str
    type_document: Optional[str] = "cni" # cni, passeport, sejour

class KYCSelfieRequest(BaseModel):
    session_id: str
    image_selfie_base64: str

class KYCVerificationResult(BaseModel):
    statut: str # en_attente, approuve, rejete, revision_manuelle
    liveness_score: float
    message: str
    session_id: str
    audit_proof_cndp: Optional[str] = None

class KYCWebhookPayload(BaseModel):
    event: str # session.completed, session.approved, session.rejected, session.requires_review
    session_id: str
    vendor_data: str # user_id
    status: str # approved, rejected, requires_review
    liveness_score: Optional[float] = 98.50
    document_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class KYCStatusResponse(BaseModel):
    user_id: uuid.UUID
    statut_verification: str
    kyc_liveness_score: float
    verifie_le: Optional[datetime] = None
    didit_session_id: Optional[str] = None
