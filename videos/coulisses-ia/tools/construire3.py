#!/usr/bin/env python3
"""Vidéo « Comment je crée mes vidéos avec l'IA » v3 (face caméra de l'utilisateur), vertical 1080×1920.

v3 : fond de studio uni et sombre (une teinte par passage) et personne éclairée/étalonnée, cuits dans assets/montage/studio.mp4
par tools/composer-studio.py (ce script écrit d'abord assets/montage/passages.json) ; plus de halo autour de la personne,
plus de vidéos en arrière-plan.

Entrées : assets/montage/parole.mp4 (meilleures prises collées par tools/assembler.py, silences coupés),
assets/montage/segments.json (coupes), assets/mots.json (mots alignés sur script.txt).
Habillage : recadrage alterné à chaque coupe (jump cuts), accroche en rafale d'extraits de ses vidéos, messages reçus,
logos (Claude, ChatGPT, Grok, Gemini), carte HyperFrames, « code ✓ / vidéo ✗ », schéma références + code → vidéo,
prix, « le modèle = la clé », Opus 5.5 / Fable 5.2, exemples 3D / 2D / isométrique, abonne-toi. Sous-titres mot à mot.
Relancer ce script ÉCRASE index.html et compositions/sous-titres.html.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent.parent
MOTS = json.loads((ICI / "assets/mots.json").read_text())
SEG = json.loads((ICI / "assets/montage/segments.json").read_text())
D = SEG["phrases"][1]["debut_montage"] - 4.53  # décalage depuis la v3 (début de la 1re phrase repris plus tôt)
D2 = SEG["phrases"][5]["debut_montage"] - 29.69  # décalage depuis la v8 (« HyperFrames intervient » repris dans une autre prise)


def DD(x):
    """temps relevé sur l'ancien montage (v3) → nouveau montage"""
    return x + D + (D2 if x + D > 27.5 else 0)
FIN = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ICI / "assets/montage/parole.mp4")],
                                 capture_output=True, text=True).stdout) + 0.6, 2)
TERRA, CREME, NUIT, CIEL = "#D97757", "#F0EEE6", "#0B1220", "#38BDF8"
NL = "\n"


def T(i):
    return MOTS[i]["start"]


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
WH = ["whoosh-cine", "swoosh-court", "whoosh-pop", "balaie-rapide", "fouet"]

# ================================================================ 1. CAMÉRA : décors adaptés, suivi du visage, poussées de tension, zooms sur les mains
VISAGE = json.loads((ICI / "assets/montage/visage.json").read_text())
GESTES = json.loads((ICI / "assets/montage/gestes.json").read_text())
PASSAGES = [(0.0, "nuit"), (T(15), "terre"), (T(40), "sarcelle"), (T(49), "graphite"), (T(78), "indigo"), (T(99), "ardoise"),
            (T(137), "bordeaux"), (T(161), "petrole"), (T(183), "sarcelle"), (T(199), "nuit")]
(ICI / "assets/montage/passages.json").write_text(json.dumps([[round(t, 3), n] for t, n in PASSAGES]))
for t, n in PASSAGES[1:]:
    son(t, tour(["whoosh-cine", "swoosh-vitesse", "whoosh-tunnel"]), 0.16, f"nouveau fond {n}")
# suivi du visage (la caméra garde le visage au centre, avec un léger retard)
kf = []
from scipy.ndimage import median_filter
VX = median_filter(np.clip(np.array([v[1] for v in VISAGE], float), 380, 700), 5)
VY = median_filter(np.clip(np.array([v[2] for v in VISAGE], float), 900, 1150), 5)
for (t, _, _), x, y in zip(VISAGE, VX, VY):
    if t < T(7):
        continue
    dx, dy = np.clip((540 - x) * 0.45, -55, 55), np.clip((1000 - y) * 0.4, -50, 50)
    kf.append(f'tl.to("#suivi", {{ x: {round(dx)}, y: {round(dy)}, duration: 0.5, ease: "sine.inOut" }}, {t});')
for l in kf:
    j(l)
# poussée lente sur chaque phrase (tension), coup de zoom à chaque coupe
for k, ph in enumerate(SEG["phrases"]):
    d0, dd = ph["debut_montage"], ph["duree"]
    j(f'tl.fromTo("#pousse", {{ scale: {1.0 if k % 2 == 0 else 1.06} }}, {{ scale: {1.12 if k % 2 == 0 else 1.18}, duration: {r(dd)}, ease: "power1.in", immediateRender: false }}, {r(d0)});')
for k, c in enumerate(SEG["coupes"]):
    if k:
        j(f'tl.fromTo("#coup", {{ scale: 1.06 }}, {{ scale: 1, duration: 0.18, ease: "power3.out", immediateRender: false }}, {r(c["t"])});')
        son(c["t"], tour(["swoosh-court", "balaie-petit", "whoosh-pop"]), 0.1, "coupe")


def zoom_main(t, hx, hy, s=1.38, d=0.85):
    """La caméra plonge vers l'objet apparu dans la main, puis ressort."""
    ox, oy = round(hx / 10.8, 1), round(hy / 19.2, 1)
    j(f'tl.set("#zoomh", {{ transformOrigin: "{ox}% {oy}%" }}, {r(t)});')
    j(f'tl.to("#zoomh", {{ scale: {s}, duration: 0.28, ease: "power3.out" }}, {r(t)});')
    j(f'tl.to("#zoomh", {{ scale: 1, duration: 0.35, ease: "power3.inOut" }}, {r(t + d)});')
    son(t, tour(["zoom-impact", "zoom-futur", "zoom-in"]), 0.38, "zoom sur la main")


MAINS = []


def dans_la_main(oid, html, t, hx, hy, t_fin, zoom=True, monte=200):
    """Un objet naît dans la main (petit, lumineux), monte au-dessus d'elle, la caméra zoome dessus."""
    hx, hy = min(max(hx, 260), 760), max(hy, 1700)
    monte = max(40, monte - 150)  # les objets restent sous les sous-titres (descendus à 1420 px)
    hx, hy = -60 + hx * 1200 / 1080, -106 + hy * 1200 / 1080  # repère de la vidéo studio agrandie
    MAINS.append(f'<div id="{oid}-eclat" class="mg-eclat" style="opacity: 0"></div>')
    j(f'tl.set("#{oid}-eclat", {{ x: {round(hx - 160)}, y: {round(hy - 220)} }}, {r(t)});')
    j(f'tl.fromTo("#{oid}-eclat", {{ opacity: 1, scale: 0.2 }}, {{ opacity: 0, scale: 1.7, duration: 0.5, ease: "power2.out", immediateRender: false }}, {r(t)});')
    MAINS.append(f'<div id="{oid}" class="main-obj" style="left: {round(hx)}px; top: {round(hy)}px; opacity: 0">{html}</div>')
    j(f'tl.fromTo("#{oid}", {{ opacity: 0, scale: 0.1, y: 0, rotation: -25 }}, {{ opacity: 1, scale: 1, y: -{monte}, rotation: 0, duration: 0.42, ease: "back.out(1.8)", immediateRender: false }}, {r(t)});')
    j(f'tl.to("#{oid}", {{ y: -{monte + 30}, duration: 0.6, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {r(t + 0.45)});')
    j(f'tl.to("#{oid}", {{ opacity: 0, scale: 0.6, duration: 0.2 }}, {r(t_fin)});')
    son(t, tour(["magie", "scintille-whoosh", "power-up"]), 0.42, f"objet dans la main {oid}")
    if zoom:
        zoom_main(t + 0.1, hx, hy - monte)


def apparait(sel, t, dy=60, s0=0.6, d=0.22):
    j(f'tl.fromTo("{sel}", {{ opacity: 0, y: {dy}, scale: {s0} }}, {{ opacity: 1, y: 0, scale: 1, duration: {d}, ease: "back.out(2)", immediateRender: false }}, {r(t)});')


def claque(sel, t, s0=2.0, d=0.14):
    j(f'tl.fromTo("{sel}", {{ opacity: 0, scale: {s0} }}, {{ opacity: 1, scale: 1, duration: {d}, ease: "power4.in", immediateRender: false }}, {r(t)});')


def cache(sel, t, d=0.15):
    j(f'tl.to("{sel}", {{ opacity: 0, scale: 0.8, duration: {d} }}, {r(t)});')


def flash(t, op=0.7):
    i = f"fl{len(HTML)}"
    HTML.append(f'<div id="{i}" class="flash"></div>')
    j(f'tl.fromTo("#{i}", {{ opacity: {op} }}, {{ opacity: 0, duration: 0.18, immediateRender: false }}, {r(t)});')


def video_plein(vid, src, t0, t1, depart=0.3):
    HTML.append(f'<div id="{vid}" class="plein" style="opacity: 0"><video id="{vid}-v" class="clip" src="{src}" data-start="{r(t0)}" '
                f'data-duration="{r(t1 - t0 + 0.04)}" data-media-start="{depart}" data-track-index="{5 + len(HTML) % 3}" muted playsinline></video></div>')
    if "exemples/" in src:
        h = HTML[-1]
        debut_v = h.index("<video")
        fin_v = h.index("</video>") + len("</video>")
        rot = (-4, 3, -2, 4)[len(HTML) % 4]
        HTML[-1] = (h[:debut_v].replace('class="plein"', 'class="plein ex-fond"') + f'<div class="tel-ex" style="transform: rotate({rot}deg)">'
                    + h[debut_v:fin_v] + '</div></div>')
    j(f'tl.set("#{vid}", {{ opacity: 1 }}, {r(t0)});')
    j(f'tl.fromTo("#{vid}", {{ scale: 1.2 }}, {{ scale: 1.02, duration: {r(t1 - t0)}, ease: "power2.out", immediateRender: false }}, {r(t0)});')
    j(f'tl.set("#{vid}", {{ opacity: 0 }}, {r(t1)});')


# ================================================================ 2. ACCROCHE : on tape « Fais-moi une vidéo » → ses vraies vidéos explosent plein écran, une par mot
#   → « 1 PROMPT = 1 VIDÉO » → tout rentre dans la main
QH = "Fais-moi une vidéo 🔥"
lettres = "".join(f'<span id="hq{i}" style="opacity: 0">{c}</span>' for i, c in enumerate(QH))
HTML.append(f'<div id="h-chat" class="plein h-chat" style="opacity: 1"><div class="hc-boite"><img src="assets/img/logo-claude.svg" alt="" />'
            f'<div class="hc-texte">{lettres}<i id="hc-curseur">|</i></div><b id="hc-envoi">↑</b></div></div>')
