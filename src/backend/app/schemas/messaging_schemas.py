import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class MessageSendRequest(BaseModel):
    destinataire_id: uuid.UUID
    contenu: str = Field(..., min_length=1, max_length=2000)
    article_id: Optional[uuid.UUID] = None
    reservation_id: Optional[uuid.UUID] = None

class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    expediteur_id: uuid.UUID
    destinataire_id: uuid.UUID
    contenu: str
    est_lu: bool
    cree_le: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: uuid.UUID
    autre_utilisateur_id: uuid.UUID
    autre_utilisateur_nom: str
    article_titre: Optional[str] = None
    dernier_message: Optional[str] = None
    messages_non_lus: int = 0
    modifie_le: datetime

class NotificationResponse(BaseModel):
    id: uuid.UUID
    titre: str
    message: str
    type_notification: str
    lien_redirection: Optional[str] = None
    est_lu: bool
    cree_le: datetime

class N8nWebhookTriggerRequest(BaseModel):
    event_type: str
    payload: dict
