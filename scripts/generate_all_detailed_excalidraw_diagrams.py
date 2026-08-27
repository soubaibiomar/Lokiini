#!/usr/bin/env python3
"""
Master Generator for All Modular Lokiini Excalidraw Diagrams with Embedded Explanations (Why & How).
Strict Excalidraw compliance:
- Hand-drawn font (Virgil, fontFamily: 1, roughness: 1)
- Embedded Pourquoi & Comment explanation cards for every section
- Generates:
  1. lokiini_system_architecture.excalidraw
  2. lokiini_database_erd.excalidraw
  3. lokiini_uml_workflows.excalidraw
"""

import json
import random
import time
from pathlib import Path

# Colors
C_TRIGGER_BG = "#FFE8CC"
C_TRIGGER_BORDER = "#D9480F"
C_TRIGGER_TEXT = "#D9480F"

C_ACTION_BG = "#D0EBFF"
C_ACTION_BORDER = "#1971C2"
C_ACTION_TEXT = "#1864AB"

C_OUTPUT_BG = "#D3F9D8"
C_OUTPUT_BORDER = "#2B8A3E"
C_OUTPUT_TEXT = "#2B8A3E"

C_TOOL_BG = "#F3D9FA"
C_TOOL_BORDER = "#AE3EC9"
C_TOOL_TEXT = "#862E9C"

C_AGENT_BG = "#E5DBFF"
C_AGENT_BORDER = "#5F3DC4"
C_AGENT_TEXT = "#5F3DC4"

C_DECISION_BG = "#FFF3BF"
C_DECISION_BORDER = "#F59F00"
C_DECISION_TEXT = "#D97706"

C_ALERT_BG = "#FFE3E3"
C_ALERT_BORDER = "#E03131"
C_ALERT_TEXT = "#C92A2A"

C_PANEL_BORDER = "#74C0FC"
C_HEADER_BG = "#E7F5FF"
C_HEADER_BORDER = "#1C7ED6"

C_EXPLANATION_BG = "#FFF9DB"
C_EXPLANATION_BORDER = "#F59F00"

CARD_BG = "#FFFFFF"
DARK_TEXT = "#1E293B"
MUTED_TEXT = "#475569"
BORDER_GRAY = "#CBD5E1"

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

def create_diamond(x, y, width, height, **kwargs):
    elem_id = kwargs.get("id", f"diamond_{random.randint(100000, 999999)}")
    now = int(time.time() * 1000)
    return {
        "id": elem_id,
        "type": "diamond",
        "x": x,
        "y": y,
        "width": max(width, 1),
        "height": max(height, 1),
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", C_DECISION_BORDER),
        "backgroundColor": kwargs.get("backgroundColor", C_DECISION_BG),
        "fillStyle": "solid",
        "strokeWidth": kwargs.get("strokeWidth", 1.5),
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
        "locked": False
    }

def create_text(text, x, y, **kwargs):
    font_size = kwargs.get("fontSize", 13)
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
        "startArrowhead": None,
        "endArrowhead": "arrow"
    }
    
    elements = [arrow]
    if "label" in kwargs and kwargs["label"]:
        label_text = kwargs["label"]
        mid_x = start_x + dx * 0.5 - 20
        mid_y = start_y + dy * 0.5 - 10
        lbl = create_text(
            label_text, mid_x, mid_y,
            fontSize=11,
            strokeColor=kwargs.get("labelColor", MUTED_TEXT),
            textAlign="center"
        )
        elements.append(lbl)
        
    return elements

def create_pill_node(x, y, width, height, text, bg_color, border_color, text_color, font_size=11):
    elements = []
    box = create_rectangle(
        x, y, width, height,
        strokeColor=border_color,
        backgroundColor=bg_color,
        strokeWidth=1.5,
        roundness={"type": 3}
    )
    elements.append(box)
    
    lines = text.split("\n")
    line_h = font_size * 1.35
    total_h = len(lines) * line_h
    t_y = y + (height - total_h) / 2
    
    t_elem = create_text(
        text, x + 4, t_y,
        width=width - 8,
        height=total_h,
        fontSize=font_size,
        strokeColor=text_color,
        textAlign="center"
    )
    elements.append(t_elem)
    return elements

