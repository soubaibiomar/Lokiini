import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


NotificationSection = Literal[
    "bookings", "verification", "payments", "messages",
    "disputes", "earnings",
]


class NotificationDestination(BaseModel):
    view: Literal["dashboard"] = "dashboard"
    section: NotificationSection
    resource_id: Optional[uuid.UUID] = None


class NotificationResponse(BaseModel):
    id: uuid.UUID
    event_type: str
    titre: str
    message: str
    destination: NotificationDestination
    deep_link: str
    est_lu: bool
    lu_le: Optional[datetime] = None
    cree_le: datetime


class NotificationReadRequest(BaseModel):
    est_lu: bool


class NotificationReadResponse(BaseModel):
    id: uuid.UUID
    est_lu: bool
    lu_le: Optional[datetime] = None


class NotificationReadAllResponse(BaseModel):
    notifications_lues: int
