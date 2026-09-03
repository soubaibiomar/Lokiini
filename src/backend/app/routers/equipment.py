import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import case, false, func, or_, text
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Article, Avis, Equipment, User
from app.schemas.equipment_schemas import (
    EquipmentCreateRequest, EquipmentUpdateRequest,
    EquipmentResponse, CategoryCountResponse
)
from app.services.risk_service import risk_service
from app.services.geo_search_service import geo_search_service
from app.services.meilisearch_service import meilisearch_service
from app.routers.auth import get_current_user

router = APIRouter(tags=["Catalogue Matériel & Recherche Géospatiale PostGIS"])

EQUIPMENT_IMAGE_TYPES = {
    "image/jpeg": (".jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/png": (".png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": (".webp", lambda data: data.startswith(b"RIFF") and data[8:12] == b"WEBP"),
}

# 1. Catégories phares avec compteurs
@router.get("/articles/categories", response_model=List[CategoryCountResponse])
@router.get("/equipment/categories", response_model=List[CategoryCountResponse])
async def get_equipment_categories(db: AsyncSession = Depends(get_db)):
    """Liste les catégories de matériel phares avec les compteurs d'articles actifs."""
    labels = {
        "tools": "Outils & Bricolage",
        "btp": "BTP & Chantier",
        "audiovisuel": "Électronique & Vidéo",
        "evenementiel": "Fête & Événementiel",
        "outdoor": "Outdoor & Camping",
        "cleaning": "Nettoyage & Entretien",
    }
    res = await db.execute(
        text("""
            SELECT categorie, COUNT(*) AS count
            FROM articles
            WHERE statut = 'actif' AND is_available IS TRUE
            GROUP BY categorie
            ORDER BY count DESC, categorie ASC
        """)
    )
    return [
        CategoryCountResponse(
            categorie=row.categorie,
            nom_affiche=labels.get(row.categorie, row.categorie.replace("_", " ").title()),
            icone=row.categorie,
            total_articles=row.count,
        )
        for row in res.fetchall()
    ]

# 2. Recherche géolocalisée par rayon PostGIS
@router.get("/articles/recherche/geo")
@router.get("/equipment/recherche/geo")
async def search_equipment_geo(
    lat: float = Query(..., description="Latitude GPS"),
    lng: float = Query(..., description="Longitude GPS"),
    radius_km: float = Query(25.0, ge=1, le=200, description="Rayon de recherche en km"),
    q: Optional[str] = Query(None, description="Recherche textuelle"),
    categorie: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    prix_min: Optional[float] = Query(None),
    prix_max: Optional[float] = Query(None),
    disponible: bool = Query(True),
    verifie: bool = Query(False),
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
        q=q,
        categorie=categorie,
        city=city,
        prix_min=prix_min,
        prix_max=prix_max,
        disponible=disponible,
        verifie=verifie,
        limit=limit,
        offset=offset
    )
    total = int(results[0].pop("total_count")) if results else 0
    return {"statut": "succes", "total": total, "donnees": results}

# 3. Liste filtrée des articles / annonces
@router.get("/articles")
@router.get("/equipment")
async def list_equipment(
    q: Optional[str] = Query(None, description="Recherche textuelle"),
    categorie: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    prix_min: Optional[float] = Query(None),
    prix_max: Optional[float] = Query(None),
    disponible: bool = Query(True),
    verifie: bool = Query(False),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """Liste filtrée des annonces de matériel avec pagination et filtres."""
    conditions = [Article.statut == "actif"]

    if categorie:
        conditions.append(Article.categorie == categorie)
    if city:
        conditions.append(Article.city.ilike(f"%{city}%"))
    if prix_min is not None:
        conditions.append(Article.prix_par_jour >= prix_min)
    if prix_max is not None:
        conditions.append(Article.prix_par_jour <= prix_max)
    if disponible:
        conditions.append(Article.is_available.is_(True))
    if verifie:
        conditions.append(User.statut_verification == "verified")

    relevance_order = None
    if q:
        meilisearch_ids = await meilisearch_service.search_articles(q, limit=100)
        if meilisearch_ids is None:
            conditions.append(or_(Article.titre.ilike(f"%{q}%"), Article.description.ilike(f"%{q}%")))
        elif not meilisearch_ids:
            conditions.append(false())
        else:
            ranked_ids = []
            for article_id in meilisearch_ids:
                try:
                    ranked_ids.append(uuid.UUID(article_id))
                except (TypeError, ValueError, AttributeError):
                    continue
            if not ranked_ids:
                conditions.append(false())
            else:
                conditions.append(Article.id.in_(ranked_ids))
                relevance_order = case(
                    {article_id: rank for rank, article_id in enumerate(ranked_ids)},
                    value=Article.id,
                    else_=len(ranked_ids),
                )

    count_query = select(func.count(Article.id)).join(User, User.id == Article.loueur_id).where(*conditions)
    total = int((await db.execute(count_query)).scalar_one())

    query = select(Article, User).join(User, User.id == Article.loueur_id).where(*conditions)
    query = query.order_by(relevance_order, Article.cree_le.desc()) if relevance_order is not None else query.order_by(Article.cree_le.desc())
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    rows = result.all()

    response_items = []
    for a, loueur in rows:
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
            "is_available": bool(a.is_available),
            "is_verified": bool(a.is_verified),
            "discount_pct": int(a.discount_pct or 0),
            "loueur_nom": loueur.nom_complet,
            "loueur_statut_kyc": loueur.statut_verification,
            "cree_le": a.cree_le.isoformat() if a.cree_le else None
        })

    return {"statut": "succes", "total": total, "donnees": response_items}

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
    return [{
        "id": str(article.id),
        "loueur_id": str(article.loueur_id),
        "titre": article.titre,
        "description": article.description,
        "categorie": article.categorie,
        "prix_par_jour": float(article.prix_par_jour),
        "montant_caution": float(article.montant_caution),
        "photos": article.photos or [],
        "specs": article.specs or {},
        "calendrier_disponibilite": article.calendrier_disponibilite or {},
        "city": article.city,
        "statut": article.statut,
        "is_available": bool(article.is_available),
        "is_verified": bool(article.is_verified),
        "cree_le": article.cree_le.isoformat() if article.cree_le else None,
    } for article in articles]


@router.post("/articles/photos", status_code=status.HTTP_201_CREATED)
async def upload_equipment_photo(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Store one authenticated owner's raster listing photo in durable media storage."""
    image_type = EQUIPMENT_IMAGE_TYPES.get((photo.content_type or "").lower())
    if not image_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={"code": "EQUIPMENT_PHOTO_TYPE_UNSUPPORTED", "message": "Formats acceptés : JPEG, PNG ou WebP."},
        )

    extension, signature_matches = image_type
    media_directory = Path(settings.EQUIPMENT_MEDIA_DIR).resolve()
    media_directory.mkdir(parents=True, exist_ok=True)
    filename = f"{current_user.id}_{uuid.uuid4().hex}{extension}"
    target = (media_directory / filename).resolve()
    if target.parent != media_directory:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide.")

    total_bytes = 0
    first_bytes = b""
    try:
        with target.open("wb") as destination:
            while chunk := await photo.read(1024 * 1024):
                if not first_bytes:
                    first_bytes = chunk[:16]
                total_bytes += len(chunk)
                if total_bytes > settings.EQUIPMENT_MEDIA_MAX_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail={"code": "EQUIPMENT_PHOTO_TOO_LARGE", "message": "La photo dépasse la taille maximale autorisée."},
                    )
                destination.write(chunk)
        if not first_bytes or not signature_matches(first_bytes):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={"code": "EQUIPMENT_PHOTO_CONTENT_INVALID", "message": "Le contenu du fichier ne correspond pas à une image valide."},
            )
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        await photo.close()

    return {
        "filename": filename,
        "url": f"{settings.API_V1_STR}/media/equipment/{filename}",
        "content_type": photo.content_type,
        "size_bytes": total_bytes,
    }


