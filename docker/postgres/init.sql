-- ==============================================================================
-- LOKIINI / MATOS - POSTGRESQL 16 + POSTGIS INITIALIZATION SCRIPT
-- Moroccan Equipment Rental Marketplace with Didit KYC, PostGIS Geosearch & COD
-- ==============================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 2. Table: utilisateurs (Users)
CREATE TABLE IF NOT EXISTS public.utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    telephone VARCHAR(30) UNIQUE NOT NULL,
    nom_complet VARCHAR(150) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    cin_number VARCHAR(100), -- Encrypted CIN
    avatar_url TEXT,
    statut_verification VARCHAR(30) DEFAULT 'en_attente' 
        CHECK (statut_verification IN ('en_attente', 'approuve', 'rejete', 'revision_manuelle')),
    didit_session_id VARCHAR(100),
    verifie_le TIMESTAMP WITH TIME ZONE,
    kyc_liveness_score NUMERIC(5,2) DEFAULT 0.00,
    note NUMERIC(3,2) DEFAULT 5.00,
    temps_reponse_minutes INTEGER DEFAULT 30,
    user_role VARCHAR(30) DEFAULT 'renter' CHECK (user_role IN ('renter', 'owner', 'pro_owner', 'admin')),
    company_name VARCHAR(150),
    company_ice VARCHAR(30), -- Identifiant Commun de l'Entreprise (Maroc)
    city VARCHAR(60) DEFAULT 'Casablanca',
    plan_abonnement VARCHAR(30) DEFAULT 'Gratuit' 
        CHECK (plan_abonnement IN ('Gratuit', 'Premium', 'Pro', 'Entreprise')),
    abonnement_valable_jusqu TIMESTAMP WITH TIME ZONE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Table: articles (Equipment Listings)
CREATE TABLE IF NOT EXISTS public.articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loueur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
    categorie VARCHAR(60) NOT NULL, -- btp, audiovisual, tools, event, outdoor, transport, cleaning, energy
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
    is_verified BOOLEAN DEFAULT TRUE,
    discount_pct INTEGER DEFAULT 0,
    specs_json JSONB DEFAULT '{}'::jsonb,
    nb_vues INTEGER DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Table: reservations (Bookings)
CREATE TABLE IF NOT EXISTS public.reservations (
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
    payment_method VARCHAR(30) DEFAULT 'cash_cod', -- cash_cod, cmi_card, cashplus
    statut VARCHAR(40) DEFAULT 'en_attente_approbation' 
        CHECK (statut IN (
            'en_attente_verification', 
            'en_attente_approbation', 
            'confirme_cod', 
            'en_cours', 
            'en_attente_validation', 
            'termine', 
            'annule', 
            'en_litige'
        )),
    cmi_status VARCHAR(30) DEFAULT 'pending_cod',
    contrat_pdf_url TEXT,
    contrat_sha256 VARCHAR(64),
    contrat_signe BOOLEAN DEFAULT FALSE,
    contrat_signe_le TIMESTAMP WITH TIME ZONE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Table: remises (Inspection Reports / Handoff)
CREATE TABLE IF NOT EXISTS public.remises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('retrait', 'retour')),
    photos JSONB DEFAULT '[]'::jsonb,
    videos JSONB DEFAULT '[]'::jsonb,
    video_url TEXT,
    video_sha256_hash VARCHAR(64),
    geolocalisation GEOMETRY(Point, 4326),
    horodatage TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    signatures JSONB DEFAULT '{}'::jsonb,
    signed_by_owner BOOLEAN DEFAULT FALSE,
    signed_by_renter BOOLEAN DEFAULT FALSE,
    notes TEXT,
    statut VARCHAR(30) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'confirme')),
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Table: confirmations_cash (Cash on Delivery Receipt)
CREATE TABLE IF NOT EXISTS public.confirmations_cash (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
    montant_recu NUMERIC(10,2) NOT NULL,
    confirme_par UUID NOT NULL REFERENCES public.utilisateurs(id),
    confirme_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

-- 7. Table: conversations
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID REFERENCES public.reservations(id) ON DELETE SET NULL,
    participant1_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
    participant2_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
    dernier_message_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT participants_differents CHECK (participant1_id <> participant2_id)
);

