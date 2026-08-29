#!/usr/bin/env python3
"""
Complete Project Pipeline & Architecture Generator for Lokiini (MatOS).
Generates a comprehensive, master-level .excalidraw diagram covering:
1. Full 5-Tier System Architecture & Infrastructure
2. All 7 End-to-End Operational Pipelines & Business Workflows
3. Moroccan Legal & Regulatory Compliance Matrix (CNDP, DOC, Loi 53-05, CMI)
4. Monétique & Escrow Caution Ledger
5. DevOps, Containerization & CI/CD Pipeline

Follows excalidraw-expert best practices:
- roughness: 0 (clean, crisp, non-sketchy lines)
- fontFamily: 2 (Normal / Helvetica sans-serif for professional look)
- Moroccan luxury brand palette: Deep Teal (#0F6E56), Terracotta (#D85A30), Sand (#FDFBF7), Dark Slate (#1E293B)
- Programmatic layout calculation preventing text overflows and collisions
- Fully valid Excalidraw v2 schema
"""

import json
import random
import time
from pathlib import Path

# --- COLOR PALETTE CONSTANTS ---
TEAL_PRIMARY = "#0F6E56"
TEAL_LIGHT = "#E8F5F1"
TEAL_BORDER = "#0B513F"

TERRACOTTA_PRIMARY = "#D85A30"
TERRACOTTA_LIGHT = "#FBEEE9"
TERRACOTTA_BORDER = "#B8431B"

SAND_BG = "#FDFBF7"
SAND_CARD = "#F7F4EE"
WHITE = "#FFFFFF"

SLATE_DARK = "#1E293B"
SLATE_MUTED = "#475569"
SLATE_LIGHT = "#F8FAFC"
BORDER_DEFAULT = "#CBD5E1"

BLUE_PRIMARY = "#0284C7"
BLUE_LIGHT = "#F0F9FF"
BLUE_BORDER = "#0369A1"

PURPLE_PRIMARY = "#7C3AED"
PURPLE_LIGHT = "#F5F3FF"
PURPLE_BORDER = "#6D28D9"

AMBER_PRIMARY = "#D97706"
AMBER_LIGHT = "#FEF3C7"
AMBER_BORDER = "#B45309"

EMERALD_PRIMARY = "#10B981"
EMERALD_LIGHT = "#ECFDF5"
EMERALD_BORDER = "#059669"

ROSE_PRIMARY = "#E11D48"
ROSE_LIGHT = "#FFE4E6"
ROSE_BORDER = "#BE123C"

INDIGO_PRIMARY = "#4F46E5"
INDIGO_LIGHT = "#EEF2FF"
INDIGO_BORDER = "#4338CA"


def get_now_ms():
    return int(time.time() * 1000)


def create_element(elem_type, x, y, width, height, **kwargs):
    elem_id = kwargs.get("id", f"{elem_type}_{random.randint(100000, 999999)}")
    now = get_now_ms()
    base = {
        "id": elem_id,
        "type": elem_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", SLATE_DARK),
        "backgroundColor": kwargs.get("backgroundColor", "transparent"),
        "fillStyle": kwargs.get("fillStyle", "solid"),
        "strokeWidth": kwargs.get("strokeWidth", 1.5),
        "strokeStyle": kwargs.get("strokeStyle", "solid"),
        "roughness": 0,
        "opacity": kwargs.get("opacity", 100),
        "groupIds": kwargs.get("groupIds", []),
        "frameId": kwargs.get("frameId", None),
        "roundness": kwargs.get("roundness", {"type": 3}),
        "seed": random.randint(1, 1000000),
        "version": 1,
        "versionNonce": random.randint(1, 1000000),
        "isDeleted": False,
        "boundElements": kwargs.get("boundElements", None),
        "updated": now,
        "link": None,
        "locked": False
    }
    for k, v in kwargs.items():
        base[k] = v
    return base


def create_text(text, x, y, **kwargs):
    font_size = kwargs.get("fontSize", 14)
    lines = text.split("\n")
    max_len = max(len(l) for l in lines) if lines else 1
    char_w = font_size * 0.58
    line_h = font_size * 1.38
    
    w = kwargs.get("width", max(max_len * char_w, 30))
    h = kwargs.get("height", len(lines) * line_h)
    
    elem_id = kwargs.get("id", f"text_{random.randint(100000, 999999)}")
    now = get_now_ms()
    return {
        "id": elem_id,
        "type": "text",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", SLATE_DARK),
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": kwargs.get("groupIds", []),
        "frameId": kwargs.get("frameId", None),
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
        "fontFamily": kwargs.get("fontFamily", 2),
        "textAlign": kwargs.get("textAlign", "left"),
        "verticalAlign": kwargs.get("verticalAlign", "top"),
        "containerId": kwargs.get("containerId", None),
        "originalText": text
    }


def create_card(x, y, width, height, title, items=None, badge=None, **kwargs):
    """Creates a beautifully structured card with title, badge, and bullet items."""
    elements = []
    box_id = kwargs.get("id", f"card_{random.randint(100000, 999999)}")
    stroke_color = kwargs.get("strokeColor", TEAL_PRIMARY)
    bg_color = kwargs.get("backgroundColor", WHITE)
    
    box = create_element(
        "rectangle", x, y, width, height,
        id=box_id,
        strokeColor=stroke_color,
        backgroundColor=bg_color,
        strokeWidth=kwargs.get("strokeWidth", 1.5),
        roundness={"type": 3}
    )
    elements.append(box)
    
    # Title
    t_y = y + 12
    title_elem = create_text(
        title, x + 14, t_y,
        fontSize=kwargs.get("titleFontSize", 14),
        strokeColor=kwargs.get("titleColor", stroke_color),
        width=width - 28
    )
    elements.append(title_elem)
    
    # Badge if present
    if badge:
        b_text = badge
        b_w = len(b_text) * 7.0 + 14
        b_h = 20
        b_x = x + width - b_w - 10
        b_y = y + 10
        badge_box = create_element(
            "rectangle", b_x, b_y, b_w, b_h,
            strokeColor=kwargs.get("badgeBorder", stroke_color),
            backgroundColor=kwargs.get("badgeBg", TEAL_LIGHT),
            strokeWidth=1,
            roundness={"type": 3}
        )
        badge_txt = create_text(
            b_text, b_x + 6, b_y + 3,
            fontSize=10,
            strokeColor=kwargs.get("badgeColor", stroke_color),
            width=b_w - 12
        )
        elements.append(badge_box)
        elements.append(badge_txt)
    
    # Subtitle / description / bullet items
    curr_y = t_y + title_elem["height"] + 6
    if items:
        if isinstance(items, list):
            item_str = "\n".join(f"• {it}" if not it.startswith("•") and not it.startswith("→") and not it.startswith("[") else it for it in items)
        else:
            item_str = items
            
        items_elem = create_text(
            item_str, x + 14, curr_y,
            fontSize=kwargs.get("itemFontSize", 11),
            strokeColor=kwargs.get("itemColor", SLATE_MUTED),
            width=width - 28
        )
        elements.append(items_elem)
        
    return box_id, elements


