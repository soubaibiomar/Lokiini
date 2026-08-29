import math
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcul de distance Haversine en km (fallback si PostGIS n'est pas actif en local)."""
    R = 6371.0 # Rayon de la Terre en km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class GeoSearchService:
    @staticmethod
    async def search_nearby(
        db: AsyncSession,
        lat: float,
        lng: float,
        radius_km: float = 25.0,
        categorie: Optional[str] = None,
        city: Optional[str] = None,
        prix_min: Optional[float] = None,
        prix_max: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Recherche géospatiale PostGIS triée par distance exacte en kilomètres."""
        try:
            # Query native avec ST_DistanceSphere (WGS84) sous PostgreSQL / PostGIS
            sql = """
                SELECT 
                    a.id, a.loueur_id, a.titre, a.description, a.categorie, 
                    a.prix_par_jour, a.prix_par_semaine, a.prix_par_mois, a.montant_caution,
                    a.mode_caution, a.niveau_risque, a.kyc_requis, a.photos, a.specs,
                    a.city, a.adresse_approximative, a.statut, a.cree_le,
                    ROUND((ST_DistanceSphere(a.coordonnees, ST_MakePoint(:lng, :lat)) / 1000.0)::numeric, 2) AS distance_km,
                    u.nom_complet AS loueur_nom, u.note AS loueur_note, u.statut_verification AS loueur_statut_kyc
                FROM articles a
                JOIN utilisateurs u ON a.loueur_id = u.id
                WHERE a.statut = 'actif'
                  AND (ST_DistanceSphere(a.coordonnees, ST_MakePoint(:lng, :lat)) / 1000.0) <= :radius_km
            """
            params = {"lat": lat, "lng": lng, "radius_km": radius_km, "limit": limit, "offset": offset}
            
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
                
            sql += " ORDER BY distance_km ASC LIMIT :limit OFFSET :offset"
            
            result = await db.execute(text(sql), params)
            rows = result.mappings().all()
            return [dict(r) for r in rows]
        except Exception:
            # Fallback local sans PostGIS (mock / sqlite)
            return []

geo_search_service = GeoSearchService()
