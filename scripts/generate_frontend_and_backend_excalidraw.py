#!/usr/bin/env python3
"""
Generator for Lokiini Frontend and Backend Architecture Diagrams in Excalidraw.
Strict schema compliance, Virgil hand-drawn font (fontFamily: 1), and embedded Why & How cards.
"""

import json
import random
import time
from pathlib import Path

# Brand Colors
TEAL_BG = "#E6FCF5"
TEAL_BORDER = "#0F6E56"
TEAL_TEXT = "#087F5B"

TERRACOTTA_BG = "#FFE8CC"
TERRACOTTA_BORDER = "#D85A30"
TERRACOTTA_TEXT = "#D9480F"

BLUE_BG = "#D0EBFF"
BLUE_BORDER = "#1971C2"
BLUE_TEXT = "#1864AB"

PURPLE_BG = "#F3D9FA"
PURPLE_BORDER = "#AE3EC9"
PURPLE_TEXT = "#862E9C"

GREEN_BG = "#D3F9D8"
GREEN_BORDER = "#2B8A3E"
GREEN_TEXT = "#2B8A3E"

YELLOW_BG = "#FFF3BF"
YELLOW_BORDER = "#F59F00"
YELLOW_TEXT = "#D97706"

ALERT_BG = "#FFE3E3"
ALERT_BORDER = "#E03131"
ALERT_TEXT = "#C92A2A"

EXPLANATION_BG = "#FFF9DB"
EXPLANATION_BORDER = "#F59F00"

CARD_BG = "#FFFFFF"
DARK_TEXT = "#1E293B"
MUTED_TEXT = "#475569"
BORDER_GRAY = "#CBD5E1"

def wrap_text(text, max_chars=80):
    words = text.split()
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + 1 > max_chars and curr:
            lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
        else:
            curr.append(w)
            curr_len += len(w) + 1
    if curr:
        lines.append(" ".join(curr))
    return lines

def create_rectangle(x, y, width, height, **kwargs):
    elem_id = kwargs.get("id", f"rect_{random.randint(100000, 999999)}")
    now = int(time.time() * 1000)
    return {
        "id": elem_id,
        "type": "rectangle",
        "x": x,
        "y": y,
        "width": max(width, 1),
        "height": max(height, 1),
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", DARK_TEXT),
        "backgroundColor": kwargs.get("backgroundColor", "transparent"),
        "fillStyle": "solid",
        "strokeWidth": kwargs.get("strokeWidth", 1.5),
        "strokeStyle": kwargs.get("strokeStyle", "solid"),
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": kwargs.get("roundness", {"type": 3}),
        "seed": random.randint(1, 1000000),
        "version": 1,
        "versionNonce": random.randint(1, 1000000),
        "isDeleted": False,
        "boundElements": None,
        "updated": now,
        "link": None,
        "locked": False
    }

def create_text(text, x, y, **kwargs):
    font_size = kwargs.get("fontSize", 12)
    lines = text.split("\n")
    max_len = max(len(l) for l in lines) if lines else 1
    char_w = font_size * 0.58
    line_h = font_size * 1.35
    w = kwargs.get("width", max(max_len * char_w, 20))
    h = kwargs.get("height", max(len(lines) * line_h, font_size * 1.2))
    
    elem_id = kwargs.get("id", f"text_{random.randint(100000, 999999)}")
    now = int(time.time() * 1000)
    return {
        "id": elem_id,
        "type": "text",
        "x": x,
        "y": y,
        "width": round(w, 2),
        "height": round(h, 2),
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", DARK_TEXT),
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": random.randint(1, 1000000),
        "version": 1,
        "versionNonce": random.randint(1, 1000000),
        "isDeleted": False,
        "boundElements": None,
        "updated": now,
        "link": None,
        "locked": False,
        "text": text,
        "fontSize": font_size,
        "fontFamily": 1,
        "textAlign": kwargs.get("textAlign", "center"),
        "verticalAlign": "middle",
        "baseline": round(font_size * 0.85, 2),
        "containerId": None,
        "originalText": text,
        "lineHeight": 1.25
    }

