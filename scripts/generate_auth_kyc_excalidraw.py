"""
Lokiini Auth & KYC Comprehensive Excalidraw Generator
Generates an ultra-detailed, professional architecture diagram covering:
1. Use Cases (Consumer Renter, Pro Loueur BTP with ICE, Lokiini Compliance)
2. Frontend Architecture (React Web & React Native Mobile, AuthModal, KYCCameraScreen, Token Storage)
3. Backend Architecture (FastAPI Routers, JWT Security, ML Biometrics, CNDP Audit)
4. PostgreSQL 16 & pgcrypto Schema (Users, Roles, KYC Hashes, Relations)
5. End-to-End Interconnected Sequence Flow & Data Transitions
"""

import json
import random
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class ExcalidrawBuilder:
    def __init__(self):
        self.elements = []
        self.counter = 0

    def get_id(self, prefix="elem"):
        self.counter += 1
        return f"{prefix}_{self.counter}_{random.randint(1000, 9999)}"

    def add_rect(self, x, y, w, h, bg_color="#FFFFFF", stroke_color="#1E293B", stroke_width=1, stroke_style="solid", fill_style="solid", opacity=100, roundness=None, frame_id=None):
        elem_id = self.get_id("rect")
        elem = {
            "id": elem_id,
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": bg_color,
            "fillStyle": fill_style,
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "roughness": 0,
            "opacity": opacity,
            "groupIds": [],
            "roundness": roundness or {"type": 3},
            "seed": random.randint(1, 1000000),
            "version": 1,
            "versionNonce": random.randint(1, 1000000),
            "isDeleted": False,
            "boundElements": [],
            "updated": int(time.time()),
            "link": None,
            "locked": False,
            "frameId": frame_id
        }
        self.elements.append(elem)
        return elem_id

    def add_text(self, x, y, text, font_size=14, font_family=2, text_align="left", color="#1E293B", font_weight="normal", container_id=None, frame_id=None):
        elem_id = self.get_id("text")
        # Approximate line count & width
        lines = text.split("\n")
        line_height = font_size * 1.35
        text_height = len(lines) * line_height
        max_line_len = max(len(l) for l in lines) if lines else 1
        text_width = max_line_len * (font_size * 0.58)

        elem = {
            "id": elem_id,
            "type": "text",
            "x": x,
            "y": y,
            "width": text_width,
            "height": text_height,
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "seed": random.randint(1, 1000000),
            "version": 1,
            "versionNonce": random.randint(1, 1000000),
            "isDeleted": False,
            "boundElements": None,
            "updated": int(time.time()),
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": font_family,
            "textAlign": text_align,
            "verticalAlign": "top",
            "containerId": container_id,
            "originalText": text,
            "lineHeight": 1.35,
            "frameId": frame_id
        }
        self.elements.append(elem)
        return elem_id

    def add_card_with_title(self, x, y, w, h, title, content_lines, header_bg="#0F6E56", body_bg="#FFFFFF", border_color="#CBD5E1", title_color="#FFFFFF", frame_id=None):
        # Outer box
        rect_id = self.add_rect(x, y, w, h, bg_color=body_bg, stroke_color=border_color, stroke_width=1.5, frame_id=frame_id)
        # Header banner
        header_h = 36
        self.add_rect(x, y, w, header_h, bg_color=header_bg, stroke_color=border_color, stroke_width=1, frame_id=frame_id)
        # Title text
        self.add_text(x + 14, y + 9, title, font_size=14, font_family=2, color=title_color, frame_id=frame_id)
        # Content lines
        body_y = y + header_h + 12
        full_content = "\n".join(content_lines)
        self.add_text(x + 14, body_y, full_content, font_size=12, font_family=2, color="#334155", frame_id=frame_id)
        return rect_id

    def add_arrow(self, start_x, start_y, end_x, end_y, label="", stroke_color="#0F6E56", stroke_width=2, stroke_style="solid", frame_id=None):
        elem_id = self.get_id("arrow")
        dx = end_x - start_x
        dy = end_y - start_y
        elem = {
            "id": elem_id,
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": abs(dx),
            "height": abs(dy),
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": stroke_style,
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "roundness": {"type": 2},
            "seed": random.randint(1, 1000000),
            "version": 1,
            "versionNonce": random.randint(1, 1000000),
            "isDeleted": False,
            "boundElements": [],
            "updated": int(time.time()),
            "link": None,
            "locked": False,
            "points": [[0, 0], [dx, dy]],
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "frameId": frame_id
        }
        self.elements.append(elem)

        if label:
            mid_x = start_x + (dx * 0.5) - 30
            mid_y = start_y + (dy * 0.5) - 18
            self.add_rect(mid_x - 6, mid_y - 2, len(label) * 7.5 + 12, 20, bg_color="#FFFFFF", stroke_color="#E2E8F0", stroke_width=1, opacity=95, frame_id=frame_id)
            self.add_text(mid_x, mid_y, label, font_size=10, font_family=2, color=stroke_color, frame_id=frame_id)
        return elem_id

    def build_document(self):
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {
                "gridSize": None,
                "viewBackgroundColor": "#F8FAFC"
            },
            "files": {}
        }


