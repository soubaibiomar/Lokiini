import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class FinancialRecordResponse(BaseModel):
    status: str
    amount_mad: float
    currency: str = "MAD"
    provider: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    updated_at: Optional[datetime] = None


class DepositResponse(BaseModel):
    status: str
    authorized_amount_mad: float
    captured_amount_mad: float
    released_amount_mad: float
    currency: str = "MAD"
    provider: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    updated_at: Optional[datetime] = None


class RefundResponse(FinancialRecordResponse):
    id: uuid.UUID


class BookingFinancialSummaryResponse(BaseModel):
    booking_id: uuid.UUID
    rental_payment: FinancialRecordResponse
    platform_fee: FinancialRecordResponse
    deposit: DepositResponse
    refunds: list[RefundResponse]
    owner_payout: Optional[FinancialRecordResponse] = None


class PaymentWebhookPayload(BaseModel):
    event_id: str = Field(min_length=1, max_length=150)
    event_type: Literal[
        "rental_payment.updated", "deposit.updated", "refund.updated", "owner_payout.updated"
    ]
    provider_transaction_id: str = Field(min_length=1, max_length=150)
    status: str = Field(min_length=1, max_length=30)
    amount_mad: Optional[float] = Field(default=None, ge=0)
    currency: str = Field(default="MAD", pattern="^[A-Z]{3}$")


class PaymentWebhookResponse(BaseModel):
    accepted: bool
    duplicate: bool = False
    matched: bool = True

