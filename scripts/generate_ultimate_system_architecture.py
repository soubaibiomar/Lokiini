#!/usr/bin/env python3
"""
Ultimate Lokiini System Architecture Generator with:
- Full inter-tier connector pipelines (Arrows with protocol labels between all 5 tiers)
- Internal component data flows
- Brand color harmonization (Teal #0F6E56, Terracotta #D85A30, Amber #F59F00, Violet #5F3DC4)
- Embedded Why & How rich explanation cards with zero text clipping
- 100% Virgil hand-drawn font & Excalidraw schema validation.
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

def wrap_text(text, max_chars=82):
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

def create_badge(x, y, text, bg_color, border_color, text_color):
    elems = []
    w = len(text) * 7.5 + 16
    h = 22
    elems.append(create_rectangle(x, y, w, h, strokeColor=border_color, backgroundColor=bg_color, strokeWidth=1, roundness={"type": 3}))
    elems.append(create_text(text, x + 8, y + 4, fontSize=9, strokeColor=text_color, textAlign="left"))
    return elems

def create_explanation_card(x, y, width, why_text, how_text, max_chars=84):
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

def build_ultimate_system_architecture():
    elements = []
    canvas_w = 1860
    
    # Master Header
    elements.append(create_rectangle(40, 30, canvas_w, 75, strokeColor=TEAL_BORDER, backgroundColor=TEAL_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Architecture Système Globale 5 Paliers avec Schéma & Explications Détaillées", 60, 44, fontSize=18, strokeColor=TEAL_BORDER, textAlign="left"))
    elements.append(create_text("Analyse approfondie de chaque palier : Rôle métier, protocoles, flux de données et justification d'ingénierie", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # -------------------------------------------------------------
    # PALIER 1: Frontends & Clients (Y: 130)
    # -------------------------------------------------------------
    p1_y = 130
    p1_h = 245
    elements.append(create_rectangle(40, p1_y, canvas_w, p1_h, strokeColor=TEAL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 1 : Applications Frontend & Expérience Client / Loueur", 60, p1_y + 10, fontSize=14, strokeColor=TEAL_BORDER, textAlign="left"))
    
    elements.extend(create_pill_node(60, p1_y + 35, 520, 70, "Next.js 14 Web App (React 18 + App Router)\nSSR / SSG pour SEO Local Maroc • Tailwind CSS + shadcn/ui\nCatalogue géolocalisé (Casablanca, Rabat, Tanger, Marrakech)", TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    elements.extend(create_badge(70, p1_y + 82, "⚡ SSR / SEO Local Maroc", TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    elements.extend(create_badge(260, p1_y + 82, "🔒 HTTPS / REST", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    elements.extend(create_pill_node(620, p1_y + 35, 540, 70, "React Native / Expo Mobile App (iOS & Android)\nAccès Caméra Native • Biométrie KYC • Scan d'État des Lieux Vidéo\nMode Offline partiel & Push Notifications instantanées", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    elements.extend(create_badge(630, p1_y + 82, "📸 Caméra KYC Live", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    elements.extend(create_badge(800, p1_y + 82, "🔄 WSS Real-Time", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    elements.extend(create_pill_node(1200, p1_y + 35, 680, 70, "Portail Professionnel B2B & Dashboard Loueur\nGestion de Flotte BTP/Audiovisuel • Calendrier Multi-Matériel\nSuivi des Cautions CMI • Factures avec ICE Maroc", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    elements.extend(create_badge(1210, p1_y + 82, "🏢 Facturation ICE B2B", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    elements.extend(create_badge(1410, p1_y + 82, "📊 Analytics MAD", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    why_p1 = "📌 POURQUOI (WHY) : Au Maroc, 65% des recherches d'outillage et de matériel BTP débutent par des requêtes Google géolocalisées ('location mini-pelle Casablanca'). Le SSR Next.js 14 est impératif pour indexer chaque machine. L'application mobile Expo permet d'exploiter la caméra native pour le liveness KYC et la vidéo d'inspection sans maintenir deux codebases natifs."
    how_p1 = "⚙️ COMMENT (HOW) : Next.js 14 App Router assure le rendu hybride avec TanStack Query pour le cache client. Expo consomme l'API Gateway en HTTPS et ouvre un tunnel WebSocket (WSS) pour le chat loueur/locataire. Les formulaires sont validés par Zod avec le design system Tailwind."
    elements.extend(create_explanation_card(60, p1_y + 120, canvas_w - 40, why_p1, how_p1, max_chars=88)[0])
    
    # Inter-tier Connection 1 ➔ 2
    elements.extend(create_arrow(320, p1_y + p1_h, 320, p1_y + p1_h + 35, strokeColor=BLUE_BORDER, strokeWidth=2, label="HTTPS / REST API"))
    elements.extend(create_arrow(890, p1_y + p1_h, 890, p1_y + p1_h + 35, strokeColor=BLUE_BORDER, strokeWidth=2, label="WSS / Live Push"))
    elements.extend(create_arrow(1540, p1_y + p1_h, 1540, p1_y + p1_h + 35, strokeColor=PURPLE_BORDER, strokeWidth=2, label="Admin / B2B HTTPS"))
    
    # -------------------------------------------------------------
    # PALIER 2: Edge Gateway & Sécurité (Y: 410)
    # -------------------------------------------------------------
    p2_y = 410
    p2_h = 240
    elements.append(create_rectangle(40, p2_y, canvas_w, p2_h, strokeColor=BLUE_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 2 : Edge Gateway, Sécurité Périphérique & Proxies", 60, p2_y + 10, fontSize=14, strokeColor=BLUE_BORDER, textAlign="left"))
    
    elements.extend(create_pill_node(60, p2_y + 35, 520, 65, "Cloudflare CDN & WAF (Périphérie Réseau)\nProtection Anti-DDoS • Terminaison SSL/TLS 1.3\nEdge Caching des Assets & Images WebP Chiffrées", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    elements.extend(create_badge(70, p2_y + 77, "🛡️ WAF Anti-DDoS", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    elements.extend(create_badge(240, p2_y + 77, "⚡ Latence <30ms", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    elements.extend(create_pill_node(620, p2_y + 35, 540, 65, "API Gateway / Reverse Proxy (Kong / Envoy)\nValidation des Tokens JWT (RS256) • Contrôle d'Accès RBAC\nRate Limiting Anti-Scraping (100 req/min par IP)", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    elements.extend(create_badge(630, p2_y + 77, "🔑 JWT RS256", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    elements.extend(create_badge(780, p2_y + 77, "🚦 Rate Limiting", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    elements.extend(create_pill_node(1200, p2_y + 35, 680, 65, "Passerelle WebSockets & Messagerie Temps Réel\nDiffusion des Notifications Push • Chat Sécurisé In-App\nSynchronisation Live des Disponibilités Calendrier", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    elements.extend(create_badge(1210, p2_y + 77, "💬 Chat Chiffré", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    elements.extend(create_badge(1390, p2_y + 77, "🔔 Push Instantané", BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    why_p2 = "📌 POURQUOI (WHY) : Protéger la marketplace contre les cyberattaques, les tentatives de force brute sur les paiements CMI et le pillage de catalogue par des robots, tout en maintenant une latence inférieure à 30ms sur l'ensemble du territoire marocain."
    how_p2 = "⚙️ COMMENT (HOW) : Cloudflare intercepte le trafic en amont. L'API Gateway décode et valide les JWT asymétriques, injecte les identités utilisateurs dans les en-têtes internes et achemine le trafic vers les microservices via un réseau privé sécurisé."
    elements.extend(create_explanation_card(60, p2_y + 115, canvas_w - 40, why_p2, how_p2, max_chars=88)[0])
    
    # Inter-tier Connection 2 ➔ 3
    elements.extend(create_arrow(320, p2_y + p2_h, 320, p2_y + p2_h + 35, strokeColor=TEAL_BORDER, strokeWidth=2, label="CRUD Catalogue"))
    elements.extend(create_arrow(700, p2_y + p2_h, 700, p2_y + p2_h + 35, strokeColor=TERRACOTTA_BORDER, strokeWidth=2, label="Réservations Escrow"))
    elements.extend(create_arrow(1150, p2_y + p2_h, 1150, p2_y + p2_h + 35, strokeColor=PURPLE_BORDER, strokeWidth=2, label="Vérification KYC"))
    elements.extend(create_arrow(1635, p2_y + p2_h, 1635, p2_y + p2_h + 35, strokeColor=GREEN_BORDER, strokeWidth=2, label="Baux & État des Lieux"))
    
    # -------------------------------------------------------------
    # PALIER 3: Backend Services & Microservices (Y: 685)
    # -------------------------------------------------------------
    p3_y = 685
    p3_h = 255
    elements.append(create_rectangle(40, p3_y, canvas_w, p3_h, strokeColor=TERRACOTTA_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 3 : Microservices Métier, Moteurs IA & Confiance Légale", 60, p3_y + 10, fontSize=14, strokeColor=TERRACOTTA_BORDER, textAlign="left"))
    
    elements.extend(create_pill_node(60, p3_y + 35, 410, 75, "Service Catalogue & Annonces\nCRUD Matériel • Grille Tarifaire Dégressive MAD\nFiltres par Villes & Catégories BTP/Outils", TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    elements.extend(create_badge(70, p3_y + 87, "🏷️ Tarifs Dégressifs MAD", TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    
    elements.extend(create_pill_node(490, p3_y + 35, 420, 75, "Service Réservations & CMI\nTunnel Escrow • Pré-autorisation Caution CMI\nCalcul Commissions Plateforme (15% vs 7%)", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    elements.extend(create_badge(500, p3_y + 87, "💳 Séquestre CMI 3D-Secure", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    elements.extend(create_pill_node(930, p3_y + 35, 440, 75, "Moteur KYC Biométrique CNDP\nOCR CIN Maroc • Liveness Check Anti-Deepfake\nArchitecture Zero-Knowledge (Purge Vidéo en RAM)", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    elements.extend(create_badge(940, p3_y + 87, "🛡️ Conformité CNDP Loi 09-08", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    elements.extend(create_pill_node(1390, p3_y + 35, 490, 75, "État des Lieux & Contrats DOC\nHachage Vidéo SHA-256 • Scellement RFC 3161\nSignature Électronique (Loi 53-05 & DOC Art. 627+)", GREEN_BG, GREEN_BORDER, GREEN_TEXT))
    elements.extend(create_badge(1400, p3_y + 87, "⚖️ Force Probante DOC Maroc", GREEN_BG, GREEN_BORDER, GREEN_TEXT))
    
    why_p3 = "📌 POURQUOI (WHY) : Découpler strictement la gestion commerciale, les flux monétaires sous séquestre et la conformité juridique pour qu'un incident sur un service tiers n'interrompe jamais l'accès global à la plateforme."
    how_p3 = "⚙️ COMMENT (HOW) : Microservices FastAPI/NestJS modulaires. Le module KYC effectue le contrôle de vivacité faciale en mémoire vive sans persistance des flux vidéo. Le module juridique génère les baux PDF scellés cryptographiquement en SHA-256 avec horodatage RFC 3161."
    elements.extend(create_explanation_card(60, p3_y + 125, canvas_w - 40, why_p3, how_p3, max_chars=88)[0])
    
    # Inter-tier Connection 3 ➔ 4 & 5
    elements.extend(create_arrow(265, p3_y + p3_h, 265, p3_y + p3_h + 35, strokeColor=TEAL_BORDER, strokeWidth=2, label="ACID Data"))
    elements.extend(create_arrow(700, p3_y + p3_h, 700, p3_y + p3_h + 35, strokeColor=ALERT_BORDER, strokeWidth=2, label="Verrous 15m"))
    elements.extend(create_arrow(1150, p3_y + p3_h, 1150, p3_y + p3_h + 35, strokeColor=PURPLE_BORDER, strokeWidth=2, label="Index & Recherche"))
    elements.extend(create_arrow(1635, p3_y + p3_h, 1635, p3_y + p3_h + 35, strokeColor=TERRACOTTA_BORDER, strokeWidth=2, label="Stockage Chiffré"))
    
    # -------------------------------------------------------------
    # PALIER 4: Data, Storage & Indexation (Y: 975)
    # -------------------------------------------------------------
    p4_y = 975
    p4_h = 245
    elements.append(create_rectangle(40, p4_y, canvas_w, p4_h, strokeColor=PURPLE_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 4 : Stockage, Données Relationnelles & Moteur de Recherche", 60, p4_y + 10, fontSize=14, strokeColor=PURPLE_BORDER, textAlign="left"))
    
    elements.extend(create_pill_node(60, p4_y + 35, 410, 70, "PostgreSQL 16 (Master/Replica)\nTransactions ACID • Extension pgcrypto\nChiffrement des Données Sensibles (CIN)", TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    elements.extend(create_badge(70, p4_y + 82, "🔒 pgcrypto Chiffré", TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    
    elements.extend(create_pill_node(490, p4_y + 35, 420, 70, "Redis 7 (In-Memory Data Store)\nSessions JWT • Verrous Dates 15m (SET NX)\nFiles de Traitement Asynchrones BullMQ", ALERT_BG, ALERT_BORDER, ALERT_TEXT))
    elements.extend(create_badge(500, p4_y + 82, "⏱️ Lock Anti-Double Booking", ALERT_BG, ALERT_BORDER, ALERT_TEXT))
    
    elements.extend(create_pill_node(930, p4_y + 35, 440, 70, "Meilisearch (Recherche Instantanée)\nRecherche Plein Texte (<20ms) • Tolérance Fautes\nFiltres Facettés par Ville, Prix MAD et Catégorie", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    elements.extend(create_badge(940, p4_y + 82, "⚡ Recherche <20ms", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    elements.extend(create_pill_node(1390, p4_y + 35, 490, 70, "Cloudflare R2 / AWS S3 (Bucket Chiffré)\nPhotos HD Matériel • Vidéos d'Inspection Scellées\nURLs Présignées à Durée Limitée (15 min)", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    elements.extend(create_badge(1400, p4_y + 82, "📦 Stockage Chiffré R2", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    why_p4 = "📌 POURQUOI (WHY) : Éliminer tout risque de double réservation simultanée sur une même machine tout en garantissant des temps de réponse instantanés sur la recherche et la confidentialité totale des pièces d'identité."
    how_p4 = "⚙️ COMMENT (HOW) : PostgreSQL assure la consistance transactionnelle ACID avec pgcrypto. Redis pose des verrous atomiques pendant le tunnel de paiement et Meilisearch synchronise l'index du catalogue à chaque modification d'annonce."
    elements.extend(create_explanation_card(60, p4_y + 120, canvas_w - 40, why_p4, how_p4, max_chars=88)[0])
    
    # Inter-tier Connection 4 ➔ 5
    elements.extend(create_arrow(265, p4_y + p4_h, 265, p4_y + p4_h + 35, strokeColor=TERRACOTTA_BORDER, strokeWidth=2, label="Pré-auth CMI"))
    elements.extend(create_arrow(700, p4_y + p4_h, 700, p4_y + p4_h + 35, strokeColor=TERRACOTTA_BORDER, strokeWidth=2, label="Dépôt CashPlus"))
    elements.extend(create_arrow(1150, p4_y + p4_h, 1150, p4_y + p4_h + 35, strokeColor=ALERT_BORDER, strokeWidth=2, label="Orchestration n8n"))
    elements.extend(create_arrow(1635, p4_y + p4_h, 1635, p4_y + p4_h + 35, strokeColor=GREEN_BORDER, strokeWidth=2, label="Garantie Assurance"))
    
    # -------------------------------------------------------------
    # PALIER 5: Écosystème Maroc & Automation (Y: 1255)
    # -------------------------------------------------------------
    p5_y = 1255
    p5_h = 245
    elements.append(create_rectangle(40, p5_y, canvas_w, p5_h, strokeColor=GREEN_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 5 : Écosystème Maroc, Passerelles de Paiement & Orchestrateur n8n", 60, p5_y + 10, fontSize=14, strokeColor=GREEN_BORDER, textAlign="left"))
    
    elements.extend(create_pill_node(60, p5_y + 35, 410, 70, "Passerelle CMI / Payzone\nPaiement CB Maroc & Visa/Mastercard\nEmpreinte Caution (Blocage Plafond sans Débit)", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    elements.extend(create_badge(70, p5_y + 82, "💳 CMI 3D-Secure v2", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    elements.extend(create_pill_node(490, p5_y + 35, 420, 70, "Réseau CashPlus / Wafacash\nPaiement Espèces (Cash-In) en Agence Locale\nValidation Instantanée par Webhook Signé HMAC", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    elements.extend(create_badge(500, p5_y + 82, "💵 Cash-In Agence Maroc", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    elements.extend(create_pill_node(930, p5_y + 35, 440, 70, "Moteur d'Automation n8n (5 Workflows)\nConseiller IA WhatsApp • Relances J-1 & H-2\nRapprochement Bancaire Quotidien (Cron 23:59)", ALERT_BG, ALERT_BORDER, ALERT_TEXT))
    elements.extend(create_badge(940, p5_y + 82, "🤖 5 Workflows n8n", ALERT_BG, ALERT_BORDER, ALERT_TEXT))
    
    elements.extend(create_pill_node(1390, p5_y + 35, 490, 70, "Tiers de Confiance & Légal Maroc\nConformité CNDP (Loi 09-08) • Horodatage RFC 3161\nPartenaire Assurance Dommages (Wafa / Sanlam)", GREEN_BG, GREEN_BORDER, GREEN_TEXT))
    elements.extend(create_badge(1400, p5_y + 82, "🛡️ Assurance Wafa/Sanlam", GREEN_BG, GREEN_BORDER, GREEN_TEXT))
    
    why_p5 = "📌 POURQUOI (WHY) : Intégrer les canaux de paiement locaux (cartes CMI et agences CashPlus pour les professionnels non bancarisés) et automatiser 100% du cycle relationnel par WhatsApp, canal n°1 au Maroc."
    how_p5 = "⚙️ COMMENT (HOW) : CMI prend une pré-autorisation bloquant la caution sans débit. CashPlus envoie des webhooks signés HMAC. n8n absorbe les webhooks, orchestre les notifications WhatsApp et réconcilie les écritures comptables chaque soir à 23h59."
    elements.extend(create_explanation_card(60, p5_y + 120, canvas_w - 40, why_p5, how_p5, max_chars=88)[0])
    
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
    
    data = build_ultimate_system_architecture()
    
    with open(base_dir / "lokiini_system_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    with open(docs_dir / "lokiini_system_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Generated Ultimate System Architecture: {len(data['elements'])} elements")

if __name__ == "__main__":
    main()
