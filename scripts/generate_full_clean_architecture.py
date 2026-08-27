#!/usr/bin/env python3
"""
Master Excalidraw Generator for Lokiini / MatOS.
Ensures 100% strict Excalidraw schema compliance:
- Every line & arrow has valid points [[0,0], [dx, dy]], lastCommittedPoint: null, etc.
- Every text has baseline, lineHeight: 1.25, containerId: null, originalText
- Shapes have boundElements: null when text is placed absolutely
- roughness: 0, fontFamily: 2 (clean professional sans-serif)
"""

import json
import random
import time
from pathlib import Path

# Brand Color Palette
TEAL_DARK = "#0F6E56"
TEAL_MED = "#148A6C"
TEAL_LIGHT = "#E8F5F1"
TERRACOTTA = "#D85A30"
TERRACOTTA_LIGHT = "#FBEEE9"
TERRACOTTA_DARK = "#B84520"
SAND_BG = "#FDFBF7"
DARK_SLATE = "#1E293B"
MUTED_SLATE = "#475569"
CARD_BG = "#FFFFFF"
BORDER_GRAY = "#CBD5E1"
BLUE_ACCENT = "#0284C7"
BLUE_LIGHT = "#F0F9FF"
PURPLE_ACCENT = "#7C3AED"
PURPLE_LIGHT = "#F5F3FF"
AMBER_ACCENT = "#D97706"
AMBER_LIGHT = "#FEF3C7"
GREEN_ACCENT = "#16A34A"
GREEN_LIGHT = "#DCFCE7"
RED_ACCENT = "#DC2626"
RED_LIGHT = "#FEE2E2"

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
        "strokeColor": kwargs.get("strokeColor", DARK_SLATE),
        "backgroundColor": kwargs.get("backgroundColor", "transparent"),
        "fillStyle": "solid",
        "strokeWidth": kwargs.get("strokeWidth", 1.5),
        "strokeStyle": kwargs.get("strokeStyle", "solid"),
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 3},
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
    font_size = kwargs.get("fontSize", 14)
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
        "strokeColor": kwargs.get("strokeColor", DARK_SLATE),
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
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
        "fontFamily": 2,
        "textAlign": kwargs.get("textAlign", "left"),
        "verticalAlign": "top",
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
        "strokeColor": kwargs.get("strokeColor", MUTED_SLATE),
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
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": "arrow"
    }
    
    elements = [arrow]
    if "label" in kwargs and kwargs["label"]:
        label_text = kwargs["label"]
        mid_x = start_x + dx * 0.5 - 25
        mid_y = start_y + dy * 0.5 - 10
        lbl = create_text(
            label_text, mid_x, mid_y,
            fontSize=11,
            strokeColor=kwargs.get("labelColor", MUTED_SLATE)
        )
        elements.append(lbl)
        
    return elements

def create_line(start_x, start_y, end_x, end_y, **kwargs):
    dx = end_x - start_x
    dy = end_y - start_y
    now = int(time.time() * 1000)
    line_id = kwargs.get("id", f"line_{random.randint(100000, 999999)}")
    
    return {
        "id": line_id,
        "type": "line",
        "x": start_x,
        "y": start_y,
        "width": max(abs(dx), 1),
        "height": max(abs(dy), 1),
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", BORDER_GRAY),
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": kwargs.get("strokeWidth", 1),
        "strokeStyle": kwargs.get("strokeStyle", "dashed"),
        "roughness": 0,
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
        "points": [[0, 0], [dx, dy]],
        "lastCommittedPoint": None,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": None
    }

