-- ==============================================================================
-- LOKIINI - SCHEMA POSTGRESQL 16 / SUPABASE CONFORME MINDMAP 2026
-- Marketplace Universelle de Location au Maroc (COD, KYC Didit, CNDP)
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 1. TABLE: utilisateurs
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    telephone TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    nom_complet TEXT NOT NULL,
    avatar_url TEXT,
    role TEXT DEFAULT 'particulier', -- 'particulier', 'pro', 'admin'
    statut_verification TEXT DEFAULT 'en_attente' CHECK (statut_verification IN ('en_attente', 'approuve', 'rejete', 'revision_manuelle')),
    didit_session_id TEXT,
    verifie_le TIMESTAMP WITH TIME ZONE,
    note NUMERIC(3,2) DEFAULT 5.00,
    date_inscription TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    temps_reponse_minutes INTEGER DEFAULT 15,
    plan_abonnement TEXT DEFAULT 'Gratuit' CHECK (plan_abonnement IN ('Gratuit', 'Premium', 'Pro', 'Entreprise')),
    abonnement_valable_jusqu TIMESTAMP WITH TIME ZONE,
    ville TEXT DEFAULT 'Casablanca',
    adresse TEXT,
    company_name TEXT,
    company_ice TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 2. TABLE: articles
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loueur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    categorie TEXT NOT NULL, -- outils, electronique, musique, evenementiel, outdoor, velos, btp
    titre TEXT NOT NULL,
    description TEXT NOT NULL,
    photos JSONB DEFAULT '[]',
    prix_par_jour NUMERIC(10,2) NOT NULL,
    montant_caution NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    niveau_risque TEXT DEFAULT 'faible' CHECK (niveau_risque IN ('faible', 'moyen', 'eleve')),
    ville TEXT NOT NULL DEFAULT 'Casablanca',
    adresse TEXT,
    localisation JSONB DEFAULT '{"lat": 33.5731, "lng": -7.5898}', -- Coordonnées Casablanca
    calendrier_disponibilite JSONB DEFAULT '{"dates_bloquees": []}',
    statut TEXT DEFAULT 'actif' CHECK (statut IN ('actif', 'en_pause', 'archive', 'en_revision')),
    nb_vues INTEGER DEFAULT 0,
    specs JSONB DEFAULT '{}',
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 3. TABLE: reservations (Flux Cash on Delivery / COD)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE RESTRICT,
    locataire_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE RESTRICT,
    loueur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE RESTRICT,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    prix_total NUMERIC(10,2) NOT NULL,
    montant_caution NUMERIC(10,2) NOT NULL,
    option_livraison TEXT DEFAULT 'retrait_sur_place' CHECK (option_livraison IN ('retrait_sur_place', 'livraison_premium')),
    adresse_retrait TEXT,
    statut TEXT DEFAULT 'en_attente_approbation' CHECK (statut IN (
        'en_attente_verification', 
        'en_attente_approbation', 
        'confirme_cod', 
        'en_cours', 
        'en_attente_validation', 
        'termine', 
        'annule', 
        'en_litige'
    )),
    contrat_pdf_url TEXT,
    contrat_signe BOOLEAN DEFAULT FALSE,
    contrat_signe_le TIMESTAMP WITH TIME ZONE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 4. TABLE: remises (États des lieux contradictoires Retrait & Retour)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS remises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID NOT NULL REFERENCES reservations(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('retrait', 'retour')),
    photos JSONB DEFAULT '[]',
    videos JSONB DEFAULT '[]',
    geolocalisation JSONB DEFAULT '{}',
    horodatage TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    signatures JSONB DEFAULT '{"locataire": null, "loueur": null}',
    statut TEXT DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'confirme')),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 5. TABLE: confirmations_cash (Validation du paiement en espèces)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS confirmations_cash (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID NOT NULL REFERENCES reservations(id) ON DELETE CASCADE,
    montant_recu NUMERIC(10,2) NOT NULL,
    confirme_par UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE RESTRICT,
    confirme_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

-- ------------------------------------------------------------------------------
-- 6. TABLE: conversations & messages
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID REFERENCES reservations(id) ON DELETE SET NULL,
    participant1_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    participant2_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    dernier_message_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    reservation_id UUID REFERENCES reservations(id) ON DELETE SET NULL,
    expediteur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    contenu TEXT NOT NULL,
    lu BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 7. TABLE: avis
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS avis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID NOT NULL REFERENCES reservations(id) ON DELETE CASCADE,
    avisateur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE RESTRICT,
    avise_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE RESTRICT,
    note INTEGER NOT NULL CHECK (note BETWEEN 1 AND 5),
    commentaire TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 8. TABLE: abonnements
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS abonnements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    plan TEXT NOT NULL CHECK (plan IN ('Gratuit', 'Premium', 'Pro', 'Entreprise')),
    taux_commission NUMERIC(5,2) NOT NULL DEFAULT 15.00,
    prix_mad NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    debute_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expire_le TIMESTAMP WITH TIME ZONE,
    statut TEXT DEFAULT 'actif' CHECK (statut IN ('actif', 'expire', 'annule')),
    fonctionnalites JSONB DEFAULT '[]'
);

