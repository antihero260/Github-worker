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
    hx, hy = min(max(hx, 220), 860), max(hy, 1700)
    hx, hy = -60 + hx * 1200 / 1080, -106 + hy * 1200 / 1080  # repère de la vidéo studio agrandie
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


# ================================================================ 2. ACCROCHE : une de ses vidéos par mot, puis retour face caméra
EX = ["enveloppes", "liste-depenser-moins", "edit-claude", "salaire-15", "site-3d-vertical", "effet-levier", "site-anime-vertical"]
for k, f in enumerate(EX):
    t0 = 0.0 if k == 0 else T(k)
    t1 = T(k + 1) if k + 1 < 7 else T(7) - 0.02
    video_plein(f"h{k}", f"assets/exemples/{f}.mp4", t0, t1, 0.2 + (k % 3) * 0.6)
    son(t0, tour(WH), 0.4 if k == 0 else 0.3, f"accroche {f}")
son(0.0, "trailer-impact", 0.45, "début")
HTML.append('<div id="h-tag" class="tag" style="left: 220px; top: 360px; opacity: 0">MES VIDÉOS</div>')
claque("#h-tag", 0.05, 2.2)
cache("#h-tag", T(7) - 0.05)
flash(T(7), 0.8)
son(T(7), "impact-basse", 0.45, "retour face caméra")

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
    cache(f"#lg{k}", T(40) - 0.1)
HTML.append('<div id="opus" class="tag" style="left: 70px; top: 640px; opacity: 0">OPUS 5.5</div>')
claque("#opus", T(20), 1.8)
son(T(20), "impact-tambour", 0.38, "Opus 5.5")
cache("#opus", T(29) - 0.05)
HTML.append('<div id="autres" class="tag clair" style="left: 300px; top: 640px; opacity: 0">+ BIEN D’AUTRES</div>')
claque("#autres", T(33), 1.8)
son(T(33), "pop-long", 0.36, "et bien d'autres")
cache("#autres", T(40) - 0.1)

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

# ================================================================ 6. Pourquoi ? Code ✓ / vidéo ✗
HTML.append(f'<div id="ok-code" class="verdict" style="left: 60px; opacity: 0"><div class="mini-ecran"><video id="code-v" class="clip" src="assets/video/code-html-bleu.mp4" '
            f'data-start="{r(T(64))}" data-duration="{r(T(78) - T(64))}" data-media-start="0.5" data-track-index="9" muted playsinline></video></div><b class="vert">CODE ✓</b></div>')
HTML.append('<div id="ko-vid" class="verdict" style="left: 540px; opacity: 0"><div class="mini-ecran barre"><i>🎬</i></div><b class="rouge">VIDÉO ✗</b></div>')
apparait("#ok-code", T(65), 80, 0.6)
son(T(65), "bonne-reponse", 0.42, "code ✓")
apparait("#ko-vid", T(71), 80, 0.6)
son(T(71), "buzzer-faux", 0.4, "vidéo ✗")
cache("#ok-code", T(78) - 0.1)
cache("#ko-vid", T(78) - 0.1)

# ================================================================ 7. HyperFrames intervient : références + code → vidéo
HTML.append('<div id="sch" class="schema" style="opacity: 0"><div id="s1" class="bloc" style="opacity: 0">RÉFÉRENCES</div><i id="s2" style="opacity: 0">+</i>'
            '<div id="s3" class="bloc" style="opacity: 0">CODE</div><i id="s4" style="opacity: 0">→</i>'
            f'<div id="s5" class="bloc vid" style="opacity: 0"><video id="sch-v" class="clip" src="assets/exemples/enveloppes.mp4" data-start="{r(T(98))}" '
            f'data-duration="{r(T(103) - T(98))}" data-media-start="0.5" data-track-index="9" muted playsinline></video></div></div>')
j(f'tl.set("#sch", {{ opacity: 1 }}, {r(T(85))});')
for sel, t in (("#s5", T(88)), ("#s1", T(94)), ("#s2", T(96)), ("#s3", T(98)), ("#s4", T(98) + 0.25)):
    apparait(sel, t, 40, 0.4, 0.18)
    son(t, tour(POPS), 0.38, "schéma")
son(T(88), "magie", 0.4, "la vidéo apparaît")
cache("#sch", T(99) - 0.05)
HTML.append('<div id="hfi" class="tag" style="left: 240px; top: 380px; opacity: 0">HYPERFRAMES</div>')
claque("#hfi", T(83), 1.8)
son(T(83), "impact-futur", 0.4, "HyperFrames intervient")
cache("#hfi", T(85))

