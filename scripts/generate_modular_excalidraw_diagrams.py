#!/usr/bin/env python3
"""
Modular Excalidraw Generator for Lokiini / MatOS.
Produces 4 separate, dedicated diagrams in the exact hand-drawn aesthetic (fontFamily: 1, roughness: 1):
1. lokiini_n8n_architecture.excalidraw (Dedicated n8n Workflow Automation Architecture)
2. lokiini_system_architecture.excalidraw (5-Tier Core System Architecture)
3. lokiini_database_erd.excalidraw (PostgreSQL 16 Entity-Relationship Diagram)
4. lokiini_uml_workflows.excalidraw (UML Sequence & State Machine)
"""

import json
import random
import time
from pathlib import Path

# Color Palette (Matching the reference hand-drawn n8n diagram)
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
C_PANEL_BG = "transparent"

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
        "roughness": kwargs.get("roughness", 1), # Hand-drawn style
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
        "fontFamily": 1, # 1 = Virgil hand-drawn font
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

def create_pill_node(x, y, width, height, text, bg_color, border_color, text_color, font_size=12):
    """Creates a rounded pill/capsule node in hand-drawn style."""
    elements = []
    box = create_rectangle(
        x, y, width, height,
        strokeColor=border_color,
        backgroundColor=bg_color,
        strokeWidth=1.5,
        roundness={"type": 3}
    )
    elements.append(box)
    
    t_elem = create_text(
        text, x + 6, y + (height - font_size * 1.35) / 2,
        width=width - 12,
        height=font_size * 1.35,
        fontSize=font_size,
        strokeColor=text_color,
        textAlign="center"
    )
    elements.append(t_elem)
    return elements

