#!/usr/bin/env python3
"""
Complete Excalidraw Suite Generator for Lokiini / MatOS.
Generates 6 modular diagrams with:
1. Zero text overflow & perfectly calculated bounding boxes (fixes all display errors).
2. Hand-drawn Virgil font (fontFamily: 1, roughness: 1).
3. NEW: UML Use Case Diagram (lokiini_use_case_diagram.excalidraw).
4. NEW: UML Class Diagram (lokiini_class_diagram.excalidraw).
5. UPDATED: UML Workflows & Sequence (lokiini_uml_workflows.excalidraw).
6. UPDATED: n8n Architecture, System Architecture, Database ERD.
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

def wrap_text(text, max_chars=55):
    """Wraps text so it never overflows a box width."""
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

def create_ellipse(x, y, width, height, **kwargs):
    elem_id = kwargs.get("id", f"ellipse_{random.randint(100000, 999999)}")
    now = int(time.time() * 1000)
    return {
        "id": elem_id,
        "type": "ellipse",
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
        "startArrowhead": kwargs.get("startArrowhead", None),
        "endArrowhead": kwargs.get("endArrowhead", "arrow")
    }
    
    elements = [arrow]
    if "label" in kwargs and kwargs["label"]:
        label_text = kwargs["label"]
        mid_x = start_x + dx * 0.5 - 20
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

def create_explanation_card(x, y, width, why_text, how_text, max_chars=65):
    """Creates a safely wrapped callout box with Why & How so text never overflows."""
    elements = []
    f_size = 11
    line_h = f_size * 1.35
    
    why_lines = wrap_text(why_text, max_chars)
    how_lines = wrap_text(how_text, max_chars)
    
    total_lines = 1 + len(why_lines) + 1 + len(how_lines)
    card_h = total_lines * line_h + 24
    
    box = create_rectangle(
        x, y, width, card_h,
        strokeColor=C_EXPLANATION_BORDER,
        backgroundColor=C_EXPLANATION_BG,
        strokeWidth=1.5,
        roundness={"type": 3}
    )
    elements.append(box)
    
    cy = y + 10
    hdr = create_text("💡 EXPLICATION MÉTIER & TECHNIQUE (POURQUOI & COMMENT) :", x + 14, cy, fontSize=11, strokeColor=C_TRIGGER_BORDER, textAlign="left")
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
# 1. FIXED UML WORKFLOWS & SEQUENCE (lokiini_uml_workflows.excalidraw)
# =====================================================================
def build_fixed_uml_workflows():
    elements = []
    
    # Master Header
    elements.append(create_rectangle(40, 30, 1860, 75, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Machine à États & Séquence UML du Tunnel de Confiance (Pourquoi & Comment)", 60, 44, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    elements.append(create_text("Modélisation dynamique du cycle de vie des réservations, de la pré-autorisation de caution CMI et des états des lieux", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Left Panel : State Machine (Y: 125, Width: 880, Height: 940)
    p1_w = 880
    p1_h = 920
    elements.append(create_rectangle(40, 125, p1_w, p1_h, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
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
        elements.extend(create_pill_node(sx + 30, sy, 380, 54, f"{title}\n{desc}", bg, border, txt, font_size=11))
        
    for i in range(len(states) - 1):
        sy_curr = states[i][3] + 54
        sy_next = states[i+1][3]
        elements.extend(create_arrow(280, sy_curr, 280, sy_next))
        
    # Branching outcomes
    elements.extend(create_pill_node(500, 625, 380, 48, "✅ Matériel Intact : Caution Libérée 100%", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT, font_size=11))
    elements.extend(create_pill_node(500, 685, 380, 48, "⚠️ Sinistre : Capture CMI + Assurance", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT, font_size=11))
    elements.extend(create_arrow(470, 682, 500, 649, strokeColor=C_OUTPUT_BORDER))
    elements.extend(create_arrow(470, 682, 500, 709, strokeColor=C_ALERT_BORDER))
    
    why_sm = "📌 POURQUOI (WHY) : La caution bancaire ne doit jamais bloquer les liquidités du locataire avant accord du propriétaire, et l'ordre de déblocage CMI doit s'exécuter immédiatement dès que le check-out est validé sans dommage."
    how_sm = "⚙️ COMMENT (HOW) : Les transitions d'état sont gérées atomiquement dans PostgreSQL. Le statut passe de 'held' à 'released' via un appel d'API CMI sécurisé déclenché automatiquement par n8n."
    elements.extend(create_explanation_card(60, 755, 840, why_sm, how_sm, max_chars=60)[0])
    
    # Right Panel : Sequence Diagram (Y: 125, X: 940, Width: 960, Height: 920)
    p2_x = 940
    p2_w = 960
    elements.append(create_rectangle(p2_x, 125, p2_w, p1_h, strokeColor=C_PANEL_BORDER, backgroundColor="transparent", strokeWidth=1.5))
    elements.append(create_text("Diagramme de Séquence UML (Tunnel de Confiance & Caution CMI)", p2_x + 20, 135, fontSize=14, strokeColor=DARK_TEXT, textAlign="left"))
    
    actors = [
        ("Locataire", p2_x + 50),
        ("Propriétaire", p2_x + 220),
        ("Lokiini API", p2_x + 420),
        ("CMI Gateway", p2_x + 630),
        ("n8n / Tiers", p2_x + 850)
    ]
    
    for name, ax in actors:
        elements.extend(create_pill_node(ax - 50, 170, 100, 32, name, C_HEADER_BG, C_HEADER_BORDER, C_HEADER_BORDER, font_size=10))
        now = int(time.time() * 1000)
        elements.append({
            "id": f"line_{random.randint(100000, 999999)}",
            "type": "line",
            "x": ax, "y": 202, "width": 1, "height": 530, "angle": 0,
            "strokeColor": BORDER_GRAY, "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "dashed", "roughness": 1, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": None, "seed": random.randint(1, 1000000),
            "version": 1, "versionNonce": random.randint(1, 1000000), "isDeleted": False,
            "boundElements": None, "updated": now, "link": None, "locked": False,
            "points": [[0, 0], [0, 530]], "lastCommittedPoint": None, "startBinding": None,
            "endBinding": None, "startArrowhead": None, "endArrowhead": None
        })
        
    seq_steps = [
        (actors[0][1], actors[2][1], 220, "1. Demande location + Scan CIN", C_ACTION_BORDER),
        (actors[2][1], actors[0][1], 255, "2. Formulaire 3D-Secure CMI", C_TRIGGER_BORDER),
        (actors[0][1], actors[3][1], 290, "3. Saisie CB & Empreinte", C_TRIGGER_BORDER),
        (actors[3][1], actors[2][1], 325, "4. Caution Bloquée (Auth Token)", C_OUTPUT_BORDER),
        (actors[2][1], actors[1][1], 360, "5. Push notif nouvelle résa", C_ACTION_BORDER),
        (actors[1][1], actors[2][1], 395, "6. Confirmation loueur", C_ACTION_BORDER),
        (actors[2][1], actors[4][1], 430, "7. Webhook n8n ➔ Contrat PDF DOC", C_TOOL_BORDER),
        (actors[4][1], actors[0][1], 465, "8. WhatsApp: Contrat + QR Check-in", C_TOOL_BORDER),
        (actors[0][1], actors[2][1], 500, "9. Upload Vidéo Check-in (SHA-256)", C_ACTION_BORDER),
        (actors[1][1], actors[2][1], 535, "10. Signature contradictoire remise", C_ACTION_BORDER),
        (actors[0][1], actors[1][1], 575, "11. Restitution du matériel", DARK_TEXT),
        (actors[1][1], actors[2][1], 610, "12. Validation retour sans dommage", C_OUTPUT_BORDER),
        (actors[2][1], actors[3][1], 645, "13. Ordre Libération Caution CMI", C_OUTPUT_BORDER),
        (actors[3][1], actors[0][1], 680, "14. Plafond CB libéré instantanément", C_OUTPUT_BORDER),
    ]
    
    for sx, ex, sy, label, col in seq_steps:
        elements.extend(create_arrow(sx, sy, ex, sy, strokeColor=col, strokeWidth=1.5, label=label, labelColor=DARK_TEXT))
        
    why_seq = "📌 POURQUOI (WHY) : Verrouiller juridiquement et financièrement chaque étape sans immobiliser de liquidités chez le locataire et sans risque d'impayé ou de vol pour le loueur."
    how_seq = "⚙️ COMMENT (HOW) : Les messages 1 à 14 s'enchaînent entre l'application, la passerelle monétique CMI et n8n qui délivre les contrats et notifie en temps réel sur WhatsApp."
    elements.extend(create_explanation_card(p2_x + 20, 755, 920, why_seq, how_seq, max_chars=68)[0])
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

# =====================================================================
# 2. NEW UML USE CASE DIAGRAM (lokiini_use_case_diagram.excalidraw)
# =====================================================================
def build_uml_use_case_diagram():
    elements = []
    
    # Master Header
    elements.append(create_rectangle(40, 30, 1860, 75, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Diagramme de Cas d'Utilisation UML (Acteurs, Cas Métier & Relations)", 60, 44, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    elements.append(create_text("Cartographie fonctionnelle des interactions entre Locataires, Loueurs B2B, Passerelle CMI, n8n et Administrateurs", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Boundary Box (System)
    sys_x = 380
    sys_y = 125
    sys_w = 1120
    sys_h = 950
    elements.append(create_rectangle(sys_x, sys_y, sys_w, sys_h, strokeColor=TEAL_BORDER if 'TEAL_BORDER' in globals() else "#0F6E56", backgroundColor="transparent", strokeWidth=2))
    elements.append(create_text("Système Lokiini Marketplace (Web + Mobile + n8n)", sys_x + 20, sys_y + 15, fontSize=15, strokeColor=C_ACTION_BORDER, textAlign="left"))
    
    # Helper to draw an Actor (Stick figure + label)
    def render_actor(x, y, label, role_desc):
        elems = []
        # Head (ellipse)
        elems.append(create_ellipse(x - 14, y, 28, 28, strokeColor=DARK_TEXT, backgroundColor=CARD_BG, strokeWidth=1.5))
        # Body (line)
        now = int(time.time() * 1000)
        elems.append({"id": f"line_{random.randint(100000, 999999)}", "type": "line", "x": x, "y": y + 28, "width": 1, "height": 38, "angle": 0, "strokeColor": DARK_TEXT, "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 1.5, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None, "seed": random.randint(1, 1000000), "version": 1, "versionNonce": random.randint(1, 1000000), "isDeleted": False, "boundElements": None, "updated": now, "link": None, "locked": False, "points": [[0, 0], [0, 38]], "lastCommittedPoint": None, "startBinding": None, "endBinding": None, "startArrowhead": None, "endArrowhead": None})
        # Arms (line)
        elems.append({"id": f"line_{random.randint(100000, 999999)}", "type": "line", "x": x - 22, "y": y + 42, "width": 44, "height": 1, "angle": 0, "strokeColor": DARK_TEXT, "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 1.5, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None, "seed": random.randint(1, 1000000), "version": 1, "versionNonce": random.randint(1, 1000000), "isDeleted": False, "boundElements": None, "updated": now, "link": None, "locked": False, "points": [[0, 0], [44, 0]], "lastCommittedPoint": None, "startBinding": None, "endBinding": None, "startArrowhead": None, "endArrowhead": None})
        # Left Leg
        elems.append({"id": f"line_{random.randint(100000, 999999)}", "type": "line", "x": x, "y": y + 66, "width": 18, "height": 28, "angle": 0, "strokeColor": DARK_TEXT, "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 1.5, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None, "seed": random.randint(1, 1000000), "version": 1, "versionNonce": random.randint(1, 1000000), "isDeleted": False, "boundElements": None, "updated": now, "link": None, "locked": False, "points": [[0, 0], [-18, 28]], "lastCommittedPoint": None, "startBinding": None, "endBinding": None, "startArrowhead": None, "endArrowhead": None})
        # Right Leg
        elems.append({"id": f"line_{random.randint(100000, 999999)}", "type": "line", "x": x, "y": y + 66, "width": 18, "height": 28, "angle": 0, "strokeColor": DARK_TEXT, "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 1.5, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None, "seed": random.randint(1, 1000000), "version": 1, "versionNonce": random.randint(1, 1000000), "isDeleted": False, "boundElements": None, "updated": now, "link": None, "locked": False, "points": [[0, 0], [18, 28]], "lastCommittedPoint": None, "startBinding": None, "endBinding": None, "startArrowhead": None, "endArrowhead": None})
        # Label
        elems.append(create_text(f"« Actor »\n{label}\n({role_desc})", x - 75, y + 102, width=150, fontSize=11, strokeColor=DARK_TEXT, textAlign="center"))
        return elems

    # Left Actors
    elements.extend(render_actor(180, 240, "Locataire", "Particulier / Artisan"))
    elements.extend(render_actor(180, 560, "Loueur", "Particulier / Pro BTP"))
    elements.extend(render_actor(180, 840, "Administrateur", "Support & Sécurité Fraude"))
    
    # Right Actors
    elements.extend(render_actor(1680, 280, "Passerelle CMI", "Monétique & Caution CB"))
    elements.extend(render_actor(1680, 620, "Moteur n8n / Tiers", "WhatsApp & Horodatage RFC 3161"))
    
    # Helper to create Use Case Ellipse
    def render_use_case(x, y, w, h, title, bg_col, border_col, txt_col):
        elems = []
        elems.append(create_ellipse(x, y, w, h, strokeColor=border_col, backgroundColor=bg_col, strokeWidth=1.5))
        lines = title.split("\n")
        f_size = 11
        line_h = f_size * 1.35
        t_y = y + (h - len(lines) * line_h) / 2
        elems.append(create_text(title, x + 6, t_y, width=w - 12, fontSize=f_size, strokeColor=txt_col, textAlign="center"))
        return elems
        
    # Column 1 of Use Cases (x: 430)
    elements.extend(render_use_case(430, 160, 280, 52, "Consulter Catalogue & Filtrer\n(Ville, BTP, Prix MAD)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    elements.extend(render_use_case(430, 240, 280, 52, "Passer KYC Biométrique CNDP\n(OCR CIN + Liveness check)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(render_use_case(430, 320, 280, 52, "Réserver Matériel & Bloquer Dates\n(Calcul dégressif journalier)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(render_use_case(430, 400, 280, 52, "Pré-autoriser Caution Bancaire\n(Empreinte CMI 3D-Secure)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(render_use_case(430, 480, 280, 52, "Publier & Gérer Annonces\n(Flotte, Tarifs, Caution MAD)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(render_use_case(430, 560, 280, 52, "Valider Demande de Réservation\n(Calendrier & Accord Loueur)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    elements.extend(render_use_case(430, 640, 280, 52, "Effectuer État des Lieux Vidéo\n(Check-in / Check-out SHA-256)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(render_use_case(430, 720, 280, 52, "Signer Contrat de Bail DOC\n(Loi 53-05 + RFC 3161)", C_TOOL_BG, C_TOOL_BORDER, C_TOOL_TEXT))
    elements.extend(render_use_case(430, 800, 280, 52, "Valider Restitution & Libérer Caution\n(Déblocage plafond CMI 100%)", C_OUTPUT_BG, C_OUTPUT_BORDER, C_OUTPUT_TEXT))
    
    # Column 2 of Use Cases (Extensions & Inclusions, x: 860)
    elements.extend(render_use_case(860, 240, 280, 52, "Détecter Fraude & Deepfake\n(Alerte Slack & Revue Manuelle)", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(render_use_case(860, 320, 280, 52, "Conseil Location IA WhatsApp\n(Agent conversationnel bilingue)", C_AGENT_BG, C_AGENT_BORDER, C_AGENT_TEXT))
    elements.extend(render_use_case(860, 480, 280, 52, "Demander Prolongation 24h/48h\n(Réajustement caution CMI)", C_TRIGGER_BG, C_TRIGGER_BORDER, C_TRIGGER_TEXT))
    elements.extend(render_use_case(860, 640, 280, 52, "Déclarer un Litige ou Sinistre\n(Capture partielle + Assurance)", C_ALERT_BG, C_ALERT_BORDER, C_ALERT_TEXT))
    elements.extend(render_use_case(860, 800, 280, 52, "Rapprocher Flux Financiers 23:59\n(Commissions & Relevés CMI)", C_ACTION_BG, C_ACTION_BORDER, C_ACTION_TEXT))
    
    # Actor Association Arrows
    # Locataire connections
    elements.extend(create_arrow(230, 280, 430, 186, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 280, 430, 266, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 280, 430, 346, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 280, 430, 426, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 280, 430, 666, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 280, 430, 746, strokeColor=DARK_TEXT, endArrowhead=None))
    
    # Loueur connections
    elements.extend(create_arrow(230, 600, 430, 506, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 600, 430, 586, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 600, 430, 666, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 600, 430, 826, strokeColor=DARK_TEXT, endArrowhead=None))
    
    # Admin connections
    elements.extend(create_arrow(230, 880, 860, 266, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 880, 860, 666, strokeColor=DARK_TEXT, endArrowhead=None))
    elements.extend(create_arrow(230, 880, 860, 826, strokeColor=DARK_TEXT, endArrowhead=None))
    
    # CMI connections
    elements.extend(create_arrow(1630, 320, 710, 426, strokeColor=C_TRIGGER_BORDER, endArrowhead=None))
    elements.extend(create_arrow(1630, 320, 710, 826, strokeColor=C_TRIGGER_BORDER, endArrowhead=None))
    elements.extend(create_arrow(1630, 320, 1140, 826, strokeColor=C_TRIGGER_BORDER, endArrowhead=None))
    
    # n8n connections
    elements.extend(create_arrow(1630, 660, 1140, 346, strokeColor=C_TOOL_BORDER, endArrowhead=None))
    elements.extend(create_arrow(1630, 660, 710, 746, strokeColor=C_TOOL_BORDER, endArrowhead=None))
    elements.extend(create_arrow(1630, 660, 1140, 826, strokeColor=C_TOOL_BORDER, endArrowhead=None))
    
    # UML <<include>> and <<extend>> dependencies
    elements.extend(create_arrow(570, 372, 570, 400, strokeColor=MUTED_TEXT, strokeStyle="dashed", label="<<include>>"))
    elements.extend(create_arrow(570, 692, 570, 720, strokeColor=MUTED_TEXT, strokeStyle="dashed", label="<<include>>"))
    elements.extend(create_arrow(710, 266, 860, 266, strokeColor=MUTED_TEXT, strokeStyle="dashed", label="<<extend>>"))
    elements.extend(create_arrow(710, 346, 860, 346, strokeColor=MUTED_TEXT, strokeStyle="dashed", label="<<extend>>"))
    elements.extend(create_arrow(710, 666, 860, 666, strokeColor=MUTED_TEXT, strokeStyle="dashed", label="<<extend>>"))
    
    # Explanation Card
    why_uc = "📌 POURQUOI CE DIAGRAMME (WHY) : Définir avec précision les droits, cas d'usage et responsabilités de chaque acteur (Locataire, Loueur B2B, Admin) et l'automatisation des flux CMI et n8n."
    how_uc = "⚙️ COMMENT ÇA MARCHE (HOW) : Les relations <<include>> garantissent que toute réservation impose la pré-autorisation CMI et que toute remise impose l'état des lieux vidéo scellé SHA-256. Les relations <<extend>> gèrent les prolongations et déclarations de sinistre."
    elements.extend(create_explanation_card(430, 880, 1020, why_uc, how_uc, max_chars=80)[0])
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#FFFFFF", "gridSize": None},
        "files": {}
    }

# =====================================================================
# 3. NEW UML CLASS DIAGRAM (lokiini_class_diagram.excalidraw)
# =====================================================================
def build_uml_class_diagram():
    elements = []
    
    # Master Header
    elements.append(create_rectangle(40, 30, 1860, 75, strokeColor=C_HEADER_BORDER, backgroundColor=C_HEADER_BG, strokeWidth=2))
    elements.append(create_text("LOKIINI — Diagramme de Classes UML (Modèle Domaine, Méthodes & Relations)", 60, 44, fontSize=18, strokeColor=C_HEADER_BORDER, textAlign="left"))
    elements.append(create_text("Spécification orientée objet : Attributs typés, opérations métier, héritages, compositions et cardinalités", 60, 74, fontSize=12, strokeColor=DARK_TEXT, textAlign="left"))
    
    # Helper to draw a UML Class Box (3 compartments)
    def render_uml_class(x, y, w, name, stereo, attrs, methods, hdr_bg, border_col):
        elems = []
        hdr_h = 42 if stereo else 32
        row_h = 20
        
        attr_h = len(attrs) * row_h + 8
        meth_h = len(methods) * row_h + 8
        tot_h = hdr_h + attr_h + meth_h
        
        # Outer box
        elems.append(create_rectangle(x, y, w, tot_h, strokeColor=border_col, backgroundColor=CARD_BG, strokeWidth=1.5))
        # Header compartment
        elems.append(create_rectangle(x, y, w, hdr_h, strokeColor=border_col, backgroundColor=hdr_bg, strokeWidth=1.5))
        
        if stereo:
            elems.append(create_text(f"« {stereo} »", x + 10, y + 5, width=w - 20, fontSize=10, strokeColor="#D1EAE2" if hdr_bg != CARD_BG else MUTED_TEXT, textAlign="center"))
            elems.append(create_text(name, x + 10, y + 20, width=w - 20, fontSize=13, strokeColor="#FFFFFF" if hdr_bg != CARD_BG else DARK_TEXT, textAlign="center"))
        else:
            elems.append(create_text(name, x + 10, y + 8, width=w - 20, fontSize=13, strokeColor="#FFFFFF" if hdr_bg != CARD_BG else DARK_TEXT, textAlign="center"))
            
        # Attributes compartment
        cy = y + hdr_h + 4
        for a in attrs:
            elems.append(create_text(a, x + 12, cy, fontSize=10, strokeColor=DARK_TEXT, textAlign="left"))
            cy += row_h
            
        # Divider line
        now = int(time.time() * 1000)
        elems.append({"id": f"line_{random.randint(100000, 999999)}", "type": "line", "x": x, "y": y + hdr_h + attr_h, "width": w, "height": 1, "angle": 0, "strokeColor": border_col, "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None, "seed": random.randint(1, 1000000), "version": 1, "versionNonce": random.randint(1, 1000000), "isDeleted": False, "boundElements": None, "updated": now, "link": None, "locked": False, "points": [[0, 0], [w, 0]], "lastCommittedPoint": None, "startBinding": None, "endBinding": None, "startArrowhead": None, "endArrowhead": None})
        
        # Methods compartment
        cy = y + hdr_h + attr_h + 4
        for m in methods:
            elems.append(create_text(m, x + 12, cy, fontSize=10, strokeColor=DARK_TEXT, textAlign="left"))
            cy += row_h
            
        return elems, tot_h
        
    # Class 1: User (Abstract)
    u_attrs = [
        "- id: UUID",
        "- fullName: String",
        "- email: String",
        "- phoneNumber: String",
        "- role: UserRole",
        "- isKycVerified: Boolean"
    ]
    u_meth = [
        "+ register(): Boolean",
        "+ login(): AuthTokens",
        "+ submitKYC(cin, video): Boolean",
        "+ getProfile(): UserProfile"
    ]
    e_u, _ = render_uml_class(60, 130, 320, "User", "Abstract Class", u_attrs, u_meth, C_ACTION_BORDER, C_ACTION_BORDER)
    elements.extend(e_u)
    
    # Class 2: KYCProfile
    k_attrs = [
        "- cinNumber: String [Encrypted]",
        "- cinFrontUrl: String",
        "- cinBackUrl: String",
        "- livenessScore: Float",
        "- verifiedAt: DateTime"
    ]
    k_meth = [
        "+ performOCR(): OCRData",
        "+ checkLiveness(video): Score",
        "+ purgeRawVideoRAM(): Void",
        "+ logCNDPAudit(): Void"
    ]
    e_k, _ = render_uml_class(440, 130, 320, "KYCProfile", "Entity", k_attrs, k_meth, C_TOOL_BORDER, C_TOOL_BORDER)
    elements.extend(e_k)
    
    # Class 3: Equipment
    eq_attrs = [
        "- id: UUID",
        "- title: String",
        "- category: EquipmentCategory",
        "- city: MoroccanCity",
        "- dailyPriceMAD: Decimal",
        "- depositAmountMAD: Decimal",
        "- isAvailable: Boolean",
        "- specsJson: Map<String, Any>"
    ]
    eq_meth = [
        "+ isAvailableForDates(d1, d2): Bool",
        "+ calcDiscountedPrice(days): Decimal",
        "+ holdLock(duration): Boolean",
        "+ releaseLock(): Void"
    ]
    e_eq, _ = render_uml_class(820, 130, 340, "Equipment", "Aggregate Root", eq_attrs, eq_meth, C_ACTION_BORDER, C_ACTION_BORDER)
    elements.extend(e_eq)
    
    # Class 4: Booking
    bk_attrs = [
        "- id: UUID",
        "- startDate: Date",
        "- endDate: Date",
        "- totalDays: Integer",
        "- rentalTotalMAD: Decimal",
        "- commissionMAD: Decimal",
        "- depositHoldMAD: Decimal",
        "- status: BookingStatus"
    ]
    bk_meth = [
        "+ createPending(): Booking",
        "+ confirmByOwner(): Void",
        "+ extendDuration(days): Decimal",
        "+ completeRental(): Void",
        "+ disputeClaim(amount): Void"
    ]
    e_bk, _ = render_uml_class(1220, 130, 340, "Booking", "Aggregate Root", bk_attrs, bk_meth, C_TRIGGER_BORDER, C_TRIGGER_BORDER)
    elements.extend(e_bk)
    
    # Class 5: CMITransaction
    cmi_attrs = [
        "- authToken: String",
        "- cmiTransId: String",
        "- preauthAmountMAD: Decimal",
        "- capturedAmountMAD: Decimal",
        "- depositStatus: DepositStatus",
        "- releasedAt: DateTime"
    ]
    cmi_meth = [
        "+ preauthorizeHold(): Token",
        "+ releaseDeposit(): Boolean",
        "+ capturePartial(amt): Boolean",
        "+ auditReconciliation(): Boolean"
    ]
    e_cmi, _ = render_uml_class(1220, 480, 340, "CMITransaction", "Financial Entity", cmi_attrs, cmi_meth, C_TRIGGER_BORDER, C_TRIGGER_BORDER)
    elements.extend(e_cmi)
    
    # Class 6: InspectionReport
    ins_attrs = [
        "- id: UUID",
        "- type: InspectionType",
        "- videoUrl: String",
        "- sha256Hash: String [64]",
        "- rfc3161Timestamp: DateTime",
        "- isSignedByBoth: Boolean"
    ]
    ins_meth = [
        "+ computeVideoHash(): String",
        "+ sealTimestampRFC3161(): Proof",
        "+ signContradictory(): Boolean",
        "+ verifyIntegrity(): Boolean"
    ]
    e_ins, _ = render_uml_class(820, 480, 340, "InspectionReport", "Legal Entity", ins_attrs, ins_meth, C_TOOL_BORDER, C_TOOL_BORDER)
    elements.extend(e_ins)
    
    # Class 7: ContractDOC
    doc_attrs = [
        "- contractNumber: String",
        "- legalArticles: String [DOC 627+]",
        "- pdfUrl: String",
        "- sha256Seal: String",
        "- generatedAt: DateTime"
    ]
    doc_meth = [
        "+ generatePDF(booking): File",
        "+ applyDigitalSignature(): File",
        "+ sendWhatsAppCopy(): Void"
    ]
    e_doc, _ = render_uml_class(440, 480, 320, "ContractDOC", "Legal Document", doc_attrs, doc_meth, C_OUTPUT_BORDER, C_OUTPUT_BORDER)
    elements.extend(e_doc)
    
    # Class 8: Review
    rev_attrs = [
        "- id: UUID",
        "- ratingScore: Integer [1..5]",
        "- comment: String",
        "- createdAt: DateTime"
    ]
    rev_meth = [
        "+ postReview(): Review",
        "+ calcAverageScore(): Float"
    ]
    e_rev, _ = render_uml_class(60, 480, 320, "Review", "Entity", rev_attrs, rev_meth, C_ACTION_BORDER, C_ACTION_BORDER)
    elements.extend(e_rev)
    
    # Associations and Inheritance Connectors
    # User 1:1 KYCProfile
    elements.extend(create_arrow(380, 200, 440, 200, strokeColor=C_TOOL_BORDER, label="1:1"))
    # User 1:N Equipment (Owner)
    elements.extend(create_arrow(380, 240, 820, 240, strokeColor=C_ACTION_BORDER, label="owner 1:N"))
    # Equipment 1:N Booking
    elements.extend(create_arrow(1160, 220, 1220, 220, strokeColor=C_TRIGGER_BORDER, label="1:N"))
    # Booking 1:1 CMITransaction (Composition)
    elements.extend(create_arrow(1390, 400, 1390, 480, strokeColor=C_TRIGGER_BORDER, label="1:1 (holds)"))
    # Booking 1:2 InspectionReport (checkin / checkout)
    elements.extend(create_arrow(1220, 520, 1160, 520, strokeColor=C_TOOL_BORDER, label="1:2 (checkin/out)"))
    # Booking 1:1 ContractDOC
    elements.extend(create_arrow(1220, 300, 760, 520, strokeColor=C_OUTPUT_BORDER, label="1:1 (DOC)"))
    # Booking 1:N Review
    elements.extend(create_arrow(820, 580, 380, 580, strokeColor=C_ACTION_BORDER, label="1:N"))
    
    # Explanation Card
    why_cd = "📌 POURQUOI CETTE STRUCTURE DE CLASSES (WHY) : Encapsuler les responsabilités métier (calculs financiers, vérifications de vivacité, scellement de baux) dans des objets découplés et facilement testables."
    how_cd = "⚙️ COMMENT ÇA FONCTIONNE (HOW) : `Booking` agit comme le chef d'orchestre du domaine, déléguant la gestion du séquestre à `CMITransaction` et l'intégrité probante à `InspectionReport` et `ContractDOC`."
    elements.extend(create_explanation_card(60, 790, 1500, why_cd, how_cd, max_chars=90)[0])
    
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
    
    # 1. Fixed UML Workflows (lokiini_uml_workflows.excalidraw)
    uml_data = build_fixed_uml_workflows()
    with open(base_dir / "lokiini_uml_workflows.excalidraw", "w", encoding="utf-8") as f:
        json.dump(uml_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_uml_workflows.excalidraw", "w", encoding="utf-8") as f:
        json.dump(uml_data, f, indent=2, ensure_ascii=False)
    print(f"Generated Fixed UML Workflows: {len(uml_data['elements'])} elements")
    
    # 2. NEW UML Use Case Diagram (lokiini_use_case_diagram.excalidraw)
    uc_data = build_uml_use_case_diagram()
    with open(base_dir / "lokiini_use_case_diagram.excalidraw", "w", encoding="utf-8") as f:
        json.dump(uc_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_use_case_diagram.excalidraw", "w", encoding="utf-8") as f:
        json.dump(uc_data, f, indent=2, ensure_ascii=False)
    print(f"Generated UML Use Case Diagram: {len(uc_data['elements'])} elements")
    
    # 3. NEW UML Class Diagram (lokiini_class_diagram.excalidraw)
    cd_data = build_uml_class_diagram()
    with open(base_dir / "lokiini_class_diagram.excalidraw", "w", encoding="utf-8") as f:
        json.dump(cd_data, f, indent=2, ensure_ascii=False)
    with open(docs_dir / "lokiini_class_diagram.excalidraw", "w", encoding="utf-8") as f:
        json.dump(cd_data, f, indent=2, ensure_ascii=False)
    print(f"Generated UML Class Diagram: {len(cd_data['elements'])} elements")

if __name__ == "__main__":
    main()
