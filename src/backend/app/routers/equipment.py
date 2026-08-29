import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from app.core.database import get_db
from app.models.models import Article, Equipment, User
from app.schemas.equipment_schemas import (
    EquipmentCreateRequest, EquipmentUpdateRequest,
    EquipmentResponse, CategoryCountResponse
)
from app.services.risk_service import risk_service
from app.services.geo_search_service import geo_search_service
from app.services.meilisearch_service import meilisearch_service
from app.routers.auth import get_current_user

router = APIRouter(tags=["Catalogue Matériel & Recherche Géospatiale PostGIS"])

# 1. Catégories phares avec compteurs
@router.get("/articles/categories", response_model=List[CategoryCountResponse])
@router.get("/equipment/categories", response_model=List[CategoryCountResponse])
async def get_equipment_categories(db: AsyncSession = Depends(get_db)):
    """Liste les catégories de matériel phares avec les compteurs d'articles actifs."""
    categories_meta = [
        {"categorie": "tools", "nom_affiche": "Outils & Bricolage", "icone": "🛠️"},
        {"categorie": "btp", "nom_affiche": "BTP & Chantier", "icone": "🏗️"},
        {"categorie": "audiovisuel", "nom_affiche": "Électronique & Vidéo", "icone": "📷"},
        {"categorie": "evenementiel", "nom_affiche": "Fête & Événementiel", "icone": "🎉"},
        {"categorie": "outdoor", "nom_affiche": "Outdoor & Camping", "icone": "🏕️"},
        {"categorie": "cleaning", "nom_affiche": "Nettoyage & Entretien", "icone": "✨"},
    ]
    
    counts = {}
    try:
        res = await db.execute(
            text("SELECT categorie, COUNT(*) as count FROM articles WHERE statut = 'actif' GROUP BY categorie")
        )
        for row in res.fetchall():
            counts[row[0]] = row[1]
    except Exception:
        pass
        
    return [
        CategoryCountResponse(
            categorie=c["categorie"],
            nom_affiche=c["nom_affiche"],
            icone=c["icone"],
            total_articles=counts.get(c["categorie"], 2) # fallback
        )
        for c in categories_meta
    ]

