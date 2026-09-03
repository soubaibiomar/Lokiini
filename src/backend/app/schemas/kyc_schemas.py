import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from app.services.kyc_lifecycle import KYCStatus


class KYCInitiateRequest(BaseModel):
    """The authenticated identity is the only allowed KYC subject."""

    model_config = ConfigDict(extra="forbid")


class KYCInitiateResponse(BaseModel):
    session_id: str
    session_token: str
    verification_url: str
    status: KYCStatus


class DiditWebhookPayload(BaseModel):
    """Only provider envelope fields required for the internal status update."""

    model_config = ConfigDict(extra="ignore")

    event_id: uuid.UUID
    webhook_type: Literal["status.updated"]
    timestamp: int
    session_id: str
    vendor_data: uuid.UUID
    status: str
    session_kind: Optional[str] = None


class KYCStatusResponse(BaseModel):
    user_id: uuid.UUID
    status: KYCStatus
    verified_at: Optional[datetime] = None
    session_id: Optional[str] = None