def create_explanation_card(x, y, width, why_text, how_text):
    elements = []
    why_lines = [l for l in why_text.split("\n") if l.strip()]
    how_lines = [l for l in how_text.split("\n") if l.strip()]
    
    f_size = 11
    line_h = f_size * 1.35
    total_lines = 1 + len(why_lines) + 1 + len(how_lines)
    card_h = total_lines * line_h + 30
    
    box = create_rectangle(
        x, y, width, card_h,
        strokeColor=C_EXPLANATION_BORDER,
        backgroundColor=C_EXPLANATION_BG,
        strokeWidth=1.5,
        roundness={"type": 3}
    )
    elements.append(box)
    
    cy = y + 12
    hdr = create_text("💡 EXPLICATION MÉTIER & TECHNIQUE (POURQUOI & COMMENT) :", x + 16, cy, fontSize=12, strokeColor=C_TRIGGER_BORDER, textAlign="left")
    elements.append(hdr)
    cy += line_h + 4
    
    for line in why_lines:
        t = create_text(line, x + 16, cy, fontSize=f_size, strokeColor=DARK_TEXT, textAlign="left")
        elements.append(t)
        cy += line_h
        
    cy += 4
    for line in how_lines:
        t = create_text(line, x + 16, cy, fontSize=f_size, strokeColor=DARK_TEXT, textAlign="left")
        elements.append(t)
        cy += line_h
        
    return elements, card_h

