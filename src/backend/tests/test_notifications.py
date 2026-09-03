import asyncio
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.main import app
from app.models.models import Notification
from app.routers import notifications as notification_router
from app.services.notification_service import (
    EVENT_SECTIONS,
    NotificationEvent,
    notification_response,
    notify,
)


class ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return self

    def first(self):
        return self.value

    def all(self):
        return self.value if isinstance(self.value, list) else [self.value]


class FakeDb:
    def __init__(self, value):
        self.value = value
        self.added = []
        self.committed = False

    async def execute(self, query):
        self.query = query
        return ScalarResult(self.value)

    def add(self, value):
        self.added.append(value)

    async def commit(self):
        self.committed = True


def make_notification(*, event_type="message_received", read=False):
    return SimpleNamespace(
        id=uuid.uuid4(),
        utilisateur_id=uuid.uuid4(),
        type=event_type,
        titre="Mise à jour réelle",
        corps="Un événement backend a été enregistré.",
        data={"conversation_id": str(uuid.uuid4())},
        lu=read,
        lu_le=datetime.now(timezone.utc) if read else None,
        cree_le=datetime.now(timezone.utc),
    )


def test_every_supported_event_has_one_backend_destination():
    assert set(EVENT_SECTIONS) == {event.value for event in NotificationEvent}
    assert EVENT_SECTIONS[NotificationEvent.RESERVATION_REQUESTED.value] == "bookings"
    assert EVENT_SECTIONS[NotificationEvent.KYC_UPDATED.value] == "verification"
    assert EVENT_SECTIONS[NotificationEvent.DEPOSIT_UPDATED.value] == "payments"
    assert EVENT_SECTIONS[NotificationEvent.MESSAGE_RECEIVED.value] == "messages"
    assert EVENT_SECTIONS[NotificationEvent.DISPUTE_UPDATED.value] == "disputes"
    assert EVENT_SECTIONS[NotificationEvent.PAYOUT_UPDATED.value] == "earnings"


def test_notification_response_builds_only_internal_account_deep_links():
    response = notification_response(make_notification())
    assert response.event_type == "message_received"
    assert response.destination.section == "messages"
    assert response.deep_link == "#account-messages"
    assert response.deep_link.startswith("#account-")


def test_notification_service_persists_real_event_and_resource_context():
    database = FakeDb(None)
    recipient_id, booking_id = uuid.uuid4(), uuid.uuid4()
    record = notify(
        database,
        recipient_id=recipient_id,
        event_type=NotificationEvent.RESERVATION_REQUESTED,
        title="Nouvelle demande",
        body="Une demande a été créée.",
        booking_id=booking_id,
    )
    assert database.added == [record]
    assert record.utilisateur_id == recipient_id
    assert record.type == "reservation_requested"
    assert record.data == {"booking_id": str(booking_id)}
    assert record.lu is False


def test_only_notification_owner_can_change_read_state():
    outsider = SimpleNamespace(id=uuid.uuid4())
    database = FakeDb(None)
    with pytest.raises(HTTPException) as failure:
        asyncio.run(notification_router._set_read_state(
            uuid.uuid4(), True, outsider, database,
        ))
    assert failure.value.status_code == 404
    compiled = str(database.query)
    assert "notifications.utilisateur_id" in compiled


def test_read_state_can_be_set_and_reversed():
    record = make_notification()
    user = SimpleNamespace(id=record.utilisateur_id)
    database = FakeDb(record)
    read = asyncio.run(notification_router._set_read_state(record.id, True, user, database))
    assert read.est_lu is True
    assert read.lu_le is not None
    assert database.committed is True

    database.committed = False
    unread = asyncio.run(notification_router._set_read_state(record.id, False, user, database))
    assert unread.est_lu is False
    assert unread.lu_le is None
    assert database.committed is True


def test_unified_notification_routes_are_authoritative():
    routes = {
        (route.path, method): route.endpoint.__module__
        for route in app.routes
        for method in getattr(route, "methods", [])
    }
    assert routes[("/api/v1/notifications", "GET")] == "app.routers.notifications"
    assert routes[("/api/v1/notifications/tout-lire", "PATCH")] == "app.routers.notifications"
    assert routes[("/api/v1/notifications/{notification_id}", "PATCH")] == "app.routers.notifications"
