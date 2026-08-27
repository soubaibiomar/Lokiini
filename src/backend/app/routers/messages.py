import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.core.database import get_db
from app.models.models import Conversation, Message, Utilisateur
from app.routers.auth import get_current_user
from app.schemas.schemas import MessageCreate, MessageResponse, ConversationResponse

router = APIRouter(tags=["Messagerie & Chat Temps Réel"])

@router.get("/messages/conversations", response_model=List[ConversationResponse])
async def lister_conversations(
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Liste toutes les conversations actives de l'utilisateur."""
    query = select(Conversation).where(
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id
        )
    ).order_by(Conversation.dernier_message_le.desc())

    result = await db.execute(query)
    conversations = result.scalars().all()

    reponses = []
    for c in conversations:
        autre_id = c.participant2_id if c.participant1_id == current_user.id else c.participant1_id
        res_autre = await db.execute(select(Utilisateur).where(Utilisateur.id == autre_id))
        autre = res_autre.scalars().first()

        # Dernier message
        res_msg = await db.execute(
            select(Message).where(Message.conversation_id == c.id).order_by(Message.cree_le.desc()).limit(1)
        )
        last_msg = res_msg.scalars().first()

        # Non lus
        res_unread = await db.execute(
            select(Message).where(
                Message.conversation_id == c.id,
                Message.expediteur_id != current_user.id,
                Message.lu == False
            )
        )
        unread_count = len(res_unread.scalars().all())

        reponses.append(ConversationResponse(
            id=c.id,
            reservation_id=c.reservation_id,
            dernier_message=last_msg.contenu if last_msg else None,
            non_lus_count=unread_count,
            autre_participant={
                "id": str(autre.id) if autre else None,
                "nom": autre.nom_complet if autre else "Utilisateur Lokiini",
                "avatar": autre.avatar_url if autre else None
            },
            dernier_message_le=c.dernier_message_le
        ))

    return reponses


@router.get("/messages/conversations/{conversation_id}", response_model=List[MessageResponse])
async def charger_messages_conversation(
    conversation_id: uuid.UUID,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Récupère l'historique complet des messages d'une conversation."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.cree_le.asc())
    )
    messages = result.scalars().all()
    return messages


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def envoyer_message(
    payload: MessageCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Envoie un nouveau message dans une conversation ou initie un échange."""
    conv_id = payload.conversation_id

    if not conv_id:
        # Trouver ou créer conversation
        if not payload.destinataire_id:
            raise HTTPException(status_code=400, detail="Identifiant destinataire requis.")

        query = select(Conversation).where(
            or_(
                and_(Conversation.participant1_id == current_user.id, Conversation.participant2_id == payload.destinataire_id),
                and_(Conversation.participant1_id == payload.destinataire_id, Conversation.participant2_id == current_user.id)
            )
        )
        res_conv = await db.execute(query)
        conv = res_conv.scalars().first()

        if not conv:
            conv = Conversation(
                participant1_id=current_user.id,
                participant2_id=payload.destinataire_id,
                reservation_id=payload.reservation_id
            )
            db.add(conv)
            await db.commit()
            await db.refresh(conv)
        conv_id = conv.id

    nouveau_message = Message(
        conversation_id=conv_id,
        reservation_id=payload.reservation_id,
        expediteur_id=current_user.id,
        contenu=payload.contenu,
        lu=False
    )

    db.add(nouveau_message)

    # Mettre à jour l'horodatage de la conversation
    res_c = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    c_obj = res_c.scalars().first()
    if c_obj:
        c_obj.dernier_message_le = datetime.utcnow()

    await db.commit()
    await db.refresh(nouveau_message)
    return nouveau_message


@router.put("/messages/conversations/{conversation_id}/lus")
async def marquer_messages_lus(
    conversation_id: uuid.UUID,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marque tous les messages non lus de cette conversation comme consultés."""
    query = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.expediteur_id != current_user.id,
        Message.lu == False
    )
    result = await db.execute(query)
    messages = result.scalars().all()

    for m in messages:
        m.lu = True

    await db.commit()
    return {"statut": "succes", "messages_lus": len(messages)}