def create_arrow(start_x, start_y, end_x, end_y, **kwargs):
    dx = end_x - start_x
    dy = end_y - start_y
    now = int(time.time() * 1000)
    arrow_id = kwargs.get("id", f"arrow_{random.randint(100000, 999999)}")
    
    arrow = {
        "id": arrow_id,
        "type": "arrow",
        "x": start_x,
        "y": start_y,
        "width": max(abs(dx), 1),
        "height": max(abs(dy), 1),
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", MUTED_TEXT),
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": kwargs.get("strokeWidth", 1.5),
        "strokeStyle": kwargs.get("strokeStyle", "solid"),
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": random.randint(1, 1000000),
        "version": 1,
        "versionNonce": random.randint(1, 1000000),
        "isDeleted": False,
        "boundElements": None,
        "updated": now,
        "link": None,
        "locked": False,
        "points": [[0, 0], [dx, dy]],
        "lastCommittedPoint": None,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": kwargs.get("startArrowhead", None),
        "endArrowhead": kwargs.get("endArrowhead", "arrow")
    }
    
    elements = [arrow]
    if "label" in kwargs and kwargs["label"]:
        label_text = kwargs["label"]
        mid_x = start_x + dx * 0.5 - 35
        mid_y = start_y + dy * 0.5 - 10
        lbl = create_text(
            label_text, mid_x, mid_y,
            fontSize=10,
            strokeColor=kwargs.get("labelColor", MUTED_TEXT),
            textAlign="center"
        )
        elements.append(lbl)
        
    return elements

def create_rich_node(x, y, width, height, title, subtitle, badges, bg_color, border_color, text_color):
    elems = []
    box = create_rectangle(x, y, width, height, strokeColor=border_color, backgroundColor=bg_color, strokeWidth=1.5)
    elems.append(box)
    
    t_elem = create_text(title, x + 8, y + 10, width=width - 16, fontSize=12, strokeColor=text_color, textAlign="center")
    elems.append(t_elem)
    
    s_elem = create_text(subtitle, x + 8, y + 32, width=width - 16, fontSize=10, strokeColor=DARK_TEXT, textAlign="center")
    elems.append(s_elem)
    
    bx = x + 16
    by = y + height - 30
    for b_text, b_bg, b_border, b_txt in badges:
        bw = len(b_text) * 7.2 + 14
        elems.append(create_rectangle(bx, by, bw, 20, strokeColor=b_border, backgroundColor=b_bg, strokeWidth=1, roundness={"type": 3}))
        elems.append(create_text(b_text, bx + 6, by + 3, fontSize=9, strokeColor=b_txt, textAlign="left"))
        bx += bw + 10
        
    return elems

def create_explanation_card(x, y, width, why_text, how_text, max_chars=80):
    elements = []
    f_size = 11
    line_h = f_size * 1.35
    
    why_lines = wrap_text(why_text, max_chars)
    how_lines = wrap_text(how_text, max_chars)
    
    total_lines = 1 + len(why_lines) + 1 + len(how_lines)
    card_h = total_lines * line_h + 24
    
    box = create_rectangle(
        x, y, width, card_h,
        strokeColor=EXPLANATION_BORDER,
        backgroundColor=EXPLANATION_BG,
        strokeWidth=1.5,
        roundness={"type": 3}
    )
    elements.append(box)
    
    cy = y + 10
    hdr = create_text("💡 EXPLICATION MÉTIER & TECHNIQUE (POURQUOI & COMMENT) :", x + 14, cy, fontSize=11, strokeColor=TERRACOTTA_BORDER, textAlign="left")
    elements.append(hdr)
    cy += line_h + 4
    
    for line in why_lines:
        t = create_text(line, x + 14, cy, fontSize=f_size, strokeColor=DARK_TEXT, textAlign="left")
        elements.append(t)
        cy += line_h
        
    cy += 4
    for line in how_lines:
        t = create_text(line, x + 14, cy, fontSize=f_size, strokeColor=DARK_TEXT, textAlign="left")
        elements.append(t)
        cy += line_h
        
    return elements, card_h

