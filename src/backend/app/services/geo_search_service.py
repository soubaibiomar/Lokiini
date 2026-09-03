import math
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Pure distance helper retained for diagnostics and tests."""
    radius = 6371.0
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(delta_lon / 2) ** 2
    )
    return round(radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value)), 2)


class GeoSearchService:
    @staticmethod
    async def search_nearby(
        db: AsyncSession,
        lat: float,
        lng: float,
        radius_km: float = 25.0,
        q: Optional[str] = None,
        categorie: Optional[str] = None,
        city: Optional[str] = None,
        prix_min: Optional[float] = None,
        prix_max: Optional[float] = None,
        disponible: bool = True,
        verifie: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Search active equipment by the current PostGIS Article schema."""
        distance_expression = """
            ST_DistanceSphere(
                a.localisation,
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
            ) / 1000.0
        """
        sql = f"""
            SELECT
                a.id, a.loueur_id, a.titre, a.description, a.categorie,
                a.prix_par_jour, a.montant_caution, a.niveau_risque,
                a.photos, a.specs_json AS specs, a.city,
                a.adresse AS adresse_approximative, a.statut, a.cree_le,
                a.is_available, a.is_verified, a.discount_pct,
                ROUND(({distance_expression})::numeric, 2) AS distance_km,
                u.nom_complet AS loueur_nom,
                u.statut_verification AS loueur_statut_kyc,
                COUNT(*) OVER() AS total_count
            FROM articles a
            JOIN utilisateurs u ON a.loueur_id = u.id
            WHERE a.statut = 'actif'
              AND a.localisation IS NOT NULL
              AND ({distance_expression}) <= :radius_km
        """
        params: Dict[str, Any] = {
            "lat": lat,
            "lng": lng,
            "radius_km": radius_km,
            "limit": limit,
            "offset": offset,
        }

        if disponible:
            sql += " AND a.is_available IS TRUE"
        if verifie:
            sql += " AND u.statut_verification = 'verified'"
        if q:
            sql += " AND (a.titre ILIKE :query OR a.description ILIKE :query)"
            params["query"] = f"%{q}%"
        if categorie:
            sql += " AND a.categorie = :categorie"
            params["categorie"] = categorie
        if city:
            sql += " AND LOWER(a.city) = LOWER(:city)"
            params["city"] = city
        if prix_min is not None:
            sql += " AND a.prix_par_jour >= :prix_min"
            params["prix_min"] = prix_min
        if prix_max is not None:
            sql += " AND a.prix_par_jour <= :prix_max"
            params["prix_max"] = prix_max

        sql += " ORDER BY distance_km ASC, a.cree_le DESC LIMIT :limit OFFSET :offset"
        result = await db.execute(text(sql), params)
        return [dict(row) for row in result.mappings().all()]


geo_search_service = GeoSearchService()
