import asyncio
import pytest
import sys
import uuid
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from fastapi import HTTPException

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pricing_service import pricing_service
from app.services.booking_state_machine import (
    BookingAction, BookingActor, BookingStatus, booking_state_machine,
)
from app.schemas.booking_schemas import (
    BookingCreateRequest, BookingStatusUpdateRequest, PricingCalculationRequest,
)

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
    """The complete happy path can only advance one backend-controlled action at a time."""
    booking = SimpleNamespace(statut=BookingStatus.DRAFT.value, modifie_le=None)
    steps = [
        (BookingAction.SUBMIT, BookingActor.RENTER, BookingStatus.PENDING_OWNER),
        (BookingAction.OWNER_ACCEPT, BookingActor.OWNER, BookingStatus.ACCEPTED),
        (BookingAction.START_PAYMENT, BookingActor.SYSTEM, BookingStatus.PAYMENT_PENDING),
        (BookingAction.CONFIRM_PAYMENT, BookingActor.SYSTEM, BookingStatus.CONFIRMED),
        (BookingAction.MARK_READY, BookingActor.OWNER, BookingStatus.READY_FOR_HANDOVER),
        (BookingAction.COMPLETE_HANDOVER, BookingActor.SYSTEM, BookingStatus.ACTIVE),
        (BookingAction.REQUEST_RETURN, BookingActor.SYSTEM, BookingStatus.RETURN_PENDING),
        (BookingAction.COMPLETE_RETURN, BookingActor.SYSTEM, BookingStatus.COMPLETED),
    ]
    for action, actor, expected in steps:
        assert booking_state_machine.transition(booking, action, actor) == expected
        assert booking.statut == expected.value


def test_booking_state_machine_valid_branches():
    assert booking_state_machine.validate_action(
        BookingStatus.PENDING_OWNER, BookingAction.OWNER_REJECT, BookingActor.OWNER,
    ) == BookingStatus.REJECTED
    assert booking_state_machine.validate_action(
        BookingStatus.ACCEPTED, BookingAction.CANCEL, BookingActor.RENTER,
    ) == BookingStatus.CANCELLED
    assert booking_state_machine.validate_action(
        BookingStatus.ACTIVE, BookingAction.OPEN_DISPUTE, BookingActor.OWNER,
    ) == BookingStatus.DISPUTED
    assert booking_state_machine.validate_action(
        BookingStatus.DISPUTED, BookingAction.RESOLVE_DISPUTE, BookingActor.ADMIN,
    ) == BookingStatus.RESOLVED

def test_booking_state_machine_invalid_transitions():
    """Explicitly reject the dangerous jumps from the lifecycle requirement."""
    for current, target in [
        ("PENDING_OWNER", "COMPLETED"),
        ("ACTIVE", "ACCEPTED"),
        ("COMPLETED", "ACTIVE"),
    ]:
        with pytest.raises(HTTPException) as exc:
            booking_state_machine.validate_transition(current, target)
        assert exc.value.status_code == 409


def test_booking_state_machine_rejects_wrong_actor():
    with pytest.raises(HTTPException) as exc:
        booking_state_machine.validate_action(
            BookingStatus.PENDING_OWNER,
            BookingAction.OWNER_ACCEPT,
            BookingActor.RENTER,
        )
    assert exc.value.status_code == 403

    with pytest.raises(HTTPException) as exc:
        booking_state_machine.validate_action(
            BookingStatus.ACTIVE,
            BookingAction.REQUEST_RETURN,
            BookingActor.OWNER,
        )
    assert exc.value.status_code == 403


def test_booking_transition_request_supports_actions_and_validated_legacy_input():
    assert BookingStatusUpdateRequest(action="owner_accept").action == "owner_accept"
    assert BookingStatusUpdateRequest(nouveau_statut="annule").nouveau_statut == "annule"
    with pytest.raises(ValueError):
        BookingStatusUpdateRequest()
    with pytest.raises(ValueError):
        BookingStatusUpdateRequest(action="cancel", nouveau_statut="annule")


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return self

    def first(self):
        return self.value


class _BookingDb:
    def __init__(self, booking):
        self.booking = booking
        self.committed = False
        self.added = []

    async def execute(self, _query):
        return _ScalarResult(self.booking)

    async def commit(self):
        self.committed = True

    def add(self, value):
        self.added.append(value)


def _booking_and_users():
    renter_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    booking = SimpleNamespace(
        id=uuid.uuid4(),
        locataire_id=renter_id,
        loueur_id=owner_id,
        statut=BookingStatus.PENDING_OWNER.value,
        modifie_le=None,
    )
    renter = SimpleNamespace(id=renter_id, user_role="renter")
    owner = SimpleNamespace(id=owner_id, user_role="owner")
    return booking, renter, owner


def test_booking_endpoint_applies_valid_owner_action():
    from app.routers.bookings import update_booking_status

    booking, _, owner = _booking_and_users()
    db = _BookingDb(booking)
    response = asyncio.run(update_booking_status(
        booking.id,
        BookingStatusUpdateRequest(action=BookingAction.OWNER_ACCEPT.value),
        owner,
        db,
    ))
    assert response["nouveau_statut"] == BookingStatus.ACCEPTED.value
    assert booking.statut == BookingStatus.ACCEPTED.value
    assert db.committed is True
    assert db.added[0].type == "reservation_accepted"
    assert db.added[0].utilisateur_id == booking.locataire_id


def test_booking_endpoint_rejects_arbitrary_completion_and_wrong_actor():
    from app.routers.bookings import update_booking_status

    booking, renter, owner = _booking_and_users()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(update_booking_status(
            booking.id,
            BookingStatusUpdateRequest(nouveau_statut="completed"),
            owner,
            _BookingDb(booking),
        ))
    assert exc.value.status_code == 409

    with pytest.raises(HTTPException) as exc:
        asyncio.run(update_booking_status(
            booking.id,
            BookingStatusUpdateRequest(action=BookingAction.OWNER_ACCEPT.value),
            renter,
            _BookingDb(booking),
        ))
    assert exc.value.status_code == 403

def test_booking_routes_integrity():
    """Test that all Phase 4 booking routes are registered in FastAPI."""
    from app.main import app
    paths = app.openapi()["paths"]

    assert "/api/v1/reservations/calculer-prix" in paths or "/api/v1/bookings/calculate-pricing" in paths
    assert "/api/v1/reservations/creer" in paths or "/api/v1/bookings/create" in paths
    assert "/api/v1/reservations" in paths or "/api/v1/bookings" in paths
    assert "/api/v1/reservations/{booking_id}" in paths or "/api/v1/bookings/{booking_id}" in paths
    assert "/api/v1/reservations/{booking_id}/statut" in paths or "/api/v1/bookings/{booking_id}/status" in paths
