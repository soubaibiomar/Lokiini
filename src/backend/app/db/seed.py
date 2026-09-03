"""Explicit, idempotent development-only seed command.

Run after migrations with: python -m app.db.seed
"""
import asyncio

from sqlalchemy import text

from app.core.config import RuntimeEnvironment, settings
from app.core.database import engine


USERS_SQL = """
INSERT INTO public.utilisateurs (
    id, email, telephone, nom_complet, statut_verification, user_role, city, plan_abonnement
) VALUES
    ('a1111111-1111-1111-1111-111111111111', 'owner.dev@lokiini.local', '+212600000001',
     'Lokiini Development Owner', 'not_started', 'owner', 'Casablanca', 'Gratuit'),
    ('a2222222-2222-2222-2222-222222222222', 'renter.dev@lokiini.local', '+212600000002',
     'Lokiini Development Renter', 'not_started', 'renter', 'Rabat', 'Gratuit')
ON CONFLICT (id) DO NOTHING
"""


ARTICLES_SQL = """
INSERT INTO public.articles (
    id, loueur_id, categorie, titre, description, photos, prix_par_jour,
    montant_caution, niveau_risque, localisation, city, adresse, specs_json,
    discount_pct, is_available, is_verified
) VALUES
    ('e1111111-1111-1111-1111-111111111111', 'a1111111-1111-1111-1111-111111111111',
     'btp', 'Bétonnière de développement', 'Annonce locale réservée au développement.',
     '["/images/concrete_mixer_lokiini.png"]'::jsonb, 180.00, 1500.00, 'eleve',
     ST_SetSRID(ST_MakePoint(-7.5321, 33.5972), 4326), 'Casablanca',
     'Adresse de développement, Casablanca', '{"capacite": "160L"}'::jsonb, 0, TRUE, FALSE),
    ('e2222222-2222-2222-2222-222222222222', 'a1111111-1111-1111-1111-111111111111',
     'tools', 'Perforateur de développement', 'Annonce locale réservée au développement.',
     '["/images/jackhammer_lokiini.png"]'::jsonb, 120.00, 1000.00, 'moyen',
     ST_SetSRID(ST_MakePoint(-6.8498, 34.0132), 4326), 'Rabat',
     'Adresse de développement, Rabat', '{"puissance": "1500W"}'::jsonb, 0, TRUE, FALSE),
    ('e3333333-3333-3333-3333-333333333333', 'a1111111-1111-1111-1111-111111111111',
     'cleaning', 'Nettoyeur de développement', 'Annonce locale réservée au développement.',
     '["/images/pressure_washer_lokiini.png"]'::jsonb, 150.00, 1200.00, 'moyen',
     ST_SetSRID(ST_MakePoint(-7.6680, 33.5650), 4326), 'Casablanca',
     'Adresse de développement, Casablanca', '{"pression": "180 Bar"}'::jsonb, 0, TRUE, FALSE)
ON CONFLICT (id) DO NOTHING
"""


async def seed_development() -> None:
    if settings.ENVIRONMENT != RuntimeEnvironment.DEVELOPMENT:
        raise RuntimeError("Development seed refused: ENVIRONMENT must be development")

    async with engine.begin() as connection:
        await connection.execute(text(USERS_SQL))
        await connection.execute(text(ARTICLES_SQL))

    print("Development seed applied. Existing rows were preserved.")


if __name__ == "__main__":
    asyncio.run(seed_development())
