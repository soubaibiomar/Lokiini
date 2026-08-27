import contextlib
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
import httpx
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.models import User, Equipment
from app.routers import auth, equipment, bookings, kyc, inspections, webhooks, contracts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lokiini-api")

async def init_db_and_seed():
    """Ensure tables exist and seed demo records if database is fresh."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).limit(1))
            user = result.scalars().first()
            if not user:
                logger.info("Database empty, initializing Moroccan seed profiles and equipment...")
                # 1. Seed Owner User
                pro_owner = User(
                    id=User.__table__.c.id.type.python_type("a1111111-1111-1111-1111-111111111111"),
                    full_name="Atlas Location BTP Maroc",
                    email="contact@atlasbtp.ma",
                    phone_number="+212661000001",
                    hashed_password="$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i",
                    is_kyc_verified=True,
                    kyc_liveness_score=98.50,
                    user_role="pro_owner",
                    company_name="Atlas Location BTP SARL",
                    company_ice="002345678000045",
                    city="Casablanca"
                )
                session.add(pro_owner)

                # 2. Seed Renter User
                renter = User(
                    id=User.__table__.c.id.type.python_type("a2222222-2222-2222-2222-222222222222"),
                    full_name="Karim Tazi (Entreprise BTP)",
                    email="karim.tazi@gmail.com",
                    phone_number="+212662000002",
                    hashed_password="$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i",
                    is_kyc_verified=True,
                    kyc_liveness_score=96.00,
                    user_role="renter",
                    city="Casablanca"
                )
                session.add(renter)
                await session.flush()

                # 3. Seed Equipment
                equipments = [
                    Equipment(
                        id=Equipment.__table__.c.id.type.python_type("e1111111-1111-1111-1111-111111111111"),
                        owner_id=pro_owner.id,
                        title="Bétonnière Professionnelle Chantier 160L",
                        description="Bétonnière robuste cuve 160 litres, moteur électrique 230V puissant, idéale pour coulage de dalles et maçonnerie sur chantier résidentiel ou pro.",
                        category="btp",
                        city="Casablanca",
                        address="Ain Sebaa, Casablanca",
                        daily_price_mad=180.00,
                        deposit_amount_mad=1500.00,
                        is_available=True,
                        is_verified=True,
                        discount_pct=0,
                        specs_json={"Capacité": "160 Litres", "Moteur": "Électrique 850W", "Poids": "55 kg"},
                        images_urls=["/images/concrete_mixer.jpg"]
                    ),
                    Equipment(
                        id=Equipment.__table__.c.id.type.python_type("e2222222-2222-2222-2222-222222222222"),
                        owner_id=pro_owner.id,
                        title="Mini-Pelle Compacte Bobcat E19 (1.9 Tonne)",
                        description="Mini-pelle sur chenilles caoutchouc Bobcat E19 avec canopy, 3 godets fournis (curage + 2 terrassement), brise-roche disponible.",
                        category="btp",
                        city="Casablanca",
                        address="Route de Bouskoura, Casablanca",
                        daily_price_mad=1280.00,
                        deposit_amount_mad=8000.00,
                        is_available=True,
                        is_verified=True,
                        discount_pct=20,
                        specs_json={"Poids": "1.88 Tonne", "Profondeur": "2.56 m", "Moteur": "Diesel Kubota"},
                        images_urls=["/images/mini_excavator.jpg"]
                    ),
                    Equipment(
                        id=Equipment.__table__.c.id.type.python_type("e3333333-3333-3333-3333-333333333333"),
                        owner_id=pro_owner.id,
                        title="Nettoyeur Haute Pression 180 Bar Thermique",
                        description="Nettoyeur haute pression thermique à essence Honda GX, débit 900L/h, lance rotative et flexible 15m pour façades, sols et terrasses.",
                        category="cleaning",
                        city="Casablanca",
                        address="Hay Hassani / Oulfa, Casablanca",
                        daily_price_mad=150.00,
                        deposit_amount_mad=1200.00,
                        is_available=True,
                        is_verified=True,
                        discount_pct=0,
                        specs_json={"Pression": "180 Bar", "Débit": "900 L/h", "Carburant": "Essence SP95"},
                        images_urls=["/images/pressure_washer.jpg"]
                    ),
                    Equipment(
                        id=Equipment.__table__.c.id.type.python_type("e4444444-4444-4444-4444-444444444444"),
                        owner_id=pro_owner.id,
                        title="Caméra Cinéma Sony FX3 4K Full-Frame + Cage XLR",
                        description="Boîtier cinéma plein format 4K 120fps, profil S-Cinetone, 2 cartes CFexpress 160Go, 4 batteries, cage SmallRig et poignée XLR audio incluse.",
                        category="audiovisual",
                        city="Marrakech",
                        address="Guéliz, Marrakech",
                        daily_price_mad=450.00,
                        deposit_amount_mad=5000.00,
                        is_available=True,
                        is_verified=True,
                        discount_pct=10,
                        specs_json={"Capteur": "Plein Format 12.1 MP", "Vidéo": "4K 120p 10-bit", "Audio": "XLR Pro 4CH"},
                        images_urls=["/images/sony_fx3.jpg"]
                    ),
                    Equipment(
                        id=Equipment.__table__.c.id.type.python_type("e5555555-5555-5555-5555-555555555555"),
                        owner_id=pro_owner.id,
                        title="Groupe Électrogène Insonorisé 10 kVA Silent",
                        description="Groupe électrogène silencieux monophasé/triphasé 10kVA, démarrage électrique automatique ATS, réservoir grande autonomie pour chantier ou événement.",
                        category="energy",
                        city="Tanger",
                        address="Tanger Free Zone, Tanger",
                        daily_price_mad=350.00,
                        deposit_amount_mad=3000.00,
                        is_available=True,
                        is_verified=True,
                        discount_pct=0,
                        specs_json={"Puissance": "10 kVA / 8 kW", "Bruit": "65 dB(A)", "Tension": "230V / 400V"},
                        images_urls=["/images/generator_10kva.jpg"]
                    ),
                    Equipment(
                        id=Equipment.__table__.c.id.type.python_type("e6666666-6666-6666-6666-666666666666"),
                        owner_id=pro_owner.id,
                        title="Perforateur Burineur Démolition Pro SDS-Max",
                        description="Marteau piqueur démolition lourd 1500W, force de frappe 25 Joules, 4 burins pointus et plats fournis en coffret rigide.",
                        category="tools",
                        city="Rabat",
                        address="Quartier Industriel Agdal, Rabat",
                        daily_price_mad=120.00,
                        deposit_amount_mad=1000.00,
                        is_available=True,
                        is_verified=True,
                        discount_pct=0,
                        specs_json={"Puissance": "1500 Watts", "Impact": "25 Joules", "Emmanchement": "SDS-Max"},
                        images_urls=["/images/jackhammer.jpg"]
                    )
                ]
                session.add_all(equipments)
                await session.commit()
                logger.info("Seed data successfully injected into database.")
    except Exception as e:
        logger.warning(f"Database initialization note: {e}")

    # Initialize Meilisearch index if available
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            headers = {"Authorization": f"Bearer {settings.MEILISEARCH_MASTER_KEY}"}
            await client.post(
                f"{settings.MEILISEARCH_URL}/indexes",
                json={"uid": "equipment", "primaryKey": "id"},
                headers=headers
            )
    except Exception:
        pass

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_and_seed()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API REST de la marketplace Lokiini (Location de matériel & d'équipements sécurisée au Maroc avec séquestre CMI, KYC CNDP et baux DOC)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(equipment.router, prefix=settings.API_V1_STR)
app.include_router(bookings.router, prefix=settings.API_V1_STR)
app.include_router(kyc.router, prefix=settings.API_V1_STR)
app.include_router(inspections.router, prefix=settings.API_V1_STR)
app.include_router(contracts.router, prefix=settings.API_V1_STR)
app.include_router(webhooks.router, prefix=settings.API_V1_STR)

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
