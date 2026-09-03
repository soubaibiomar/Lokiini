import uuid
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.main import app
from app.schemas.payment_schemas import PaymentWebhookPayload
from app.services.payment_lifecycle import (
    DEPOSIT_TRANSITIONS, PAYOUT_TRANSITIONS, PAYMENT_TRANSITIONS,
    PLATFORM_FEE_TRANSITIONS, REFUND_TRANSITIONS,
    DepositStatus, FinancialTransitionError, OwnerPayoutStatus, RentalPaymentStatus,
    PlatformFeeStatus, RefundStatus,
    validate_deposit_capture, validate_transition,
)
from app.services.payment_webhook_service import (
    WebhookAuthenticationError, sign_webhook, verify_webhook_signature,
)


BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("target", [
    DepositStatus.RELEASED, DepositStatus.PARTIALLY_CAPTURED, DepositStatus.CAPTURED,
])
def test_authorized_deposit_allows_only_explicit_terminal_branches(target):
    validate_transition(DepositStatus.AUTHORIZED, target, DEPOSIT_TRANSITIONS, "deposit")


@pytest.mark.parametrize("current,target", [
    (DepositStatus.RELEASED, DepositStatus.CAPTURED),
    (DepositStatus.CAPTURED, DepositStatus.RELEASED),
    (DepositStatus.NOT_STARTED, DepositStatus.AUTHORIZED),
])
def test_invalid_deposit_transitions_are_rejected(current, target):
    with pytest.raises(FinancialTransitionError):
        validate_transition(current, target, DEPOSIT_TRANSITIONS, "deposit")


def test_deposit_capture_amount_matches_partial_or_full_state():
    validate_deposit_capture(Decimal("5000"), Decimal("1200"), DepositStatus.PARTIALLY_CAPTURED)
    validate_deposit_capture(Decimal("5000"), Decimal("5000"), DepositStatus.CAPTURED)
    with pytest.raises(FinancialTransitionError):
        validate_deposit_capture(Decimal("5000"), Decimal("5001"), DepositStatus.CAPTURED)
    with pytest.raises(FinancialTransitionError):
        validate_deposit_capture(Decimal("5000"), Decimal("5000"), DepositStatus.PARTIALLY_CAPTURED)


def test_rental_payment_and_payout_transitions_are_independent():
    validate_transition(
        RentalPaymentStatus.PENDING, RentalPaymentStatus.SUCCEEDED,
        PAYMENT_TRANSITIONS, "rental payment",
    )
    validate_transition(
        OwnerPayoutStatus.NOT_READY, OwnerPayoutStatus.PENDING,
        PAYOUT_TRANSITIONS, "owner payout",
    )
    with pytest.raises(FinancialTransitionError):
        validate_transition(
            OwnerPayoutStatus.NOT_READY, OwnerPayoutStatus.PAID,
            PAYOUT_TRANSITIONS, "owner payout",
        )


def test_fee_and_refund_have_their_own_terminal_states():
    validate_transition(
        PlatformFeeStatus.PENDING, PlatformFeeStatus.EARNED,
        PLATFORM_FEE_TRANSITIONS, "platform fee",
    )
    validate_transition(
        PlatformFeeStatus.EARNED, PlatformFeeStatus.REVERSED,
        PLATFORM_FEE_TRANSITIONS, "platform fee",
    )
    validate_transition(
        RefundStatus.PENDING, RefundStatus.SUCCEEDED,
        REFUND_TRANSITIONS, "refund",
    )
    with pytest.raises(FinancialTransitionError):
        validate_transition(
            RefundStatus.SUCCEEDED, RefundStatus.FAILED,
            REFUND_TRANSITIONS, "refund",
        )


def test_signed_webhook_rejects_bad_signature_and_stale_timestamp():
    body = b'{"event_id":"evt-1"}'
    signature = sign_webhook("secret", "1000", body)
    verify_webhook_signature(
        secret="secret", timestamp="1000", signature=f"sha256={signature}",
        body=body, tolerance_seconds=300, now=1100,
    )
    with pytest.raises(WebhookAuthenticationError):
        verify_webhook_signature(
            secret="secret", timestamp="1000", signature="wrong",
            body=body, tolerance_seconds=300, now=1100,
        )
    with pytest.raises(WebhookAuthenticationError):
        verify_webhook_signature(
            secret="secret", timestamp="1000", signature=signature,
            body=body, tolerance_seconds=300, now=1400,
        )


def test_webhook_deposit_transition_updates_only_a_matching_backend_record():
    from app.routers.webhooks import _apply_provider_transition

    record = SimpleNamespace(
        status="authorized", authorized_amount_mad=Decimal("5000"),
        captured_amount_mad=Decimal("0"), released_amount_mad=Decimal("0"),
        provider_status=None, updated_at=None, reconciled_at=None,
    )
    payload = PaymentWebhookPayload(
        event_id="evt-2", event_type="deposit.updated",
        provider_transaction_id="provider-deposit-1",
        status="partially_captured", amount_mad=1200,
    )
    _apply_provider_transition(record, payload)
    assert record.status == "partially_captured"
    assert record.captured_amount_mad == 1200
    assert record.released_amount_mad == Decimal("0")


def test_payment_api_exposes_reads_but_no_client_status_mutation():
    paths = app.openapi()["paths"]
    assert "/api/v1/payments" in paths
    assert "/api/v1/payments/bookings/{booking_id}" in paths
    assert "/api/v1/webhooks/payments/{provider}" in paths
    payments_source = (BACKEND_DIR / "app/routers/payments.py").read_text(encoding="utf-8")
    assert "PAYMENT_PROVIDER_UNAVAILABLE" in payments_source
    assert "payment=true" not in payments_source


def test_payment_migration_is_additive_and_tracks_replay_ids():
    source = (BACKEND_DIR / "alembic/versions/20260901_04_payment_architecture.py").read_text(encoding="utf-8")
    for table in (
        "rental_payments", "platform_fee_records", "deposit_records",
        "refund_records", "owner_payouts", "payment_webhook_events",
    ):
        assert f'"{table}"' in source
    assert "uq_payment_webhook_provider_event" in source
    assert 'down_revision: Union[str, None] = "20260830_03"' in source
    assert "INSERT INTO" not in source
