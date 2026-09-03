from collections import Counter
from pathlib import Path

from fastapi.routing import APIRoute

from app.main import app
from app.schemas.billing_schemas import SubscriptionUpgradeRequest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ROUTERS = BACKEND_ROOT / "app/routers"


def _route(path: str, method: str) -> APIRoute:
    return next(
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == path
        and method in route.methods
    )


def test_retired_duplicate_modules_are_not_present_or_imported():
    for module_name in ["messages.py", "abonnements.py", "handoff.py"]:
        assert not (ROUTERS / module_name).exists()

    assert not (BACKEND_ROOT / "app/schemas/schemas.py").exists()
    for source in (BACKEND_ROOT / "app").rglob("*.py"):
        assert "app.schemas.schemas" not in source.read_text(encoding="utf-8")


def test_each_public_method_and_path_has_one_registered_handler():
    route_keys = [
        (route.path, method)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    ]
    duplicates = [key for key, count in Counter(route_keys).items() if count > 1]
    assert duplicates == []


def test_authoritative_domains_own_legacy_compatibility_paths():
    messaging_paths = [
        ("/api/v1/messages", "POST"),
        ("/api/v1/messages/conversations/{conversation_id}/lus", "PUT"),
    ]
    billing_paths = [
        ("/api/v1/abonnements/plans", "GET"),
        ("/api/v1/tarifs/plans", "GET"),
        ("/api/v1/abonnements/annuler", "POST"),
    ]
    inspection_paths = [
        ("/api/v1/inspections/seal", "POST"),
        ("/api/v1/remises/check-in", "POST"),
        ("/api/v1/remises/check-out", "POST"),
        ("/api/v1/remises/reservation/{booking_id}", "GET"),
        ("/api/v1/remises/confirmation-cash", "POST"),
    ]

    for path, method in messaging_paths:
        assert _route(path, method).endpoint.__module__ == "app.routers.messaging"
    for path, method in billing_paths:
        assert _route(path, method).endpoint.__module__ == "app.routers.billing"
    for path, method in inspection_paths:
        assert _route(path, method).endpoint.__module__ == "app.routers.inspections"
    assert _route(
        "/api/v1/reservations/{reservation_id}/remise/litige", "POST"
    ).endpoint.__module__ == "app.routers.disputes"


def test_language_compatibility_paths_share_authoritative_handlers():
    route_pairs = [
        (("/api/v1/articles", "GET"), ("/api/v1/equipment", "GET")),
        (("/api/v1/reservations", "GET"), ("/api/v1/bookings", "GET")),
        (("/api/v1/contrats/{booking_id}", "GET"), ("/api/v1/contracts/{booking_id}", "GET")),
        (("/api/v1/kyc/initier", "POST"), ("/api/v1/auth/kyc/initier", "POST")),
        (("/api/v1/abonnements/plans", "GET"), ("/api/v1/tarifs/plans", "GET")),
    ]
    for left, right in route_pairs:
        assert _route(*left).endpoint is _route(*right).endpoint


def test_subscription_upgrade_accepts_current_and_legacy_field_names():
    assert SubscriptionUpgradeRequest(nouveau_plan="Gratuit").nouveau_plan == "Gratuit"
    assert SubscriptionUpgradeRequest(plan_id="Gratuit").nouveau_plan == "Gratuit"


def test_legacy_current_user_paths_delegate_to_identity_handlers():
    users_source = (ROUTERS / "users.py").read_text(encoding="utf-8")
    assert "return await get_me(current_user)" in users_source
    assert "return await update_me(payload, current_user, db)" in users_source
    assert _route("/api/v1/auth/me", "GET").endpoint.__module__ == "app.routers.auth"
    assert _route("/api/v1/utilisateurs/moi", "GET").endpoint.__module__ == "app.routers.users"