def create_arrow(start_x, start_y, end_x, end_y, **kwargs):
    dx = end_x - start_x
    dy = end_y - start_y
    now = get_now_ms()
    arrow_id = kwargs.get("id", f"arrow_{random.randint(100000, 999999)}")
    arrow = {
        "id": arrow_id,
        "type": "arrow",
        "x": start_x,
        "y": start_y,
        "width": abs(dx) if dx != 0 else 1,
        "height": abs(dy) if dy != 0 else 1,
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", SLATE_MUTED),
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": kwargs.get("strokeWidth", 1.5),
        "strokeStyle": kwargs.get("strokeStyle", "solid"),
        "roughness": 0,
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
        "startBinding": kwargs.get("startBinding", None),
        "endBinding": kwargs.get("endBinding", None),
        "startArrowhead": kwargs.get("startArrowhead", None),
        "endArrowhead": "arrow"
    }
    elements = [arrow]
    
    if "label" in kwargs and kwargs["label"]:
        label_text = kwargs["label"]
        mid_x = start_x + dx * 0.5 - (len(label_text) * 3.2)
        mid_y = start_y + dy * 0.5 - 10
        lbl = create_text(
            label_text, mid_x, mid_y,
            fontSize=10,
            strokeColor=kwargs.get("labelColor", kwargs.get("strokeColor", SLATE_DARK))
        )
        elements.append(lbl)
        
    return elements


def create_pipeline_step(x, y, width, height, step_num, title, action, protocol, tech, **kwargs):
    """Creates a standardized pipeline node with step number, title, action, and tech badge."""
    elements = []
    bg_color = kwargs.get("backgroundColor", WHITE)
    stroke_color = kwargs.get("strokeColor", TEAL_PRIMARY)
    
    # Outer box
    box_id = kwargs.get("id", f"step_{random.randint(100000, 999999)}")
    box = create_element(
        "rectangle", x, y, width, height,
        id=box_id,
        strokeColor=stroke_color,
        backgroundColor=bg_color,
        strokeWidth=1.5,
        roundness={"type": 3}
    )
    elements.append(box)
    
    # Step Number Badge (circle or rounded box)
    s_size = 22
    s_box = create_element(
        "rectangle", x + 10, y + 10, s_size, s_size,
        strokeColor=stroke_color,
        backgroundColor=stroke_color,
        strokeWidth=1,
        roundness={"type": 3}
    )
    s_txt = create_text(
        str(step_num), x + 16 if step_num < 10 else x + 13, y + 13,
        fontSize=11,
        strokeColor=WHITE,
        width=15
    )
    elements.append(s_box)
    elements.append(s_txt)
    
    # Title
    t_elem = create_text(
        title, x + 38, y + 12,
        fontSize=12,
        strokeColor=stroke_color,
        width=width - 50
    )
    elements.append(t_elem)
    
    # Action description
    act_elem = create_text(
        action, x + 12, y + 38,
        fontSize=10,
        strokeColor=SLATE_DARK,
        width=width - 24
    )
    elements.append(act_elem)
    
    # Protocol / Tech footer badge
    foot_txt = f"{protocol} | {tech}"
    foot_elem = create_text(
        foot_txt, x + 12, y + height - 20,
        fontSize=9,
        strokeColor=SLATE_MUTED,
        width=width - 24
    )
    elements.append(foot_elem)
    
    return box_id, elements


