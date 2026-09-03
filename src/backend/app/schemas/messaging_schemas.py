import uuid
from typing import Literal, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class MessageCreateRequest(BaseModel):
    contenu: str = Field(..., min_length=1, max_length=2000)

    @field_validator("contenu")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        content = value.strip()
        if not content:
            raise ValueError("Le message ne peut pas être vide.")
        return content


class MessageSendRequest(MessageCreateRequest):
    destinataire_id: uuid.UUID
    article_id: Optional[uuid.UUID] = None
    reservation_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def require_one_context(self):
        if bool(self.article_id) == bool(self.reservation_id):
            raise ValueError("Indiquez exactement un contexte: article_id ou reservation_id.")
        return self

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
    reservation_id: Optional[uuid.UUID] = None
    article_id: Optional[uuid.UUID] = None
    context_type: Literal["equipment", "reservation", "legacy"] = "legacy"
    autre_utilisateur_id: uuid.UUID
    autre_utilisateur_nom: str
    autre_utilisateur_avatar: Optional[str] = None
    article_titre: Optional[str] = None
    article_photo: Optional[str] = None
    reservation_statut: Optional[str] = None
    reservation_date_debut: Optional[date] = None
    reservation_date_fin: Optional[date] = None
    dernier_message: Optional[str] = None
    messages_non_lus: int = 0
    modifie_le: datetime

class N8nWebhookTriggerRequest(BaseModel):
    event_type: str
    payload: dict
