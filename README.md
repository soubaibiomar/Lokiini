# Lokiini — Marketplace Universelle de Location de Matériel Sécurisée (Maroc)

> **Plateforme de mise en relation pour la location de matériel à haute valeur ajoutée avec vérification d'identité biométrique par caméra en direct, état des lieux photo/vidéo scellé par IA et couverture assurantielle évolutive.**

---

## 🧭 Sommaire du Projet

- [1. Vision & Proposition de Valeur](#1-vision--proposition-de-valeur)
- [2. Suite Documentaire & Études Thématiques (PDF)](#2-suite-documentaire--études-thématiques-pdf)
- [3. Architecture du Référentiel](#3-architecture-du-référentiel)
- [4. Stack Technique & Pipeline IA](#4-stack-technique--pipeline-ia)
- [5. Cadre Réglementaire & Conformité Marocaine](#5-cadre-réglementaire--conformité-marocaine)
- [6. Modèle Économique & Tarification](#6-modèle-économique--tarification)
- [7. Compilation des Documents & Démarrage](#7-compilation-des-documents--démarrage)

---

## 1. Vision & Proposition de Valeur

Au Maroc, le marché de la location d'équipements (BTP, outillage, audiovisuel, électronique, événementiel) est fracturé en deux extrêmes :
1. **L'informel (Avito, Facebook Marketplace)** : Zéro vérification d'identité, risques élevés de vol, dégradations non couvertes et exigences de cautions en cash paralysantes.
2. **Les loueurs traditionnels B2B (Krini, SIBOX, Sebul, Premium Location)** : Processus lourds sur devis, réservés aux grands comptes BTP, inaccessibles aux particuliers, freelances et artisans indépendants.

**MatOS** comble ce vide en créant un tiers de confiance numérique :
- **Navigation 100% libre** sans mur d'inscription pour maximiser l'indexation SEO et le partage viral.
- **KYC Biométrique déclenché à l'action** (*Réserver* ou *Publier*) avec contrôle d'authenticité CIN/Passeport et test de vivacité (*liveness check*) caméra en direct anti-deepfake.
- **État des lieux contradictoire photo/vidéo** horodaté cryptographiquement (RFC 3161 / SHA-256) éliminant les litiges d'état.
- **Contrat de bail numérique automatique** sous le Dahir des Obligations et Contrats (DOC) et la Loi 53-05.
- **Grille tarifaire hybride** combinant commission dégressive (15% à 5%) et abonnements récurrents (Premium Particulier à 49 MAD/m, Pro BTP à 299 MAD/m).

---

## 2. Suite Documentaire & Études Thématiques (PDF)

Tous les dossiers stratégiques, techniques et juridiques sont rédigés et compilés en **PDF haute fidélité** dans le dossier docs/ :

| # | Document & Thématique | Livrable PDF | Sources Principales |
|---|---|---|---|
| **00** | **Dossier Maître d'Ingénierie Stratégique** | docs/00_master_dossier_strategique/MatOS_Master_Dossier_Strategique.pdf | Synthèse intégrale des 5 piliers stratégiques |
| **01** | **Étude de Marché, Concurrence & Personas** | docs/01_etude_marche_et_concurrence/etude_marche.pdf | HCP, ANRT, CMI, Benchmark Hygglo/Fat Llama |
| **02** | **Architecture Technique, IA & Anti-Deepfake** | docs/02_architecture_technique_et_ia/architecture_technique.pdf | ISO/IEC 30107-3, NIST SP 800-63B, FaceForensics++ |
| **03** | **Cadre Juridique, Réglementaire & CNDP** | docs/03_cadre_juridique_et_conformite_cndp/cadre_juridique_cndp.pdf | DOC Maroc, Loi 09-08 CNDP, Loi 53-05, ACAPS |
| **04** | **Spécification Produit, UX & Processus** | docs/04_specification_produit_ux_et_process/specification_produit_ux.pdf | Nielsen Norman Group, Protocoles CEMA |
| **05** | **Modèle Économique & Business Plan 36M** | docs/05_modele_economique_et_business_plan/business_plan_financier.pdf | CGI Maroc, Modélisation SaaS/Marketplace a16z |

---

## 3. Architecture du Référentiel

`	ext
D:\startup\MatOS/
├── README.md
├── docs/
│   ├── 00_master_dossier_strategique/         # Rapport exécutif consolidé
│   ├── 01_etude_marche_et_concurrence/        # Étude sectorielle, concurrence et personas
│   ├── 02_architecture_technique_et_ia/       # Schémas techniques, API & module liveness
│   ├── 03_cadre_juridique_et_conformite_cndp/ # Lois marocaines, statuts SARL-AU, CGU, CNDP
│   ├── 04_specification_produit_ux_et_process/# Funnels UX, matrice de risque, litiges
│   ├── 05_modele_economique_et_business_plan/ # Grilles tarifaires, P&L 36M, point mort
│   └── assets/                                # Logos, diagrammes et illustrations
├── src/
│   ├── backend/                               # API FastAPI / PostgreSQL
│   ├── frontend/
│   │   ├── web/                               # Catalogue Web Next.js / PWA (SEO-optimized)
│   │   └── mobile/                            # Application Flutter iOS/Android
│   └── ml_biometrics/                         # Inférence OCR CIN & Anti-Deepfake / Liveness
└── scripts/
    └── compile_all_pdfs.py                    # Script d'automatisation de compilation LaTeX
`

---

## 4. Stack Technique & Pipeline IA

- **Backend** : FastAPI (Python 3.11+), Uvicorn, SQLAlchemy 2.0 async, Pydantic v2.
- **Base de Données** : PostgreSQL 16 avec extension pgcrypto et hachage cryptographique.
- **Frontend** : Next.js 14 / React pour la vitrine web et le SEO ; Flutter pour l'application mobile native.
- **Module Vision / IA** : ONNX Runtime / PyTorch léger (modèles de classification de vivacité faciale, micro-textures et détection de reflets cornéens anti-replay attack).
- **Paiement & Monétique** : Passerelle CMI (Centre Monétique Interbancaire) / Payzone / HPS avec pré-autorisation d'empreinte bancaire.
- **Stockage Objets** : Cloudflare R2 / AWS S3 avec URL signées et scellement d'horodatage RFC 3161.

---

## 5. Cadre Réglementaire & Conformité Marocaine

1. **Forme Juridique** : **SARL-AU** (Société à Responsabilité Limitée à Associé Unique) créée via le CRI, assurant l'étanchéité du patrimoine personnel.
2. **Protection des Données Personnelles** : Déclaration préalable obligatoire auprès de la **CNDP** en vertu de la **Loi n° 09-08** pour le traitement des données d'identité et biométriques avec politique *Zero-Knowledge* (traitement des flux vidéo en mémoire vive éphémère).
3. **Contrats & Signatures Électroniques** : Application de la **Loi n° 53-05** et des articles 627+ du **Dahir des Obligations et Contrats (DOC)** pour la validité juridique probante des états des lieux et contrats de bail dématérialisés.
4. **Positionnement Juridique Évolutif** : Lancement en **Modèle B (Intermédiaire Technique Facilitateur)** puis passage au **Modèle Hybride** avec assurance dommages/vol adossée à une compagnie marocaine de premier plan (Wafa Assurance, Saham, Sanlam).

---

## 6. Modèle Économique & Tarification

- **Formule Gratuite (Découverte)** : 0 MAD/mois — 15% de commission par transaction.
- **Premium Particulier** : 49 MAD/mois — 10% de commission, livraison incluse (<15 km), caution cash supprimée, vérification prioritaire.
- **Pro BTP & Événementiel** : 299 MAD/mois — 7% de commission, gestion multi-chantiers, facturation B2B avec ICE, support dédié 24/7.
- **BTP Entreprise / Grands Comptes** : Sur devis — 5% de commission, intégration ERP/API, contrats-cadres.

---

## 7. Compilation des Documents & Démarrage

Pour recompiler l'intégralité des études thématiques en PDF :

`powershell
python scripts/compile_all_pdfs.py
`

Les fichiers .pdf générés se trouveront directement dans leurs sous-dossiers respectifs sous docs/.
>>>>>>> 342fbb9 (feat: complete Lokiini Moroccan equipment rental marketplace with full web, backend, mobile, n8n workflows, biometrics engine and official logo)
