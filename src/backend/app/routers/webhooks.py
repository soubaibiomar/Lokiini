from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import get_db
from app.models.models import (
    DepositRecord, Litige, OwnerPayout, PaymentWebhookEvent,
    PlatformFeeRecord, RefundRecord, RentalPayment, Reservation,
)
from app.schemas.payment_schemas import PaymentWebhookPayload, PaymentWebhookResponse
from app.services.payment_lifecycle import (
    DEPOSIT_TRANSITIONS, PAYOUT_TRANSITIONS, PAYMENT_TRANSITIONS, PLATFORM_FEE_TRANSITIONS,
    REFUND_TRANSITIONS,
    DepositStatus, FinancialTransitionError, OwnerPayoutStatus, RefundStatus,
    RentalPaymentStatus, PlatformFeeStatus, validate_deposit_capture, validate_transition,
)
from app.services.payment_webhook_service import WebhookAuthenticationError, payload_sha256, verify_webhook_signature
from app.services.booking_state_machine import BookingAction, BookingActor, booking_state_machine
from app.services.dispute_lifecycle import (
    DisputeAction, DisputeActor, DisputeStatus, DisputeTransitionError,
    expected_deposit_status, transition as transition_dispute,
)
from app.services.notification_service import NotificationEvent, notify


router = APIRouter(prefix="/webhooks", tags=["Payment provider webhooks"])
SUPPORTED_PAYMENT_PROVIDERS = {"cmi", "cashplus"}


def _webhook_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


async def _provider_record(db: AsyncSession, provider: str, payload: PaymentWebhookPayload):
    model = {
        "rental_payment.updated": RentalPayment,
        "deposit.updated": DepositRecord,
        "refund.updated": RefundRecord,
        "owner_payout.updated": OwnerPayout,
    }[payload.event_type]
    result = await db.execute(select(model).where(
        model.provider == provider,
        model.provider_transaction_id == payload.provider_transaction_id,
    ))
    return result.scalars().first()


def _apply_provider_transition(record, payload: PaymentWebhookPayload) -> None:
    try:
        if payload.event_type == "rental_payment.updated":
            current, target = RentalPaymentStatus(record.status), RentalPaymentStatus(payload.status)
            validate_transition(current, target, PAYMENT_TRANSITIONS, "rental payment")
            if payload.amount_mad is not None and round(float(record.amount_mad), 2) != round(payload.amount_mad, 2):
                raise FinancialTransitionError("Rental payment amount does not match the expected amount")
        elif payload.event_type == "deposit.updated":
            current, target = DepositStatus(record.status), DepositStatus(payload.status)
            validate_transition(current, target, DEPOSIT_TRANSITIONS, "deposit")
            if target in {DepositStatus.PARTIALLY_CAPTURED, DepositStatus.CAPTURED}:
                if payload.amount_mad is None:
                    raise FinancialTransitionError("Deposit capture amount is required")
                validate_deposit_capture(record.authorized_amount_mad, payload.amount_mad, target)
                capture_amount = Decimal(str(payload.amount_mad))
                record.captured_amount_mad = capture_amount
            elif target == DepositStatus.RELEASED:
                record.released_amount_mad = record.authorized_amount_mad
        elif payload.event_type == "refund.updated":
            current, target = RefundStatus(record.status), RefundStatus(payload.status)
            validate_transition(current, target, REFUND_TRANSITIONS, "refund")
            if payload.amount_mad is not None and round(float(record.amount_mad), 2) != round(payload.amount_mad, 2):
                raise FinancialTransitionError("Refund amount does not match the requested amount")
        else:
            current, target = OwnerPayoutStatus(record.status), OwnerPayoutStatus(payload.status)
            validate_transition(current, target, PAYOUT_TRANSITIONS, "owner payout")
            if payload.amount_mad is not None and round(float(record.payout_amount_mad), 2) != round(payload.amount_mad, 2):
                raise FinancialTransitionError("Owner payout amount does not match the expected amount")
    except (ValueError, FinancialTransitionError) as exc:
        raise _webhook_error(status.HTTP_409_CONFLICT, "INVALID_FINANCIAL_TRANSITION", str(exc)) from exc
    record.status = target.value
    if hasattr(record, "provider_status"):
        record.provider_status = payload.status
    record.updated_at = datetime.utcnow()
    record.reconciled_at = datetime.utcnow()


