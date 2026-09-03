"""Establish the current Lokiini relational schema.

Revision ID: 20260830_01
Revises: None
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260830_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CORE_TABLES = {
    "utilisateurs",
    "articles",
    "reservations",
    "remises",
    "confirmations_cash",
    "conversations",
    "messages",
    "avis",
    "abonnements",
    "litiges",
    "notifications",
}
MANAGED_TABLES = CORE_TABLES | {"cmi_transactions"}


CREATE_TABLE_STATEMENTS = [
    """
    CREATE TABLE public.utilisateurs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        firebase_uid VARCHAR(128),
        email VARCHAR(255) UNIQUE,
        telephone VARCHAR(30) UNIQUE,
        nom_complet VARCHAR(150) NOT NULL,
        hashed_password VARCHAR(255),
        cin_number VARCHAR(100),
        avatar_url TEXT,
        statut_verification VARCHAR(30) DEFAULT 'en_attente'
            CHECK (statut_verification IN ('en_attente', 'approuve', 'rejete', 'revision_manuelle')),
        didit_session_id VARCHAR(100),
        verifie_le TIMESTAMPTZ,
        kyc_liveness_score NUMERIC(5,2) DEFAULT 0.00,
        note NUMERIC(3,2) DEFAULT 5.00,
        temps_reponse_minutes INTEGER DEFAULT 30,
        user_role VARCHAR(30) DEFAULT 'renter'
            CHECK (user_role IN ('renter', 'owner', 'pro_owner', 'admin')),
        company_name VARCHAR(150),
        company_ice VARCHAR(30),
        city VARCHAR(60) DEFAULT 'Casablanca',
        plan_abonnement VARCHAR(30) DEFAULT 'Gratuit'
            CHECK (plan_abonnement IN ('Gratuit', 'Premium', 'Pro', 'Entreprise')),
        abonnement_valable_jusqu TIMESTAMPTZ,
        cree_le TIMESTAMPTZ DEFAULT NOW(),
        modifie_le TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE public.articles (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        loueur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
        categorie VARCHAR(60) NOT NULL,
        titre VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        photos JSONB DEFAULT '[]'::jsonb,
        prix_par_jour NUMERIC(10,2) NOT NULL CHECK (prix_par_jour > 0),
        montant_caution NUMERIC(10,2) DEFAULT 0.00,
        niveau_risque VARCHAR(20) DEFAULT 'faible'
            CHECK (niveau_risque IN ('faible', 'moyen', 'eleve')),
        localisation GEOMETRY(Point, 4326),
        city VARCHAR(60) NOT NULL DEFAULT 'Casablanca',
        adresse TEXT NOT NULL,
        calendrier_disponibilite JSONB DEFAULT '{"dates_bloquees": []}'::jsonb,
        statut VARCHAR(30) DEFAULT 'actif'
            CHECK (statut IN ('actif', 'en_pause', 'archive', 'en_revision')),
        is_available BOOLEAN DEFAULT TRUE,
        is_verified BOOLEAN DEFAULT FALSE,
        discount_pct INTEGER DEFAULT 0,
        specs_json JSONB DEFAULT '{}'::jsonb,
        nb_vues INTEGER DEFAULT 0,
        cree_le TIMESTAMPTZ DEFAULT NOW(),
        modifie_le TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE public.reservations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        article_id UUID NOT NULL REFERENCES public.articles(id) ON DELETE RESTRICT,
        locataire_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE RESTRICT,
        loueur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE RESTRICT,
        date_debut DATE NOT NULL,
        date_fin DATE NOT NULL,
        total_days INTEGER NOT NULL,
        prix_total NUMERIC(10,2) NOT NULL,
        montant_caution NUMERIC(10,2) NOT NULL,
        option_livraison VARCHAR(40) DEFAULT 'retrait_sur_place'
            CHECK (option_livraison IN ('retrait_sur_place', 'livraison_premium')),
        adresse_retrait TEXT,
        payment_method VARCHAR(30) DEFAULT 'cash_cod',
        statut VARCHAR(40) DEFAULT 'en_attente_approbation'
            CHECK (statut IN ('en_attente_verification', 'en_attente_approbation', 'confirme_cod',
                              'en_cours', 'en_attente_validation', 'termine', 'annule', 'en_litige')),
        cmi_status VARCHAR(30) DEFAULT 'pending_cod',
        contrat_pdf_url TEXT,
        contrat_sha256 VARCHAR(64),
        contrat_signe BOOLEAN DEFAULT FALSE,
        contrat_signe_le TIMESTAMPTZ,
        cree_le TIMESTAMPTZ DEFAULT NOW(),
        modifie_le TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE public.remises (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        reservation_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
        type VARCHAR(20) NOT NULL CHECK (type IN ('retrait', 'retour')),
        photos JSONB DEFAULT '[]'::jsonb,
        videos JSONB DEFAULT '[]'::jsonb,
        video_url TEXT,
        video_sha256_hash VARCHAR(64),
        geolocalisation GEOMETRY(Point, 4326),
        horodatage TIMESTAMPTZ DEFAULT NOW(),
        signatures JSONB DEFAULT '{}'::jsonb,
        signed_by_owner BOOLEAN DEFAULT FALSE,
        signed_by_renter BOOLEAN DEFAULT FALSE,
        notes TEXT,
        statut VARCHAR(30) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'confirme')),
        cree_le TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE public.confirmations_cash (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        reservation_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
        montant_recu NUMERIC(10,2) NOT NULL,
        confirme_par UUID NOT NULL REFERENCES public.utilisateurs(id),
        confirme_le TIMESTAMPTZ DEFAULT NOW(),
        notes TEXT
    )
    """,
    """
    CREATE TABLE public.conversations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        reservation_id UUID REFERENCES public.reservations(id) ON DELETE SET NULL,
        participant1_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
        participant2_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
        dernier_message_le TIMESTAMPTZ DEFAULT NOW(),
        cree_le TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT participants_differents CHECK (participant1_id <> participant2_id)
    )
    """,
    """
    CREATE TABLE public.messages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
        expediteur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
        contenu TEXT NOT NULL,
        lu BOOLEAN DEFAULT FALSE,
        cree_le TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE public.avis (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        reservation_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
        avisateur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
        avise_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
        note INTEGER NOT NULL CHECK (note BETWEEN 1 AND 5),
        commentaire TEXT,
        cree_le TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE public.abonnements (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        utilisateur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
        plan VARCHAR(30) NOT NULL CHECK (plan IN ('Gratuit', 'Premium', 'Pro', 'Entreprise')),
        taux_commission NUMERIC(5,2) NOT NULL,
        prix_mad NUMERIC(10,2) NOT NULL,
        debute_le TIMESTAMPTZ DEFAULT NOW(),
        expire_le TIMESTAMPTZ,
        statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'expire', 'annule')),
        fonctionnalites JSONB DEFAULT '[]'::jsonb
    )
    """,
    """
    CREATE TABLE public.litiges (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        reservation_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
        soumis_par UUID NOT NULL REFERENCES public.utilisateurs(id),
        motif VARCHAR(150) NOT NULL,
        description TEXT NOT NULL,
        photos JSONB DEFAULT '[]'::jsonb,
        statut VARCHAR(30) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'resolu', 'clos')),
        notes_resolution TEXT,
        cree_le TIMESTAMPTZ DEFAULT NOW(),
        resolu_le TIMESTAMPTZ
    )
    """,
    """
    CREATE TABLE public.notifications (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        utilisateur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
        type VARCHAR(30) NOT NULL CHECK (type IN ('reservation', 'message', 'systeme', 'paiement')),
        titre VARCHAR(255) NOT NULL,
        corps TEXT NOT NULL,
        data JSONB DEFAULT '{}'::jsonb,
        lu BOOLEAN DEFAULT FALSE,
        cree_le TIMESTAMPTZ DEFAULT NOW()
    )
    """,
]


CREATE_CMI_TRANSACTIONS = """
CREATE TABLE public.cmi_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
    cmi_auth_token VARCHAR(255),
    cmi_trans_id VARCHAR(100),
    card_brand VARCHAR(20),
    preauth_amount_mad NUMERIC(10,2) DEFAULT 0.00,
    captured_amount_mad NUMERIC(10,2) DEFAULT 0.00,
    deposit_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
)
"""


SUPPORTING_STATEMENTS = [
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_utilisateurs_firebase_uid ON public.utilisateurs(firebase_uid) WHERE firebase_uid IS NOT NULL",
    "CREATE INDEX IF NOT EXISTS idx_articles_localisation ON public.articles USING GIST(localisation)",
    "CREATE INDEX IF NOT EXISTS idx_articles_categorie_statut ON public.articles(categorie, statut)",
    "CREATE INDEX IF NOT EXISTS idx_articles_prix ON public.articles(prix_par_jour)",
    "CREATE INDEX IF NOT EXISTS idx_articles_titre_trgm ON public.articles USING GIN (titre gin_trgm_ops)",
    "CREATE INDEX IF NOT EXISTS idx_reservations_dates ON public.reservations(date_debut, date_fin)",
    "CREATE INDEX IF NOT EXISTS idx_reservations_statut ON public.reservations(statut)",
    "CREATE INDEX IF NOT EXISTS idx_reservations_locataire ON public.reservations(locataire_id)",
    "CREATE INDEX IF NOT EXISTS idx_reservations_loueur ON public.reservations(loueur_id)",
    "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON public.messages(conversation_id)",
    "CREATE INDEX IF NOT EXISTS idx_notifications_user_lu ON public.notifications(utilisateur_id, lu)",
    """
    CREATE OR REPLACE VIEW public.users AS
        SELECT id, firebase_uid, nom_complet AS full_name, email, telephone AS phone_number,
               hashed_password, cin_number, (statut_verification = 'approuve') AS is_kyc_verified,
               kyc_liveness_score, verifie_le AS kyc_verified_at, user_role, company_name,
               company_ice, city, cree_le AS created_at
        FROM public.utilisateurs
    """,
    """
    CREATE OR REPLACE VIEW public.equipment AS
        SELECT id, loueur_id AS owner_id, titre AS title, description, categorie AS category,
               city, adresse AS address, prix_par_jour AS daily_price_mad,
               montant_caution AS deposit_amount_mad, is_available, is_verified, discount_pct,
               specs_json, photos AS images_urls, cree_le AS created_at
        FROM public.articles
    """,
    """
    CREATE OR REPLACE VIEW public.bookings AS
        SELECT id, article_id AS equipment_id, locataire_id AS renter_id, date_debut AS start_date,
               date_fin AS end_date, total_days,
               (prix_total / NULLIF(total_days, 0)) AS daily_rate_applied_mad,
               prix_total AS rental_total_mad, (prix_total * 0.15) AS platform_commission_mad,
               montant_caution AS deposit_hold_mad, statut AS booking_status, cmi_status,
               contrat_pdf_url, contrat_sha256, cree_le AS created_at
        FROM public.reservations
    """,
    """
    CREATE OR REPLACE FUNCTION public.search_articles_geo(
        query_text TEXT DEFAULT NULL,
        cat_filter TEXT DEFAULT NULL,
        min_p DECIMAL DEFAULT NULL,
        max_p DECIMAL DEFAULT NULL,
        user_lat DOUBLE PRECISION DEFAULT NULL,
        user_lng DOUBLE PRECISION DEFAULT NULL,
        radius_km DOUBLE PRECISION DEFAULT NULL,
        only_verified BOOLEAN DEFAULT FALSE,
        p_offset INTEGER DEFAULT 0,
        p_limit INTEGER DEFAULT 20
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
               u.id, u.nom_complet, u.note, (u.statut_verification = 'approuve'), COUNT(*) OVER()
        FROM public.articles a
        JOIN public.utilisateurs u ON a.loueur_id = u.id
        WHERE a.statut = 'actif'
          AND (query_text IS NULL OR a.titre ILIKE '%' || query_text || '%' OR a.description ILIKE '%' || query_text || '%')
          AND (cat_filter IS NULL OR cat_filter = 'all' OR a.categorie = cat_filter)
          AND (min_p IS NULL OR a.prix_par_jour >= min_p)
          AND (max_p IS NULL OR a.prix_par_jour <= max_p)
          AND (only_verified IS FALSE OR u.statut_verification = 'approuve')
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
    """,
]


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "postgis"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names(schema="public"))
    managed_existing = existing_tables & MANAGED_TABLES

    if managed_existing:
        missing_core = CORE_TABLES - existing_tables
        if missing_core:
            names = ", ".join(sorted(missing_core))
            raise RuntimeError(
                "Refusing to baseline a partial Lokiini schema. "
                f"Missing core tables: {names}"
            )
    else:
        for statement in CREATE_TABLE_STATEMENTS:
            op.execute(statement)

    # Safe, additive reconciliation for databases created by the legacy startup path.
    op.execute("ALTER TABLE public.utilisateurs ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(128)")
    op.execute("ALTER TABLE public.utilisateurs ALTER COLUMN email DROP NOT NULL")
    op.execute("ALTER TABLE public.utilisateurs ALTER COLUMN telephone DROP NOT NULL")
    op.execute("ALTER TABLE public.utilisateurs ALTER COLUMN hashed_password DROP NOT NULL")
    op.execute("ALTER TABLE public.articles ADD COLUMN IF NOT EXISTS localisation GEOMETRY(Point, 4326)")
    op.execute("ALTER TABLE public.remises ADD COLUMN IF NOT EXISTS geolocalisation GEOMETRY(Point, 4326)")

    inspector = sa.inspect(op.get_bind())
    if "cmi_transactions" not in inspector.get_table_names(schema="public"):
        op.execute(CREATE_CMI_TRANSACTIONS)
    else:
        op.execute("ALTER TABLE public.cmi_transactions ALTER COLUMN id SET DEFAULT gen_random_uuid()")

    op.execute("DROP VIEW IF EXISTS public.bookings")
    op.execute("DROP VIEW IF EXISTS public.equipment")
    op.execute("DROP VIEW IF EXISTS public.users")
    for statement in SUPPORTING_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS public.search_articles_geo(TEXT, TEXT, DECIMAL, DECIMAL, DOUBLE PRECISION, DOUBLE PRECISION, DOUBLE PRECISION, BOOLEAN, INTEGER, INTEGER)")
    op.execute("DROP VIEW IF EXISTS public.bookings")
    op.execute("DROP VIEW IF EXISTS public.equipment")
    op.execute("DROP VIEW IF EXISTS public.users")
    for table_name in [
        "cmi_transactions",
        "notifications",
        "litiges",
        "abonnements",
        "avis",
        "messages",
        "conversations",
        "confirmations_cash",
        "remises",
        "reservations",
        "articles",
        "utilisateurs",
    ]:
        op.execute(f"DROP TABLE IF EXISTS public.{table_name} CASCADE")