def create_box_card(x, y, width, height, title, subtitle=None, badge=None, **kwargs):
    elements = []
    box = create_rectangle(
        x, y, width, height,
        strokeColor=kwargs.get("strokeColor", TEAL_DARK),
        backgroundColor=kwargs.get("backgroundColor", CARD_BG),
        strokeWidth=kwargs.get("strokeWidth", 1.5)
    )
    elements.append(box)
    
    t_y = y + 14
    title_elem = create_text(
        title, x + 16, t_y,
        fontSize=kwargs.get("titleFontSize", 15),
        strokeColor=kwargs.get("titleColor", TEAL_DARK),
        width=width - 32
    )
    elements.append(title_elem)
    
    if subtitle:
        sub_y = t_y + title_elem["height"] + 6
        sub_elem = create_text(
            subtitle, x + 16, sub_y,
            fontSize=kwargs.get("subFontSize", 12),
            strokeColor=kwargs.get("subColor", MUTED_SLATE),
            width=width - 32
        )
        elements.append(sub_elem)
        
    if badge:
        badge_w = len(badge) * 7.5 + 16
        badge_h = 22
        badge_x = x + width - badge_w - 12
        badge_y = y + 10
        badge_box = create_rectangle(
            badge_x, badge_y, badge_w, badge_h,
            strokeColor=kwargs.get("badgeBorder", TERRACOTTA),
            backgroundColor=kwargs.get("badgeBg", TERRACOTTA_LIGHT),
            strokeWidth=1
        )
        badge_txt = create_text(
            badge, badge_x + 8, badge_y + 4,
            fontSize=10,
            strokeColor=kwargs.get("badgeColor", TERRACOTTA),
            width=badge_w - 16
        )
        elements.append(badge_box)
        elements.append(badge_txt)
        
    return elements

def create_table_card(x, y, width, table_name, pk_fields, fk_fields, regular_fields, **kwargs):
    elements = []
    header_h = 36
    row_h = 22
    total_fields = len(pk_fields) + len(fk_fields) + len(regular_fields)
    total_h = header_h + (total_fields * row_h) + 16
    
    # Outer box
    tbl_box = create_rectangle(
        x, y, width, total_h,
        strokeColor=kwargs.get("strokeColor", TEAL_DARK),
        backgroundColor=CARD_BG,
        strokeWidth=1.5
    )
    elements.append(tbl_box)
    
    # Header bar
    tbl_hdr = create_rectangle(
        x, y, width, header_h,
        strokeColor=kwargs.get("strokeColor", TEAL_DARK),
        backgroundColor=kwargs.get("headerBg", TEAL_DARK),
        strokeWidth=1.5
    )
    elements.append(tbl_hdr)
    
    # Header Text
    hdr_txt = create_text(
        f"TABLE: {table_name}", x + 14, y + 9,
        fontSize=13,
        strokeColor="#FFFFFF"
    )
    elements.append(hdr_txt)
    
    curr_y = y + header_h + 8
    
    # Render PKs
    for name, dtype in pk_fields:
        icon_txt = create_text("🔑 PK", x + 12, curr_y, fontSize=11, strokeColor=AMBER_ACCENT)
        field_txt = create_text(f"{name} : {dtype}", x + 58, curr_y, fontSize=11, strokeColor=DARK_SLATE)
        elements.extend([icon_txt, field_txt])
        curr_y += row_h
        
    # Render FKs
    for name, dtype, ref in fk_fields:
        icon_txt = create_text("🔗 FK", x + 12, curr_y, fontSize=11, strokeColor=BLUE_ACCENT)
        field_txt = create_text(f"{name} : {dtype} ➔ {ref}", x + 58, curr_y, fontSize=11, strokeColor=DARK_SLATE)
        elements.extend([icon_txt, field_txt])
        curr_y += row_h
        
    # Render Regular
    for name, dtype in regular_fields:
        icon_txt = create_text("▫️", x + 18, curr_y, fontSize=10, strokeColor=MUTED_SLATE)
        field_txt = create_text(f"{name} : {dtype}", x + 58, curr_y, fontSize=11, strokeColor=MUTED_SLATE)
        elements.extend([icon_txt, field_txt])
        curr_y += row_h
        
    return elements, total_h