# ================================================================ 8. Plusieurs possibilités : Claude Pro, Claude Max, chatbot
HTML.append('<div id="poss" class="tag clair" style="left: 150px; top: 420px; opacity: 0">PLUSIEURS POSSIBILITÉS</div>')
claque("#poss", T(101), 1.8)
son(T(101), "impact-tambour", 0.38, "plusieurs possibilités")
cache("#poss", T(103) - 0.05)
HTML.append('<div id="p1" class="prix" style="left: 60px; opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /><b>CLAUDE PRO</b><span>20 $ / mois</span><em>pour commencer</em></div>')
HTML.append('<div id="p2" class="prix" style="left: 560px; opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /><b>CLAUDE MAX</b><span>pour aller plus loin</span></div>')
apparait("#p1", T(103), 100, 0.5, 0.25)
son(T(110), "scanner-caisse", 0.42, "20 dollars")
apparait("#p2", T(124), 100, 0.5, 0.25)
son(T(124), "pieces-tintent", 0.4, "Claude Max")
cache("#p1", T(126) - 0.05)
cache("#p2", T(126) - 0.05)
HTML.append('<div id="p3" class="prix" style="left: 240px; width: 600px; opacity: 0"><b>💬 TON CHATBOT</b><span>installe la skill dedans</span></div>')
apparait("#p3", T(126), 100, 0.5, 0.25)
son(T(126), tour(WH), 0.4, "chatbot")
cache("#p3", T(137) - 0.05)

# ================================================================ 9. Attention : le modèle fait la différence
HTML.append('<div id="att" class="alerte" style="opacity: 0">⚠ L’OUTIL NE FAIT PAS TOUT</div>')
claque("#att", T(137), 1.8)
son(T(137), "alarme-alerte", 0.3, "attention", d=0.8)
cache("#att", T(144))
HTML.append('<div id="cle" class="slam petit" style="opacity: 0">LE MODÈLE<br>= LA CLÉ</div>')
claque("#cle", T(152), 2.0)
son(T(152), "impact-basse", 0.45, "le modèle")
cache("#cle", T(161) - 0.05)

# ================================================================ 10. Opus 5.5 / Fable 5.2
HTML.append('<div id="m1" class="modele-c" style="left: 60px; opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /><b>OPUS 5.5</b><span>très intéressant</span></div>')
HTML.append('<div id="m2" class="modele-c or" style="left: 560px; opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /><b>FABLE 5.2</b><span>vient de sortir</span></div>')
apparait("#m1", T(161), 100, 0.5, 0.25)
son(T(161), tour(WH), 0.4, "Opus 5.5")
apparait("#m2", T(171), 100, 0.5, 0.25)
son(T(171), "revelation", 0.42, "Fable 5.2")
HTML.append('<div id="mieux" class="tag" style="left: 600px; top: 760px; opacity: 0">★ PEUT FAIRE MIEUX</div>')
claque("#mieux", T(178), 1.8)
son(T(178), "cloche-succes", 0.4, "peut faire mieux")
for s_ in ("#m1", "#m2", "#mieux"):
    cache(s_, T(183) - 0.05)

# ================================================================ 11. 3D, 2D, isométrique : vrais exemples
video_plein("ex1", "assets/exemples/site-3d-vertical.mp4", T(183), T(187), 0.5)
video_plein("ex2", "assets/exemples/enveloppes.mp4", T(187), T(191), 1.0)
video_plein("ex3", "assets/exemples/classement-ia-vertical.mp4", T(191), T(196), 0.5)
FINS = (T(187), T(191), T(196))
for k, (txt, t) in enumerate((("3D", T(186)), ("2D", T(190)), ("3D ISOMÉTRIQUE", T(194)))):
    HTML.append(f'<div id="ty{k}" class="slam petit" style="top: 760px; opacity: 0">{txt}</div>')
    claque(f"#ty{k}", t, 2.2)
    son(t, tour(["impact-tambour", "impact-futur", "impact-whoosh"]), 0.42, f"type {txt}")
    cache(f"#ty{k}", FINS[k] - 0.02, 0.05)
    flash(t, 0.5)
HTML.append('<div id="iso" class="iso" style="opacity: 0"><svg viewBox="0 0 200 200" width="260" height="260"><path d="M100 20 L170 60 L100 100 L30 60 Z" fill="#7DD3FC" stroke="#0B1220" stroke-width="6" stroke-linejoin="round" />'
            '<path d="M30 60 L100 100 L100 180 L30 140 Z" fill="#38BDF8" stroke="#0B1220" stroke-width="6" stroke-linejoin="round" />'
            '<path d="M170 60 L100 100 L100 180 L170 140 Z" fill="#0284C7" stroke="#0B1220" stroke-width="6" stroke-linejoin="round" /></svg></div>')
apparait("#iso", T(196), 60, 0.3, 0.25)
son(T(196), "pop-long", 0.36, "et j'en passe")
j(f'tl.to("#iso svg", {{ rotation: 360, duration: 1.0, ease: "power2.inOut" }}, {r(T(196) + 0.1)});')
cache("#iso", T(199) - 0.05)

