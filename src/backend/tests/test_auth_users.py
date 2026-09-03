import asyncio
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Response
from starlette.requests import Request

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.authorization import require_resource_access
from app.core.config import settings
from app.routers import auth as auth_router
from app.schemas.user_schemas import UserUpdateRequest
from app.services import firebase_identity


class ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return self

    def first(self):
        return self.value

    def scalar_one_or_none(self):
        return self.value


class FakeDb:
    def __init__(self, user):
        self.user = user

    async def execute(self, _query):
        return ScalarResult(self.user)

    async def flush(self):
        pass

    async def commit(self):
        pass

    async def refresh(self, _user):
        pass


def make_request(method="GET", cookie=None, origin=None):
    headers = []
    if cookie:
        headers.append((b"cookie", f"{settings.FIREBASE_SESSION_COOKIE_NAME}={cookie}".encode()))
    if origin:
        headers.append((b"origin", origin.encode()))
    return Request({"type": "http", "method": method, "path": "/", "headers": headers})


def make_user(uid="firebase-user-1"):
    return SimpleNamespace(
        id=uuid.uuid4(), firebase_uid=uid, email="verified@example.ma", telephone=None,
        nom_complet="Verified User", avatar_url=None, statut_verification="not_started",
        note=5.0, temps_reponse_minutes=30, user_role="renter",
        company_name=None, company_ice=None, city="Casablanca", plan_abonnement="Gratuit",
        cree_le=None,
    )


def test_missing_credentials_returns_401(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth_router.get_current_user(make_request(), None, FakeDb(make_user())))
    assert exc.value.status_code == 401


def test_invalid_and_expired_tokens_return_401(monkeypatch):
    async def invalid(_token):
        raise firebase_identity.InvalidFirebaseToken("expired")

    monkeypatch.setattr(firebase_identity, "verify_id_token", invalid)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth_router.get_current_user(make_request(), "Bearer expired-token", FakeDb(make_user())))
    assert exc.value.status_code == 401


def test_bearer_token_resolves_database_user(monkeypatch):
    user = make_user()
    monkeypatch.setattr(firebase_identity, "verify_id_token", AsyncMock(return_value={"uid": user.firebase_uid}))
    resolved = asyncio.run(auth_router.get_current_user(make_request(), "Bearer firebase-id-token", FakeDb(user)))
    assert resolved is user
    assert resolved.user_role == "renter"


def test_web_login_sets_httponly_session_cookie(monkeypatch):
    user = make_user()
    monkeypatch.setattr(firebase_identity, "verify_id_token", AsyncMock(return_value={"uid": user.firebase_uid}))
    monkeypatch.setattr(firebase_identity, "create_session_cookie", AsyncMock(return_value="signed-session-cookie"))
    response = Response()
    resolved = asyncio.run(auth_router.create_web_session(
        auth_router.FirebaseSessionRequest(id_token="x" * 100),
        make_request(method="POST", origin=settings.cors_origins[0]), response, FakeDb(user),
    ))
    cookie = response.headers["set-cookie"].lower()
    assert resolved is user
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_session_restoration_uses_server_cookie(monkeypatch):
    user = make_user()
    monkeypatch.setattr(firebase_identity, "verify_session_cookie", AsyncMock(return_value={"uid": user.firebase_uid}))
    resolved = asyncio.run(auth_router.get_current_user(make_request(cookie="signed"), None, FakeDb(user)))
    assert resolved is user


def test_logout_deletes_session_cookie():
    response = Response()
    asyncio.run(auth_router.delete_web_session(response))
    cookie = response.headers["set-cookie"].lower()
    assert "max-age=0" in cookie


def test_cookie_mutation_rejects_untrusted_origin(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth_router.get_current_user(
            make_request(method="POST", cookie="signed", origin="https://attacker.example"),
            None, FakeDb(make_user()),
        ))
    assert exc.value.status_code == 403


def test_unauthorized_resource_access_returns_403():
    user = make_user()
    with pytest.raises(HTTPException) as exc:
        require_resource_access(user, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 403


def test_booking_endpoint_rejects_non_participant():
    from app.routers.bookings import get_booking_detail

    outsider = make_user()
    booking = SimpleNamespace(
        id=uuid.uuid4(), locataire_id=uuid.uuid4(), loueur_id=uuid.uuid4(), article_id=uuid.uuid4(),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_booking_detail(booking.id, outsider, FakeDb(booking)))
    assert exc.value.status_code == 403


def test_user_update_schema_has_no_authorization_fields():
    update = UserUpdateRequest(nom_complet="Nouveau nom", city="Tanger")
    assert update.nom_complet == "Nouveau nom"
    assert "user_role" not in UserUpdateRequest.model_fields
    assert "statut_verification" not in UserUpdateRequest.model_fields


def test_only_firebase_session_auth_routes_are_exposed():
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/auth/session" in paths
    assert "/api/v1/auth/me" in paths
    assert "/api/v1/auth/login" not in paths
    assert "/api/v1/auth/register" not in paths
    assert "/api/v1/auth/refresh" not in paths
