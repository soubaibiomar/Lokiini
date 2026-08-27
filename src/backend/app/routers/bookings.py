import uuid
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Equipment, Booking, CMITransaction, User
from app.schemas.schemas import (
    PriceCalculationRequest, PriceCalculationResponse,
    BookingCreateRequest, BookingResponse, BookingStatusUpdateRequest
)

router = APIRouter(prefix="/bookings", tags=["Réservations & Cautions CMI"])

def calculate_degressive_discount(days: int) -> int:
    """Moroccan rental discount tiers."""
    if days >= 30:
        return 50 # -50% pour location mensuelle
    elif days >= 7:
        return 30 # -30% pour location hebdomadaire
    elif days >= 3:
        return 15 # -15% pour 3 jours et plus
    return 0

def format_booking_response(b: Booking) -> BookingResponse:
    cmi = b.cmi_transaction
    eq = b.equipment
    renter = b.renter
    owner = eq.owner if eq else None
    
    img = None
    if eq and eq.images_urls:
        if isinstance(eq.images_urls, list) and len(eq.images_urls) > 0:
            img = eq.images_urls[0]

    return BookingResponse(
        id=b.id,
        equipment_id=b.equipment_id,
        renter_id=b.renter_id,
        start_date=b.start_date,
        end_date=b.end_date,
        total_days=b.total_days,
        daily_rate_applied_mad=float(b.daily_rate_applied_mad) if b.daily_rate_applied_mad else float(b.rental_total_mad / b.total_days),
        rental_total_mad=float(b.rental_total_mad),
        platform_commission_mad=float(b.platform_commission_mad),
        deposit_hold_mad=float(b.deposit_hold_mad),
        booking_status=b.booking_status,
        cmi_status=b.cmi_status,
        cmi_auth_token=cmi.cmi_auth_token if cmi else None,
        cmi_trans_id=cmi.cmi_trans_id if cmi else None,
        contract_pdf_url=b.contract_pdf_url,
        contract_sha256=b.contract_sha256,
        equipment_title=eq.title if eq else "Équipement",
        equipment_city=eq.city if eq else "Casablanca",
        equipment_image=img,
        renter_name=renter.full_name if renter else "Locataire",
        owner_name=owner.full_name if owner else "Loueur Pro",
        created_at=b.created_at
    )

@router.post("/calculate-pricing", response_model=PriceCalculationResponse)
async def calculate_pricing(payload: PriceCalculationRequest, db: AsyncSession = Depends(get_db)):
    if payload.end_date < payload.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de fin doit être supérieure ou égale à la date de début."
        )

    result = await db.execute(select(Equipment).where(Equipment.id == payload.equipment_id))
    equipment = result.scalars().first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Équipement introuvable.")

    total_days = (payload.end_date - payload.start_date).days + 1
    daily_base = float(equipment.daily_price_mad)
    
    # Degressive calculation
    discount_pct = calculate_degressive_discount(total_days)
    discounted_daily_rate = daily_base * (1 - discount_pct / 100)
    
    subtotal_rental = round(discounted_daily_rate * total_days, 2)
    commission = round(subtotal_rental * settings.PLATFORM_COMMISSION_PCT, 2)
    total_due = subtotal_rental # Renter pays the rental subtotal (commission included)
    
    return PriceCalculationResponse(
        total_days=total_days,
        daily_base_price_mad=daily_base,
        discount_percentage=discount_pct,
        discounted_daily_rate_mad=discounted_daily_rate,
        subtotal_rental_mad=subtotal_rental,
        platform_commission_mad=commission,
        total_due_renter_mad=total_due,
        deposit_hold_mad=float(equipment.deposit_amount_mad),
        currency="MAD"
    )

