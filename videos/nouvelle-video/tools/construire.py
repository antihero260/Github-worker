#!/usr/bin/env python3
"""Montage « Les 3 niveaux de l'IA » (agents IA) : vertical 1080×1920, face caméra.
Base : assets/montage.mp4 (découpage de tools/decouper.py, étalonné). Les graphiques occupent le haut de l'image (le plafond),
le visage reste libre, les sous-titres mot à mot sont posés sur le t-shirt (y ≈ 1420).
Scènes : accroche (saturation d'outils IA) → niveau 1 prompting (conversation) → niveau 2 automatisation (scénario mail → résumé → CRM)
→ niveau 3 agents IA (objectif + étapes cochées par l'agent) → la révolution (répond → délègue).
Zoom alterné à chaque coupe (cache les sauts d'image), bruitages partout, deux beats (Creepin' puis Superhero, Metro Boomin).
Usage : python3 tools/construire.py  →  index.html + compositions/sous-titres.html ; puis npx hyperframes check / render."""
import json, subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
NL = "\n"
DEC = json.loads((ICI / "assets/decoupage.json").read_text())
BRUT = json.loads((ICI / "assets/transcript-brut.json").read_text())
BRUT = BRUT if isinstance(BRUT, list) else BRUT["words"]
DECAL = 0.18   # les temps de Parakeet arrivent ~0,2 s en avance sur le son (vérifié sur l'énergie)

# indices de mots par morceau (mêmes que tools/decouper.py)
PLAGES = [(15, 37), (103, 104), (105, 106), (115, 124), (153, 159), (164, 167), (191, 205), (239, 244), (250, 254), (257, 264),
          (287, 289), (310, 313), (339, 346), (363, 368), (381, 389), (408, 416), (427, 435), (451, 465)]
CORR = {33: "ChatGPT", 37: "automatisations ?", 104: "niveau :", 120: "ChatGPT,", 124: "répond,", 157: "nécessite", 167: "IA.",
        204: "résumer,", 239: "enregistrer", 263: "agents", 339: "et", 408: "vérifier", 451: "passer", 435: "révolution :"}
SUPPR = {34, 121}   # « GPT » fusionné dans « ChatGPT »

T_SEG, MOTS, IDX = [], [], {}
t = 0.0
for (m0, m1), o in zip(PLAGES, DEC):
    T_SEG.append(t)
    d = o["fin"] - o["debut"]
    for i in range(m0, m1 + 1):
        if i in SUPPR:
            continue
        s = min(max(BRUT[i]["start"] + DECAL - o["debut"], 0.0), d - 0.1) + t
        IDX[i] = len(MOTS)
        MOTS.append({"text": CORR.get(i, BRUT[i]["text"]), "start": round(s, 3), "orig": i})
        if i == 344:   # « nécessaires » : dit, mais absent de la transcription (vérifié avec Whisper)
            MOTS.append({"text": "nécessaires", "start": round(t + 196.30 - o["debut"], 3), "orig": None})
    t += d
FIN = round(t + 0.5, 2)
T_SEG.append(t)


def W(i):
    """temps (montage) du mot d'indice i de la transcription brute"""
    return MOTS[IDX[i]]["start"]


def r(x):
    return round(x, 3)


JS, HTML, SONS = [], [], []


def j(l):
    JS.append("      " + l)


SFX = ICI / "assets/sfx"
PICS = json.loads((SFX / "pics.json").read_text())


def son(t, nom, v=0.35, note="", sur_pic=True, d=None):
    p = PICS[nom]
    debut = max(0.0, t - (p["pic"] if sur_pic else 0))
    duree = min(p["duree"], d or 99, FIN - debut)
    if duree > 0.05:
        SONS.append((r(debut), nom, round(v * 0.75, 3), note, r(duree)))


TOURS = {}


def tour(liste):
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


POPS = ["pop-cartoon", "pop-bulle", "pop-click", "pop-sec"]
WH = ["whoosh-cine", "swoosh-court", "whoosh-pop", "balaie-rapide", "souffle-rapide"]


def apparait(sel, t, dy=60, s0=0.6, d=0.25):
    j(f'tl.fromTo("{sel}", {{ opacity: 0, y: {dy}, scale: {s0} }}, {{ opacity: 1, y: 0, scale: 1, duration: {d}, ease: "back.out(1.7)", immediateRender: false }}, {r(t)});')


def claque(sel, t, s0=2.2, d=0.14):
    j(f'tl.fromTo("{sel}", {{ opacity: 0, scale: {s0} }}, {{ opacity: 1, scale: 1, duration: {d}, ease: "power4.in", immediateRender: false }}, {r(t)});')


def cache(sel, t, d=0.18):
    j(f'tl.to("{sel}", {{ opacity: 0, scale: 0.85, duration: {d}, ease: "power2.in" }}, {r(t)});')


def flash(t, op=0.6, coul="#fff"):
    i = f"fl{len(HTML)}"
    HTML.append(f'<div id="{i}" class="flash" style="background: {coul}"></div>')
    j(f'tl.fromTo("#{i}", {{ opacity: {op} }}, {{ opacity: 0, duration: 0.25, immediateRender: false }}, {r(t)});')


