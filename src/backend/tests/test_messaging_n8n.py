import pytest
import sys
import uuid
import asyncio
from datetime import datetime
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.n8n_webhook_service import n8n_webhook_service
from app.schemas.messaging_schemas import (
    MessageSendRequest, MessageResponse,
    ConversationResponse, NotificationResponse
)

def test_message_send_request_schema():
    """Test MessageSendRequest validation."""
    dest_id = uuid.uuid4()
    req = MessageSendRequest(
        destinataire_id=dest_id,
        contenu="Bonjour, la bétonnière est-elle toujours disponible pour demain matin ?"
    )
    assert req.destinataire_id == dest_id
    assert "bétonnière" in req.contenu
    assert req.article_id is None

def test_n8n_webhook_emission_mock():
    """Test n8n webhook event emission."""
    event_payload = {
        "booking_id": str(uuid.uuid4()),
        "user_phone": "+212661000001",
        "action": "reminder_checkin"
    }
    
    result = asyncio.run(n8n_webhook_service.emit_event("booking.created", event_payload))
    assert result is True

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

def test_notification_response_schema():
    """Test NotificationResponse structure."""
    notif = NotificationResponse(
        id=uuid.uuid4(),
        titre="Réservation Approuvée !",
        message="Le loueur a accepté votre demande. Vous pouvez maintenant sceller le bail.",
        type_notification="booking_approved",
        est_lu=False,
        cree_le=datetime.utcnow()
    )
    assert notif.type_notification == "booking_approved"
    assert notif.est_lu is False

def test_messaging_routes_integrity():
    """Test that all Phase 7 messaging & notification routes are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]
    
    assert "/api/v1/messages/conversations" in paths
    assert "/api/v1/messages/conversations/{conversation_id}" in paths
    assert "/api/v1/messages" in paths
    assert "/api/v1/notifications" in paths
    assert "/api/v1/notifications/{notification_id}/lire" in paths
    assert "/api/v1/webhooks/n8n/trigger" in paths