# 2. Recherche géolocalisée par rayon PostGIS
@router.get("/articles/recherche/geo")
@router.get("/equipment/recherche/geo")
async def search_equipment_geo(
    lat: float = Query(..., description="Latitude GPS"),
    lng: float = Query(..., description="Longitude GPS"),
    radius_km: float = Query(25.0, description="Rayon de recherche en km"),
    categorie: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    prix_min: Optional[float] = Query(None),
    prix_max: Optional[float] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """Recherche d'équipements géolocalisés par proximité géographique exacte (ST_DistanceSphere)."""
    results = await geo_search_service.search_nearby(
        db=db,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        categorie=categorie,
        city=city,
        prix_min=prix_min,
        prix_max=prix_max,
        limit=limit,
        offset=offset
    )
    return {"statut": "succes", "total": len(results), "donnees": results}

# 3. Liste filtrée des articles / annonces
@router.get("/articles")
@router.get("/equipment")
async def list_equipment(
    q: Optional[str] = Query(None, description="Recherche textuelle"),
    categorie: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    prix_min: Optional[float] = Query(None),
    prix_max: Optional[float] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """Liste filtrée des annonces de matériel avec pagination et filtres."""
    query = select(Article).where(Article.statut == "actif")

    if categorie:
        query = query.where(Article.categorie == categorie)
    if city:
        query = query.where(Article.city.ilike(f"%{city}%"))
    if prix_min is not None:
        query = query.where(Article.prix_par_jour >= prix_min)
    if prix_max is not None:
        query = query.where(Article.prix_par_jour <= prix_max)
    if q:
        query = query.where((Article.titre.ilike(f"%{q}%")) | (Article.description.ilike(f"%{q}%")))

    query = query.order_by(Article.cree_le.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    articles = result.scalars().all()

    response_items = []
    for a in articles:
        # Get loueur details
        loueur_res = await db.execute(select(User).where(User.id == a.loueur_id))
        loueur = loueur_res.scalars().first()
        
        response_items.append({
            "id": str(a.id),
            "loueur_id": str(a.loueur_id),
            "titre": a.titre,
            "description": a.description,
            "categorie": a.categorie,
            "prix_par_jour": float(a.prix_par_jour),
            "prix_par_semaine": float(a.prix_par_semaine) if a.prix_par_semaine else None,
            "prix_par_mois": float(a.prix_par_mois) if a.prix_par_mois else None,
            "montant_caution": float(a.montant_caution),
            "mode_caution": a.mode_caution or "cash",
            "niveau_risque": a.niveau_risque or "faible",
            "kyc_requis": a.kyc_requis if a.kyc_requis is not None else False,
            "photos": a.photos or [],
            "specs": a.specs or {},
            "city": a.city or "Casablanca",
            "adresse_approximative": a.adresse_approximative,
            "statut": a.statut,
            "loueur_nom": loueur.nom_complet if loueur else "Loueur Lokiini",
            "loueur_note": float(loueur.note) if loueur and loueur.note else 5.0,
            "loueur_statut_kyc": loueur.statut_verification if loueur else "en_attente",
            "cree_le": a.cree_le.isoformat() if a.cree_le else None
        })

    return {"statut": "succes", "total": len(response_items), "donnees": response_items}

# 4. Mes annonces (Loueur connecté)
@router.get("/articles/my-listings")
@router.get("/equipment/my-listings")
async def get_my_listings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Récupère toutes les annonces publiées par l'utilisateur connecté."""
    result = await db.execute(
        select(Article).where(Article.loueur_id == current_user.id, Article.statut != "archive").order_by(Article.cree_le.desc())
    )
    articles = result.scalars().all()
    return articles

# 5. Détail d'une annonce
@router.get("/articles/{article_id}")
@router.get("/equipment/{equipment_id}")
async def get_equipment_detail(
    article_id: Optional[uuid.UUID] = None,
    equipment_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """Consulte la fiche détaillée complète d'un équipement."""
    target_id = article_id or equipment_id
    result = await db.execute(select(Article).where(Article.id == target_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EQUIPMENT_404", "message": "Annonce de matériel introuvable."}
        )

    # Récupération profil loueur
    loueur_res = await db.execute(select(User).where(User.id == article.loueur_id))
    loueur = loueur_res.scalars().first()

    return {
        "id": str(article.id),
        "loueur_id": str(article.loueur_id),
        "titre": article.titre,
        "description": article.description,
        "categorie": article.categorie,
        "prix_par_jour": float(article.prix_par_jour),
        "prix_par_semaine": float(article.prix_par_semaine) if article.prix_par_semaine else None,
        "prix_par_mois": float(article.prix_par_mois) if article.prix_par_mois else None,
        "montant_caution": float(article.montant_caution),
        "mode_caution": article.mode_caution or "cash",
        "niveau_risque": article.niveau_risque or "faible",
        "kyc_requis": bool(article.kyc_requis),
        "photos": article.photos or [],
        "specs": article.specs or {},
        "city": article.city,
        "adresse_approximative": article.adresse_approximative,
        "statut": article.statut,
        "loueur": {
            "id": str(loueur.id) if loueur else None,
            "nom": loueur.nom_complet if loueur else "Loueur Lokiini",
            "note": float(loueur.note) if loueur and loueur.note else 5.0,
            "badge_verifie": loueur.statut_verification == "approuve" if loueur else False,
            "temps_reponse_minutes": loueur.temps_reponse_minutes if loueur else 30
        },
        "cree_le": article.cree_le.isoformat() if article.cree_le else None
    }

# 6. Création d'une annonce
@router.post("/articles", status_code=status.HTTP_201_CREATED)
@router.post("/equipment", status_code=status.HTTP_201_CREATED)
async def create_equipment(
    payload: EquipmentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publie une nouvelle annonce de matériel avec calcul automatique du risque et point PostGIS."""
    # 1. Évaluation automatique du risque via RiskService
    risk_info = risk_service.evaluate_risk(
        categorie=payload.categorie,
        prix_par_jour=payload.prix_par_jour,
        montant_caution=payload.montant_caution,
        specs=payload.specs
    )

    new_id = uuid.uuid4()
    # 2. Assignation coordonnées WKT PostGIS
    point_wkt = f"SRID=4326;POINT({payload.lng} {payload.lat})"

    article = Article(
        id=new_id,
        loueur_id=current_user.id,
        titre=payload.titre,
        description=payload.description,
        categorie=payload.categorie,
        prix_par_jour=payload.prix_par_jour,
        prix_par_semaine=payload.prix_par_semaine,
        prix_par_mois=payload.prix_par_mois,
        montant_caution=payload.montant_caution,
        mode_caution=payload.mode_caution or ("cash" if risk_info["caution_obligatoire"] else "non_requis"),
        niveau_risque=risk_info["niveau_risque"],
        kyc_requis=risk_info["kyc_obligatoire"],
        photos=payload.photos or [],
        specs=payload.specs or {},
        coordonnees=point_wkt,
        city=payload.city or "Casablanca",
        adresse_approximative=payload.adresse_approximative or f"Quartier {payload.city}",
        statut="actif",
        cree_le=datetime.utcnow()
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)

    # 3. Synchronisation asynchrone Meilisearch
    await meilisearch_service.index_article({
        "id": str(article.id),
        "titre": article.titre,
        "description": article.description,
        "categorie": article.categorie,
        "prix_par_jour": article.prix_par_jour,
        "city": article.city,
        "niveau_risque": article.niveau_risque
    })

    return {
        "statut": "succes",
        "message": "Annonce publiée avec succès.",
        "article_id": str(article.id),
        "niveau_risque": article.niveau_risque,
        "kyc_requis": article.kyc_requis
    }

# 7. Mise à jour d'une annonce
@router.put("/articles/{article_id}")
@router.patch("/equipment/{equipment_id}")
async def update_equipment(
    payload: EquipmentUpdateRequest,
    article_id: Optional[uuid.UUID] = None,
    equipment_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Met à jour une annonce existante."""
    target_id = article_id or equipment_id
    result = await db.execute(select(Article).where(Article.id == target_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Annonce introuvable.")

    if article.loueur_id != current_user.id and current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à modifier cette annonce.")

    if payload.titre is not None: article.titre = payload.titre
    if payload.description is not None: article.description = payload.description
    if payload.categorie is not None: article.categorie = payload.categorie
    if payload.prix_par_jour is not None: article.prix_par_jour = payload.prix_par_jour
    if payload.prix_par_semaine is not None: article.prix_par_semaine = payload.prix_par_semaine
    if payload.prix_par_mois is not None: article.prix_par_mois = payload.prix_par_mois
    if payload.montant_caution is not None: article.montant_caution = payload.montant_caution
    if payload.mode_caution is not None: article.mode_caution = payload.mode_caution
    if payload.photos is not None: article.photos = payload.photos
    if payload.specs is not None: article.specs = payload.specs
    if payload.statut is not None: article.statut = payload.statut
    if payload.city is not None: article.city = payload.city
    if payload.adresse_approximative is not None: article.adresse_approximative = payload.adresse_approximative

    article.modifie_le = datetime.utcnow()
    await db.commit()
    await db.refresh(article)

    # Réindexation Meilisearch
    await meilisearch_service.index_article({
        "id": str(article.id),
        "titre": article.titre,
        "description": article.description,
        "categorie": article.categorie,
        "prix_par_jour": article.prix_par_jour,
        "city": article.city,
        "niveau_risque": article.niveau_risque
    })

    return {"statut": "succes", "message": "Annonce mise à jour avec succès."}

# 8. Archivage logique
@router.delete("/articles/{article_id}")
@router.delete("/equipment/{equipment_id}")
async def archive_equipment(
    article_id: Optional[uuid.UUID] = None,
    equipment_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archivage logique de sécurité (statut = 'archive')."""
    target_id = article_id or equipment_id
    result = await db.execute(select(Article).where(Article.id == target_id))
    article = result.scalars().first()
    if not article:
        raise HTTPException(status_code=404, detail="Annonce introuvable.")

    if article.loueur_id != current_user.id and current_user.user_role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé.")

    article.statut = "archive"
    article.modifie_le = datetime.utcnow()
    await db.commit()

    # Retrait de Meilisearch
    await meilisearch_service.remove_article(str(article.id))

    return {"statut": "succes", "message": "Annonce archivée avec succès."}