# ================================================================ caméra : zoom alterné à chaque coupe + poussée lente + zooms de cinéma
ZOOMS = [1.0, 1.14, 1.0, 1.12, 1.0, 1.15, 1.0, 1.13, 1.0, 1.16, 1.0, 1.12, 1.0, 1.14, 1.0, 1.13, 1.0, 1.15]
for k in range(len(DEC)):
    a, b = T_SEG[k], T_SEG[k + 1]
    z = ZOOMS[k]
    j(f'tl.set("#coupe", {{ scale: {z} }}, {r(a)});')
    if k:
        j(f'tl.fromTo("#cam", {{ scale: 1.05 }}, {{ scale: 1, duration: 0.22, ease: "power3.out", immediateRender: false }}, {r(a)});')
        son(a, tour(WH), 0.16, f"raccord {k + 1}")
j(f'tl.fromTo("#pousse", {{ scale: 1 }}, {{ scale: 1.06, duration: {FIN}, ease: "none", immediateRender: false }}, 0);')


def zoom_cine(t, s=1.22, tenue=0.5, boom="impact-basse"):
    j(f'tl.to("#cine", {{ scale: {s}, duration: 0.15, ease: "power4.out" }}, {r(t - 0.04)});')
    j(f'tl.to("#cine", {{ scale: 1, duration: 0.5, ease: "power2.inOut" }}, {r(t + tenue)});')
    son(t - 0.04, tour(["zoom-impact", "zoom-in", "zoom-futur", "whoosh-cine"]), 0.3, "zoom de cinéma")
    son(t, boom, 0.24, "boom du zoom")


# ================================================================ 1. ACCROCHE : saturation d'outils IA, puis « ? », puis ChatGPT vs automatisations
OUTILS = ["ChatGPT", "Claude", "Gemini", "Grok", "Copilot", "Manus", "Operator", "AutoGPT", "n8n", "Make", "Zapier", "CrewAI", "LangChain",
          "Mistral", "Perplexity", "Devin", "Cursor", "Lindy", "Agents IA", "Assistants", "Workflows", "Bots", "ChatGPT", "Claude", "Gemini",
          "Agents IA", "n8n", "Make", "Zapier", "Copilot", "Manus", "Operator", "Agents IA", "Grok", "Mistral", "Devin", "Agents IA", "Cursor",
          "LangChain", "CrewAI"]
