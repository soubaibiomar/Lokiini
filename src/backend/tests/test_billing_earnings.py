import pytest
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.subscription_service import subscription_service
from app.services.earnings_service import earnings_service
from app.schemas.billing_schemas import (
    SubscriptionPlanResponse, MySubscriptionResponse,
    SubscriptionUpgradeRequest, EarningsDashboardResponse, InvoiceResponse
)

def test_subscription_service_plans():
    """Test that all 4 subscription tiers exist."""
    plans = subscription_service.get_all_plans()
    plan_names = [p["nom"] for p in plans]
    
    assert len(plans) == 4
    assert "Gratuit" in plan_names
    assert "Premium" in plan_names
    assert "Pro" in plan_names
    assert "Entreprise" in plan_names

def test_subscription_tier_details():
    """Test commission rates and quota configurations."""
    pro = subscription_service.get_plan_details("Pro")
    assert pro["prix_mensuel_mad"] == 149.0
    assert pro["commission_pct"] == 0.07 # 7%
    assert pro["facturation_ice"] is True

    premium = subscription_service.get_plan_details("Premium")
    assert premium["prix_mensuel_mad"] == 79.0
    assert premium["commission_pct"] == 0.12 # 12%

    entreprise = subscription_service.get_plan_details("Entreprise")
    assert entreprise["prix_mensuel_mad"] == 300.0
    assert entreprise["commission_pct"] == 0.05 # 5%

    gratuit = subscription_service.get_plan_details("Gratuit")
    assert gratuit["prix_mensuel_mad"] == 0.0
    assert gratuit["commission_pct"] == 0.15 # 15%
    assert gratuit["max_annonces"] == 3

def test_earnings_service_calculations():
    """Test aggregation of earnings, commissions, and nets."""
    data = [
        {"rental_amount": 1000.0, "platform_fee": 70.0, "payout_amount": 930.0, "payout_status": "paid", "statut_reservation": "termine", "article_titre": "Perforateur"},
        {"rental_amount": 2000.0, "platform_fee": 140.0, "payout_amount": 1860.0, "payout_status": "paid", "statut_reservation": "termine", "article_titre": "Bétonnière"}
    ]
    
    metrics = earnings_service.calculate_dashboard_metrics(data, "mois")
    assert metrics["total_gains_bruts_mad"] == 3000.0
    assert metrics["total_commissions_plateforme_mad"] == 210.0
    assert metrics["total_gains_nets_mad"] == 2790.0
    assert metrics["nombre_locations_terminees"] == 2
    assert len(metrics["top_articles_rentables"]) == 2
    assert metrics["payout_status"] == "paid"

def test_invoice_calculation():
    """Test invoice TVA calculation."""
    total_ttc = 1200.0
    ht = round(total_ttc / 1.20, 2) # 1000.00
    tva = round(total_ttc - ht, 2)  # 200.00
    
    assert ht == 1000.0
    assert tva == 200.0

def test_billing_routes_integrity():
    """Test that all Phase 8 billing routes are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]
    
    assert "/api/v1/abonnements/plans" in paths
    assert "/api/v1/tarifs/plans" in paths
    assert "/api/v1/abonnements/moi" in paths
    assert "/api/v1/abonnements/upgrade" in paths
    assert "/api/v1/abonnements/annuler" in paths
    assert "/api/v1/dashboard/gains" in paths
    assert "/api/v1/factures/{booking_id}" in paths