@router.get("", response_model=List[BookingResponse])
async def list_bookings(
    status_filter: Optional[str] = Query(None, description="Filtrer par statut (pending, confirmed, in_progress, completed)"),
    owner_id: Optional[uuid.UUID] = Query(None, description="Filtrer par propriétaire d'équipement"),
    renter_id: Optional[uuid.UUID] = Query(None, description="Filtrer par locataire"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Booking).options(
        selectinload(Booking.equipment).selectinload(Equipment.owner),
        selectinload(Booking.renter),
        selectinload(Booking.cmi_transaction)
    )

    if status_filter:
        query = query.where(Booking.booking_status == status_filter)
    if renter_id:
        query = query.where(Booking.renter_id == renter_id)
    if owner_id:
        query = query.join(Equipment, Booking.equipment_id == Equipment.id).where(Equipment.owner_id == owner_id)

    result = await db.execute(query.order_by(Booking.created_at.desc()))
    bookings = result.scalars().all()
    return [format_booking_response(b) for b in bookings]

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.equipment).selectinload(Equipment.owner),
            selectinload(Booking.renter),
            selectinload(Booking.cmi_transaction)
        )
    )
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")
    return format_booking_response(booking)

@router.post("/create", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    # Fetch equipment
    result = await db.execute(
        select(Equipment)
        .where(Equipment.id == payload.equipment_id)
        .options(selectinload(Equipment.owner))
    )
    equipment = result.scalars().first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Équipement introuvable.")

    renter_id = payload.renter_id
    if not renter_id:
        # Default to renter user from seed
        result_user = await db.execute(select(User).where(User.user_role == "renter").limit(1))
        renter = result_user.scalars().first()
        if not renter:
            result_user = await db.execute(select(User).limit(1))
            renter = result_user.scalars().first()
        if not renter:
            # Create a renter user
            renter = User(
                full_name="Karim Tazi (Client Pro)",
                email="karim.tazi@gmail.com",
                phone_number="+212662000002",
                hashed_password="hashed_pass",
                user_role="renter",
                city="Casablanca",
                is_kyc_verified=True,
                kyc_liveness_score=96.00
            )
            db.add(renter)
            await db.flush()
        renter_id = renter.id

    total_days = (payload.end_date - payload.start_date).days + 1
    daily_base = float(equipment.daily_price_mad)
    discount_pct = calculate_degressive_discount(total_days)
    discounted_daily_rate = daily_base * (1 - discount_pct / 100)
    rental_total = round(discounted_daily_rate * total_days, 2)
    commission = round(rental_total * settings.PLATFORM_COMMISSION_PCT, 2)
    deposit_hold = float(equipment.deposit_amount_mad)

    # 1. Create Booking Record
    booking_uuid = uuid.uuid4()
    new_booking = Booking(
        id=booking_uuid,
        equipment_id=equipment.id,
        renter_id=renter_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        total_days=total_days,
        daily_rate_applied_mad=discounted_daily_rate,
        rental_total_mad=rental_total,
        platform_commission_mad=commission,
        deposit_hold_mad=deposit_hold,
        booking_status="confirmed",
        cmi_status="held",
        contract_pdf_url=f"/api/v1/contracts/{booking_uuid}",
        contract_sha256="7b2a94f1c3098e72ba6301fa38290f9b6910a301db54321fa98bc1948301ec74"
    )
    db.add(new_booking)
    await db.flush()

    # 2. Create CMI Escrow Transaction
    cmi_tx = CMITransaction(
        booking_id=new_booking.id,
        cmi_auth_token=f"CMI_AUTH_{uuid.uuid4().hex[:16].upper()}",
        cmi_trans_id=f"TX_CMI_{uuid.uuid4().hex[:12].upper()}",
        card_brand="CMI / Mastercard Maroc (3D-Secure v2)",
        preauth_amount_mad=deposit_hold,
        captured_amount_mad=0.00,
        deposit_status="held"
    )
    db.add(cmi_tx)
    await db.commit()

    # Re-fetch with relationships
    return await get_booking(new_booking.id, db)

@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: uuid.UUID,
    payload: BookingStatusUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.cmi_transaction))
    )
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    if payload.booking_status:
        booking.booking_status = payload.booking_status
    
    if payload.cmi_status:
        booking.cmi_status = payload.cmi_status
        if booking.cmi_transaction:
            booking.cmi_transaction.deposit_status = payload.cmi_status
            if payload.cmi_status == "released":
                booking.cmi_transaction.released_at = datetime.utcnow()
            elif payload.cmi_status == "captured":
                booking.cmi_transaction.captured_amount_mad = booking.deposit_hold_mad

    await db.commit()
    return await get_booking(booking_id, db)