LOGO = {"ChatGPT": "logo-chatgpt-noir.svg", "Claude": "logo-claude.svg", "Gemini": "logo-gemini.svg", "Grok": "logo-grok-noir.svg"}  # logos blancs → version sombre sur fond blanc
COUL = ["#38BDF8", "#F2B705", "#FF6B6B", "#A78BFA", "#34D399", "#FB923C", "#F472B6", "#7DD3FC"]
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
t_s0, t_s1, t_asp = 0.0, W(21), W(22) - 0.05
HTML.append('<div id="sat-voile" class="flash" style="background: rgba(5,8,15,0.55); z-index: 11"></div>')
j(f'tl.set("#sat-voile", {{ opacity: 1 }}, 0); tl.to("#sat-voile", {{ opacity: 0, duration: 0.25 }}, {r(t_asp + 0.1)});')
for k, nom in enumerate(OUTILS):
    col, row = k % 5, k // 5
    x = 30 + col * 205 + ((row * 41 + k * 59) % 60) - 30
    y = 140 + row * 150 + ((k * 67) % 40) - 20
    rot = ((k * 43) % 34) - 17
    ic = f'<img src="assets/img/{LOGO[nom]}" alt="" />' if nom in LOGO else f'<i style="background: {COUL[k % len(COUL)]}"></i>'
    HTML.append(f'<div id="sat{k}" class="chip" data-layout-allow-overlap style="left: {x}px; top: {y}px; opacity: 0">{ic}{nom}</div>')
    t0 = t_s0 + (t_s1 - t_s0) * (k / len(OUTILS)) ** 0.85
    dx, dy = DIRS[k % 8]
    j(f'tl.fromTo("#sat{k}", {{ opacity: 0, x: {dx * 900}, y: {dy * 1500}, rotation: {rot * 4}, scale: 1.8 }}, '
      f'{{ opacity: 1, x: 0, y: 0, rotation: {rot}, scale: 1, duration: 0.22, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    j(f'tl.to("#sat{k}", {{ opacity: 0, scale: 0.1, x: {round((540 - x) * 0.9)}, y: {round((900 - y) * 0.9)}, rotation: {rot + 140}, duration: 0.24, ease: "power3.in" }}, {r(t_asp + 0.004 * k)});')
    if k % 3 == 0:
        son(t0, tour(["whoosh-pop", "swoosh-court", "souffle-rapide"] + POPS), 0.2, f"outil {nom}")
son(0.0, "swell-court", 0.3, "saturation d'outils IA")
son(t_asp, "aspiration", 0.32, "les outils sont aspirés")
HTML.append('<div id="h-agents" class="slam" data-layout-allow-overlap style="top: 600px; z-index: 13; opacity: 0">AGENTS IA</div>')
claque("#h-agents", W(19), 2.4)
son(W(19), "impact-futur", 0.36, "agents IA")
cache("#h-agents", t_asp)
HTML.append('<div id="h-q" class="slam" style="top: 230px; font-size: 380px; color: #38BDF8; opacity: 0">?</div>')
claque("#h-q", W(24), 3.0)
son(W(24), "coup-mystere", 0.4, "qu'est-ce que c'est")
j(f'tl.fromTo("#h-q", {{ rotation: -8 }}, {{ rotation: 8, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }}, {r(W(24) + 0.15)});')
cache("#h-q", W(31) - 0.1)
HTML.append('<div id="vs" class="vs" style="opacity: 0"><div id="vs-a" class="vs-carte" style="opacity: 0"><img src="assets/img/logo-chatgpt-noir.svg" alt="" /><b>ChatGPT</b></div>'
            '<div id="vs-v" class="vs-v" style="opacity: 0">VS</div>'
            '<div id="vs-b" class="vs-carte" style="opacity: 0"><svg viewBox="0 0 100 100" width="150" height="150"><g fill="none" stroke="#0B1220" stroke-width="9">'
            '<circle cx="50" cy="50" r="16"/><path d="M50 8v14M50 78v14M8 50h14M78 50h14M20 20l10 10M70 70l10 10M80 20l-10 10M30 70l-10 10"/></g></svg>'
            '<b>Automatisations</b></div></div>')
j(f'tl.set("#vs", {{ opacity: 1 }}, {r(W(31))});')
apparait("#vs-a", W(33), 120, 0.4)
son(W(33), tour(POPS), 0.4, "ChatGPT")
apparait("#vs-v", W(35), 0, 2.5, 0.18)
son(W(35), "impact-tambour", 0.36, "VS")
apparait("#vs-b", W(37), 120, 0.4)
son(W(37), tour(POPS), 0.4, "automatisations")
j(f'tl.to("#vs", {{ opacity: 0, y: -80, duration: 0.25 }}, {r(T_SEG[1] - 0.2)});')

# ================================================================ bandeau titre (après l'accroche) + jauge des 3 niveaux
HTML.append('<div id="titre" style="opacity: 0"><b>LES 3 NIVEAUX DE <i>L’IA</i></b></div>')
j(f'tl.fromTo("#titre", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out", immediateRender: false }}, {r(T_SEG[1])});')
NIV = [("1", "PROMPTING", T_SEG[1], "#38BDF8"), ("2", "AUTOMATISATION IA", T_SEG[5], "#F2B705"), ("3", "AGENTS IA", T_SEG[9], "#FF6B6B")]
for k, (n, nom, t0, c) in enumerate(NIV):
    barres = "".join(f'<i class="{"on" if q <= k else ""}" style="{"background: " + c if q <= k else ""}"></i>' for q in range(3))
    HTML.append(f'<div id="niv{n}" class="niveau" style="opacity: 0"><span style="background: {c}">NIVEAU {n}</span><b>{nom}</b><em>{barres}</em></div>')
    claque(f"#niv{n}", t0 + 0.05, 2.0, 0.16)
    son(t0 - 0.9, "riser-tech", 0.28, f"montée vers le niveau {n}", d=0.9)
    son(t0 + 0.05, "trailer-impact" if n == "3" else "impact-basse", 0.4, f"niveau {n}")
    flash(t0 + 0.05, 0.5, c)
    cache(f"#niv{n}", t0 + 1.55)
    HTML.append(f'<div id="mini{n}" class="niv-mini" style="opacity: 0"><span style="background: {c}">NIVEAU {n}</span> {nom}</div>')
    apparait(f"#mini{n}", t0 + 1.6, -30, 0.6, 0.25)
    son(t0 + 1.6, tour(POPS), 0.26, f"pastille niveau {n}")
    fin_n = NIV[k + 1][2] - 0.15 if k < 2 else T_SEG[16] - 0.1
    cache(f"#mini{n}", fin_n)
zoom_cine(T_SEG[1] + 0.05, 1.2)
zoom_cine(T_SEG[5] + 0.05, 1.2)
zoom_cine(T_SEG[9] + 0.05, 1.28, boom="trailer-impact")

# ================================================================ 2. NIVEAU 1 : la conversation ; chaque nouvelle tâche revient vers toi
t_c = W(115) - 0.1
HTML.append('<div id="chat" class="carte" style="opacity: 0"><div class="c-tete"><img src="assets/img/logo-chatgpt-noir.svg" alt="" /><b>ChatGPT</b></div>'
            '<div id="b1" class="bulle moi" style="opacity: 0">Écris un mail à mon client</div>'
            '<div id="b2" class="bulle ia" style="opacity: 0">Voici votre mail : « Bonjour Monsieur… »</div>'
            '<div id="b3" class="bulle moi" style="opacity: 0">Maintenant, résume ce PDF</div>'
            '<div id="b4" class="bulle moi" style="opacity: 0">Et planifie la réunion</div></div>')
apparait("#chat", t_c, 120, 0.7, 0.3)
son(t_c, tour(WH), 0.3, "la conversation arrive")
apparait("#b1", W(116), 40, 0.6)
son(W(116), "clavier-ordi", 0.3, "il tape sa demande", d=0.9)
apparait("#b2", W(124) - 0.15, 40, 0.6)
son(W(124) - 0.15, "notif-positive", 0.38, "ChatGPT répond")
j(f'tl.to(["#b1", "#b2"], {{ y: -120, opacity: 0, duration: 0.3 }}, {r(W(155))});')
apparait("#b3", W(155), 40, 0.6)
son(W(155), "clavier-ordi-2", 0.3, "nouvelle tâche", d=0.6)
apparait("#b4", W(157), 40, 0.6)
son(W(157), "clavier-tel", 0.3, "encore une tâche", d=0.5)
HTML.append('<div id="toi" class="tampon" style="top: 430px; opacity: 0">TOUJOURS TOI</div>')
claque("#toi", W(159) + 0.1, 2.6)
son(W(159) + 0.1, "buzz-faux", 0.36, "votre intervention")
j(f'tl.fromTo("#toi", {{ x: -10 }}, {{ x: 10, duration: 0.04, repeat: 7, yoyo: true, ease: "none", immediateRender: false }}, {r(W(159) + 0.25)});')
cache("#chat", T_SEG[5] - 0.12)
cache("#toi", T_SEG[5] - 0.12)

# ================================================================ 3. NIVEAU 2 : scénario fixe mail → résumé → CRM
ICONES = {
    "mail": '<svg viewBox="0 0 100 80" width="120" height="96"><rect x="6" y="8" width="88" height="64" rx="10" fill="#fff" stroke="#0B1220" stroke-width="7"/><path d="M8 14l42 32 42-32" fill="none" stroke="#0B1220" stroke-width="7" stroke-linejoin="round"/></svg>',
    "resume": '<svg viewBox="0 0 80 100" width="96" height="120"><rect x="6" y="6" width="68" height="88" rx="8" fill="#fff" stroke="#0B1220" stroke-width="7"/><path d="M20 30h40M20 48h40M20 66h24" stroke="#0B1220" stroke-width="7" stroke-linecap="round"/></svg>',
    "crm": '<svg viewBox="0 0 90 100" width="108" height="120"><ellipse cx="45" cy="18" rx="36" ry="12" fill="#fff" stroke="#0B1220" stroke-width="7"/><path d="M9 18v64c0 7 16 12 36 12s36-5 36-12V18" fill="#fff" stroke="#0B1220" stroke-width="7"/><path d="M9 50c0 7 16 12 36 12s36-5 36-12" fill="none" stroke="#0B1220" stroke-width="7"/></svg>',
}
NOEUDS = [("mail", "Recevoir un mail", W(200)), ("resume", "Le résumer", W(204)), ("crm", "L’enregistrer dans le CRM", W(239))]
HTML.append('<div id="flux" class="flux" style="opacity: 0"><div class="f-tete">SCÉNARIO DÉFINI À L’AVANCE</div><div class="f-ligne">'
            + "".join(f'<div id="nd{k}" class="noeud"><div class="n-vide">{k + 1}</div><div id="nd{k}-p" class="n-plein" style="opacity: 0">{ICONES[ic]}<b>{lab}</b></div></div>'
                      + (f'<div id="fl{k}" class="fleche"><i id="fl{k}-i"></i></div>' if k < 2 else "") for k, (ic, lab, _) in enumerate(NOEUDS))
            + '</div><div id="jeton" class="jeton" style="opacity: 0"></div></div>')
apparait("#flux", W(192), 120, 0.7, 0.3)
son(W(192), tour(WH), 0.3, "le scénario apparaît")
for k in range(3):
    apparait(f"#nd{k}", W(195) + 0.15 * k, 50, 0.5, 0.2)
    son(W(195) + 0.15 * k, tour(POPS), 0.3, f"case {k + 1}")
for k, (_, lab, tk) in enumerate(NOEUDS):
    j(f'tl.fromTo("#nd{k}-p", {{ opacity: 0, scale: 0.4, rotation: -10 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.28, ease: "back.out(2)", immediateRender: false }}, {r(tk)});')
    j(f'tl.to("#nd{k} .n-vide", {{ opacity: 0, duration: 0.1 }}, {r(tk)});')
    son(tk, "coche" if k else "notif-indice", 0.38, lab)
    if k < 2:
        j(f'tl.fromTo("#fl{k}-i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.3, ease: "power2.out", immediateRender: false }}, {r(NOEUDS[k + 1][2] - 0.2)});')
# l'IA exécute simplement le scénario : un jeton parcourt les cases, deux fois, sans décider de rien
j(f'tl.set("#jeton", {{ opacity: 1, x: 0 }}, {r(W(251))});')
j(f'tl.to("#jeton", {{ x: 600, duration: 1.0, ease: "none", repeat: 1 }}, {r(W(251))});')
j(f'tl.set("#jeton", {{ opacity: 0 }}, {r(W(251) + 2.05)});')
son(W(251), "scanner", 0.3, "l'IA exécute le scénario", d=1.5)
HTML.append('<div id="fixe" class="f-tete2" style="opacity: 0">L’IA EXÉCUTE, POINT.</div>')
j(f'tl.to("#flux .f-tete", {{ opacity: 0, duration: 0.1 }}, {r(W(254))});')
claque("#fixe", W(254), 1.8)
son(W(254), "verrou", 0.4, "simplement votre scénario")
cache("#flux", T_SEG[9] - 0.12)
cache("#fixe", T_SEG[9] - 0.12)

# ================================================================ 4. NIVEAU 3 : un objectif, l'agent décide lui-même des étapes
HTML.append('<div id="diff" class="slam rouge" data-layout-allow-overlap style="top: 560px; z-index: 13; opacity: 0">DIFFÉRENT</div>')
claque("#diff", W(289), 2.6)
son(W(289), "glitch-rugit", 0.36, "ici c'est différent")
j(f'tl.fromTo("#diff", {{ skewX: -14 }}, {{ skewX: 0, duration: 0.3, ease: "power2.out", immediateRender: false }}, {r(W(289))});')
cache("#diff", T_SEG[11] + 0.05)
ETAPES = [("Consulter vos mails", W(383)), ("Analyser les anciens échanges", W(386)), ("Vérifier votre calendrier", W(408)), ("Préparer un compte rendu", W(413))]
HTML.append('<div id="agent" class="carte agent" style="opacity: 0"><div class="a-obj"><svg viewBox="0 0 100 100" width="96" height="96">'
            '<circle cx="50" cy="50" r="42" fill="#FF6B6B"/><circle cx="50" cy="50" r="28" fill="#fff"/><circle cx="50" cy="50" r="14" fill="#FF6B6B"/></svg>'
            '<div><span>OBJECTIF</span><b id="obj-txt"><em id="obj-q">?</em><em id="obj-v" style="opacity: 0">Préparer le rendez-vous client</em></b></div></div>'
            '<div id="a-dec" class="a-dec" style="opacity: 0">L’AGENT DÉCIDE LUI-MÊME DES ÉTAPES</div>'
            + "".join(f'<div id="et{k}" class="etape" style="opacity: 0"><i id="et{k}-c" class="case"></i><b id="et{k}-t" style="opacity: 0.25">Étape {k + 1}…</b>'
                      f'<b id="et{k}-v" class="et-v" style="opacity: 0">{lab}</b></div>' for k, (lab, _) in enumerate(ETAPES)) + '</div>')
apparait("#agent", W(311), 120, 0.7, 0.3)
son(W(311), tour(WH), 0.3, "l'objectif arrive")
son(W(313), "impact-tambour", 0.36, "un objectif")
zoom_cine(W(313), 1.18)
apparait("#a-dec", W(341), 30, 0.6, 0.22)
son(W(341), "robot-scifi", 0.3, "l'agent décide")
for k in range(4):
    apparait(f"#et{k}", W(342) + 0.18 * k, 40, 0.6, 0.2)
    son(W(342) + 0.18 * k, tour(POPS), 0.28, f"étape {k + 1} (vide)")
j(f'tl.to("#obj-q", {{ opacity: 0, duration: 0.12 }}, {r(W(365))});')
j(f'tl.fromTo("#obj-v", {{ opacity: 0, x: 40 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out", immediateRender: false }}, {r(W(365))});')
son(W(365), "clavier-ordi", 0.3, "l'objectif s'écrit", d=0.8)
for k, (lab, tk) in enumerate(ETAPES):
    j(f'tl.to("#et{k}-t", {{ opacity: 0, duration: 0.1 }}, {r(tk)});')
    j(f'tl.fromTo("#et{k}-v", {{ opacity: 0, x: 30 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "power3.out", immediateRender: false }}, {r(tk)});')
    j(f'tl.to("#et{k}-c", {{ backgroundColor: "#34D399", borderColor: "#0B1220", duration: 0.1 }}, {r(tk + 0.35)});')
    j(f'tl.fromTo("#et{k}-c", {{ scale: 1.6 }}, {{ scale: 1, duration: 0.25, ease: "back.out(2)", immediateRender: false }}, {r(tk + 0.35)});')
    j(f'tl.fromTo("#et{k}", {{ backgroundColor: "rgba(52,211,153,0.35)" }}, {{ backgroundColor: "rgba(255,255,255,0)", duration: 0.6, immediateRender: false }}, {r(tk + 0.35)});')
    son(tk + 0.35, "coche", 0.4, f"étape cochée : {lab}")
HTML.append('<div id="fait" class="a-fait" style="opacity: 0">✓ TOUT FAIT PAR L’AGENT</div>')
j(f'tl.to("#a-dec", {{ opacity: 0, duration: 0.1 }}, {r(W(416) + 0.2)});')
claque("#fait", W(416) + 0.2, 1.8)
son(W(416) + 0.2, "mission-ok", 0.4, "tout est fait")
cache("#agent", T_SEG[16] - 0.12)
cache("#fait", T_SEG[16] - 0.12)

# ================================================================ 5. LA RÉVOLUTION : une IA qui répond → une IA à qui on délègue
HTML.append('<div id="revo" class="slam or" data-layout-allow-overlap style="top: 330px; z-index: 13; opacity: 0">LA RÉVOLUTION</div>')
claque("#revo", W(435), 2.6)
son(W(435), "trailer-impact", 0.42, "la révolution")
flash(W(435), 0.6, "#F2B705")
zoom_cine(W(435), 1.25, boom="trailer-impact-2")
j(f'tl.to("#revo", {{ scale: 0.6, y: -120, duration: 0.35, ease: "power3.inOut" }}, {r(W(451) - 0.1)});')
HTML.append('<div id="av" class="avap" style="opacity: 0"><div id="av-a" class="av-c gris" style="opacity: 0">UNE IA QUI <b>RÉPOND</b></div>'
            '<div id="av-f" class="av-f" style="opacity: 0">↓</div><div id="av-b" class="av-c or" style="opacity: 0">UNE IA À QUI ON <b>DÉLÈGUE</b></div></div>')
j(f'tl.set("#av", {{ opacity: 1 }}, {r(W(451))});')
apparait("#av-a", W(455), 50, 0.6)
son(W(455), tour(POPS), 0.36, "une IA qui répond")
apparait("#av-f", W(457), 0, 0.3, 0.2)
son(W(457), "swoosh-monte", 0.3, "flèche")
apparait("#av-b", W(463), 50, 0.6)
son(W(463), "power-up", 0.4, "on peut déléguer")
j(f'tl.fromTo("#av-b", {{ boxShadow: "0 0 0px rgba(242,183,5,0)" }}, {{ boxShadow: "0 0 80px rgba(242,183,5,0.9)", duration: 0.5, yoyo: true, repeat: 3, immediateRender: false }}, {r(W(463) + 0.2)});')
j(f'tl.fromTo("#fondu", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.45, immediateRender: false }}, {r(FIN - 0.45)});')


# ================================================================ sous-titres mot à mot
def sous_titres():
    groupes, cur = [], []
    for i, m in enumerate(MOTS):
        cur.append(i)
        if m["text"][-1] in ".,;:!?…" or len(cur) >= 3 or len(" ".join(MOTS[x]["text"] for x in cur)) >= 16:
            groupes.append(cur)
            cur = []
    if cur:
        groupes.append(cur)
    html, js = [], []
    for n, g in enumerate(groupes):
        t0 = MOTS[g[0]]["start"]
        t1 = MOTS[groupes[n + 1][0]]["start"] if n + 1 < len(groupes) else FIN - 0.45
        spans = []
        for i in g:
            spans.append(f'<span id="st-{i}" class="st-mot" style="display: none">{MOTS[i]["text"]}</span>')
            js.append(f'    tl.set("#st-{i}", {{ display: "inline-block" }}, {MOTS[i]["start"]});')
            js.append(f'    tl.fromTo("#st-{i}", {{ scale: 1.2 }}, {{ scale: 1, duration: 0.12, ease: "back.out(2)", immediateRender: false }}, {MOTS[i]["start"]});')
        html.append(f'    <div id="st-g{n}" class="st-groupe" data-layout-ignore style="opacity: 0"><div class="st-bandeau">{" ".join(spans)}</div></div>')
        js.append(f'    tl.set("#st-g{n}", {{ opacity: 1 }}, {t0});')
        js.append(f'    tl.set("#st-g{n}", {{ opacity: 0 }}, {round(t1 - 0.01, 3)});')
    page = f"""<!-- Sous-titres mot à mot (écrit par tools/construire.py). -->
<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .st-groupe {{ position: absolute; left: 40px; width: 1000px; top: 1420px; text-align: center; }}
    .st-bandeau {{ display: inline-block; background: #FFFFFF; color: #0B1220; font-family: "Anton", sans-serif; font-size: 84px;
      line-height: 1; padding: 14px 24px 12px; text-transform: uppercase; box-shadow: 0 18px 50px rgba(0, 0, 0, 0.55); transform: rotate(-1.5deg); }}
  </style>
  <div id="root" data-composition-id="sous-titres" data-width="1080" data-height="1920">
{NL.join(html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{NL.join(js)}
    window.__timelines["sous-titres"] = tl;
  </script>
</template>
"""
    (ICI / "compositions").mkdir(exist_ok=True)
    (ICI / "compositions/sous-titres.html").write_text(page, encoding="utf-8")


sous_titres()

# ================================================================ musiques (deux beats, ≈ 5–6 dB sous la voix qui est à −22 LUFS)
MUS = ICI / "assets/music"
COUPURE = T_SEG[9]
for nom, src, debut, d, fe, ff in (("piste-1.mp3", MUS / "creepin-long.wav", 0.0, COUPURE + 0.3, 0.05, 0.3),
                                   ("piste-2.mp3", MUS / "superhero.mp3", 0.0, FIN - COUPURE, 0.02, 1.2)):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                    f"atrim=start={debut}:duration={d:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-2:LRA=8,afade=t=in:d={fe},afade=t=out:st={max(0, d - ff):.3f}:d={ff}",
                    "-ar", "48000", "-b:a", "192k", str(MUS / nom)], check=True)