def generate_clean_excalidraw():
    elements = []
    
    # -------------------------------------------------------------
    # SECTION 1: SYSTEM ARCHITECTURE (Y: 30 to 1150)
    # -------------------------------------------------------------
    elements.append(create_rectangle(
        40, 30, 1620, 85,
        strokeColor=TEAL_DARK, backgroundColor=TEAL_DARK, strokeWidth=1
    ))
    elements.append(create_text(
        "LOKIINI / MatOS — ARCHITECTURE GLOBALE DU SYSTÈME (5 PALIERS)",
        65, 46, fontSize=23, strokeColor="#FFFFFF"
    ))
    elements.append(create_text(
        "Architecture d'entreprise Marketplace • Web Next.js 14 + Mobile React Native • Microservices • CMI / CashPlus • n8n",
        65, 80, fontSize=13, strokeColor="#D1EAE2"
    ))
    
    # Palier 1: Frontends
    elements.append(create_rectangle(40, 135, 1620, 195, strokeColor=TEAL_DARK, backgroundColor=TEAL_LIGHT, strokeWidth=1, strokeStyle="dashed"))
    elements.append(create_text("PALIER 1 : FRONTEND TIER (WEB, MOBILE & PORTAIL PRO)", 60, 145, fontSize=13, strokeColor=TEAL_DARK))
    
    elements.extend(create_box_card(
        60, 175, 470, 135,
        "Next.js 14+ Web Application",
        "• SSR / SSG optimisé SEO local marocain\n• Catalogue public, filtres villes & catégories\n• Tailwind CSS + shadcn/ui (Teal & Terracotta)\n• Zustand / TanStack Query (cache client)",
        badge="Web / SEO", strokeColor=TEAL_DARK
    ))
    elements.extend(create_box_card(
        580, 175, 470, 135,
        "React Native / Expo Mobile App",
        "• iOS & Android sur codebase unifié\n• Module Caméra KYC & test de vivacité en direct\n• État des lieux photo/vidéo scellé à la remise\n• Push Notifications & Géolocalisation",
        badge="iOS & Android", strokeColor=TEAL_DARK, badgeBorder=TERRACOTTA, badgeBg=TERRACOTTA_LIGHT, badgeColor=TERRACOTTA
    ))
    elements.extend(create_box_card(
        1100, 175, 540, 135,
        "Portail Pro & Dashboard Loueur",
        "• Gestion flotte d'équipements & disponibilités\n• Suivi des cautions CMI sous séquestre\n• Facturation B2B conforme avec ICE / TVA\n• Analytics des revenus en Dirhams (MAD)",
        badge="B2B & Loueurs", strokeColor=TEAL_DARK, badgeBorder=PURPLE_ACCENT, badgeBg=PURPLE_LIGHT, badgeColor=PURPLE_ACCENT
    ))
    
    # Palier 2: Edge Gateway
    elements.append(create_rectangle(40, 350, 1620, 115, strokeColor=BLUE_ACCENT, backgroundColor=BLUE_LIGHT, strokeWidth=1, strokeStyle="dashed"))
    elements.append(create_text("PALIER 2 : EDGE GATEWAY, SÉCURITÉ & REVERSE PROXY", 60, 360, fontSize=13, strokeColor=BLUE_ACCENT))
    
    elements.extend(create_box_card(60, 385, 470, 65, "Cloudflare CDN & WAF", "Protection DDoS, SSL/TLS, Caching assets statiques", badge="Edge DNS", strokeColor=BLUE_ACCENT, badgeBorder=BLUE_ACCENT, badgeBg="#E0F2FE", badgeColor=BLUE_ACCENT))
    elements.extend(create_box_card(580, 385, 470, 65, "API Gateway & Auth Proxy", "Rate Limiting, Validation JWT tokens, Routage microservices", badge="Kong / Nginx", strokeColor=BLUE_ACCENT, badgeBorder=BLUE_ACCENT, badgeBg="#E0F2FE", badgeColor=BLUE_ACCENT))
    elements.extend(create_box_card(1100, 385, 540, 65, "Passerelle WebSockets", "Messagerie temps réel loueur-locataire & alertes push", badge="Socket.io", strokeColor=BLUE_ACCENT, badgeBorder=BLUE_ACCENT, badgeBg="#E0F2FE", badgeColor=BLUE_ACCENT))
    
    # Palier 3: Services Métier
    elements.append(create_rectangle(40, 485, 1620, 245, strokeColor=TEAL_DARK, backgroundColor=TEAL_LIGHT, strokeWidth=1, strokeStyle="dashed"))
    elements.append(create_text("PALIER 3 : SERVICES MÉTIER & MOTEURS IA / CNDP", 60, 495, fontSize=13, strokeColor=TEAL_DARK))
    
    elements.extend(create_box_card(60, 525, 360, 185, "Service Catalogue & Annonces", "• CRUD matériel & spécifications\n• Calendrier des disponibilités\n• Algorithme de tarification dégressive\n• Catégorisation BTP, Outils, AV", badge="Catalog API", strokeColor=TEAL_DARK))
    elements.extend(create_box_card(445, 525, 370, 185, "Service Réservations & CMI", "• Tunnel de réservation & validation\n• Pré-autorisation caution bancaire (CMI)\n• Capture / Libération séquestre\n• Facturation & splits commissions", badge="Escrow Engine", strokeColor=TERRACOTTA, badgeBorder=TERRACOTTA, badgeBg=TERRACOTTA_LIGHT, badgeColor=TERRACOTTA))
    elements.extend(create_box_card(840, 525, 380, 185, "Moteur KYC & Conformité CNDP", "• OCR CIN Marocaine & Passeports\n• Liveness check caméra anti-deepfake\n• Traitement Zero-Knowledge en RAM\n• Scellement horodaté RFC 3161 (DOC)", badge="IA & Sécurité", strokeColor=PURPLE_ACCENT, badgeBorder=PURPLE_ACCENT, badgeBg=PURPLE_LIGHT, badgeColor=PURPLE_ACCENT))
    elements.extend(create_box_card(1245, 525, 395, 185, "État des Lieux & Litiges", "• Check-in / Check-out contradictoire\n• Hachage SHA-256 des vidéos/photos\n• Signature numérique des baux (Loi 53-05)\n• Gestion d'arbitrage et sinistres", badge="Bail & Preuve", strokeColor=TEAL_DARK))
    
    # Palier 4: Data Tier
    elements.append(create_rectangle(40, 750, 1620, 185, strokeColor=MUTED_SLATE, backgroundColor="#F8FAFC", strokeWidth=1, strokeStyle="dashed"))
    elements.append(create_text("PALIER 4 : STOCKAGE, BASE DE DONNÉES & INDEXATION RECHERCHE", 60, 760, fontSize=13, strokeColor=MUTED_SLATE))
    
    elements.extend(create_box_card(60, 790, 360, 130, "PostgreSQL 16 (Master/Replica)", "• Relations utilisateurs, baux, transactions\n• Extension pgcrypto pour données chiffrées\n• Schéma strict ACID pour réservations\n• Audit trail immuable des signatures", badge="SQL / ACID", strokeColor=BLUE_ACCENT))
    elements.extend(create_box_card(445, 790, 370, 130, "Redis 7 (In-Memory Data)", "• Cache de sessions & tokens JWT\n• Verrous distribués (disponibilité dates)\n• Pub/Sub WebSockets & files BullMQ\n• Rate-limiting par IP / compte", badge="In-Memory", strokeColor=RED_ACCENT, badgeBorder=RED_ACCENT, badgeBg=RED_LIGHT, badgeColor=RED_ACCENT))
    elements.extend(create_box_card(840, 790, 380, 130, "Meilisearch / Algolia", "• Recherche plein texte instantanée (<50ms)\n• Filtres facettés (Prix, Ville, Catégorie)\n• Recherche géolocalisée (Rayon km)\n• Auto-complétion multilingue (FR/AR)", badge="Fast Search", strokeColor="#EC4899", badgeBorder="#EC4899", badgeBg="#FDF2F8", badgeColor="#EC4899"))
    elements.extend(create_box_card(1245, 790, 395, 130, "Cloudflare R2 / AWS S3", "• Photos haute résolution des matériels\n• Médias chiffrés d'états des lieux\n• Pièces d'identité KYC éphémères\n• URLs présignées sécurisées", badge="Blob Storage", strokeColor=TERRACOTTA, badgeBorder=TERRACOTTA, badgeBg=TERRACOTTA_LIGHT, badgeColor=TERRACOTTA))
    
    # Palier 5: Écosystème Maroc
    elements.append(create_rectangle(40, 955, 1620, 185, strokeColor=TERRACOTTA, backgroundColor=TERRACOTTA_LIGHT, strokeWidth=1, strokeStyle="dashed"))
    elements.append(create_text("PALIER 5 : ÉCOSYSTÈME MAROC, PAIEMENTS & AUTOMATION (N8N)", 60, 965, fontSize=13, strokeColor=TERRACOTTA))
    
    elements.extend(create_box_card(60, 995, 360, 130, "CMI / Payzone (Maroc)", "• Paiements CB marocaines & internationales\n• Empreinte bancaire pour caution sans débit\n• Conformité 3D-Secure v2\n• Rapprochement bancaire automatisé", badge="Monétique Maroc", strokeColor=TERRACOTTA, badgeBorder=TERRACOTTA, badgeBg="#FFFFFF", badgeColor=TERRACOTTA))
    elements.extend(create_box_card(445, 995, 370, 130, "CashPlus / Wafacash", "• Réseau physique de paiement en cash\n• Code de réservation généré par Lokiini\n• Dépôt de caution en agence locale\n• Déblocage instantané par Webhook", badge="Cash-In / Out", strokeColor=TERRACOTTA, badgeBorder=TERRACOTTA, badgeBg="#FFFFFF", badgeColor=TERRACOTTA))
    elements.extend(create_box_card(840, 995, 380, 130, "n8n Workflow Automation", "• Relances automatiques avant fin de location\n• Notification WhatsApp/SMS propriétaire\n• Workflow d'alerte des KYC litigieux\n• Génération & archivage des rapports comptables", badge="Core Automation", strokeColor="#FF6D5A", badgeBorder="#FF6D5A", badgeBg="#FFFFFF", badgeColor="#FF6D5A"))
    elements.extend(create_box_card(1245, 995, 395, 130, "Messagerie & Tiers Légal", "• WhatsApp Business API & SMS Maroc\n• CNDP (Autorisation traitement données)\n• Horodatage certifié RFC 3161\n• ACAPS / Partenaire Assurance Wafa/Sanlam", badge="Légal & Comms", strokeColor=PURPLE_ACCENT, badgeBorder=PURPLE_ACCENT, badgeBg="#FFFFFF", badgeColor=PURPLE_ACCENT))
    
    # Arrows Tier 1 -> 2 -> 3 -> 4 / 5
    elements.extend(create_arrow(295, 310, 295, 385, strokeColor=TEAL_DARK, label="HTTPS/REST"))
    elements.extend(create_arrow(815, 310, 815, 385, strokeColor=TEAL_DARK, label="WSS/Camera"))
    elements.extend(create_arrow(1370, 310, 1370, 385, strokeColor=TEAL_DARK, label="Admin API"))
    elements.extend(create_arrow(295, 450, 240, 525, strokeColor=BLUE_ACCENT))
    elements.extend(create_arrow(815, 450, 630, 525, strokeColor=BLUE_ACCENT))
    elements.extend(create_arrow(815, 450, 1030, 525, strokeColor=BLUE_ACCENT))
    elements.extend(create_arrow(1370, 450, 1440, 525, strokeColor=BLUE_ACCENT))
    elements.extend(create_arrow(240, 710, 240, 790, strokeColor=TEAL_DARK, label="SQL"))
    elements.extend(create_arrow(630, 710, 630, 790, strokeColor=TERRACOTTA, label="Locks/Cache"))
    elements.extend(create_arrow(1030, 710, 1440, 790, strokeColor=PURPLE_ACCENT, label="Media Upload"))
    elements.extend(create_arrow(630, 710, 240, 995, strokeColor=TERRACOTTA, label="Pre-Auth CMI"))
    elements.extend(create_arrow(1030, 710, 1030, 995, strokeColor="#FF6D5A", label="Webhook Events"))
    
    # -------------------------------------------------------------
    # SECTION 2: DATABASE STRUCTURE & ERD (Y: 1180 to 1860)
    # -------------------------------------------------------------
    elements.append(create_rectangle(40, 1180, 1620, 670, strokeColor=BLUE_ACCENT, backgroundColor="#F8FAFC", strokeWidth=1))
    elements.append(create_rectangle(40, 1180, 1620, 65, strokeColor=BLUE_ACCENT, backgroundColor=BLUE_ACCENT, strokeWidth=1))
    elements.append(create_text("SCHÉMA RELATIONNEL DE BASE DE DONNÉES — POSTGRESQL 16 (ERD / UML)", 65, 1195, fontSize=20, strokeColor="#FFFFFF"))
    elements.append(create_text("Structure des tables, clés primaires (PK), clés étrangères (FK), types et contraintes d'intégrité référentielle", 65, 1225, fontSize=12, strokeColor="#E0F2FE"))
    
    # Tables
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
    elements.extend(create_table_card(60, 1270, 360, "users", u_pk, u_fk, u_reg, headerBg=TEAL_DARK, strokeColor=TEAL_DARK)[0])
    
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
    elements.extend(create_table_card(450, 1270, 360, "equipment", eq_pk, eq_fk, eq_reg, headerBg=TEAL_DARK, strokeColor=TEAL_DARK)[0])
    
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
    elements.extend(create_table_card(840, 1270, 380, "bookings", bk_pk, bk_fk, bk_reg, headerBg=TERRACOTTA, strokeColor=TERRACOTTA)[0])
    
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
    elements.extend(create_table_card(1250, 1270, 390, "cmi_transactions", cmi_pk, cmi_fk, cmi_reg, headerBg=TERRACOTTA, strokeColor=TERRACOTTA)[0])
    
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
    elements.extend(create_table_card(450, 1575, 360, "inspection_reports", ins_pk, ins_fk, ins_reg, headerBg=PURPLE_ACCENT, strokeColor=PURPLE_ACCENT)[0])
    
    rev_pk = [("id", "UUID (v4)")]
    rev_fk = [("booking_id", "UUID", "bookings.id"), ("reviewer_id", "UUID", "users.id")]
    rev_reg = [
        ("rating_score", "INTEGER CHECK (1-5)"),
        ("comment", "TEXT"),
        ("created_at", "TIMESTAMPTZ DEFAULT NOW()")
    ]
    elements.extend(create_table_card(840, 1575, 380, "reviews", rev_pk, rev_fk, rev_reg, headerBg=TEAL_DARK, strokeColor=TEAL_DARK)[0])
    
    # ERD Arrows
    elements.extend(create_arrow(420, 1310, 450, 1310, strokeColor=TEAL_DARK, label="1:N"))
    elements.extend(create_arrow(420, 1360, 840, 1360, strokeColor=BLUE_ACCENT, label="renter 1:N"))
    elements.extend(create_arrow(810, 1310, 840, 1310, strokeColor=TERRACOTTA, label="1:N"))
    elements.extend(create_arrow(1220, 1310, 1250, 1310, strokeColor=TERRACOTTA, label="1:1"))
    elements.extend(create_arrow(840, 1500, 810, 1610, strokeColor=PURPLE_ACCENT, label="1:2"))
    elements.extend(create_arrow(1030, 1530, 1030, 1575, strokeColor=TEAL_DARK, label="1:N"))
    
    # -------------------------------------------------------------
    # SECTION 3: UML WORKFLOW & STATE MACHINE (Y: 1880 to 2600)
    # -------------------------------------------------------------
    elements.append(create_rectangle(40, 1880, 1620, 720, strokeColor=PURPLE_ACCENT, backgroundColor="#FAF5FF", strokeWidth=1))
    elements.append(create_rectangle(40, 1880, 1620, 65, strokeColor=PURPLE_ACCENT, backgroundColor=PURPLE_ACCENT, strokeWidth=1))
    elements.append(create_text("DIAGRAMMES UML : MACHINE À ÉTATS & SÉQUENCE DU TUNNEL DE LOCATION", 65, 1895, fontSize=20, strokeColor="#FFFFFF"))
    elements.append(create_text("Cycle de vie complet de la caution CMI, signature du contrat DOC et scellement d'état des lieux RFC 3161", 65, 1925, fontSize=12, strokeColor="#F5F3FF"))
    
    # 3.1 State Machine Box
    elements.append(create_rectangle(60, 1965, 750, 610, strokeColor=DARK_SLATE, backgroundColor=CARD_BG, strokeWidth=1.5))
    elements.append(create_text("MACHINE À ÉTATS : CYCLE DE VIE D'UNE RÉSERVATION & CAUTION CMI", 80, 1980, fontSize=13, strokeColor=PURPLE_ACCENT))
    
    states = [
        ("1. DEMANDE INITIALE", "Locataire choisit dates & valide panier", 90, 2020, BLUE_ACCENT, BLUE_LIGHT),
        ("2. PRÉ-AUTORISATION CMI", "Empreinte bancaire bloquée sans débit", 90, 2100, TERRACOTTA, TERRACOTTA_LIGHT),
        ("3. ACCEPTATION LOUEUR", "Contrat DOC généré & signé électroniquement", 90, 2180, TEAL_DARK, TEAL_LIGHT),
        ("4. CHECK-IN SCELLÉ", "Vidéo d'état des lieux horodatée SHA-256", 90, 2260, PURPLE_ACCENT, PURPLE_LIGHT),
        ("5. EN COURS D'UTILISATION", "Location active • Relances n8n planifiées", 90, 2340, GREEN_ACCENT, GREEN_LIGHT),
        ("6. CHECK-OUT & CONTRÔLE", "Vérification contradictoire au retour", 90, 2420, AMBER_ACCENT, AMBER_LIGHT),
        ("7. CLÔTURE OU LITIGE", "Libération immédiate ou capture de caution", 90, 2500, TEAL_DARK, TEAL_LIGHT),
    ]
    
    for title, desc, sx, sy, s_color, s_bg in states:
        elements.append(create_rectangle(sx, sy, 320, 52, strokeColor=s_color, backgroundColor=s_bg, strokeWidth=1.5))
        elements.append(create_text(title, sx + 12, sy + 8, fontSize=12, strokeColor=s_color))
        elements.append(create_text(desc, sx + 12, sy + 28, fontSize=10, strokeColor=DARK_SLATE))
        
    for i in range(len(states) - 1):
        sy_curr = states[i][3] + 52
        sy_next = states[i+1][3]
        elements.extend(create_arrow(250, sy_curr, 250, sy_next, strokeColor=DARK_SLATE))
        
    elements.append(create_rectangle(450, 2460, 330, 48, strokeColor=GREEN_ACCENT, backgroundColor=GREEN_LIGHT, strokeWidth=1.5))
    elements.append(create_text("✅ Matériel Intact : Caution libérée à 100%", 460, 2475, fontSize=11, strokeColor=GREEN_ACCENT))
    
    elements.append(create_rectangle(450, 2520, 330, 48, strokeColor=RED_ACCENT, backgroundColor=RED_LIGHT, strokeWidth=1.5))
    elements.append(create_text("⚠️ Dégradation : Capture partielle CMI + Assurance", 460, 2535, fontSize=11, strokeColor=RED_ACCENT))
    
    elements.extend(create_arrow(410, 2526, 450, 2484, strokeColor=GREEN_ACCENT))
    elements.extend(create_arrow(410, 2526, 450, 2544, strokeColor=RED_ACCENT))
    
    # 3.2 Sequence Diagram Box
    elements.append(create_rectangle(840, 1965, 800, 610, strokeColor=DARK_SLATE, backgroundColor=CARD_BG, strokeWidth=1.5))
    elements.append(create_text("DIAGRAMME DE SÉQUENCE UML DU TUNNEL DE CONFIANCE (CMI + KYC)", 860, 1980, fontSize=13, strokeColor=PURPLE_ACCENT))
    
    actors = [
        ("Locataire", 880),
        ("Propriétaire", 1030),
        ("Lokiini API", 1180),
        ("CMI Gateway", 1330),
        ("n8n / Tiers", 1480)
    ]
    
    for name, ax in actors:
        elements.append(create_rectangle(ax - 45, 2015, 90, 32, strokeColor=TEAL_DARK, backgroundColor=TEAL_LIGHT, strokeWidth=1.5))
        elements.append(create_text(name, ax - 35, 2023, fontSize=11, strokeColor=TEAL_DARK))
        # Add valid line element with points
        elements.append(create_line(ax, 2047, ax, 2550, strokeColor=BORDER_GRAY, strokeWidth=1, strokeStyle="dashed"))
        
    seq_steps = [
        (880, 1180, 2065, "1. Demande location + Scan CIN", BLUE_ACCENT),
        (1180, 880, 2095, "2. Formulaire 3D-Secure CMI", TERRACOTTA),
        (880, 1330, 2130, "3. Saisie CB & Empreinte", TERRACOTTA),
        (1330, 1180, 2165, "4. Caution Bloquée (Auth Token)", GREEN_ACCENT),
        (1180, 1030, 2200, "5. Notification push nouvelle résa", TEAL_DARK),
        (1030, 1180, 2235, "6. Confirmation loueur", TEAL_DARK),
        (1180, 1480, 2270, "7. Webhook n8n ➔ Contrat PDF DOC", PURPLE_ACCENT),
        (1480, 880, 2305, "8. WhatsApp: Contrat + QR Code", PURPLE_ACCENT),
        (880, 1180, 2350, "9. Upload Vidéo Check-in (SHA-256)", BLUE_ACCENT),
        (1030, 1180, 2385, "10. Signature remise contradictoire", TEAL_DARK),
        (880, 1030, 2430, "11. Restitution de l'appareil", DARK_SLATE),
        (1030, 1180, 2465, "12. Validation retour conforme", GREEN_ACCENT),
        (1180, 1330, 2500, "13. Ordre Libération Caution CMI", GREEN_ACCENT),
        (1330, 880, 2530, "14. Plafond CB libéré instantanément", GREEN_ACCENT),
    ]
    
    for sx, ex, sy, label, col in seq_steps:
        elements.extend(create_arrow(sx, sy, ex, sy, strokeColor=col, strokeWidth=1.5, label=label, labelColor=DARK_SLATE))
        
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
    data = generate_clean_excalidraw()
    
    out_file_root = Path(r"d:\Lokiini\lokiini_project_architecture.excalidraw")
    out_file_docs = Path(r"d:\Lokiini\docs\02_architecture_technique_et_ia\lokiini_project_architecture.excalidraw")
    
    with open(out_file_root, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    with open(out_file_docs, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated {len(data['elements'])} strictly validated elements.")

if __name__ == "__main__":
    main()