for i in range(len(QH)):
    j(f'tl.set("#hq{i}", {{ opacity: 1 }}, {r(0.04 + 0.024 * i)});')
son(0.02, "clavier-ordi", 0.32, "on tape le prompt", d=0.5)
j(f'tl.fromTo("#hc-envoi", {{ scale: 1 }}, {{ scale: 1.5, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }}, {r(T(1) - 0.12)});')
son(T(1) - 0.12, "pop-click", 0.36, "envoyer")
j(f'tl.set("#h-chat", {{ opacity: 0 }}, {r(T(1))});')
# plans sans texte incrusté (sinon leurs sous-titres se mélangent aux nôtres) : son edit Claude, grille rétro, route néon, tunnel
# SATURATION : des vidéos arrivent de tous les côtés, dans toutes les positions, jusqu'à remplir l'écran
TUILES = [("assets/exemples/edit-claude.mp4", 1), ("assets/magie/retro-soleil.mp4", 0), ("assets/exemples/site-3d-vertical.mp4", 1),
          ("assets/accroche/supernova.mp4", 0), ("assets/exemples/enveloppes.mp4", 1), ("assets/fonds/neon-3d-route.mp4", 0),
          ("assets/exemples/salaire-15.mp4", 1), ("assets/accroche/passage-cercles.mp4", 0), ("assets/exemples/classement-ia-vertical.mp4", 1),
          ("assets/accroche/neon-violet-3d.mp4", 0), ("assets/exemples/tontine-epargne.mp4", 1), ("assets/accroche/planete-rocheuse.mp4", 0),
          ("assets/exemples/liste-depenser-moins.mp4", 1), ("assets/accroche/explosion-particules.mp4", 0), ("assets/exemples/effet-levier.mp4", 1),
          ("assets/accroche/lasers.mp4", 0), ("assets/exemples/site-anime-vertical.mp4", 1), ("assets/accroche/nebuleuse.mp4", 0),
          ("assets/exemples/edit-claude.mp4", 1), ("assets/magie/retro-soleil.mp4", 0)]
