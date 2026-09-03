"""Introduce the provider-controlled KYC lifecycle and remove fake scores.

Revision ID: 20260830_03
Revises: 20260830_02
"""
from typing import Sequence, Union

from alembic import op


revision: str = "20260830_03"
down_revision: Union[str, None] = "20260830_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


KYC_VALUES = (
    "not_started",
    "pending",
    "in_review",
    "verified",
    "rejected",
    "requires_action",
)


def _constraint(values: tuple[str, ...]) -> str:
    allowed = ", ".join(f"'{value}'" for value in values)
    return f"CHECK (statut_verification IN ({allowed}))"


def _users_view(verified_value: str, include_score: bool) -> str:
    score = ", kyc_liveness_score" if include_score else ""
    return f"""
    CREATE OR REPLACE VIEW public.users AS
        SELECT id, firebase_uid, nom_complet AS full_name, email, telephone AS phone_number,
               hashed_password, cin_number, (statut_verification = '{verified_value}') AS is_kyc_verified
               {score}, verifie_le AS kyc_verified_at, user_role, company_name,
               company_ice, city, cree_le AS created_at
        FROM public.utilisateurs
    """


def _search_function(verified_value: str) -> str:
    return f"""
    CREATE OR REPLACE FUNCTION public.search_articles_geo(
        query_text TEXT DEFAULT NULL, cat_filter TEXT DEFAULT NULL,
        min_p DECIMAL DEFAULT NULL, max_p DECIMAL DEFAULT NULL,
        user_lat DOUBLE PRECISION DEFAULT NULL, user_lng DOUBLE PRECISION DEFAULT NULL,
        radius_km DOUBLE PRECISION DEFAULT NULL, only_verified BOOLEAN DEFAULT FALSE,
        p_offset INTEGER DEFAULT 0, p_limit INTEGER DEFAULT 20
    ) RETURNS TABLE (
        id UUID, titre VARCHAR(255), categorie VARCHAR(60), prix_par_jour NUMERIC(10,2),
        montant_caution NUMERIC(10,2), photos JSONB, statut VARCHAR(30), city VARCHAR(60),
        adresse TEXT, distance_km DOUBLE PRECISION, loueur_id UUID, loueur_nom VARCHAR(150),
        loueur_note NUMERIC(3,2), loueur_verifie BOOLEAN, total_records BIGINT
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT a.id, a.titre, a.categorie, a.prix_par_jour, a.montant_caution, a.photos,
               a.statut, a.city, a.adresse,
               CASE WHEN user_lat IS NOT NULL AND user_lng IS NOT NULL AND a.localisation IS NOT NULL
                    THEN ST_DistanceSphere(a.localisation, ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326)) / 1000.0
                    ELSE 0.0 END,
               u.id, u.nom_complet, u.note, (u.statut_verification = '{verified_value}'), COUNT(*) OVER()
        FROM public.articles a
        JOIN public.utilisateurs u ON a.loueur_id = u.id
        WHERE a.statut = 'actif'
          AND (query_text IS NULL OR a.titre ILIKE '%' || query_text || '%' OR a.description ILIKE '%' || query_text || '%')
          AND (cat_filter IS NULL OR cat_filter = 'all' OR a.categorie = cat_filter)
          AND (min_p IS NULL OR a.prix_par_jour >= min_p)
          AND (max_p IS NULL OR a.prix_par_jour <= max_p)
          AND (only_verified IS FALSE OR u.statut_verification = '{verified_value}')
          AND (user_lat IS NULL OR user_lng IS NULL OR radius_km IS NULL OR a.localisation IS NULL OR
               ST_DWithin(a.localisation::geography,
                          ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326)::geography,
                          radius_km * 1000))
        ORDER BY CASE WHEN user_lat IS NOT NULL AND user_lng IS NOT NULL AND a.localisation IS NOT NULL
                      THEN ST_DistanceSphere(a.localisation, ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326))
                 END ASC NULLS LAST,
                 a.cree_le DESC
        OFFSET p_offset LIMIT p_limit;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER
    """


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.users")
    op.execute("ALTER TABLE public.utilisateurs DROP CONSTRAINT IF EXISTS utilisateurs_statut_verification_check")
    op.execute("ALTER TABLE public.utilisateurs DROP CONSTRAINT IF EXISTS ck_utilisateurs_kyc_status")
    op.execute("ALTER TABLE public.utilisateurs ADD COLUMN IF NOT EXISTS kyc_provider_status VARCHAR(30)")
    op.execute("ALTER TABLE public.utilisateurs ADD COLUMN IF NOT EXISTS kyc_last_event_id VARCHAR(36)")
    op.execute("""
        UPDATE public.utilisateurs
        SET statut_verification = CASE
            WHEN statut_verification = 'approuve' THEN 'verified'
            WHEN statut_verification = 'rejete' THEN 'rejected'
            WHEN statut_verification = 'revision_manuelle' THEN 'in_review'
            WHEN statut_verification = 'en_attente' AND didit_session_id IS NOT NULL THEN 'pending'
            WHEN statut_verification = 'en_attente' THEN 'not_started'
            ELSE statut_verification
        END
    """)
    op.execute("ALTER TABLE public.utilisateurs ALTER COLUMN statut_verification SET DEFAULT 'not_started'")
    op.execute(
        "ALTER TABLE public.utilisateurs ADD CONSTRAINT ck_utilisateurs_kyc_status "
        + _constraint(KYC_VALUES)
    )
    op.execute("ALTER TABLE public.utilisateurs DROP COLUMN IF EXISTS kyc_liveness_score")
    op.execute(_users_view("verified", include_score=False))
    op.execute(_search_function("verified"))


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.users")
    op.execute("ALTER TABLE public.utilisateurs DROP CONSTRAINT IF EXISTS ck_utilisateurs_kyc_status")
    op.execute("ALTER TABLE public.utilisateurs ADD COLUMN IF NOT EXISTS kyc_liveness_score NUMERIC(5,2) DEFAULT 0.00")
    op.execute("""
        UPDATE public.utilisateurs
        SET statut_verification = CASE
            WHEN statut_verification = 'verified' THEN 'approuve'
            WHEN statut_verification = 'rejected' THEN 'rejete'
            WHEN statut_verification IN ('in_review', 'requires_action') THEN 'revision_manuelle'
            ELSE 'en_attente'
        END
    """)
    op.execute("ALTER TABLE public.utilisateurs ALTER COLUMN statut_verification SET DEFAULT 'en_attente'")
    op.execute(
        "ALTER TABLE public.utilisateurs ADD CONSTRAINT utilisateurs_statut_verification_check "
        + _constraint(("en_attente", "approuve", "rejete", "revision_manuelle"))
    )
    op.execute("ALTER TABLE public.utilisateurs DROP COLUMN IF EXISTS kyc_last_event_id")
    op.execute("ALTER TABLE public.utilisateurs DROP COLUMN IF EXISTS kyc_provider_status")
    op.execute(_users_view("approuve", include_score=True))
    op.execute(_search_function("approuve"))
