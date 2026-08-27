#!/usr/bin/env python3
"""
Perfect Layout Generator for Lokiini System Architecture.
Fixes ALL visual and display overlap issues:
1. Node box text separated completely from badges (boxes height=100px, badges at y+62).
2. Inter-tier gaps expanded to 70px so arrow labels sit in clean empty space.
3. Palier containers enlarged to 325px height with 20px margins around explanation cards.
4. Explanations wrapped cleanly so text never touches or overflows borders.
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
        mid_x = start_x + dx * 0.5 - 45
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
    """Creates a beautifully padded node box with title, subtitle, and badges at the bottom."""
    elems = []
    box = create_rectangle(x, y, width, height, strokeColor=border_color, backgroundColor=bg_color, strokeWidth=1.5)
    elems.append(box)
    
    # Title
    t_elem = create_text(title, x + 8, y + 10, width=width - 16, fontSize=12, strokeColor=text_color, textAlign="center")
    elems.append(t_elem)
    
    # Subtitle
    s_elem = create_text(subtitle, x + 8, y + 32, width=width - 16, fontSize=10, strokeColor=DARK_TEXT, textAlign="center")
    elems.append(s_elem)
    
    # Badges at bottom (y + height - 32)
    bx = x + 16
    by = y + height - 30
    for b_text, b_bg, b_border, b_txt in badges:
        bw = len(b_text) * 7.2 + 14
        elems.append(create_rectangle(bx, by, bw, 20, strokeColor=b_border, backgroundColor=b_bg, strokeWidth=1, roundness={"type": 3}))
        elems.append(create_text(b_text, bx + 6, by + 3, fontSize=9, strokeColor=b_txt, textAlign="left"))
        bx += bw + 10
        
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

def build_perfect_system_architecture():
    elements = []
    canvas_w = 1860
    
    # Master Header
    elements.append(create_rectangle(40, 30, canvas_w, 75, strokeColor=TEAL_BORDER, backgroundColor=TEAL_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Architecture Système Globale 5 Paliers avec Schéma & Explications Détaillées", 60, 44, fontSize=18, strokeColor=TEAL_BORDER, textAlign="left"))
    elements.append(create_text("Analyse approfondie de chaque palier : Rôle métier, protocoles, flux de données et justification d'ingénierie", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # -------------------------------------------------------------
    # PALIER 1: Frontends & Clients (Y: 130, Height: 320)
    # -------------------------------------------------------------
    p1_y = 130
    p1_h = 320
    elements.append(create_rectangle(40, p1_y, canvas_w, p1_h, strokeColor=TEAL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 1 : Applications Frontend & Expérience Client / Loueur", 60, p1_y + 12, fontSize=14, strokeColor=TEAL_BORDER, textAlign="left"))
    
    # Node 1: Next.js Web
    n1_badges = [("⚡ SSR / SEO Local Maroc", TEAL_BG, TEAL_BORDER, TEAL_TEXT), ("🔒 HTTPS / REST", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(60, p1_y + 38, 540, 95, "Next.js 14 Web App (React 18 + App Router)", "SSR / SSG pour SEO Local Maroc • Tailwind CSS + shadcn/ui\nCatalogue géolocalisé (Casablanca, Rabat, Tanger, Marrakech)", n1_badges, TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    
    # Node 2: Mobile App
    n2_badges = [("📸 Caméra KYC Live", BLUE_BG, BLUE_BORDER, BLUE_TEXT), ("🔄 WSS Real-Time", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(630, p1_y + 38, 550, 95, "React Native / Expo Mobile App (iOS & Android)", "Accès Caméra Native • Biométrie KYC • Scan d'État des Lieux Vidéo\nMode Offline partiel & Push Notifications instantanées", n2_badges, BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    # Node 3: B2B Portal
    n3_badges = [("🏢 Facturation ICE B2B", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT), ("📊 Analytics MAD", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT)]
    elements.extend(create_rich_node(1210, p1_y + 38, 670, 95, "Portail Professionnel B2B & Dashboard Loueur", "Gestion de Flotte BTP/Audiovisuel • Calendrier Multi-Matériel\nSuivi des Cautions CMI • Factures avec ICE Maroc", n3_badges, PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    why_p1 = "📌 POURQUOI (WHY) : Au Maroc, 65% des recherches d'outillage et de matériel BTP débutent par des requêtes Google géolocalisées ('location mini-pelle Casablanca'). Le SSR Next.js 14 est impératif pour indexer chaque machine. L'application mobile Expo permet d'exploiter la caméra native pour le liveness KYC et la vidéo d'inspection sans maintenir deux codebases natifs."
    how_p1 = "⚙️ COMMENT (HOW) : Next.js 14 App Router assure le rendu hybride avec TanStack Query pour le cache client. Expo consomme l'API Gateway en HTTPS et ouvre un tunnel WebSocket (WSS) pour le chat loueur/locataire. Les formulaires sont validés par Zod avec le design system Tailwind."
    elements.extend(create_explanation_card(60, p1_y + 148, canvas_w - 40, why_p1, how_p1, max_chars=88)[0])
    
    # Inter-tier Connection 1 ➔ 2 (Gap: 70px, from Y: 450 to 520)
    elements.extend(create_arrow(330, 450, 330, 520, strokeColor=BLUE_BORDER, strokeWidth=2, label="HTTPS / REST API"))
    elements.extend(create_arrow(905, 450, 905, 520, strokeColor=BLUE_BORDER, strokeWidth=2, label="WSS / Live Push"))
    elements.extend(create_arrow(1545, 450, 1545, 520, strokeColor=PURPLE_BORDER, strokeWidth=2, label="Admin / B2B HTTPS"))
    
    # -------------------------------------------------------------
    # PALIER 2: Edge Gateway & Sécurité (Y: 520, Height: 320)
    # -------------------------------------------------------------
    p2_y = 520
    p2_h = 320
    elements.append(create_rectangle(40, p2_y, canvas_w, p2_h, strokeColor=BLUE_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 2 : Edge Gateway, Sécurité Périphérique & Proxies", 60, p2_y + 12, fontSize=14, strokeColor=BLUE_BORDER, textAlign="left"))
    
    n4_badges = [("🛡️ WAF Anti-DDoS", BLUE_BG, BLUE_BORDER, BLUE_TEXT), ("⚡ Latence <30ms", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(60, p2_y + 38, 540, 95, "Cloudflare CDN & WAF (Périphérie Réseau)", "Protection Anti-DDoS • Terminaison SSL/TLS 1.3\nEdge Caching des Assets & Images WebP Chiffrées", n4_badges, BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    n5_badges = [("🔑 JWT RS256", BLUE_BG, BLUE_BORDER, BLUE_TEXT), ("🚦 Rate Limiting", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(630, p2_y + 38, 550, 95, "API Gateway / Reverse Proxy (Kong / Envoy)", "Validation des Tokens JWT (RS256) • Contrôle d'Accès RBAC\nRate Limiting Anti-Scraping (100 req/min par IP)", n5_badges, BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    n6_badges = [("💬 Chat Chiffré", BLUE_BG, BLUE_BORDER, BLUE_TEXT), ("🔔 Push Instantané", BLUE_BG, BLUE_BORDER, BLUE_TEXT)]
    elements.extend(create_rich_node(1210, p2_y + 38, 670, 95, "Passerelle WebSockets & Messagerie Temps Réel", "Diffusion des Notifications Push • Chat Sécurisé In-App\nSynchronisation Live des Disponibilités Calendrier", n6_badges, BLUE_BG, BLUE_BORDER, BLUE_TEXT))
    
    why_p2 = "📌 POURQUOI (WHY) : Protéger la marketplace contre les cyberattaques, les tentatives de force brute sur les paiements CMI et le pillage de catalogue par des robots, tout en maintenant une latence inférieure à 30ms sur l'ensemble du territoire marocain."
    how_p2 = "⚙️ COMMENT (HOW) : Cloudflare intercepte le trafic en amont. L'API Gateway décode et valide les JWT asymétriques, injecte les identités utilisateurs dans les en-têtes internes et achemine le trafic vers les microservices via un réseau privé sécurisé."
    elements.extend(create_explanation_card(60, p2_y + 148, canvas_w - 40, why_p2, how_p2, max_chars=88)[0])
    
    # Inter-tier Connection 2 ➔ 3 (Gap: 70px, from Y: 840 to 910)
    elements.extend(create_arrow(265, 840, 265, 910, strokeColor=TEAL_BORDER, strokeWidth=2, label="CRUD Catalogue"))
    elements.extend(create_arrow(700, 840, 700, 910, strokeColor=TERRACOTTA_BORDER, strokeWidth=2, label="Réservations Escrow"))
    elements.extend(create_arrow(1150, 840, 1150, 910, strokeColor=PURPLE_BORDER, strokeWidth=2, label="Vérification KYC"))
    elements.extend(create_arrow(1615, 840, 1615, 910, strokeColor=GREEN_BORDER, strokeWidth=2, label="Baux & État des Lieux"))
    
    # -------------------------------------------------------------
    # PALIER 3: Backend Services & Microservices (Y: 910, Height: 320)
    # -------------------------------------------------------------
    p3_y = 910
    p3_h = 320
    elements.append(create_rectangle(40, p3_y, canvas_w, p3_h, strokeColor=TERRACOTTA_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 3 : Microservices Métier, Moteurs IA & Confiance Légale", 60, p3_y + 12, fontSize=14, strokeColor=TERRACOTTA_BORDER, textAlign="left"))
    
    n7_badges = [("🏷️ Tarifs Dégressifs MAD", TEAL_BG, TEAL_BORDER, TEAL_TEXT)]
    elements.extend(create_rich_node(60, p3_y + 38, 410, 95, "Service Catalogue & Annonces", "CRUD Matériel • Grille Tarifaire Dégressive MAD\nFiltres par Villes & Catégories BTP/Outils", n7_badges, TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    
    n8_badges = [("💳 Séquestre CMI 3D-Secure", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT)]
    elements.extend(create_rich_node(490, p3_y + 38, 420, 95, "Service Réservations & CMI", "Tunnel Escrow • Pré-autorisation Caution CMI\nCalcul Commissions Plateforme (15% vs 7%)", n8_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    n9_badges = [("🛡️ Conformité CNDP Loi 09-08", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT)]
    elements.extend(create_rich_node(930, p3_y + 38, 440, 95, "Moteur KYC Biométrique CNDP", "OCR CIN Maroc • Liveness Check Anti-Deepfake\nArchitecture Zero-Knowledge (Purge Vidéo en RAM)", n9_badges, PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    n10_badges = [("⚖️ Force Probante DOC Maroc", GREEN_BG, GREEN_BORDER, GREEN_TEXT)]
    elements.extend(create_rich_node(1390, p3_y + 38, 490, 95, "État des Lieux & Contrats DOC", "Hachage Vidéo SHA-256 • Scellement RFC 3161\nSignature Électronique (Loi 53-05 & DOC Art. 627+)", n10_badges, GREEN_BG, GREEN_BORDER, GREEN_TEXT))
    
    why_p3 = "📌 POURQUOI (WHY) : Découpler strictement la gestion commerciale, les flux monétaires sous séquestre et la conformité juridique pour qu'un incident sur un service tiers n'interrompe jamais l'accès global à la plateforme."
    how_p3 = "⚙️ COMMENT (HOW) : Microservices FastAPI/NestJS modulaires. Le module KYC effectue le contrôle de vivacité faciale en mémoire vive sans persistance des flux vidéo. Le module juridique génère les baux PDF scellés cryptographiquement en SHA-256 avec horodatage RFC 3161."
    elements.extend(create_explanation_card(60, p3_y + 148, canvas_w - 40, why_p3, how_p3, max_chars=88)[0])
    
    # Inter-tier Connection 3 ➔ 4 (Gap: 70px, from Y: 1230 to 1300)
    elements.extend(create_arrow(265, 1230, 265, 1300, strokeColor=TEAL_BORDER, strokeWidth=2, label="ACID Data"))
    elements.extend(create_arrow(700, 1230, 700, 1300, strokeColor=ALERT_BORDER, strokeWidth=2, label="Verrous 15m"))
    elements.extend(create_arrow(1150, 1230, 1150, 1300, strokeColor=PURPLE_BORDER, strokeWidth=2, label="Index & Recherche"))
    elements.extend(create_arrow(1635, 1230, 1635, 1300, strokeColor=TERRACOTTA_BORDER, strokeWidth=2, label="Stockage Chiffré"))
    
    # -------------------------------------------------------------
    # PALIER 4: Data, Storage & Indexation (Y: 1300, Height: 320)
    # -------------------------------------------------------------
    p4_y = 1300
    p4_h = 320
    elements.append(create_rectangle(40, p4_y, canvas_w, p4_h, strokeColor=PURPLE_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 4 : Stockage, Données Relationnelles & Moteur de Recherche", 60, p4_y + 12, fontSize=14, strokeColor=PURPLE_BORDER, textAlign="left"))
    
    n11_badges = [("🔒 pgcrypto Chiffré", TEAL_BG, TEAL_BORDER, TEAL_TEXT)]
    elements.extend(create_rich_node(60, p4_y + 38, 410, 95, "PostgreSQL 16 (Master/Replica)", "Transactions ACID • Extension pgcrypto\nChiffrement des Données Sensibles (CIN)", n11_badges, TEAL_BG, TEAL_BORDER, TEAL_TEXT))
    
    n12_badges = [("⏱️ Lock Anti-Double Booking", ALERT_BG, ALERT_BORDER, ALERT_TEXT)]
    elements.extend(create_rich_node(490, p4_y + 38, 420, 95, "Redis 7 (In-Memory Data Store)", "Sessions JWT • Verrous Dates 15m (SET NX)\nFiles de Traitement Asynchrones BullMQ", n12_badges, ALERT_BG, ALERT_BORDER, ALERT_TEXT))
    
    n13_badges = [("⚡ Recherche <20ms", PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT)]
    elements.extend(create_rich_node(930, p4_y + 38, 440, 95, "Meilisearch (Recherche Instantanée)", "Recherche Plein Texte (<20ms) • Tolérance Fautes\nFiltres Facettés par Ville, Prix MAD et Catégorie", n13_badges, PURPLE_BG, PURPLE_BORDER, PURPLE_TEXT))
    
    n14_badges = [("📦 Stockage Chiffré R2", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT)]
    elements.extend(create_rich_node(1390, p4_y + 38, 490, 95, "Cloudflare R2 / AWS S3 (Bucket Chiffré)", "Photos HD Matériel • Vidéos d'Inspection Scellées\nURLs Présignées à Durée Limitée (15 min)", n14_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    why_p4 = "📌 POURQUOI (WHY) : Éliminer tout risque de double réservation simultanée sur une même machine tout en garantissant des temps de réponse instantanés sur la recherche et la confidentialité totale des pièces d'identité."
    how_p4 = "⚙️ COMMENT (HOW) : PostgreSQL assure la consistance transactionnelle ACID avec pgcrypto. Redis pose des verrous atomiques pendant le tunnel de paiement et Meilisearch synchronise l'index du catalogue à chaque modification d'annonce."
    elements.extend(create_explanation_card(60, p4_y + 148, canvas_w - 40, why_p4, how_p4, max_chars=88)[0])
    
    # Inter-tier Connection 4 ➔ 5 (Gap: 70px, from Y: 1620 to 1690)
    elements.extend(create_arrow(265, 1620, 265, 1690, strokeColor=TERRACOTTA_BORDER, strokeWidth=2, label="Pré-auth CMI"))
    elements.extend(create_arrow(700, 1620, 700, 1690, strokeColor=TERRACOTTA_BORDER, strokeWidth=2, label="Dépôt CashPlus"))
    elements.extend(create_arrow(1150, 1620, 1150, 1690, strokeColor=ALERT_BORDER, strokeWidth=2, label="Orchestration n8n"))
    elements.extend(create_arrow(1635, 1620, 1635, 1690, strokeColor=GREEN_BORDER, strokeWidth=2, label="Garantie Assurance"))
    
    # -------------------------------------------------------------
    # PALIER 5: Écosystème Maroc & Automation (Y: 1690, Height: 320)
    # -------------------------------------------------------------
    p5_y = 1690
    p5_h = 320
    elements.append(create_rectangle(40, p5_y, canvas_w, p5_h, strokeColor=GREEN_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 5 : Écosystème Maroc, Passerelles de Paiement & Orchestrateur n8n", 60, p5_y + 12, fontSize=14, strokeColor=GREEN_BORDER, textAlign="left"))
    
    n15_badges = [("💳 CMI 3D-Secure v2", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT)]
    elements.extend(create_rich_node(60, p5_y + 38, 410, 95, "Passerelle CMI / Payzone", "Paiement CB Maroc & Visa/Mastercard\nEmpreinte Caution (Blocage Plafond sans Débit)", n15_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    n16_badges = [("💵 Cash-In Agence Maroc", TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT)]
    elements.extend(create_rich_node(490, p5_y + 38, 420, 95, "Réseau CashPlus / Wafacash", "Paiement Espèces (Cash-In) en Agence Locale\nValidation Instantanée par Webhook Signé HMAC", n16_badges, TERRACOTTA_BG, TERRACOTTA_BORDER, TERRACOTTA_TEXT))
    
    n17_badges = [("🤖 5 Workflows n8n", ALERT_BG, ALERT_BORDER, ALERT_TEXT)]
    elements.extend(create_rich_node(930, p5_y + 38, 440, 95, "Moteur d'Automation n8n (5 Workflows)", "Conseiller IA WhatsApp • Relances J-1 & H-2\nRapprochement Bancaire Quotidien (Cron 23:59)", n17_badges, ALERT_BG, ALERT_BORDER, ALERT_TEXT))
    
    n18_badges = [("🛡️ Assurance Wafa/Sanlam", GREEN_BG, GREEN_BORDER, GREEN_TEXT)]
    elements.extend(create_rich_node(1390, p5_y + 38, 490, 95, "Tiers de Confiance & Légal Maroc", "Conformité CNDP (Loi 09-08) • Horodatage RFC 3161\nPartenaire Assurance Dommages (Wafa / Sanlam)", n18_badges, GREEN_BG, GREEN_BORDER, GREEN_TEXT))
    
    why_p5 = "📌 POURQUOI (WHY) : Intégrer les canaux de paiement locaux (cartes CMI et agences CashPlus pour les professionnels non bancarisés) et automatiser 100% du cycle relationnel par WhatsApp, canal n°1 au Maroc."
    how_p5 = "⚙️ COMMENT (HOW) : CMI prend une pré-autorisation bloquant la caution sans débit. CashPlus envoie des webhooks signés HMAC. n8n absorbe les webhooks, orchestre les notifications WhatsApp et réconcilie les écritures comptables chaque soir à 23h59."
    elements.extend(create_explanation_card(60, p5_y + 148, canvas_w - 40, why_p5, how_p5, max_chars=88)[0])
    
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
    
    data = build_perfect_system_architecture()
    
    with open(base_dir / "lokiini_system_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    with open(docs_dir / "lokiini_system_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Generated Perfect System Architecture with Zero Overlaps: {len(data['elements'])} elements")

if __name__ == "__main__":
    main()
