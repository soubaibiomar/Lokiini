import uuid
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_, func

from app.core.database import get_db
from app.models.models import Article, Utilisateur, Reservation, Avis
from app.routers.auth import get_current_user
from app.schemas.schemas import (
    ArticleCreate, ArticleUpdate, ArticleResponse, ArticleSearchQuery, UserPublicProfile
)

router = APIRouter(tags=["Articles & Catalogue"])

# Helper: Auto-detect risk level based on price & deposit
def detecter_niveau_risque(prix_par_jour: float, montant_caution: float) -> str:
    if prix_par_jour >= 400 or montant_caution >= 3000:
        return "eleve"
    elif prix_par_jour >= 150 or montant_caution >= 1000:
        return "moyen"
    return "faible"


# ==============================================================================
# 1. CRÉATION D'ARTICLE / ANNONCE
# ==============================================================================
@router.post("/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
@router.post("/equipment", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def publier_article(
    payload: ArticleCreate,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publie une annonce avec détection automatique du niveau de risque et calcul de caution recommandée."""
    niveau_calcule = detecter_niveau_risque(payload.prix_par_jour, payload.montant_caution or 0)
    
    # Calcul de la caution par défaut si non spécifiée (généralement 5 à 10x le prix journalier)
    caution = payload.montant_caution if payload.montant_caution and payload.montant_caution > 0 else payload.prix_par_jour * 8

    nouvel_article = Article(
        loueur_id=current_user.id,
        categorie=payload.categorie,
        titre=payload.titre,
        description=payload.description,
        photos=payload.photos or ["/images/default_tool.jpg"],
        prix_par_jour=payload.prix_par_jour,
        montant_caution=caution,
        niveau_risque=payload.niveau_risque or niveau_calcule,
        ville=payload.ville or current_user.ville or "Casablanca",
        adresse=payload.adresse or current_user.adresse,
        localisation=payload.localisation or {"lat": 33.5731, "lng": -7.5898},
        calendrier_disponibilite=payload.calendrier_disponibilite or {"dates_bloquees": []},
        specs=payload.specs or {},
        statut="actif"
    )

    db.add(nouvel_article)
    await db.commit()
    await db.refresh(nouvel_article)
    return nouvel_article


# ==============================================================================
# 2. RECHERCHE & LISTE DES ARTICLES (PUBLIC)
# ==============================================================================
@router.get("/articles", response_model=List[ArticleResponse])
@router.get("/equipment", response_model=List[ArticleResponse])
@router.get("/articles/recherche")
async def rechercher_articles(
    q: Optional[str] = Query(None, description="Mot-clé de recherche"),
    categorie: Optional[str] = Query(None, description="Catégorie (outils, electronique, musique, evenementiel, outdoor, velos, btp)"),
    ville: Optional[str] = Query(None, description="Ville marocaine (ex: Casablanca, Rabat, Marrakech)"),
    prix_min: Optional[float] = Query(None, description="Prix min par jour en MAD"),
    prix_max: Optional[float] = Query(None, description="Prix max par jour en MAD"),
    uniquement_verifies: Optional[bool] = Query(False, description="Uniquement loueurs vérifiés Didit"),
    tri_par: Optional[str] = Query("plus_recent", description="Tri: prix_asc, prix_desc, plus_recent"),
    page: int = Query(1, ge=1),
    limite: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Recherche multi-critères dans le catalogue public d'articles sans authentification requise."""
    query = select(Article).where(Article.statut == "actif")

    if q:
        search_pattern = f"%{q}%"
        query = query.where(or_(Article.titre.ilike(search_pattern), Article.description.ilike(search_pattern)))

    if categorie:
        query = query.where(Article.categorie == categorie.lower())

    if ville:
        query = query.where(Article.ville.ilike(f"%{ville}%"))

    if prix_min is not None:
        query = query.where(Article.prix_par_jour >= prix_min)

    if prix_max is not None:
        query = query.where(Article.prix_par_jour <= prix_max)

    # Ordering
    if tri_par == "prix_asc":
        query = query.order_by(Article.prix_par_jour.asc())
    elif tri_par == "prix_desc":
        query = query.order_by(Article.prix_par_jour.desc())
    else:
        query = query.order_by(Article.cree_le.desc())

    offset = (page - 1) * limite
    query = query.offset(offset).limit(limite)

    result = await db.execute(query)
    articles = result.scalars().all()
    return articles


# ==============================================================================
# 3. DÉTAIL D'UN ARTICLE
# ==============================================================================
@router.get("/articles/{article_id}", response_model=ArticleResponse)
@router.get("/equipment/{article_id}", response_model=ArticleResponse)
async def obtenir_article(article_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Fiche détaillée d'un article avec informations du loueur et calcul de caution COD."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    # Incrémenter les vues
    article.nb_vues = (article.nb_vues or 0) + 1
    await db.commit()
    await db.refresh(article)
    return article


# ==============================================================================
# 4. VÉRIFICATION DE DISPONIBILITÉ
# ==============================================================================
@router.get("/articles/{article_id}/disponibilite")
async def verifier_disponibilite(
    article_id: uuid.UUID,
    date_debut: date = Query(..., description="Date début souhaitée"),
    date_fin: date = Query(..., description="Date fin souhaitée"),
    db: AsyncSession = Depends(get_db)
):
    """Vérifie si un article est libre sur la plage de dates demandée."""
    if date_fin < date_debut:
        raise HTTPException(status_code=400, detail="La date de fin doit être postérieure à la date de début.")

    # Check overlapping confirmed bookings
    query = select(Reservation).where(
        Reservation.article_id == article_id,
        Reservation.statut.in_(["confirme_cod", "en_cours", "en_attente_approbation"]),
        Reservation.date_debut <= date_fin,
        Reservation.date_fin >= date_debut
    )
    result = await db.execute(query)
    conflits = result.scalars().all()

    disponible = len(conflits) == 0
    return {
        "article_id": article_id,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "disponible": disponible,
        "nb_reservations_conflit": len(conflits)
    }


# ==============================================================================
# 5. MODIFICATION & SUPPRESSION
# ==============================================================================
@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def modifier_article(
    article_id: uuid.UUID,
    payload: ArticleUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Met à jour une annonce (propriétaire uniquement)."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    if article.loueur_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à modifier cette annonce.")

    if payload.titre is not None:
        article.titre = payload.titre
    if payload.description is not None:
        article.description = payload.description
    if payload.prix_par_jour is not None:
        article.prix_par_jour = payload.prix_par_jour
    if payload.montant_caution is not None:
        article.montant_caution = payload.montant_caution
    if payload.statut is not None:
        article.statut = payload.statut
    if payload.calendrier_disponibilite is not None:
        article.calendrier_disponibilite = payload.calendrier_disponibilite
    if payload.specs is not None:
        article.specs = payload.specs

    article.modifie_le = datetime.utcnow()
    await db.commit()
    await db.refresh(article)
    return article


@router.delete("/articles/{article_id}")
async def archiver_article(
    article_id: uuid.UUID,
    current_user: Utilisateur = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archivage doux d'une annonce."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    if article.loueur_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à supprimer cette annonce.")

    article.statut = "archive"
    article.modifie_le = datetime.utcnow()
    await db.commit()
    return {"statut": "succes", "message": "Annonce archivée avec succès."}


# ==============================================================================
# 6. CATÉGORIES & SUGGESTIONS
# ==============================================================================
@router.get("/categories")
async def lister_categories(db: AsyncSession = Depends(get_db)):
    """Retourne les 6 catégories phares de Lokiini avec le décompte d'articles actifs."""
    categories_def = [
        {"id": "outils", "nom": "Outils & Bricolage", "icone": "Wrench", "description": "Perforateurs, scies, échafaudages, ponceuses", "niveau_risque": "moyen"},
        {"id": "electronique", "nom": "Électronique & Vidéo", "icone": "Camera", "description": "Caméras 4K, drones, éclairage LED, objectifs", "niveau_risque": "eleve"},
        {"id": "musique", "nom": "Instruments de musique", "icone": "Music", "description": "Guitares, claviers, micros, tables de mixage", "niveau_risque": "faible"},
        {"id": "evenementiel", "nom": "Fête & Événementiel", "icone": "Sparkles", "description": "Enceintes sono, chapiteaux, tireuses, lumières", "niveau_risque": "moyen"},
        {"id": "outdoor", "nom": "Outdoor & Camping", "icone": "Compass", "description": "Tentes de toit, paddles, matériel de bivouac", "niveau_risque": "moyen"},
        {"id": "velos", "nom": "Remorques & Vélos", "icone": "Bike", "description": "Remorques porte-motos, vélos électriques, porte-vélos", "niveau_risque": "moyen"}
    ]

    for cat in categories_def:
        res = await db.execute(select(func.count(Article.id)).where(Article.categorie == cat["id"], Article.statut == "actif"))
        cat["nombre_articles"] = res.scalar() or 0

    return categories_def