MUSIQUES = [f'<audio id="musique-1" src="assets/music/piste-1.mp3" data-start="0" data-duration="{r(COUPURE + 0.3)}" data-volume="0.30" data-track-index="20"></audio>',
            f'<audio id="musique-2" src="assets/music/piste-2.mp3" data-start="{r(COUPURE)}" data-duration="{r(FIN - COUPURE)}" data-volume="0.32" data-track-index="21"></audio>']
son(COUPURE, "trailer-impact-2", 0.36, "changement de musique")

_vus = set()
SONS[:] = [x for x in SONS if not ((x[0], x[1]) in _vus or _vus.add((x[0], x[1])))]
pistes, sons_html = {}, []
for n, (d0, f, v, note, dd) in enumerate(sorted(SONS), start=1):
    p = 30
    while pistes.get(p, -1) > d0 - 0.01:
        p += 1
    pistes[p] = d0 + dd
    sons_html.append(f'<audio id="sfx-{n:03d}" src="assets/sfx/{f}.mp3" data-start="{d0}" data-duration="{dd}" data-volume="{v}" data-track-index="{p}"></audio><!-- {note} -->')

CSS = """
      @font-face { font-family: "Anton"; src: url("assets/fonts/Anton-Regular.woff2") format("woff2"); }
      @font-face { font-family: "Inter Lf"; src: url("assets/fonts/Inter-ExtraBold.otf") format("opentype"); font-weight: 800; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
      #cine, #pousse, #cam, #coupe { position: absolute; inset: 0; transform-origin: 50% 54%; }
      #video { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }
      #vignette { position: absolute; inset: 0; z-index: 9; pointer-events: none; background: radial-gradient(ellipse 80% 70% at 50% 52%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.5) 100%); }
      #haut { position: absolute; left: 0; top: 0; width: 1080px; height: 900px; z-index: 9; pointer-events: none; background: linear-gradient(180deg, rgba(5,8,15,0.55), rgba(5,8,15,0) 100%); }
      .flash { position: absolute; inset: 0; opacity: 0; pointer-events: none; z-index: 40; }
      #fondu { position: absolute; inset: 0; opacity: 0; z-index: 60; background: #000; }
      #titre { position: absolute; left: 0; top: 0; width: 1080px; height: 270px; z-index: 30; display: flex; justify-content: center; padding-top: 120px;
        background: linear-gradient(180deg, rgba(0,0,0,0.9), rgba(0,0,0,0.5) 70%, rgba(0,0,0,0)); }
      #titre b { font-family: "Anton", sans-serif; font-weight: 400; font-size: 64px; color: #fff; letter-spacing: 1px; -webkit-text-stroke: 8px #000; paint-order: stroke fill; }
      #titre b i { font-style: normal; color: #38BDF8; }
      .chip { position: absolute; display: flex; align-items: center; gap: 10px; font-family: "Anton", sans-serif; font-size: 44px; color: #0B1220; background: #fff;
        border: 5px solid #0B1220; border-radius: 18px; padding: 6px 16px 2px; white-space: nowrap; z-index: 12; box-shadow: 0 12px 30px rgba(0,0,0,0.45); }
      .chip img { width: 46px; height: 46px; } .chip i { width: 22px; height: 22px; border-radius: 50%; display: inline-block; }
      .slam { position: absolute; left: 0; top: 420px; width: 1080px; text-align: center; font-family: "Anton", sans-serif; font-size: 170px; line-height: 1; color: #fff;
        -webkit-text-stroke: 14px #0B1220; paint-order: stroke fill; text-shadow: 0 0 50px rgba(56,189,248,0.7); z-index: 14; }
      .slam.rouge { color: #FF6B6B; text-shadow: 0 0 50px rgba(255,107,107,0.8); }
      .slam.or { color: #F2B705; font-size: 150px; text-shadow: 0 0 60px rgba(242,183,5,0.9); }
      .vs { position: absolute; left: 0; top: 300px; width: 1080px; height: 460px; z-index: 13; display: flex; align-items: center; justify-content: center; gap: 30px; }
      .vs-carte { width: 380px; height: 380px; background: #fff; border: 8px solid #0B1220; border-radius: 40px; display: flex; flex-direction: column; align-items: center;
        justify-content: center; gap: 20px; box-shadow: 0 24px 60px rgba(0,0,0,0.55); }
      .vs-carte img { width: 150px; height: 150px; }
      .vs-carte b { font-family: "Anton", sans-serif; font-weight: 400; font-size: 52px; color: #0B1220; }
      .vs-v { font-family: "Anton", sans-serif; font-size: 120px; color: #F2B705; -webkit-text-stroke: 10px #0B1220; paint-order: stroke fill; }
      .niveau { position: absolute; left: 0; top: 330px; width: 1080px; text-align: center; z-index: 16; }
      .niveau span { display: inline-block; font-family: "Anton", sans-serif; font-size: 70px; color: #0B1220; border: 7px solid #0B1220; border-radius: 22px;
        padding: 8px 30px 2px; transform: rotate(-3deg); box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
      .niveau b { display: block; margin-top: 18px; font-family: "Anton", sans-serif; font-weight: 400; font-size: 130px; line-height: 1; color: #fff;
        -webkit-text-stroke: 12px #0B1220; paint-order: stroke fill; }
      .niveau em { display: flex; justify-content: center; gap: 16px; margin-top: 22px; }
      .niveau em i { width: 120px; height: 26px; border-radius: 13px; background: rgba(255,255,255,0.25); border: 5px solid #0B1220; }
      .carte { position: absolute; left: 60px; top: 300px; width: 960px; height: 560px; background: #fff; border: 8px solid #0B1220; border-radius: 40px; z-index: 12;
        box-shadow: 0 30px 80px rgba(0,0,0,0.55); overflow: hidden; }
      .c-tete { display: flex; align-items: center; gap: 18px; padding: 22px 30px; border-bottom: 5px solid #E5E7EB; }
      .c-tete img { width: 60px; height: 60px; } .c-tete b { font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 44px; color: #0B1220; }
      .bulle { position: absolute; max-width: 700px; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 40px; line-height: 1.2; padding: 20px 28px; border-radius: 30px; }
      .bulle.moi { right: 30px; background: #38BDF8; color: #0B1220; border-bottom-right-radius: 8px; }
      .bulle.ia { left: 30px; background: #F3F4F6; color: #0B1220; border-bottom-left-radius: 8px; }
      #b1 { top: 140px; } #b2 { top: 270px; } #b3 { top: 300px; } #b4 { top: 420px; }
      .tampon { position: absolute; left: 0; top: 760px; width: 1080px; text-align: center; z-index: 15; font-family: "Anton", sans-serif; font-size: 96px;
        color: #fff; -webkit-text-stroke: 10px #0B1220; paint-order: stroke fill; }
      .tampon { color: #FF3B3B; transform: rotate(-4deg); }
      .tampon.jaune { color: #F2B705; } .tampon.vert { color: #34D399; }
      .flux { position: absolute; left: 40px; top: 300px; width: 1000px; height: 520px; background: #fff; border: 8px solid #0B1220; border-radius: 40px; z-index: 12;
        box-shadow: 0 30px 80px rgba(0,0,0,0.55); }
      .f-tete { text-align: center; padding: 26px 0 0; font-family: "Anton", sans-serif; font-size: 50px; color: #0B1220; letter-spacing: 1px; }
      .f-ligne { position: absolute; left: 30px; right: 30px; top: 130px; display: flex; align-items: center; justify-content: space-between; }
      .noeud { position: relative; width: 250px; height: 300px; }
      .n-vide { position: absolute; inset: 0; border: 6px dashed #9CA3AF; border-radius: 28px; display: flex; align-items: center; justify-content: center;
        font-family: "Anton", sans-serif; font-size: 110px; color: #D1D5DB; }
      .n-plein { position: absolute; inset: 0; background: #FEF3C7; border: 6px solid #0B1220; border-radius: 28px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; gap: 14px; padding: 10px; text-align: center; }
      .n-plein b { font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 32px; line-height: 1.15; color: #0B1220; }
      .fleche { width: 70px; height: 14px; background: #E5E7EB; border-radius: 7px; overflow: hidden; }
      .fleche i { display: block; width: 100%; height: 100%; background: #0B1220; transform-origin: 0 50%; }
      .jeton { position: absolute; left: 140px; top: 455px; width: 44px; height: 44px; border-radius: 50%; background: #F2B705; border: 6px solid #0B1220;
        box-shadow: 0 0 30px #F2B705; }
      .agent { padding: 26px 34px; height: 600px; top: 290px; }
      .a-obj { display: flex; align-items: center; gap: 24px; padding-bottom: 18px; border-bottom: 5px solid #E5E7EB; }
      .a-obj span { display: block; font-family: "Anton", sans-serif; font-size: 40px; color: #FF6B6B; letter-spacing: 2px; }
      .a-obj b { position: relative; display: block; height: 56px; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 44px; color: #0B1220; }
      .a-obj b em { position: absolute; left: 0; top: 0; font-style: normal; white-space: nowrap; }
      .a-dec { margin: 16px 0 8px; font-family: "Anton", sans-serif; font-size: 36px; color: #6B7280; letter-spacing: 1px; }
      .etape { position: relative; display: flex; align-items: center; gap: 22px; height: 82px; border-radius: 18px; padding: 0 12px; }
      .case { width: 54px; height: 54px; border: 6px solid #9CA3AF; border-radius: 14px; flex: none; background: #fff; }
      .etape b { font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 42px; color: #0B1220; }
      .et-v { position: absolute; left: 88px; }
      .niv-mini { position: absolute; left: 0; top: 200px; width: 1080px; text-align: center; z-index: 31; font-family: "Anton", sans-serif; font-size: 40px;
        color: #fff; -webkit-text-stroke: 6px #000; paint-order: stroke fill; }
      .niv-mini span { display: inline-block; color: #0B1220; -webkit-text-stroke: 0; border: 4px solid #0B1220; border-radius: 12px; padding: 2px 14px 0; margin-right: 8px; }
      .f-tete2 { position: absolute; left: 40px; top: 318px; width: 1000px; text-align: center; z-index: 13; font-family: "Anton", sans-serif; font-size: 54px;
        color: #0B1220; } .f-tete2 { background: #F2B705; border-radius: 0; }
      .a-fait { position: absolute; left: 94px; top: 425px; z-index: 13; font-family: "Anton", sans-serif; font-size: 40px; color: #fff; background: #34D399;
        border: 5px solid #0B1220; border-radius: 14px; padding: 4px 18px 0; }
      .avap { position: absolute; left: 0; top: 400px; width: 1080px; z-index: 13; text-align: center; }
      .av-c { display: inline-block; font-family: "Anton", sans-serif; font-size: 70px; color: #0B1220; background: #fff; border: 7px solid #0B1220; border-radius: 26px;
        padding: 10px 30px 4px; box-shadow: 0 18px 44px rgba(0,0,0,0.5); }
      .av-c.gris { background: #E5E7EB; color: #4B5563; } .av-c.gris b { color: #4B5563; text-decoration: line-through; text-decoration-thickness: 8px; }
      .av-c.or { background: #F2B705; } .av-c b { font-weight: 400; }
      .av-f { font-family: "Anton", sans-serif; font-size: 90px; color: #fff; -webkit-text-stroke: 8px #0B1220; paint-order: stroke fill; line-height: 1.1; }
"""
page = f"""<!doctype html>
<html lang="fr" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="1080" data-height="1920">
      <div id="cine"><div id="pousse"><div id="cam"><div id="coupe">
        <video id="video" class="clip" src="assets/montage.mp4" data-start="0" data-duration="{r(T_SEG[-1])}" data-media-start="0" data-has-audio="true" data-track-index="1" playsinline></video>
      </div></div></div></div>
      <div id="haut"></div>
      <div id="vignette"></div>
{NL.join("      " + h for h in HTML)}
      <div id="sous-titres" data-composition-id="sous-titres" data-composition-src="compositions/sous-titres.html" data-start="0" data-duration="{FIN}" data-track-index="3"
        data-width="1080" data-height="1920" style="position: absolute; inset: 0; z-index: 35"></div>
      <div id="fondu"></div>
{NL.join("      " + m for m in MUSIQUES)}
{NL.join("      " + s for s in sons_html)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{NL.join(JS)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ICI / "index.html").write_text(page, encoding="utf-8")
print(f"durée {FIN} s, {len(DEC)} morceaux, {len(MOTS)} mots, {len(SONS)} bruitages")
