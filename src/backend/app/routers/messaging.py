import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_, func
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.models import Conversation, Message, Article, Reservation, User
from app.schemas.messaging_schemas import (
    MessageCreateRequest, MessageSendRequest, MessageResponse,
    ConversationResponse, N8nWebhookTriggerRequest
)
from app.services.n8n_webhook_service import n8n_webhook_service
from app.services.notification_service import NotificationEvent, notify
from app.routers.auth import get_current_user
from app.core.authorization import is_admin

router = APIRouter(tags=["Messagerie Inter-utilisateurs & Centre de Notifications"])


def _messaging_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _require_conversation_participant(conversation: Conversation, current_user: User) -> None:
    if current_user.id not in {conversation.participant1_id, conversation.participant2_id}:
        raise _messaging_error(
            status.HTTP_403_FORBIDDEN,
            "CONVERSATION_FORBIDDEN",
            "Vous ne participez pas à cette conversation.",
        )


async def _get_authorized_conversation(
    conversation_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Conversation:
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalars().first()
    if not conversation:
        raise _messaging_error(status.HTTP_404_NOT_FOUND, "CONVERSATION_NOT_FOUND", "Conversation introuvable.")
    _require_conversation_participant(conversation, current_user)
    return conversation


def _message_response(message: Message, recipient_id: uuid.UUID) -> dict:
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "expediteur_id": message.expediteur_id,
        "destinataire_id": recipient_id,
        "contenu": message.contenu,
        "est_lu": message.lu,
        "cree_le": message.cree_le,
    }


async def _persist_message(
    conversation: Conversation,
    content: str,
    current_user: User,
    db: AsyncSession,
) -> dict:
    _require_conversation_participant(conversation, current_user)
    recipient_id = (
        conversation.participant2_id
        if conversation.participant1_id == current_user.id
        else conversation.participant1_id
    )
    now = datetime.utcnow()
    new_message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        expediteur_id=current_user.id,
        contenu=content,
        lu=False,
        cree_le=now,
    )
    db.add(new_message)
    conversation.dernier_message_le = now
    notify(
        db,
        recipient_id=recipient_id,
        event_type=NotificationEvent.MESSAGE_RECEIVED,
        title=f"Nouveau message de {current_user.nom_complet}",
        body=content[:160],
        conversation_id=conversation.id,
    )
    await db.commit()
    await db.refresh(new_message)

    await n8n_webhook_service.emit_event(
        event_type="message.received",
        payload={
            "message_id": str(new_message.id),
            "conversation_id": str(conversation.id),
            "sender_id": str(current_user.id),
            "sender_name": current_user.nom_complet,
            "recipient_id": str(recipient_id),
            "content_preview": content[:100],
        },
    )
    return _message_response(new_message, recipient_id)

# 1. Liste des conversations actives
@router.get("/messages/conversations", response_model=List[ConversationResponse])
async def list_user_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Liste toutes les conversations actives de l'utilisateur connecté."""
    query = select(Conversation).where(
        or_(Conversation.participant1_id == current_user.id, Conversation.participant2_id == current_user.id)
    ).order_by(Conversation.dernier_message_le.desc())
    
    result = await db.execute(query)
    conversations = result.scalars().all()

    response = []
    for c in conversations:
        other_user_id = c.participant2_id if c.participant1_id == current_user.id else c.participant1_id
        other_user_res = await db.execute(select(User).where(User.id == other_user_id))
        other_user = other_user_res.scalars().first()

        # Fetch last message
        last_msg_res = await db.execute(
            select(Message).where(Message.conversation_id == c.id).order_by(Message.cree_le.desc()).limit(1)
        )
        last_msg = last_msg_res.scalars().first()

        # Unread messages count
        unread_res = await db.execute(
            select(func.count(Message.id)).where(
                Message.conversation_id == c.id,
                Message.expediteur_id != current_user.id,
                Message.lu == False
            )
        )
        unread_count = unread_res.scalar_one() or 0

        booking = None
        article = None
        if c.reservation_id:
            booking_res = await db.execute(select(Reservation).where(Reservation.id == c.reservation_id))
            booking = booking_res.scalars().first()
        article_id = c.article_id or (booking.article_id if booking else None)
        if article_id:
            article_res = await db.execute(select(Article).where(Article.id == article_id))
            article = article_res.scalars().first()
        photos = article.photos if article and isinstance(article.photos, list) else []

        response.append(ConversationResponse(
            id=c.id,
            reservation_id=c.reservation_id,
            article_id=article_id,
            context_type="reservation" if c.reservation_id else ("equipment" if article_id else "legacy"),
            autre_utilisateur_id=other_user_id,
            autre_utilisateur_nom=other_user.nom_complet if other_user else "Utilisateur Lokiini",
            autre_utilisateur_avatar=other_user.avatar_url if other_user else None,
            article_titre=article.titre if article else None,
            article_photo=photos[0] if photos else None,
            reservation_statut=booking.statut if booking else None,
            reservation_date_debut=booking.date_debut if booking else None,
            reservation_date_fin=booking.date_fin if booking else None,
            dernier_message=last_msg.contenu if last_msg else None,
            messages_non_lus=unread_count,
            modifie_le=c.dernier_message_le
        ))

    return response

