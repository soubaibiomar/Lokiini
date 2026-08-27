import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
import httpx
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Equipment, User
from app.schemas.schemas import EquipmentCreate, EquipmentResponse

router = APIRouter(prefix="/equipment", tags=["Catalogue & Équipements"])

class EquipmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    daily_price_mad: Optional[float] = None
    deposit_amount_mad: Optional[float] = None
    is_available: Optional[bool] = None
    discount_pct: Optional[int] = None
    specs_json: Optional[Dict[str, Any]] = None
    images_urls: Optional[List[str]] = None

async def sync_to_meilisearch(item: Equipment):
    """Asynchronously index or update document in Meilisearch."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            headers = {"Authorization": f"Bearer {settings.MEILISEARCH_MASTER_KEY}"}
            doc = {
                "id": str(item.id),
                "title": item.title,
                "description": item.description,
                "category": item.category,
                "city": item.city,
                "daily_price_mad": float(item.daily_price_mad),
                "deposit_amount_mad": float(item.deposit_amount_mad),
                "is_available": item.is_available
            }
            await client.post(
                f"{settings.MEILISEARCH_URL}/indexes/equipment/documents",
                json=[doc],
                headers=headers
            )
    except Exception:
        # Gracefully handle Meilisearch offline in local environments
        pass

@router.get("", response_model=List[EquipmentResponse])
async def list_equipment(
    city: Optional[str] = Query(None, description="Filtrer par ville marocaine (ex: Casablanca, Rabat, Marrakech)"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie (ex: btp, tools, audiovisual, energy, cleaning, heating)"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    max_price: Optional[float] = Query(None, description="Prix journalier maximum en MAD"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Equipment).where(Equipment.is_available == True)
    
    if city and city != "Toutes les villes":
        query = query.where(Equipment.city.ilike(f"%{city}%"))
    if category and category != "all":
        query = query.where(Equipment.category == category)
    if max_price:
        query = query.where(Equipment.daily_price_mad <= max_price)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Equipment.title.ilike(search_pattern)) | 
            (Equipment.description.ilike(search_pattern)) |
            (Equipment.city.ilike(search_pattern))
        )

    result = await db.execute(query.order_by(Equipment.created_at.desc()))
    items = result.scalars().all()
    return items

@router.get("/my-listings", response_model=List[EquipmentResponse])
async def get_my_equipment_listings(
    owner_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    if not owner_id:
        # Default to first pro owner in database
        result_user = await db.execute(select(User).where(User.user_role.in_(["pro_owner", "owner"])).limit(1))
        user = result_user.scalars().first()
        if not user:
            # Fallback to any user
            result_user = await db.execute(select(User).limit(1))
            user = result_user.scalars().first()
        if not user:
            return []
        owner_id = user.id

    result = await db.execute(select(Equipment).where(Equipment.owner_id == owner_id).order_by(Equipment.created_at.desc()))
    return result.scalars().all()

@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(equipment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalars().first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement introuvable."
        )
    return equipment

@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    equipment_in: EquipmentCreate,
    owner_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    if not owner_id:
        result = await db.execute(select(User).where(User.user_role.in_(["pro_owner", "owner"])).limit(1))
        user = result.scalars().first()
        if not user:
            result = await db.execute(select(User).limit(1))
            user = result.scalars().first()
        if not user:
            # Auto create default pro owner if empty
            user = User(
                full_name="Atlas Location BTP Maroc",
                email="contact@atlasbtp.ma",
                phone_number="+212661000001",
                hashed_password="bcrypt_hashed_pass",
                user_role="pro_owner",
                company_name="Atlas Location BTP SARL",
                company_ice="002345678000045",
                city="Casablanca",
                is_kyc_verified=True,
                kyc_liveness_score=98.50
            )
            db.add(user)
            await db.flush()
        owner_id = user.id

    new_equipment = Equipment(
        owner_id=owner_id,
        title=equipment_in.title,
        description=equipment_in.description,
        category=equipment_in.category,
        city=equipment_in.city,
        address=equipment_in.address or f"{equipment_in.city}, Maroc",
        daily_price_mad=equipment_in.daily_price_mad,
        deposit_amount_mad=equipment_in.deposit_amount_mad,
        is_available=equipment_in.is_available if equipment_in.is_available is not None else True,
        is_verified=True,
        discount_pct=equipment_in.discount_pct or 0,
        specs_json=equipment_in.specs_json or {},
        images_urls=equipment_in.images_urls if equipment_in.images_urls else ["https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800"]
    )
    db.add(new_equipment)
    await db.commit()
    await db.refresh(new_equipment)

    await sync_to_meilisearch(new_equipment)
    return new_equipment

@router.patch("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: uuid.UUID,
    equipment_update: EquipmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalars().first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Équipement introuvable.")

    if equipment_update.title is not None:
        equipment.title = equipment_update.title
    if equipment_update.description is not None:
        equipment.description = equipment_update.description
    if equipment_update.category is not None:
        equipment.category = equipment_update.category
    if equipment_update.city is not None:
        equipment.city = equipment_update.city
    if equipment_update.address is not None:
        equipment.address = equipment_update.address
    if equipment_update.daily_price_mad is not None:
        equipment.daily_price_mad = equipment_update.daily_price_mad
    if equipment_update.deposit_amount_mad is not None:
        equipment.deposit_amount_mad = equipment_update.deposit_amount_mad
    if equipment_update.is_available is not None:
        equipment.is_available = equipment_update.is_available
    if equipment_update.discount_pct is not None:
        equipment.discount_pct = equipment_update.discount_pct
    if equipment_update.specs_json is not None:
        equipment.specs_json = equipment_update.specs_json
    if equipment_update.images_urls is not None:
        equipment.images_urls = equipment_update.images_urls

    await db.commit()
    await db.refresh(equipment)
    await sync_to_meilisearch(equipment)
    return equipment

@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(equipment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalars().first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Équipement introuvable.")

    await db.delete(equipment)
    await db.commit()
    return None
