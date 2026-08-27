#!/usr/bin/env python3
"""
Generator for Lokiini n8n Architecture with Embedded Why & How Paragraphs inside Excalidraw.
Strictly valid Excalidraw schema with hand-drawn font (Virgil, fontFamily: 1).
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
        "fontFamily": 1, # Virgil hand-drawn font
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
        "strokeStyle": "solid",
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
    """Creates a distinct styled callout card inside Excalidraw with Why & How paragraphs."""
    elements = []
    
    why_lines = [l for l in why_text.split("\n") if l.strip()]
    how_lines = [l for l in how_text.split("\n") if l.strip()]
    
    f_size = 11
    line_h = f_size * 1.35
    
    total_lines = 1 + len(why_lines) + 1 + len(how_lines)
    card_h = total_lines * line_h + 30
    
    # Outer box
    box = create_rectangle(
        x, y, width, card_h,
        strokeColor=C_EXPLANATION_BORDER,
        backgroundColor=C_EXPLANATION_BG,
        strokeWidth=1.5,
        roundness={"type": 3}
    )
    elements.append(box)
    
    cy = y + 12
    # Title
    hdr = create_text("💡 EXPLICATION MÉTIER & TECHNIQUE (POURQUOI & COMMENT) :", x + 16, cy, fontSize=12, strokeColor=C_TRIGGER_BORDER, textAlign="left")
    elements.append(hdr)
    cy += line_h + 4
    
    # Why section
    for line in why_lines:
        t = create_text(line, x + 16, cy, fontSize=f_size, strokeColor=DARK_TEXT, textAlign="left")
        elements.append(t)
        cy += line_h
        
    cy += 4
    # How section
    for line in how_lines:
        t = create_text(line, x + 16, cy, fontSize=f_size, strokeColor=DARK_TEXT, textAlign="left")
        elements.append(t)
        cy += line_h
        
    return elements, card_h

def build_complete_n8n_diagram():
    elements = []
    
    # Main Header
    elements.append(create_rectangle(
        40, 30, 1680, 75,
        strokeColor=C_HEADER_BORDER,
        backgroundColor=C_HEADER_BG,
        strokeWidth=2
    ))
    elements.append(create_text(
        "LOKIINI — Architecture n8n avec Explications Métier & Techniques Intégrées (Pourquoi & Comment)",
        60, 44,
        fontSize=18,
        strokeColor=C_HEADER_BORDER,
        textAlign="left"
    ))
    elements.append(create_text(
        "Orchestrateur d'automatisation événementielle • Conseiller IA WhatsApp, KYC Biométrique CNDP, Contrats DOC & Rapprochement CMI",
        60, 74,
        fontSize=12,
        strokeColor=DARK_TEXT,
        textAlign="left"
    ))
    
    # -----------------------------------------------------------------
    # WORKFLOW E: Ingestion & Rapprochement Bancaire CMI (Y: 125)
    # -----------------------------------------------------------------
    e_y = 125
    elements.append(create_rectangle(40, e_y, 1680, 205, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("E. Ingestion & Rapprochement Bancaire Journalier CMI, Payzone & CashPlus (Cron 23:59)", 60, e_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Nodes
    elements.extend(create_pill_node(60, e_y + 35, 150, 48, "Cron Trigger\n(Tous les soirs 23:59)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(240, e_y + 35, 180, 48, "HTTP: Fetch CMI Daily Batch\n& Webhook CashPlus logs", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(450, e_y + 35, 190, 48, "PostgreSQL: Query Bookings\n& Pre-auth Tokens du jour", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(670, e_y + 35, 180, 48, "Code: Reconcile Amounts\n& Calc Platform Splits (15-5%)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(880, e_y + 35, 170, 48, "Generate Financial Summary\n(PDF / Excel Consolidé)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1080, e_y + 35, 190, 48, "Email Node: Send Daily Report\n➔ Direction Financière (MAD)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1300, e_y + 35, 180, 48, "Slack / Discord Admin Alert:\nStatut Rapprochement OK", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1510, e_y + 35, 190, 48, "Archive Audit Log\n(Bucket R2 Chiffré)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    
    elements.extend(create_arrow(210, e_y + 59, 240, e_y + 59))
    elements.extend(create_arrow(420, e_y + 59, 450, e_y + 59))
    elements.extend(create_arrow(640, e_y + 59, 670, e_y + 59))
    elements.extend(create_arrow(850, e_y + 59, 880, e_y + 59))
    elements.extend(create_arrow(1050, e_y + 59, 1080, e_y + 59))
    elements.extend(create_arrow(1270, e_y + 59, 1300, e_y + 59))
    elements.extend(create_arrow(1480, e_y + 59, 1510, e_y + 59))
    
    # Embedded Paragraph Explanation for Workflow E
    why_e = "📌 POURQUOI (WHY) : Séparer hermétiquement les cautions séquestrées (passif) du chiffre d'affaires réel de la plateforme (commissions 15% particuliers, 7% pros), et détecter immédiatement tout rejet ou fraude CMI/CashPlus."
    how_e = "⚙️ COMMENT (HOW) : À 23h59, n8n interroge les API CMI/CashPlus, réconcilie ligne à ligne avec PostgreSQL, calcule les commissions nettes, émet le rapport financier consolidé et alerte sur Slack (0 divergence)."
    elements.extend(create_explanation_card(60, e_y + 95, 1640, why_e, how_e)[0])
    
    # -------------------------------------------------------------
    # WORKFLOW D: Relance Restitution & Rappels Check-out (Y: 350)
    # -------------------------------------------------------------
    d_y = 350
    elements.append(create_rectangle(40, d_y, 1680, 205, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("D. Relance Restitution, Prolongation Payante & Rappel d'État des Lieux (Cron Horaire)", 60, d_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, d_y + 35, 150, 48, "Hourly Cron Schedule\n(Toutes les heures 00:00)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(240, d_y + 35, 180, 48, "PostgreSQL: Get Bookings\nExpiring at J-1 & H-2", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(450, d_y + 35, 180, 48, "Item Lists: Split In Batches\n& Filter Already Reminded", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(660, d_y + 35, 190, 48, "Generate Dynamic Return Link\n& Secure Upload Token", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(880, d_y + 35, 220, 48, "WhatsApp Cloud API: Send Return\nChecklist + Video Check-out Button", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1130, d_y + 35, 200, 48, "Option: Click 'Prolonger 24h'\n➔ Re-calc Total MAD & Pre-auth", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(1360, d_y + 35, 180, 48, "PostgreSQL: Update Status\n➔ reminder_sent = true", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1570, d_y + 35, 130, 48, "Notify Owner\n(Push App)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    elements.extend(create_arrow(210, d_y + 59, 240, d_y + 59))
    elements.extend(create_arrow(420, d_y + 59, 450, d_y + 59))
    elements.extend(create_arrow(630, d_y + 59, 660, d_y + 59))
    elements.extend(create_arrow(850, d_y + 59, 880, d_y + 59))
    elements.extend(create_arrow(1100, d_y + 59, 1130, d_y + 59))
    elements.extend(create_arrow(1330, d_y + 59, 1360, d_y + 59))
    elements.extend(create_arrow(1540, d_y + 59, 1570, d_y + 59))
    
    why_d = "📌 POURQUOI (WHY) : Réduire le taux de retard de restitution de 35% à moins de 3%, désamorcer les conflits d'horaires entre locataires et loueurs, et monétiser les prolongations de chantier en un clic sans friction."
    how_d = "⚙️ COMMENT (HOW) : Un cron horaire cible les fins de location à J-1 et H-2, envoie par WhatsApp une checklist de retour avec bouton vidéo de check-out et option 'Prolonger 24h' qui réajuste automatiquement l'autorisation CMI."
    elements.extend(create_explanation_card(60, d_y + 95, 1640, why_d, how_d)[0])
    
    # -------------------------------------------------------------
    # WORKFLOW C: Contrat de Bail DOC & Scellement RFC 3161 (Y: 575)
    # -------------------------------------------------------------
    c_y = 575
    elements.append(create_rectangle(40, c_y, 1680, 205, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("C. Génération Contrat de Bail Numérique DOC & Scellement Horodaté RFC 3161 (Loi 53-05)", 60, c_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, c_y + 35, 160, 48, "Webhook: booking.confirmed\n(Propriétaire a validé)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(250, c_y + 35, 190, 48, "Fetch Rental Details, CIN,\nMatériel & CMI Pre-auth Ref", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(470, c_y + 35, 190, 48, "HTML-to-PDF Engine:\nGenerate Contrat DOC Art. 627", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(690, c_y + 35, 180, 48, "Crypto Node: Compute\nSHA-256 Hash du Contrat PDF", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(900, c_y + 35, 180, 48, "HTTP: RFC 3161 Timestamp\n(Horodatage Légal Certifié)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(1110, c_y + 35, 180, 48, "S3/R2 Node: Upload Contract\n& Generate Signed URLs", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1320, c_y + 35, 200, 48, "WhatsApp: Send Contract PDF\n+ QR Code Check-in au Locataire", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1550, c_y + 35, 150, 48, "WhatsApp: Send Copy\n➔ Propriétaire Pro", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    elements.extend(create_arrow(220, c_y + 59, 250, c_y + 59))
    elements.extend(create_arrow(440, c_y + 59, 470, c_y + 59))
    elements.extend(create_arrow(660, c_y + 59, 690, c_y + 59))
    elements.extend(create_arrow(870, c_y + 59, 900, c_y + 59))
    elements.extend(create_arrow(1080, c_y + 59, 1110, c_y + 59))
    elements.extend(create_arrow(1290, c_y + 59, 1320, c_y + 59))
    elements.extend(create_arrow(1520, c_y + 59, 1550, c_y + 59))
    
    why_c = "📌 POURQUOI (WHY) : Conférer une pleine force probante et exécutoire devant les tribunaux marocains en cas de vol ou litige (Dahir des Obligations et Contrats - DOC, Art. 627+ et Loi 53-05 sur la signature électronique)."
    how_c = "⚙️ COMMENT (HOW) : Dès acceptation de la réservation, n8n génère le contrat PDF avec identités CIN/ICE vérifiées, calcule l'empreinte SHA-256, scelle l'horodatage RFC 3161, archive sur Cloudflare R2 et envoie le bail signé + QR Code par WhatsApp."
    elements.extend(create_explanation_card(60, c_y + 95, 1640, why_c, how_c)[0])
    
    # -------------------------------------------------------------
    # WORKFLOW B: Pipeline KYC Biométrique CNDP (Y: 800)
    # -------------------------------------------------------------
    b_y = 800
    elements.append(create_rectangle(40, b_y, 1680, 220, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("B. Pipeline KYC Biométrique CNDP (OCR CIN, Liveness anti-deepfake & Escalade Fraude)", 60, b_y + 10, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, b_y + 35, 160, 48, "Webhook: kyc.submitted\n(Upload CIN + Vidéo Selfie)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(250, b_y + 35, 180, 48, "HTTP: Call OCR Engine\n(Extract CIN, Nom, Dates)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(460, b_y + 35, 180, 48, "HTTP: Liveness & Vector Match\n(Deepfake & Texture Check)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    # Diamond
    elements.append(create_diamond(670, b_y + 30, 90, 58))
    elements.append(create_text("Score\n>= 85%?", 672, b_y + 48, fontSize=10, strokeColor=C_DECISION_TEXT))
    
    # Yes
    elements.extend(create_pill_node(800, b_y + 15, 200, 36, "PostgreSQL: is_kyc_verified=true\n& Log CNDP Zero-Knowledge", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=10))
    elements.extend(create_pill_node(1030, b_y + 15, 220, 36, "WhatsApp: 'Identité Validée CNDP'\n➔ Déblocage Réservations Immédiat", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=10))
    elements.extend(create_pill_node(1280, b_y + 15, 190, 36, "Purge Raw Selfie in RAM\n(Conformité Loi 09-08)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT, font_size=10))
    
    # No
    elements.extend(create_pill_node(800, b_y + 60, 200, 36, "Slack / Telegram Alert:\n'KYC Suspect / Score Bas'", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT, font_size=10))
    elements.extend(create_pill_node(1030, b_y + 60, 220, 36, "WhatsApp: 'Vérification requise'\n➔ Conseil éclairage / repasser selfie", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT, font_size=10))
    elements.extend(create_pill_node(1280, b_y + 60, 190, 36, "Lock Booking Action\n(En attente examen manuel)", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT, font_size=10))
    
    elements.extend(create_arrow(220, b_y + 59, 250, b_y + 59))
    elements.extend(create_arrow(430, b_y + 59, 460, b_y + 59))
    elements.extend(create_arrow(640, b_y + 59, 670, b_y + 59))
    elements.extend(create_arrow(760, b_y + 45, 800, b_y + 33, label="Yes", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(760, b_y + 70, 800, b_y + 78, label="No", strokeColor=C_ALERT_BORDER))
    elements.extend(create_arrow(1000, b_y + 33, 1030, b_y + 33))
    elements.extend(create_arrow(1250, b_y + 33, 1280, b_y + 33))
    elements.extend(create_arrow(1000, b_y + 78, 1030, b_y + 78))
    elements.extend(create_arrow(1250, b_y + 78, 1280, b_y + 78))
    
    why_b = "📌 POURQUOI (WHY) : Empêcher les usurpations d'identité et les vols de matériel tout en respectant strictement la Loi 09-08 de la CNDP interdisant le stockage permanent de vidéos biométriques brutes."
    how_b = "⚙️ COMMENT (HOW) : Analyse OCR de la CIN + test de vivacité anti-deepfake. Si score >= 85%, validation PostgreSQL, envoi de confirmation WhatsApp et purge immédiate des vidéos de la mémoire vive (Zero-Knowledge Architecture)."
    elements.extend(create_explanation_card(60, b_y + 110, 1640, why_b, how_b)[0])
    
    # -------------------------------------------------------------
    # WORKFLOW A: Conseiller Location IA WhatsApp (Y: 1040)
    # -------------------------------------------------------------
    a_y = 1040
    elements.append(create_rectangle(40, a_y, 1680, 520, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("A. Conseiller Location IA WhatsApp (LOKIINI Conversational Agent, Tools Stack & Intent Router)", 60, a_y + 10, fontSize=14, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Webhook Verify & Message
    elements.extend(create_pill_node(60, a_y + 35, 160, 40, "WhatsApp Webhook (GET)\nHub Verify Challenge", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT, font_size=10))
    elements.extend(create_pill_node(250, a_y + 35, 160, 40, "Validate Hub Token\n➔ Return challenge", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=10))
    elements.extend(create_pill_node(440, a_y + 35, 130, 40, "Respond 200 OK\n(Meta Handshake)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=10))
    elements.extend(create_arrow(220, a_y + 55, 250, a_y + 55))
    elements.extend(create_arrow(410, a_y + 55, 440, a_y + 55))
    
    elements.extend(create_pill_node(60, a_y + 88, 160, 45, "WhatsApp Webhook (POST)\nIncoming Customer Msg", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT, font_size=10))
    elements.extend(create_pill_node(250, a_y + 88, 170, 45, "Extract Message Payload\n(Text / Voice / Location / Phone)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=10))
    elements.extend(create_arrow(220, a_y + 110, 250, a_y + 110))
    
    # Tools Stack
    tool_items = [
        ("Claude 3.5 Sonnet / Gemini Flash LLM (Bilingue FR / Darija)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Redis Window Buffer (10 Derniers échanges contextuels)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Meilisearch Catalog (Filtre Villes, BTP, Caméras, Outils)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Calculator (Prix Journalier MAD + Caution CMI Séquestre)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Check Slot Availability (Redis Lock / Postgres Bookings)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Generate CMI 3D-Secure 1-Click Payment Link", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
    ]
    t_y = a_y + 145
    for label, bg, border, txt in tool_items:
        elements.extend(create_pill_node(100, t_y, 250, 30, label, bg, border, txt, font_size=9))
        elements.extend(create_arrow(350, t_y + 15, 460, a_y + 195, strokeColor=border, strokeWidth=1, strokeStyle="dashed"))
        t_y += 34
        
    # AI Agent Core
    elements.extend(create_pill_node(460, a_y + 170, 130, 55, "LOKIINI\nAI Agent Core", C_AGENT_BG, C_AGENT_BORDER, C_AGENT_TEXT, font_size=12))
    elements.extend(create_arrow(420, a_y + 110, 460, a_y + 185))
    
    elements.extend(create_pill_node(620, a_y + 175, 140, 46, "Parse Structured\nIntent Output (JSON)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=10))
    elements.extend(create_arrow(590, a_y + 198, 620, a_y + 198))
    
    # Router Diamond
    elements.append(create_diamond(790, a_y + 170, 90, 56))
    elements.append(create_text("Intent\nRouter?", 792, a_y + 187, fontSize=11, strokeColor=C_DECISION_TEXT))
    elements.extend(create_arrow(760, a_y + 198, 790, a_y + 198))
    
    # Branch 1: Conseil
    elements.extend(create_pill_node(920, a_y + 40, 200, 38, "Generate Expert Rental Advice\n(Conseils d'usage & sécurité)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=10))
    elements.extend(create_pill_node(1150, a_y + 40, 200, 38, "WhatsApp: Send Text Response\n(Ton chaleureux & pro)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=10))
    elements.extend(create_arrow(880, a_y + 185, 920, a_y + 59, label="conseil", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(1120, a_y + 59, 1150, a_y + 59))
    
    # Branch 2: Search Catalog
    elements.extend(create_pill_node(920, a_y + 95, 200, 38, "Meilisearch: Fetch Top 3 Matériels\n(Prix MAD/j + Photos + Rayon km)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=10))
    elements.extend(create_pill_node(1150, a_y + 95, 220, 38, "WhatsApp: Send Interactive List\n(Cartes d'équipements + Boutons)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=10))
    elements.extend(create_arrow(880, a_y + 195, 920, a_y + 114, label="search", strokeColor=C_ACTION_BORDER))
    elements.extend(create_arrow(1120, a_y + 114, 1150, a_y + 114))
    
    # Branch 3: Pricing
    elements.extend(create_pill_node(920, a_y + 150, 200, 38, "Calc Total Rental + Commission\n+ Caution CMI (Non Débitée)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=10))
    elements.extend(create_pill_node(1150, a_y + 150, 220, 38, "WhatsApp: Send Transparent Summary\n(Détail MAD + Explication Caution)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=10))
    elements.extend(create_arrow(880, a_y + 200, 920, a_y + 169, label="pricing", strokeColor=C_ACTION_BORDER))
    elements.extend(create_arrow(1120, a_y + 169, 1150, a_y + 169))
    
    # Branch 4: Booking & Caution Hold
    elements.extend(create_pill_node(920, a_y + 205, 200, 38, "Redis: Hold Slot (INCR)\n& Lock Equipment Dates 15m", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=10))
    
    # Diamond Slot OK?
    elements.append(create_diamond(1150, a_y + 198, 85, 52))
    elements.append(create_text("Slot\nDispo?", 1152, a_y + 214, fontSize=10, strokeColor=C_DECISION_TEXT))
    elements.extend(create_arrow(880, a_y + 205, 920, a_y + 224, label="book", strokeColor=C_ALERT_BORDER))
    elements.extend(create_arrow(1120, a_y + 224, 1150, a_y + 224))
    
    # Slot Unavailable
    elements.extend(create_pill_node(1270, a_y + 180, 190, 34, "WhatsApp: Proposer Autres Dates\n(Créneau actuellement indisponible)", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT, font_size=9))
    elements.extend(create_arrow(1235, a_y + 215, 1270, a_y + 197, label="No", strokeColor=C_ALERT_BORDER))
    
    # Slot OK
    elements.extend(create_pill_node(1270, a_y + 230, 190, 34, "Postgres: Create Booking\n(Status = pending_preauth)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=9))
    elements.extend(create_pill_node(1270, a_y + 275, 210, 34, "WhatsApp: Send CMI Pre-auth Link\n(Sécurisation caution par carte CB)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=9))
    elements.extend(create_pill_node(1270, a_y + 320, 210, 34, "Push Notification Loueur Pro:\n'Nouvelle demande de réservation'", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT, font_size=9))
    
    elements.extend(create_arrow(1235, a_y + 235, 1270, a_y + 247, label="Yes", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(1365, a_y + 264, 1365, a_y + 275))
    elements.extend(create_arrow(1365, a_y + 309, 1365, a_y + 320))
    
    why_a = "📌 POURQUOI (WHY) : Capter les 80%+ de demandes de location initiées sur WhatsApp au Maroc (en Darija ou Français) et transformer une simple discussion informelle en réservation ferme avec paiement / caution CMI en moins de 60 secondes."
    how_a = "⚙️ COMMENT (HOW) : Webhook Meta ➔ LLM Claude/Gemini avec buffer mémoire Redis ➔ Appel d'outils (Meilisearch, Calculateur CMI MAD, Lock Redis 15m) ➔ Aiguillage vers 4 intentions (Conseil, Recherche, Devis, Réservation 1-clic avec lien de pré-autorisation CMI 3D-Secure)."
    elements.extend(create_explanation_card(60, a_y + 365, 1640, why_a, how_a)[0])
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

def main():
    data = build_complete_n8n_diagram()
    
    f1 = Path(r"d:\Lokiini\lokiini_n8n_architecture.excalidraw")
    f2 = Path(r"d:\Lokiini\docs\02_architecture_technique_et_ia\lokiini_n8n_architecture.excalidraw")
    
    with open(f1, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    with open(f2, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Generated n8n diagram with embedded explanations: {len(data['elements'])} elements")

if __name__ == "__main__":
    main()
