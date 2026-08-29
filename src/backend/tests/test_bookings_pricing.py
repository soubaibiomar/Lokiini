import pytest
import sys
import uuid
from datetime import date
from pathlib import Path
from fastapi import HTTPException

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pricing_service import pricing_service
from app.services.booking_state_machine import booking_state_machine
from app.schemas.booking_schemas import PricingCalculationRequest, BookingCreateRequest

def test_pricing_duration_calculation():
    """Test duration calculation."""
    d1 = date(2026, 9, 1)
    d2 = date(2026, 9, 3)
    assert pricing_service.calculate_duration_days(d1, d2) == 3

    with pytest.raises(ValueError):
        pricing_service.calculate_duration_days(date(2026, 9, 5), date(2026, 9, 1))

def test_pricing_standard_1_day():
    """Test 1 day location without discount."""
    p = pricing_service.compute_pricing_breakdown(
        prix_par_jour=100.0,
        prix_par_semaine=None,
        prix_par_mois=None,
        montant_caution=500.0,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 1),
        is_pro_owner=False
    )
    assert p["nombre_jours"] == 1
    assert p["remise_pourcentage"] == 0
    assert p["total_location_mad"] == 100.0
    assert p["frais_service_plateforme_mad"] == 15.0 # 15%
    assert p["gains_net_loueur_mad"] == 85.0
    assert p["total_a_payer_a_la_remise_mad"] == 600.0 # 100 + 500

def test_pricing_short_stay_discount():
    """Test 3 days location with 10% discount."""
    p = pricing_service.compute_pricing_breakdown(
        prix_par_jour=100.0,
        prix_par_semaine=None,
        prix_par_mois=None,
        montant_caution=500.0,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3), # 3 days
        is_pro_owner=False
    )
    assert p["nombre_jours"] == 3
    assert p["remise_pourcentage"] == 10
    assert p["total_location_mad"] == 270.0 # 300 * 0.9

def test_pricing_weekly_discount():
    """Test 7 days location with 15% discount."""
    p = pricing_service.compute_pricing_breakdown(
        prix_par_jour=100.0,
        prix_par_semaine=None,
        prix_par_mois=None,
        montant_caution=500.0,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 7), # 7 days
        is_pro_owner=False
    )
    assert p["nombre_jours"] == 7
    assert p["remise_pourcentage"] == 15
    assert p["total_location_mad"] == 595.0 # 700 * 0.85

def test_pricing_monthly_discount_and_pro_commission():
    """Test 30 days location with 25% discount and 7% pro commission."""
    p = pricing_service.compute_pricing_breakdown(
        prix_par_jour=100.0,
        prix_par_semaine=None,
        prix_par_mois=None,
        montant_caution=1000.0,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30), # 30 days
        is_pro_owner=True
    )
    assert p["nombre_jours"] == 30
    assert p["remise_pourcentage"] == 25
    assert p["total_location_mad"] == 2250.0 # 3000 * 0.75
    assert p["commission_pourcentage"] == 7
    assert p["frais_service_plateforme_mad"] == 157.50 # 2250 * 0.07
    assert p["gains_net_loueur_mad"] == 2092.50

def test_booking_state_machine_valid_transitions():
    """Test valid sequential state transitions."""
    assert booking_state_machine.validate_transition("en_attente_approbation", "confirme_cod") is True
    assert booking_state_machine.validate_transition("confirme_cod", "en_cours") is True
    assert booking_state_machine.validate_transition("en_cours", "termine") is True
    assert booking_state_machine.validate_transition("en_attente_approbation", "annule") is True
    assert booking_state_machine.validate_transition("en_cours", "litige") is True

def test_booking_state_machine_invalid_transitions():
    """Test rejection of illegal state transitions."""
    with pytest.raises(HTTPException):
        booking_state_machine.validate_transition("termine", "en_cours")

    with pytest.raises(HTTPException):
        booking_state_machine.validate_transition("annule", "confirme_cod")

    with pytest.raises(HTTPException):
        booking_state_machine.validate_transition("en_attente_approbation", "termine")

def test_booking_routes_integrity():
    """Test that all Phase 4 booking routes are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]

    assert "/api/v1/reservations/calculer-prix" in paths or "/api/v1/bookings/calculate-pricing" in paths
    assert "/api/v1/reservations/creer" in paths or "/api/v1/bookings/create" in paths
    assert "/api/v1/reservations" in paths or "/api/v1/bookings" in paths
    assert "/api/v1/reservations/{booking_id}" in paths or "/api/v1/bookings/{booking_id}" in paths
    assert "/api/v1/reservations/{booking_id}/statut" in paths or "/api/v1/bookings/{booking_id}/status" in paths