-- 8. Table: messages
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    expediteur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
    contenu TEXT NOT NULL,
    lu BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. Table: avis (Reviews & Ratings)
CREATE TABLE IF NOT EXISTS public.avis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
    avisateur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
    avise_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
    note INTEGER NOT NULL CHECK (note BETWEEN 1 AND 5),
    commentaire TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. Table: abonnements (Subscriptions)
CREATE TABLE IF NOT EXISTS public.abonnements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
    plan VARCHAR(30) NOT NULL CHECK (plan IN ('Gratuit', 'Premium', 'Pro', 'Entreprise')),
    taux_commission NUMERIC(5,2) NOT NULL,
    prix_mad NUMERIC(10,2) NOT NULL,
    debute_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expire_le TIMESTAMP WITH TIME ZONE,
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'expire', 'annule')),
    fonctionnalites JSONB DEFAULT '[]'::jsonb
);

-- 11. Table: litiges (Disputes)
CREATE TABLE IF NOT EXISTS public.litiges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID NOT NULL REFERENCES public.reservations(id) ON DELETE CASCADE,
    soumis_par UUID NOT NULL REFERENCES public.utilisateurs(id),
    motif VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    photos JSONB DEFAULT '[]'::jsonb,
    statut VARCHAR(30) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'resolu', 'clos')),
    notes_resolution TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolu_le TIMESTAMP WITH TIME ZONE
);

-- 12. Table: notifications
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES public.utilisateurs(id) ON DELETE CASCADE,
    type VARCHAR(30) NOT NULL CHECK (type IN ('reservation', 'message', 'systeme', 'paiement')),
    titre VARCHAR(255) NOT NULL,
    corps TEXT NOT NULL,
    data JSONB DEFAULT '{}'::jsonb,
    lu BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================================================
-- BACKWARD COMPATIBLE VIEWS (for existing modules)
-- ==============================================================================
CREATE OR REPLACE VIEW users AS 
    SELECT id, nom_complet AS full_name, email, telephone AS phone_number, 
           hashed_password, cin_number, (statut_verification = 'approuve') AS is_kyc_verified,
           kyc_liveness_score, verifie_le AS kyc_verified_at, user_role, company_name, 
           company_ice, city, cree_le AS created_at
    FROM public.utilisateurs;

CREATE OR REPLACE VIEW equipment AS
    SELECT id, loueur_id AS owner_id, titre AS title, description, categorie AS category,
           city, adresse AS address, prix_par_jour AS daily_price_mad, montant_caution AS deposit_amount_mad,
           is_available, is_verified, discount_pct, specs_json, photos AS images_urls, cree_le AS created_at
    FROM public.articles;

CREATE OR REPLACE VIEW bookings AS
    SELECT id, article_id AS equipment_id, locataire_id AS renter_id, date_debut AS start_date,
           date_fin AS end_date, total_days, (prix_total / NULLIF(total_days, 0)) AS daily_rate_applied_mad,
           prix_total AS rental_total_mad, (prix_total * 0.15) AS platform_commission_mad,
           montant_caution AS deposit_hold_mad, statut AS booking_status, cmi_status,
           contrat_pdf_url, contrat_sha256, cree_le AS created_at
    FROM public.reservations;