# =====================================================================
# 1. FRONTEND ARCHITECTURE (React 18 + Next.js Component Tree)
# =====================================================================
def build_frontend_architecture():
    elements = []
    canvas_w = 1860
    
    # Header
    elements.append(create_rectangle(40, 30, canvas_w, 75, strokeColor=TEAL_BORDER, backgroundColor=TEAL_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Architecture Frontend Web (Composants React 18, État Global & Services API)", 60, 44, fontSize=18, strokeColor=TEAL_BORDER, textAlign="left"))
    elements.append(create_text("Hiérarchie des composants, gestion de l'état asynchrone, intégration Tailwind CSS et connecteurs API FastAPI", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Section 1: App Root & Navigation
    elements.append(create_rectangle(40, 130, canvas_w, 280, strokeColor=TEAL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("1. Composant Racine & Barre de Navigation (App.jsx & Navbar.jsx)", 60, 142, fontSize=14, strokeColor=TEAL_BORDER, textAlign="left"))
    
    n1_badges = [("⚛️ React 18 Root", TEAL_BG, TEAL_BORDER, TEAL_TEXT), ("🌐 Router Switch", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(60, 170, 520, 95, "App.jsx (Composant Racine)", "Gestion des vues actives ('catalog' vs 'dashboard')\nSynchronisation des filtres et écoute de l'état KYC", n1_badges, TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    
    n2_badges = [("🛡️ Statut CNDP Live", BLUE_BG, BLUE_BORDER, BLUE_TEXT), ("📍 Switch Espace Pro", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT)]
    elements.extend(create_rich_node(610, 170, 550, 95, "Navbar.jsx (En-tête Sticky)", "Indicateur d'identité vérifiée • Bouton de dépôt d'annonce\nNavigation fluide et bascule de profil locataire/loueur", n2_badges, BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    n3_badges = [("📡 Fetch / Fallback", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT), ("⚡ Async Data", GREEN_BG, GREEN_BORDER, GREEN_TEXT)]
    elements.extend(create_rich_node(1190, 170, 690, 95, "services/api.js (Couche d'Accès API)", "Client HTTP asynchrone pointant vers http://localhost:8000/api/v1\nFallback automatique sur mockData.js si backend en démarrage", n3_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    why_f1 = "📌 POURQUOI (WHY) : Offrir une interface ultra-rapide avec tolérance aux pannes réseau : l'application charge instantanément le catalogue localement et se synchronise en arrière-plan avec l'API FastAPI."
    how_f1 = "⚙️ COMMENT (HOW) : App.jsx déclenche un `useEffect` au chargement qui interroge `getEquipmentList()`. Si l'API répond, les données fraîches de PostgreSQL sont affichées, sinon le jeu de données initial prend le relais."
    elements.extend(create_explanation_card(60, 280, canvas_w - 40, why_f1, how_f1, max_chars=88)[0])
    
    # Section 2: Catalog & Modals
    elements.append(create_rectangle(40, 430, canvas_w, 280, strokeColor=BLUE_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("2. Catalogue, Moteur de Recherche & Modales Interactives", 60, 442, fontSize=14, strokeColor=BLUE_BORDER, textAlign="left"))
    
    n4_badges = [("🇲🇦 Villes Maroc", BLUE_BG, BLUE_BORDER, BLUE_TEXT), ("🔍 Filtres BTP/Outils", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(60, 470, 520, 95, "Hero.jsx (Barre de Recherche Flottante)", "Sélecteur géolocalisé (Casablanca, Rabat, Marrakech, Tanger)\nFiltrage instantané par catégorie et mot-clé textuel", n4_badges, BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    n5_badges = [("💳 Caution CMI Bloquée", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT), ("📉 Remise Dégressive", YELLOW_BG, YELLOW_BORDER, YELLOW_TEXT)]
    elements.extend(create_rich_node(610, 470, 550, 95, "EquipmentModal.jsx (Calculateur & Booking)", "Calculateur de réduction de durée (3j=-15%, 7j=-30%, 30j=-50%)\nExplication transparente du séquestre de caution CMI", n5_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    n6_badges = [("📸 Liveness Anti-Deepfake", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT), ("🔒 Zero-Knowledge RAM", GREEN_BG, GREEN_BORDER, GREEN_TEXT)]
    elements.extend(create_rich_node(1190, 470, 690, 95, "KYCVerificationModal.jsx (Contrôle CIN CNDP)", "Simulation de test de vivacité caméra et saisie de CIN\nPurge immédiate des flux vidéo de la mémoire vive", n6_badges, PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    why_f2 = "📌 POURQUOI (WHY) : La clarté sur la caution est le 1er facteur de conversion au Maroc. Le locataire doit comprendre que les 1500 MAD de caution ne sont pas prélevés de son compte, mais uniquement réservés sur son plafond."
    how_f2 = "⚙️ COMMENT (HOW) : `EquipmentModal` utilise un hook `useMemo` pour recalculer en temps réel le sous-total et afficher le badge explicatif CMI avec confirmation en 1 clic."
    elements.extend(create_explanation_card(60, 580, canvas_w - 40, why_f2, how_f2, max_chars=88)[0])
    
    # Section 3: Pro Dashboard
    elements.append(create_rectangle(40, 730, canvas_w, 270, strokeColor=PURPLE_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("3. Espace Professionnel Loueur & Suivi de Flotte (OwnerDashboard.jsx)", 60, 742, fontSize=14, strokeColor=PURPLE_BORDER, textAlign="left"))
    
    n7_badges = [("🏢 ICE Entreprise Maroc", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT), ("📊 KPI Revenus MAD", GREEN_BG, GREEN_BORDER, GREEN_TEXT)]
    elements.extend(create_rich_node(60, 770, 520, 95, "Gestion de Flotte BTP & Matériel", "Vue d'ensemble des équipements en location et disponibles\nIndicateurs de chiffre d'affaires mensuel en Dirhams", n7_badges, PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    n8_badges = [("🔒 Cautions Séquestrées", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT), ("⏰ Relances J-1/H-2", ALERT_BG, ALERT_BORDER, ALERT_TEXT)]
    elements.extend(create_rich_node(610, 770, 550, 95, "Tableau de Suivi des Cautions CMI", "Suivi des empreintes bancaires actives (42 000 MAD sous séquestre)\nStatut des relances automatisées n8n et états des lieux", n8_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    n9_badges = [("⚖️ Baux Horodatés", GREEN_BG, GREEN_BORDER, GREEN_TEXT), ("📑 Export Factures", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(1190, 770, 690, 95, "Contrats DOC & Rapports Financiers", "Accès direct aux baux PDF scellés en SHA-256 avec horodatage RFC 3161\nFacturation avec mention obligatoire de l'ICE de l'entreprise", n9_badges, GREEN_BG, GREEN_BORDER, GREEN_TEXT))
    
    why_f3 = "📌 POURQUOI (WHY) : Offrir aux entreprises de BTP et loueurs professionnels une visibilité totale sur leurs garanties financières et leurs encaissements en dirhams sans complexité administrative."
    how_f3 = "⚙️ COMMENT (HOW) : Le tableau de bord affiche les contrats actifs et permet de déclencher l'ordre de libération de caution CMI dès la restitution du matériel sans dommage."
    elements.extend(create_explanation_card(60, 880, canvas_w - 40, why_f3, how_f3, max_chars=88)[0])
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

# =====================================================================
# 2. BACKEND ARCHITECTURE (FastAPI Layered & Security Pipeline)
# =====================================================================
def build_backend_architecture():
    elements = []
    canvas_w = 1860
    
    # Header
    elements.append(create_rectangle(40, 30, canvas_w, 75, strokeColor=TERRACOTTA_BORDER, backgroundColor=TERRACOTTA_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Architecture Backend API (FastAPI Asynchrone, Sécurité & Moteurs Métier)", 60, 44, fontSize=18, strokeColor=TERRACOTTA_BORDER, textAlign="left"))
    elements.append(create_text("Architecture en couches : Routeurs REST, Modèles SQLAlchemy, Séquestre CMI, Pipeline KYC Zero-Knowledge & Baux DOC", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Section 1: Routers & Ingestion
    elements.append(create_rectangle(40, 130, canvas_w, 280, strokeColor=TERRACOTTA_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("1. Couche Présentation & Routeurs REST (FastAPI Routers)", 60, 142, fontSize=14, strokeColor=TERRACOTTA_BORDER, textAlign="left"))
    
    n1_badges = [("🔑 Auth JWT RS256", BLUE_BG, BLUE_BORDER, BLUE_TEXT), ("📦 CRUD Annonces", TEAL_BG, TEAL_BORDER, TEAL_TEXT)]
    elements.extend(create_rich_node(60, 170, 520, 95, "/api/v1/auth & /api/v1/equipment", "Gestion des comptes utilisateurs et des profils loueurs\nCatalogue avec filtres géographiques et tri tarifaire MAD", n1_badges, TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    
    n2_badges = [("💳 Caution CMI Escrow", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT), ("⏱️ Verrous Redis 15m", ALERT_BG, ALERT_BORDER, ALERT_TEXT)]
    elements.extend(create_rich_node(610, 170, 550, 95, "/api/v1/bookings & /calculate-pricing", "Calculateur de prix dégressif et création des réservations\nGénération des tokens de pré-autorisation bancaire CMI", n2_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    n3_badges = [("🛡️ CNDP Loi 09-08", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT), ("⚖️ SHA-256 RFC 3161", GREEN_BG, GREEN_BORDER, GREEN_TEXT)]
    elements.extend(create_rich_node(1190, 170, 690, 95, "/api/v1/kyc, /inspections & /webhooks", "Vérification biométrique avec purge Zero-Knowledge\nScellement des vidéos d'inspection et webhooks CMI/CashPlus", n3_badges, PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    why_b1 = "📌 POURQUOI (WHY) : Séparer strictement les routes métier pour garantir une réponse sous 25ms, tout en appliquant la validation de schéma stricte via Pydantic v2."
    how_b1 = "⚙️ COMMENT (HOW) : FastAPI gère les requêtes asynchrones en coroutines Python (`async def`), avec injection de dépendance (`Depends(get_db)`) pour chaque session de base de données."
    elements.extend(create_explanation_card(60, 280, canvas_w - 40, why_b1, how_b1, max_chars=88)[0])
    
    # Section 2: Core Domain & Data Layer
    elements.append(create_rectangle(40, 430, canvas_w, 280, strokeColor=TEAL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("2. Domaine Métier, Modèles de Données & Stockage (SQLAlchemy & PostgreSQL 16)", 60, 442, fontSize=14, strokeColor=TEAL_BORDER, textAlign="left"))
    
    n4_badges = [("🔒 pgcrypto Chiffré", TEAL_BG, TEAL_BORDER, TEAL_TEXT), ("✨ ACID Transactions", TEAL_BG, TEAL_BORDER, TEAL_TEXT)]
    elements.extend(create_rich_node(60, 470, 520, 95, "PostgreSQL 16 Engine (asyncpg Driver)", "Pool de connexions asynchrones haute performance (pool_size=20)\nChiffrement matériel des numéros de CIN via l'extension pgcrypto", n4_badges, TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    
    n5_badges = [("⏱️ SET lock 15m NX", ALERT_BG, ALERT_BORDER, ALERT_TEXT), ("⚡ Sessions JWT", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(610, 470, 550, 95, "Redis 7 In-Memory Cache & Distributed Lock", "Verrouillage atomique des dates d'équipement pendant le paiement\nStockage des sessions et mise en mémoire tampon des requêtes", n5_badges, ALERT_BG, ALERT_BORDER, ALERT_TEXT))
    
    n6_badges = [("🔍 Recherche <20ms", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT), ("📦 Stockage Chiffré R2", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT)]
    elements.extend(create_rich_node(1190, 470, 690, 95, "Meilisearch Sync & Cloudflare R2 Store", "Indexation textuelle tolérante aux fautes d'orthographe (Darija/FR)\nStockage des photos et vidéos d'état des lieux horodatées", n6_badges, PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    why_b2 = "📌 POURQUOI (WHY) : Empêcher le risque de double réservation simultanée sur une même machine tout en garantissant la confidentialité absolue des données personnelles."
    how_b2 = "⚙️ COMMENT (HOW) : Redis pose un verrou atomique `SET lock:equip_id 15m NX`. PostgreSQL applique les contraintes d'intégrité relationnelle avec chiffrement pgcrypto."
    elements.extend(create_explanation_card(60, 580, canvas_w - 40, why_b2, how_b2, max_chars=88)[0])
    
    # Section 3: Legal & Payment Orchestration
    elements.append(create_rectangle(40, 730, canvas_w, 270, strokeColor=GREEN_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("3. Moteur Monétique CMI & Sécurité Juridique DOC (Loi 53-05 & RFC 3161)", 60, 742, fontSize=14, strokeColor=GREEN_BORDER, textAlign="left"))
    
    n7_badges = [("💳 Séquestre sans Débit", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT), ("🛡️ 3D-Secure v2", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(60, 770, 520, 95, "Passerelle CMI & Payzone Connector", "Génération des tokens d'autorisation de caution par carte bancaire\nLibération instantanée du plafond dès la confirmation de restitution", n7_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    n8_badges = [("📄 Baux DOC Art. 627+", GREEN_BG, GREEN_BORDER, GREEN_TEXT), ("🔒 SHA-256 Immuable", GREEN_BG, GREEN_BORDER, GREEN_TEXT)]
    elements.extend(create_rich_node(610, 770, 550, 95, "Générateur de Contrats & Scellement Légal", "Production automatique des baux de louage de choses conformes au DOC\nCalcul de l'empreinte SHA-256 et horodatage certifié RFC 3161", n8_badges, GREEN_BG, GREEN_BORDER, GREEN_TEXT))
    
    n9_badges = [("🤖 5 Workflows n8n", ALERT_BG, ALERT_BORDER, ALERT_TEXT), ("💬 WhatsApp API Meta", GREEN_BG, GREEN_BORDER, GREEN_TEXT)]
    elements.extend(create_rich_node(1190, 770, 690, 95, "Moteur d'Automation n8n & Conseiller WhatsApp", "Envoi des contrats PDF et QR Codes de check-in par WhatsApp\nRelances à J-1/H-2 et réconciliation comptable nocturne à 23h59", n9_badges, ALERT_BG, ALERT_BORDER, ALERT_TEXT))
    
    why_b3 = "📌 POURQUOI (WHY) : Conférer une pleine valeur juridique aux transactions locatives devant les tribunaux marocains tout en protégeant les fonds des locataires."
    how_b3 = "⚙️ COMMENT (HOW) : Le backend combine les tokens CMI avec la génération de baux horodatés RFC 3161 distribués instantanément par n8n sur WhatsApp."
    elements.extend(create_explanation_card(60, 880, canvas_w - 40, why_b3, how_b3, max_chars=88)[0])
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

def main():
    base_dir = Path(r"d:\Lokiini")
    docs_dir = base_dir / "docs" / "02_architecture_technique_et_ia"
    
    # 1. Frontend Architecture
    fe_data = build_frontend_architecture()
    with open(base_dir / "lokiini_frontend_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(fe_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_frontend_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(fe_data, f, indent=2, ensure_ascii=False)
    print(f"Generated Frontend Architecture: {len(fe_data['elements'])} elements")
    
    # 2. Backend Architecture
    be_data = build_backend_architecture()
    with open(base_dir / "lokiini_backend_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(be_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_backend_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(be_data, f, indent=2, ensure_ascii=False)
    print(f"Generated Backend Architecture: {len(be_data['elements'])} elements")

if __name__ == "__main__":
    main()
