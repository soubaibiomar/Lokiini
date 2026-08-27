-- ==============================================================================
-- LOKIINI / MATOS - POSTGRESQL 16 INITIALIZATION SCRIPT
-- Moroccan Equipment Rental Marketplace with CNDP & CMI Escrow Integration
-- ==============================================================================

-- 1. Enable pgcrypto extension for CNDP compliance (encrypted CIN storage)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    cin_number VARCHAR(100), -- Encrypted Moroccan CIN
    is_kyc_verified BOOLEAN DEFAULT FALSE,
    kyc_liveness_score NUMERIC(5,2) DEFAULT 0.00,
    kyc_verified_at TIMESTAMP WITH TIME ZONE,
    user_role VARCHAR(20) DEFAULT 'renter', -- renter, owner, pro_owner, admin
    company_name VARCHAR(150),
    company_ice VARCHAR(20), -- Identifiant Commun de l'Entreprise (ICE Maroc)
    city VARCHAR(50) DEFAULT 'Casablanca',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create Equipment Table
CREATE TABLE IF NOT EXISTS equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL, -- btp, tools, cleaning, energy, audiovisual, heating
    city VARCHAR(50) NOT NULL, -- Casablanca, Rabat, Marrakech, Tanger, Fès, Agadir, Oujda
    address TEXT,
    daily_price_mad NUMERIC(10,2) NOT NULL,
    deposit_amount_mad NUMERIC(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT TRUE,
    discount_pct INTEGER DEFAULT 0,
    specs_json JSONB DEFAULT '{}',
    images_urls JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID NOT NULL REFERENCES equipment(id) ON DELETE RESTRICT,
    renter_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    daily_rate_applied_mad NUMERIC(10,2) NOT NULL,
    rental_total_mad NUMERIC(10,2) NOT NULL,
    platform_commission_mad NUMERIC(10,2) NOT NULL,
    deposit_hold_mad NUMERIC(10,2) NOT NULL,
    booking_status VARCHAR(30) DEFAULT 'pending', -- pending, confirmed, in_progress, completed, cancelled, disputed
    cmi_status VARCHAR(30) DEFAULT 'pending_preauth', -- pending_preauth, held, captured, released
    contract_pdf_url TEXT,
    contract_sha256 VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create CMI Transactions Table
CREATE TABLE IF NOT EXISTS cmi_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    cmi_auth_token VARCHAR(255) NOT NULL,
    cmi_trans_id VARCHAR(100),
    card_brand VARCHAR(20) DEFAULT 'CMI/VISA',
    preauth_amount_mad NUMERIC(10,2) NOT NULL,
    captured_amount_mad NUMERIC(10,2) DEFAULT 0.00,
    deposit_status VARCHAR(20) DEFAULT 'held', -- held, released, captured
    released_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Create Inspection Reports Table
CREATE TABLE IF NOT EXISTS inspection_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    type VARCHAR(10) NOT NULL, -- check_in, check_out
    video_url TEXT NOT NULL,
    video_sha256_hash VARCHAR(64) NOT NULL,
    rfc3161_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    signed_by_owner BOOLEAN DEFAULT FALSE,
    signed_by_renter BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Create Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    target_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    rating_score INTEGER NOT NULL CHECK (rating_score BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================================================
-- SEED DATA (Authentic Moroccan Profiles & Professional Equipment)
-- ==============================================================================

-- Seed Users
INSERT INTO users (id, full_name, email, phone_number, hashed_password, is_kyc_verified, kyc_liveness_score, user_role, company_name, company_ice, city)
VALUES 
    ('a1111111-1111-1111-1111-111111111111', 'Atlas Location BTP Maroc', 'contact@atlasbtp.ma', '+212661000001', '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', TRUE, 98.50, 'pro_owner', 'Atlas Location BTP SARL', '002345678000045', 'Casablanca'),
    ('a2222222-2222-2222-2222-222222222222', 'Karim Tazi', 'karim.tazi@gmail.com', '+212662000002', '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', TRUE, 96.00, 'renter', NULL, NULL, 'Casablanca'),
    ('a3333333-3333-3333-3333-333333333333', 'Red City Prod Marrakech', 'booking@redcityprod.ma', '+212663000003', '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', TRUE, 99.00, 'pro_owner', 'Red City Productions Marrakech', '001987654000089', 'Marrakech')
ON CONFLICT (id) DO NOTHING;

-- Seed Equipment Listings with Images
INSERT INTO equipment (id, owner_id, title, description, category, city, address, daily_price_mad, deposit_amount_mad, is_available, is_verified, discount_pct, specs_json, images_urls)
VALUES
    (
        'e1111111-1111-1111-1111-111111111111',
        'a1111111-1111-1111-1111-111111111111',
        'Bétonnière Professionnelle Chantier 160L',
        'Bétonnière robuste cuve 160 litres, moteur électrique 230V puissant, idéale pour coulage de dalles et maçonnerie sur chantier résidentiel ou pro.',
        'btp',
        'Casablanca',
        'Ain Sebaa, Casablanca',
        180.00,
        1500.00,
        TRUE,
        TRUE,
        0,
        '{"capacite": "160L", "moteur": "Electrique 850W", "poids": "55kg"}',
        '["/images/concrete_mixer.jpg"]'
    ),
    (
        'e2222222-2222-2222-2222-222222222222',
        'a1111111-1111-1111-1111-111111111111',
        'Mini-Pelle Compacte Bobcat E19 (1.9 Tonne)',
        'Mini-pelle sur chenilles caoutchouc Bobcat E19 avec canopy, 3 godets fournis (curage + 2 terrassement), brise-roche disponible.',
        'btp',
        'Casablanca',
        'Route de Bouskoura, Casablanca',
        1280.00,
        8000.00,
        TRUE,
        TRUE,
        20,
        '{"poids": "1880 kg", "profondeur": "2.56 m", "moteur": "Diesel Kubota", "godets": "30cm, 60cm, 100cm"}',
        '["/images/mini_excavator.jpg"]'
    ),
    (
        'e3333333-3333-3333-3333-333333333333',
        'a1111111-1111-1111-1111-111111111111',
        'Nettoyeur Haute Pression 180 Bar Thermique',
        'Nettoyeur haute pression thermique à essence Honda GX, débit 900L/h, lance rotative et flexible 15m pour façades, sols et terrasses.',
        'cleaning',
        'Casablanca',
        'Hay Hassani / Oulfa, Casablanca',
        150.00,
        1200.00,
        TRUE,
        TRUE,
        0,
        '{"pression": "180 Bar", "debit": "900 L/h", "moteur": "Essence 6.5 CV", "flexible": "15m"}',
        '["/images/pressure_washer.jpg"]'
    ),
    (
        'e4444444-4444-4444-4444-444444444444',
        'a3333333-3333-3333-3333-333333333333',
        'Caméra Cinéma Sony FX3 4K Full-Frame + Cage XLR',
        'Boîtier cinéma plein format 4K 120fps, profil S-Cinetone, 2 cartes CFexpress 160Go, 4 batteries, cage SmallRig et poignée XLR audio incluse.',
        'audiovisual',
        'Marrakech',
        'Guéliz, Marrakech',
        450.00,
        5000.00,
        TRUE,
        TRUE,
        10,
        '{"capteur": "Full-Frame 12.1 MP", "video": "4K 120p 10-bit 4:2:2", "audio": "XLR 4 canaux", "monture": "Sony E"}',
        '["/images/sony_fx3.jpg"]'
    ),
    (
        'e5555555-5555-5555-5555-555555555555',
        'a1111111-1111-1111-1111-111111111111',
        'Groupe Électrogène Insonorisé 10 kVA Silent',
        'Groupe électrogène silencieux monophasé/triphasé 10kVA, démarrage électrique automatique ATS, réservoir grande autonomie pour chantier ou événement.',
        'energy',
        'Tanger',
        'Tanger Free Zone, Tanger',
        350.00,
        3000.00,
        TRUE,
        TRUE,
        0,
        '{"puissance": "10 kVA / 8 kW", "tension": "230V / 400V", "niveau_sonore": "65 dB(A)", "demarrage": "Electrique ATS"}',
        '["/images/generator_10kva.jpg"]'
    ),
    (
        'e6666666-6666-6666-6666-666666666666',
        'a1111111-1111-1111-1111-111111111111',
        'Perforateur Burineur Démolition Pro SDS-Max',
        'Marteau piqueur démolition lourd 1500W, force de frappe 25 Joules, 4 burins pointus et plats fournis en coffret rigide.',
        'tools',
        'Rabat',
        'Quartier Industriel Agdal, Rabat',
        120.00,
        1000.00,
        TRUE,
        TRUE,
        0,
        '{"puissance": "1500W", "impact": "25 Joules", "emmanchement": "SDS-Max"}',
        '["/images/jackhammer.jpg"]'
    )
ON CONFLICT (id) DO UPDATE SET 
    images_urls = EXCLUDED.images_urls,
    title = EXCLUDED.title,
    description = EXCLUDED.description;
