#!/usr/bin/env python3
"""
Deep & Detailed n8n Architecture Generator for Lokiini / MatOS.
Produces an ultra-detailed, highly readable, hand-drawn Excalidraw file:
- Workflow A: Conseiller Location IA WhatsApp (Full agent stack, tools, 4 intent branches)
- Workflow B: Pipeline KYC Biométrique CNDP (OCR CIN, Liveness anti-deepfake, Zero-Knowledge)
- Workflow C: Contrat de Bail DOC Automatisé & Scellement RFC 3161 (Loi 53-05)
- Workflow D: Relance Restitution & Rappels Check-out (J-1 & H-2 Follow-up)
- Workflow E: Rapprochement Bancaire Journalier CMI & CashPlus (Cron 23:59)
"""

import json
import random
import time
from pathlib import Path

# Hand-drawn Color Palette
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
        "fontFamily": 1, # Virgil font
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

def generate_detailed_n8n_architecture():
    elements = []
    
    # -------------------------------------------------------------
    # 0. MAIN HEADER BANNER
    # -------------------------------------------------------------
    elements.append(create_rectangle(
        40, 30, 1680, 70,
        strokeColor=C_HEADER_BORDER,
        backgroundColor=C_HEADER_BG,
        strokeWidth=2
    ))
    elements.append(create_text(
        "LOKIINI — Architecture Complète des Workflows n8n (Conseiller IA WhatsApp, KYC CNDP, Contrat DOC, Cautions & Rapprochement)",
        60, 44,
        fontSize=18,
        strokeColor=C_HEADER_BORDER,
        textAlign="left"
    ))
    elements.append(create_text(
        "Orchestrateur d'automatisation événementielle & asynchrone • Intégrations Meta Cloud API, CMI, CashPlus & PostgreSQL 16",
        60, 72,
        fontSize=12,
        strokeColor=DARK_TEXT,
        textAlign="left"
    ))
    
    # -------------------------------------------------------------
    # WORKFLOW E: Rapprochement Bancaire Journalier CMI & CashPlus
    # -------------------------------------------------------------
    elements.append(create_rectangle(40, 120, 1680, 115, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("E. Ingestion & Rapprochement Bancaire Journalier CMI, Payzone & CashPlus (Cron 23:59)", 60, 130, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, 158, 150, 52, "Cron Trigger\n(Tous les soirs 23:59)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(240, 158, 180, 52, "HTTP: Fetch CMI Daily Batch\n& Webhook CashPlus logs", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(450, 158, 190, 52, "PostgreSQL: Query Bookings\n& Pre-auth Tokens du jour", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(670, 158, 180, 52, "Code: Reconcile Amounts\n& Calc Platform Splits (15-5%)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(880, 158, 170, 52, "Generate Financial Summary\n(PDF / Excel Consolidé)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1080, 158, 190, 52, "Email Node: Send Daily Report\n➔ Direction Financière (MAD)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1300, 158, 190, 52, "Slack / Discord Admin Alert:\nStatut Rapprochement OK (0 écart)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1520, 158, 180, 52, "Archive Audit Log\n(Bucket R2 Chiffré)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    
    elements.extend(create_arrow(210, 184, 240, 184))
    elements.extend(create_arrow(420, 184, 450, 184))
    elements.extend(create_arrow(640, 184, 670, 184))
    elements.extend(create_arrow(850, 184, 880, 184))
    elements.extend(create_arrow(1050, 184, 1080, 184))
    elements.extend(create_arrow(1270, 184, 1300, 184))
    elements.extend(create_arrow(1490, 184, 1520, 184))
    
    # -------------------------------------------------------------
    # WORKFLOW D: Relances Restitution & Rappels Check-out (J-1 & H-2)
    # -------------------------------------------------------------
    elements.append(create_rectangle(40, 250, 1680, 115, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("D. Relance Restitution, Prolongation Payante & Rappel d'État des Lieux (Cron Horaire)", 60, 260, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, 288, 150, 52, "Hourly Cron Schedule\n(Toutes les heures 00:00)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(240, 288, 180, 52, "PostgreSQL: Get Bookings\nExpiring at J-1 & H-2", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(450, 288, 180, 52, "Item Lists: Split In Batches\n& Filter Already Reminded", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(660, 288, 190, 52, "Generate Dynamic Return Link\n& Secure Upload Token", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(880, 288, 220, 52, "WhatsApp Cloud API: Send Return\nChecklist + Video Check-out Button", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1130, 288, 200, 52, "Option: Click 'Prolonger 24h'\n➔ Re-calc Total MAD & Pre-auth", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(1360, 288, 180, 52, "PostgreSQL: Update Status\n➔ reminder_sent = true", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1570, 288, 130, 52, "Notify Owner\n(Push App)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    elements.extend(create_arrow(210, 314, 240, 314))
    elements.extend(create_arrow(420, 314, 450, 314))
    elements.extend(create_arrow(630, 314, 660, 314))
    elements.extend(create_arrow(850, 314, 880, 314))
    elements.extend(create_arrow(1100, 314, 1130, 314))
    elements.extend(create_arrow(1330, 314, 1360, 314))
    elements.extend(create_arrow(1540, 314, 1570, 314))
    
    # -------------------------------------------------------------
    # WORKFLOW C: Contrat de Bail DOC Automatisé & Scellement RFC 3161
    # -------------------------------------------------------------
    elements.append(create_rectangle(40, 380, 1680, 115, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("C. Génération Contrat de Bail Numérique DOC & Scellement Horodaté RFC 3161 (Loi 53-05)", 60, 390, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, 418, 160, 52, "Webhook: booking.confirmed\n(Propriétaire a validé)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(250, 418, 190, 52, "Fetch Rental Details, CIN,\nMatériel & CMI Pre-auth Ref", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(470, 418, 190, 52, "HTML-to-PDF Engine:\nGenerate Contrat DOC Art. 627", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(690, 418, 180, 52, "Crypto Node: Compute\nSHA-256 Hash du Contrat PDF", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(900, 418, 180, 52, "HTTP: RFC 3161 Timestamp\n(Horodatage Légal Certifié)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(1110, 418, 180, 52, "S3/R2 Node: Upload Contract\n& Generate Signed URLs", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1320, 418, 200, 52, "WhatsApp: Send Contract PDF\n+ QR Code Check-in au Locataire", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1550, 418, 150, 52, "WhatsApp: Send Copy\n➔ Propriétaire Pro", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    elements.extend(create_arrow(220, 444, 250, 444))
    elements.extend(create_arrow(440, 444, 470, 444))
    elements.extend(create_arrow(660, 444, 690, 444))
    elements.extend(create_arrow(870, 444, 900, 444))
    elements.extend(create_arrow(1080, 444, 1110, 444))
    elements.extend(create_arrow(1290, 444, 1320, 444))
    elements.extend(create_arrow(1520, 444, 1550, 444))
    
    # -------------------------------------------------------------
    # WORKFLOW B: Pipeline KYC Biométrique & Alerte Fraude CNDP
    # -------------------------------------------------------------
    elements.append(create_rectangle(40, 510, 1680, 125, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("B. Pipeline KYC Biométrique CNDP (OCR CIN, Liveness anti-deepfake & Escalade Fraude)", 60, 520, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, 550, 160, 54, "Webhook: kyc.submitted\n(Upload CIN + Vidéo Selfie)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(250, 550, 180, 54, "HTTP: Call OCR Engine\n(Extract CIN, Nom, Dates)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(460, 550, 180, 54, "HTTP: Liveness & Vector Match\n(Deepfake & Texture Check)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    # Decision Diamond
    elements.append(create_diamond(670, 545, 90, 60))
    elements.append(create_text("Score\n>= 85%?", 672, 563, fontSize=10, strokeColor=C_DECISION_TEXT))
    
    # Yes Branch (Validation)
    elements.extend(create_pill_node(800, 525, 200, 42, "PostgreSQL: is_kyc_verified=true\n& Log CNDP Zero-Knowledge Audit", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1030, 525, 220, 42, "WhatsApp: 'Identité Validée CNDP'\n➔ Déblocage Réservations Immédiat", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1280, 525, 190, 42, "Purge Raw Selfie Video in RAM\n(Conformité Loi 09-08)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    
    # No Branch (Review / Fraud Alert)
    elements.extend(create_pill_node(800, 580, 200, 42, "Slack / Telegram Alert:\n'KYC Suspect / Score Bas'", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_pill_node(1030, 580, 220, 42, "WhatsApp: 'Vérification requise'\n➔ Conseil éclairage / repasser selfie", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_pill_node(1280, 580, 190, 42, "Lock Booking Action\n(En attente examen manuel)", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    
    elements.extend(create_arrow(220, 577, 250, 577))
    elements.extend(create_arrow(430, 577, 460, 577))
    elements.extend(create_arrow(640, 577, 670, 577))
    elements.extend(create_arrow(760, 560, 800, 546, label="Yes", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(760, 590, 800, 601, label="No", strokeColor=C_ALERT_BORDER))
    elements.extend(create_arrow(1000, 546, 1030, 546))
    elements.extend(create_arrow(1250, 546, 1280, 546))
    elements.extend(create_arrow(1000, 601, 1030, 601))
    elements.extend(create_arrow(1250, 601, 1280, 601))
    
    # -------------------------------------------------------------
    # WORKFLOW A: Conseiller Location IA WhatsApp & Intent Router
    # -------------------------------------------------------------
    elements.append(create_rectangle(40, 650, 1680, 440, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("A. Conseiller Location IA WhatsApp (LOKIINI Conversational Agent, Tools Stack & Intent Router)", 60, 660, fontSize=14, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Inbound Webhook Verify & Message
    elements.extend(create_pill_node(60, 695, 160, 42, "WhatsApp Webhook (GET)\nHub Verify Challenge", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(250, 695, 160, 42, "Validate Hub Token\n➔ Return challenge", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(440, 695, 130, 42, "Respond 200 OK\n(Meta Handshake)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_arrow(220, 716, 250, 716))
    elements.extend(create_arrow(410, 716, 440, 716))
    
    elements.extend(create_pill_node(60, 755, 160, 48, "WhatsApp Webhook (POST)\nIncoming Customer Msg", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(250, 755, 170, 48, "Extract Message Payload\n(Text / Voice / Location / Phone)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_arrow(220, 779, 250, 779))
    
    # AI Tools Stack
    tool_items = [
        ("Claude 3.5 Sonnet / Gemini Flash LLM (Bilingue FR / Darija)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Redis Window Buffer (10 Derniers échanges contextuels)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Meilisearch Catalog (Filtre Villes, BTP, Caméras, Outils)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Calculator (Prix Journalier MAD + Caution CMI Séquestre)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Check Slot Availability (Redis Lock / Postgres Bookings)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Generate CMI 3D-Secure 1-Click Payment Link", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
    ]
    t_y = 825
    for label, bg, border, txt in tool_items:
        elements.extend(create_pill_node(100, t_y, 250, 32, label, bg, border, txt, font_size=9))
        elements.extend(create_arrow(350, t_y + 16, 460, 875, strokeColor=border, strokeWidth=1, strokeStyle="dashed"))
        t_y += 37
        
    # AI Agent Core
    elements.extend(create_pill_node(460, 850, 130, 60, "LOKIINI\nAI Agent Core", C_AGENT_BG, C_AGENT_BORDER, C_AGENT_TEXT, font_size=13))
    elements.extend(create_arrow(420, 779, 460, 860))
    
    elements.extend(create_pill_node(620, 855, 140, 50, "Parse Structured\nIntent Output (JSON)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_arrow(590, 880, 620, 880))
    
    # Router Diamond
    elements.append(create_diamond(790, 850, 90, 60))
    elements.append(create_text("Intent\nRouter?", 792, 868, fontSize=11, strokeColor=C_DECISION_TEXT))
    elements.extend(create_arrow(760, 880, 790, 880))
    
    # Branch 1: Conseil & Persona
    elements.extend(create_pill_node(920, 715, 200, 42, "Generate Expert Rental Advice\n(Conseils d'usage & sécurité)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1150, 715, 200, 42, "WhatsApp: Send Text Response\n(Ton chaleureux & professionnel)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_arrow(880, 865, 920, 736, label="conseil", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(1120, 736, 1150, 736))
    
    # Branch 2: Search Catalog
    elements.extend(create_pill_node(920, 775, 200, 42, "Meilisearch: Fetch Top 3 Matériels\n(Prix MAD/j + Photos + Rayon km)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1150, 775, 220, 42, "WhatsApp: Send Interactive List\n(Cartes d'équipements + Boutons)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_arrow(880, 875, 920, 796, label="search", strokeColor=C_ACTION_BORDER))
    elements.extend(create_arrow(1120, 796, 1150, 796))
    
    # Branch 3: Pricing & Deposit Breakdown
    elements.extend(create_pill_node(920, 835, 200, 42, "Calc Total Rental + Commission\n+ Caution CMI (Non Débitée)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1150, 835, 220, 42, "WhatsApp: Send Transparent Summary\n(Détail MAD + Explication Caution)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_arrow(880, 880, 920, 856, label="pricing", strokeColor=C_ACTION_BORDER))
    elements.extend(create_arrow(1120, 856, 1150, 856))
    
    # Branch 4: 1-Click Booking & Caution Hold
    elements.extend(create_pill_node(920, 895, 200, 42, "Redis: Hold Slot (INCR)\n& Lock Equipment Dates 15m", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    # Diamond Slot OK?
    elements.append(create_diamond(1150, 888, 85, 55))
    elements.append(create_text("Slot\nDispo?", 1152, 905, fontSize=10, strokeColor=C_DECISION_TEXT))
    elements.extend(create_arrow(880, 895, 920, 916, label="book", strokeColor=C_ALERT_BORDER))
    elements.extend(create_arrow(1120, 916, 1150, 916))
    
    # Slot Unavailable
    elements.extend(create_pill_node(1270, 870, 190, 38, "WhatsApp: Proposer Autres Dates\n(Créneau actuellement indisponible)", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_arrow(1235, 905, 1270, 889, label="No", strokeColor=C_ALERT_BORDER))
    
    # Slot OK Sub-flow
    elements.extend(create_pill_node(1270, 925, 190, 38, "Postgres: Create Booking\n(Status = pending_preauth)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1270, 975, 210, 38, "WhatsApp: Send CMI Pre-auth Link\n(Sécurisation caution par carte CB)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1270, 1025, 210, 38, "Push Notification Loueur Pro:\n'Nouvelle demande de réservation'", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    elements.extend(create_arrow(1235, 925, 1270, 944, label="Yes", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(1365, 963, 1365, 975))
    elements.extend(create_arrow(1365, 1013, 1365, 1025))
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

def main():
    data = generate_detailed_n8n_architecture()
    
    f1 = Path(r"d:\Lokiini\lokiini_n8n_architecture.excalidraw")
    f2 = Path(r"d:\Lokiini\docs\02_architecture_technique_et_ia\lokiini_n8n_architecture.excalidraw")
    
    with open(f1, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    with open(f2, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Generated Detailed n8n Architecture with {len(data['elements'])} elements.")

if __name__ == "__main__":
    main()
