from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Mapping, Set, TypeVar


class FinancialTransitionError(ValueError):
    """Raised when an internal financial state change is not allowed."""


class RentalPaymentStatus(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    REQUIRES_ACTION = "requires_action"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIALLY_REFUNDED = "partially_refunded"
    REFUNDED = "refunded"


class PlatformFeeStatus(str, Enum):
    PENDING = "pending"
    EARNED = "earned"
    REVERSED = "reversed"


class DepositStatus(str, Enum):
    NOT_STARTED = "not_started"
    AUTHORIZATION_PENDING = "authorization_pending"
    AUTHORIZED = "authorized"
    AUTHORIZATION_FAILED = "authorization_failed"
    RELEASED = "released"
    PARTIALLY_CAPTURED = "partially_captured"
    CAPTURED = "captured"


class RefundStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class OwnerPayoutStatus(str, Enum):
    NOT_READY = "not_ready"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REVERSED = "reversed"


T = TypeVar("T", bound=Enum)


PAYMENT_TRANSITIONS: Mapping[RentalPaymentStatus, Set[RentalPaymentStatus]] = {
    RentalPaymentStatus.NOT_STARTED: {RentalPaymentStatus.PENDING},
    RentalPaymentStatus.PENDING: {
        RentalPaymentStatus.REQUIRES_ACTION,
        RentalPaymentStatus.SUCCEEDED,
        RentalPaymentStatus.FAILED,
        RentalPaymentStatus.CANCELLED,
    },
    RentalPaymentStatus.REQUIRES_ACTION: {
        RentalPaymentStatus.PENDING,
        RentalPaymentStatus.SUCCEEDED,
        RentalPaymentStatus.FAILED,
        RentalPaymentStatus.CANCELLED,
    },
    RentalPaymentStatus.SUCCEEDED: {
        RentalPaymentStatus.PARTIALLY_REFUNDED,
        RentalPaymentStatus.REFUNDED,
    },
    RentalPaymentStatus.PARTIALLY_REFUNDED: {RentalPaymentStatus.REFUNDED},
    RentalPaymentStatus.FAILED: set(),
    RentalPaymentStatus.CANCELLED: set(),
    RentalPaymentStatus.REFUNDED: set(),
}

PLATFORM_FEE_TRANSITIONS: Mapping[PlatformFeeStatus, Set[PlatformFeeStatus]] = {
    PlatformFeeStatus.PENDING: {PlatformFeeStatus.EARNED, PlatformFeeStatus.REVERSED},
    PlatformFeeStatus.EARNED: {PlatformFeeStatus.REVERSED},
    PlatformFeeStatus.REVERSED: set(),
}

DEPOSIT_TRANSITIONS: Mapping[DepositStatus, Set[DepositStatus]] = {
    DepositStatus.NOT_STARTED: {DepositStatus.AUTHORIZATION_PENDING},
    DepositStatus.AUTHORIZATION_PENDING: {
        DepositStatus.AUTHORIZED,
        DepositStatus.AUTHORIZATION_FAILED,
    },
    DepositStatus.AUTHORIZED: {
        DepositStatus.RELEASED,
        DepositStatus.PARTIALLY_CAPTURED,
        DepositStatus.CAPTURED,
    },
    DepositStatus.AUTHORIZATION_FAILED: set(),
    DepositStatus.RELEASED: set(),
    DepositStatus.PARTIALLY_CAPTURED: set(),
    DepositStatus.CAPTURED: set(),
}

REFUND_TRANSITIONS: Mapping[RefundStatus, Set[RefundStatus]] = {
    RefundStatus.PENDING: {RefundStatus.SUCCEEDED, RefundStatus.FAILED},
    RefundStatus.SUCCEEDED: set(),
    RefundStatus.FAILED: set(),
}

PAYOUT_TRANSITIONS: Mapping[OwnerPayoutStatus, Set[OwnerPayoutStatus]] = {
    OwnerPayoutStatus.NOT_READY: {OwnerPayoutStatus.PENDING},
    OwnerPayoutStatus.PENDING: {OwnerPayoutStatus.PAID, OwnerPayoutStatus.FAILED},
    OwnerPayoutStatus.PAID: {OwnerPayoutStatus.REVERSED},
    OwnerPayoutStatus.FAILED: {OwnerPayoutStatus.PENDING},
    OwnerPayoutStatus.REVERSED: set(),
}


def validate_transition(current: T, target: T, transitions: Mapping[T, Set[T]], domain: str) -> None:
    if target == current:
        return
    if target not in transitions.get(current, set()):
        raise FinancialTransitionError(
            f"Invalid {domain} transition: {current.value} -> {target.value}"
        )


def validate_deposit_capture(
    authorized_amount: Decimal,
    capture_amount: Decimal,
    target: DepositStatus,
) -> None:
    authorized = Decimal(authorized_amount)
    capture = Decimal(capture_amount)
    if capture <= 0 or capture > authorized:
        raise FinancialTransitionError("Deposit capture must be positive and cannot exceed the authorization")
    if target == DepositStatus.PARTIALLY_CAPTURED and capture >= authorized:
        raise FinancialTransitionError("A partial deposit capture must be less than the authorization")
    if target == DepositStatus.CAPTURED and capture != authorized:
        raise FinancialTransitionError("A full deposit capture must equal the authorization")

