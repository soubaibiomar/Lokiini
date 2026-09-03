import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.models import User, Article, Avis
from app.schemas.user_schemas import (
    UserProfileResponse, UserUpdateRequest, PublicUserResponse,
    UserEquipmentSummary, UserReviewSummary
)
from app.routers.auth import get_current_user, get_me, update_me

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs & Profils Publics"])

@router.get("/moi", response_model=UserProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Compatibility path for the authoritative identity profile handler."""
    return await get_me(current_user)

@router.put("/moi", response_model=UserProfileResponse)
async def update_my_profile(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Compatibility path for the authoritative identity profile handler."""
    return await update_me(payload, current_user, db)

@router.get("/{user_id}/profil", response_model=PublicUserResponse)
async def get_public_user_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Consulte le profil public d'un loueur ou locataire (Note, badge Didit, réputation)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_404", "message": "Utilisateur introuvable."}
        )

    # Count active equipment listings
    eq_res = await db.execute(select(Article).where(Article.loueur_id == user_id, Article.statut == "actif"))
    listings = eq_res.scalars().all()

    return PublicUserResponse(
        user_id=user.id,
        nom=user.nom_complet,
        note=float(user.note) if user.note else 5.0,
        badge_verifie=user.statut_verification == "verified",
        date_inscription=user.cree_le,
        temps_reponse_minutes=user.temps_reponse_minutes or 30,
        city=user.city or "Casablanca",
        total_annonces=len(listings)
    )

@router.get("/{user_id}/annonces", response_model=List[UserEquipmentSummary])
async def get_user_listings(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Liste toutes les annonces de matériel publiées par cet utilisateur."""
    result = await db.execute(
        select(Article).where(Article.loueur_id == user_id, Article.statut == "actif").order_by(Article.cree_le.desc())
    )
    articles = result.scalars().all()
    
    return [
        UserEquipmentSummary(
            id=a.id,
            titre=a.titre,
            categorie=a.categorie,
            prix_par_jour=float(a.prix_par_jour),
            montant_caution=float(a.montant_caution),
            photos=a.photos or [],
            statut=a.statut,
            city=a.city
        )
        for a in articles
    ]

@router.get("/{user_id}/avis", response_model=List[UserReviewSummary])
async def get_user_reviews(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Liste les avis et notes reçus par cet utilisateur."""
    result = await db.execute(
        select(Avis).where(Avis.avise_id == user_id).order_by(Avis.cree_le.desc())
    )
    reviews = result.scalars().all()
    
    response = []
    for r in reviews:
        # Fetch reviewer name
        rev_user_res = await db.execute(select(User).where(User.id == r.avisateur_id))
        rev_user = rev_user_res.scalars().first()
        response.append(UserReviewSummary(
            id=r.id,
            note=r.note,
            commentaire=r.commentaire,
            avisateur_nom=rev_user.nom_complet if rev_user else "Utilisateur Lokiini",
            cree_le=r.cree_le
        ))
    return response
