from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class LokiiniAPIException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, details=None):
        super().__init__(
            status_code=status_code, 
            detail={"code": code, "message": message, "details": details}
        )

async def global_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={"statut": "erreur", "erreur": exc.detail}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"statut": "erreur", "erreur": {"code": f"HTTP_{exc.status_code}", "message": str(exc.detail)}}
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
            }
        }
    )