# ================================================================ 12. Abonne-toi + prochaine vidéo
HTML.append('<div id="proch" class="prochaine" style="opacity: 0"><span>PROCHAINE VIDÉO</span><b>Copier le style visuel<br>d’un autre créateur</b></div>')
apparait("#proch", T(204), 100, 0.5, 0.3)
son(T(204), "whoosh-tunnel", 0.42, "prochaine vidéo")
j(f'tl.fromTo("#fondu", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, immediateRender: false }}, {r(FIN - 0.4)});')
HTML.append('<div id="fondu" class="flash" style="background: #000"></div>')


# ================================================================ OBJETS QUI NAISSENT DANS LES MAINS (gestes détectés)
def geste(t0):
    g = min(GESTES, key=lambda e: abs(e[0] - t0))
    return g[0], g[3], g[4]


t, hx, hy = geste(6.8)
dans_la_main("mo1", '<img src="assets/img/logo-claude.svg" alt="" class="m-logo" />', t, hx, hy, T(29) - 0.1)
t, hx, hy = geste(14.53)
dans_la_main("mo2", '<b class="m-txt">GAME<br>CHANGER</b>', t, hx, hy, T(48) - 0.1, monte=230)
t, hx, hy = geste(18.87)
dans_la_main("mo3", '<b class="m-txt q">?</b>', t, hx, hy, T(58), zoom=False)
t, hx, hy = geste(22.93)
dans_la_main("mo4", '<b class="m-code">&lt;/&gt;</b>', t, hx, hy, T(78) - 0.1)
t, hx, hy = geste(28.27)
dans_la_main("mo5", '<img src="assets/img/logo-heygen.png" alt="" class="m-logo rond" />', t, hx, hy, T(94) - 0.1)
t, hx, hy = geste(31.4)
dans_la_main("mo6", '<b class="m-chip">IMAGES</b>', t, hx, hy, T(99) - 0.1, zoom=False, monte=190)
t, hx, hy = geste(33.13)
dans_la_main("mo7", '<b class="m-chip">CODE</b>', t, hx, hy, T(99) + 0.6, zoom=False, monte=120)
t, hx, hy = geste(40.87)
dans_la_main("mo11", '<b class="m-txt q">💬</b>', t, hx, hy, T(137) - 0.1, monte=210)
t, hx, hy = geste(52.0)
dans_la_main("mo9", '<b class="m-chip">OPUS 5.5</b>', t, hx, hy, T(171) - 0.1, zoom=False, monte=190)
t, hx, hy = geste(54.53)
dans_la_main("mo8", '<b class="m-chip or">FABLE 5.2</b>', t, hx, hy, T(183) - 0.1)
t, hx, hy = geste(63.4)
dans_la_main("mo10", '<b class="m-abo">S’ABONNER 🔔</b>', t, hx, hy, T(204) - 0.1, monte=210)


# ================================================================ TENSION (montées sonores et battements)
son(T(40) - 0.9, "riser-tech", 0.32, "montée vers le game changer", d=0.9)
son(T(78) - 0.9, "riser-trailer", 0.3, "montée vers HyperFrames intervient", d=0.9)
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
    .st-groupe {{ position: absolute; left: 40px; width: 1000px; top: 1240px; text-align: center; }}
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
      #suivi, #pousse, #coup, #zoomh, #mains {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      #pousse {{ transform-origin: 50% 45%; }}
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
      <div id="suivi"><div id="pousse"><div id="coup"><div id="zoomh">
        <video id="studio" class="clip" src="assets/montage/studio.mp4" data-start="0" data-duration="{FIN - 0.6}" data-track-index="4" muted playsinline></video>
        <div id="mains">
{NL.join("          " + m for m in MAINS)}
        </div>
      </div></div></div></div>
      <div id="vignette"></div>
      <div id="tension" style="opacity: 0"></div>
      <div id="calques">
{NL.join("        " + h for h in HTML)}
      </div>
      <div id="titre" class="clip" data-layout-allow-overlap data-start="0" data-duration="{FIN}" data-track-index="0"><b>COMMENT JE FAIS MES <i>VIDÉOS</i></b></div>
      <div id="sous-titres" data-composition-id="sous-titres" data-composition-src="compositions/sous-titres.html" data-start="0" data-duration="{FIN}" data-track-index="3"
        data-width="1080" data-height="1920" style="z-index: 50"></div>
      <audio id="voix" src="assets/audio-voix.wav" data-start="0" data-duration="{FIN - 0.6}" data-volume="1" data-track-index="19"></audio>
      <audio id="musique-1" src="assets/music/greed.mp3" data-start="0" data-duration="{FIN}" data-volume="0.22" data-track-index="20"></audio>
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
