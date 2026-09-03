import pytest
import sys
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import HTTPException
from pydantic import ValidationError

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.n8n_webhook_service import n8n_webhook_service
from app.schemas.messaging_schemas import (
    MessageCreateRequest, MessageSendRequest, MessageResponse,
    ConversationResponse
)
from app.routers import messaging as messaging_router


class ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return self

    def first(self):
        return self.value

    def all(self):
        return self.value if isinstance(self.value, list) else [self.value]

    def scalar_one(self):
        return self.value


class FakeDb:
    def __init__(self, *values):
        self.values = iter(values)
        self.added = []

    async def execute(self, _query):
        return ScalarResult(next(self.values))

    def add(self, value):
        self.added.append(value)

    async def flush(self):
        return None

    async def commit(self):
        return None

    async def rollback(self):
        return None

    async def refresh(self, _value):
        return None

def test_message_send_request_schema():
    """Test MessageSendRequest validation."""
    dest_id = uuid.uuid4()
    req = MessageSendRequest(
        destinataire_id=dest_id,
        contenu="Bonjour, la bétonnière est-elle toujours disponible pour demain matin ?",
        article_id=uuid.uuid4(),
    )
    assert req.destinataire_id == dest_id
    assert "bétonnière" in req.contenu
    assert req.article_id is not None


def test_new_conversation_requires_exactly_one_marketplace_context():
    values = {"destinataire_id": uuid.uuid4(), "contenu": "Bonjour"}
    with pytest.raises(ValidationError):
        MessageSendRequest(**values)
    with pytest.raises(ValidationError):
        MessageSendRequest(**values, article_id=uuid.uuid4(), reservation_id=uuid.uuid4())


def test_message_content_is_trimmed_and_blank_content_is_rejected():
    assert MessageCreateRequest(contenu="  Bonjour  ").contenu == "Bonjour"
    with pytest.raises(ValidationError):
        MessageCreateRequest(contenu="   ")

def test_n8n_webhook_failure_is_not_reported_as_success():
    """An unavailable n8n endpoint must fail closed."""
    event_payload = {
        "booking_id": str(uuid.uuid4()),
        "user_phone": "+212661000001",
        "action": "reminder_checkin"
    }
    
    result = asyncio.run(n8n_webhook_service.emit_event("booking.created", event_payload))
    assert result is False

def test_conversation_response_schema():
    """Test ConversationResponse structure."""
    conv = ConversationResponse(
        id=uuid.uuid4(),
        autre_utilisateur_id=uuid.uuid4(),
        autre_utilisateur_nom="Omar Loueur BTP",
        article_titre="Perforateur Bosch 800W",
        dernier_message="D'accord, rendez-vous à 9h à Sidi Maarouf.",
        messages_non_lus=1,
        modifie_le=datetime.utcnow()
    )
    assert conv.autre_utilisateur_nom == "Omar Loueur BTP"
    assert conv.messages_non_lus == 1


def test_non_participant_cannot_read_or_send_even_with_admin_role():
    conversation = SimpleNamespace(
        id=uuid.uuid4(),
        participant1_id=uuid.uuid4(),
        participant2_id=uuid.uuid4(),
    )
    outsider = SimpleNamespace(id=uuid.uuid4(), user_role="admin")
    with pytest.raises(HTTPException) as failure:
        asyncio.run(messaging_router._get_authorized_conversation(
            conversation.id,
            outsider,
            FakeDb(conversation),
        ))
    assert failure.value.status_code == 403
    assert failure.value.detail["code"] == "CONVERSATION_FORBIDDEN"


def test_equipment_conversation_persists_context_and_real_message(monkeypatch):
    sender_id, owner_id, article_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    sender = SimpleNamespace(id=sender_id, nom_complet="Locataire", user_role="renter")
    recipient = SimpleNamespace(id=owner_id)
    article = SimpleNamespace(id=article_id, loueur_id=owner_id)
    database = FakeDb(recipient, article, None)
    monkeypatch.setattr(n8n_webhook_service, "emit_event", AsyncMock(return_value=True))

    response = asyncio.run(messaging_router.send_message(
        MessageSendRequest(
            destinataire_id=owner_id,
            article_id=article_id,
            contenu="  Le matériel est-il disponible ?  ",
        ),
        sender,
        database,
    ))

    conversation, message, notification = database.added
    assert conversation.article_id == article_id
    assert conversation.reservation_id is None
    assert message.conversation_id == conversation.id
    assert message.contenu == "Le matériel est-il disponible ?"
    assert notification.type == "message_received"
    assert notification.utilisateur_id == owner_id
    assert response["conversation_id"] == conversation.id

def test_messaging_routes_integrity():
    """Test that all Phase 7 messaging & notification routes are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]
    
    assert "/api/v1/messages/conversations" in paths
    assert "/api/v1/messages/conversations/{conversation_id}" in paths
    assert "/api/v1/messages" in paths
    assert "/api/v1/messages/conversations/{conversation_id}/lus" in paths
    assert "/api/v1/webhooks/n8n/trigger" in paths

    conversation_operations = paths["/api/v1/messages/conversations/{conversation_id}"]
    assert "get" in conversation_operations
    assert "post" in conversation_operations
