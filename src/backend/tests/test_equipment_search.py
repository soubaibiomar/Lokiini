import pytest
import asyncio
from io import BytesIO
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

from fastapi import HTTPException
from starlette.datastructures import Headers, UploadFile

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
    assert req.is_available is True
    assert req.calendrier_disponibilite == {}

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
    assert "/api/v1/articles/photos" in paths
    assert "/api/v1/articles/photos/{filename}" in paths
    assert "/api/v1/articles/{article_id}" in paths or "/api/v1/equipment/{equipment_id}" in paths


def test_catalogue_openapi_exposes_supported_filters():
    from app.main import app

    paths = app.openapi()["paths"]
    list_parameters = {
        parameter["name"]
        for parameter in paths["/api/v1/articles"]["get"]["parameters"]
    }
    assert {"q", "categorie", "city", "prix_min", "prix_max", "disponible", "verifie", "limit", "offset"} <= list_parameters

    geo_parameters = {
        parameter["name"]
        for parameter in paths["/api/v1/articles/recherche/geo"]["get"]["parameters"]
    }
    assert {"lat", "lng", "radius_km", "q", "disponible", "verifie"} <= geo_parameters


def test_geo_search_uses_current_schema_and_never_turns_errors_into_empty_success():
    service_source = (Path(__file__).parent.parent / "app/services/geo_search_service.py").read_text(encoding="utf-8")
    assert "a.localisation" in service_source
    assert "a.specs_json AS specs" in service_source
    assert "COUNT(*) OVER() AS total_count" in service_source
    assert "except Exception" not in service_source


def test_category_counts_have_no_invented_inventory_fallback():
    router_source = (Path(__file__).parent.parent / "app/routers/equipment.py").read_text(encoding="utf-8")
    assert "counts.get" not in router_source
    assert "fallback" not in router_source.lower().split("# 2. Recherche", 1)[0]


def test_equipment_detail_uses_real_review_aggregates_and_trust_fields():
    router_source = (Path(__file__).parent.parent / "app/routers/equipment.py").read_text(encoding="utf-8")
    assert "func.avg(Avis.note)" in router_source
    assert '"nombre_avis": int(review_count or 0)' in router_source
    assert '"date_inscription"' in router_source
    assert '"total_annonces"' in router_source
    assert 'else 5.0' not in router_source


def test_equipment_photo_upload_is_authenticated_bounded_and_raster_only():
    from app.main import app

    upload = app.openapi()["paths"]["/api/v1/articles/photos"]["post"]
    assert "multipart/form-data" in upload["requestBody"]["content"]

    router_source = (Path(__file__).parent.parent / "app/routers/equipment.py").read_text(encoding="utf-8")
    assert "current_user: User = Depends(get_current_user)" in router_source
    assert "EQUIPMENT_MEDIA_MAX_BYTES" in router_source
    assert '"image/jpeg"' in router_source
    assert '"image/png"' in router_source
    assert '"image/webp"' in router_source
    assert '"image/svg+xml"' not in router_source
    assert 'filename.startswith(f"{current_user.id}_")' in router_source


def test_equipment_schema_accepts_real_availability_metadata():
    request = EquipmentCreateRequest(
        titre="Nettoyeur haute pression",
        description="Nettoyeur entretenu avec flexible et lance inclus.",
        categorie="cleaning",
        prix_par_jour=150,
        montant_caution=800,
        photos=["/api/v1/media/equipment/photo.webp"],
        is_available=False,
        calendrier_disponibilite={"disponible_a_partir_du": "2026-09-15", "dates_bloquees": []},
    )
    assert request.is_available is False
    assert request.calendrier_disponibilite["disponible_a_partir_du"] == "2026-09-15"


def test_equipment_photo_upload_persists_and_owner_can_delete(tmp_path):
    from app.core.config import settings
    from app.routers.equipment import delete_equipment_photo, upload_equipment_photo

    previous_directory = settings.EQUIPMENT_MEDIA_DIR
    settings.EQUIPMENT_MEDIA_DIR = str(tmp_path)
    owner = SimpleNamespace(id=uuid.uuid4())
    photo = UploadFile(
        filename="machine.png",
        file=BytesIO(b"\x89PNG\r\n\x1a\n" + b"real-image-bytes"),
        headers=Headers({"content-type": "image/png"}),
    )
    try:
        uploaded = asyncio.run(upload_equipment_photo(photo=photo, current_user=owner))
        assert uploaded["url"].startswith("/api/v1/media/equipment/")
        stored = tmp_path / uploaded["filename"]
        assert stored.is_file()

        asyncio.run(delete_equipment_photo(filename=uploaded["filename"], current_user=owner))
        assert not stored.exists()
    finally:
        settings.EQUIPMENT_MEDIA_DIR = previous_directory


def test_equipment_photo_upload_rejects_spoofed_content(tmp_path):
    from app.core.config import settings
    from app.routers.equipment import upload_equipment_photo

    previous_directory = settings.EQUIPMENT_MEDIA_DIR
    settings.EQUIPMENT_MEDIA_DIR = str(tmp_path)
    photo = UploadFile(
        filename="not-really.jpg",
        file=BytesIO(b"this is not a jpeg"),
        headers=Headers({"content-type": "image/jpeg"}),
    )
    try:
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(upload_equipment_photo(photo=photo, current_user=SimpleNamespace(id=uuid.uuid4())))
        assert exc_info.value.status_code == 415
        assert list(tmp_path.iterdir()) == []
    finally:
        settings.EQUIPMENT_MEDIA_DIR = previous_directory