# 2. Historique d'une conversation
@router.get("/messages/conversations/{conversation_id}", response_model=List[MessageResponse])
async def get_conversation_history(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Affiche tous les messages d'une conversation et marque les messages reçus comme lus."""
    conv = await _get_authorized_conversation(conversation_id, current_user, db)

    msg_res = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.cree_le.asc())
    )
    messages = msg_res.scalars().all()

    # Marquer les messages reçus comme lus
    for m in messages:
        if m.expediteur_id != current_user.id and not m.lu:
            m.lu = True

    await db.commit()
    other_id = conv.participant2_id if conv.participant1_id == current_user.id else conv.participant1_id
    return [{
        "id": m.id, "conversation_id": m.conversation_id, "expediteur_id": m.expediteur_id,
        "destinataire_id": other_id if m.expediteur_id == current_user.id else current_user.id,
        "contenu": m.contenu, "est_lu": m.lu, "cree_le": m.cree_le,
    } for m in messages]


@router.put("/messages/conversations/{conversation_id}/lus")
async def mark_conversation_messages_as_read(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compatibility endpoint retained from the legacy messaging router."""
    await _get_authorized_conversation(conversation_id, current_user, db)
    result = await db.execute(
        select(Message).where(
            Message.conversation_id == conversation_id,
            Message.expediteur_id != current_user.id,
            Message.lu == False,
        )
    )
    messages = result.scalars().all()
    for message in messages:
        message.lu = True
    await db.commit()
    return {"statut": "succes", "messages_lus": len(messages)}


@router.post(
    "/messages/conversations/{conversation_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_conversation_message(
    conversation_id: uuid.UUID,
    payload: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Envoie un message dans une conversation dont l'utilisateur est participant."""
    conversation = await _get_authorized_conversation(conversation_id, current_user, db)
    return await _persist_message(conversation, payload.contenu, current_user, db)


# 3. Démarrer une conversation contextualisée
@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    payload: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Démarre une conversation liée à un équipement ou à une réservation."""
    if payload.destinataire_id == current_user.id:
        raise _messaging_error(status.HTTP_400_BAD_REQUEST, "MESSAGE_SELF_RECIPIENT", "Vous ne pouvez pas vous envoyer un message.")
    recipient_result = await db.execute(select(User).where(User.id == payload.destinataire_id))
    if not recipient_result.scalars().first():
        raise _messaging_error(status.HTTP_404_NOT_FOUND, "MESSAGE_RECIPIENT_NOT_FOUND", "Destinataire introuvable.")

    article_id = payload.article_id
    if payload.reservation_id:
        booking_result = await db.execute(select(Reservation).where(Reservation.id == payload.reservation_id))
        booking = booking_result.scalars().first()
        if not booking:
            raise _messaging_error(status.HTTP_404_NOT_FOUND, "BOOKING_NOT_FOUND", "Réservation introuvable.")
        participants = {booking.locataire_id, booking.loueur_id}
        if current_user.id not in participants or payload.destinataire_id not in participants:
            raise _messaging_error(
                status.HTTP_403_FORBIDDEN,
                "BOOKING_CONVERSATION_FORBIDDEN",
                "Seuls les participants à cette réservation peuvent échanger dans cette conversation.",
            )
        article_id = booking.article_id
    elif payload.article_id:
        article_result = await db.execute(select(Article).where(Article.id == payload.article_id))
        article = article_result.scalars().first()
        if not article:
            raise _messaging_error(status.HTTP_404_NOT_FOUND, "EQUIPMENT_NOT_FOUND", "Article introuvable.")
        if payload.destinataire_id != article.loueur_id:
            raise _messaging_error(
                status.HTTP_403_FORBIDDEN,
                "EQUIPMENT_CONVERSATION_FORBIDDEN",
                "Une nouvelle conversation doit cibler le propriétaire de l'article.",
            )

    # 1. Recherche ou création de la conversation
    query = select(Conversation).where(
        or_(
            and_(Conversation.participant1_id == current_user.id, Conversation.participant2_id == payload.destinataire_id),
            and_(Conversation.participant1_id == payload.destinataire_id, Conversation.participant2_id == current_user.id)
        )
    )
    if payload.reservation_id:
        query = query.where(Conversation.reservation_id == payload.reservation_id)
    else:
        query = query.where(
            Conversation.reservation_id.is_(None),
            Conversation.article_id == article_id,
        )

    conv_res = await db.execute(query)
    conv = conv_res.scalars().first()

    if not conv:
        conv = Conversation(
            id=uuid.uuid4(),
            reservation_id=payload.reservation_id,
            article_id=article_id,
            participant1_id=current_user.id,
            participant2_id=payload.destinataire_id,
            dernier_message_le=datetime.utcnow()
        )
        db.add(conv)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            conv_res = await db.execute(query)
            conv = conv_res.scalars().first()
            if not conv:
                raise _messaging_error(
                    status.HTTP_409_CONFLICT,
                    "CONVERSATION_CREATE_CONFLICT",
                    "La conversation n'a pas pu être créée. Réessayez.",
                )

    return await _persist_message(conv, payload.contenu, current_user, db)

# 4. Webhook n8n trigger
@router.post("/webhooks/n8n/trigger")
async def trigger_n8n_event(
    payload: N8nWebhookTriggerRequest,
    current_user: User = Depends(get_current_user),
):
    """Déclenche manuellement un événement d'automation vers n8n."""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Accès administrateur requis.")
    success = await n8n_webhook_service.emit_event(payload.event_type, payload.payload)
    return {"statut": "succes" if success else "erreur", "event": payload.event_type}