def generate_architecture():
    builder = ExcalidrawBuilder()

    # =========================================================================
    # MASTER TITLE & BRAND HEADER
    # =========================================================================
    builder.add_rect(40, 30, 2520, 110, bg_color="#0F172A", stroke_color="#0F6E56", stroke_width=2)
    builder.add_text(70, 48, "LOKIINI 🇲🇦 — ARCHITECTURE COMPLÈTE AUTHENTIFICATION, LOGIN/REGISTER & KYC BIOMÉTRIQUE CNDP", font_size=22, color="#38BDF8")
    builder.add_text(70, 84, "Cartographie Exhaustive des Cas d'Usage, Composants Frontend (Web & Mobile), API Backend FastAPI, Moteur IA ISO/IEC 30107-3 et Base PostgreSQL 16 (pgcrypto)", font_size=13, color="#94A3B8")

    # =========================================================================
    # COLUMN 1: USE CASES & ACTORS (X: 40 - 580)
    # =========================================================================
    builder.add_rect(40, 160, 520, 1340, bg_color="#FFFFFF", stroke_color="#CBD5E1", stroke_width=1.5)
    builder.add_rect(40, 160, 520, 48, bg_color="#0F6E56", stroke_color="#0F6E56", stroke_width=1)
    builder.add_text(60, 174, "1. CAS D'UTILISATION (USE CASES) & ACTEURS", font_size=16, color="#FFFFFF")

    # Actor 1: Renter
    builder.add_card_with_title(
        65, 230, 470, 190,
        "👤 Acteur : Locataire Particulier (Consumer / Artisan)",
        [
            "• UC-01 : Création de compte (Email, Mot de passe, Téléphone, Nom)",
            "• UC-02 : Connexion par identifiants & réception du JWT Bearer",
            "• UC-03 : Navigation & recherche sans inscription préalable (SEO Libre)",
            "• UC-04 : Déclenchement KYC Just-In-Time au moment de Réserver",
            "• UC-05 : Prise de selfie liveness + scan recto/verso CIN",
            "• UC-06 : Consultation de l'historique des baux & cautions CMI"
        ],
        header_bg="#0F6E56", body_bg="#F0FDF4", border_color="#86EFAC"
    )

    # Actor 2: Pro Owner
    builder.add_card_with_title(
        65, 440, 470, 210,
        "🏢 Acteur : Loueur Professionnel BTP (Entreprise / ICE)",
        [
            "• UC-07 : Inscription Pro avec Raison Sociale, ICE (15 car.) et RC",
            "• UC-08 : Vérification légale d'entreprise & mandat de gérance",
            "• UC-09 : Publication d'annonces matériel & tarification MAD/jour",
            "• UC-10 : Définition du montant de caution séquestrée CMI",
            "• UC-11 : Espace Loueur Pro avec tableau de bord temps réel",
            "• UC-12 : Déclenchement & validation du Check-in / Check-out vidéo",
            "• UC-13 : Signature électronique du bail (Loi n° 53-05)"
        ],
        header_bg="#D85A30", body_bg="#FFF7ED", border_color="#FDBA74"
    )

    # Actor 3: Compliance & CNDP
    builder.add_card_with_title(
        65, 670, 470, 200,
        "🛡️ Acteur : Moteur de Conformité CNDP & Sécurité",
        [
            "• UC-14 : Détection de vivacité faciale anti-deepfake (ISO 30107-3)",
            "• UC-15 : Extraction OCR et validation syntaxique préfectorale CIN",
            "• UC-16 : Émission du certificat Zero-Knowledge (Loi n° 09-08)",
            "• UC-17 : Purge cryptographique irréversible des flux vidéo de la RAM",
            "• UC-18 : Audit journalier automatisé des accès et consentements"
        ],
        header_bg="#1E293B", body_bg="#F8FAFC", border_color="#94A3B8"
    )

    # Actor 4: Lifecycle Matrix
    builder.add_card_with_title(
        65, 890, 470, 260,
        "🔄 Matrice des Transitions d'États Utilisateur",
        [
            "1. ANONYME (Visiteur non connecté) :",
            "   ➔ Consultation catalogue, filtres villes, détails machine",
            "2. INSCRIT_NON_VÉRIFIÉ (Role: Renter / Owner) :",
            "   ➔ Accès dashboard, création brouillons annonces",
            "   ➔ Bloqué pour réservation ferme ou signature de bail",
            "3. KYC_EN_COURS (Upload selfie + CIN) :",
            "   ➔ Traitement ML éphémère (temps réel < 1.2s)",
            "4. KYC_CERTIFIÉ (is_kyc_verified = True) :",
            "   ➔ Déblocage séquestre caution CMI & baux juridiques",
            "5. SUSPENDU (Liveness échec / Fraude avérée) :",
            "   ➔ Révocation des accès et signalement audit CNDP"
        ],
        header_bg="#0284C7", body_bg="#F0F9FF", border_color="#7DD3FC"
    )

    # Key Principles Callout
    builder.add_card_with_title(
        65, 1170, 470, 300,
        "⚡ Principes Clés d'Expérience & Sécurité",
        [
            "• Zero Friction Onboarding : Aucune barrière à l'entrée pour",
            "  visiter le catalogue; l'authentification est contextuelle.",
            "• Just-in-Time KYC : Le contrôle d'identité n'est requis que",
            "  lorsqu'un engagement financier (caution/bail) a lieu.",
            "• RGPD & CNDP Zero-Storage : Les flux caméras ne sont JAMAIS",
            "  enregistrés sur disque dur. Seule l'empreinte SHA-256",
            "  d'attestation est conservée dans la base de données.",
            "• Role-Based Access Control (RBAC) : Isolation stricte entre",
            "  comptes particuliers et loueurs professionnels avec ICE."
        ],
        header_bg="#475569", body_bg="#F1F5F9", border_color="#CBD5E1"
    )

    # =========================================================================
    # COLUMN 2: FRONTEND ARCHITECTURE (X: 590 - 1180)
    # =========================================================================
    builder.add_rect(590, 160, 570, 1340, bg_color="#FFFFFF", stroke_color="#CBD5E1", stroke_width=1.5)
    builder.add_rect(590, 160, 570, 48, bg_color="#0F6E56", stroke_color="#0F6E56", stroke_width=1)
    builder.add_text(610, 174, "2. COUCHE FRONTEND (REACT WEB & REACT NATIVE)", font_size=16, color="#FFFFFF")

    # Component: AuthModal.jsx
    builder.add_card_with_title(
        610, 230, 530, 220,
        "💻 Web : AuthModal.jsx (src/frontend/web/src/components/)",
        [
            "• Bascule interactive Connexion ➔ Inscription",
            "• Sélecteur de profil : 'Particulier' vs 'Loueur Pro BTP'",
            "• Champs Pro conditionnels : ICE (15 chiffres), Raison Sociale",
            "• Validation formulaire en temps réel (Email, Password >= 8 car.)",
            "• Intégration du logo officiel Lokiini sans marges parasites",
            "• Stockage du token : localStorage.setItem('lokiini_token', jwt)",
            "• Déclencheur automatique de rechargement du profil utilisateur"
        ],
        header_bg="#0F6E56", body_bg="#F0FDF4", border_color="#86EFAC"
    )

    # Component: KYCVerificationModal.jsx
    builder.add_card_with_title(
        610, 470, 530, 240,
        "📷 Web : KYCVerificationModal.jsx",
        [
            "• Guide visuel pas-à-pas (Étape 1: CIN ➔ Étape 2: Selfie Vivant)",
            "• Formulaire de saisie CIN avec masque de format (ex: BK849201)",
            "• Simulation flux caméra avec animation radar de détection faciale",
            "• Analyse en direct des micro-mouvements et clignements d'yeux",
            "• Affichage du bandeau de conformité légale CNDP (Loi 09-08)",
            "• Notification de réussite avec score de vivacité (ex: 96.8%)",
            "• Callback 'onSuccess' déclenchant la réactivation de l'action en cours"
        ],
        header_bg="#0F6E56", body_bg="#F0FDF4", border_color="#86EFAC"
    )

    # Component: Mobile Screens
    builder.add_card_with_title(
        610, 730, 530, 230,
        "📱 Mobile : KYCCameraScreen.js & BookingsScreen.js",
        [
            "• Écran KYCCameraScreen.js (React Native / Expo Camera)",
            "• Capture instantanée haute fidélité de la CIN et du visage",
            "• Validation optique embarquée et transmission HTTPS chiffrée",
            "• Écran BookingsScreen.js : Suivi des baux et statut CMI bloqué",
            "• Écran VideoInspectionScreen.js : État des lieux vidéo contradictoire",
            "• Calcul et affichage en surimpression du hachage SHA-256 en continu",
            "• Signature bilatérale sur écran tactile sous Loi 53-05"
        ],
        header_bg="#D85A30", body_bg="#FFF7ED", border_color="#FDBA74"
    )

    # Component: api.js Client & State
    builder.add_card_with_title(
        610, 980, 530, 250,
        "🌐 Service API Client : api.js & Intercepteurs HTTP",
        [
            "• Résolution intelligente URL Gateway (Port 80 Nginx / 8000 Dev)",
            "• authService.login({ email, password }) ➔ JWT Bearer",
            "• authService.register({ email, password, full_name, role, ... })",
            "• authService.getCurrentUser() ➔ GET /api/v1/auth/me",
            "• kycService.verifyCIN({ cin_number, user_id })",
            "• kycService.verifyBiometrics({ cin_number, liveness_score })",
            "• Intercepteur Axios injectant 'Authorization: Bearer <token>'",
            "• Gestion centralisée des erreurs 401 (Auto-déconnexion & redirection)"
        ],
        header_bg="#0284C7", body_bg="#F0F9FF", border_color="#7DD3FC"
    )

    # State Flow Callout
    builder.add_card_with_title(
        610, 1250, 530, 220,
        "🔄 Synchronisation d'État Réactive (App.jsx)",
        [
            "• State global 'currentUser' & 'isKYCVerified' dans App.jsx",
            "• Au montage de l'application : vérification du token dans localStorage",
            "• Si token valide : appel 'authService.getCurrentUser()' pour hydrater",
            "• Navbar dynamique : Affiche Nom/Rôle + Badge 'CIN Vérifiée (CNDP)'",
            "• Bascule instantanée entre Catalogue public et Espace Loueur Pro"
        ],
        header_bg="#475569", body_bg="#F1F5F9", border_color="#CBD5E1"
    )

    # =========================================================================
    # COLUMN 3: BACKEND & ML BIOMETRICS (X: 1190 - 1800)
    # =========================================================================
    builder.add_rect(1190, 160, 590, 1340, bg_color="#FFFFFF", stroke_color="#CBD5E1", stroke_width=1.5)
    builder.add_rect(1190, 160, 590, 48, bg_color="#0F6E56", stroke_color="#0F6E56", stroke_width=1)
    builder.add_text(1210, 174, "3. COUCHE BACKEND FASTAPI & MOTEUR ML BIOMÉTRIQUE", font_size=16, color="#FFFFFF")

    # Router: auth.py & security.py
    builder.add_card_with_title(
        1210, 230, 550, 240,
        "🔐 FastAPI : Routers Auth & Sécurité (src/backend/app/)",
        [
            "• POST /api/v1/auth/register :",
            "   - Validation schémas Pydantic v2 (UserRegisterRequest)",
            "   - Hachage sécurisé du mot de passe via Passlib / Argon2 / bcrypt",
            "   - Création du profil en base PostgreSQL (Rôle RENTER ou PRO_OWNER)",
            "• POST /api/v1/auth/login :",
            "   - Vérification hash mot de passe + vérification compte actif",
            "   - Émission JWT Access Token signé en HMAC-SHA256 (expire: 7j)",
            "• GET /api/v1/auth/me : Dépendance 'get_current_user' avec validation JWT",
            "• PATCH /api/v1/auth/me : Mise à jour profil (téléphone, ICE, adresse)"
        ],
        header_bg="#0F6E56", body_bg="#F0FDF4", border_color="#86EFAC"
    )

    # Router: kyc.py
    builder.add_card_with_title(
        1210, 490, 550, 220,
        "🛡️ FastAPI : Router KYC & Audit (src/backend/app/routers/kyc.py)",
        [
            "• POST /api/v1/kyc/verify-cin :",
            "   - Contrôle regex CIN marocaine ([A-Z]{1,2}[0-9]{5,6})",
            "   - Extraction automatique de la préfecture d'émission",
            "• POST /api/v1/kyc/liveness-check :",
            "   - Analyse biométrique ISO/IEC 30107-3 PAD Niveau 2",
            "   - Génération du jeton d'audit cryptographique CNDP (SHA-256)",
            "   - Mise à jour atomique de l'utilisateur : is_kyc_verified = True",
            "• GET /api/v1/kyc/status/{user_id} : Vérification d'état d'audit"
        ],
        header_bg="#0F6E56", body_bg="#F0FDF4", border_color="#86EFAC"
    )

    # ML Module: liveness_detector.py
    builder.add_card_with_title(
        1210, 730, 550, 240,
        "🧠 Moteur ML : Liveness Detector (src/ml_biometrics/)",
        [
            "• Détection d'Attaque par Présentation (ISO/IEC 30107-3 PAD Level 2) :",
            "   1. Analyse Micro-Texturale Haute Fréquence (Anti-Photo imprimée)",
            "   2. Cohérence de Réflexion Cornéenne & Spéculaire (Anti-Écran rejeu)",
            "   3. Flux Temporel & Analyse du Mouvement Crânien (Head-Turn)",
            "   4. Détection dynamique du clignement d'yeux (Eye-Blink Rate)",
            "• Formule Score Composite :",
            "   Score = (Texture * 0.3) + (Reflet * 0.3) + (Mouvement * 0.2) + (Blink * 0.2)",
            "• Seuil d'Acceptation : >= 85.0% ➔ Certification 'is_live: True'"
        ],
        header_bg="#6366F1", body_bg="#EEF2FF", border_color="#A5B4FC"
    )

    # ML Module: cndp_audit.py & cin_ocr.py
    builder.add_card_with_title(
        1210, 990, 550, 240,
        "📜 Moteur CNDP & OCR CIN (src/ml_biometrics/)",
        [
            "• cin_ocr.py : Parser Préfectoral du Royaume du Maroc",
            "   - Préfixes : BK (Casablanca Anfa), AA (Rabat), EE (Marrakech),",
            "     K (Tanger), CD (Fès), JM (Agadir), F (Oujda), etc.",
            "• cndp_audit.py : Attestation Cryptographique Zero-Knowledge",
            "   - Payload : CNDP_MAROC_09_08|CIN:{cin}|SCORE:{score}|TIME:{utc}",
            "   - Empreinte immuable SHA-256 (64 caractères hexadécimaux)",
            "   - Garantie formelle : Purge intégrale de la RAM volatile",
            "   - Référence déclaration CNDP : CNDP-DEP-2026-MAROC-89421"
        ],
        header_bg="#1E293B", body_bg="#F8FAFC", border_color="#94A3B8"
    )

    # Backend Interconnections Callout
    builder.add_card_with_title(
        1210, 1250, 550, 220,
        "🔗 Interconnexion avec les Baux DOC & Cautions CMI",
        [
            "• Le statut 'is_kyc_verified = True' est un pré-requis bloquant pour :",
            "   1. POST /api/v1/bookings/create (Blocage d'empreinte caution CMI)",
            "   2. POST /api/v1/inspections/seal-checkin (Scellement état des lieux)",
            "   3. GET /api/v1/contracts/booking/{id} (Émission contrat de bail DOC)",
            "• Intégrité contractuelle garantie sous les Art. 627+ du DOC"
        ],
        header_bg="#475569", body_bg="#F1F5F9", border_color="#CBD5E1"
    )

    # =========================================================================
    # COLUMN 4: DATABASE SCHEMA & STORAGE (X: 1810 - 2560)
    # =========================================================================
    builder.add_rect(1810, 160, 750, 1340, bg_color="#FFFFFF", stroke_color="#CBD5E1", stroke_width=1.5)
    builder.add_rect(1810, 160, 750, 48, bg_color="#0F6E56", stroke_color="#0F6E56", stroke_width=1)
    builder.add_text(1830, 174, "4. COUCHE DONNÉES POSTGRESQL 16 (PGCRYPTO) & RELATIONS", font_size=16, color="#FFFFFF")

    # Table: users
    builder.add_card_with_title(
        1830, 230, 710, 310,
        "🗄️ Table 'users' (Modèle SQLAlchemy & PostgreSQL 16)",
        [
            "Columns & Types :",
            "  • id                 : UUID (Primary Key, default gen_random_uuid())",
            "  • email              : VARCHAR(255) UNIQUE NOT NULL (Indexé)",
            "  • hashed_password    : VARCHAR(255) NOT NULL (Argon2 / bcrypt hash)",
            "  • full_name          : VARCHAR(255) NOT NULL",
            "  • phone_number       : VARCHAR(50) (Format marocain +212)",
            "  • role               : VARCHAR(50) NOT NULL ('renter' | 'pro_owner' | 'admin')",
            "  • company_name       : VARCHAR(255) NULL (Pour Loueurs BTP)",
            "  • ice_number         : VARCHAR(15) NULL (Identifiant Commun de l'Entreprise)",
            "  • rc_number          : VARCHAR(100) NULL (Registre du Commerce)",
            "  • cin_number         : VARCHAR(20) NULL (Chiffré via pgcrypto)",
            "  • is_kyc_verified    : BOOLEAN DEFAULT FALSE",
            "  • kyc_liveness_score : NUMERIC(5,2) NULL (ex: 96.80)",
            "  • kyc_audit_hash     : VARCHAR(64) NULL (Empreinte SHA-256 CNDP)",
            "  • cndp_consent_at    : TIMESTAMP WITH TIME ZONE NULL",
            "  • created_at         : TIMESTAMP WITH TIME ZONE DEFAULT NOW()"
        ],
        header_bg="#0F6E56", body_bg="#F0FDF4", border_color="#86EFAC"
    )

    # Table: audit_logs & kyc_records
    builder.add_card_with_title(
        1830, 560, 710, 210,
        "📋 Table 'cndp_audit_logs' (Registre Inaltérable Loi 09-08)",
        [
            "Columns & Types :",
            "  • id                 : UUID PRIMARY KEY",
            "  • user_id            : UUID REFERENCES users(id) ON DELETE CASCADE",
            "  • event_type         : VARCHAR(100) ('LIVENESS_CHECK' | 'CIN_VERIFY' | 'LOGIN')",
            "  • audit_proof_sha256 : VARCHAR(64) NOT NULL (Empreinte cryptographique)",
            "  • declaration_ref    : VARCHAR(100) ('CNDP-DEP-2026-MAROC-89421')",
            "  • ip_anonymized      : VARCHAR(45) (IPv4/IPv6 masquée)",
            "  • memory_purged_flag : BOOLEAN DEFAULT TRUE",
            "  • created_at         : TIMESTAMP WITH TIME ZONE DEFAULT NOW()"
        ],
        header_bg="#1E293B", body_bg="#F8FAFC", border_color="#94A3B8"
    )

    # Relations diagram
    builder.add_card_with_title(
        1830, 790, 710, 310,
        "🔗 Relations Entités & Clés Étrangères (Database ERD)",
        [
            "Relations 1-to-N issues de 'users' :",
            "",
            "  [users.id] (Propriétaire) ──< 1 : N >─── [equipment.owner_id]",
            "  └─ Un loueur possède N équipements, avec tarifs MAD et caution.",
            "",
            "  [users.id] (Locataire)    ──< 1 : N >─── [bookings.renter_id]",
            "  └─ Un locataire certifié KYC peut créer N réservations sous séquestre CMI.",
            "",
            "  [users.id]                ──< 1 : N >─── [inspections.inspector_id]",
            "  └─ Signature de l'état des lieux d'entrée et de sortie contradictoire.",
            "",
            "  [users.id]                ──< 1 : N >─── [cndp_audit_logs.user_id]",
            "  └─ Traçabilité juridique CNDP horodatée RFC 3161."
        ],
        header_bg="#0284C7", body_bg="#F0F9FF", border_color="#7DD3FC"
    )

    # Security & pgcrypto Callout
    builder.add_card_with_title(
        1830, 1120, 710, 350,
        "🔒 Mesures de Protection des Données (pgcrypto & RGPD/CNDP)",
        [
            "1. Extension pgcrypto activée dans PostgreSQL 16 (docker/postgres/init.sql)",
            "2. Chiffrement symétrique AES-256 des numéros de CIN stockés :",
            "   PGP_SYM_ENCRYPT(cin_number, '${ENCRYPTION_SECRET}')",
            "3. Hachage à sens unique des mots de passe (Argon2id avec salt aléatoire)",
            "4. Rétention minimale : Aucune image ou vidéo brute n'est persistée en base.",
            "5. Index B-Tree sur 'email' et 'role' pour des requêtes auth en < 1.5ms.",
            "6. Séparation stricte des privilèges : Rôle DB 'lokiini_user' sans droits DDL."
        ],
        header_bg="#475569", body_bg="#F1F5F9", border_color="#CBD5E1"
    )

    # =========================================================================
    # BOTTOM MASTER FLOW: STEP-BY-STEP SEQUENCE PIPELINE (Y: 1530 - 1880)
    # =========================================================================
    builder.add_rect(40, 1530, 2520, 340, bg_color="#FFFFFF", stroke_color="#CBD5E1", stroke_width=1.5)
    builder.add_rect(40, 1530, 2520, 44, bg_color="#1E293B", stroke_color="#1E293B", stroke_width=1)
    builder.add_text(60, 1542, "5. PIPELINE SÉQUENTIEL BOUT-EN-BOUT : LOGIN / REGISTER ➔ KYC ➔ DÉBLOCAGE BAIL & CAUTION", font_size=15, color="#FFFFFF")

    # Step 1
    builder.add_card_with_title(
        65, 1590, 450, 250,
        "Étape 1 : Formulaire Client (Web/Mobile)",
        [
            "• Saisie Email, Password, Nom, Rôle",
            "• Si Pro : Saisie ICE & Raison Sociale",
            "• Validation locale des critères de sécurité",
            "• Envoi HTTPS : POST /api/v1/auth/register",
            "  ou POST /api/v1/auth/login"
        ],
        header_bg="#0F6E56", body_bg="#F0FDF4", border_color="#86EFAC"
    )

    # Arrow 1 -> 2
    builder.add_arrow(515, 1715, 575, 1715, label="1. HTTP POST", stroke_color="#0F6E56")

    # Step 2
    builder.add_card_with_title(
        575, 1590, 450, 250,
        "Étape 2 : API Gateway & Backend Auth",
        [
            "• Nginx Gateway valide le routage /api/",
            "• FastAPI valide le schéma Pydantic",
            "• Hashage / Vérification bcrypt de mot de passe",
            "• PostgreSQL persiste le profil utilisateur",
            "• Retour JWT Bearer Access Token au client"
        ],
        header_bg="#0F6E56", body_bg="#F0FDF4", border_color="#86EFAC"
    )

    # Arrow 2 -> 3
    builder.add_arrow(1025, 1715, 1085, 1715, label="2. JWT Token", stroke_color="#0F6E56")

    # Step 3
    builder.add_card_with_title(
        1085, 1590, 450, 250,
        "Étape 3 : Déclencheur KYC Just-In-Time",
        [
            "• L'utilisateur clique sur 'Réserver' ou 'Publier'",
            "• Le frontend détecte 'is_kyc_verified == False'",
            "• Ouverture automatique de la KYCVerificationModal",
            "• Saisie de la CIN et ouverture flux caméra",
            "• Envoi des données au module ML Biométrie"
        ],
        header_bg="#D85A30", body_bg="#FFF7ED", border_color="#FDBA74"
    )

    # Arrow 3 -> 4
    builder.add_arrow(1535, 1715, 1595, 1715, label="3. Liveness Check", stroke_color="#D85A30")

    # Step 4
    builder.add_card_with_title(
        1595, 1590, 450, 250,
        "Étape 4 : Moteur ML Biométrie & CNDP",
        [
            "• Contrôle vivacité faciale ISO 30107-3 (>= 85%)",
            "• Vérification OCR préfectorale CIN marocaine",
            "• Calcul empreinte d'audit SHA-256 (CNDP)",
            "• Purge immédiate de la RAM volatile",
            "• Émission du certificat de conformité"
        ],
        header_bg="#6366F1", body_bg="#EEF2FF", border_color="#A5B4FC"
    )

    # Arrow 4 -> 5
    builder.add_arrow(2045, 1715, 2105, 1715, label="4. is_kyc=True", stroke_color="#6366F1")

    # Step 5
    builder.add_card_with_title(
        2105, 1590, 430, 250,
        "Étape 5 : Déblocage Caution & Bail DOC",
        [
            "• Base de données : is_kyc_verified = True",
            "• Déblocage du tunnel de réservation CMI",
            "• Pré-autorisation caution sans débit",
            "• Génération & signature du contrat DOC",
            "• Accès complet aux fonctionnalités de la plateforme"
        ],
        header_bg="#059669", body_bg="#ECFDF5", border_color="#6EE7B7"
    )

    # Inter-column Structural Connectors
    # Column 1 (Actors) -> Column 2 (Frontend)
    builder.add_arrow(560, 310, 610, 310, label="Interagit", stroke_color="#0F6E56")
    builder.add_arrow(560, 530, 610, 530, label="Gère annonces", stroke_color="#D85A30")
    builder.add_arrow(560, 750, 610, 750, label="Vérification", stroke_color="#1E293B")

    # Column 2 (Frontend) -> Column 3 (Backend)
    builder.add_arrow(1140, 330, 1210, 330, label="POST /auth/register", stroke_color="#0F6E56")
    builder.add_arrow(1140, 570, 1210, 570, label="POST /kyc/liveness", stroke_color="#0F6E56")

    # Column 3 (Backend) -> Column 4 (Database)
    builder.add_arrow(1760, 350, 1830, 350, label="INSERT users (hash)", stroke_color="#0F6E56")
    builder.add_arrow(1760, 610, 1830, 610, label="UPDATE is_kyc_verified", stroke_color="#0F6E56")

    return builder.build_document()


def main():
    doc = generate_architecture()

    # Target 1: inside docs folder
    docs_path = PROJECT_ROOT / "docs" / "02_architecture_technique_et_ia" / "lokiini_auth_kyc_full_architecture.excalidraw"
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)

    # Target 2: root directory for instant accessibility
    root_path = PROJECT_ROOT / "lokiini_auth_kyc_full_architecture.excalidraw"
    with open(root_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)

    print(f"[OK] Diagramme Excalidraw généré avec succès ({len(doc['elements'])} éléments) :")
    print(f"  1. {docs_path}")
    print(f"  2. {root_path}")


if __name__ == "__main__":
    main()
