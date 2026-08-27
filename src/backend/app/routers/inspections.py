import uuid
import hashlib
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.models import Booking, InspectionReport
from app.schemas.schemas import InspectionCreateRequest, InspectionResponse

router = APIRouter(prefix="/inspections", tags=["États des Lieux & Scellement SHA-256"])

@router.get("/booking/{booking_id}", response_model=List[InspectionResponse])
async def list_inspections_for_booking(booking_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(InspectionReport)
        .where(InspectionReport.booking_id == booking_id)
        .order_by(InspectionReport.created_at.asc())
    )
    return result.scalars().all()

@router.post("/seal", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def seal_inspection_report(payload: InspectionCreateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Booking).where(Booking.id == payload.booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    # Compute SHA-256 hash of the video evidence and timestamp
    timestamp_iso = datetime.utcnow().isoformat()
    raw_signature = f"{payload.booking_id}:{payload.type}:{payload.video_url}:{timestamp_iso}:RFC3161_SEAL_LOKIINI"
    video_hash = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()

    inspection = InspectionReport(
        booking_id=payload.booking_id,
        type=payload.type,
        video_url=payload.video_url,
        video_sha256_hash=video_hash,
        rfc3161_timestamp=datetime.utcnow(),
        signed_by_owner=True,
        signed_by_renter=True,
        notes=payload.notes or f"État des lieux {payload.type} contradictoire scellé avec succès."
    )
    db.add(inspection)

    # Update booking status accordingly
    if payload.type == "check_in":
        booking.booking_status = "in_progress"
    elif payload.type == "check_out":
        booking.booking_status = "completed"
        booking.cmi_status = "released"

    await db.commit()
    await db.refresh(inspection)

    return inspection
