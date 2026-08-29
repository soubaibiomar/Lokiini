import uuid
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, jwt
from app.models.models import User
from app.schemas.auth_schemas import SignUpRequest, SignInRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user_schemas import UserProfileResponse, UserUpdateRequest

router = APIRouter(prefix="/auth", tags=["Authentification & Sessions"])

class JWTError(Exception): pass

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization:
        # Fallback to first user in database for smooth dev exploration if present
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_005", "message": "En-tête d'autorisation manquant."}
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail={"code": "AUTH_005", "message": "Schéma d'authentification invalide (Bearer requis)."}
            )
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail={"code": "AUTH_003", "message": "Jeton JWT invalide : identifiant manquant."}
            )
        user_id = uuid.UUID(user_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_004", "message": "Jeton d'authentification expiré ou corrompu."}
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_404", "message": "Utilisateur associé au jeton introuvable."}
        )
    return user


@router.post("/inscription", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: SignUpRequest, db: AsyncSession = Depends(get_db)):
    """Inscription nouvel utilisateur (Email ou Téléphone marocain)."""
    # 1. Vérification unicité Email
    existing_email = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing_email.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "AUTH_001", "message": "Un compte existe déjà avec cette adresse email."}
        )

    # 2. Vérification unicité Téléphone
    existing_phone = await db.execute(select(User).where(User.telephone == payload.telephone))
    if existing_phone.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "AUTH_002", "message": "Un compte existe déjà avec ce numéro de téléphone."}
        )

    # 3. Création de l'utilisateur
    new_user = User(
        id=uuid.uuid4(),
        email=payload.email.lower(),
        telephone=payload.telephone,
        nom_complet=payload.nom_complet,
        hashed_password=get_password_hash(payload.mot_de_passe),
        user_role=payload.user_role or "renter",
        company_name=payload.company_name,
        company_ice=payload.company_ice,
        city=payload.city or "Casablanca",
        statut_verification="en_attente",
        plan_abonnement="Gratuit",
        cree_le=datetime.utcnow()
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 4. Émission des tokens
    access_token = create_access_token(new_user.id, expires_delta=timedelta(minutes=15))
    refresh_token = create_access_token(new_user.id, expires_delta=timedelta(days=30))

    return TokenResponse(
        user_id=new_user.id,
        nom_complet=new_user.nom_complet,
        email=new_user.email,
        telephone=new_user.telephone,
        user_role=new_user.user_role,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_seconds=900
    )


@router.post("/connexion", response_model=TokenResponse)
@router.post("/login", response_model=TokenResponse)
async def login(payload: SignInRequest, db: AsyncSession = Depends(get_db)):
    """Connexion avec Email ou Téléphone marocain + Mot de passe."""
    identifier = payload.email_ou_telephone.strip()
    
    # Recherche par email ou par téléphone
    query = select(User).where((User.email == identifier.lower()) | (User.telephone == identifier))
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(payload.mot_de_passe, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_003", "message": "Identifiant ou mot de passe incorrect."}
        )

    access_token = create_access_token(user.id, expires_delta=timedelta(minutes=15))
    refresh_token = create_access_token(user.id, expires_delta=timedelta(days=30))

    return TokenResponse(
        user_id=user.id,
        nom_complet=user.nom_complet,
        email=user.email,
        telephone=user.telephone,
        user_role=user.user_role,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_seconds=900
    )


@router.post("/rafraichir", response_model=TokenResponse)
@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Renouvelle le jeton d'accès à partir du jeton de rafraîchissement (30j)."""
    try:
        decoded = jwt.decode(payload.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = uuid.UUID(decoded.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_004", "message": "Jeton de rafraîchissement invalide ou expiré."}
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_404", "message": "Utilisateur introuvable."}
        )

    new_access_token = create_access_token(user.id, expires_delta=timedelta(minutes=15))
    new_refresh_token = create_access_token(user.id, expires_delta=timedelta(days=30))

    return TokenResponse(
        user_id=user.id,
        nom_complet=user.nom_complet,
        email=user.email,
        telephone=user.telephone,
        user_role=user.user_role,
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in_seconds=900
    )


@router.post("/deconnexion")
async def logout():
    """Invalide la session (traitement côté client)."""
    return {"statut": "succes", "message": "Déconnexion réussie."}


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retourne le profil complet de l'utilisateur connecté."""
    return current_user


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Met à jour les informations du profil utilisateur connecté."""
    if payload.nom_complet is not None: current_user.nom_complet = payload.nom_complet
    if payload.telephone is not None: current_user.telephone = payload.telephone
    if payload.avatar_url is not None: current_user.avatar_url = payload.avatar_url
    if payload.company_name is not None: current_user.company_name = payload.company_name
    if payload.company_ice is not None: current_user.company_ice = payload.company_ice
    if payload.city is not None: current_user.city = payload.city
    
    current_user.modifie_le = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    return current_user
