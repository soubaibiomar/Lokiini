import pytest
import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.equipment_schemas import (
    EquipmentCreateRequest, EquipmentUpdateRequest,
    EquipmentResponse, CategoryCountResponse
)
from app.services.risk_service import risk_service
from app.services.geo_search_service import calculate_haversine_distance

def test_equipment_create_schema_validation():
    """Test validation of EquipmentCreateRequest."""
    req = EquipmentCreateRequest(
        titre="Bétonnière Thermique 350L Altrad",
        description="Idéal pour chantiers de construction à Casablanca et région.",
        categorie="btp",
        prix_par_jour=350.0,
        prix_par_semaine=2100.0,
        montant_caution=4000.0,
        lat=33.5731,
        lng=-7.5898,
        city="Casablanca"
    )
    assert req.titre == "Bétonnière Thermique 350L Altrad"
    assert req.categorie == "btp"
    assert req.montant_caution == 4000.0
    assert req.lat == 33.5731
    assert req.lng == -7.5898

def test_equipment_risk_assessment():
    """Test risk assignment on equipment creation."""
    risk_btp = risk_service.evaluate_risk("btp", 350.0, 4000.0)
    assert risk_btp["niveau_risque"] == "eleve"
    assert risk_btp["kyc_obligatoire"] is True
    assert risk_btp["caution_obligatoire"] is True

    risk_drill = risk_service.evaluate_risk("tools", 80.0, 300.0)
    assert risk_drill["niveau_risque"] == "faible"
    assert risk_drill["kyc_obligatoire"] is False

def test_haversine_distance_calculation():
    """Test spatial distance calculation between Casablanca and Rabat (~87 km)."""
    casa_lat, casa_lng = 33.5731, -7.5898
    rabat_lat, rabat_lng = 34.0209, -6.8416
    
    distance = calculate_haversine_distance(casa_lat, casa_lng, rabat_lat, rabat_lng)
    # The actual distance between Casa and Rabat is ~86-88 km
    assert 80.0 <= distance <= 95.0

def test_equipment_update_schema():
    """Test EquipmentUpdateRequest optional fields."""
    update = EquipmentUpdateRequest(
        prix_par_jour=280.0,
        statut="indisponible"
    )
    assert update.prix_par_jour == 280.0
    assert update.statut == "indisponible"
    assert update.titre is None

def test_equipment_category_response_schema():
    """Test CategoryCountResponse model."""
    cat = CategoryCountResponse(
        categorie="tools",
        nom_affiche="Outils & Bricolage",
        icone="🛠️",
        total_articles=14
    )
    assert cat.categorie == "tools"
    assert cat.total_articles == 14

def test_equipment_routes_integrity():
    """Test that all Phase 3 equipment endpoints are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]
    
    assert "/api/v1/articles" in paths or "/api/v1/equipment" in paths
    assert "/api/v1/articles/categories" in paths or "/api/v1/equipment/categories" in paths
    assert "/api/v1/articles/recherche/geo" in paths or "/api/v1/equipment/recherche/geo" in paths
    assert "/api/v1/articles/my-listings" in paths or "/api/v1/equipment/my-listings" in paths
    assert "/api/v1/articles/{article_id}" in paths or "/api/v1/equipment/{equipment_id}" in paths