-- ==============================================================================
-- INDEXES & PERFORMANCE
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_articles_localisation ON public.articles USING GIST(localisation);
CREATE INDEX IF NOT EXISTS idx_articles_categorie_statut ON public.articles(categorie, statut);
CREATE INDEX IF NOT EXISTS idx_articles_prix ON public.articles(prix_par_jour);
CREATE INDEX IF NOT EXISTS idx_articles_titre_trgm ON public.articles USING gin (titre gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_reservations_dates ON public.reservations(date_debut, date_fin);
CREATE INDEX IF NOT EXISTS idx_reservations_statut ON public.reservations(statut);
CREATE INDEX IF NOT EXISTS idx_reservations_locataire ON public.reservations(locataire_id);
CREATE INDEX IF NOT EXISTS idx_reservations_loueur ON public.reservations(loueur_id);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON public.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_lu ON public.notifications(utilisateur_id, lu);

-- ==============================================================================
-- POSTGIS STORED PROCEDURE: search_articles_geo
-- ==============================================================================
CREATE OR REPLACE FUNCTION search_articles_geo(
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
)
RETURNS TABLE (
    id UUID,
    titre VARCHAR(255),
    categorie VARCHAR(60),
    prix_par_jour NUMERIC(10,2),
    montant_caution NUMERIC(10,2),
    photos JSONB,
    statut VARCHAR(30),
    city VARCHAR(60),
    adresse TEXT,
    distance_km DOUBLE PRECISION,
    loueur_id UUID,
    loueur_nom VARCHAR(150),
    loueur_note NUMERIC(3,2),
    loueur_verifie BOOLEAN,
    total_records BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.titre,
        a.categorie,
        a.prix_par_jour,
        a.montant_caution,
        a.photos,
        a.statut,
        a.city,
        a.adresse,
        CASE 
            WHEN user_lat IS NOT NULL AND user_lng IS NOT NULL AND a.localisation IS NOT NULL THEN
                ST_DistanceSphere(a.localisation, ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326)) / 1000.0
            ELSE 0.0
        END AS distance_km,
        u.id AS loueur_id,
        u.nom_complet AS loueur_nom,
        u.note AS loueur_note,
        (u.statut_verification = 'approuve') AS loueur_verifie,
        COUNT(*) OVER() AS total_records
    FROM public.articles a
    JOIN public.utilisateurs u ON a.loueur_id = u.id
    WHERE a.statut = 'actif'
      AND (query_text IS NULL OR a.titre ILIKE '%' || query_text || '%' OR a.description ILIKE '%' || query_text || '%')
      AND (cat_filter IS NULL OR cat_filter = 'all' OR a.categorie = cat_filter)
      AND (min_p IS NULL OR a.prix_par_jour >= min_p)
      AND (max_p IS NULL OR a.prix_par_jour <= max_p)
      AND (only_verified IS FALSE OR u.statut_verification = 'approuve')
      AND (
          user_lat IS NULL OR user_lng IS NULL OR radius_km IS NULL OR a.localisation IS NULL OR
          ST_DWithin(a.localisation::geography, ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326)::geography, radius_km * 1000)
      )
    ORDER BY 
        CASE WHEN user_lat IS NOT NULL AND user_lng IS NOT NULL AND a.localisation IS NOT NULL THEN
            ST_DistanceSphere(a.localisation, ST_SetSRID(ST_MakePoint(user_lng, user_lat), 4326))
        END ASC NULLS LAST,
        a.cree_le DESC
    OFFSET p_offset LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==============================================================================
-- SEED DATA (Authentic Moroccan Profiles, Equipment with PostGIS Geolocation)
-- ==============================================================================

-- 1. Seed Utilisateurs
INSERT INTO public.utilisateurs (
    id, email, telephone, nom_complet, hashed_password, cin_number, 
    statut_verification, verifie_le, kyc_liveness_score, note, user_role, 
    company_name, company_ice, city, plan_abonnement
)
VALUES 
    (
        'a1111111-1111-1111-1111-111111111111', 
        'contact@atlasbtp.ma', 
        '+212661000001', 
        'Atlas Location BTP Maroc', 
        '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', 
        'BK849201', 
        'approuve', 
        NOW(), 
        98.50, 
        4.95, 
        'pro_owner', 
        'Atlas Location BTP SARL', 
        '002345678000045', 
        'Casablanca', 
        'Pro'
    ),
    (
        'a2222222-2222-2222-2222-222222222222', 
        'karim.tazi@gmail.com', 
        '+212662000002', 
        'Karim Tazi', 
        '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', 
        'BE918234', 
        'approuve', 
        NOW(), 
        96.00, 
        4.85, 
        'renter', 
        NULL, 
        NULL, 
        'Casablanca', 
        'Gratuit'
    ),
    (
        'a3333333-3333-3333-3333-333333333333', 
        'booking@redcityprod.ma', 
        '+212663000003', 
        'Red City Prod Marrakech', 
        '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', 
        'EE109283', 
        'approuve', 
        NOW(), 
        99.00, 
        5.00, 
        'pro_owner', 
        'Red City Productions SARL-AU', 
        '001987654000089', 
        'Marrakech', 
        'Premium'
    )
