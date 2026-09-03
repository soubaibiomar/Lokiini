"""Server-side Firebase identity verification.

Firebase establishes identity. Lokiini roles, ownership and verification status are
always loaded from PostgreSQL and are never accepted from token custom claims.
"""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings

logger = logging.getLogger("lokiini-auth")


class FirebaseUnavailable(RuntimeError):
    pass


class InvalidFirebaseToken(ValueError):
    pass


def _require_jwt_shape(token: str) -> None:
    parts = token.split(".") if isinstance(token, str) else []
    if len(parts) != 3 or any(not part for part in parts):
        raise InvalidFirebaseToken("Malformed Firebase token")


@lru_cache(maxsize=1)
def get_firebase_app():
    if not settings.FIREBASE_PROJECT_ID:
        raise FirebaseUnavailable("FIREBASE_PROJECT_ID is not configured")

    try:
        return firebase_admin.get_app()
    except ValueError:
        try:
            if settings.FIREBASE_CREDENTIALS_PATH:
                path = Path(settings.FIREBASE_CREDENTIALS_PATH)
                if not path.is_file():
                    raise FirebaseUnavailable("Firebase credentials file is missing")
                credential = credentials.Certificate(str(path))
            else:
                credential = credentials.ApplicationDefault()
            return firebase_admin.initialize_app(
                credential,
                {"projectId": settings.FIREBASE_PROJECT_ID},
            )
        except FirebaseUnavailable:
            raise
        except Exception as exc:
            logger.error("Firebase Admin initialization failed: %s", exc)
            raise FirebaseUnavailable("Firebase Admin is unavailable") from exc


async def verify_id_token(id_token: str) -> dict[str, Any]:
    _require_jwt_shape(id_token)
    try:
        return await asyncio.to_thread(
            auth.verify_id_token,
            id_token,
            check_revoked=True,
            app=get_firebase_app(),
        )
    except FirebaseUnavailable:
        raise
    except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError,
            auth.UserDisabledError, ValueError) as exc:
        raise InvalidFirebaseToken("Invalid, expired or revoked Firebase ID token") from exc
    except Exception as exc:
        logger.error("Firebase token verification failed: %s", exc)
        raise FirebaseUnavailable("Firebase token verification is unavailable") from exc


async def verify_session_cookie(session_cookie: str) -> dict[str, Any]:
    _require_jwt_shape(session_cookie)
    try:
        return await asyncio.to_thread(
            auth.verify_session_cookie,
            session_cookie,
            check_revoked=True,
            app=get_firebase_app(),
        )
    except FirebaseUnavailable:
        raise
    except (auth.InvalidSessionCookieError, auth.ExpiredSessionCookieError,
            auth.RevokedSessionCookieError, auth.UserDisabledError, ValueError) as exc:
        raise InvalidFirebaseToken("Invalid, expired or revoked Firebase session") from exc
    except Exception as exc:
        logger.error("Firebase session verification failed: %s", exc)
        raise FirebaseUnavailable("Firebase session verification is unavailable") from exc


async def create_session_cookie(id_token: str, expires_in_seconds: int) -> str:
    _require_jwt_shape(id_token)
    try:
        return await asyncio.to_thread(
            auth.create_session_cookie,
            id_token,
            expires_in=expires_in_seconds,
            app=get_firebase_app(),
        )
    except FirebaseUnavailable:
        raise
    except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, ValueError) as exc:
        raise InvalidFirebaseToken("Invalid or expired Firebase ID token") from exc
    except Exception as exc:
        logger.error("Firebase session creation failed: %s", exc)
        raise FirebaseUnavailable("Firebase session creation is unavailable") from exc
