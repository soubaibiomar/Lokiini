import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from app.core.database import get_db
from app.models.models import Conversation, Message, Notification, Article, User
from app.schemas.messaging_schemas import (
    MessageSendRequest, MessageResponse,
    ConversationResponse, NotificationResponse,
    N8nWebhookTriggerRequest
)
from app.services.n8n_webhook_service import n8n_webhook_service
from app.routers.auth import get_current_user

router = APIRouter(tags=["Messagerie Inter-utilisateurs & Centre de Notifications"])

# 1. Liste des conversations actives
@router.get("/messages/conversations", response_model=List[ConversationResponse])
async def list_user_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Liste toutes les conversations actives de l'utilisateur connecté."""
    query = select(Conversation).where(
        or_(Conversation.locataire_id == current_user.id, Conversation.loueur_id == current_user.id)
    ).order_by(Conversation.modifie_le.desc())
    
    result = await db.execute(query)
    conversations = result.scalars().all()

    response = []
    for c in conversations:
        other_user_id = c.loueur_id if c.locataire_id == current_user.id else c.locataire_id
        other_user_res = await db.execute(select(User).where(User.id == other_user_id))
        other_user = other_user_res.scalars().first()

        # Fetch last message
        last_msg_res = await db.execute(
            select(Message).where(Message.conversation_id == c.id).order_by(Message.cree_le.desc()).limit(1)
        )
        last_msg = last_msg_res.scalars().first()

        # Unread messages count
        unread_res = await db.execute(
            select(Message).where(
                Message.conversation_id == c.id,
                Message.destinataire_id == current_user.id,
                Message.est_lu == False
            )
        )
        unread_count = len(unread_res.scalars().all())

        art_title = None
        if c.article_id:
            art_res = await db.execute(select(Article).where(Article.id == c.article_id))
            art = art_res.scalars().first()
            if art: art_title = art.titre

        response.append(ConversationResponse(
            id=c.id,
            autre_utilisateur_id=other_user_id,
            autre_utilisateur_nom=other_user.nom_complet if other_user else "Utilisateur Lokiini",
            article_titre=art_title,
            dernier_message=last_msg.contenu if last_msg else None,
            messages_non_lus=unread_count,
            modifie_le=c.modifie_le
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
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable.")

    if current_user.id not in [conv.locataire_id, conv.loueur_id] and current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé.")

    msg_res = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.cree_le.asc())
    )
    messages = msg_res.scalars().all()

    # Marquer les messages reçus comme lus
    for m in messages:
        if m.destinataire_id == current_user.id and not m.est_lu:
            m.est_lu = True

    await db.commit()
    return messages

# 3. Envoyer un message
@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    payload: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Envoie un message textuel et déclenche l'événement webhook vers n8n."""
    # 1. Recherche ou création de la conversation
    query = select(Conversation).where(
        or_(
            and_(Conversation.locataire_id == current_user.id, Conversation.loueur_id == payload.destinataire_id),
            and_(Conversation.locataire_id == payload.destinataire_id, Conversation.loueur_id == current_user.id)
        )
    )
    if payload.article_id:
        query = query.where(Conversation.article_id == payload.article_id)

    conv_res = await db.execute(query)
    conv = conv_res.scalars().first()

    if not conv:
        conv = Conversation(
            id=uuid.uuid4(),
            article_id=payload.article_id,
            reservation_id=payload.reservation_id,
            locataire_id=current_user.id,
            loueur_id=payload.destinataire_id,
            modifie_le=datetime.utcnow()
        )
        db.add(conv)
        await db.flush()

    # 2. Création du message
    new_message = Message(
        id=uuid.uuid4(),
        conversation_id=conv.id,
        expediteur_id=current_user.id,
        destinataire_id=payload.destinataire_id,
        contenu=payload.contenu,
        est_lu=False,
        cree_le=datetime.utcnow()
    )
    db.add(new_message)
    conv.modifie_le = datetime.utcnow()
    await db.commit()
    await db.refresh(new_message)

    # 3. Déclenchement événement n8n pour notification WhatsApp/Push
    await n8n_webhook_service.emit_event(
        event_type="message.received",
        payload={
            "message_id": str(new_message.id),
            "sender_id": str(current_user.id),
            "sender_name": current_user.nom_complet,
            "recipient_id": str(payload.destinataire_id),
            "content_preview": payload.contenu[:100]
        }
    )

    return new_message

# 4. Centre de notifications
@router.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Consulte les notifications de l'utilisateur."""
    result = await db.execute(
        select(Notification).where(Notification.utilisateur_id == current_user.id).order_by(Notification.cree_le.desc())
    )
    notifs = result.scalars().all()
    return notifs

# 5. Marquer notification comme lue
@router.patch("/notifications/{notification_id}/lire")
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marque une notification comme lue."""
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notif = result.scalars().first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable.")

    if notif.utilisateur_id != current_user.id and current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé.")

    notif.est_lu = True
    await db.commit()
    return {"statut": "succes", "message": "Notification marquée comme lue."}

# 6. Webhook n8n trigger
@router.post("/webhooks/n8n/trigger")
async def trigger_n8n_event(payload: N8nWebhookTriggerRequest):
    """Déclenche manuellement un événement d'automation vers n8n."""
    success = await n8n_webhook_service.emit_event(payload.event_type, payload.payload)
    return {"statut": "succes" if success else "erreur", "event": payload.event_type}
