import uuid
from enum import Enum

from app.models.models import Notification
from app.schemas.notification_schemas import NotificationDestination, NotificationResponse


class NotificationEvent(str, Enum):
    RESERVATION_REQUESTED = "reservation_requested"
    RESERVATION_ACCEPTED = "reservation_accepted"
    RESERVATION_REJECTED = "reservation_rejected"
    KYC_UPDATED = "kyc_updated"
    PAYMENT_UPDATED = "payment_updated"
    DEPOSIT_UPDATED = "deposit_updated"
    INSPECTION_REQUIRED = "inspection_required"
    MESSAGE_RECEIVED = "message_received"
    DISPUTE_UPDATED = "dispute_updated"
    PAYOUT_UPDATED = "payout_updated"


EVENT_SECTIONS = {
    NotificationEvent.RESERVATION_REQUESTED.value: "bookings",
    NotificationEvent.RESERVATION_ACCEPTED.value: "bookings",
    NotificationEvent.RESERVATION_REJECTED.value: "bookings",
    NotificationEvent.KYC_UPDATED.value: "verification",
    NotificationEvent.PAYMENT_UPDATED.value: "payments",
    NotificationEvent.DEPOSIT_UPDATED.value: "payments",
    NotificationEvent.INSPECTION_REQUIRED.value: "bookings",
    NotificationEvent.MESSAGE_RECEIVED.value: "messages",
    NotificationEvent.DISPUTE_UPDATED.value: "disputes",
    NotificationEvent.PAYOUT_UPDATED.value: "earnings",
}

LEGACY_EVENT_ALIASES = {
    "reservation": NotificationEvent.RESERVATION_REQUESTED.value,
    "booking_approved": NotificationEvent.RESERVATION_ACCEPTED.value,
    "message": NotificationEvent.MESSAGE_RECEIVED.value,
    "paiement": NotificationEvent.PAYMENT_UPDATED.value,
    "payment": NotificationEvent.PAYMENT_UPDATED.value,
    "dispute": NotificationEvent.DISPUTE_UPDATED.value,
}

RESOURCE_KEYS = {
    "bookings": "booking_id",
    "verification": "user_id",
    "payments": "booking_id",
    "messages": "conversation_id",
    "disputes": "dispute_id",
    "earnings": "payout_id",
}


def normalize_event_type(value: str) -> str:
    return LEGACY_EVENT_ALIASES.get(value, value)


def notification_destination(notification: Notification) -> NotificationDestination:
    event_type = normalize_event_type(notification.type)
    section = EVENT_SECTIONS.get(event_type, "bookings")
    data = notification.data if isinstance(notification.data, dict) else {}
    resource_value = data.get(RESOURCE_KEYS[section])
    try:
        resource_id = uuid.UUID(str(resource_value)) if resource_value else None
    except (TypeError, ValueError, AttributeError):
        resource_id = None
    return NotificationDestination(section=section, resource_id=resource_id)


def notification_response(notification: Notification) -> NotificationResponse:
    event_type = normalize_event_type(notification.type)
    destination = notification_destination(notification)
    return NotificationResponse(
        id=notification.id,
        event_type=event_type,
        titre=notification.titre,
        message=notification.corps,
        destination=destination,
        deep_link=f"#account-{destination.section}",
        est_lu=bool(notification.lu),
        lu_le=notification.lu_le,
        cree_le=notification.cree_le,
    )


def notify(
    db,
    *,
    recipient_id: uuid.UUID,
    event_type: NotificationEvent,
    title: str,
    body: str,
    booking_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    conversation_id: uuid.UUID | None = None,
    dispute_id: uuid.UUID | None = None,
    payout_id: uuid.UUID | None = None,
) -> Notification:
    data = {
        key: str(value)
        for key, value in {
            "booking_id": booking_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "dispute_id": dispute_id,
            "payout_id": payout_id,
        }.items()
        if value is not None
    }
    record = Notification(
        utilisateur_id=recipient_id,
        type=event_type.value,
        titre=title,
        corps=body,
        data=data,
        lu=False,
    )
    db.add(record)
    return record
