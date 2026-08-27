import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, Token
from pydantic import BaseModel
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["Authentification & Profils"])

class LoginRequest(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    company_name: Optional[str] = None
    company_ice: Optional[str] = None
    user_role: Optional[str] = None

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization:
        # Fallback to first user in database for smooth dev exploration
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="En-tête d'autorisation manquant."
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Schéma d'authentification invalide.")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token JWT invalide.")
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification expiré ou corrompu."
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cette adresse e-mail existe déjà."
        )

    result = await db.execute(select(User).where(User.phone_number == user_in.phone_number))
    existing_phone = result.scalars().first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec ce numéro de téléphone existe déjà."
        )

    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        hashed_password=get_password_hash(user_in.password),
        city=user_in.city or "Casablanca",
        user_role=user_in.user_role or "renter",
        company_name=user_in.company_name,
        company_ice=user_in.company_ice,
        is_kyc_verified=False,
        kyc_liveness_score=0.00
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login_user(login_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalars().first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides (e-mail ou mot de passe incorrect)."
        )

    token = create_access_token(subject=str(user.id))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone_number is not None:
        current_user.phone_number = user_update.phone_number
    if user_update.city is not None:
        current_user.city = user_update.city
    if user_update.company_name is not None:
        current_user.company_name = user_update.company_name
    if user_update.company_ice is not None:
        current_user.company_ice = user_update.company_ice
    if user_update.user_role is not None:
        current_user.user_role = user_update.user_role

    await db.commit()
    await db.refresh(current_user)
    return current_user
