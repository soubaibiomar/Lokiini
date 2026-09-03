import contextlib
import logging

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    COMMON_ERROR_RESPONSES,
    global_http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.request_context import resolve_request_id
from app.routers import (
    auth, users, equipment, bookings, kyc, inspections,
    webhooks, contracts, billing, messaging, notifications, payments, disputes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lokiini-api")


async def init_search_index():
    """Initialize the external search index; relational schema is managed by Alembic."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            headers = {"Authorization": f"Bearer {settings.MEILISEARCH_MASTER_KEY}"}
            await client.post(
                f"{settings.MEILISEARCH_URL}/indexes",
                json={"uid": "equipment", "primaryKey": "id"},
                headers=headers
            )
    except Exception as exc:
        logger.warning("Meilisearch initialization failed: %s", exc)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await init_search_index()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API REST de la marketplace Lokiini.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    responses=COMMON_ERROR_RESPONSES,
)


@app.middleware("http")
async def add_request_context(request, call_next):
    request.state.request_id = resolve_request_id(request)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.add_exception_handler(HTTPException, global_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(equipment.router, prefix=settings.API_V1_STR)
app.include_router(bookings.router, prefix=settings.API_V1_STR)
app.include_router(kyc.router, prefix=settings.API_V1_STR)
app.include_router(inspections.router, prefix=settings.API_V1_STR)
app.include_router(disputes.router, prefix=settings.API_V1_STR)
app.include_router(disputes.compatibility_router, prefix=settings.API_V1_STR)
app.include_router(contracts.router, prefix=settings.API_V1_STR)
app.include_router(webhooks.router, prefix=settings.API_V1_STR)
app.include_router(billing.router, prefix=settings.API_V1_STR)
app.include_router(messaging.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def health_check():
    return {
        "status": "HEALTHY",
        "service": "Lokiini Backend API",
        "version": settings.VERSION,
        "environment": "docker-containerized",
        "currency": settings.DEFAULT_CURRENCY
    }
