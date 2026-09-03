import logging
from typing import Any, Optional

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel


logger = logging.getLogger("lokiini-api")


class APIErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class APIErrorResponse(BaseModel):
    statut: str = "erreur"
    erreur: APIErrorDetail
    request_id: str


DEFAULT_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "AUTH_REQUIRED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    408: "REQUEST_TIMEOUT",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
    504: "GATEWAY_TIMEOUT",
}


COMMON_ERROR_RESPONSES = {
    code: {
        "model": APIErrorResponse,
        "description": label.replace("_", " ").title(),
        "headers": {"X-Request-ID": {"schema": {"type": "string"}}},
    }
    for code, label in DEFAULT_ERROR_CODES.items()
}


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")

class LokiiniAPIException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, details=None):
        super().__init__(
            status_code=status_code, 
            detail={"code": code, "message": message, "details": details}
        )

async def global_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        error = {
            "code": exc.detail.get("code", DEFAULT_ERROR_CODES.get(exc.status_code, f"HTTP_{exc.status_code}")),
            "message": exc.detail.get("message", "La requête a échoué."),
            "details": exc.detail.get("details"),
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={"statut": "erreur", "erreur": error, "request_id": _request_id(request)},
            headers=exc.headers,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statut": "erreur",
            "erreur": {
                "code": DEFAULT_ERROR_CODES.get(exc.status_code, f"HTTP_{exc.status_code}"),
                "message": str(exc.detail),
                "details": None,
            },
            "request_id": _request_id(request),
        },
        headers=exc.headers,
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        errors.append(f"{loc}: {err.get('msg')}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "statut": "erreur",
            "erreur": {
                "code": "VALIDATION_ERROR",
                "message": "Les données envoyées sont invalides ou incomplètes.",
                "details": errors
            },
            "request_id": _request_id(request),
        }
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled API error request_id=%s", _request_id(request), exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "statut": "erreur",
            "erreur": {
                "code": "INTERNAL_ERROR",
                "message": "Une erreur interne est survenue.",
                "details": None,
            },
            "request_id": _request_id(request),
        },
    )
