import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.authorization import is_admin, require_resource_access
from app.core.database import get_db
from app.models.models import (
    DepositRecord, OwnerPayout, PlatformFeeRecord, RefundRecord,
    RentalPayment, Reservation, User,
)
from app.routers.auth import get_current_user
from app.schemas.payment_schemas import (
    BookingFinancialSummaryResponse, DepositResponse, FinancialRecordResponse,
    RefundResponse,
)
from app.services.payment_lifecycle import DepositStatus, OwnerPayoutStatus, RentalPaymentStatus


router = APIRouter(prefix="/payments", tags=["Payments & Deposits"])


async def _latest(db: AsyncSession, model, booking_id: uuid.UUID):
    result = await db.execute(
        select(model).where(model.booking_id == booking_id).order_by(model.created_at.desc()).limit(1)
    )
    return result.scalars().first()


async def _summary(db: AsyncSession, booking: Reservation, current_user: User):
    payment = await _latest(db, RentalPayment, booking.id)
    fee = await _latest(db, PlatformFeeRecord, booking.id)
    deposit = await _latest(db, DepositRecord, booking.id)
    payout = await _latest(db, OwnerPayout, booking.id)
    refund_result = await db.execute(
        select(RefundRecord).where(RefundRecord.booking_id == booking.id).order_by(RefundRecord.created_at.desc())
    )
    refunds = refund_result.scalars().all()

    rental_response = FinancialRecordResponse(
        status=payment.status if payment else RentalPaymentStatus.NOT_STARTED.value,
        amount_mad=float(payment.amount_mad if payment else booking.prix_total),
        currency=payment.currency if payment else "MAD",
        provider=payment.provider if payment else None,
        provider_transaction_id=payment.provider_transaction_id if payment else None,
        updated_at=payment.updated_at if payment else None,
    )
    fee_response = FinancialRecordResponse(
        status=fee.status if fee else "not_ready",
        amount_mad=float(fee.amount_mad if fee else booking.platform_commission_mad),
        currency=fee.currency if fee else "MAD",
        updated_at=fee.updated_at if fee else None,
    )
    deposit_response = DepositResponse(
        status=deposit.status if deposit else DepositStatus.NOT_STARTED.value,
        authorized_amount_mad=float(deposit.authorized_amount_mad if deposit else booking.montant_caution),
        captured_amount_mad=float(deposit.captured_amount_mad if deposit else 0),
        released_amount_mad=float(deposit.released_amount_mad if deposit else 0),
        currency=deposit.currency if deposit else "MAD",
        provider=deposit.provider if deposit else None,
        provider_transaction_id=deposit.provider_transaction_id if deposit else None,
        updated_at=deposit.updated_at if deposit else None,
    )
    payout_response = None
    if payout and (current_user.id == booking.loueur_id or is_admin(current_user)):
        payout_response = FinancialRecordResponse(
            status=payout.status,
            amount_mad=float(payout.payout_amount_mad), currency=payout.currency,
            provider=payout.provider, provider_transaction_id=payout.provider_transaction_id,
            updated_at=payout.updated_at,
        )
    elif current_user.id == booking.loueur_id or is_admin(current_user):
        payout_response = FinancialRecordResponse(
            status=OwnerPayoutStatus.NOT_READY.value,
            amount_mad=float(booking.prix_total) - float(booking.platform_commission_mad),
        )

    return BookingFinancialSummaryResponse(
        booking_id=booking.id,
        rental_payment=rental_response,
        platform_fee=fee_response,
        deposit=deposit_response,
        refunds=[
            RefundResponse(
                id=item.id, status=item.status, amount_mad=float(item.amount_mad),
                currency=item.currency, provider=item.provider,
                provider_transaction_id=item.provider_transaction_id, updated_at=item.updated_at,
            ) for item in refunds
        ],
        owner_payout=payout_response,
    )


@router.get("", response_model=list[BookingFinancialSummaryResponse])
async def list_my_financial_summaries(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Reservation).where(
            (Reservation.locataire_id == current_user.id) | (Reservation.loueur_id == current_user.id)
        ).order_by(Reservation.cree_le.desc())
    )
    return [await _summary(db, booking, current_user) for booking in result.scalars().all()]


@router.get("/bookings/{booking_id}", response_model=BookingFinancialSummaryResponse)
async def get_booking_financial_summary(
    booking_id: uuid.UUID, current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Reservation).where(Reservation.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail={"code": "BOOKING_NOT_FOUND", "message": "Réservation introuvable."})
    require_resource_access(current_user, booking.locataire_id, booking.loueur_id)
    return await _summary(db, booking, current_user)


@router.post("/bookings/{booking_id}/initiate", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
async def initiate_payment(
    booking_id: uuid.UUID,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=16, max_length=128),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Reservation).where(Reservation.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail={"code": "BOOKING_NOT_FOUND", "message": "Réservation introuvable."})
    require_resource_access(current_user, booking.locataire_id)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "PAYMENT_PROVIDER_UNAVAILABLE",
            "message": "Aucun prestataire de paiement n'est actuellement activé.",
            "details": {"payment_status": RentalPaymentStatus.NOT_STARTED.value},
        },
    )