async def _reconcile_related_records(db: AsyncSession, record, payload: PaymentWebhookPayload) -> None:
    if payload.event_type == "rental_payment.updated" and record.status == RentalPaymentStatus.SUCCEEDED.value:
        result = await db.execute(select(PlatformFeeRecord).where(
            PlatformFeeRecord.rental_payment_id == record.id,
        ).order_by(PlatformFeeRecord.created_at.desc()).limit(1))
        fee = result.scalars().first()
        if fee:
            current, target = PlatformFeeStatus(fee.status), PlatformFeeStatus.EARNED
            validate_transition(current, target, PLATFORM_FEE_TRANSITIONS, "platform fee")
            fee.status = target.value
            fee.updated_at = datetime.utcnow()

    if payload.event_type == "deposit.updated":
        dispute_result = await db.execute(select(Litige).where(
            Litige.reservation_id == record.booking_id,
            Litige.statut == DisputeStatus.DECISION.value,
            Litige.deposit_action_status == "pending_provider",
        ).order_by(Litige.decided_at.desc()).limit(1).with_for_update())
        dispute = dispute_result.scalars().first()
        if dispute:
            expected_status = expected_deposit_status(dispute.decision_code)
            if expected_status != record.status:
                raise _webhook_error(
                    409, "DISPUTE_DEPOSIT_OUTCOME_MISMATCH",
                    "Le statut confirmé par le prestataire ne correspond pas à la décision enregistrée.",
                )
            if expected_status in {DepositStatus.PARTIALLY_CAPTURED.value, DepositStatus.CAPTURED.value}:
                expected_amount = round(float(dispute.deposit_capture_amount_mad or 0), 2)
                actual_amount = round(float(record.captured_amount_mad or 0), 2)
                if expected_amount != actual_amount:
                    raise _webhook_error(
                        409, "DISPUTE_DEPOSIT_AMOUNT_MISMATCH",
                        "Le montant confirmé par le prestataire ne correspond pas à la décision enregistrée.",
                    )
            try:
                dispute.statut = transition_dispute(
                    dispute.statut, DisputeAction.CONFIRM_RESOLUTION, DisputeActor.SYSTEM,
                ).value
            except DisputeTransitionError as exc:
                raise _webhook_error(409, "DISPUTE_TRANSITION_INVALID", str(exc)) from exc
            dispute.deposit_action_status = "confirmed"
            dispute.resolu_le = datetime.utcnow()
            dispute.modifie_le = datetime.utcnow()
            booking_result = await db.execute(select(Reservation).where(
                Reservation.id == record.booking_id,
            ).with_for_update())
            booking = booking_result.scalars().first()
            if not booking:
                raise _webhook_error(409, "BOOKING_RECORD_MISSING", "La réservation liée au dossier est introuvable.")
            booking_state_machine.transition(booking, BookingAction.RESOLVE_DISPUTE, BookingActor.SYSTEM)
            for user_id in {dispute.renter_id, dispute.owner_id}:
                notify(
                    db,
                    recipient_id=user_id,
                    event_type=NotificationEvent.DISPUTE_UPDATED,
                    title="Traitement financier confirmé",
                    body="Le prestataire a confirmé le traitement du dépôt associé au dossier.",
                    dispute_id=dispute.id,
                )

    if payload.event_type != "refund.updated" or record.status != RefundStatus.SUCCEEDED.value:
        return
    payment_result = await db.execute(select(RentalPayment).where(RentalPayment.id == record.rental_payment_id))
    payment = payment_result.scalars().first()
    if not payment:
        raise _webhook_error(409, "PAYMENT_RECORD_MISSING", "Le paiement lié au remboursement est introuvable.")
    refunds_result = await db.execute(select(RefundRecord).where(
        RefundRecord.rental_payment_id == payment.id,
        RefundRecord.status == RefundStatus.SUCCEEDED.value,
    ))
    refunded_amount = sum(float(item.amount_mad) for item in refunds_result.scalars().all())
    payment_amount = float(payment.amount_mad)
    if refunded_amount > payment_amount:
        raise _webhook_error(409, "REFUND_EXCEEDS_PAYMENT", "Le cumul des remboursements dépasse le paiement.")
    target = (
        RentalPaymentStatus.REFUNDED
        if round(refunded_amount, 2) == round(payment_amount, 2)
        else RentalPaymentStatus.PARTIALLY_REFUNDED
    )
    validate_transition(RentalPaymentStatus(payment.status), target, PAYMENT_TRANSITIONS, "rental payment")
    payment.status = target.value
    payment.updated_at = datetime.utcnow()
    if target == RentalPaymentStatus.REFUNDED:
        fee_result = await db.execute(select(PlatformFeeRecord).where(
            PlatformFeeRecord.rental_payment_id == payment.id,
        ).order_by(PlatformFeeRecord.created_at.desc()).limit(1))
        fee = fee_result.scalars().first()
        if fee:
            validate_transition(
                PlatformFeeStatus(fee.status), PlatformFeeStatus.REVERSED,
                PLATFORM_FEE_TRANSITIONS, "platform fee",
            )
            fee.status = PlatformFeeStatus.REVERSED.value
            fee.updated_at = datetime.utcnow()