# points d'arrivée qui couvrent tout l'écran (centres), tailles et rotations variées
ARR = [(540, 960), (230, 420), (850, 380), (200, 1380), (880, 1420), (540, 560), (520, 1500), (180, 820), (900, 900), (380, 1160),
       (720, 1180), (540, 240), (260, 1720), (840, 1740), (130, 300), (960, 160), (640, 780), (420, 680), (760, 1560), (340, 1000)]
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
t_s0, t_s1 = T(1), T(6)
for k, (src, vert) in enumerate(TUILES):
    w = (300 + (k * 37) % 120) if vert else (440 + (k * 53) % 140)
    h = round(w * 16 / 9) if vert else round(w * 9 / 16)
    cx, cy = ARR[k]
    dx, dy = DIRS[k % 8]
    rot = ((k * 47) % 50) - 25
    t0 = t_s0 + (t_s1 - t_s0) * (k / len(TUILES)) ** 0.85
    HTML.append(f'<div id="ht{k}" class="h-tuile" style="left: {cx - w // 2}px; top: {cy - h // 2}px; width: {w}px; height: {h}px; opacity: 0">'
                f'<video id="ht{k}-v" class="clip" src="{src}" data-start="{r(t0)}" data-duration="{r(T(7) + 0.4 - t0)}" data-media-start="{0.3 + (k % 5) * 0.5}" '
                f'data-track-index="{40 + k}" muted playsinline></video></div>')
    j(f'tl.set("#ht{k}", {{ opacity: 1 }}, {r(t0)});')
    j(f'tl.fromTo("#ht{k}", {{ x: {dx * 1300}, y: {dy * 2100}, rotation: {rot * 3}, scale: 1.6 }}, '
      f'{{ x: 0, y: 0, rotation: {rot}, scale: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    if k % 2 == 0:
        son(t0, tour(["whoosh-cine", "swoosh-court", "glitch-court", "whoosh-pop", "souffle-rapide", "balaie-rapide"]), 0.14, f"vidéo {k} arrive")
    # aspirées dans la main
    j(f'tl.to("#ht{k}", {{ x: {380 - cx}, y: {1600 - cy}, scale: 0.03, rotation: {rot + 180}, duration: 0.3, ease: "power3.in" }}, {r(T(7) - 0.05 + 0.012 * k)});')
    j(f'tl.set("#ht{k}", {{ opacity: 0 }}, {r(T(7) + 0.3 + 0.012 * k)});')
HTML.append('<div id="h-tag" class="slam" data-layout-allow-overlap style="top: 760px; z-index: 13; opacity: 0">1 PROMPT<br>= 1 VIDÉO</div>')
claque("#h-tag", T(2), 2.4)
cache("#h-tag", T(7) - 0.06)
son(T(1), "trailer-impact", 0.22, "les vidéos déferlent")
son(T(1), "swell-court", 0.24, "saturation")
HTML.append('<div id="h-eclat" class="mg-eclat" style="opacity: 0"></div>')
j(f'tl.set("#h-eclat", {{ x: 220, y: 1440 }}, {r(T(7) + 0.28)});')
j(f'tl.fromTo("#h-eclat", {{ opacity: 1, scale: 0.3 }}, {{ opacity: 0, scale: 1.8, duration: 0.45, ease: "power2.out", immediateRender: false }}, {r(T(7) + 0.28)});')
son(T(7) - 0.05, "aspiration", 0.32, "les vidéos sont aspirées dans la main")
son(T(7) + 0.3, "impact-basse", 0.28, "retour face caméra")

# ================================================================ 3. « certains d'entre vous m'ont contacté » : messages reçus
MSG = [("Tu fais comment tes vidéos ?", T(8)), ("C’est quelle appli ?? 🔥", T(11)), ("Tu peux m’apprendre ?", T(13))]
for k, (txt, t) in enumerate(MSG):
    HTML.append(f'<div id="msg{k}" class="msg" style="top: {360 + k * 135}px; left: {60 + (k % 2) * 140}px; opacity: 0"><b>Nouveau message</b>{txt}</div>')
    apparait(f"#msg{k}", t, 50, 0.7)
    son(t, tour(["notif-indice", "notif-positive", "notif-magique"]), 0.42, "message reçu")
    cache(f"#msg{k}", T(17) - 0.1)

# ================================================================ 4. Claude, Opus 5.5 ; ChatGPT, Grok, Gemini…
LOGOS = [("logo-claude.svg", "Claude", T(18), 70), ("logo-chatgpt.svg", "ChatGPT", T(29), 290), ("logo-grok.svg", "Grok", T(30), 510),
         ("logo-gemini.svg", "Gemini", T(31), 730)]
for k, (f, n, t, x) in enumerate(LOGOS):
    HTML.append(f'<div id="lg{k}" class="logo-chip" style="left: {x}px; top: 400px; opacity: 0"><img src="assets/img/{f}" alt="" /><span>{n}</span></div>')
    apparait(f"#lg{k}", t, 80, 0.3)
    son(t, tour(POPS), 0.42, f"logo {n}")
    cache(f"#lg{k}", T(33))
HTML.append('<div id="opus" class="tag" style="left: 70px; top: 640px; opacity: 0">OPUS 5.5</div>')
claque("#opus", T(20), 1.8)
son(T(20), "impact-tambour", 0.38, "Opus 5.5")
cache("#opus", T(29) - 0.05)
# saturation : l'écran se remplit de modèles d'IA
SAT = ["DeepSeek", "Mistral", "Llama", "Qwen", "Copilot", "Perplexity", "Kimi", "Midjourney", "Sora", "Veo", "Kling", "Runway", "Suno",
       "Flux", "Gemma", "Phi", "GLM", "Hailuo", "Seedance", "Pika", "Luma", "Ideogram", "MiniMax", "Codestral", "Command R", "Ernie",
       "Nova", "Yi", "Claude", "ChatGPT", "Gemini", "Grok", "DeepSeek", "Mistral", "Llama", "Qwen", "Sora", "Veo", "Kling", "Midjourney",
       "Perplexity", "Copilot", "Flux", "Runway", "Gemma", "Hailuo", "Pika", "Luma", "Suno", "Seedance", "Ideogram", "Phi", "GLM", "Yi",
       "Nova", "Kimi", "MiniMax", "Ernie", "Claude", "ChatGPT"]
LOGO_SAT = {"Claude": "logo-claude.svg", "ChatGPT": "logo-chatgpt.svg", "Gemini": "logo-gemini.svg", "Grok": "logo-grok.svg"}
COUL = ["#38BDF8", "#F2B705", "#FF6B6B", "#7DD3FC", "#A78BFA", "#34D399", "#FB923C", "#F472B6"]
HTML.append('<div id="sat-voile" class="flash" style="background: rgba(5,8,15,0.55); z-index: 11"></div>')
j(f'tl.fromTo("#sat-voile", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, immediateRender: false }}, {r(T(33))});')
j(f'tl.to("#sat-voile", {{ opacity: 0, duration: 0.2 }}, {r(T(40) - 0.12)});')
t_sat0, t_sat1 = T(33), T(39)
for k, nom in enumerate(SAT):
    col, row = k % 5, k // 5
    x = 30 + col * 205 + ((row * 37 + k * 53) % 60) - 30
    y = 170 + row * 128 + ((k * 71) % 40) - 20  # 13 rangées : tout l'écran est rempli
    rot = ((k * 37) % 30) - 15
    ic = f'<img src="assets/img/{LOGO_SAT[nom]}" alt="" />' if nom in LOGO_SAT else f'<i style="background: {COUL[k % len(COUL)]}"></i>'
    HTML.append(f'<div id="sat{k}" class="sat-chip" data-layout-allow-overlap style="left: {x}px; top: {y}px; opacity: 0; transform: rotate({rot}deg)">{ic}{nom}</div>')
    t0 = t_sat0 + (t_sat1 - t_sat0) * (k / len(SAT)) ** 0.8
    j(f'tl.fromTo("#sat{k}", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.in", immediateRender: false }}, {r(t0)});')
    j(f'tl.to("#sat{k}", {{ opacity: 0, scale: 0.2, x: {round((540 - x) * 0.8)}, y: {round((960 - y) * 0.8)}, duration: 0.22, ease: "power3.in" }}, {r(T(40) - 0.18)});')
    if k % 4 == 0:
        son(t0, tour(POPS), 0.26, f"modèle {nom}")
son(t_sat0, "swell-court", 0.3, "saturation de modèles")
son(T(40) - 0.18, "aspiration", 0.32, "les modèles sont aspirés")
HTML.append('<div id="autres" class="slam" data-layout-allow-overlap style="top: 860px; z-index: 13; opacity: 0">+ BIEN<br>D’AUTRES</div>')
claque("#autres", T(34), 2.2)
son(T(34), "impact-basse", 0.3, "et bien d'autres")
cache("#autres", T(40) - 0.12)

# ================================================================ 5. Le game changer : HyperFrames
cap = ICI / "assets/captures/hyperframes-accueil.mp4"
fen = (f'<video id="hf-v" class="clip" src="assets/captures/hyperframes-accueil.mp4" data-start="{r(T(44))}" data-duration="{r(T(49) - T(44) + 0.3)}" '
       f'data-media-start="0.0" data-track-index="9" muted playsinline></video>') if cap.exists() else ""
HTML.append(f'<div id="hf" class="carte-hf" style="opacity: 0"><div class="hf-tete"><img src="assets/img/logo-heygen.png" alt="" /><b>HYPERFRAMES</b></div>'
            f'<span>une skill · gratuite et open source</span>{("<div class=" + chr(34) + "hf-fen" + chr(34) + ">" + fen + "</div>") if fen else ""}</div>')
apparait("#hf", T(44), 120, 0.5, 0.3)
son(T(44), "whoosh-tunnel", 0.45, "carte HyperFrames")
son(T(48), "revelation", 0.4, "HyperFrames")
cache("#hf", T(49) - 0.05)

# ================================================================ 6. « Tous les modèles… » : la liste des modèles sort du doigt et le suit
# trajectoire du bout des doigts relevée image par image (montage, pixels 1080×1920), passée dans le repère de la vidéo studio agrandie
DOIGT = [(19.53, 650, 1500), (19.62, 700, 1400), (19.70, 729, 1296), (19.80, 702, 1188), (19.90, 594, 1134), (20.00, 486, 1107),
         (20.10, 260, 1040), (20.20, 200, 1048), (20.30, 190, 1048), (20.40, 120, 1048), (20.50, 60, 1050), (20.60, -40, 1060)]
DOIGT = [(t + D, -60 + x * 1200 / 1080, -106 + y * 1200 / 1080) for t, x, y in DOIGT]


def doigt(t):
    if t <= DOIGT[0][0]:
        return DOIGT[0][1:]
    for (t0, x0, y0), (t1, x1, y1) in zip(DOIGT, DOIGT[1:]):
        if t <= t1:
            m = (t - t0) / (t1 - t0)
            return x0 + (x1 - x0) * m, y0 + (y1 - y0) * m
    return DOIGT[-1][1:]


CHAT = ('<div class="faux-chat"><img src="assets/img/logo-chatgpt.svg" alt="" /><div class="fc-q">Fais-moi une vidéo animée</div>'
        '<div class="fc-r"><i></i><i></i><i></i></div></div>')
MODELES = [("claude", "Claude", "logo-claude.svg", '<video id="lv-claude" class="clip" src="assets/fonds/claude-accueil.mp4" data-start="{a}" data-duration="{d}" data-media-start="0.3" data-track-index="9" muted playsinline></video>'),
           ("chatgpt", "ChatGPT", "logo-chatgpt.svg", CHAT),
           ("gemini", "Gemini", "logo-gemini.svg", '<video id="lv-gemini" class="clip" src="assets/captures/modele-gemini.mp4" data-start="{a}" data-duration="{d}" data-media-start="0" data-track-index="10" muted playsinline></video>'),
           ("grok", "Grok", "logo-grok.svg", '<video id="lv-grok" class="clip" src="assets/captures/modele-grok.mp4" data-start="{a}" data-duration="{d}" data-media-start="0" data-track-index="11" muted playsinline></video>')]
GRILLE = [(265, 480), (815, 480), (265, 740), (815, 740)]
L_FIN = T(78) - 0.1
for k, (cle_, nom, logo, contenu) in enumerate(MODELES):
    s0 = 19.72 + D + 0.12 * k          # naissance au bout du doigt
    lag = 0.07 * k                 # chaque carte suit le doigt avec un petit retard : une file
    contenu = contenu.format(a=r(s0), d=r(L_FIN - s0 + 0.05))
    HTML.append(f'<div id="lm-{cle_}" class="liste-mod" style="opacity: 0"><div class="lm-ecran">{contenu}</div>'
                 f'<div class="lm-nom"><img src="assets/img/{logo}" alt="" />{nom}</div>'
                 f'<b id="lm-ok-{cle_}" class="lm-tampon ok" style="opacity: 0">CODE ✓</b><b id="lm-ko-{cle_}" class="lm-tampon ko" style="opacity: 0">VIDÉO ✗</b></div>')
    x, y = doigt(s0 - lag)
    j(f'tl.set("#lm-{cle_}", {{ x: {round(x)}, y: {round(y - 150)}, xPercent: -50, yPercent: -50, scale: 0.1, opacity: 1 }}, {r(s0)});')
    j(f'tl.to("#lm-{cle_}", {{ scale: 0.5, duration: 0.15, ease: "back.out(2)" }}, {r(s0)});')
    t = s0
    while t < 20.52 + D:
        x, y = doigt(t + 0.05 - lag)
        j(f'tl.to("#lm-{cle_}", {{ x: {round(x)}, y: {round(y - 150 - 20 * k)}, duration: 0.05, ease: "none" }}, {r(t)});')
        t += 0.05
    gx, gy = GRILLE[k]
    j(f'tl.to("#lm-{cle_}", {{ x: {gx}, y: {gy}, scale: 1, rotation: {(-3, 2, 3, -2)[k]}, duration: 0.38, ease: "back.out(1.4)" }}, {r(20.55 + D + 0.06 * k)});')
    son(s0, tour(POPS), 0.4, f"{nom} sort du doigt")
    j(f'tl.to("#lm-{cle_}", {{ opacity: 0, scale: 0.7, duration: 0.18 }}, {r(L_FIN)});')
    # verdicts : code oui, vidéo non
    j(f'tl.fromTo("#lm-ok-{cle_}", {{ opacity: 0, scale: 2.2 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.in", immediateRender: false }}, {r(T(65) + 0.08 * k)});')
    j(f'tl.to("#lm-ok-{cle_}", {{ opacity: 0, duration: 0.12 }}, {r(T(71) - 0.05)});')
    j(f'tl.fromTo("#lm-ko-{cle_}", {{ opacity: 0, scale: 2.2 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.in", immediateRender: false }}, {r(T(71) + 0.08 * k)});')
son(20.55 + D, "whoosh-cine", 0.4, "la liste se range")
son(T(65), "bonne-reponse", 0.42, "code ✓")
son(T(71), "buzzer-faux", 0.4, "vidéo ✗")
for k in range(4):
    son(T(65) + 0.08 * k, "impact-tambour", 0.18, "tampon code")
    son(T(71) + 0.08 * k, "impact-basse", 0.18, "tampon vidéo")
# la caméra accompagne le balayage du bras vers la gauche, puis revient
j(f'tl.to("#pousse", {{ x: 70, duration: 0.9, ease: "sine.inOut" }}, {r(19.75 + D)});')
j(f'tl.to("#pousse", {{ x: 0, duration: 0.8, ease: "sine.inOut" }}, {r(21.2 + D)});')

# ================================================================ 7. HyperFrames intervient : références + code → vidéo
HTML.append('<div id="sch" class="schema" style="opacity: 0"><div id="s1" class="bloc" style="opacity: 0">RÉFÉRENCES</div><i id="s2" style="opacity: 0">+</i>'
            '<div id="s3" class="bloc" style="opacity: 0">CODE</div><i id="s4" style="opacity: 0">→</i>'
            f'<div id="s5" class="bloc vid" style="opacity: 0"><video id="sch-v" class="clip" src="assets/exemples/enveloppes.mp4" data-start="{r(T(88))}" '
            f'data-duration="{r(T(99) - T(88))}" data-media-start="0.5" data-track-index="9" muted playsinline></video></div></div>')
j(f'tl.set("#sch", {{ opacity: 1 }}, {r(T(85))});')
for sel, t in (("#s5", T(88)), ("#s1", T(94)), ("#s2", T(96)), ("#s3", T(98)), ("#s4", T(98) + 0.25)):
    apparait(sel, t, 40, 0.4, 0.18)
    son(t, tour(POPS), 0.38, "schéma")
son(T(88), "magie", 0.4, "la vidéo apparaît")
cache("#sch", T(98) + 0.02)
HTML.append('<div id="hfi" class="tag" style="left: 240px; top: 380px; opacity: 0">HYPERFRAMES</div>')
claque("#hfi", T(83), 1.8)
son(T(83), "impact-futur", 0.4, "HyperFrames intervient")
cache("#hfi", T(85))

# ================================================================ 8. Plusieurs possibilités : Claude Pro, Claude Max, chatbot
HTML.append('<div id="poss" class="tag clair" style="left: 150px; top: 420px; opacity: 0">PLUSIEURS POSSIBILITÉS</div>')
claque("#poss", T(101), 1.8)
son(T(101), "impact-tambour", 0.38, "plusieurs possibilités")
j('tl.set("#poss", { zIndex: 14 }, 0);')
cache("#poss", T(103) + 0.2)
# saturation : l'écran se remplit de toutes les façons d'utiliser HyperFrames, arrivées de tous les côtés, puis aspirées
POSS = ["Claude Pro", "Claude Max", "Claude Code", "Claude Desktop", "claude.ai", "Terminal", "VS Code", "Cursor", "API", "Chatbot",
        "Codex", "Gemini CLI", "Windsurf", "Copilot", "Mac", "Windows", "Linux", "Navigateur", "Mobile", "npx hyperframes", "Skill",
        "Plugin", "MCP", "Cloud", "Studio", "Opus 5.5", "Fable 5.2", "Sonnet", "GPT", "Gemini", "Grok", "DeepSeek", "Projet", "Équipe",
        "Claude Pro", "Claude Code", "Terminal", "Cursor", "API", "VS Code", "Chatbot", "Skill", "Claude Max", "MCP", "Cloud", "Studio",
        "Mac", "Windows", "Codex", "claude.ai", "Plugin", "Navigateur", "Opus 5.5", "Fable 5.2", "Gemini CLI"]
HTML.append('<div id="poss-voile" class="flash" style="background: rgba(5,8,15,0.55); z-index: 11"></div>')
j(f'tl.fromTo("#poss-voile", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, {r(T(101))});')
j(f'tl.to("#poss-voile", {{ opacity: 0, duration: 0.25 }}, {r(T(103) + 0.25)});')
DIRS_P = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
t_p0, t_p1, t_asp = T(101), T(102) + 0.45, T(103) + 0.2
for k, nom in enumerate(POSS):
    col, row = k % 5, k // 5
    x = 30 + col * 205 + ((row * 41 + k * 59) % 60) - 30
    y = 150 + row * 140 + ((k * 67) % 40) - 20
    rot = ((k * 43) % 34) - 17
    ic = '<img src="assets/img/logo-claude.svg" alt="" />' if nom.startswith("Claude") or nom.startswith("claude") else f'<i style="background: {COUL[k % len(COUL)]}"></i>'
    HTML.append(f'<div id="ps{k}" class="sat-chip" data-layout-allow-overlap style="left: {x}px; top: {y}px; opacity: 0">{ic}{nom}</div>')
    t0 = t_p0 + (t_p1 - t_p0) * (k / len(POSS)) ** 0.8
    dx, dy = DIRS_P[k % 8]
    j(f'tl.fromTo("#ps{k}", {{ opacity: 0, x: {dx * 900}, y: {dy * 1500}, rotation: {rot * 4}, scale: 1.8 }}, '
      f'{{ opacity: 1, x: 0, y: 0, rotation: {rot}, scale: 1, duration: 0.22, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    j(f'tl.to("#ps{k}", {{ opacity: 0, scale: 0.15, x: {round((540 - x) * 0.85)}, y: {round((900 - y) * 0.85)}, rotation: {rot + 120}, duration: 0.24, ease: "power3.in" }}, {r(t_asp + 0.004 * k)});')
    if k % 3 == 0:
        son(t0, tour(["whoosh-pop", "swoosh-court", "souffle-rapide"] + POPS), 0.2, f"possibilité {nom}")
son(t_p0, "swell-court", 0.3, "saturation de possibilités")
son(t_asp, "aspiration", 0.32, "les possibilités sont aspirées")
HTML.append('<div id="p1" class="prix" style="left: 60px; opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /><b>CLAUDE PRO</b><span>20 $ / mois</span><em>pour commencer</em></div>')
HTML.append('<div id="p2" class="prix" style="left: 560px; opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /><b>CLAUDE MAX</b><span>pour aller plus loin</span></div>')
apparait("#p1", T(105) - 0.1, 100, 0.5, 0.25)  # après la saturation des possibilités
son(T(110), "scanner-caisse", 0.42, "20 dollars")
apparait("#p2", T(124), 100, 0.5, 0.25)
son(T(124), "pieces-tintent", 0.4, "Claude Max")
cache("#p1", T(126) - 0.05)
cache("#p2", T(126) - 0.05)

# ================================================================ 9. Attention : le modèle fait la différence
HTML.append('<div id="att" class="alerte" style="opacity: 0">⚠ L’OUTIL NE FAIT PAS TOUT</div>')
claque("#att", T(137), 1.8)
son(T(137), "alarme-alerte", 0.3, "attention", d=0.8)
cache("#att", T(144))
HTML.append('<div id="cle" class="slam petit" style="top: 660px; font-size: 104px; opacity: 0">LE MODÈLE = LA CLÉ</div>')
claque("#cle", T(152), 2.0)
son(T(152), "impact-basse", 0.45, "le modèle")
cache("#cle", T(155) - 0.05)

# ================================================================ 12. Abonne-toi + prochaine vidéo
HTML.append('<div id="proch" class="prochaine" style="opacity: 0"><span>PROCHAINE VIDÉO</span><b>Copier le style visuel<br>d’un autre créateur</b></div>')
apparait("#proch", T(204), 100, 0.5, 0.3)
son(T(204), "whoosh-tunnel", 0.42, "prochaine vidéo")
j(f'tl.fromTo("#fondu", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, immediateRender: false }}, {r(FIN - 0.4)});')
HTML.append('<div id="fondu" class="flash" style="background: #000"></div>')


# ================================================================ MAGIE : une vidéo naît dans la main, la suit, puis plein écran (zoom), puis retourne dans la main
MAINS_TRAJ = json.loads((ICI / "assets/montage/mains.json").read_text())


def geste(t0):
    g = min(GESTES, key=lambda e: abs(e[0] - t0))
    return g[0], g[3], g[4]


# positions de la paume relevées à l'œil sur les images (le suivi automatique se perd quand la main sort du cadre)
MANUEL = {
    "A": [(31.4, 380, 1760), (33.7, 420, 1760)],
    "B": [(40.9, 700, 1760), (44.3, 700, 1760)],
    "C": [(49.0, 400, 1650), (49.5, 220, 1300), (49.9, 190, 1260), (51.2, 190, 1260)],
    "E2": [(59.75, 760, 1560), (60.0, 770, 1570), (60.4, 950, 1330), (60.9, 950, 1330)],
    "E3": [(60.85, 330, 1380), (62.45, 330, 1380)],
    "E4": [(62.45, 560, 1660), (63.8, 560, 1660)],
    "D": [(68.8, 560, 1700), (70.7, 560, 1700)],
    "O": [(50.0, 600, 1720), (54.0, 600, 1720)],
    "F": [(52.5, 480, 1720), (58.5, 480, 1720)],
}


MANUEL = {k_: [(t_ + (D2 if t_ > 27.5 else 0), x_, y_) for t_, x_, y_ in v_] for k_, v_ in MANUEL.items()}


def _lin(kf, t):
    if t <= kf[0][0]:
        return kf[0][1:]
    for (t0, x0, y0), (t1, x1, y1) in zip(kf, kf[1:]):
        if t <= t1:
            m = (t - t0) / (t1 - t0)
            return x0 + (x1 - x0) * m, y0 + (y1 - y0) * m
    return kf[-1][1:]


def paume(nom, t):
    if nom == "E":  # 3D : suivi automatique (paume ouverte bien visible) ; ensuite relevés à l'œil
        nom = "E" if t < 59.75 + D2 else "E2" if t < 60.85 + D2 else "E3" if t < 62.45 + D2 else "E4"
    if nom in MANUEL:
        x, y = _lin(MANUEL[nom], t)
        return -60 + x * 1200 / 1080, -106 + y * 1200 / 1080
    tr = MAINS_TRAJ[nom]
    p = min(tr, key=lambda e: abs(e[0] - t))
    # repère écran : vidéo studio agrandie (×1200/1080, décalée de -60, -106)
    return -60 + p[1] * 1200 / 1080, -106 + p[2] * 1200 / 1080


def contenu_video(vid, src, t0, t1, depart=0.0, large=False, centre=False):
    """vertical : la vidéo couvre la carte ; 16:9 : copie floutée derrière + vidéo entière en largeur"""
    d = r(t1 - t0 + 0.05)
    if not large:
        return (f'<video id="{vid}" class="clip{" mg-zoom" if centre else ""}" src="{src}" data-start="{r(t0)}" data-duration="{d}" data-media-start="{depart}" '
                f'data-track-index="{12 + len(HTML) % 4}" muted playsinline></video>')
    return (f'<video id="{vid}-f" class="clip mg-flou" src="{src}" data-start="{r(t0)}" data-duration="{d}" data-media-start="{depart}" '
            f'data-track-index="{16 + len(HTML) % 3}" muted playsinline></video>'
            f'<video id="{vid}" class="clip mg-large" src="{src}" data-start="{r(t0)}" data-duration="{d}" data-media-start="{depart}" '
            f'data-track-index="{12 + len(HTML) % 4}" muted playsinline></video>')


def magie(mid, contenu, nom_main, t_app, t_zoom, t_fin, etiquette="", retour=True):
    HTML.append(f'<div id="{mid}" class="magie" style="opacity: 0"><div class="mg-carte">{contenu}'
                f'{("<b class=" + chr(34) + "mg-etiq" + chr(34) + ">" + etiquette + "</b>") if etiquette else ""}</div></div>')
    HTML.append(f'<div id="{mid}-eclat" class="mg-eclat" style="opacity: 0"></div>')
    x, y = paume(nom_main, t_app)
    # éclat de magie dans la paume
    j(f'tl.set("#{mid}-eclat", {{ x: {round(x - 160)}, y: {round(y - 160)} }}, {r(t_app)});')
    j(f'tl.fromTo("#{mid}-eclat", {{ opacity: 1, scale: 0.2 }}, {{ opacity: 0, scale: 1.6, duration: 0.45, ease: "power2.out", immediateRender: false }}, {r(t_app)});')
    # la vidéo naît au-dessus de la paume
    j(f'tl.set("#{mid}", {{ opacity: 1, x: {round(x - 540)}, y: {round(y - 960 - 170)}, scale: 0.02, rotation: -14 }}, {r(t_app)});')
    j(f'tl.to("#{mid}", {{ scale: 0.17, rotation: -6, duration: 0.22, ease: "back.out(2.2)" }}, {r(t_app)});')
    t = t_app + 0.1
    while t < t_zoom - 0.05:
        x, y = paume(nom_main, t + 0.1)
        j(f'tl.to("#{mid}", {{ x: {round(x - 540)}, y: {round(y - 960 - 170)}, duration: 0.1, ease: "none" }}, {r(t)});')
        t += 0.1
    # grand zoom : la vidéo remplit l'écran
    j(f'tl.to("#{mid}", {{ x: 0, y: 0, scale: 1, rotation: 0, duration: 0.34, ease: "power3.inOut" }}, {r(t_zoom)});')
    j(f'tl.to("#{mid} .mg-carte", {{ borderRadius: 0, borderWidth: 0, duration: 0.34, ease: "power3.inOut" }}, {r(t_zoom)});')
    j(f'tl.to("#titre", {{ opacity: 0, duration: 0.2 }}, {r(t_zoom + 0.1)});')
    if t_fin is not None:
        j(f'tl.to("#titre", {{ opacity: 1, duration: 0.2 }}, {r(t_fin)});')
    son(t_app, tour(["magie", "scintille-whoosh", "power-up"]), 0.42, f"{mid} naît dans la main")
    son(t_zoom, tour(["zoom-impact", "zoom-futur", "zoom-in"]), 0.42, f"{mid} plein écran")
    son(t_zoom, tour(WH), 0.3, f"{mid} souffle")
    if t_fin is None:
        return
    if retour:  # elle retourne dans la main
        x, y = paume(nom_main, t_fin + 0.25)
        j(f'tl.to("#{mid} .mg-carte", {{ borderRadius: 70, borderWidth: 12, duration: 0.25, ease: "power2.in" }}, {r(t_fin)});')
        j(f'tl.to("#{mid}", {{ x: {round(x - 540)}, y: {round(y - 960 - 120)}, scale: 0.05, rotation: 10, duration: 0.25, ease: "power3.in" }}, {r(t_fin)});')
        j(f'tl.set("#{mid}", {{ opacity: 0 }}, {r(t_fin + 0.26)});')
        son(t_fin, tour(["swoosh-court", "balaie-petit", "whoosh-pop"]), 0.3, f"{mid} retourne dans la main")
    else:
        j(f'tl.to("#{mid}", {{ opacity: 0, duration: 0.12 }}, {r(t_fin)});')


def ville_iso():
    """petite ville en 3D isométrique (SVG) dont les blocs sortent du sol"""
    blocs, js_ = [], []
    k = 0
    for gx, gy in sorted(((a, b) for a in range(4) for b in range(5)), key=lambda e: e[0] + e[1]):  # du fond vers l'avant
        if True:
            hgt = (40, 110, 70, 160, 90, 130, 60, 190, 100, 80)[(gx * 3 + gy * 7) % 10]
            cx, cy = 540 + (gx - gy) * 120, 760 + (gx + gy) * 70
            col = ("#7DD3FC", "#38BDF8", "#0284C7") if (gx + gy) % 3 else ("#FDE68A", "#F2B705", "#B07D00")
            blocs.append(f'<g id="iso-b{k}" style="transform-origin: {cx}px {cy + 70}px">'
                         f'<path d="M{cx} {cy - hgt} L{cx + 120} {cy + 70 - hgt} L{cx} {cy + 140 - hgt} L{cx - 120} {cy + 70 - hgt} Z" fill="{col[0]}" stroke="#0B1220" stroke-width="5" />'
                         f'<path d="M{cx - 120} {cy + 70 - hgt} L{cx} {cy + 140 - hgt} L{cx} {cy + 140} L{cx - 120} {cy + 70} Z" fill="{col[1]}" stroke="#0B1220" stroke-width="5" />'
                         f'<path d="M{cx + 120} {cy + 70 - hgt} L{cx} {cy + 140 - hgt} L{cx} {cy + 140} L{cx + 120} {cy + 70} Z" fill="{col[2]}" stroke="#0B1220" stroke-width="5" /></g>')
            k += 1
    return ('<div class="mg-iso"><svg viewBox="0 0 1080 1920" width="1080" height="1920">' + "".join(blocs) + '</svg></div>'), k


# --- « il permet de créer des vidéos à partir de références visuelles et de code » : une de ses vidéos sort de la main
tA = geste(DD(31.4))[0]
magie("mgA", contenu_video("mgA-v", "assets/exemples/liste-depenser-moins.mp4", tA, T(101) + 0.9, 0.2, centre=True), "A", tA, T(98) + 0.05, T(101), "LE RÉSULTAT")
# --- « installer la skill dans un environnement de chatbot » : un vrai chatbot sort de la main
tB = geste(DD(40.87))[0]
magie("mgB", contenu_video("mgB-v", "assets/captures/modele-gemini.mp4", tB, T(137), 0.0, large=True), "B", tB, T(131), T(137) - 0.3, "TON CHATBOT")
# --- « pour générer ta vidéo »
ROUL = [("Grok", "logo-grok.svg"), ("Gemini", "logo-gemini.svg"), ("DeepSeek", None), ("ChatGPT", "logo-chatgpt.svg"), ("Mistral", None),
        ("Llama", None), ("Qwen", None), ("Fable 5.2", "logo-claude.svg"), ("Gemini", "logo-gemini.svg"), ("Grok", "logo-grok.svg"),
        ("ChatGPT", "logo-chatgpt.svg"), ("DeepSeek", None), ("Opus 5.5", "logo-claude.svg"), ("Kimi", None), ("Mistral", None)]
cartes = "".join(f'<div class="rl-carte{" cible" if n == "Opus 5.5" else ""}">' + (f'<img src="assets/img/{l}" alt="" />' if l else f'<i>{n[0]}</i>') + f'<b>{n}</b></div>'
                 for n, l in ROUL)
HTML.append(f'<div id="roul" class="roulette" style="opacity: 0"><div id="roul-bande" class="rl-bande">{cartes}</div><div class="rl-cadre"></div></div>')
t_r0, t_r1 = T(145), T(152)
cible = [n for n, _ in ROUL].index("Opus 5.5")
j(f'tl.set("#roul", {{ opacity: 1 }}, {r(t_r0)});')
j(f'tl.fromTo("#roul-bande", {{ x: 0 }}, {{ x: {-(cible * 300) + 390}, duration: {r(t_r1 - t_r0)}, ease: "power4.out", immediateRender: false }}, {r(t_r0)});')
for k in range(9):
    son(t_r0 + (t_r1 - t_r0) * (k / 9) ** 2.2, "tic", 0.3, "la roulette tourne")
son(t_r1, "trailer-impact", 0.3, "la roulette s'arrête sur Opus 5.5")
flash(t_r1, 0.45)
j(f'tl.to("#roul", {{ opacity: 0, duration: 0.15 }}, {r(T(155) - 0.05)});')
# puis plusieurs modèles côte à côte : le cadre de sélection saute de l'un à l'autre
GRM = [("Opus 5.5", "logo-claude.svg"), ("Fable 5.2", "logo-claude.svg"), ("ChatGPT", "logo-chatgpt.svg"), ("Gemini", "logo-gemini.svg"),
       ("Grok", "logo-grok.svg"), ("DeepSeek", None)]
for k, (n, l) in enumerate(GRM):
    gx, gy = 60 + (k % 3) * 330, 330 + (k // 3) * 230
    ic = f'<img src="assets/img/{l}" alt="" />' if l else f'<i>{n[0]}</i>'
    HTML.append(f'<div id="gm{k}" class="rl-carte grille" style="left: {gx}px; top: {gy}px; opacity: 0">{ic}<b>{n}</b></div>')
    apparait(f"#gm{k}", T(155) + 0.05 * k, 60, 0.4, 0.2)
    j(f'tl.to("#gm{k}", {{ opacity: 0, scale: 0.8, duration: 0.15 }}, {r(T(161) - 0.05)});')
son(T(155), "whoosh-cine", 0.34, "les modèles s'alignent")
HTML.append('<div id="gm-sel" class="gm-sel" style="opacity: 0"></div>')
ordre = [2, 3, 4, 5, 1, 0]
for k, i in enumerate(ordre):
    t = T(156) + 0.25 * k
    gx, gy = 60 + (i % 3) * 330, 330 + (i // 3) * 230
    j(f'tl.set("#gm-sel", {{ opacity: 1, x: {gx - 10}, y: {gy - 10} }}, {r(t)});')
    son(t, "clic-souris", 0.3, "on choisit le modèle")
j(f'tl.to("#gm-sel", {{ opacity: 0, duration: 0.15 }}, {r(T(161) - 0.05)});')
# --- « des vidéos en 3D, des vidéos en 2D, des vidéos en 3D isométrique, et j'en passe » : le tour de magie
magie("mg3d", contenu_video("mg3d-v", "assets/magie/retro-soleil.mp4", T(183), T(187), 0.5, large=True), "E", T(183), T(185), T(187) - 0.28, "3D")
magie("mg2d", contenu_video("mg2d-v", "assets/exemples/enveloppes.mp4", T(187), T(191), 0.6, centre=True), "E", T(187), T(189), T(191) - 0.28, "2D")
iso_html, n_iso = ville_iso()
magie("mgiso", iso_html, "E", T(191), T(193), T(196) - 0.05, "3D ISOMÉTRIQUE")
for i in range(n_iso):
    j(f'tl.fromTo("#iso-b{i}", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.3, ease: "back.out(2)", immediateRender: false }}, {r(T(193) + 0.2 + 0.035 * i)});')
son(T(193) + 0.3, "pop-long", 0.3, "la ville isométrique sort du sol")
# --- « Opus 5.5 est très intéressant » / « Fable 5.2 peut faire mieux » : on écrit dans le chat, en vrai
def chat_html(cid, modele, question, reponse_html, autre_modele=""):
    mots_q = "".join(f'<span id="{cid}-q{i}" style="opacity: 0">{m} </span>' for i, m in enumerate(question.split()))
    puce = (f'<b id="{cid}-puce" class="ch-puce">{modele} ▾</b>' if not autre_modele else
            f'<b id="{cid}-puce" class="ch-puce"><i id="{cid}-p1">{autre_modele} ▾</i><i id="{cid}-p2" class="nouv" style="opacity: 0">{modele} ✦</i></b>')
    return (f'<div class="chat"><div class="ch-tete"><img src="assets/img/logo-claude.svg" alt="" /><b>Claude</b>{puce}</div>'
            f'<div class="ch-fil"><div id="{cid}-bulle" class="ch-moi" style="opacity: 0">{mots_q}</div>'
            f'<div id="{cid}-rep" class="ch-ia" style="opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /><div>{reponse_html}</div></div></div>'
            f'<div class="ch-saisie"><span>Écris à Claude…</span><i>↑</i></div></div>')


def taper(cid, question, t0, d):
    n = len(question.split())
    j(f'tl.set("#{cid}-bulle", {{ opacity: 1 }}, {r(t0)});')
    for i in range(n):
        j(f'tl.set("#{cid}-q{i}", {{ opacity: 1 }}, {r(t0 + d * i / n)});')
    son(t0, "clavier-ordi", 0.3, f"{cid} on tape la demande", d=d)
    son(t0 + d + 0.02, "pop-click", 0.32, f"{cid} envoyer")


QO = "Fais-moi une vidéo animée de 30 s : la méthode des enveloppes"
RO = ('<p class="ch-titre">Opus 5.5</p><p>Je crée la composition HyperFrames…</p>'
      '<pre id="co-code"><span id="co-l0" style="opacity: 0">&lt;div class="scene"&gt;</span><span id="co-l1" style="opacity: 0">  gsap.timeline({ paused: true })</span>'
      '<span id="co-l2" style="opacity: 0">  .from("#enveloppe", { y: 400 })</span><span id="co-l3" style="opacity: 0">✓ vidéo prête : 1080×1920</span></pre>')
tO0 = T(161)
magie("mgO", chat_html("co", "Opus 5.5", QO, RO), "O", tO0, tO0 + 0.25, T(166) + 0.02, "")
taper("co", QO, tO0 + 0.42, 0.55)
j(f'tl.set("#co-rep", {{ opacity: 1 }}, {r(tO0 + 1.02)});')
for i in range(4):
    j(f'tl.set("#co-l{i}", {{ opacity: 1 }}, {r(tO0 + 1.1 + 0.15 * i)});')
    son(tO0 + 1.1 + 0.15 * i, "clavier-bit", 0.18, "code qui s'écrit")

QF = "La même, mais en 3D cinématique"
RF = ('<p class="ch-titre or">Fable 5.2</p><div class="ch-video"><video id="cf-v" class="clip" src="assets/magie/retro-soleil.mp4" '
      f'data-start="{r(T(176))}" data-duration="{r(T(182) - T(176) + 0.3)}" data-media-start="1.5" data-track-index="24" muted playsinline></video>'
      '<b id="cf-mieux" class="ch-mieux" style="opacity: 0">★ ENCORE MIEUX</b></div>')
tF0 = T(166)
magie("mgF", chat_html("cf", "Fable 5.2", QF, RF, autre_modele="Opus 5.5"), "F", tF0, tF0 + 0.3, T(182) + 0.12, "")
j(f'tl.to("#cf-p1", {{ opacity: 0, duration: 0.12 }}, {r(T(171))});')
j(f'tl.fromTo("#cf-p2", {{ opacity: 0, scale: 1.8 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, {r(T(171))});')
son(T(171), "revelation", 0.42, "on passe sur Fable 5.2")
taper("cf", QF, T(171) + 0.3, 0.7)
j(f'tl.set("#cf-rep", {{ opacity: 1 }}, {r(T(176))});')
son(T(176), "magie", 0.36, "la vidéo 3D de Fable apparaît")
j(f'tl.fromTo("#cf-mieux", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.16, ease: "power4.in", immediateRender: false }}, {r(T(178))});')
son(T(178), "cloche-succes", 0.38, "peut faire mieux")

# « et j'en passe » : six de ses vidéos jaillissent de la main
EXB = ["salaire-15", "site-3d-vertical", "edit-claude", "tontine-epargne", "site-anime-vertical", "classement-ia-vertical"]
GR = [(200, 560), (540, 560), (880, 560), (200, 1010), (540, 1010), (880, 1010)]
for k, f in enumerate(EXB):
    t0 = T(196) + 0.05 * k
    x, y = paume("E", t0)
    HTML.append(f'<div id="mb{k}" class="mg-mini" style="opacity: 0"><video id="mb{k}-v" class="clip" src="assets/exemples/{f}.mp4" data-start="{r(t0)}" '
                f'data-duration="{r(T(199) - t0 + 0.1)}" data-media-start="0.6" data-track-index="{20 + k}" muted playsinline></video></div>')
    gx, gy = GR[k]
    j(f'tl.set("#mb{k}", {{ opacity: 1, x: {round(x - 130)}, y: {round(y - 231)}, scale: 0.05, rotation: -20 }}, {r(t0)});')
    j(f'tl.to("#mb{k}", {{ x: {gx - 130}, y: {gy - 231}, scale: 1, rotation: {(-6, 3, 7, -4, 5, -7)[k]}, duration: 0.35, ease: "back.out(1.6)" }}, {r(t0)});')
    j(f'tl.to("#mb{k}", {{ scale: 0, opacity: 0, duration: 0.18, ease: "power2.in" }}, {r(T(199) - 0.15)});')
    son(t0, tour(POPS), 0.3, f"vidéo {f} jaillit")
son(T(196), "magie", 0.4, "et j'en passe")
# --- fin : « pour faire tes vidéos » : une dernière vidéo sort de la main et remplit l'écran
magie("mgD", contenu_video("mgD-v", "assets/exemples/edit-claude.mp4", T(216), FIN, 0.2), "D", T(216), T(219), None)

# ================================================================ OBJETS QUI NAISSENT DANS LES MAINS (gestes détectés)
def geste(t0):
    g = min(GESTES, key=lambda e: abs(e[0] - t0))
    return g[0], g[3], g[4]


t, hx, hy = geste(DD(6.8))
dans_la_main("mo1", '<img src="assets/img/logo-claude.svg" alt="" class="m-logo" />', t, hx, hy, T(29) - 0.1)
t, hx, hy = geste(DD(14.53))
dans_la_main("mo2", '<b class="m-txt">GAME<br>CHANGER</b>', t, hx, hy, T(48) - 0.1, monte=230)
t, hx, hy = geste(DD(18.87))
dans_la_main("mo3", '<b class="m-txt q">?</b>', t, hx, hy, 19.55 + D, zoom=False, monte=750)
t, hx, hy = geste(DD(22.93))
dans_la_main("mo4", '<b class="m-code">&lt;/&gt;</b>', t, hx, hy, T(78) - 0.1, zoom=False)
t, hx, hy = geste(DD(28.27))
dans_la_main("mo5", '<img src="assets/img/logo-heygen.png" alt="" class="m-logo rond" />', t, hx, hy, T(94) - 0.1)
t, hx, hy = geste(DD(63.4))
dans_la_main("mo10", '<b class="m-abo">S’ABONNER 🔔</b>', t, hx, hy, T(204) - 0.1, monte=300)


# ================================================================ ZOOMS DE CINÉMA (coup de zoom sur les mots forts, souffle + boom)
def zoom_cine(t, s=1.28, tenue=0.55, boom="impact-basse"):
    j(f'tl.to("#cine", {{ scale: {s}, duration: 0.16, ease: "power4.out" }}, {r(t - 0.04)});')
    j(f'tl.to("#cine", {{ scale: 1, duration: 0.55, ease: "power2.inOut" }}, {r(t + tenue)});')
    son(t - 0.04, tour(["zoom-impact", "zoom-in", "zoom-futur", "whoosh-cine"]), 0.34, "zoom de cinéma")
    son(t, boom, 0.26, "boom du zoom")


for i_, s_ in ((42, 1.25), (48, 1.3), (50, 1.22), (83, 1.3), (110, 1.22), (124, 1.25), (138, 1.32), (149, 1.22), (152, 1.35), (199, 1.3), (211, 1.22)):
    zoom_cine(T(i_), s_, boom=("trailer-impact" if i_ in (48, 152) else "impact-basse"))

# ================================================================ TENSION (montées sonores et battements)
son(T(40) - 0.9, "riser-tech", 0.32, "montée vers le game changer", d=0.9)
son(T(78) - 0.9, "riser-trailer", 0.3, "montée vers HyperFrames intervient", d=0.9)
son(T(99) - 1.0, "riser-trailer", 0.32, "montée vers la musique 3 (tambours)", d=1.0)
for t_ in (T(40), T(99), T(161)):
    son(t_, "trailer-impact-2", 0.36, "boom : changement de musique")
son(T(137) - 1.2, "roulement-suspense", 0.3, "roulement avant attention", d=1.2)
son(T(137) - 0.2, "battements", 0.32, "tension : l'outil ne fait pas tout", d=3.0)
son(T(161) - 1.0, "riser-synth", 0.3, "montée vers Opus / Fable", d=1.0)
son(T(199) - 0.8, "riser-tech", 0.3, "montée vers abonne-toi", d=0.8)
j(f'tl.fromTo("#tension", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, immediateRender: false }}, {r(T(137))});')
j(f'tl.to("#tension", {{ opacity: 0, duration: 0.6 }}, {r(T(161))});')

# ================================================================ SOUS-TITRES (mot à mot)
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
        t1 = MOTS[groupes[n + 1][0]]["start"] if n + 1 < len(groupes) else FIN - 0.4
        spans = []
        for i in g:
            mot = MOTS[i]["text"].replace("_", " ")
            spans.append(f'<span id="st-{i}" class="st-mot" style="display: none">{mot}</span>')
            js.append(f'    tl.set("#st-{i}", {{ display: "inline-block" }}, {MOTS[i]["start"]});')
            js.append(f'    tl.fromTo("#st-{i}", {{ scale: 1.2 }}, {{ scale: 1, duration: 0.12, ease: "back.out(2)", immediateRender: false }}, {MOTS[i]["start"]});')
        html.append(f'    <div id="st-g{n}" class="st-groupe" data-layout-ignore style="opacity: 0"><div class="st-bandeau">{" ".join(spans)}</div></div>')
        js.append(f'    tl.set("#st-g{n}", {{ opacity: 1 }}, {t0});')
        js.append(f'    tl.set("#st-g{n}", {{ opacity: 0 }}, {round(t1 - 0.01, 3)});')
    page = f"""<!-- Sous-titres mot à mot (écrit par tools/construire3.py). -->
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


MUSIQUES = []
for k_, m_ in enumerate(json.loads((ICI / "assets/music/tension.json").read_text())):
    vol = (0.50, 0.50)[k_]  # deux morceaux à −17 LUFS : la musique reste environ 5–6 dB sous la voix
    MUSIQUES.append(f'      <audio id="musique-{k_ + 1}" src="assets/music/{m_["fichier"]}" data-start="{m_["debut"]}" data-duration="{min(m_["duree"], round(FIN - m_["debut"], 3))}" '
                    f'data-volume="{vol}" data-track-index="{20 + k_ % 2}"></audio>')
sous_titres()
_vus = set()
SONS[:] = [x for x in SONS if not ((x[0], x[1]) in _vus or _vus.add((x[0], x[1])))]
pistes, sons_html = {}, []
for n, (d0, f, v, note, dd) in enumerate(sorted(SONS), start=1):
    p = 30
    while pistes.get(p, -1) > d0 - 0.01:
        p += 1
    pistes[p] = d0 + dd
    sons_html.append(f'<audio id="sfx-{n:03d}" src="assets/sfx/{f}.mp3" data-start="{d0}" data-duration="{dd}" data-volume="{v}" data-track-index="{p}"></audio><!-- {note} -->')
CSS = f"""
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.woff2") format("woff2"); }}
      @font-face {{ font-family: "Inter Lf"; src: url("assets/fonts/Inter-ExtraBold.otf") format("opentype"); font-weight: 800; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #suivi, #pousse, #coup, #cine, #zoomh, #mains {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      #pousse {{ transform-origin: 50% 45%; }}
      #cine {{ transform-origin: 50% 47%; }}
      #studio {{ position: absolute; left: -60px; top: -106px; width: 1200px; height: 2133px; object-fit: cover; }}
      #tension {{ position: absolute; inset: 0; z-index: 9; pointer-events: none; background: radial-gradient(ellipse 70% 60% at 50% 48%, rgba(80,0,0,0) 40%, rgba(90,0,10,0.7) 100%); }}
      #vignette {{ position: absolute; inset: 0; z-index: 9; pointer-events: none; background: radial-gradient(ellipse 80% 70% at 50% 48%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.45) 100%); }}
      .main-obj {{ position: absolute; transform-origin: 50% 50%; margin-left: -120px; margin-top: -60px; width: 240px; text-align: center; filter: drop-shadow(0 16px 30px rgba(0,0,0,0.7)); }}
      .m-logo {{ width: 200px; height: 200px; }}
      .m-logo.rond {{ border-radius: 40px; }}
      .m-txt {{ display: block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 110px; line-height: 0.95; color: #fff; -webkit-text-stroke: 12px #0B1220; paint-order: stroke fill; margin-left: -140px; width: 520px; }}
      .m-txt.q {{ font-size: 260px; margin-left: 0; width: 240px; color: #38BDF8; }}
      .m-code {{ display: inline-block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 120px; color: #0B1220; background: #38BDF8; border: 8px solid #0B1220; border-radius: 30px; padding: 6px 26px 0; }}
      .m-chip {{ display: inline-block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 64px; color: #0B1220; background: #fff; border: 6px solid #0B1220; border-radius: 22px; padding: 6px 20px 0; white-space: nowrap; }}
      .m-chip.or {{ background: #F2B705; font-size: 80px; }}
      .m-abo {{ display: inline-block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 70px; color: #fff; background: #FF0033; border: 7px solid #0B1220; border-radius: 26px; padding: 10px 28px 2px; white-space: nowrap; margin-left: -120px; }}
      .liste-mod {{ position: absolute; left: 0; top: 0; width: 380px; z-index: 5; }}
      .lm-ecran {{ width: 380px; height: 214px; border-radius: 22px; overflow: hidden; border: 6px solid #fff; background: #fff; box-shadow: 0 22px 60px rgba(0,0,0,0.6); }}
      .lm-ecran video {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 0; }}
      .lm-nom {{ position: absolute; left: 14px; top: 160px; display: flex; align-items: center; gap: 10px; background: {NUIT}; color: #fff; font-family: "Anton", sans-serif;
        font-size: 40px; padding: 6px 18px 2px 10px; border-radius: 16px; border: 4px solid #fff; }}
      .lm-nom img {{ width: 40px; height: 40px; }}
      .lm-tampon {{ position: absolute; right: -10px; top: -26px; font-family: "Anton", sans-serif; font-weight: 400; font-size: 54px; padding: 4px 18px 0; border: 6px solid {NUIT};
        transform: rotate(8deg); color: {NUIT}; white-space: nowrap; }}
      .lm-tampon.ok {{ background: {CIEL}; }}
      .lm-tampon.ko {{ background: #FF6B6B; }}
      .faux-chat {{ position: absolute; inset: 0; background: #212121; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }}
      .faux-chat img {{ width: 54px; height: 54px; }}
      .fc-q {{ background: #303030; color: #fff; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 22px; padding: 10px 18px; border-radius: 20px; }}
      .fc-r i {{ display: inline-block; width: 12px; height: 12px; margin: 0 4px; border-radius: 6px; background: #bbb; }}
      .magie {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 35; transform-origin: 50% 50%; }}
      .mg-carte {{ position: absolute; inset: 0; overflow: hidden; border-radius: 70px; border: 12px solid #fff; background: #05070d; box-shadow: 0 40px 120px rgba(0,0,0,0.7); }}
      .mg-carte video {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
      .mg-carte video.mg-zoom {{ transform: scale(1.35); transform-origin: 50% -86px; }}
      .mg-carte video.mg-flou {{ filter: blur(40px) brightness(0.55); transform: scale(1.2); }}
      .mg-carte video.mg-large {{ top: 50%; height: 608px; margin-top: -304px; object-fit: cover; }}
      .mg-etiq {{ position: absolute; left: 0; right: 0; top: 1580px; text-align: center; font-family: "Anton", sans-serif; font-weight: 400; font-size: 150px; line-height: 1; color: #fff;
        -webkit-text-stroke: 14px {NUIT}; paint-order: stroke fill; }}
      .mg-eclat {{ position: absolute; left: 0; top: 0; width: 320px; height: 320px; z-index: 34; border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.95) 0%, rgba(125,211,252,0.6) 35%, rgba(56,189,248,0) 70%); }}
      .mg-iso {{ position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 50% 50%, #16346a 0%, #05070d 80%); }}
      .mg-mini {{ position: absolute; left: 0; top: 0; width: 260px; height: 462px; z-index: 33; border-radius: 30px; overflow: hidden; border: 7px solid #fff; box-shadow: 0 20px 60px rgba(0,0,0,0.6); }}
      .mg-mini video {{ width: 100%; height: 100%; object-fit: cover; }}
      .chat {{ position: absolute; inset: 0; background: #1f1e1b; font-family: "Inter Lf", sans-serif; font-weight: 800; color: #f0eee6; }}
      .ch-tete {{ position: absolute; left: 0; right: 0; top: 300px; display: flex; align-items: center; gap: 20px; padding: 0 70px; }}
      .ch-tete img {{ width: 80px; height: 80px; }}
      .ch-tete > b {{ font-family: "Anton", sans-serif; font-weight: 400; font-size: 70px; }}
      .ch-puce {{ position: relative; margin-left: auto; font-size: 46px; background: #2f2d29; border: 4px solid #5a564d; border-radius: 40px; padding: 14px 34px; min-width: 330px; text-align: center; }}
      .ch-puce i {{ font-style: normal; }}
      .ch-puce i.nouv {{ position: absolute; left: 0; right: 0; top: 14px; color: #F2B705; }}
      .ch-fil {{ position: absolute; left: 60px; right: 60px; top: 460px; }}
      .ch-moi {{ margin-left: 140px; background: #393731; border-radius: 40px; padding: 26px 36px; font-size: 48px; line-height: 1.25; }}
      .ch-ia {{ display: flex; gap: 26px; margin-top: 46px; }}
      .ch-ia > img {{ width: 70px; height: 70px; flex: none; }}
      .ch-ia p {{ font-size: 40px; line-height: 1.3; margin: 0 0 18px; color: #d8d4c8; }}
      .ch-ia p.ch-titre {{ font-family: "Anton", sans-serif; font-weight: 400; font-size: 60px; color: {TERRA}; }}
      .ch-ia p.ch-titre.or {{ color: #F2B705; }}
      .ch-ia pre {{ margin: 0; background: #0b0b0a; border-radius: 26px; padding: 22px 28px; font-size: 31px; line-height: 1.5; color: #7DD3FC; white-space: pre; }}
      .ch-ia pre span {{ display: block; }}
      .ch-video {{ position: relative; width: 760px; height: 428px; border-radius: 28px; overflow: hidden; border: 6px solid #F2B705; }}
      .ch-video video {{ width: 100%; height: 100%; object-fit: cover; }}
      .ch-mieux {{ position: absolute; right: 16px; top: 16px; z-index: 2; font-family: "Anton", sans-serif; font-weight: 400; font-size: 70px; color: {NUIT}; background: #F2B705; padding: 6px 28px 0; border: 6px solid {NUIT}; transform: rotate(-3deg); }}
      .ch-saisie {{ position: absolute; left: 60px; right: 60px; top: 1560px; height: 130px; border-radius: 65px; background: #2f2d29; border: 4px solid #5a564d; display: flex; align-items: center; padding: 0 50px; font-size: 44px; color: #8a857a; }}
      .ch-saisie i {{ margin-left: auto; font-style: normal; width: 80px; height: 80px; border-radius: 40px; background: {TERRA}; color: #fff; text-align: center; line-height: 80px; }}
      .sat-chip {{ position: absolute; display: flex; align-items: center; gap: 12px; background: #fff; color: {NUIT}; font-family: "Anton", sans-serif; font-size: 44px;
        padding: 10px 22px 6px 14px; border-radius: 18px; border: 5px solid {NUIT}; box-shadow: 0 14px 40px rgba(0,0,0,0.55); white-space: nowrap; z-index: 12; }}
      .sat-chip img {{ width: 44px; height: 44px; background: {NUIT}; border-radius: 10px; padding: 4px; }}
      .sat-chip i {{ display: inline-block; width: 26px; height: 26px; border-radius: 50%; }}
      .roulette {{ position: absolute; left: 0; top: 340px; width: 1080px; height: 300px; overflow: hidden; }}
      .rl-bande {{ position: absolute; left: 0; top: 30px; display: flex; gap: 0; }}
      .rl-carte {{ width: 280px; height: 240px; margin-right: 20px; flex: none; background: #fff; border: 7px solid {NUIT}; border-radius: 30px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; gap: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.55); }}
      .rl-carte img {{ width: 96px; height: 96px; background: {NUIT}; border-radius: 22px; padding: 10px; }}
      .rl-carte i {{ width: 96px; height: 96px; border-radius: 22px; background: {CIEL}; color: {NUIT}; font-style: normal; font-family: "Anton", sans-serif; font-size: 64px;
        display: flex; align-items: center; justify-content: center; }}
      .rl-carte b {{ font-family: "Anton", sans-serif; font-weight: 400; font-size: 48px; color: {NUIT}; }}
      .rl-carte.cible {{ background: #FFF4D6; border-color: {TERRA}; }}
      .rl-carte.grille {{ position: absolute; width: 300px; height: 210px; margin: 0; }}
      .rl-cadre {{ position: absolute; left: 380px; top: 20px; width: 320px; height: 260px; border: 10px solid #F2B705; border-radius: 38px; box-shadow: 0 0 40px rgba(242,183,5,0.7); }}
      .gm-sel {{ position: absolute; left: 0; top: 0; width: 320px; height: 230px; border: 10px solid #F2B705; border-radius: 36px; box-shadow: 0 0 40px rgba(242,183,5,0.7); z-index: 12; }}
      .h-tuile {{ position: absolute; z-index: 12; border-radius: 22px; overflow: hidden; border: 6px solid #fff; box-shadow: 0 24px 70px rgba(0,0,0,0.7); background: #000; }}
      .h-tuile video {{ width: 100%; height: 100%; object-fit: cover; }}
      .h-chat {{ background: radial-gradient(ellipse 80% 60% at 50% 45%, #2a2824 0%, #141311 80%); }}
      .hc-boite {{ position: absolute; left: 50px; right: 50px; top: 820px; height: 190px; border-radius: 95px; background: #2f2d29; border: 5px solid #6b665c;
        display: flex; align-items: center; gap: 26px; padding: 0 30px 0 40px; box-shadow: 0 30px 90px rgba(0,0,0,0.6); }}
      .hc-boite img {{ width: 84px; height: 84px; }}
      .hc-texte {{ font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 56px; color: #f0eee6; white-space: nowrap; }}
      .hc-texte i {{ font-style: normal; color: {TERRA}; }}
      .hc-boite b {{ flex: none; margin-left: auto; width: 120px; height: 120px; border-radius: 60px; background: {TERRA}; color: #fff; font-size: 70px; display: flex; align-items: center; justify-content: center; }}
      #calques {{ position: absolute; inset: 0; z-index: 10; pointer-events: none; }}
      .plein {{ position: absolute; inset: 0; overflow: hidden; background: #000; }}
      .plein video {{ width: 100%; height: 100%; object-fit: cover; }}
      .ex-fond {{ background: radial-gradient(ellipse 80% 60% at 50% 40%, #16346a 0%, #05070d 75%); }}
      .tel-ex {{ position: absolute; left: 250px; top: 330px; width: 580px; height: 1030px; border-radius: 60px; overflow: hidden; border: 14px solid #11151f;
        box-shadow: 0 0 0 4px #3b4252, 0 40px 120px rgba(0,0,0,0.8); background: #000; }}
      .tel-ex video {{ width: 100%; height: 100%; object-fit: cover; }}
      .flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 40; }}
      #titre {{ position: absolute; left: 0; top: 0; width: 1080px; height: 290px; z-index: 30; display: flex; justify-content: center; padding-top: 140px;
        background: linear-gradient(180deg, rgba(0,0,0,0.92), rgba(0,0,0,0.55) 70%, rgba(0,0,0,0)); }}
      #titre b {{ font-family: "Anton", sans-serif; font-weight: 400; font-size: 58px; color: #fff; letter-spacing: 1px; -webkit-text-stroke: 8px #000; paint-order: stroke fill; }}
      #titre b i {{ font-style: normal; color: {CIEL}; }}
      .tag {{ position: absolute; font-family: "Anton", sans-serif; font-size: 72px; color: {NUIT}; background: {CIEL}; border: 6px solid {NUIT}; padding: 6px 26px 0;
        transform: rotate(-3deg); box-shadow: 0 18px 50px rgba(0,0,0,0.5); white-space: nowrap; }}
      .tag.clair {{ background: #fff; }}
      .slam {{ position: absolute; left: 0; top: 420px; width: 1080px; text-align: center; font-family: "Anton", sans-serif; font-size: 170px; line-height: 1; color: #fff;
        -webkit-text-stroke: 14px {NUIT}; paint-order: stroke fill; text-shadow: 0 0 50px rgba(56,189,248,0.7); }}
      .slam.petit {{ font-size: 130px; }}
      .msg {{ position: absolute; width: 760px; background: #fff; border-radius: 28px; padding: 18px 26px; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 40px;
        color: {NUIT}; box-shadow: 0 20px 60px rgba(0,0,0,0.5); border-left: 14px solid {CIEL}; }}
      .msg b {{ display: block; font-size: 28px; color: #0284C7; margin-bottom: 4px; }}
      .logo-chip {{ position: absolute; width: 200px; padding: 22px 0 16px; text-align: center; background: rgba(11,18,32,0.92); border: 5px solid #fff; border-radius: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5); }}
      .logo-chip img {{ width: 100px; height: 100px; }}
      .logo-chip span {{ display: block; margin-top: 10px; font-family: "Anton", sans-serif; font-size: 40px; color: #fff; }}
      .carte-hf {{ position: absolute; left: 90px; top: 360px; width: 900px; padding: 30px; background: #fff; border: 8px solid {NUIT}; border-radius: 36px; text-align: center;
        box-shadow: 0 30px 90px rgba(0,0,0,0.6); }}
      .hf-tete {{ display: flex; align-items: center; justify-content: center; gap: 22px; }}
      .hf-tete img {{ width: 90px; height: 90px; border-radius: 20px; }}
      .hf-tete b {{ font-family: "Anton", sans-serif; font-weight: 400; font-size: 110px; color: {NUIT}; }}
      .carte-hf > span {{ display: block; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 38px; color: #0284C7; margin-top: 4px; }}
      .hf-fen {{ margin-top: 16px; height: 220px; border-radius: 18px; overflow: hidden; border: 4px solid {NUIT}; }}
      .hf-fen video {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 0; }}
      .verdict {{ position: absolute; top: 380px; width: 460px; text-align: center; }}
      .mini-ecran {{ height: 300px; border-radius: 24px; overflow: hidden; border: 7px solid #fff; background: {NUIT}; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }}
      .mini-ecran video {{ width: 100%; height: 100%; object-fit: cover; }}
      .mini-ecran.barre {{ display: flex; align-items: center; justify-content: center; }}
      .mini-ecran.barre i {{ font-style: normal; font-size: 150px; filter: grayscale(1); opacity: 0.6; }}
      .verdict b {{ display: inline-block; margin-top: 16px; font-family: "Anton", sans-serif; font-weight: 400; font-size: 80px; padding: 4px 26px 0; border: 6px solid {NUIT}; color: {NUIT}; }}
      .verdict b.vert {{ background: {CIEL}; }}
      .verdict b.rouge {{ background: #FF6B6B; }}
      .schema {{ position: absolute; left: 40px; top: 380px; width: 1000px; display: flex; align-items: center; justify-content: center; gap: 14px; }}
      .schema .bloc {{ font-family: "Anton", sans-serif; font-size: 46px; color: {NUIT}; background: #fff; border: 6px solid {NUIT}; border-radius: 22px; padding: 30px 18px 22px; }}
      .schema i {{ font-style: normal; font-family: "Anton", sans-serif; font-size: 80px; color: #fff; -webkit-text-stroke: 8px {NUIT}; paint-order: stroke fill; }}
      .schema .bloc.vid {{ width: 240px; height: 420px; padding: 0; overflow: hidden; border-color: {CIEL}; }}
      .schema .bloc.vid video {{ width: 100%; height: 100%; object-fit: cover; }}
      .prix, .modele-c {{ position: absolute; top: 380px; width: 460px; padding: 30px 20px 26px; text-align: center; background: #fff; border: 8px solid {NUIT}; border-radius: 34px;
        box-shadow: 0 24px 70px rgba(0,0,0,0.55); }}
      .prix img, .modele-c img {{ width: 90px; height: 90px; }}
      .prix b, .modele-c b {{ display: block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 76px; line-height: 1.05; color: {NUIT}; margin-top: 8px; }}
      .prix span, .modele-c span {{ display: block; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 40px; color: {TERRA}; margin-top: 8px; }}
      .prix em {{ display: block; font-style: normal; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 28px; color: #64748b; margin-top: 6px; }}
      .modele-c.or {{ background: #FFF4D6; border-color: #b07d00; }}
      .alerte {{ position: absolute; left: 70px; top: 420px; width: 940px; text-align: center; font-family: "Anton", sans-serif; font-size: 80px; color: {NUIT}; background: #F2B705;
        border: 8px solid {NUIT}; padding: 14px 0 8px; transform: rotate(-2deg); }}
      .iso {{ position: absolute; left: 410px; top: 380px; }}
      .abo {{ position: absolute; left: 240px; top: 520px; width: 600px; height: 150px; }}
      .abo b {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-family: "Anton", sans-serif; font-weight: 400; font-size: 80px;
        color: #fff; background: #FF0033; border-radius: 28px; border: 7px solid {NUIT}; }}
      .abo b.ok {{ background: #fff; color: {NUIT}; }}
      .souris {{ position: absolute; left: 640px; top: 620px; width: 80px; height: 104px; opacity: 0; z-index: 12; }}
      .prochaine {{ position: absolute; left: 90px; top: 380px; width: 900px; padding: 30px; text-align: center; background: {NUIT}; border: 7px solid {CIEL}; border-radius: 36px;
        box-shadow: 0 30px 90px rgba(0,0,0,0.6); }}
      .prochaine span {{ display: inline-block; font-family: "Anton", sans-serif; font-size: 48px; color: {NUIT}; background: {CIEL}; padding: 4px 20px 0; }}
      .prochaine b {{ display: block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 84px; line-height: 1.05; color: #fff; margin-top: 16px; }}
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
      <div id="suivi"><div id="pousse"><div id="coup"><div id="cine"><div id="zoomh">
        <video id="studio" class="clip" src="assets/montage/studio.mp4" data-start="0" data-duration="{FIN - 0.6}" data-track-index="4" muted playsinline></video>
        <div id="mains">
{NL.join("          " + m for m in MAINS)}
        </div>
      </div></div></div></div></div>
      <div id="vignette"></div>
      <div id="tension" style="opacity: 0"></div>
      <div id="calques">
{NL.join("        " + h for h in HTML)}
      </div>
      <div id="titre" class="clip" data-layout-allow-overlap data-start="0" data-duration="{FIN}" data-track-index="0"><b>COMMENT JE FAIS MES <i>VIDÉOS</i></b></div>
      <div id="sous-titres" data-composition-id="sous-titres" data-composition-src="compositions/sous-titres.html" data-start="0" data-duration="{FIN}" data-track-index="3"
        data-width="1080" data-height="1920" style="z-index: 50"></div>
      <audio id="voix" src="assets/audio-voix.wav" data-start="0" data-duration="{FIN - 0.6}" data-volume="1" data-track-index="19"></audio>
{NL.join(MUSIQUES)}
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
print(f"durée {FIN} s, {len(SEG['coupes'])} coupes, {len(SONS)} bruitages, {len(MOTS)} mots")
