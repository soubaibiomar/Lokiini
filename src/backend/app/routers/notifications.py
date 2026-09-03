import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.models import Notification, User
from app.routers.auth import get_current_user
from app.schemas.notification_schemas import (
    NotificationReadAllResponse,
    NotificationReadRequest,
    NotificationReadResponse,
    NotificationResponse,
)
from app.services.notification_service import notification_response


router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "NOTIFICATION_NOT_FOUND", "message": "Notification introuvable."},
    )


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    state: Literal["all", "unread"] = Query("all"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notification).where(Notification.utilisateur_id == current_user.id)
    if state == "unread":
        query = query.where(Notification.lu.is_(False))
    result = await db.execute(query.order_by(Notification.cree_le.desc()).limit(100))
    return [notification_response(item) for item in result.scalars().all()]


@router.patch("/tout-lire", response_model=NotificationReadAllResponse)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Notification).where(
        Notification.utilisateur_id == current_user.id,
        Notification.lu.is_(False),
    ))
    notifications = result.scalars().all()
    read_at = datetime.now(timezone.utc)
    for notification in notifications:
        notification.lu = True
        notification.lu_le = read_at
    await db.commit()
    return NotificationReadAllResponse(notifications_lues=len(notifications))


async def _set_read_state(
    notification_id: uuid.UUID,
    is_read: bool,
    current_user: User,
    db: AsyncSession,
) -> NotificationReadResponse:
    result = await db.execute(select(Notification).where(and_(
        Notification.id == notification_id,
        Notification.utilisateur_id == current_user.id,
    )).with_for_update())
    notification = result.scalars().first()
    if not notification:
        raise _not_found()
    notification.lu = is_read
    notification.lu_le = datetime.now(timezone.utc) if is_read else None
    await db.commit()
    return NotificationReadResponse(
        id=notification.id,
        est_lu=notification.lu,
        lu_le=notification.lu_le,
    )


@router.patch("/{notification_id}", response_model=NotificationReadResponse)
async def update_notification_read_state(
    notification_id: uuid.UUID,
    payload: NotificationReadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _set_read_state(notification_id, payload.est_lu, current_user, db)


@router.patch("/{notification_id}/lire", response_model=NotificationReadResponse, include_in_schema=False)
async def mark_notification_as_read_legacy(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _set_read_state(notification_id, True, current_user, db)