async def _notify_financial_event(db: AsyncSession, record, payload: PaymentWebhookPayload) -> None:
    if payload.event_type == "owner_payout.updated":
        notify(
            db,
            recipient_id=record.owner_id,
            event_type=NotificationEvent.PAYOUT_UPDATED,
            title="Statut du versement mis à jour",
            body=f"Le versement propriétaire est maintenant au statut {record.status}.",
            payout_id=record.id,
            booking_id=record.booking_id,
        )
        return

    booking_result = await db.execute(select(Reservation).where(Reservation.id == record.booking_id))
    booking = booking_result.scalars().first()
    if not booking:
        raise _webhook_error(409, "BOOKING_RECORD_MISSING", "La réservation liée au mouvement financier est introuvable.")

    if payload.event_type == "deposit.updated":
        event_type = NotificationEvent.DEPOSIT_UPDATED
        title = "Statut du dépôt mis à jour"
        body = f"Le dépôt de garantie est maintenant au statut {record.status}."
    elif payload.event_type == "refund.updated":
        event_type = NotificationEvent.PAYMENT_UPDATED
        title = "Statut du remboursement mis à jour"
        body = f"Le remboursement est maintenant au statut {record.status}."
    else:
        event_type = NotificationEvent.PAYMENT_UPDATED
        title = "Statut du paiement mis à jour"
        body = f"Le paiement de la location est maintenant au statut {record.status}."

    for user_id in {booking.locataire_id, booking.loueur_id}:
        notify(
            db,
            recipient_id=user_id,
            event_type=event_type,
            title=title,
            body=body,
            booking_id=booking.id,
        )


@router.post("/payments/{provider}", response_model=PaymentWebhookResponse)
async def payment_provider_webhook(
    provider: str, request: Request,
    x_webhook_timestamp: str | None = Header(None, alias="X-Webhook-Timestamp"),
    x_webhook_signature: str | None = Header(None, alias="X-Webhook-Signature"),
    x_webhook_event_id: str | None = Header(None, alias="X-Webhook-Event-ID"),
    db: AsyncSession = Depends(get_db),
):
    if provider not in SUPPORTED_PAYMENT_PROVIDERS:
        raise _webhook_error(404, "PAYMENT_PROVIDER_UNKNOWN", "Prestataire de paiement inconnu.")
    body = await request.body()
    try:
        verify_webhook_signature(
            secret=settings.PAYMENT_WEBHOOK_SECRET, timestamp=x_webhook_timestamp,
            signature=x_webhook_signature, body=body,
            tolerance_seconds=settings.PAYMENT_WEBHOOK_TOLERANCE_SECONDS,
        )
    except WebhookAuthenticationError as exc:
        raise _webhook_error(401, "INVALID_WEBHOOK_SIGNATURE", "Signature du webhook invalide.") from exc
    try:
        payload = PaymentWebhookPayload.model_validate_json(body)
    except ValidationError as exc:
        raise _webhook_error(422, "INVALID_WEBHOOK_PAYLOAD", "Charge utile du webhook invalide.") from exc
    if not x_webhook_event_id or x_webhook_event_id != payload.event_id:
        raise _webhook_error(400, "WEBHOOK_EVENT_ID_MISMATCH", "L'identifiant d'événement est absent ou incohérent.")

    seen = await db.execute(select(PaymentWebhookEvent).where(
        PaymentWebhookEvent.provider == provider,
        PaymentWebhookEvent.provider_event_id == payload.event_id,
    ))
    if seen.scalars().first():
        return PaymentWebhookResponse(accepted=True, duplicate=True)

    event = PaymentWebhookEvent(
        provider=provider, provider_event_id=payload.event_id, event_type=payload.event_type,
        provider_transaction_id=payload.provider_transaction_id,
        payload_sha256=payload_sha256(body), processing_status="received",
    )
    db.add(event)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        return PaymentWebhookResponse(accepted=True, duplicate=True)
    record = await _provider_record(db, provider, payload)
    if not record:
        event.processing_status = "unmatched"
        event.processed_at = datetime.utcnow()
        await db.commit()
        return PaymentWebhookResponse(accepted=True, matched=False)
    try:
        _apply_provider_transition(record, payload)
        await _reconcile_related_records(db, record, payload)
        await _notify_financial_event(db, record, payload)
    except (HTTPException, FinancialTransitionError, ValueError) as exc:
        await db.rollback()
        db.add(PaymentWebhookEvent(
            provider=provider, provider_event_id=payload.event_id, event_type=payload.event_type,
            provider_transaction_id=payload.provider_transaction_id,
            payload_sha256=payload_sha256(body), processing_status="rejected",
            processed_at=datetime.utcnow(),
        ))
        await db.commit()
        if isinstance(exc, HTTPException):
            raise
        raise _webhook_error(409, "INVALID_FINANCIAL_TRANSITION", str(exc)) from exc
    event.processing_status = "processed"
    event.processed_at = datetime.utcnow()
    await db.commit()
    return PaymentWebhookResponse(accepted=True)


@router.post("/cmi/callback", include_in_schema=False)
@router.post("/cashplus/deposit", include_in_schema=False)
async def disabled_unsigned_payment_callback():
    raise _webhook_error(
        status.HTTP_503_SERVICE_UNAVAILABLE, "PAYMENT_PROVIDER_UNAVAILABLE",
        "Ce callback non signé est désactivé.",
    )