@router.delete("/articles/photos/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment_photo(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """Remove an uploaded photo only when it belongs to the authenticated owner."""
    if Path(filename).name != filename or not filename.startswith(f"{current_user.id}_"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Suppression de photo interdite.")
    media_directory = Path(settings.EQUIPMENT_MEDIA_DIR).resolve()
    target = (media_directory / filename).resolve()
    if target.parent != media_directory:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide.")
    target.unlink(missing_ok=True)


@router.get("/media/equipment/{filename}", include_in_schema=False)
async def get_equipment_photo(filename: str):
    """Serve public listing media using immutable filenames."""
    if Path(filename).name != filename:
        raise HTTPException(status_code=404, detail="Photo introuvable.")
    media_directory = Path(settings.EQUIPMENT_MEDIA_DIR).resolve()
    target = (media_directory / filename).resolve()
    if target.parent != media_directory or not target.is_file():
        raise HTTPException(status_code=404, detail="Photo introuvable.")
    return FileResponse(target, headers={"Cache-Control": "public, max-age=31536000, immutable"})

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

    # Récupération du profil public et des signaux de confiance réels du loueur.
    loueur_res = await db.execute(select(User).where(User.id == article.loueur_id))
    loueur = loueur_res.scalars().first()
    review_stats = await db.execute(
        select(func.count(Avis.id), func.avg(Avis.note)).where(Avis.avise_id == article.loueur_id)
    )
    review_count, review_average = review_stats.one()
    listing_count = int((await db.execute(
        select(func.count(Article.id)).where(
            Article.loueur_id == article.loueur_id,
            Article.statut == "actif",
        )
    )).scalar_one())

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
        "calendrier_disponibilite": article.calendrier_disponibilite or {},
        "city": article.city,
        "adresse_approximative": article.adresse_approximative,
        "statut": article.statut,
        "is_available": bool(article.is_available),
        "is_verified": bool(article.is_verified),
        "discount_pct": int(article.discount_pct or 0),
        "loueur": {
            "id": str(loueur.id) if loueur else None,
            "nom": loueur.nom_complet if loueur else "Profil indisponible",
            "avatar_url": loueur.avatar_url if loueur else None,
            "note": round(float(review_average), 1) if review_average is not None else None,
            "nombre_avis": int(review_count or 0),
            "badge_verifie": loueur.statut_verification == "verified" if loueur else False,
            "date_inscription": loueur.cree_le.isoformat() if loueur and loueur.cree_le else None,
            "total_annonces": listing_count,
            "company_name": loueur.company_name if loueur else None,
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
    point_wkt = (
        f"SRID=4326;POINT({payload.lng} {payload.lat})"
        if payload.lat is not None and payload.lng is not None
        else None
    )

    article = Article(
        id=new_id,
        loueur_id=current_user.id,
        titre=payload.titre,
        description=payload.description,
        categorie=payload.categorie,
        prix_par_jour=payload.prix_par_jour,
        montant_caution=payload.montant_caution,
        niveau_risque=risk_info["niveau_risque"],
        photos=payload.photos or [],
        specs_json=payload.specs or {},
        calendrier_disponibilite=payload.calendrier_disponibilite or {},
        is_available=payload.is_available,
        localisation=point_wkt,
        city=payload.city or "Casablanca",
        adresse=payload.adresse_approximative or f"Quartier {payload.city or 'Casablanca'}",
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
    if payload.montant_caution is not None: article.montant_caution = payload.montant_caution
    if payload.photos is not None: article.photos = payload.photos
    if payload.specs is not None: article.specs_json = payload.specs
    if payload.statut is not None: article.statut = payload.statut
    if payload.city is not None: article.city = payload.city
    if payload.adresse_approximative is not None: article.adresse = payload.adresse_approximative
    if payload.is_available is not None: article.is_available = payload.is_available
    if payload.calendrier_disponibilite is not None: article.calendrier_disponibilite = payload.calendrier_disponibilite

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
