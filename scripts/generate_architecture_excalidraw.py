#!/usr/bin/env python3
"""
Generator script for Lokiini Complete Architecture in Excalidraw format (.excalidraw).
Follows the excalidraw-expert skill guidelines:
- Professional styling (roughness: 0, fontFamily: 2, strict Lokiini palette)
- Programmatic grid & swimlane layout with exact bounding
- Bound text containers and relative-point arrows
"""

import json
import random
import time
from pathlib import Path

def create_element(elem_type, x, y, width, height, **kwargs):
    elem_id = kwargs.get("id", f"{elem_type}_{random.randint(100000, 999999)}")
    now = int(time.time() * 1000)
    base = {
        "id": elem_id,
        "type": elem_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", "#1E293B"),
        "backgroundColor": kwargs.get("backgroundColor", "transparent"),
        "fillStyle": kwargs.get("fillStyle", "solid"),
        "strokeWidth": kwargs.get("strokeWidth", 1),
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
    font_size = kwargs.get("fontSize", 16)
    lines = text.split("\n")
    max_len = max(len(l) for l in lines) if lines else 1
    # Estimate width & height
    char_w = font_size * 0.58
    line_h = font_size * 1.35
    w = kwargs.get("width", max(max_len * char_w, 40))
    h = kwargs.get("height", len(lines) * line_h)
    
    elem_id = kwargs.get("id", f"text_{random.randint(100000, 999999)}")
    now = int(time.time() * 1000)
    return {
        "id": elem_id,
        "type": "text",
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", "#1E293B"),
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

def create_box_with_text(x, y, width, height, title, subtitle=None, badge=None, **kwargs):
    elements = []
    box_id = kwargs.get("id", f"rect_{random.randint(100000, 999999)}")
    title_id = f"txt_title_{random.randint(100000, 999999)}"
    
    stroke_color = kwargs.get("strokeColor", "#0F6E56")
    bg_color = kwargs.get("backgroundColor", "#FFFFFF")
    
    box = create_element(
        "rectangle", x, y, width, height,
        id=box_id,
        strokeColor=stroke_color,
        backgroundColor=bg_color,
        fillStyle="solid",
        strokeWidth=kwargs.get("strokeWidth", 1.5),
        roundness={"type": 3},
        boundElements=[{"id": title_id, "type": "text"}]
    )
    elements.append(box)
    
    # Title
    t_y = y + 14
    title_elem = create_text(
        title, x + 16, t_y,
        id=title_id,
        fontSize=kwargs.get("titleFontSize", 15),
        strokeColor=kwargs.get("titleColor", "#0F6E56"),
        width=width - 32
    )
    elements.append(title_elem)
    
    # Subtitle / Details
    if subtitle:
        sub_y = t_y + (title_elem["height"]) + 6
        sub_elem = create_text(
            subtitle, x + 16, sub_y,
            fontSize=kwargs.get("subFontSize", 12),
            strokeColor=kwargs.get("subColor", "#475569"),
            width=width - 32
        )
        elements.append(sub_elem)
        
    # Badge (e.g. "KYC", "CMI", "Loi 09-08")
    if badge:
        badge_w = len(badge) * 7.5 + 16
        badge_h = 22
        badge_x = x + width - badge_w - 12
        badge_y = y + 10
        badge_box = create_element(
            "rectangle", badge_x, badge_y, badge_w, badge_h,
            strokeColor=kwargs.get("badgeBorder", "#D85A30"),
            backgroundColor=kwargs.get("badgeBg", "#FBEEE9"),
            strokeWidth=1,
            roundness={"type": 3}
        )
        badge_txt = create_text(
            badge, badge_x + 8, badge_y + 4,
            fontSize=10,
            strokeColor=kwargs.get("badgeColor", "#D85A30"),
            width=badge_w - 16
        )
        elements.append(badge_box)
        elements.append(badge_txt)
        
    return box_id, elements

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
        "width": abs(dx),
        "height": abs(dy),
        "angle": 0,
        "strokeColor": kwargs.get("strokeColor", "#64748B"),
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
        "startArrowhead": None,
        "endArrowhead": "arrow"
    }
    
    elements = [arrow]
    if "label" in kwargs and kwargs["label"]:
        label_text = kwargs["label"]
        mid_x = start_x + dx * 0.5 - 40
        mid_y = start_y + dy * 0.5 - 12
        lbl = create_text(
            label_text, mid_x, mid_y,
            fontSize=11,
            strokeColor=kwargs.get("labelColor", "#475569")
        )
        elements.append(lbl)
        
    return elements

def build_architecture():
    elements = []
    
    # Palette constants
    TEAL_DARK = "#0F6E56"
    TEAL_LIGHT = "#E8F5F1"
    TERRACOTTA = "#D85A30"
    TERRACOTTA_LIGHT = "#FBEEE9"
    SAND_BG = "#FDFBF7"
    DARK_SLATE = "#1E293B"
    CARD_BG = "#FFFFFF"
    BORDER_GRAY = "#CBD5E1"
    BLUE_ACCENT = "#0284C7"
    BLUE_LIGHT = "#F0F9FF"
    PURPLE_ACCENT = "#7C3AED"
    PURPLE_LIGHT = "#F5F3FF"
    
    # Header Banner / Title
    elements.append(create_element(
        "rectangle", 40, 30, 1600, 90,
        strokeColor=TEAL_DARK,
        backgroundColor=TEAL_DARK,
        strokeWidth=1,
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "LOKIINI / MatOS — ARCHITECTURE GLOBALE DU SYSTÈME & DES FLUX",
        65, 48,
        fontSize=24,
        strokeColor="#FFFFFF"
    ))
    elements.append(create_text(
        "Plateforme de location de matériel (Web + Mobile) • Paiement CMI & Cautions • KYC Biométrique CNDP • Automatisation n8n",
        65, 84,
        fontSize=13,
        strokeColor="#D1EAE2"
    ))
    
    # TIER 1: CLIENTS & FRONTENDS (Y: 150 to 340)
    elements.append(create_element(
        "rectangle", 40, 145, 1600, 200,
        strokeColor=TEAL_DARK,
        backgroundColor=TEAL_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "1. FRONTEND TIER (APPLICATIONS UTILISATEURS & PROS)",
        60, 155,
        fontSize=14,
        strokeColor=TEAL_DARK
    ))
    
    # Web App Card
    w_box, w_elems = create_box_with_text(
        70, 185, 460, 140,
        "Next.js 14+ Web Application",
        "• SSR / SSG optimisé SEO local marocain\n• Catalogue public, filtres villes & catégories\n• Tailwind CSS + shadcn/ui (Teal & Terracotta)\n• Zustand / TanStack Query (cache client)",
        badge="Web / SEO",
        strokeColor=TEAL_DARK,
        backgroundColor=CARD_BG,
        badgeBorder=TEAL_DARK,
        badgeBg=TEAL_LIGHT,
        badgeColor=TEAL_DARK
    )
    elements.extend(w_elems)
    
    # Mobile App Card
    m_box, m_elems = create_box_with_text(
        570, 185, 460, 140,
        "React Native / Expo Mobile App",
        "• iOS & Android sur codebase unifié\n• Module Caméra KYC & test de vivacité en direct\n• État des lieux photo/vidéo scellé à la remise\n• Push Notifications & Géolocalisation",
        badge="iOS & Android",
        strokeColor=TEAL_DARK,
        backgroundColor=CARD_BG,
        badgeBorder=TERRACOTTA,
        badgeBg=TERRACOTTA_LIGHT,
        badgeColor=TERRACOTTA
    )
    elements.extend(m_elems)
    
    # Pro / Loueur Dashboard Card
    d_box, d_elems = create_box_with_text(
        1070, 185, 460, 140,
        "Portail Pro & Dashboard Loueur",
        "• Gestion flotte d'équipements & disponibilités\n• Suivi des cautions CMI sous séquestre\n• Facturation B2B conforme avec ICE / TVA\n• Analytics des revenus en Dirhams (MAD)",
        badge="B2B & Loueurs",
        strokeColor=TEAL_DARK,
        backgroundColor=CARD_BG,
        badgeBorder=PURPLE_ACCENT,
        badgeBg=PURPLE_LIGHT,
        badgeColor=PURPLE_ACCENT
    )
    elements.extend(d_elems)
    
    # TIER 2: EDGE, CDN & SECURITY GATEWAY (Y: 375 to 490)
    elements.append(create_element(
        "rectangle", 40, 370, 1600, 120,
        strokeColor="#0284C7",
        backgroundColor=BLUE_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "2. EDGE GATEWAY, SÉCURITÉ & REVERSE PROXY",
        60, 380,
        fontSize=14,
        strokeColor="#0284C7"
    ))
    
    gw1, gw1_e = create_box_with_text(
        70, 405, 460, 70,
        "Cloudflare CDN & WAF",
        "Protection DDoS, SSL/TLS, Caching assets statiques",
        badge="Edge DNS",
        strokeColor="#0284C7",
        badgeBorder="#0284C7", badgeBg="#E0F2FE", badgeColor="#0284C7"
    )
    elements.extend(gw1_e)
    
    gw2, gw2_e = create_box_with_text(
        570, 405, 460, 70,
        "API Gateway & Auth Proxy",
        "Rate Limiting, Validation JWT tokens, Routage microservices",
        badge="Kong / Nginx",
        strokeColor="#0284C7",
        badgeBorder="#0284C7", badgeBg="#E0F2FE", badgeColor="#0284C7"
    )
    elements.extend(gw2_e)
    
    gw3, gw3_e = create_box_with_text(
        1070, 405, 460, 70,
        "Passerelle WebSockets",
        "Messagerie instantanée loueur-locataire, notifications temps réel",
        badge="Socket.io",
        strokeColor="#0284C7",
        badgeBorder="#0284C7", badgeBg="#E0F2FE", badgeColor="#0284C7"
    )
    elements.extend(gw3_e)
    
    # TIER 3: BACKEND SERVICES & BUSINESS LOGIC (Y: 520 to 760)
    elements.append(create_element(
        "rectangle", 40, 515, 1600, 255,
        strokeColor=TEAL_DARK,
        backgroundColor=TEAL_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "3. BACKEND SERVICES & MOTEURS MÉTIER (API REST / NestJS ou FastAPI)",
        60, 525,
        fontSize=14,
        strokeColor=TEAL_DARK
    ))
    
    # Service 1: Rental & Catalog
    s1, s1_e = create_box_with_text(
        70, 555, 350, 195,
        "Service Catalogue & Annonces",
        "• CRUD matériel & spécifications\n• Calendrier des disponibilités\n• Algorithme de tarification dégressive\n• Catégorisation BTP, Outils, AV",
        badge="Catalog API",
        strokeColor=TEAL_DARK
    )
    elements.extend(s1_e)
    
    # Service 2: Booking & Payments (CMI)
    s2, s2_e = create_box_with_text(
        445, 555, 360, 195,
        "Service Réservations & CMI",
        "• Tunnel de réservation & validation\n• Pré-autorisation caution bancaire (CMI)\n• Capture / Libération séquestre\n• Facturation & splits commissions",
        badge="Escrow Engine",
        strokeColor=TERRACOTTA,
        badgeBorder=TERRACOTTA,
        badgeBg=TERRACOTTA_LIGHT,
        badgeColor=TERRACOTTA
    )
    elements.extend(s2_e)
    
    # Service 3: Biometric KYC & CNDP
    s3, s3_e = create_box_with_text(
        830, 555, 365, 195,
        "Moteur KYC & Conformité CNDP",
        "• OCR CIN Marocaine & Passeports\n• Liveness check caméra anti-deepfake\n• Traitement Zero-Knowledge en RAM\n• Scellement horodaté RFC 3161 (DOC)",
        badge="IA & Sécurité",
        strokeColor=PURPLE_ACCENT,
        badgeBorder=PURPLE_ACCENT,
        badgeBg=PURPLE_LIGHT,
        badgeColor=PURPLE_ACCENT
    )
    elements.extend(s3_e)
    
    # Service 4: Inspection & Check-in
    s4, s4_e = create_box_with_text(
        1220, 555, 350, 195,
        "État des Lieux & Litiges",
        "• Check-in / Check-out contradictoire\n• Hachage SHA-256 des vidéos/photos\n• Signature numérique des baux (Loi 53-05)\n• Gestion d'arbitrage et sinistres",
        badge="Bail & Preuve",
        strokeColor=TEAL_DARK
    )
    elements.extend(s4_e)
    
    # TIER 4: DATA, STORAGE & SEARCH (Y: 795 to 975)
    elements.append(create_element(
        "rectangle", 40, 790, 1600, 190,
        strokeColor="#475569",
        backgroundColor="#F8FAFC",
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "4. STOCKAGE, BASE DE DONNÉES & INDEXATION RECHERCHE",
        60, 800,
        fontSize=14,
        strokeColor="#475569"
    ))
    
    # PostgreSQL
    db1, db1_e = create_box_with_text(
        70, 830, 350, 135,
        "PostgreSQL 16 (Master + Replica)",
        "• Relations utilisateurs, baux, transactions\n• Extension pgcrypto pour données chiffrées\n• Schéma strict ACID pour réservations\n• Audit trail immuable des signatures",
        badge="SQL / ACID",
        strokeColor="#0284C7"
    )
    elements.extend(db1_e)
    
    # Redis
    db2, db2_e = create_box_with_text(
        445, 830, 360, 135,
        "Redis 7 (In-Memory Data)",
        "• Cache de sessions & tokens JWT\n• Verrous distribués (disponibilité dates)\n• Pub/Sub WebSockets & files BullMQ\n• Rate-limiting par IP / compte",
        badge="In-Memory",
        strokeColor="#EF4444",
        badgeBorder="#EF4444", badgeBg="#FEE2E2", badgeColor="#EF4444"
    )
    elements.extend(db2_e)
    
    # Meilisearch
    db3, db3_e = create_box_with_text(
        830, 830, 365, 135,
        "Meilisearch / Algolia",
        "• Recherche plein texte instantanée (<50ms)\n• Filtres facettés (Prix, Ville, Catégorie)\n• Recherche géolocalisée (Rayon km)\n• Auto-complétion multilingue (FR/AR)",
        badge="Fast Search",
        strokeColor="#EC4899",
        badgeBorder="#EC4899", badgeBg="#FDF2F8", badgeColor="#EC4899"
    )
    elements.extend(db3_e)
    
    # S3 / Cloudflare R2
    db4, db4_e = create_box_with_text(
        1220, 830, 350, 135,
        "Cloudflare R2 / AWS S3",
        "• Photos haute résolution des matériels\n• Médias chiffrés d'états des lieux\n• Pièces d'identité KYC éphémères\n• URLs présignées sécurisées",
        badge="Blob Storage",
        strokeColor="#D85A30",
        badgeBorder=TERRACOTTA, badgeBg=TERRACOTTA_LIGHT, badgeColor=TERRACOTTA
    )
    elements.extend(db4_e)
    
    # TIER 5: EXTERNAL ECOSYSTEM & AUTOMATION (Y: 1005 to 1185)
    elements.append(create_element(
        "rectangle", 40, 1000, 1600, 195,
        strokeColor=TERRACOTTA,
        backgroundColor=TERRACOTTA_LIGHT,
        strokeWidth=1,
        strokeStyle="dashed",
        roundness={"type": 3}
    ))
    elements.append(create_text(
        "5. ÉCOSYSTÈME MAROC, PAIEMENTS & AUTOMATION (N8N)",
        60, 1010,
        fontSize=14,
        strokeColor=TERRACOTTA
    ))
    
    # CMI / Payzone
    ex1, ex1_e = create_box_with_text(
        70, 1040, 350, 140,
        "CMI / Payzone (Maroc)",
        "• Paiements CB marocaines & internationales\n• Empreinte bancaire pour caution sans débit\n• Conformité 3D-Secure v2\n• Rapprochement bancaire automatisé",
        badge="Monétique Maroc",
        strokeColor=TERRACOTTA,
        badgeBorder=TERRACOTTA, badgeBg="#FFFFFF", badgeColor=TERRACOTTA
    )
    elements.extend(ex1_e)
    
    # CashPlus / Wafacash
    ex2, ex2_e = create_box_with_text(
        445, 1040, 360, 140,
        "CashPlus / Wafacash",
        "• Réseau physique de paiement en cash\n• Code de réservation généré par Lokiini\n• Dépôt de caution en agence locale\n• Déblocage instantané par Webhook",
        badge="Cash-In / Out",
        strokeColor=TERRACOTTA,
        badgeBorder=TERRACOTTA, badgeBg="#FFFFFF", badgeColor=TERRACOTTA
    )
    elements.extend(ex2_e)
    
    # n8n Automation Engine
    ex3, ex3_e = create_box_with_text(
        830, 1040, 365, 140,
        "n8n Workflow Automation",
        "• Relances automatiques avant fin de location\n• Notification WhatsApp/SMS propriétaire\n• Workflow d'alerte des KYC litigieux\n• Génération & archivage des rapports comptables",
        badge="Core Automation",
        strokeColor="#FF6D5A",
        badgeBorder="#FF6D5A", badgeBg="#FFFFFF", badgeColor="#FF6D5A"
    )
    elements.extend(ex3_e)
    
    # Notifications & Legal Authority
    ex4, ex4_e = create_box_with_text(
        1220, 1040, 350, 140,
        "Messagerie & Tiers Légal",
        "• WhatsApp Business API & SMS Maroc\n• CNDP (Autorisation traitement données)\n• Horodatage certifié RFC 3161\n• ACAPS / Partenaire Assurance Wafa/Sanlam",
        badge="Légal & Comms",
        strokeColor=PURPLE_ACCENT,
        badgeBorder=PURPLE_ACCENT, badgeBg="#FFFFFF", badgeColor=PURPLE_ACCENT
    )
    elements.extend(ex4_e)
    
    # CONNECTING ARROWS & FLOWS
    # 1. Frontends to Gateway
    elements.extend(create_arrow(300, 325, 300, 405, strokeColor=TEAL_DARK, label="HTTPS / REST"))
    elements.extend(create_arrow(800, 325, 800, 405, strokeColor=TEAL_DARK, label="WSS / Biometrics"))
    elements.extend(create_arrow(1300, 325, 1300, 405, strokeColor=TEAL_DARK, label="B2B Admin"))
    
    # 2. Gateway to Backend Services
    elements.extend(create_arrow(300, 475, 245, 555, strokeColor="#0284C7"))
    elements.extend(create_arrow(800, 475, 625, 555, strokeColor="#0284C7"))
    elements.extend(create_arrow(800, 475, 1012, 555, strokeColor="#0284C7"))
    elements.extend(create_arrow(1300, 475, 1395, 555, strokeColor="#0284C7"))
    
    # 3. Backend to Data Layer
    elements.extend(create_arrow(245, 750, 245, 830, strokeColor=TEAL_DARK, label="SQL"))
    elements.extend(create_arrow(625, 750, 625, 830, strokeColor=TERRACOTTA, label="Locks/Cache"))
    elements.extend(create_arrow(245, 750, 950, 830, strokeColor="#EC4899", label="Sync Index"))
    elements.extend(create_arrow(1012, 750, 1395, 830, strokeColor=PURPLE_ACCENT, label="Upload KYC"))
    elements.extend(create_arrow(1395, 750, 1395, 830, strokeColor=TEAL_DARK, label="Check-in Media"))
    
    # 4. Backend to Moroccan Ecosystem & n8n
    elements.extend(create_arrow(625, 750, 245, 1040, strokeColor=TERRACOTTA, label="Pre-Auth CMI"))
    elements.extend(create_arrow(625, 750, 625, 1040, strokeColor=TERRACOTTA, label="Cash Code"))
    elements.extend(create_arrow(1012, 750, 1012, 1040, strokeColor="#FF6D5A", label="Webhook Events"))
    elements.extend(create_arrow(1395, 750, 1395, 1040, strokeColor=PURPLE_ACCENT, label="Signature DOC"))
    
    # Assemble Excalidraw root
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
    data = build_architecture()
    
    out_dir_1 = Path(r"d:\Lokiini\docs\02_architecture_technique_et_ia")
    out_dir_1.mkdir(parents=True, exist_ok=True)
    out_file_1 = out_dir_1 / "lokiini_project_architecture.excalidraw"
    
    out_file_root = Path(r"d:\Lokiini\lokiini_project_architecture.excalidraw")
    
    with open(out_file_1, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    with open(out_file_root, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Generated {len(data['elements'])} elements.")
    print(f"Saved to {out_file_1}")
    print(f"Saved to {out_file_root}")

if __name__ == "__main__":
    main()
