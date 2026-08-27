import uuid
from typing import Optional, List, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import Utilisateur, Article, Avis
from app.schemas.schemas import (
    UserCreate, UserResponse, UserLogin, UserProfileUpdate, 
    UserPublicProfile, Token
)

router = APIRouter(tags=["Authentification & Profils"])

# Dependency: Get current authenticated user
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Utilisateur:
    if not authorization:
        # Dev fallback: return first demo user if no bearer token passed
        result = await db.execute(select(Utilisateur).limit(1))
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="En-tête d'autorisation manquant (Bearer Token requis)."
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

    result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return user


# ==============================================================================
# AUTH ROUTES
# ==============================================================================

@router.post("/auth/inscription", response_model=Token, status_code=status.HTTP_201_CREATED)
@router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def inscription(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Crée un nouvel utilisateur dans Lokiini avec redirection automatique vers le flux KYC."""
    # Check existing email
    res_email = await db.execute(select(Utilisateur).where(Utilisateur.email == payload.email))
    if res_email.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cette adresse email existe déjà."
        )

    # Check existing phone
    res_phone = await db.execute(select(Utilisateur).where(Utilisateur.telephone == payload.telephone))
    if res_phone.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce numéro de téléphone est déjà associé à un autre compte."
        )

    new_user = Utilisateur(
        email=payload.email,
        telephone=payload.telephone,
        hashed_password=get_password_hash(payload.mot_de_passe),
        nom_complet=payload.nom_complet,
        ville=payload.ville or "Casablanca",
        role=payload.role or "particulier",
        company_name=payload.company_name,
        company_ice=payload.company_ice,
        statut_verification="en_attente",
        plan_abonnement="Gratuit",
        note=5.00
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_access_token(data={"sub": str(new_user.id)}, expires_delta=timedelta(days=30))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=new_user
    )


@router.post("/auth/connexion", response_model=Token)
@router.post("/auth/login", response_model=Token)
async def connexion(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Connexion utilisateur par Email ou Numéro de Téléphone marocain."""
    query = select(Utilisateur).where(
        (Utilisateur.email == payload.email_ou_telephone) | 
        (Utilisateur.telephone == payload.email_ou_telephone)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(payload.mot_de_passe, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides (Email/Téléphone ou mot de passe incorrect)."
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(days=30))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user
    )


@router.post("/auth/rafraichir")
@router.post("/auth/refresh")
async def rafraichir_token(refresh_token: str):
    """Rafraîchit l'access token avec le refresh token longue durée."""
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Refresh token invalide.")
        new_token = create_access_token(data={"sub": user_id_str})
        return {"access_token": new_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token expiré ou corrompu.")


@router.post("/auth/deconnexion")
async def deconnexion():
    """Invalide la session côté client."""
    return {"statut": "succes", "message": "Déconnexion réussie."}


# ==============================================================================
# UTILISATEURS / PROFILS ROUTES
# ==============================================================================

@router.get("/utilisateurs/moi", response_model=UserResponse)
@router.get("/auth/me", response_model=UserResponse)
async def obtenir_mon_profil(current_user: Utilisateur = Depends(get_current_user)):
    """Retourne le profil complet de l'utilisateur connecté."""
    return current_user


@router.put("/utilisateurs/moi", response_model=UserResponse)
@router.put("/auth/me", response_model=UserResponse)
async def mettre_a_jour_profil(
    payload: UserProfileUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Met à jour les informations du profil utilisateur."""
    if payload.nom_complet is not None:
        current_user.nom_complet = payload.nom_complet
    if payload.telephone is not None:
        current_user.telephone = payload.telephone
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    if payload.adresse is not None:
        current_user.adresse = payload.adresse
    if payload.ville is not None:
        current_user.ville = payload.ville
    if payload.company_name is not None:
        current_user.company_name = payload.company_name
    if payload.company_ice is not None:
        current_user.company_ice = payload.company_ice

    current_user.modifie_le = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/utilisateurs/{user_id}/profil", response_model=UserPublicProfile)
async def profil_public_utilisateur(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retourne le profil public d'un loueur ou locataire (pour la page article ou avis)."""
    result = await db.execute(select(Utilisateur).where(Utilisateur.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    return UserPublicProfile(
        id=user.id,
        nom=user.nom_complet,
        note=float(user.note or 5.0),
        badge_verifie=user.statut_verification == "approuve",
        date_inscription=user.date_inscription or user.cree_le,
        temps_reponse=f"< {user.temps_reponse_minutes} min"
    )


@router.get("/utilisateurs/{user_id}/annonces")
async def annonces_utilisateur(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retourne toutes les annonces actives publiées par cet utilisateur."""
    result = await db.execute(
        select(Article)
        .where(Article.loueur_id == user_id, Article.statut == "actif")
        .order_by(Article.cree_le.desc())
    )
    articles = result.scalars().all()
    return [{"id": a.id, "titre": a.titre, "categorie": a.categorie, "prix": float(a.prix_par_jour), "photos": a.photos, "statut": a.statut} for a in articles]


@router.get("/utilisateurs/{user_id}/avis")
async def avis_utilisateur(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retourne les avis reçus par cet utilisateur."""
    result = await db.execute(
        select(Avis)
        .where(Avis.avise_id == user_id)
        .order_by(Avis.cree_le.desc())
    )
    avis_list = result.scalars().all()
    return [{"id": av.id, "note": av.note, "commentaire": av.commentaire, "cree_le": av.cree_le} for av in avis_list]