# =====================================================================
# 1. N8N ARCHITECTURE DIAGRAM (Matches user reference image layout)
# =====================================================================
def build_n8n_architecture():
    elements = []
    
    # Master Header (Top Banner)
    elements.append(create_rectangle(
        40, 30, 1620, 65,
        strokeColor=C_HEADER_BORDER,
        backgroundColor=C_HEADER_BG,
        strokeWidth=2
    ))
    elements.append(create_text(
        "LOKIINI — Architecture Système n8n (Conseiller IA WhatsApp, KYC Biométrique CNDP, Caution CMI & Rapprochement)",
        60, 48,
        fontSize=18,
        strokeColor=C_HEADER_BORDER,
        textAlign="left"
    ))
    
    # -----------------------------------------------------------------
    # WORKFLOW E: Rapprochement Bancaire CMI & CashPlus (Top swimlane)
    # -----------------------------------------------------------------
    elements.append(create_rectangle(40, 115, 1620, 100, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("E. Ingestion & Rapprochement Bancaire Journalier CMI & CashPlus (Daily 23:59 Cron)", 60, 125, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, 150, 160, 44, "Cron Schedule (23:59)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(260, 150, 180, 44, "Fetch CMI Batch & CashPlus", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(480, 150, 190, 44, "Reconcile with Postgres DB", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(710, 150, 180, 44, "Calc Platform Split (15-5%)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(930, 150, 160, 44, "Split in Batches", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1130, 150, 200, 44, "Send Accounting Report (Email)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1370, 150, 180, 44, "Push Status to Slack Admin", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    elements.extend(create_arrow(220, 172, 260, 172))
    elements.extend(create_arrow(440, 172, 480, 172))
    elements.extend(create_arrow(670, 172, 710, 172))
    elements.extend(create_arrow(890, 172, 930, 172))
    elements.extend(create_arrow(1090, 172, 1130, 172))
    elements.extend(create_arrow(1330, 172, 1370, 172))
    
    # -----------------------------------------------------------------
    # WORKFLOW D: Relance Restitution & Check-out (J-1 & H-2)
    # -----------------------------------------------------------------
    elements.append(create_rectangle(40, 230, 1620, 100, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("D. Relance Restitution & Suivi Fin de Location (Daily / Hourly Cron)", 60, 240, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, 265, 160, 44, "Hourly Rental Monitor", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(260, 265, 180, 44, "Get Ending Bookings (J-1/H-2)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(480, 265, 190, 44, "Generate Check-out Link", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(710, 265, 160, 44, "Split Renters", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(910, 265, 220, 44, "Send WhatsApp Return Checklist", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1170, 265, 200, 44, "Update Booking State in DB", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    elements.extend(create_arrow(220, 287, 260, 287))
    elements.extend(create_arrow(440, 287, 480, 287))
    elements.extend(create_arrow(670, 287, 710, 287))
    elements.extend(create_arrow(870, 287, 910, 287))
    elements.extend(create_arrow(1130, 287, 1170, 287))
    
    # -----------------------------------------------------------------
    # WORKFLOW C: Ingestion Matériel, Scoring & Sync Catalogue
    # -----------------------------------------------------------------
    elements.append(create_rectangle(40, 345, 1620, 100, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("C. Ingestion Matériel Loueur, Auto-Scoring & Synchronisation Meilisearch", 60, 355, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, 380, 160, 44, "New Equipment Webhook", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(260, 380, 180, 44, "Normalize Specs (AI Vision)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(480, 380, 190, 44, "Lokiini Pricing Evaluator", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(710, 380, 180, 44, "Upsert PostgreSQL DB", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(930, 380, 180, 44, "Sync Index Meilisearch", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1150, 380, 170, 44, "Purge Redis Cache", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1360, 380, 190, 44, "Notify Owner Published", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    elements.extend(create_arrow(220, 402, 260, 402))
    elements.extend(create_arrow(440, 402, 480, 402))
    elements.extend(create_arrow(670, 402, 710, 402))
    elements.extend(create_arrow(890, 402, 930, 402))
    elements.extend(create_arrow(1110, 402, 1150, 402))
    elements.extend(create_arrow(1320, 402, 1360, 402))
    
    # -----------------------------------------------------------------
    # WORKFLOW B: Traitement KYC Biométrique & Alerte Fraude CNDP
    # -----------------------------------------------------------------
    elements.append(create_rectangle(40, 460, 1620, 100, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("B. Pipeline KYC Biométrique CNDP & Circuit d'Alerte Fraude (Liveness Check)", 60, 470, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    
    elements.extend(create_pill_node(60, 495, 160, 44, "KYC Submission Webhook", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(260, 495, 180, 44, "OCR CIN & Face Vector Match", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    # Diamond decision for Score
    elements.append(create_diamond(480, 492, 90, 50))
    elements.append(create_text("Score >= 85%?", 482, 508, fontSize=10, strokeColor=C_DECISION_TEXT))
    
    # Valid branch
    elements.extend(create_pill_node(610, 475, 180, 38, "Update User: KYC Verified", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(830, 475, 200, 38, "WhatsApp: Identité Validée", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    # Invalid / Review branch
    elements.extend(create_pill_node(610, 520, 180, 38, "Notify Support (Slack Alert)", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_pill_node(830, 520, 200, 38, "WhatsApp: Reprendre Selfie", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    
    elements.extend(create_arrow(220, 517, 260, 517))
    elements.extend(create_arrow(440, 517, 480, 517))
    elements.extend(create_arrow(570, 505, 610, 494, label="Yes", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(570, 525, 610, 539, label="No", strokeColor=C_ALERT_BORDER))
    elements.extend(create_arrow(790, 494, 830, 494))
    elements.extend(create_arrow(790, 539, 830, 539))
    
    # -----------------------------------------------------------------
    # WORKFLOW A: Conseiller IA WhatsApp Lokiini & Intent Router (Bottom)
    # -----------------------------------------------------------------
    elements.append(create_rectangle(40, 575, 1620, 380, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("A. Conseiller Location IA WhatsApp (LOKIINI AI Agent & Intent Router)", 60, 585, fontSize=14, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Inbound triggers
    elements.extend(create_pill_node(60, 615, 150, 38, "WhatsApp Verify (GET)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(240, 615, 150, 38, "Return hub.challenge", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(420, 615, 130, 38, "Respond 200 OK", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    elements.extend(create_arrow(210, 634, 240, 634))
    elements.extend(create_arrow(390, 634, 420, 634))
    
    elements.extend(create_pill_node(60, 675, 150, 44, "Incoming Msg (POST)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(240, 675, 160, 44, "Extract User Intent & Loc", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_arrow(210, 697, 240, 697))
    
    # AI Tools Stack (Left side capsules)
    tools_y = 735
    tools = [
        ("Claude 3.5 / Gemini Flash LLM", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Redis Window Memory (Session)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Search Lokiini Catalog", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Calc CMI Caution & MAD", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: Check Equipment Slot", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("Tool: 1-Click Book & Pay Link", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
    ]
    for label, bg, border, txt in tools:
        elements.extend(create_pill_node(130, tools_y, 200, 32, label, bg, border, txt, font_size=10))
        elements.extend(create_arrow(330, tools_y + 16, 430, 770, strokeColor=border, strokeWidth=1, strokeStyle="dashed"))
        tools_y += 36
        
    # AI Agent Central Node
    elements.extend(create_pill_node(430, 745, 110, 50, "AI Agent", C_AGENT_BG, C_AGENT_BORDER, C_AGENT_TEXT, font_size=14))
    elements.extend(create_arrow(320, 719, 430, 765))
    
    elements.extend(create_pill_node(570, 748, 130, 44, "Parse Output", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_arrow(540, 770, 570, 770))
    
    # Intent Decision Diamond
    elements.append(create_diamond(730, 745, 80, 50))
    elements.append(create_text("Intent?", 734, 762, fontSize=11, strokeColor=C_DECISION_TEXT))
    elements.extend(create_arrow(700, 770, 730, 770))
    
    # Intent Branch 1: Chat / Conseil
    elements.extend(create_pill_node(860, 620, 180, 36, "Generate Persona Advice", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1080, 620, 180, 36, "Send WhatsApp Message", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_arrow(810, 760, 860, 638, label="conseil", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(1040, 638, 1080, 638))
    
    # Intent Branch 2: Search Equipment
    elements.extend(create_pill_node(860, 675, 180, 36, "Fetch 3 Matériels (MAD/j)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1080, 675, 200, 36, "Send Interactive Card List (WA)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_arrow(810, 765, 860, 693, label="search", strokeColor=C_ACTION_BORDER))
    elements.extend(create_arrow(1040, 693, 1080, 693))
    
    # Intent Branch 3: Pricing & Caution Calc
    elements.extend(create_pill_node(860, 730, 180, 36, "Calc Total MAD + CMI Deposit", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1080, 730, 200, 36, "Send Price & Caution Summary", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_arrow(810, 770, 860, 748, label="price", strokeColor=C_ACTION_BORDER))
    elements.extend(create_arrow(1040, 748, 1080, 748))
    
    # Intent Branch 4: Book & Lock Slot
    elements.extend(create_pill_node(860, 785, 180, 36, "Hold Slot (Redis INCR)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    # Diamond Slot OK?
    elements.append(create_diamond(1080, 778, 80, 50))
    elements.append(create_text("Slot OK?", 1085, 795, fontSize=10, strokeColor=C_DECISION_TEXT))
    elements.extend(create_arrow(810, 775, 860, 803, label="book", strokeColor=C_ALERT_BORDER))
    elements.extend(create_arrow(1040, 803, 1080, 803))
    
    # Slot Unavailable branch
    elements.extend(create_pill_node(1200, 765, 180, 34, "Send Alt Dates (WA)", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_arrow(1160, 795, 1200, 782, label="No", strokeColor=C_ALERT_BORDER))
    
    # Slot OK branch
    elements.extend(create_pill_node(1200, 815, 180, 34, "Create Booking in DB", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1200, 860, 180, 34, "Send CMI 3D-Secure Link", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(create_pill_node(1200, 905, 180, 34, "Push Lead to Pro Loueur", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    elements.extend(create_arrow(1160, 810, 1200, 832, label="Yes", strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(1290, 849, 1290, 860))
    elements.extend(create_arrow(1290, 894, 1290, 905))
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

# =====================================================================
# 2. SYSTEM ARCHITECTURE (Dedicated 5-Tier Diagram)
# =====================================================================
def build_system_architecture():
    elements = []
    
    elements.append(create_rectangle(40, 30, 1620, 65, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Architecture Système Globale (5 Paliers)", 60, 48, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    
    # Tier 1: Frontends
    elements.append(create_rectangle(40, 115, 1620, 140, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 1 : Applications Frontend & Clients", 60, 125, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, 160, 460, 80, "Next.js 14 Web (App Router)\nSSR / SEO Local Maroc • Tailwind + shadcn/ui", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(580, 160, 460, 80, "React Native / Expo Mobile App\nCaméra KYC Direct • État des Lieux Vidéo", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1100, 160, 540, 80, "Portail Pro & Dashboard Loueur\nGestion Flotte • Cautions CMI • Factures ICE B2B", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    
    # Tier 2: Edge Gateway
    elements.append(create_rectangle(40, 275, 1620, 110, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 2 : Edge Gateway & Sécurité", 60, 285, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, 315, 460, 55, "Cloudflare CDN & WAF (DDoS / SSL)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(580, 315, 460, 55, "API Gateway / JWT Auth & Rate Limiting", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(1100, 315, 540, 55, "Passerelle WebSockets (Chat & Notifs Live)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    # Tier 3: Backend Services
    elements.append(create_rectangle(40, 405, 1620, 140, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 3 : Microservices & Moteurs Métier", 60, 415, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, 445, 360, 85, "Service Catalogue & Annonces\nCRUD Matériel • Calendrier Dispo", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(450, 445, 370, 85, "Service Réservations & CMI\nTunnel Escrow • Caution • Splits", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(850, 445, 370, 85, "Moteur KYC Biométrique CNDP\nOCR CIN • Liveness anti-deepfake", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(1250, 445, 390, 85, "État des Lieux & Contrat DOC\nVidéo SHA-256 • Scellement RFC 3161", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    # Tier 4: Data Layer
    elements.append(create_rectangle(40, 565, 1620, 130, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 4 : Stockage, Données & Moteur de Recherche", 60, 575, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, 605, 360, 75, "PostgreSQL 16 (Master/Replica)\nRelations ACID • Chiffrement pgcrypto", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(create_pill_node(450, 605, 370, 75, "Redis 7 (In-Memory)\nSessions • Verrous de dates • Queues", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_pill_node(850, 605, 370, 75, "Meilisearch\nRecherche plein texte instantanée (<50ms)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(create_pill_node(1250, 605, 390, 75, "Cloudflare R2 / AWS S3\nPhotos Matériel & Vidéos SHA-256", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    
    # Tier 5: Moroccan Integrations & Automation
    elements.append(create_rectangle(40, 715, 1620, 130, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Palier 5 : Écosystème Maroc & Moteur Automation n8n", 60, 725, fontSize=13, strokeColor=DARK_TEXT, textAlign="left"))
    elements.extend(create_pill_node(60, 755, 360, 75, "Passerelle CMI / Payzone\nEmpreinte Caution sans débit", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(450, 755, 370, 75, "Réseau CashPlus / Wafacash\nPaiement Cash-In en agence", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(create_pill_node(850, 755, 370, 75, "Moteur Automation n8n\nRelances WhatsApp • Audit CMI", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(create_pill_node(1250, 755, 390, 75, "Tiers de Confiance & Légal\nCNDP (Loi 09-08) • Horodatage RFC 3161", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    # Flow Arrows
    elements.extend(create_arrow(290, 240, 290, 315))
    elements.extend(create_arrow(810, 240, 810, 315))
    elements.extend(create_arrow(1370, 240, 1370, 315))
    
    elements.extend(create_arrow(290, 370, 240, 445))
    elements.extend(create_arrow(810, 370, 635, 445))
    elements.extend(create_arrow(810, 370, 1035, 445))
    elements.extend(create_arrow(1370, 370, 1445, 445))
    
    elements.extend(create_arrow(240, 530, 240, 605, label="SQL"))
    elements.extend(create_arrow(635, 530, 635, 605, label="Locks"))
    elements.extend(create_arrow(1035, 530, 1035, 605, label="Index"))
    elements.extend(create_arrow(1445, 530, 1445, 605, label="Media"))
    
    elements.extend(create_arrow(635, 680, 240, 755, label="Pre-Auth"))
    elements.extend(create_arrow(635, 680, 635, 755, label="Cash"))
    elements.extend(create_arrow(1035, 530, 1035, 755, label="Events"))
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

# =====================================================================
# 3. DATABASE ERD DIAGRAM (Dedicated PostgreSQL Schema)
# =====================================================================
def build_database_erd():
    elements = []
    
    elements.append(create_rectangle(40, 30, 1620, 65, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Schéma de Base de Données Relationnel (PostgreSQL 16 ERD)", 60, 48, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    
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
    
    # Render table boxes in hand-drawn style
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
        
    e1, _ = render_hand_drawn_table(60, 120, 360, "users", u_pk, u_fk, u_reg, C_ACTION_BORDER, C_ACTION_BORDER)
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
    e2, _ = render_hand_drawn_table(460, 120, 360, "equipment", eq_pk, eq_fk, eq_reg, C_ACTION_BORDER, C_ACTION_BORDER)
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
    e3, _ = render_hand_drawn_table(860, 120, 380, "bookings", bk_pk, bk_fk, bk_reg, C_TRIGGER_BORDER, C_TRIGGER_BORDER)
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
    e4, _ = render_hand_drawn_table(1280, 120, 380, "cmi_transactions", cmi_pk, cmi_fk, cmi_reg, C_TRIGGER_BORDER, C_TRIGGER_BORDER)
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
    e5, _ = render_hand_drawn_table(460, 460, 360, "inspection_reports", ins_pk, ins_fk, ins_reg, C_TOOL_BORDER, C_TOOL_BORDER)
    elements.extend(e5)
    
    # Table 6: REVIEWS
    rev_pk = [("id", "UUID (v4)")]
    rev_fk = [("booking_id", "UUID", "bookings.id"), ("reviewer_id", "UUID", "users.id")]
    rev_reg = [
        ("rating_score", "INTEGER CHECK (1-5)"),
        ("comment", "TEXT"),
        ("created_at", "TIMESTAMPTZ DEFAULT NOW()")
    ]
    e6, _ = render_hand_drawn_table(860, 460, 380, "reviews", rev_pk, rev_fk, rev_reg, C_OUTPUT_BORDER, C_OUTPUT_BORDER)
    elements.extend(e6)
    
    # ERD Relationship Arrows
    elements.extend(create_arrow(420, 160, 460, 160, strokeColor=C_ACTION_BORDER, label="1:N"))
    elements.extend(create_arrow(420, 200, 860, 200, strokeColor=C_ACTION_BORDER, label="renter 1:N"))
    elements.extend(create_arrow(820, 160, 860, 160, strokeColor=C_TRIGGER_BORDER, label="1:N"))
    elements.extend(create_arrow(1240, 160, 1280, 160, strokeColor=C_TRIGGER_BORDER, label="1:1"))
    elements.extend(create_arrow(860, 400, 820, 480, strokeColor=C_TOOL_BORDER, label="1:2"))
    elements.extend(create_arrow(1050, 420, 1050, 460, strokeColor=C_OUTPUT_BORDER, label="1:N"))
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

# =====================================================================
# 4. UML WORKFLOWS & STATE MACHINE (Dedicated Flow Diagram)
# =====================================================================
def build_uml_workflows():
    elements = []
    
    elements.append(create_rectangle(40, 30, 1620, 65, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Machine à États & Séquence UML du Tunnel de Confiance", 60, 48, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    
    # Left: State Machine
    elements.append(create_rectangle(40, 115, 760, 700, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Machine à États : Cycle de Réservation & Caution CMI", 60, 125, fontSize=14, strokeColor=DARK_TEXT, textAlign="left"))
    
    states = [
        ("1. DEMANDE INITIALE", "Locataire choisit dates & panier", 60, 165, C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT),
        ("2. PRÉ-AUTORISATION CMI", "Empreinte bancaire bloquée sans débit", 60, 245, C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT),
        ("3. ACCEPTATION LOUEUR", "Contrat DOC généré & signé", 60, 325, C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT),
        ("4. CHECK-IN SCELLÉ", "Vidéo d'état des lieux SHA-256", 60, 405, C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT),
        ("5. EN COURS D'UTILISATION", "Location active • Relances n8n", 60, 485, C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT),
        ("6. CHECK-OUT & CONTRÔLE", "Vérification contradictoire au retour", 60, 565, C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT),
        ("7. DÉNOUEMENT CAUTION", "Libération 100% ou Capture sinistre", 60, 645, C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT),
    ]
    
    for title, desc, sx, sy, bg, border, txt in states:
        elements.extend(create_pill_node(sx + 40, sy, 340, 54, f"{title}\n{desc}", bg, border, txt, font_size=11))
        
    for i in range(len(states) - 1):
        sy_curr = states[i][3] + 54
        sy_next = states[i+1][3]
        elements.extend(create_arrow(250, sy_curr, 250, sy_next))
        
    # Branching outcomes
    elements.extend(create_pill_node(450, 615, 320, 48, "✅ Matériel Intact : Caution Libérée 100%", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=11))
    elements.extend(create_pill_node(450, 675, 320, 48, "⚠️ Sinistre : Capture CMI + Assurance", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT, font_size=11))
    elements.extend(create_arrow(420, 672, 450, 639, strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(420, 672, 450, 699, strokeColor=C_ALERT_BORDER))
    
    # Right: Sequence Diagram
    elements.append(create_rectangle(820, 115, 840, 700, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Diagramme de Séquence UML (Tunnel de Confiance & Caution CMI)", 840, 125, fontSize=14, strokeColor=DARK_TEXT, textAlign="left"))
    
    actors = [
        ("Locataire", 860),
        ("Propriétaire", 1010),
        ("Lokiini API", 1160),
        ("CMI Gateway", 1310),
        ("n8n / Tiers", 1480)
    ]
    
    for name, ax in actors:
        elements.extend(create_pill_node(ax - 45, 160, 90, 32, name, C_HEADER_BG, C_HEADER_BORDER, C_HEADER_BORDER, font_size=10))
        # Dashed lifeline line
        now = int(time.time() * 1000)
        elements.append({
            "id": f"line_{random.randint(100000, 999999)}",
            "type": "line",
            "x": ax, "y": 192, "width": 1, "height": 590, "angle": 0,
            "strokeColor": BORDER_GRAY, "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "dashed", "roughness": 1, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": None, "seed": random.randint(1, 1000000),
            "version": 1, "versionNonce": random.randint(1, 1000000), "isDeleted": False,
            "boundElements": None, "updated": now, "link": None, "locked": False,
            "points": [[0, 0], [0, 590]], "lastCommittedPoint": None, "startBinding": None,
            "endBinding": None, "startArrowhead": None, "endArrowhead": None
        })
        
    seq_steps = [
        (860, 1160, 210, "1. Demande location + Scan CIN", C_ACTION_BORDER),
        (1160, 860, 245, "2. Formulaire 3D-Secure CMI", C_TRIGGER_BORDER),
        (860, 1310, 280, "3. Saisie CB & Empreinte", C_TRIGGER_BORDER),
        (1310, 1160, 315, "4. Caution Bloquée (Auth Token)", C_OUTPUT_BORDER),
        (1160, 1010, 350, "5. Push notif nouvelle résa", C_ACTION_BORDER),
        (1010, 1160, 385, "6. Confirmation loueur", C_ACTION_BORDER),
        (1160, 1480, 420, "7. Webhook n8n ➔ Contrat PDF DOC", C_TOOL_BORDER),
        (1480, 860, 455, "8. WhatsApp: Contrat + QR Check-in", C_TOOL_BORDER),
        (860, 1160, 490, "9. Upload Vidéo Check-in (SHA-256)", C_ACTION_BORDER),
        (1010, 1160, 525, "10. Signature contradictoire", C_ACTION_BORDER),
        (860, 1010, 565, "11. Restitution du matériel", DARK_TEXT),
        (1010, 1160, 605, "12. Validation retour sans dommage", C_OUTPUT_BORDER),
        (1160, 1310, 645, "13. Ordre Libération Caution CMI", C_OUTPUT_BORDER),
        (1310, 860, 680, "14. Plafond CB libéré instantanément", C_OUTPUT_BORDER),
    ]
    
    for sx, ex, sy, label, col in seq_steps:
        elements.extend(create_arrow(sx, sy, ex, sy, strokeColor=col, strokeWidth=1.5, label=label, labelColor=DARK_TEXT))
        
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
    
    # 1. n8n Architecture
    n8n_data = build_n8n_architecture()
    with open(base_dir / "lokiini_n8n_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(n8n_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_n8n_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(n8n_data, f, indent=2, ensure_ascii=False)
    print(f"Generated n8n Architecture: {len(n8n_data['elements'])} elements")
    
    # 2. System Architecture
    sys_data = build_system_architecture()
    with open(base_dir / "lokiini_system_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(sys_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_system_architecture.excalidraw", "w", encoding="utf-8") as f:
        json.dump(sys_data, f, indent=2, ensure_ascii=False)
    print(f"Generated System Architecture: {len(sys_data['elements'])} elements")
    
    # 3. Database ERD
    db_data = build_database_erd()
    with open(base_dir / "lokiini_database_erd.excalidraw", "w", encoding="utf-8") as f:
        json.dump(db_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_database_erd.excalidraw", "w", encoding="utf-8") as f:
        json.dump(db_data, f, indent=2, ensure_ascii=False)
    print(f"Generated Database ERD: {len(db_data['elements'])} elements")
    
    # 4. UML Workflows
    uml_data = build_uml_workflows()
    with open(base_dir / "lokiini_uml_workflows.excalidraw", "w", encoding="utf-8") as f:
        json.dump(uml_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_uml_workflows.excalidraw", "w", encoding="utf-8") as f:
        json.dump(uml_data, f, indent=2, ensure_ascii=False)
    print(f"Generated UML Workflows: {len(uml_data['elements'])} elements")

if __name__ == "__main__":
    main()