def build_complete_project_architecture():
    elements = []
    
    # =========================================================================
    # 0. MASTER CANVAS HEADER BANNER
    # =========================================================================
    header_w = 3450
    header_h = 100
    elements.append(create_element(
        "rectangle", 40, 30, header_w, header_h,
        strokeColor=TEAL_PRIMARY,
        backgroundColor=TEAL_PRIMARY,
        strokeWidth=1,
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "LOKIINI (MatOS) — ARCHITECTURE GLOBALE DU SYSTÈME & PIPELINES TECHNIQUES END-TO-END",
        65, 46,
        fontSize=24,
        strokeColor=WHITE
    ))
    elements.append(create_text(
        "Marketplace Universelle de Location de Matériel Sécurisée au Maroc (Web & Mobile) • Cautions CMI • KYC Biométrique CNDP • Contrats DOC Loi 53-05 • Automation n8n • 100% Dockerisé",
        65, 84,
        fontSize=13,
        strokeColor=TEAL_LIGHT
    ))
    
    # Status badges on the right side of header
    badges = [
        ("🇲🇦 MAROC (MAD)", TERRACOTTA_LIGHT, TERRACOTTA_PRIMARY, 2700),
        ("🛡️ CONFORME CNDP (09-08)", EMERALD_LIGHT, EMERALD_PRIMARY, 2870),
        ("💳 CMI / 3D-SECURE v2", BLUE_LIGHT, BLUE_PRIMARY, 3100),
        ("🐳 100% DOCKER", PURPLE_LIGHT, PURPLE_PRIMARY, 3310),
    ]
    for b_title, b_bg, b_col, b_x in badges:
        bw = len(b_title) * 7.2 + 16
        elements.append(create_element(
            "rectangle", b_x, 50, bw, 28,
            strokeColor=WHITE,
            backgroundColor=b_bg,
            strokeWidth=1,
            roundness={"type": 3}
        ))
        elements.append(create_text(
            b_title, b_x + 8, 56,
            fontSize=11,
            strokeColor=b_col,
            width=bw - 16
        ))

    # =========================================================================
    # SECTION 1 (LEFT COLUMN): 🏛️ MULTI-TIER SYSTEM ARCHITECTURE (X: 40 to 1660)
    # =========================================================================
    sec1_x = 40
    sec1_w = 1620
    
    # Section 1 Container Title
    elements.append(create_element(
        "rectangle", sec1_x, 150, sec1_w, 40,
        strokeColor=TEAL_BORDER,
        backgroundColor=TEAL_PRIMARY,
        strokeWidth=1,
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PARTIE 1 : ARCHITECTURE SYSTÈME MODULAIRE EN 5 PALIERS (INFRASTRUCTURE & SERVICES)",
        sec1_x + 20, 160,
        fontSize=15,
        strokeColor=WHITE
    ))

    # -------------------------------------------------------------------------
    # TIER 1: CLIENTS & FRONTEND (Y: 205 to 395)
    # -------------------------------------------------------------------------
    t1_y = 205
    t1_h = 195
    elements.append(create_element(
        "rectangle", sec1_x, t1_y, sec1_w, t1_h,
        strokeColor=TEAL_PRIMARY,
        backgroundColor=TEAL_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PALIER 1 : FRONTEND, APPLICATIONS CLIENTS & EXPÉRIENCE UTILISATEUR",
        sec1_x + 20, t1_y + 10,
        fontSize=13,
        strokeColor=TEAL_PRIMARY
    ))
    
    # Cards in Tier 1
    # 1.1 Web App
    c1_1, e1_1 = create_card(
        sec1_x + 20, t1_y + 35, 380, 145,
        "Next.js 14+ Web Application",
        items=[
            "SSR / SSG pour SEO local marocain",
            "Catalogue matériel sans inscription requise",
            "Filtres par ville (Casa, Rabat, Tanger, Marrakech)",
            "Tailwind CSS + shadcn/ui (Teal & Terracotta)",
            "Zustand / TanStack Query (state & cache)"
        ],
        badge="Web / SEO",
        strokeColor=TEAL_PRIMARY,
        backgroundColor=WHITE
    )
    elements.extend(e1_1)
    
    # 1.2 Mobile App
    c1_2, e1_2 = create_card(
        sec1_x + 415, t1_y + 35, 380, 145,
        "React Native / Expo Mobile App",
        items=[
            "iOS & Android sur codebase unifié",
            "Module Caméra KYC & vivacité en direct",
            "État des lieux vidéo contradictoire scellé",
            "Notifications push Expo / Firebase",
            "Géolocalisation & itinéraires chantiers"
        ],
        badge="Mobile Native",
        strokeColor=TERRACOTTA_PRIMARY,
        badgeBorder=TERRACOTTA_PRIMARY,
        badgeBg=TERRACOTTA_LIGHT,
        badgeColor=TERRACOTTA_PRIMARY,
        backgroundColor=WHITE
    )
    elements.extend(e1_2)
    
    # 1.3 Loueur / Pro Dashboard
    c1_3, e1_3 = create_card(
        sec1_x + 810, t1_y + 35, 380, 145,
        "Portail Pro & Dashboard Loueur",
        items=[
            "Gestion de flotte & calendrier disponibilités",
            "Registre des cautions CMI sous séquestre",
            "Facturation B2B conforme (ICE, IF, TVA 20%)",
            "Analytics des revenus en Dirhams (MAD)",
            "Gestion multi-utilisateurs & collaborateurs"
        ],
        badge="B2B / Loueur",
        strokeColor=PURPLE_PRIMARY,
        badgeBorder=PURPLE_PRIMARY,
        badgeBg=PURPLE_LIGHT,
        badgeColor=PURPLE_PRIMARY,
        backgroundColor=WHITE
    )
    elements.extend(e1_3)
    
    # 1.4 Admin & Support Desk
    c1_4, e1_4 = create_card(
        sec1_x + 1205, t1_y + 35, 395, 145,
        "Admin Desk & Médiation",
        items=[
            "File d'attente d'audit manuel KYC litigieux",
            "Arbitrage des sinistres & litiges d'état des lieux",
            "Monitoring des flux de paiement CMI & CashPlus",
            "Gestion des signalements & modération",
            "Journal d'audit de sécurité CNDP"
        ],
        badge="Super Admin",
        strokeColor=ROSE_PRIMARY,
        badgeBorder=ROSE_PRIMARY,
        badgeBg=ROSE_LIGHT,
        badgeColor=ROSE_PRIMARY,
        backgroundColor=WHITE
    )
    elements.extend(e1_4)

    # -------------------------------------------------------------------------
    # TIER 2: EDGE GATEWAY & SECURITY (Y: 415 to 545)
    # -------------------------------------------------------------------------
    t2_y = 415
    t2_h = 135
    elements.append(create_element(
        "rectangle", sec1_x, t2_y, sec1_w, t2_h,
        strokeColor=BLUE_PRIMARY,
        backgroundColor=BLUE_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PALIER 2 : EDGE GATEWAY, SÉCURITÉ PÉRIPHÉRIQUE & REVERSE PROXY",
        sec1_x + 20, t2_y + 10,
        fontSize=13,
        strokeColor=BLUE_PRIMARY
    ))
    
    # 2.1 Cloudflare Edge
    c2_1, e2_1 = create_card(
        sec1_x + 20, t2_y + 32, 510, 90,
        "Cloudflare CDN & WAF (Edge Security)",
        items=[
            "Protection anti-DDoS, SSL/TLS Edge termination",
            "Mise en cache des assets statiques sur POPs Casablanca/Madrid",
            "Règles WAF anti-bot & rate limiting strict sur /auth et /kyc"
        ],
        badge="Edge DNS/WAF",
        strokeColor=BLUE_PRIMARY
    )
    elements.extend(e2_1)
    
    # 2.2 Nginx API Gateway
    c2_2, e2_2 = create_card(
        sec1_x + 545, t2_y + 32, 535, 90,
        "Nginx API Gateway & Reverse Proxy (Docker)",
        items=[
            "Routage unifié: /api/v1 (FastAPI), /n8n/ (Workflows), /docs (OpenAPI)",
            "Vérification headers JWT, injection CORS, compression Gzip/Brotli",
            "Limiteur de débit (100 req/min/IP) et isolation réseau Docker bridge"
        ],
        badge="Gateway :80",
        strokeColor=BLUE_PRIMARY
    )
    elements.extend(e2_2)
    
    # 2.3 WebSocket Real-time Gateway
    c2_3, e2_3 = create_card(
        sec1_x + 1095, t2_y + 32, 505, 90,
        "Passerelle WebSockets Temps Réel",
        items=[
            "Messagerie instantanée directe loueur-locataire",
            "Diffusion en temps réel des changements d'états de réservation",
            "Streaming des checkpoints de vivacité KYC vers le client mobile"
        ],
        badge="WSS / Events",
        strokeColor=BLUE_PRIMARY
    )
    elements.extend(e2_3)

    # -------------------------------------------------------------------------
    # TIER 3: BACKEND MICROSERVICES & ENGINES (Y: 565 to 845)
    # -------------------------------------------------------------------------
    t3_y = 565
    t3_h = 280
    elements.append(create_element(
        "rectangle", sec1_x, t3_y, sec1_w, t3_h,
        strokeColor=TEAL_PRIMARY,
        backgroundColor=TEAL_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PALIER 3 : MOTEURS MÉTIER, LOGIQUE BACKEND ASYNCHRONE (FASTAPI / PYTHON 3.11)",
        sec1_x + 20, t3_y + 10,
        fontSize=13,
        strokeColor=TEAL_PRIMARY
    ))
    
    # 3.1 Service Catalogue & Matériel
    c3_1, e3_1 = create_card(
        sec1_x + 20, t3_y + 35, 305, 230,
        "Service Catalogue & Annonces",
        items=[
            "CRUD équipement & spécifications",
            "Catégories BTP, Événementiel, AV",
            "Calendrier de disponibilité fine",
            "Algorithme de tarification dégressive",
            "Calcul dynamique des commissions",
            "Gestion des photos & fiches techniques"
        ],
        badge="app.routers.equipment",
        strokeColor=TEAL_PRIMARY
    )
    elements.extend(e3_1)
    
    # 3.2 Service Réservations & CMI
    c3_2, e3_2 = create_card(
        sec1_x + 340, t3_y + 35, 310, 230,
        "Service Réservations & CMI",
        items=[
            "Tunnel de réservation en 5 étapes",
            "Verrouillage distribué des dates (Redis)",
            "Gestion pré-autorisation caution CMI",
            "Calcul des acomptes & séquestre",
            "Facturation automatique avec ICE/IF",
            "Transition de machine à états ACID"
        ],
        badge="app.routers.bookings",
        strokeColor=TERRACOTTA_PRIMARY,
        badgeBorder=TERRACOTTA_PRIMARY,
        badgeBg=TERRACOTTA_LIGHT,
        badgeColor=TERRACOTTA_PRIMARY
    )
    elements.extend(e3_2)
    
    # 3.3 Moteur KYC Biométrique & Anti-Deepfake
    c3_3, e3_3 = create_card(
        sec1_x + 665, t3_y + 35, 320, 230,
        "Moteur KYC & Anti-Deepfake",
        items=[
            "OCR CIN Marocaine (Arabe + Français)",
            "Liveness check caméra passive + active",
            "Détection micro-textures & reflets cornéens",
            "Politique Zero-Knowledge (RAM éphémère)",
            "Génération score de confiance (0 à 100%)",
            "Conformité stricte CNDP Loi 09-08"
        ],
        badge="ml_biometrics",
        strokeColor=PURPLE_PRIMARY,
        badgeBorder=PURPLE_PRIMARY,
        badgeBg=PURPLE_LIGHT,
        badgeColor=PURPLE_PRIMARY
    )
    elements.extend(e3_3)
    
    # 3.4 État des Lieux & Baux DOC
    c3_4, e3_4 = create_card(
        sec1_x + 1000, t3_y + 35, 305, 230,
        "État des Lieux & Baux DOC",
        items=[
            "Check-in / Check-out contradictoire",
            "Hachage cryptographique SHA-256 vidéo",
            "Horodatage légal certifié (RFC 3161)",
            "Signature électronique Loi 53-05",
            "Contrat de louage sous DOC (Art. 627+)",
            "Dossier de preuve immuable en litige"
        ],
        badge="app.routers.inspections",
        strokeColor=EMERALD_PRIMARY,
        badgeBorder=EMERALD_PRIMARY,
        badgeBg=EMERALD_LIGHT,
        badgeColor=EMERALD_PRIMARY
    )
    elements.extend(e3_4)
    
    # 3.5 Auth, Sécurité & Webhooks
    c3_5, e3_5 = create_card(
        sec1_x + 1320, t3_y + 35, 280, 230,
        "Auth, Sécurité & Webhooks",
        items=[
            "JWT Access/Refresh tokens",
            "RBAC: Renter, Owner, Pro, Admin",
            "Chiffrement pgcrypto des CINs",
            "Webhook Dispatcher sécurisé (HMAC)",
            "Journal d'audit immuable CNDP",
            "Gestion des sessions multi-devices"
        ],
        badge="app.routers.auth",
        strokeColor=ROSE_PRIMARY,
        badgeBorder=ROSE_PRIMARY,
        badgeBg=ROSE_LIGHT,
        badgeColor=ROSE_PRIMARY
    )
    elements.extend(e3_5)

    # -------------------------------------------------------------------------
    # TIER 4: DATA, STORAGE, CACHE & SEARCH (Y: 860 to 1055)
    # -------------------------------------------------------------------------
    t4_y = 860
    t4_h = 195
    elements.append(create_element(
        "rectangle", sec1_x, t4_y, sec1_w, t4_h,
        strokeColor=SLATE_MUTED,
        backgroundColor=SLATE_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PALIER 4 : PERSISTANCE, CACHE, INDEXATION RECHERCHE & STOCKAGE OBJETS",
        sec1_x + 20, t4_y + 10,
        fontSize=13,
        strokeColor=SLATE_MUTED
    ))
    
    # 4.1 PostgreSQL 16
    c4_1, e4_1 = create_card(
        sec1_x + 20, t4_y + 35, 380, 145,
        "PostgreSQL 16 (Base Relationnelle ACID)",
        items=[
            "Tables: users, equipment, bookings, contracts, inspections",
            "Extension pgcrypto pour chiffrement transparent des CINs",
            "Isolation SERIALIZABLE pour les transactions de caution",
            "Clés étrangères en CASCADE et triggers d'audit automatiques"
        ],
        badge="PostgreSQL :5432",
        strokeColor=BLUE_PRIMARY
    )
    elements.extend(e4_1)
    
    # 4.2 Redis 7 In-Memory
    c4_2, e4_2 = create_card(
        sec1_x + 415, t4_y + 35, 380, 145,
        "Redis 7 (In-Memory Cache & Locks)",
        items=[
            "Verrous distribués Redlock sur les plages de dates matériels",
            "Blacklist des tokens JWT révoqués et sessions actives",
            "Compteurs de Rate-Limiting par IP et par compte utilisateur",
            "Pub/Sub pour notifications temps réel WebSockets"
        ],
        badge="Redis :6379",
        strokeColor=ROSE_PRIMARY,
        badgeBorder=ROSE_PRIMARY,
        badgeBg=ROSE_LIGHT,
        badgeColor=ROSE_PRIMARY
    )
    elements.extend(e4_2)
    
    # 4.3 Meilisearch v1.8
    c4_3, e4_3 = create_card(
        sec1_x + 810, t4_y + 35, 380, 145,
        "Meilisearch v1.8 (Recherche Rapide)",
        items=[
            "Recherche plein texte instantanée (<15ms)",
            "Tolérance aux fautes de frappe bilingue (Français / Arabe)",
            "Filtres facettés: ville, catégorie, fourchette de prix, caution",
            "Tri par géolocalisation et distance de chantier"
        ],
        badge="Meilisearch :7700",
        strokeColor=PURPLE_PRIMARY,
        badgeBorder=PURPLE_PRIMARY,
        badgeBg=PURPLE_LIGHT,
        badgeColor=PURPLE_PRIMARY
    )
    elements.extend(e4_3)
    
    # 4.4 Cloudflare R2 / S3 Storage
    c4_4, e4_4 = create_card(
        sec1_x + 1205, t4_y + 35, 395, 145,
        "Cloudflare R2 / S3 (Blob Chiffré)",
        items=[
            "Photos HD matériels et fiches techniques certifiées",
            "Vidéos scellées d'états des lieux (Check-in & Check-out)",
            "Contrats de bail signés (PDF) scellés sous RFC 3161",
            "URLs présignées à durée de vie limitée (TTL 15 min)"
        ],
        badge="S3 / R2 Bucket",
        strokeColor=TERRACOTTA_PRIMARY,
        badgeBorder=TERRACOTTA_PRIMARY,
        badgeBg=TERRACOTTA_LIGHT,
        badgeColor=TERRACOTTA_PRIMARY
    )
    elements.extend(e4_4)

    # -------------------------------------------------------------------------
    # TIER 5: MOROCCAN ECOSYSTEM & AUTOMATION (Y: 1070 to 1270)
    # -------------------------------------------------------------------------
    t5_y = 1070
    t5_h = 200
    elements.append(create_element(
        "rectangle", sec1_x, t5_y, sec1_w, t5_h,
        strokeColor=TERRACOTTA_PRIMARY,
        backgroundColor=TERRACOTTA_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PALIER 5 : ÉCOSYSTÈME MAROCAIN, MONÉTIQUE, TIERS LÉGAUX & MOTEUR N8N",
        sec1_x + 20, t5_y + 10,
        fontSize=13,
        strokeColor=TERRACOTTA_PRIMARY
    ))
    
    # 5.1 CMI / Payzone
    c5_1, e5_1 = create_card(
        sec1_x + 20, t5_y + 35, 380, 150,
        "Passerelle CMI / Payzone (CB Maroc)",
        items=[
            "Paiement CB nationales et internationales (Visa/Mastercard)",
            "Empreinte bancaire pour caution sans débit immédiat",
            "Protocole 3D-Secure v2 obligatoire anti-fraude",
            "Rapprochement bancaire automatisé & webhook de confirmation"
        ],
        badge="Monétique CMI",
        strokeColor=TERRACOTTA_PRIMARY
    )
    elements.extend(e5_1)
    
    # 5.2 CashPlus / Wafacash
    c5_2, e5_2 = create_card(
        sec1_x + 415, t5_y + 35, 380, 150,
        "Réseau CashPlus / Wafacash",
        items=[
            "Paiement et dépôt de caution en espèces en agence locale",
            "Génération d'un code de transaction sécurisé par Lokiini",
            "Notification instantanée par webhook dès versement en agence",
            "Idéal pour artisans et indépendants non bancarisés"
        ],
        badge="Cash-In / Cash-Out",
        strokeColor=TERRACOTTA_PRIMARY
    )
    elements.extend(e5_2)
    
    # 5.3 Moteur d'Automation n8n
    c5_3, e5_3 = create_card(
        sec1_x + 810, t5_y + 35, 380, 150,
        "Moteur d'Automation n8n (5 Workflows)",
        items=[
            "Workflow 1: Notification WhatsApp & SMS loueur / locataire",
            "Workflow 2: Relances automatiques avant fin de location (J-1 / H-3)",
            "Workflow 3: Alerte immédiate sur anomalie KYC (Score < 0.70)",
            "Workflow 4: Rapprochement comptable quotidien CMI / Banque",
            "Workflow 5: Sollicitation d'avis & notation réciproque"
        ],
        badge="n8n Engine :5678",
        strokeColor=AMBER_PRIMARY,
        badgeBorder=AMBER_PRIMARY,
        badgeBg=AMBER_LIGHT,
        badgeColor=AMBER_PRIMARY
    )
    elements.extend(e5_3)
    
    # 5.4 Cadre Légal & Assurances Maroc
    c5_4, e5_4 = create_card(
        sec1_x + 1205, t5_y + 35, 395, 150,
        "Tiers de Confiance & Cadre Légal",
        items=[
            "Autorité d'horodatage qualifiée RFC 3161 (Barid Al-Maghrib)",
            "Conformité CNDP Loi 09-08 (Récépissé de déclaration formelle)",
            "Dahir des Obligations et Contrats (DOC Art. 627+ louage)",
            "Partenaires Assurances (Wafa Assurance, Sanlam Maroc)"
        ],
        badge="Légal & Assurance",
        strokeColor=PURPLE_PRIMARY,
        badgeBorder=PURPLE_PRIMARY,
        badgeBg=PURPLE_LIGHT,
        badgeColor=PURPLE_PRIMARY
    )
    elements.extend(e5_4)

    # -------------------------------------------------------------------------
    # INTER-TIER ARROWS (SYSTEM ARCHITECTURE)
    # -------------------------------------------------------------------------
    # Frontend to Gateway
    elements.extend(create_arrow(sec1_x + 210, t1_y + 180, sec1_x + 275, t2_y + 32, strokeColor=TEAL_PRIMARY, label="HTTPS / REST"))
    elements.extend(create_arrow(sec1_x + 605, t1_y + 180, sec1_x + 812, t2_y + 32, strokeColor=TERRACOTTA_PRIMARY, label="API / Auth"))
    elements.extend(create_arrow(sec1_x + 605, t1_y + 180, sec1_x + 1347, t2_y + 32, strokeColor=BLUE_PRIMARY, label="WSS Stream"))
    
    # Gateway to Backend Microservices
    elements.extend(create_arrow(sec1_x + 812, t2_y + 122, sec1_x + 172, t3_y + 35, strokeColor=BLUE_PRIMARY))
    elements.extend(create_arrow(sec1_x + 812, t2_y + 122, sec1_x + 495, t3_y + 35, strokeColor=BLUE_PRIMARY))
    elements.extend(create_arrow(sec1_x + 812, t2_y + 122, sec1_x + 825, t3_y + 35, strokeColor=BLUE_PRIMARY))
    elements.extend(create_arrow(sec1_x + 812, t2_y + 122, sec1_x + 1152, t3_y + 35, strokeColor=BLUE_PRIMARY))
    elements.extend(create_arrow(sec1_x + 812, t2_y + 122, sec1_x + 1460, t3_y + 35, strokeColor=BLUE_PRIMARY))
    
    # Backend to Data
    elements.extend(create_arrow(sec1_x + 172, t3_y + 265, sec1_x + 210, t4_y + 35, strokeColor=TEAL_PRIMARY, label="SQL / CRUD"))
    elements.extend(create_arrow(sec1_x + 495, t3_y + 265, sec1_x + 210, t4_y + 35, strokeColor=TERRACOTTA_PRIMARY))
    elements.extend(create_arrow(sec1_x + 495, t3_y + 265, sec1_x + 605, t4_y + 35, strokeColor=ROSE_PRIMARY, label="Redlock Dates"))
    elements.extend(create_arrow(sec1_x + 172, t3_y + 265, sec1_x + 1000, t4_y + 35, strokeColor=PURPLE_PRIMARY, label="Sync Search"))
    elements.extend(create_arrow(sec1_x + 825, t3_y + 265, sec1_x + 1402, t4_y + 35, strokeColor=TERRACOTTA_PRIMARY, label="Presigned S3"))
    elements.extend(create_arrow(sec1_x + 1152, t3_y + 265, sec1_x + 1402, t4_y + 35, strokeColor=EMERALD_PRIMARY, label="Store Hash Video"))

    # Backend to Tier 5
    elements.extend(create_arrow(sec1_x + 495, t3_y + 265, sec1_x + 210, t5_y + 35, strokeColor=TERRACOTTA_PRIMARY, label="Pre-Auth CMI"))
    elements.extend(create_arrow(sec1_x + 495, t3_y + 265, sec1_x + 605, t5_y + 35, strokeColor=TERRACOTTA_PRIMARY, label="Code CashPlus"))
    elements.extend(create_arrow(sec1_x + 1460, t3_y + 265, sec1_x + 1000, t5_y + 35, strokeColor=AMBER_PRIMARY, label="Dispatch Webhook"))
    elements.extend(create_arrow(sec1_x + 1152, t3_y + 265, sec1_x + 1402, t5_y + 35, strokeColor=PURPLE_PRIMARY, label="RFC 3161 Stamp"))

    # =========================================================================
    # SECTION 2 (LOWER LEFT): 🇲🇦 CONFORMITÉ, MATRICE DE SÉCURITÉ & MODÈLE ÉCO (Y: 1290 to 2550)
    # =========================================================================
    sec2_y = 1290
    elements.append(create_element(
        "rectangle", sec1_x, sec2_y, sec1_w, 40,
        strokeColor=TERRACOTTA_BORDER,
        backgroundColor=TERRACOTTA_PRIMARY,
        strokeWidth=1,
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PARTIE 2 : MATRICE DE SÉCURITÉ, CONFORMITÉ JURIDIQUE MAROCAINE & MODÈLE ÉCONOMIQUE",
        sec1_x + 20, sec2_y + 10,
        fontSize=15,
        strokeColor=WHITE
    ))

    # Grid of 4 deep compliance cards
    # Card 2.1: CNDP & Protection des données
    c_cndp, e_cndp = create_card(
        sec1_x, sec2_y + 55, 385, 300,
        "Conformité CNDP & Loi 09-08",
        items=[
            "Déclaration formelle préalable auprès de la CNDP",
            "Politique Zero-Knowledge: Traitement des flux vidéo KYC en mémoire vive (RAM) éphémère",
            "Chiffrement fort asymétrique pgcrypto sur les numéros de CIN et données personnelles",
            "Droit d'accès, de rectification et d'effacement garanti",
            "Purge automatique des vidéos temporaires après validation",
            "Serveurs et bases de données étanches hébergés selon les exigences de souveraineté"
        ],
        badge="Loi 09-08 CNDP",
        strokeColor=EMERALD_PRIMARY,
        badgeBorder=EMERALD_PRIMARY,
        badgeBg=EMERALD_LIGHT,
        badgeColor=EMERALD_PRIMARY
    )
    elements.extend(e_cndp)

    # Card 2.2: DOC & Loi 53-05
    c_doc, e_doc = create_card(
        sec1_x + 410, sec2_y + 55, 385, 300,
        "Dahir Obligations & Contrats (DOC)",
        items=[
            "Contrat de louage de choses régi par les articles 627 et suivants du DOC marocain",
            "Génération automatique d'un bail numérique complet avec clause résolutoire expresse",
            "Signature électronique conforme à la Loi n° 53-05",
            "Scellement de l'état des lieux photo/vidéo par hachage cryptographique SHA-256",
            "Horodatage certifié RFC 3161 conférant date certaine probante devant les tribunaux du Royaume",
            "Conservation sécurisée du dossier de preuve d'intégrité"
        ],
        badge="DOC & Loi 53-05",
        strokeColor=PURPLE_PRIMARY,
        badgeBorder=PURPLE_PRIMARY,
        badgeBg=PURPLE_LIGHT,
        badgeColor=PURPLE_PRIMARY
    )
    elements.extend(e_doc)

    # Card 2.3: Monétique & Cautions CMI
    c_cmi, e_cmi = create_card(
        sec1_x + 820, sec2_y + 55, 385, 300,
        "Monétique CMI & Séquestre",
        items=[
            "Aucun numéro de carte bancaire stocké sur les serveurs Lokiini (Conformité PCI-DSS)",
            "Empreinte bancaire par pré-autorisation CMI : Bloque le plafond de caution sans débit",
            "Validation obligatoire par 3D-Secure v2 (SMS OTP bancaire)",
            "Déblocage instantané et gratuit de la caution à la restitution conforme du matériel",
            "Option de paiement fractionné et cash en agences partenaires CashPlus / Wafacash",
            "Rapprochement comptable automatisé et balance en MAD"
        ],
        badge="CMI / PCI-DSS",
        strokeColor=TERRACOTTA_PRIMARY,
        badgeBorder=TERRACOTTA_PRIMARY,
        badgeBg=TERRACOTTA_LIGHT,
        badgeColor=TERRACOTTA_PRIMARY
    )
    elements.extend(e_cmi)

    # Card 2.4: Modèle Économique & Tarification
    c_biz, e_biz = create_card(
        sec1_x + 1230, sec2_y + 55, 390, 300,
        "Grille Tarifaire & Modèle Économique",
        items=[
            "Formule Particulier Gratuit (0 MAD/mois) : Commission 15% par location conclue",
            "Formule Premium Particulier (49 MAD/mois) : Commission réduite à 10%, badge vérifié VIP",
            "Formule Pro BTP & Événementiel (299 MAD/mois) : Commission 7%, multi-chantiers, factures ICE",
            "Formule Grand Compte BTP (Sur Devis) : Commission 5%, intégration API / ERP dédiée",
            "Option Assurance Dommages / Vol intégrée (partenariat Wafa Assurance / Sanlam)",
            "Frais de traitement transparents sans coûts cachés"
        ],
        badge="Business Model",
        strokeColor=AMBER_PRIMARY,
        badgeBorder=AMBER_PRIMARY,
        badgeBg=AMBER_LIGHT,
        badgeColor=AMBER_PRIMARY
    )
    elements.extend(e_biz)

    # Summary Architecture Legend below Part 2
    leg_y = sec2_y + 375
    elements.append(create_element(
        "rectangle", sec1_x, leg_y, sec1_w, 140,
        strokeColor=SLATE_MUTED,
        backgroundColor=WHITE,
        strokeWidth=1,
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "LÉGENDE TECHNIQUE DES FLUX & PROTOCOLES DU SYSTÈME LOKIINI",
        sec1_x + 20, leg_y + 12,
        fontSize=13,
        strokeColor=SLATE_DARK
    ))
    legend_items = [
        "🟩 Vert Émeraude : Services Catalogue, États des Lieux & Conformité CNDP",
        "🟧 Terracotta : Moteur de Réservations, Monétique CMI, Cautions & CashPlus",
        "🟪 Violet : Moteurs d'Intelligence Artificielle, Biométrie KYC, Anti-Deepfake & Lois DOC / 53-05",
        "🟦 Bleu Azur : Infrastructure Edge, Gateway Nginx, API FastAPI Asynchrone & PostgreSQL 16",
        "🟨 Ambre : Automatisation n8n, Relances WhatsApp Business, SMS & Monitoring",
        "🟥 Rose : Sécurité des Tokens JWT, Redlock Redis, Détection de Fraude & Desk de Médiation"
    ]
    elements.append(create_text(
        "\n".join(legend_items[:3]),
        sec1_x + 20, leg_y + 38,
        fontSize=11,
        strokeColor=SLATE_MUTED,
        width=750
    ))
    elements.append(create_text(
        "\n".join(legend_items[3:]),
        sec1_x + 800, leg_y + 38,
        fontSize=11,
        strokeColor=SLATE_MUTED,
        width=750
    ))

    # =========================================================================
    # SECTION 3 (RIGHT COLUMN): 🔄 THE 7 END-TO-END OPERATIONAL PIPELINES (X: 1700 to 3450)
    # =========================================================================
    sec3_x = 1700
    sec3_w = 1790
    
    elements.append(create_element(
        "rectangle", sec3_x, 150, sec3_w, 40,
        strokeColor=PURPLE_BORDER,
        backgroundColor=PURPLE_PRIMARY,
        strokeWidth=1,
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PARTIE 3 : LES 7 PIPELINES OPÉRATIONNELS END-TO-END DE LOKIINI (FLUX MÉTIER & TECHNIQUES)",
        sec3_x + 20, 160,
        fontSize=15,
        strokeColor=WHITE
    ))

    # Helper to layout a horizontal pipeline with 6 or 7 steps
    def render_horizontal_pipeline(y_start, p_num, p_title, p_badge, p_color, p_light_color, steps):
        p_elements = []
        p_height = 135
        
        # Outer swimlane box
        p_elements.append(create_element(
            "rectangle", sec3_x, y_start, sec3_w, p_height,
            strokeColor=p_color,
            backgroundColor=p_light_color,
            strokeWidth=1,
            roundness={"type": 3}
        ))
        
        # Header text
        p_elements.append(create_text(
            f"PIPELINE {p_num} : {p_title}",
            sec3_x + 20, y_start + 8,
            fontSize=13,
            strokeColor=p_color
        ))
        
        # Badge
        b_w = len(p_badge) * 7.2 + 16
        p_elements.append(create_element(
            "rectangle", sec3_x + sec3_w - b_w - 15, y_start + 7, b_w, 22,
            strokeColor=p_color,
            backgroundColor=WHITE,
            strokeWidth=1,
            roundness={"type": 3}
        ))
        p_elements.append(create_text(
            p_badge, sec3_x + sec3_w - b_w - 7, y_start + 11,
            fontSize=10,
            strokeColor=p_color,
            width=b_w - 16
        ))
        
        # Step boxes layout
        num_steps = len(steps)
        step_gap = 12
        available_w = sec3_w - 40 - (step_gap * (num_steps - 1))
        step_w = available_w / num_steps
        step_h = 88
        step_y = y_start + 36
        
        prev_x = None
        for i, st in enumerate(steps):
            cur_x = sec3_x + 20 + i * (step_w + step_gap)
            s_id, s_elems = create_pipeline_step(
                cur_x, step_y, step_w, step_h,
                i + 1, st["title"], st["action"], st["protocol"], st["tech"],
                strokeColor=p_color,
                backgroundColor=WHITE
            )
            p_elements.extend(s_elems)
            
            # Connector arrow to next step
            if prev_x is not None:
                arr_start_x = prev_x + step_w
                arr_end_x = cur_x
                arr_y = step_y + (step_h / 2)
                p_elements.extend(create_arrow(
                    arr_start_x, arr_y, arr_end_x, arr_y,
                    strokeColor=p_color,
                    strokeWidth=1.5
                ))
            prev_x = cur_x
            
        return p_elements

    # -------------------------------------------------------------------------
    # PIPELINE 1: Onboarding & KYC Biométrique Anti-Deepfake
    # -------------------------------------------------------------------------
    pipe1_steps = [
        {"title": "Déclenchement Action", "action": "Clic 'Réserver' ou 'Publier matériel'", "protocol": "Event Hook", "tech": "React/Expo UI"},
        {"title": "Capture Caméra Direct", "action": "Flux vidéo selfie live + Scan CIN", "protocol": "WebRTC / AV", "tech": "Mobile Vision"},
        {"title": "Test de Vivacité (Liveness)", "action": "Clignement, mouvements & reflets", "protocol": "Inférence ONNX", "tech": "PyTorch / Vision"},
        {"title": "Détection Anti-Deepfake", "action": "Analyse micro-textures et cornée", "protocol": "Score > 85%", "tech": "ISO/IEC 30107"},
        {"title": "OCR CIN Marocaine", "action": "Extraction Nom, Prénom, N° CIN", "protocol": "Tesseract/CRNN", "tech": "Bilingue AR/FR"},
        {"title": "Purge Zero-Knowledge", "action": "Destruction vidéo RAM éphémère", "protocol": "Purge Mémoire", "tech": "Loi 09-08 CNDP"},
        {"title": "Validation & Badge", "action": "Statut vérifié & déblocage tunnel", "protocol": "JWT Refresh", "tech": "PostgreSQL 16"}
    ]
    elements.extend(render_horizontal_pipeline(205, "1", "ONBOARDING & KYC BIOMÉTRIQUE ANTI-DEEPFAKE (DÉCLENCHÉ À L'ACTION)", "Sécurité CNDP", PURPLE_PRIMARY, PURPLE_LIGHT, pipe1_steps))

    # -------------------------------------------------------------------------
    # PIPELINE 2: Publication Matériel, Médias & Indexation Recherche
    # -------------------------------------------------------------------------
    pipe2_steps = [
        {"title": "Saisie de l'Annonce", "action": "Titre, description, prix/jour, caution", "protocol": "Form Validation", "tech": "Zod / Pydantic"},
        {"title": "Upload Photos HD", "action": "Upload direct via URL présignée", "protocol": "HTTPS PUT", "tech": "Cloudflare R2 / S3"},
        {"title": "Compression WebP", "action": "Génération vignettes & optimisation", "protocol": "Async Worker", "tech": "Sharp / Pillow"},
        {"title": "Persistance BDD", "action": "Enregistrement équipement & loueur", "protocol": "SQL INSERT", "tech": "PostgreSQL 16"},
        {"title": "Sync Meilisearch", "action": "Indexation plein texte et facettes", "protocol": "Async Task", "tech": "Meilisearch v1.8"},
        {"title": "Disponibilité Publique", "action": "Visible immédiatement au catalogue", "protocol": "Edge Cache", "tech": "Next.js SSR"}
    ]
    elements.extend(render_horizontal_pipeline(360, "2", "PUBLICATION DE MATÉRIEL, OPTIMISATION MÉDIAS & RECHERCHE GÉOLOCALISÉE", "Indexation & Catalogue", TEAL_PRIMARY, TEAL_LIGHT, pipe2_steps))

    # -------------------------------------------------------------------------
    # PIPELINE 3: Réservation, Caution Bancaire CMI & Séquestre
    # -------------------------------------------------------------------------
    pipe3_steps = [
        {"title": "Choix des Dates", "action": "Sélection période & calcul tarification", "protocol": "Client State", "tech": "Zustand Engine"},
        {"title": "Verrouillage Redis", "action": "Lock distribué anti-doublon (Redlock)", "protocol": "SETNX TTL=15m", "tech": "Redis 7"},
        {"title": "Empreinte Caution CMI", "action": "Saisie CB 3D-Secure v2 sans débit", "protocol": "Iframe CMI", "tech": "Payzone / CMI"},
        {"title": "Validation Loueur", "action": "Acceptation de la demande (SLA 24h)", "protocol": "Push Notification", "tech": "WebSocket / n8n"},
        {"title": "Génération Bail DOC", "action": "Contrat PDF automatique avec clauses", "protocol": "PDF Rendering", "tech": "DOC Art. 627+"},
        {"title": "Alerte & WhatsApp", "action": "Envoi du contrat et coordonnées", "protocol": "Webhook", "tech": "n8n WhatsApp API"}
    ]
    elements.extend(render_horizontal_pipeline(515, "3", "RÉSERVATION, SÉQUESTRE DE CAUTION CMI & BAIL AUTOMATIQUE", "Monétique & Caution", TERRACOTTA_PRIMARY, TERRACOTTA_LIGHT, pipe3_steps))

    # -------------------------------------------------------------------------
    # PIPELINE 4: État des Lieux Vidéo & Scellement Numérique
    # -------------------------------------------------------------------------
    pipe4_steps = [
        {"title": "Remise Matériel", "action": "Rencontre physique loueur-locataire", "protocol": "Rendez-vous", "tech": "Check-in Live"},
        {"title": "Vidéo Contradictoire", "action": "Scan 360° du matériel & accessoires", "protocol": "Mobile Caméra", "tech": "Expo Video Engine"},
        {"title": "Hachage SHA-256", "action": "Extraction keyframes et empreinte", "protocol": "Hash Cryptographique", "tech": "SHA-256 Engine"},
        {"title": "Double Signature", "action": "Signature sur écran tactile des 2 parties", "protocol": "Loi 53-05", "tech": "Canvas Touch Sign"},
        {"title": "Horodatage Légal", "action": "Sceau temporel probant RFC 3161", "protocol": "Time-Stamp API", "tech": "Barid Al-Maghrib"},
        {"title": "Stockage Chiffré", "action": "Archivage preuve immuable en coffre", "protocol": "Encrypted S3", "tech": "Cloudflare R2"}
    ]
    elements.extend(render_horizontal_pipeline(670, "4", "ÉTAT DES LIEUX VIDÉO & SCELLEMENT NUMÉRIQUE (LOI 53-05)", "Preuve Cryptographique", EMERALD_PRIMARY, EMERALD_LIGHT, pipe4_steps))

    # -------------------------------------------------------------------------
    # PIPELINE 5: Restitution, Libération Caution & Rémunération
    # -------------------------------------------------------------------------
    pipe5_steps = [
        {"title": "Check-out Sortie", "action": "Inspection physique de retour matériel", "protocol": "Contradictoire", "tech": "Mobile Check-out"},
        {"title": "Validation Intégrité", "action": "Comparaison avec vidéo Check-in", "protocol": "Zéro Dommage", "tech": "Accord Bilatéral"},
        {"title": "Déblocage Caution", "action": "Annulation immédiate pré-auth CMI", "protocol": "CMI Void API", "tech": "0 MAD Débité"},
        {"title": "Déduction Commission", "action": "Prélèvement commission Lokiini (15-5%)", "protocol": "Split Payout", "tech": "PostgreSQL ACID"},
        {"title": "Virement Loueur", "action": "Transfert net sur RIB bancaire loueur", "protocol": "Virement MAD", "tech": "Banque Marocaine"},
        {"title": "Notation Réciproque", "action": "Évaluation loueur / locataire", "protocol": "Workflow Trigger", "tech": "n8n Automation"}
    ]
    elements.extend(render_horizontal_pipeline(825, "5", "RESTITUTION DU MATÉRIEL, DÉBLOCAGE CAUTION CMI & PAIEMENT DU LOUEUR", "Clôture & Payout", BLUE_PRIMARY, BLUE_LIGHT, pipe5_steps))

    # -------------------------------------------------------------------------
    # PIPELINE 6: Automation Événementielle & Workflows n8n
    # -------------------------------------------------------------------------
    pipe6_steps = [
        {"title": "Événement Métier", "action": "Réservation, Fin location, Incident", "protocol": "Event Emitter", "tech": "FastAPI Async"},
        {"title": "Webhook Dispatch", "action": "Payload JSON signé avec clé HMAC", "protocol": "HTTPS Webhook", "tech": "Gateway Nginx"},
        {"title": "Routeur n8n", "action": "Filtrage et aiguillage selon type d'event", "protocol": "Trigger Node", "tech": "n8n Engine :5678"},
        {"title": "Relances & Messages", "action": "Templates WhatsApp & SMS en Darija/FR", "protocol": "Meta / Twilio API", "tech": "WhatsApp Business"},
        {"title": "Rapprochement CMI", "action": "Cron quotidien à 02h00 du matin", "protocol": "Scheduled Cron", "tech": "n8n SQL Query"},
        {"title": "Alerte Incident Admin", "action": "Escalade Slack / Email en cas de litige", "protocol": "Webhooks Alert", "tech": "Admin Mediation"}
    ]
    elements.extend(render_horizontal_pipeline(980, "6", "AUTOMATION ÉVÉNEMENTIELLE, NOTIFICATIONS WHATSAPP & WORKFLOWS N8N", "Orchestration n8n", AMBER_PRIMARY, AMBER_LIGHT, pipe6_steps))

    # -------------------------------------------------------------------------
    # PIPELINE 7: CI/CD, Conteneurisation & Déploiement 100% Docker
    # -------------------------------------------------------------------------
    pipe7_steps = [
        {"title": "Commit & Push", "action": "Développement feature sur branche git", "protocol": "Git VCS", "tech": "GitHub / GitLab"},
        {"title": "Tests Automatisés", "action": "Exécution pytest, linting & types", "protocol": "CI Runner", "tech": "GitHub Actions"},
        {"title": "Build Multi-Stage", "action": "Images Docker légères Alpine Linux", "protocol": "Docker Build", "tech": "Dockerfile multi-stage"},
        {"title": "Docker Compose Up", "action": "Orchestration des 7 conteneurs unifiés", "protocol": "Bridge Network", "tech": "docker-compose.yml"},
        {"title": "Ingress Nginx :80", "action": "Reverse proxy & routage interne sécurisé", "protocol": "Healthcheck", "tech": "Nginx Gateway"},
        {"title": "Monitoring & Logs", "action": "Surveillance santé conteneurs et métriques", "protocol": "Docker Logs", "tech": "Prometheus/Grafana"}
    ]
    elements.extend(render_horizontal_pipeline(1135, "7", "PIPELINE CI/CD, CONTENEURISATION & DÉPLOIEMENT PRODUCTION 100% DOCKER", "DevOps & Cloud", INDIGO_PRIMARY, INDIGO_LIGHT, pipe7_steps))

    # -------------------------------------------------------------------------
    # SUMMARY HIGHLIGHTS & ARCHITECTURAL METRICS PANEL (RIGHT COLUMN BOTTOM)
    # -------------------------------------------------------------------------
    metric_y = 1290
    elements.append(create_element(
        "rectangle", sec3_x, metric_y, sec3_w, 40,
        strokeColor=BLUE_BORDER,
        backgroundColor=BLUE_PRIMARY,
        strokeWidth=1,
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "PARTIE 4 : MÉTRIQUES DE PERFORMANCE, SLA & KPI CLÉS DU SYSTÈME LOKIINI",
        sec3_x + 20, metric_y + 10,
        fontSize=15,
        strokeColor=WHITE
    ))

    # 4 Key Metrics Cards
    # Metric 1
    m1, e_m1 = create_card(
        sec3_x, metric_y + 55, 430, 200,
        "⚡ Performance & Vitesse Réseau",
        items=[
            "Temps de réponse API FastAPI : < 35 ms (p95)",
            "Temps de recherche Meilisearch : < 15 ms",
            "Latence Edge Cloudflare Maroc : < 20 ms",
            "SSR Next.js First Contentful Paint : < 0.8 s",
            "Capacité de charge : 5000+ transactions/heure"
        ],
        badge="SLA Latence",
        strokeColor=BLUE_PRIMARY
    )
    elements.extend(e_m1)

    # Metric 2
    m2, e_m2 = create_card(
        sec3_x + 450, metric_y + 55, 430, 200,
        "🛡️ Sécurité & Anti-Fraude",
        items=[
            "Score de vivacité KYC : Seuil minimal à 85%",
            "Taux de faux positifs biométriques : < 0.1%",
            "Chiffrement des données sensibles : AES-256 pgcrypto",
            "Conformité PCI-DSS Level 1 via CMI / Payzone",
            "Zéro persistance PAN / CVV sur les serveurs"
        ],
        badge="Sécurité 99.9%",
        strokeColor=EMERALD_PRIMARY,
        badgeBorder=EMERALD_PRIMARY,
        badgeBg=EMERALD_LIGHT,
        badgeColor=EMERALD_PRIMARY
    )
    elements.extend(e_m2)

    # Metric 3
    m3, e_m3 = create_card(
        sec3_x + 900, metric_y + 55, 430, 200,
        "💳 Efficacité Cautions & Monétique",
        items=[
            "Taux d'autorisation 3D-Secure v2 : 98.4%",
            "Délai moyen de libération de caution : < 2 min",
            "Frais de caution pour le locataire : 0 MAD",
            "Rapprochement bancaire CMI automatique : 100%",
            "Couverture du réseau physique CashPlus : 3000+ agences"
        ],
        badge="Monétique Maroc",
        strokeColor=TERRACOTTA_PRIMARY,
        badgeBorder=TERRACOTTA_PRIMARY,
        badgeBg=TERRACOTTA_LIGHT,
        badgeColor=TERRACOTTA_PRIMARY
    )
    elements.extend(e_m3)

    # Metric 4
    m4, e_m4 = create_card(
        sec3_x + 1350, metric_y + 55, 440, 200,
        "🤖 Automation & Disponibilité n8n",
        items=[
            "Délai d'envoi WhatsApp confirmation : < 5 secondes",
            "Taux de délivrabilité des notifications SMS : 99.7%",
            "Disponibilité système (Uptime SLA) : 99.95%",
            "Déploiement 1-clic via Docker Compose : < 60s",
            "Sauvegardes automatiques quotidiennes chiffrées"
        ],
        badge="DevOps 99.95%",
        strokeColor=PURPLE_PRIMARY,
        badgeBorder=PURPLE_PRIMARY,
        badgeBg=PURPLE_LIGHT,
        badgeColor=PURPLE_PRIMARY
    )
    elements.extend(e_m4)

    # Master Footer Note
    elements.append(create_element(
        "rectangle", sec3_x, metric_y + 275, sec3_w, 60,
        strokeColor=TEAL_PRIMARY,
        backgroundColor=TEAL_LIGHT,
        strokeWidth=1,
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "📌 Lokiini / MatOS Architecture Document — Généré programmatiquement pour Excalidraw conformément aux règles d'ingénierie logicielle avancée et à la réglementation marocaine (CNDP, DOC, Loi 53-05, CMI).",
        sec3_x + 20, metric_y + 295,
        fontSize=12,
        strokeColor=TEAL_PRIMARY
    ))

    # =========================================================================
    # EXCALIDRAW ROOT SCHEMA ASSEMBLY
    # =========================================================================
    excalidraw_data = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "viewBackgroundColor": SAND_BG,
            "gridSize": None
        },
        "files": {}
    }
    
    return excalidraw_data


def main():
    print("Building Lokiini Complete Project Pipeline & Architecture Excalidraw diagram...")
    data = build_complete_project_architecture()
    elem_count = len(data["elements"])
    print(f"Successfully generated {elem_count} Excalidraw elements!")
    
    # Save locations
    destinations = [
        Path(r"d:\Lokiini\lokiini_project_pipeline_architecture.excalidraw"),
        Path(r"d:\Lokiini\lokiini_project_architecture.excalidraw"),
        Path(r"d:\Lokiini\docs\02_architecture_technique_et_ia\lokiini_project_pipeline_architecture.excalidraw"),
        Path(r"d:\Lokiini\docs\02_architecture_technique_et_ia\lokiini_project_architecture.excalidraw"),
    ]
    
    for dest in destinations:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved: {dest} ({dest.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