# =====================================================================
# 1. DETAILED SYSTEM ARCHITECTURE (5 TIERS WITH EMBEDDED EXPLANATIONS)
# =====================================================================
def build_detailed_system_architecture():
    elements = []
    
    # Master Header
    elements.append(create_rectangle(40, 30, 1680, 75, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Architecture Système Globale 5 Paliers avec Explications (Pourquoi & Comment)", 60, 44, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    elements.append(create_text("Vue d'ensemble de l'infrastructure d'entreprise : Clients, Edge Gateway, Microservices, Données & Écosystème Maroc", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Tier 1: Frontends (Y: 125)
    t1_y = 125
    elements.append(create_rectangle(40, t1_y, 1680, 215, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 1 : Applications Frontend & Expérience Utilisateur", 60, t1_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, t1_y + 35, 480, 65, "Next.js 14 Web (App Router)\nSSR / SSG pour SEO Local Maroc • Tailwind + shadcn/ui", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(580, t1_y + 35, 480, 65, "React Native / Expo Mobile App\nAccès Caméra Native • Biométrie KYC • État des Lieux Vidéo", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1100, t1_y + 35, 600, 65, "Portail Pro B2B & Dashboard Loueur\nDisponibilité Flotte • Suivi Cautions CMI • Factures ICE B2B", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    
    why_t1 = "📌 POURQUOI (WHY) : Rendre chaque machine indexable sur Google Maroc (SEO SSR pour 'location matériel Casablanca') et offrir une application mobile fluide pour filmer l'état des lieux sans développer deux codebases distincts."
    how_t1 = "⚙️ COMMENT (HOW) : Next.js 14 App Router assure le rendu hybride et consomme l'API Gateway en REST/JSON. Expo exploite les capteurs caméra pour le liveness check KYC et le scan de documents en temps réel."
    elements.extend(create_explanation_card(60, t1_y + 115, 1640, why_t1, how_t1)[0])
    
    # Tier 2: Edge Gateway (Y: 360)
    t2_y = 360
    elements.append(create_rectangle(40, t2_y, 1680, 195, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 2 : Edge Gateway, Sécurité & Proxies", 60, t2_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, t2_y + 35, 480, 55, "Cloudflare CDN & WAF\nProtection DDoS, SSL/TLS, Caching Périphérique", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(580, t2_y + 35, 480, 55, "API Gateway / Auth Proxy\nValidation JWT, RBAC & Rate Limiting IP", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1100, t2_y + 35, 600, 55, "Passerelle WebSockets\nMessagerie Privée Loueur-Locataire & Alertes Push", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    why_t2 = "📌 POURQUOI (WHY) : Sécuriser les API contre le piratage et les attaques par déni de service, tout en maintenant une latence inférieure à 40ms pour tous les utilisateurs au Maroc."
    how_t2 = "⚙️ COMMENT (HOW) : Cloudflare gère le trafic DNS et SSL. L'API Gateway valide les signatures JWT, applique des quotas de requêtes et route les flux vers les microservices appropriés."
    elements.extend(create_explanation_card(60, t2_y + 105, 1640, why_t2, how_t2)[0])
    
    # Tier 3: Backend Services (Y: 575)
    t3_y = 575
    elements.append(create_rectangle(40, t3_y, 1680, 225, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 3 : Microservices Métier & Moteurs IA / CNDP", 60, t3_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, t3_y + 35, 380, 70, "Service Catalogue & Annonces\nCRUD Matériel • Calendrier Dispo\nFormule Tarifaire Dégressive", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(470, t3_y + 35, 380, 70, "Service Réservations & CMI\nTunnel Escrow • Caution CMI\nCalcul Commissions (15-5%)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(880, t3_y + 35, 380, 70, "Moteur KYC Biométrique CNDP\nOCR CIN Maroc • Liveness Check\nPolitique Zero-Knowledge en RAM", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(1290, t3_y + 35, 410, 70, "État des Lieux & Contrat DOC\nVidéo SHA-256 • Scellement RFC 3161\nSignature Électronique Loi 53-05", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    why_t3 = "📌 POURQUOI (WHY) : Découpler la gestion du catalogue, le traitement des cautions bancaires et la conformité CNDP pour une haute disponibilité et une intégrité contractuelle infalsifiable."
    how_t3 = "⚙️ COMMENT (HOW) : Microservices FastAPI/NestJS communiquant via PostgreSQL et Redis. Les baux DOC sont générés en PDF avec condensat SHA-256 certifié par horodatage légal RFC 3161."
    elements.extend(create_explanation_card(60, t3_y + 120, 1640, why_t3, how_t3)[0])
    
    # Tier 4: Data Layer (Y: 820)
    t4_y = 820
    elements.append(create_rectangle(40, t4_y, 1680, 215, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 4 : Stockage, Données & Moteur de Recherche", 60, t4_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, t4_y + 35, 380, 65, "PostgreSQL 16 (Master/Replica)\nTransactions ACID • Extension pgcrypto\nAudit Trail Immuable", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(470, t4_y + 35, 380, 65, "Redis 7 (In-Memory)\nSessions JWT • Verrous Dates 15m\nQueues Asynchrones BullMQ", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_pill_node(880, t4_y + 35, 380, 65, "Meilisearch\nRecherche Plein Texte (<20ms)\nFiltres Villes, Prix MAD, Catégories", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(1290, t4_y + 35, 410, 65, "Cloudflare R2 / AWS S3\nPhotos HD • Vidéos d'Inspection SHA-256\nURLs Présignées à Durée Limitée", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    
    why_t4 = "📌 POURQUOI (WHY) : Empêcher absolument les réservations concurrentes sur le même matériel (double-booking) tout en assurant une recherche instantanée et le stockage chiffré des pièces sensibles."
    how_t4 = "⚙️ COMMENT (HOW) : PostgreSQL garantit l'intégrité relationnelle avec chiffrement des CIN via pgcrypto. Redis pose des verrous atomiques pendant le paiement et Meilisearch indexe en mémoire les fiches matériel."
    elements.extend(create_explanation_card(60, t4_y + 115, 1640, why_t4, how_t4)[0])
    
    # Tier 5: Ecosystem & n8n (Y: 1055)
    t5_y = 1055
    elements.append(create_rectangle(40, t5_y, 1680, 215, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 5 : Écosystème Maroc, Paiements & Automatisation n8n", 60, t5_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, t5_y + 35, 380, 65, "Passerelle CMI / Payzone\nCartes Bancaires Maroc & Visa/MC\nEmpreinte Caution sans Débit", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(470, t5_y + 35, 380, 65, "Réseau CashPlus / Wafacash\nPaiement Cash-In en Agence Locale\nValidation Immédiate par Webhook", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(880, t5_y + 35, 380, 65, "Moteur d'Automation n8n\nConseiller IA WhatsApp • Relances J-1/H-2\nRapprochement Bancaire 23:59", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_pill_node(1290, t5_y + 35, 410, 65, "Tiers Juridiques & Assurance\nCNDP (Loi 09-08) • Horodatage RFC 3161\nPartenaire Assurance (Wafa/Sanlam)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    why_t5 = "📌 POURQUOI (WHY) : Intégrer les moyens de paiement locaux (cartes CMI et espèces CashPlus pour les non-bancarisés) et automatiser 100% de la relation client par WhatsApp pour maximiser l'adoption."
    how_t5 = "⚙️ COMMENT (HOW) : CMI émet des tokens de pré-autorisation bancaire sans impacter le compte. CashPlus envoie un webhook de validation. n8n orchestre les rappels WhatsApp et réconcilie les comptes chaque soir à 23h59."
    elements.extend(create_explanation_card(60, t5_y + 115, 1640, why_t5, how_t5)[0])
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

# =====================================================================
# 2. DETAILED DATABASE ERD (WITH EMBEDDED WHY & HOW EXPLANATIONS)
# =====================================================================
def build_detailed_database_erd():
    elements = []
    
    # Master Header
    elements.append(create_rectangle(40, 30, 1680, 75, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Modèle de Données Relationnel PostgreSQL 16 (ERD avec Explications Pourquoi & Comment)", 60, 44, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    elements.append(create_text("Schéma des tables, contraintes d'intégrité, relations 1:N / 1:1 et justification des choix de modélisation", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Helper to render table
    def render_hand_drawn_table(x, y, w, name, pks, fks, regs, header_bg, border_col):
        elems = []
        hdr_h = 36
        row_h = 24
        tot_h = hdr_h + (len(pks) + len(fks) + len(regs)) * row_h + 14
        
        elems.append(create_rectangle(x, y, w, tot_h, strokeColor=border_col, backgroundColor=CARD_BG, strokeWidth=1.5))
        elems.append(create_rectangle(x, y, w, hdr_h, strokeColor=border_col, backgroundColor=header_bg, strokeWidth=1.5))
        elems.append(create_text(f"TABLE: {name}", x + 14, y + 10, fontSize=13, strokeColor="#FFFFFF", textAlign="left"))
        
        cy = y + hdr_h + 6
        for k, t in pks:
            elems.append(create_text(f"🔑 PK  {k} : {t}", x + 12, cy, fontSize=11, strokeColor=C_TRIGGER_TEXT, textAlign="left"))
            cy += row_h
        for k, t, r in fks:
            elems.append(create_text(f"🔗 FK  {k} : {t} ➔ {r}", x + 12, cy, fontSize=11, strokeColor=C_ACTION_TEXT, textAlign="left"))
            cy += row_h
        for k, t in regs:
            elems.append(create_text(f"▫️ {k} : {t}", x + 16, cy, fontSize=11, strokeColor=MUTED_TEXT, textAlign="left"))
            cy += row_h
            
        return elems, tot_h
        
    # Table 1: USERS
    u_pk = [("id", "UUID (v4)")]
    u_fk = []
    u_reg = [
        ("full_name", "VARCHAR(120)"),
        ("email", "VARCHAR(255) UNIQUE"),
        ("phone_number", "VARCHAR(20) UNIQUE"),
        ("cin_number", "VARCHAR(20) ENCRYPTED"),
        ("is_kyc_verified", "BOOLEAN DEFAULT FALSE"),
        ("kyc_liveness_score", "NUMERIC(5,2)"),
        ("user_role", "ENUM ('renter','owner','pro')"),
        ("company_ice", "VARCHAR(20) NULL"),
        ("created_at", "TIMESTAMPTZ DEFAULT NOW()")
    ]
    e1, _ = render_hand_drawn_table(60, 125, 370, "users", u_pk, u_fk, u_reg, C_ACTION_BORDER, C_ACTION_BORDER)
    elements.extend(e1)
    
    # Table 2: EQUIPMENT
    eq_pk = [("id", "UUID (v4)")]
    eq_fk = [("owner_id", "UUID", "users.id")]
    eq_reg = [
        ("title", "VARCHAR(200)"),
        ("category", "VARCHAR(50)"),
        ("city", "VARCHAR(50)"),
        ("daily_price_mad", "NUMERIC(10,2)"),
        ("deposit_amount_mad", "NUMERIC(10,2)"),
        ("is_available", "BOOLEAN DEFAULT TRUE"),
        ("specs_json", "JSONB DEFAULT '{}'"),
        ("images_urls", "JSONB DEFAULT '[]'"),
        ("created_at", "TIMESTAMPTZ DEFAULT NOW()")
    ]
    e2, _ = render_hand_drawn_table(470, 125, 370, "equipment", eq_pk, eq_fk, eq_reg, C_ACTION_BORDER, C_ACTION_BORDER)
    elements.extend(e2)
    
    # Table 3: BOOKINGS
    bk_pk = [("id", "UUID (v4)")]
    bk_fk = [("equipment_id", "UUID", "equipment.id"), ("renter_id", "UUID", "users.id")]
    bk_reg = [
        ("start_date", "DATE"),
        ("end_date", "DATE"),
        ("total_days", "INTEGER"),
        ("rental_total_mad", "NUMERIC(10,2)"),
        ("commission_mad", "NUMERIC(10,2)"),
        ("deposit_hold_mad", "NUMERIC(10,2)"),
        ("booking_status", "VARCHAR(30)"),
        ("cmi_status", "VARCHAR(30)"),
        ("contract_pdf_url", "TEXT")
    ]
    e3, _ = render_hand_drawn_table(880, 125, 380, "bookings", bk_pk, bk_fk, bk_reg, C_TRIGGER_BORDER, C_TRIGGER_BORDER)
    elements.extend(e3)
    
    # Table 4: CMI_TRANSACTIONS
    cmi_pk = [("id", "UUID (v4)")]
    cmi_fk = [("booking_id", "UUID", "bookings.id")]
    cmi_reg = [
        ("cmi_auth_token", "VARCHAR(255)"),
        ("cmi_trans_id", "VARCHAR(100)"),
        ("preauth_amount_mad", "NUMERIC(10,2)"),
        ("captured_amount_mad", "NUMERIC(10,2)"),
        ("deposit_status", "ENUM ('held','released','captured')"),
        ("released_at", "TIMESTAMPTZ NULL"),
        ("created_at", "TIMESTAMPTZ DEFAULT NOW()")
    ]
    e4, _ = render_hand_drawn_table(1290, 125, 390, "cmi_transactions", cmi_pk, cmi_fk, cmi_reg, C_TRIGGER_BORDER, C_TRIGGER_BORDER)
    elements.extend(e4)
    
    # Table 5: INSPECTION_REPORTS
    ins_pk = [("id", "UUID (v4)")]
    ins_fk = [("booking_id", "UUID", "bookings.id")]
    ins_reg = [
        ("type", "ENUM ('check_in', 'check_out')"),
        ("video_url", "TEXT"),
        ("video_sha256_hash", "VARCHAR(64) UNIQUE"),
        ("rfc3161_timestamp", "TIMESTAMPTZ"),
        ("signed_by_owner", "BOOLEAN DEFAULT FALSE"),
        ("signed_by_renter", "BOOLEAN DEFAULT FALSE")
    ]
    e5, _ = render_hand_drawn_table(470, 480, 370, "inspection_reports", ins_pk, ins_fk, ins_reg, C_TOOL_BORDER, C_TOOL_BORDER)
    elements.extend(e5)
    
    # Table 6: REVIEWS
    rev_pk = [("id", "UUID (v4)")]
    rev_fk = [("booking_id", "UUID", "bookings.id"), ("reviewer_id", "UUID", "users.id")]
    rev_reg = [
        ("rating_score", "INTEGER CHECK (1-5)"),
        ("comment", "TEXT"),
        ("created_at", "TIMESTAMPTZ DEFAULT NOW()")
    ]
    e6, _ = render_hand_drawn_table(880, 480, 380, "reviews", rev_pk, rev_fk, rev_reg, C_OUTPUT_BORDER, C_OUTPUT_BORDER)
    elements.extend(e6)
    
    # ERD Arrows
    elements.extend(create_arrow(430, 160, 470, 160, strokeColor=C_ACTION_BORDER, label="1:N"))
    elements.extend(create_arrow(430, 200, 880, 200, strokeColor=C_ACTION_BORDER, label="renter 1:N"))
    elements.extend(create_arrow(840, 160, 880, 160, strokeColor=C_TRIGGER_BORDER, label="1:N"))
    elements.extend(create_arrow(1260, 160, 1290, 160, strokeColor=C_TRIGGER_BORDER, label="1:1"))
    elements.extend(create_arrow(880, 410, 840, 490, strokeColor=C_TOOL_BORDER, label="1:2"))
    elements.extend(create_arrow(1070, 420, 1070, 480, strokeColor=C_OUTPUT_BORDER, label="1:N"))
    
    # Embedded Explanations Cards for ERD
    erd_y = 780
    why_erd1 = "📌 POURQUOI CETTE MODÉLISATION (WHY) : Séparer strictement la réservation (`bookings`) de la transaction bancaire (`cmi_transactions`) permet de gérer les pré-autorisations de caution sans impacter la comptabilité locative, et d'isoler les données d'identité chiffrées (`cin_number` via pgcrypto) conformément à la CNDP."
    how_erd1 = "⚙️ COMMENT ÇA FONCTIONNE (HOW) : Lors de la réservation, un enregistrement `bookings` est créé en liaison 1:1 avec `cmi_transactions`. À la remise et au retour, deux lignes `inspection_reports` (check_in et check_out) scellent les vidéos avec une empreinte SHA-256 unique et horodatage certifié RFC 3161."
    elements.extend(create_explanation_card(60, erd_y, 1640, why_erd1, how_erd1)[0])
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

# =====================================================================
# 3. DETAILED UML WORKFLOWS (MACHINE À ÉTATS & SÉQUENCE CMI)
# =====================================================================
def build_detailed_uml_workflows():
    elements = []
    
    # Master Header
    elements.append(create_rectangle(40, 30, 1680, 75, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Machine à États & Séquence UML du Tunnel de Confiance (Pourquoi & Comment)", 60, 44, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    elements.append(create_text("Modélisation dynamique du cycle de vie des réservations, de la pré-autorisation de caution CMI et des états des lieux", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Left: State Machine (Y: 125)
    elements.append(create_rectangle(40, 125, 780, 750, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Machine à États : Cycle de Réservation & Caution CMI", 60, 135, fontSize=14, strokeColor=DARK_TEXT, textAlign="left"))
    
    states = [
        ("1. DEMANDE INITIALE", "Locataire choisit les dates & valide son panier", 60, 175, C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT),
        ("2. PRÉ-AUTORISATION CMI", "Empreinte bancaire bloquée sur le plafond sans débit", 60, 255, C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT),
        ("3. ACCEPTATION LOUEUR", "Bail numérique DOC généré & signé électroniquement", 60, 335, C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT),
        ("4. CHECK-IN SCELLÉ", "Vidéo contradictoire d'inspection horodatée SHA-256", 60, 415, C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("5. EN COURS D'UTILISATION", "Location active • Relances n8n J-1 & H-2 programmées", 60, 495, C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT),
        ("6. CHECK-OUT & CONTRÔLE", "Vérification contradictoire au retour du matériel", 60, 575, C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT),
        ("7. DÉNOUEMENT CAUTION", "Libération 100% ou Capture partielle pour sinistre", 60, 655, C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT),
    ]
    
    for title, desc, sx, sy, bg, border, txt in states:
        elements.extend(create_pill_node(sx + 40, sy, 360, 54, f"{title}\n{desc}", bg, border, txt, font_size=11))
        
    for i in range(len(states) - 1):
        sy_curr = states[i][3] + 54
        sy_next = states[i+1][3]
        elements.extend(create_arrow(260, sy_curr, 260, sy_next))
        
    elements.extend(create_pill_node(470, 625, 330, 48, "✅ Matériel Intact : Caution Libérée 100%", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=11))
    elements.extend(create_pill_node(470, 685, 330, 48, "⚠️ Sinistre : Capture CMI + Assurance", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT, font_size=11))
    elements.extend(create_arrow(440, 682, 470, 649, strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(440, 682, 470, 709, strokeColor=C_ALERT_BORDER))
    
    why_sm = "📌 POURQUOI CETTE MACHINE À ÉTATS (WHY) : Empêcher qu'un locataire soit débité avant accord du propriétaire, et garantir la libération instantanée du plafond bancaire dès le check-out validé sans dommage."
    how_sm = "⚙️ COMMENT (HOW) : Les transitions d'état sont atomiques dans PostgreSQL. L'état `held` passe à `released` via un appel d'API CMI sécurisé déclenché par n8n."
    elements.extend(create_explanation_card(60, 755, 740, why_sm, how_sm)[0])
    
    # Right: Sequence Diagram (Y: 125)
    elements.append(create_rectangle(840, 125, 880, 750, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Diagramme de Séquence UML (Tunnel de Confiance & Caution CMI)", 860, 135, fontSize=14, strokeColor=DARK_TEXT, textAlign="left"))
    
    actors = [
        ("Locataire", 880),
        ("Propriétaire", 1030),
        ("Lokiini API", 1180),
        ("CMI Gateway", 1330),
        ("n8n / Tiers", 1520)
    ]
    
    for name, ax in actors:
        elements.extend(create_pill_node(ax - 50, 170, 100, 32, name, C_HEADER_BG, C_HEADER_BORDER, C_HEADER_BORDER, font_size=10))
        now = int(time.time() * 1000)
        elements.append({
            "id": f"line_{random.randint(100000, 999999)}",
            "type": "line",
            "x": ax, "y": 202, "width": 1, "height": 520, "angle": 0,
            "strokeColor": BORDER_GRAY, "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "dashed", "roughness": 1, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": None, "seed": random.randint(1, 1000000),
            "version": 1, "versionNonce": random.randint(1, 1000000), "isDeleted": False,
            "boundElements": None, "updated": now, "link": None, "locked": False,
            "points": [[0, 0], [0, 520]], "lastCommittedPoint": None, "startBinding": None,
            "endBinding": None, "startArrowhead": None, "endArrowhead": None
        })
        
    seq_steps = [
        (880, 1180, 220, "1. Demande location + Scan CIN", C_ACTION_BORDER),
        (1180, 880, 255, "2. Formulaire 3D-Secure CMI", C_TRIGGER_BORDER),
        (880, 1330, 290, "3. Saisie CB & Empreinte", C_TRIGGER_BORDER),
        (1330, 1180, 325, "4. Caution Bloquée (Auth Token)", C_OUTPUT_BORDER),
        (1180, 1030, 360, "5. Push notif nouvelle résa", C_ACTION_BORDER),
        (1030, 1180, 395, "6. Confirmation loueur", C_ACTION_BORDER),
        (1180, 1520, 430, "7. Webhook n8n ➔ Contrat PDF DOC", C_TOOL_BORDER),
        (1520, 880, 465, "8. WhatsApp: Contrat + QR Check-in", C_TOOL_BORDER),
        (880, 1180, 500, "9. Upload Vidéo Check-in (SHA-256)", C_ACTION_BORDER),
        (1030, 1180, 535, "10. Signature contradictoire remise", C_ACTION_BORDER),
        (880, 1030, 575, "11. Restitution du matériel", DARK_TEXT),
        (1030, 1180, 610, "12. Validation retour sans dommage", C_OUTPUT_BORDER),
        (1180, 1330, 645, "13. Ordre Libération Caution CMI", C_OUTPUT_BORDER),
        (1330, 880, 680, "14. Plafond CB libéré instantanément", C_OUTPUT_BORDER),
    ]
    
    for sx, ex, sy, label, col in seq_steps:
        elements.extend(create_arrow(sx, sy, ex, sy, strokeColor=col, strokeWidth=1.5, label=label, labelColor=DARK_TEXT))
        
    why_seq = "📌 POURQUOI CE FLUX DE SÉQUENCE (WHY) : Verrouiller juridiquement et financièrement chaque étape sans immobiliser de liquidités chez le locataire et sans risque d'impayé pour le loueur."
    how_seq = "⚙️ COMMENT (HOW) : Les messages 1 à 14 s'enchaînent entre l'application, la passerelle monétique CMI et n8n qui délivre les contrats et notifie par WhatsApp."
    elements.extend(create_explanation_card(860, 755, 840, why_seq, how_seq)[0])
    
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
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. System Architecture
    sys_data = build_detailed_system_architecture()
    with open(base_dir / "lokiini_system_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(sys_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_system_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(sys_data, f, indent=2, ensure_ascii=False)
    print(f"Generated System Architecture with embedded explanations: {len(sys_data['elements'])} elements")
    
    # 2. Database ERD
    db_data = build_detailed_database_erd()
    with open(base_dir / "lokiini_database_erd.excalidraw", "w", encoding="utf-8") as f:
        json.dump(db_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_database_erd.excalidraw", "w", encoding="utf-8") as f:
        json.dump(db_data, f, indent=2, ensure_ascii=False)
    print(f"Generated Database ERD with embedded explanations: {len(db_data['elements'])} elements")
    
    # 3. UML Workflows
    uml_data = build_detailed_uml_workflows()
    with open(base_dir / "lokiini_uml_workflows.excalidraw", "w", encoding="utf-8") as f:
        json.dump(uml_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_uml_workflows.excalidraw", "w", encoding="utf-8") as f:
        json.dump(uml_data, f, indent=2, ensure_ascii=False)
    print(f"Generated UML Workflows with embedded explanations: {len(uml_data['elements'])} elements")

if __name__ == "__main__":
    main()