ON CONFLICT (id) DO NOTHING;

-- 2. Seed Articles / Equipment (With PostGIS Point: lng, lat)
INSERT INTO public.articles (
    id, loueur_id, categorie, titre, description, photos, 
    prix_par_jour, montant_caution, niveau_risque, localisation, 
    city, adresse, specs_json, discount_pct, is_available, is_verified
)
VALUES
    (
        'e1111111-1111-1111-1111-111111111111',
        'a1111111-1111-1111-1111-111111111111',
        'btp',
        'Bétonnière Professionnelle Chantier 160L',
        'Bétonnière robuste cuve 160 litres, moteur électrique 230V puissant, idéale pour coulage de dalles et maçonnerie sur chantier résidentiel ou pro.',
        '["/images/concrete_mixer.jpg"]'::jsonb,
        180.00,
        1500.00,
        'eleve',
        ST_SetSRID(ST_MakePoint(-7.5321, 33.5972), 4326), -- Ain Sebaa, Casablanca
        'Casablanca',
        'Ain Sebaa, Casablanca',
        '{"capacite": "160L", "moteur": "Electrique 850W", "poids": "55kg"}'::jsonb,
        0,
        TRUE,
        TRUE
    ),
    (
        'e2222222-2222-2222-2222-222222222222',
        'a1111111-1111-1111-1111-111111111111',
        'btp',
        'Mini-Pelle Compacte Bobcat E19 (1.9 Tonne)',
        'Mini-pelle sur chenilles caoutchouc Bobcat E19 avec canopy, 3 godets fournis (curage + 2 terrassement), brise-roche disponible.',
        '["/images/mini_excavator.jpg"]'::jsonb,
        1280.00,
        8000.00,
        'eleve',
        ST_SetSRID(ST_MakePoint(-7.6480, 33.5240), 4326), -- Route de Bouskoura, Casablanca
        'Casablanca',
        'Route de Bouskoura, Casablanca',
        '{"poids": "1880 kg", "profondeur": "2.56 m", "moteur": "Diesel Kubota"}'::jsonb,
        20,
        TRUE,
        TRUE
    ),
    (
        'e3333333-3333-3333-3333-333333333333',
        'a1111111-1111-1111-1111-111111111111',
        'cleaning',
        'Nettoyeur Haute Pression 180 Bar Thermique',
        'Nettoyeur haute pression thermique à essence Honda GX, débit 900L/h, lance rotative et flexible 15m pour façades, sols et terrasses.',
        '["/images/pressure_washer.jpg"]'::jsonb,
        150.00,
        1200.00,
        'moyen',
        ST_SetSRID(ST_MakePoint(-7.6680, 33.5650), 4326), -- Hay Hassani, Casablanca
        'Casablanca',
        'Hay Hassani / Oulfa, Casablanca',
        '{"pression": "180 Bar", "debit": "900 L/h", "moteur": "Essence 6.5 CV"}'::jsonb,
        0,
        TRUE,
        TRUE
    ),
    (
        'e4444444-4444-4444-4444-444444444444',
        'a3333333-3333-3333-3333-333333333333',
        'audiovisual',
        'Caméra Cinéma Sony FX3 4K Full-Frame + Cage XLR',
        'Boîtier cinéma plein format 4K 120fps, profil S-Cinetone, 2 cartes CFexpress 160Go, 4 batteries, cage SmallRig et poignée XLR audio incluse.',
        '["/images/sony_fx3.jpg"]'::jsonb,
        450.00,
        5000.00,
        'eleve',
        ST_SetSRID(ST_MakePoint(-8.0080, 31.6340), 4326), -- Guéliz, Marrakech
        'Marrakech',
        'Guéliz, Marrakech',
        '{"capteur": "Full-Frame 12.1 MP", "video": "4K 120p 10-bit", "audio": "XLR Pro"}'::jsonb,
        10,
        TRUE,
        TRUE
    ),
    (
        'e5555555-5555-5555-5555-555555555555',
        'a1111111-1111-1111-1111-111111111111',
        'energy',
        'Groupe Électrogène Insonorisé 10 kVA Silent',
        'Groupe électrogène silencieux monophasé/triphasé 10kVA, démarrage électrique automatique ATS, réservoir grande autonomie pour chantier ou événement.',
        '["/images/generator_10kva.jpg"]'::jsonb,
        350.00,
        3000.00,
        'eleve',
        ST_SetSRID(ST_MakePoint(-5.8040, 35.7595), 4326), -- Tanger Free Zone
        'Tanger',
        'Tanger Free Zone, Tanger',
        '{"puissance": "10 kVA / 8 kW", "tension": "230V / 400V", "bruit": "65 dB"}'::jsonb,
        0,
        TRUE,
        TRUE
    ),
    (
        'e6666666-6666-6666-6666-666666666666',
        'a1111111-1111-1111-1111-111111111111',
        'tools',
        'Perforateur Burineur Démolition Pro SDS-Max',
        'Marteau piqueur démolition lourd 1500W, force de frappe 25 Joules, 4 burins pointus et plats fournis en coffret rigide.',
        '["/images/jackhammer.jpg"]'::jsonb,
        120.00,
        1000.00,
        'moyen',
        ST_SetSRID(ST_MakePoint(-6.8498, 34.0132), 4326), -- Agdal, Rabat
        'Rabat',
        'Quartier Industriel Agdal, Rabat',
        '{"puissance": "1500W", "impact": "25 Joules", "emmanchement": "SDS-Max"}'::jsonb,
        0,
        TRUE,
        TRUE
    ),
    (
        'e7777777-7777-7777-7777-777777777777',
        'a3333333-3333-3333-3333-333333333333',
        'event',
        'Tente Caïdale Traditionnelle Marocaine 50m²',
        'Tente artisanale de réception doublée rouge/vert avec motifs traditionnels pour mariages, dîners et événements.',
        '["https://images.unsplash.com/photo-1519741497674-611481863552?w=800"]'::jsonb,
        1200.00,
        4000.00,
        'moyen',
        ST_SetSRID(ST_MakePoint(-8.0080, 31.6340), 4326),
        'Marrakech',
        'Palmeraie, Marrakech',
        '{"surface": "50 m²", "capacite": "80 personnes"}'::jsonb,
        15,
        TRUE,
        TRUE
    ),
    (
        'e8888888-8888-8888-8888-888888888888',
        'a1111111-1111-1111-1111-111111111111',
        'vehicles',
        'Fourgon Utilitaire 12m³ Renault Master avec Hayon',
        'Camionnette utilitaire diesel permis B avec hayon hydraulique 500kg.',
        '["https://images.unsplash.com/photo-1559297434-fae8a1916a79?w=800"]'::jsonb,
        450.00,
        3500.00,
        'eleve',
        ST_SetSRID(ST_MakePoint(-7.5321, 33.5972), 4326),
        'Casablanca',
        'Ain Sebaa, Casablanca',
        '{"volume": "12 m³", "permis": "Permis B"}'::jsonb,
        10,
        TRUE,
        TRUE
    ),
    (
        'e9999999-9999-9999-9999-999999999999',
        'a2222222-2222-2222-2222-222222222222',
        'hightech',
        'Pack Casque VR Meta Quest 3 512Go',
        'Casque de réalité mixte 4K+ pour animations salon, corporate et gaming.',
        '["https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=800"]'::jsonb,
        200.00,
        2000.00,
        'faible',
        ST_SetSRID(ST_MakePoint(-6.8498, 34.0132), 4326),
        'Rabat',
        'Technopolis, Rabat',
        '{"stockage": "512 Go", "resolution": "4K+"}'::jsonb,
        0,
        TRUE,
        TRUE
    )
ON CONFLICT (id) DO UPDATE SET 
    photos = EXCLUDED.photos,
    titre = EXCLUDED.titre,
    description = EXCLUDED.description;
