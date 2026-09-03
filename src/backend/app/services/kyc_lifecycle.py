from datetime import datetime, timezone
from enum import Enum


class KYCStatus(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    IN_REVIEW = "in_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REQUIRES_ACTION = "requires_action"


class KYCTransitionError(ValueError):
    pass


PROVIDER_STATUS_MAP = {
    "Not Started": KYCStatus.PENDING,
    "In Progress": KYCStatus.PENDING,
    "Approved": KYCStatus.VERIFIED,
    "Declined": KYCStatus.REJECTED,
    "In Review": KYCStatus.IN_REVIEW,
    "Resubmitted": KYCStatus.REQUIRES_ACTION,
    "Expired": KYCStatus.REQUIRES_ACTION,
    "Kyc Expired": KYCStatus.REQUIRES_ACTION,
    "Abandoned": KYCStatus.REQUIRES_ACTION,
    "Awaiting User": KYCStatus.REQUIRES_ACTION,
}


ALLOWED_TRANSITIONS = {
    KYCStatus.NOT_STARTED: {
        KYCStatus.PENDING,
        KYCStatus.IN_REVIEW,
        KYCStatus.VERIFIED,
        KYCStatus.REJECTED,
        KYCStatus.REQUIRES_ACTION,
    },
    KYCStatus.PENDING: {
        KYCStatus.PENDING,
        KYCStatus.IN_REVIEW,
        KYCStatus.VERIFIED,
        KYCStatus.REJECTED,
        KYCStatus.REQUIRES_ACTION,
    },
    KYCStatus.IN_REVIEW: {
        KYCStatus.IN_REVIEW,
        KYCStatus.VERIFIED,
        KYCStatus.REJECTED,
        KYCStatus.REQUIRES_ACTION,
    },
    KYCStatus.REQUIRES_ACTION: {
        KYCStatus.PENDING,
        KYCStatus.IN_REVIEW,
        KYCStatus.VERIFIED,
        KYCStatus.REJECTED,
        KYCStatus.REQUIRES_ACTION,
    },
    KYCStatus.REJECTED: {
        KYCStatus.PENDING,
        KYCStatus.IN_REVIEW,
        KYCStatus.VERIFIED,
        KYCStatus.REJECTED,
        KYCStatus.REQUIRES_ACTION,
    },
    # A signed provider correction can revoke a previous approval.
    KYCStatus.VERIFIED: {
        KYCStatus.VERIFIED,
        KYCStatus.REJECTED,
        KYCStatus.REQUIRES_ACTION,
    },
}


def normalize_internal_status(value: str | None) -> KYCStatus:
    legacy = {
        None: KYCStatus.NOT_STARTED,
        "en_attente": KYCStatus.PENDING,
        "revision_manuelle": KYCStatus.IN_REVIEW,
        "approuve": KYCStatus.VERIFIED,
        "rejete": KYCStatus.REJECTED,
    }
    if value in legacy:
        return legacy[value]
    try:
        return KYCStatus(value)
    except ValueError as exc:
        raise KYCTransitionError(f"Unknown internal KYC status: {value}") from exc


def map_provider_status(provider_status: str) -> KYCStatus:
    """Map Didit's exact session status to Lokiini's smaller internal lifecycle."""
    return PROVIDER_STATUS_MAP.get(provider_status, KYCStatus.REQUIRES_ACTION)


def transition(user, target: KYCStatus, *, provider_status: str | None = None) -> KYCStatus:
    current = normalize_internal_status(user.statut_verification)
    if target not in ALLOWED_TRANSITIONS[current]:
        raise KYCTransitionError(f"Invalid KYC transition: {current.value} -> {target.value}")

    user.statut_verification = target.value
    if provider_status is not None:
        user.kyc_provider_status = provider_status
    if target == KYCStatus.VERIFIED:
        if user.verifie_le is None:
            user.verifie_le = datetime.now(timezone.utc)
    else:
        user.verifie_le = None
    return target


def apply_provider_status(user, provider_status: str) -> KYCStatus:
    return transition(
        user,
        map_provider_status(provider_status),
        provider_status=provider_status,
    )