-- ------------------------------------------------------------------------------
-- 9. TABLE: litiges
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS litiges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID NOT NULL REFERENCES reservations(id) ON DELETE CASCADE,
    soumis_par UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE RESTRICT,
    motif TEXT NOT NULL,
    description TEXT NOT NULL,
    photos JSONB DEFAULT '[]',
    statut TEXT DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'resolu', 'clos')),
    notes_resolution TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolu_le TIMESTAMP WITH TIME ZONE
);

-- ------------------------------------------------------------------------------
-- 10. TABLE: notifications
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('reservation', 'message', 'systeme', 'paiement')),
    titre TEXT NOT NULL,
    corps TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    lu BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================================================
-- INDEX DE PERFORMANCE & CONTRAINTES
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_articles_categorie_statut ON articles(categorie, statut);
CREATE INDEX IF NOT EXISTS idx_articles_prix ON articles(prix_par_jour);
CREATE INDEX IF NOT EXISTS idx_articles_ville ON articles(ville);
CREATE INDEX IF NOT EXISTS idx_reservations_dates ON reservations(date_debut, date_fin);
CREATE INDEX IF NOT EXISTS idx_reservations_statut ON reservations(statut);
CREATE INDEX IF NOT EXISTS idx_reservations_locataire ON reservations(locataire_id);
CREATE INDEX IF NOT EXISTS idx_reservations_loueur ON reservations(loueur_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_utilisateurs_statut_verification ON utilisateurs(statut_verification);

-- ==============================================================================
-- JEU DE DONNÉES DE DÉMARRAGE (SEED DATA MAROC)
-- ==============================================================================

-- Utilisateurs Démo
INSERT INTO utilisateurs (id, email, telephone, hashed_password, nom_complet, role, statut_verification, verifie_le, note, plan_abonnement, ville, company_name, company_ice)
VALUES 
    (
        'a1111111-1111-1111-1111-111111111111', 
        'contact@atlasbtp.ma', 
        '+212661000001', 
        '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', 
        'Atlas Location BTP Maroc', 
        'pro', 
        'approuve', 
        NOW(), 
        4.95, 
        'Pro', 
        'Casablanca', 
        'Atlas Location BTP SARL', 
        '002345678000045'
    ),
    (
        'a2222222-2222-2222-2222-222222222222', 
        'karim.tazi@gmail.com', 
        '+212662000002', 
        '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', 
        'Karim Tazi', 
        'particulier', 
        'approuve', 
        NOW(), 
        4.85, 
        'Premium', 
        'Casablanca', 
        NULL, 
        NULL
    ),
    (
        'a3333333-3333-3333-3333-333333333333', 
        'booking@redcityprod.ma', 
        '+212663000003', 
        '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', 
        'Red City Prod Marrakech', 
        'pro', 
        'approuve', 
        NOW(), 
        5.00, 
        'Pro', 
        'Marrakech', 
        'Red City Productions SARL', 
        '001987654000089'
    ),
    (
        'a4444444-4444-4444-4444-444444444444', 
        'youssef.berrada@gmail.com', 
        '+212664000004', 
        '$2b$12$e80yqVb0b6rU/8P47tU41.V6p4qQ5zGz9P8BqP3yJ3bH7h0o5q6i', 
        'Youssef Berrada', 
        'particulier', 
        'approuve', 
        NOW(), 
        4.90, 
        'Gratuit', 
        'Rabat', 
        NULL, 
        NULL
    )
ON CONFLICT (id) DO NOTHING;

-- Annonces d'Articles (6 Catégories Phares)
INSERT INTO articles (id, loueur_id, categorie, titre, description, photos, prix_par_jour, montant_caution, niveau_risque, ville, adresse, specs, statut)
VALUES
    (
        'e1111111-1111-1111-1111-111111111111',
        'a1111111-1111-1111-1111-111111111111',
        'outils',
        'Perforateur Burineur Démolition Pro SDS-Max 1500W',
        'Marteau piqueur démolition professionnel Bosch 1500W, force de frappe 25 Joules. 4 burins fournis avec coffret.',
        '["/images/jackhammer.jpg"]',
        120.00,
        1000.00,
        'moyen',
        'Casablanca',
        'Ain Sebaa, Casablanca',
        '{"puissance": "1500W", "impact": "25J", "marque": "Bosch Pro"}',
        'actif'
    ),
    (
        'e2222222-2222-2222-2222-222222222222',
        'a3333333-3333-3333-3333-333333333333',
        'electronique',
        'Pack Caméra Cinéma Sony FX3 Full-Frame 4K + Cage XLR',
        'Boîtier cinéma plein format Sony FX3, 2 cartes CFexpress 160Go, 4 batteries, poignée son XLR, objectif 24-70mm f/2.8 GM.',
        '["/images/sony_fx3.jpg"]',
        450.00,
        5000.00,
        'eleve',
        'Marrakech',
        'Guéliz, Marrakech',
        '{"resolution": "4K 120fps", "capteur": "Full-Frame 12MP", "audio": "XLR 4CH"}',
        'actif'
    ),
    (
        'e3333333-3333-3333-3333-333333333333',
        'a4444444-4444-4444-4444-444444444444',
        'musique',
        'Guitare Électro-Acoustique Fender CD-60SCE + Ampli Fishman',
        'Table en épicéa massif, pan coupé, micro et préampli Fishman intégrés avec accordeur. Housse et câble jack inclus.',
        '["/images/guitar_fender.jpg"]',
        90.00,
        800.00,
        'faible',
        'Rabat',
        'Agdal, Rabat',
        '{"marque": "Fender", "preamp": "Fishman Classic", "accessoires": "Housse + Stand"}',
        'actif'
    ),
    (
        'e4444444-4444-4444-4444-444444444444',
        'a1111111-1111-1111-1111-111111111111',
        'evenementiel',
        'Pack Sonorisation JBL PartyBox 710 (800W RMS) + 2 Micros Sans Fil',
        'Enceinte de soirée ultra-puissante 800W avec jeux de lumières dynamiques synchronisés, entrées guitare et micros.',
        '["/images/partybox.jpg"]',
        250.00,
        2000.00,
        'moyen',
        'Casablanca',
        'Maârif, Casablanca',
        '{"puissance": "800W RMS", "lumieres": "RGB LED", "micros": "2 UHF Wireless"}',
        'actif'
    ),
    (
        'e5555555-5555-5555-5555-555555555555',
        'a2222222-2222-2222-2222-222222222222',
        'outdoor',
        'Tente de Toit Voiture 4 Saisons 2/3 Personnes Hussarde',
        'Tente de toit rigide ouverture rapide 30s, matelas haute densité mémoire de forme, échelle télescopique alu incluse.',
        '["/images/roof_tent.jpg"]',
        180.00,
        1500.00,
        'moyen',
        'Casablanca',
        'Bourgogne, Casablanca',
        '{"capacite": "2-3 Personnes", "matelas": "140x200cm", "compatibilite": "Barres de toit"}',
        'actif'
    ),
    (
        'e6666666-6666-6666-6666-666666666666',
        'a1111111-1111-1111-1111-111111111111',
        'velos',
        'Remorque Porte-Motos / Porte-Vélos Basculante 500kg',
        'Remorque galvanisée homologuée route avec rampe de montée, antivol tête d''attelage et roue jockey.',
        '["/images/trailer_500kg.jpg"]',
        140.00,
        1200.00,
        'moyen',
        'Casablanca',
        'Sidi Maarouf, Casablanca',
        '{"charge_utile": "500 kg", "prise": "7 broches", "rampe": "Fournie"}',
        'actif'
    )
ON CONFLICT (id) DO NOTHING;

-- Seed Réservations
INSERT INTO reservations (id, article_id, locataire_id, loueur_id, date_debut, date_fin, prix_total, montant_caution, option_livraison, statut, contrat_signe)
VALUES 
    (
        'b1111111-1111-1111-1111-111111111111',
        'e1111111-1111-1111-1111-111111111111',
        'a2222222-2222-2222-2222-222222222222',
        'a1111111-1111-1111-1111-111111111111',
        CURRENT_DATE + INTERVAL '1 day',
        CURRENT_DATE + INTERVAL '3 day',
        240.00,
        1000.00,
        'retrait_sur_place',
        'confirme_cod',
        TRUE
    )
ON CONFLICT (id) DO NOTHING;

-- Seed Avis
INSERT INTO avis (id, reservation_id, avisateur_id, avise_id, note, commentaire)
VALUES
    (
        'c1111111-1111-1111-1111-111111111111',
        'b1111111-1111-1111-1111-111111111111',
        'a2222222-2222-2222-2222-222222222222',
        'a1111111-1111-1111-1111-111111111111',
        5,
        'Matériel en parfait état de fonctionnement, remise ponctuelle et loueur très professionnel !'
    )
ON CONFLICT (id) DO NOTHING;
