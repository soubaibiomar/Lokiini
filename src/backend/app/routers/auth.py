import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User
from app.schemas.user_schemas import UserProfileResponse, UserUpdateRequest
from app.services import firebase_identity

router = APIRouter(prefix="/auth", tags=["Authentification Firebase & Sessions"])


class FirebaseSessionRequest(BaseModel):
    id_token: str = Field(min_length=100, max_length=10000)


def _unauthorized(message: str = "Authentification requise.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "AUTH_REQUIRED", "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def _firebase_error(exc: Exception) -> HTTPException:
    if isinstance(exc, firebase_identity.InvalidFirebaseToken):
        return _unauthorized("Jeton Firebase invalide, expiré ou révoqué.")
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={"code": "FIREBASE_UNAVAILABLE", "message": "Le service d'authentification est indisponible."},
    )


def _assert_cookie_request_origin(request: Request) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    origin = request.headers.get("origin")
    if not origin or origin not in settings.cors_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "CSRF_ORIGIN_REJECTED", "message": "Origine de requête non autorisée."},
        )


async def _resolve_internal_user(claims: dict[str, Any], db: AsyncSession) -> User:
    firebase_uid = claims.get("uid") or claims.get("sub")
    if not isinstance(firebase_uid, str) or not firebase_uid:
        raise _unauthorized("Jeton Firebase sans identifiant utilisateur.")

    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalars().first()
    if user:
        return user

    raw_email = claims.get("email")
    email = raw_email.strip().lower() if isinstance(raw_email, str) and raw_email.strip() else None
    email_verified = claims.get("email_verified") is True

    if email and email_verified:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalars().first()
        if existing:
            if existing.firebase_uid and existing.firebase_uid != firebase_uid:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "IDENTITY_CONFLICT", "message": "Cette adresse est déjà liée à une autre identité."},
                )
            existing.firebase_uid = firebase_uid
            await db.flush()
            return existing
    elif email:
        # Never link an unverified Firebase email to an existing Lokiini account.
        result = await db.execute(select(User.id).where(User.email == email))
        if result.scalar_one_or_none() is not None:
            email = None

    phone = claims.get("phone_number") if isinstance(claims.get("phone_number"), str) else None
    if phone:
        duplicate_phone = await db.execute(select(User.id).where(User.telephone == phone))
        if duplicate_phone.scalar_one_or_none() is not None:
            phone = None

    display_name = claims.get("name")
    if not isinstance(display_name, str) or not display_name.strip():
        display_name = email.split("@", 1)[0] if email else "Utilisateur Lokiini"

    user = User(
        id=uuid.uuid4(), firebase_uid=firebase_uid, email=email, telephone=phone,
        nom_complet=display_name.strip()[:150], hashed_password=None,
        avatar_url=claims.get("picture") if isinstance(claims.get("picture"), str) else None,
        user_role="renter", statut_verification="not_started", plan_abonnement="Gratuit",
        city="Casablanca", cree_le=datetime.utcnow(),
    )
    db.add(user)
    await db.flush()
    return user


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    session_cookie = request.cookies.get(settings.FIREBASE_SESSION_COOKIE_NAME)
    try:
        if session_cookie:
            _assert_cookie_request_origin(request)
            claims = await firebase_identity.verify_session_cookie(session_cookie)
        elif authorization:
            parts = authorization.split()
            if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
                raise _unauthorized("Schéma Bearer invalide.")
            claims = await firebase_identity.verify_id_token(parts[1])
        else:
            raise _unauthorized()
    except HTTPException:
        raise
    except Exception as exc:
        raise _firebase_error(exc) from exc
    return await _resolve_internal_user(claims, db)


@router.post("/session", response_model=UserProfileResponse)
async def create_web_session(
    payload: FirebaseSessionRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    origin = request.headers.get("origin")
    if origin and origin not in settings.cors_origins:
        raise HTTPException(status_code=403, detail={"code": "ORIGIN_REJECTED", "message": "Origine non autorisée."})
    try:
        claims = await firebase_identity.verify_id_token(payload.id_token)
        expires_in = settings.FIREBASE_SESSION_DAYS * 24 * 60 * 60
        cookie = await firebase_identity.create_session_cookie(payload.id_token, expires_in)
    except Exception as exc:
        raise _firebase_error(exc) from exc

    user = await _resolve_internal_user(claims, db)
    await db.commit()
    await db.refresh(user)
    response.set_cookie(
        key=settings.FIREBASE_SESSION_COOKIE_NAME, value=cookie, max_age=expires_in,
        httponly=True, secure=settings.SESSION_COOKIE_SECURE, samesite="lax", path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    return user


@router.delete("/session", status_code=status.HTTP_204_NO_CONTENT)
async def delete_web_session(response: Response):
    response.delete_cookie(
        settings.FIREBASE_SESSION_COOKIE_NAME, path="/", secure=settings.SESSION_COOKIE_SECURE,
        httponly=True, samesite="lax",
    )


@router.post("/deconnexion", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
async def logout_compatibility(response: Response):
    return await delete_web_session(response)


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for field in ("nom_complet", "telephone", "avatar_url", "company_name", "company_ice", "city"):
        value = getattr(payload, field)
        if value is not None:
            setattr(current_user, field, value)
    current_user.modifie_le = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    return current_user
