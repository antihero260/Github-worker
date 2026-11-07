#!/usr/bin/env python3
"""Écrit index.html de « edit-site » (vidéo 18, v3) : un VRAI edit de hype sur l'univers IA / création de sites.

Pas de texte, pas de voix. Monté comme la vidéo de référence de l'utilisateur : plans très courts pleins de mouvement
(danse, breakdance, robots, moto, vitesse, VR, hologrammes, tunnels, code) coupés sur les temps, rafales de coupes sur le
drop, vrais sites (Spline, Framer, café, construction d'un site) seulement en flashs. Effets sur le rythme : coups de zoom,
flashs, inversion des couleurs au drop, barres de glitch, flou de fouet sur les demi-temps, secousses sur les kicks.

Son : extrait 25,130 → 40,281 s du son de la vidéo de référence (tools/temps.json : 24 temps, drop au temps 8).
Relancer ce script ÉCRASE index.html. (Version précédente « présentation du site VOLT » : refusée, « c'est un edit ».)
"""
import json
import math
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
TEMPS = json.loads((ICI / "tools/temps.json").read_text())
BEATS, KICKS, FIN = TEMPS["beats"], TEMPS["kicks"], TEMPS["fin"]


def T(x):
    n = int(math.floor(x))
    if n >= len(BEATS) - 1:
        return round(BEATS[-1], 3)
    return round(BEATS[n] + (x - n) * (BEATS[n + 1] - BEATS[n]), 3)


def r(x):
    return round(x, 3)


HTML, JS = [], []


def j(ligne):
    JS.append("      " + ligne)


# ================================================================ SON (bruitages discrets : c'est la musique qui porte l'edit)
SFX = ICI / "assets/sfx"
PICS = json.loads((SFX / "pics.json").read_text())
SONS = []


def son(t, nom, v=0.3, note="", sur_pic=True, d=None, fin=None):
    p = PICS[nom]
    debut = max(0.0, t - (p["pic"] if sur_pic else 0))
    duree = min(p["duree"], d or 99, FIN - debut, (fin - debut) if fin else 99)
    if duree > 0.05:
        SONS.append((r(debut), nom, round(v, 3), note, r(duree)))


TOURS = {}


def tour(liste):
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


WHOOSH = ["souffle-rapide", "swoosh-court", "fouet", "swoosh-vol", "balaie-rapide", "swoosh-accent", "balaie-court"]

# ================================================================ LES PLANS (temps musical, vidéo, départ dans le fichier, effet)
# effet : "coup" = coup de zoom ; "fouet" = flou filé latéral ; "drop" ; "pousse" = zoom continu
import subprocess


def duree(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(ICI / "assets/video" / f"{f}.mp4")], capture_output=True, text=True).stdout)


# Deux réserves : des plans en mouvement (sur les temps) et de vrais sites (sur les demi-temps et dans les rafales)
MOUVEMENT = ["danse-silhouette-rouge", "moto-wheelie", "danse-rue-choregraphie", "robot-danse", "skate-rampe", "danse-basket-nuit",
             "breakdance", "boxe-ko", "danse-lumieres", "conduite-nuit", "vr-combinaison", "skate-pirouette", "danse-hiphop-groupe",
             "feux-artifice", "basket-tir", "danse-fumee-violette", "moto-tunnel", "hologramme-gestes-vr", "danse-rue-cinq",
             "autoroute-nuit", "boxe-match", "danseur-dos", "foot-but", "vr-fille", "skate-bowl", "breakdance-2", "danse-silhouette-energie",
             "feux-explosions", "hologramme-main", "danse-fumee-2", "gamer-rgb", "voiture-rouge-spot", "robot-yeux", "hacker-darkweb"]
SITES = ["site-apple", "spline-ai", "site-stripe", "site-figma", "framer-ai", "site-notion", "site-webflow", "cafe-anims", "site-vercel",
         "volt-visite", "site-spline-site", "site-nike", "cafe-survol", "spline", "site-linear", "site-lusion", "site-igloo", "site-bruno-simon",
         "site-raycast", "site-bolt", "site-v0", "site-cursor", "site-replit", "site-locomotive", "site-activetheory", "site-cuberto",
         "site-dogstudio", "site-midjourney", "site-shopify", "site-spotify", "site-airbnb", "site-duolingo", "site-wix", "site-squarespace",
         "cafe-defile", "hologramme-navigateur"]
SITES = [f for f in SITES if (ICI / "assets/video" / f"{f}.mp4").exists()]
FX = ["rayons-lumiere", "neon-etincelles", "etincelles", "trou-de-ver", "tunnel-cubes", "lignes-3d", "paysage-neon", "neon-3d-route",
      "immeubles-futur", "retro-soleil", "ecrans-matrix", "code-chiffres", "fibre-optique", "neon-japon", "serveurs-lumieres"]
DUREES = {}
USAGES = {}
CURSEUR = {"m": 0, "s": 0, "x": 0}


def prend(reserve, cle):
    f = reserve[CURSEUR[cle] % len(reserve)]
    CURSEUR[cle] += 1
    return f


PLANS = [  # intro (temps 0 à 8) : la tension monte
    (0, "hacker-glitch", 0.2, "pousse"), (1, "ecrans-matrix", 0.3, "coup"), (2, "danse-fumee-violette", 0.2, "coup"),
    (3, "vr-mains-interface", 0.4, "coup"), (4, "hologramme-web", 1.0, "coup"), (5, "danse-silhouette-energie", 0.3, "coup"),
    (6, "lignes-3d", 0.5, "coup"), (6.5, "tunnel-cubes", 0.6, "fouet"), (7, "trou-de-ver", 0.3, "pousse"),
    (7.25, "rayons-lumiere", 0.4, "fouet"), (7.5, "neon-etincelles", 0.5, "fouet"), (7.75, "explosion-particules", 1.2, "fouet"),
    (8, "supernova", 1.6, "drop"),
]
# Rafale juste après le premier drop
for x in (8.25, 8.5, 8.75):
    PLANS.append((x, prend(SITES, "s"), None, "fouet"))
# Temps 9 à 38 : un plan en mouvement sur chaque temps, un vrai site sur le demi-temps, une rafale de 4 à la fin de chaque phrase
for n in range(9, 39):
    if n % 8 == 7:
        for q in (0, 0.25, 0.5, 0.75):
            PLANS.append((n + q, prend(SITES, "s") if q in (0.25, 0.75) else prend(FX, "x"), None, "fouet"))
    else:
        PLANS.append((n, prend(MOUVEMENT, "m"), None, "coup"))
        PLANS.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
# Temps 39 : le trou des basses → un seul plan qui pousse, puis noir
PLANS.append((39, "danse-silhouette-rouge", 1.0, "pousse"))
# Temps 40 : DEUXIÈME DROP, puis un plan par demi-temps jusqu'à la fin
PLANS.append((40, "feux-explosions", 0.5, "drop"))
for x in (40.25, 40.5, 40.75):
    PLANS.append((x, prend(SITES, "s"), None, "fouet"))
for n in range(41, 47):
    PLANS.append((n, prend(MOUVEMENT, "m"), None, "coup"))
    PLANS.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
PLANS.append((47, "hacker-glitch", 1.4, "pousse"))  # la boucle retombe sur le plan du début

# Départ dans chaque fichier : change à chaque réutilisation pour ne jamais revoir la même image
plans = []
for k, (x, f, depart, effet) in enumerate(PLANS):
    if f not in DUREES:
        DUREES[f] = duree(f)
    t0 = T(x)
    t1 = T(PLANS[k + 1][0]) if k + 1 < len(PLANS) else FIN
    if depart is None:
        u = USAGES.get(f, 0)
        marge = max(0.0, DUREES[f] - (t1 - t0) - 0.15)
        depart = round((0.3 + u * 1.1) % marge, 2) if marge > 0.3 else 0.0
        if f.startswith("site-") or f in ("spline-ai", "framer-ai", "spline", "cafe-defile", "volt-visite"):
            depart = round(min(marge, 1.2 + u * 1.3), 2)
    USAGES[f] = USAGES.get(f, 0) + 1
    plans.append((x, f, depart, effet))
PLANS = plans

vids = []
for k, (x, f, depart, effet) in enumerate(PLANS):
    t0 = T(x)
    t1 = T(PLANS[k + 1][0]) if k + 1 < len(PLANS) else FIN
    vids.append(f'<video id="p{k:02d}" class="clip ed-plan" src="assets/video/{f}.mp4" data-start="{t0}" data-duration="{r(t1 - t0)}" '
                f'data-media-start="{depart}" data-track-index="{1 + k % 2}" muted playsinline></video>')
    if effet == "pousse":
        j(f'tl.fromTo("#p{k:02d}", {{ scale: 1.0 }}, {{ scale: 1.18, duration: {r(t1 - t0)}, ease: "none", immediateRender: false }}, {t0});')
    elif effet == "coup":
        j(f'tl.fromTo("#p{k:02d}", {{ scale: 1.16 }}, {{ scale: 1.02, duration: 0.32, ease: "power3.out", immediateRender: false }}, {t0});')
        j(f'tl.to("#p{k:02d}", {{ scale: 1.08, duration: {r(max(0.05, t1 - t0 - 0.32))}, ease: "none" }}, {r(t0 + 0.32)});')
    elif effet == "fouet":
        sens = 1 if k % 2 else -1
        j(f'tl.fromTo("#p{k:02d}", {{ x: {sens * 140}, scale: 1.12, filter: "blur(14px)" }}, {{ x: 0, scale: 1.04, filter: "blur(0px)", duration: 0.1, ease: "power3.out", immediateRender: false }}, {t0});')
    elif effet == "drop":
        j(f'tl.fromTo("#p{k:02d}", {{ scale: 1.6 }}, {{ scale: 1.05, duration: 0.25, ease: "power4.out", immediateRender: false }}, {t0});')
    if k > 0:
        son(t0, tour(WHOOSH), 0.26 if effet == "fouet" else 0.3, f"coupe {f}")


# ================================================================ EFFETS SUR LE RYTHME
def flash(t, coul="#ffffff", op=0.5, d=0.07):
    k = len(HTML)
    HTML.append(f'<div id="fl{k}" class="ed-flash" style="background: {coul}"></div>')
    j(f'tl.set("#fl{k}", {{ opacity: {op} }}, {r(t)});')
    j(f'tl.to("#fl{k}", {{ opacity: 0, duration: {d}, ease: "power2.out" }}, {r(t + 0.034)});')


def glitch(t):
    k = len(HTML)
    barres = "".join(f'<i style="top: {y}px; height: {h}px; background: {c}; left: {x}px; width: {w}px"></i>'
                     for y, h, c, x, w in ((120, 30, "#ff2a55", 0, 1920), (380, 14, "#00e5ff", 300, 1620), (590, 46, "#ffffff", 0, 1200),
                                           (800, 20, "#ff2a55", 600, 1320), (960, 12, "#00e5ff", 0, 1920)))
    HTML.append(f'<div id="gl{k}" class="ed-glitch">{barres}</div>')
    j(f'tl.set("#gl{k}", {{ opacity: 0.85, x: -50 }}, {r(t)});')
    j(f'tl.set("#gl{k}", {{ opacity: 0.6, x: 40 }}, {r(t + 0.034)});')
    j(f'tl.set("#gl{k}", {{ opacity: 0 }}, {r(t + 0.1)});')


def secousse(t, amp=18, n=4):
    kf = [f'{{ x: {r(amp * (1 - k / n) * (1 if k % 2 == 0 else -1))}, y: {r(amp * 0.6 * (1 - k / n) * (-1 if k % 2 == 0 else 1))}, '
          f'rotation: {r(amp * 0.05 * (1 - k / n) * (1 if k % 2 else -1))}, duration: 0.035 }}' for k in range(n)]
    kf.append('{ x: 0, y: 0, rotation: 0, duration: 0.04 }')
    j(f'tl.to("#cam", {{ keyframes: [{", ".join(kf)}] }}, {r(t)});')


def inverse(t, d=0.067):
    j(f'tl.set("#cam", {{ filter: "invert(1) saturate(1.4)" }}, {r(t)});')
    j(f'tl.set("#cam", {{ filter: "invert(0) saturate(1.25) contrast(1.08)" }}, {r(t + d)});')


j('tl.set("#cam", { filter: "invert(0) saturate(1.25) contrast(1.08)" }, 0);')

# Intro : flash léger sur les temps pairs, la tension monte
for x in (2, 4, 6):
    flash(T(x), "#ffffff", 0.22, 0.08)
    secousse(T(x) + 0.01, 8, 3)
for x in (7.25, 7.5, 7.75):
    flash(T(x), "#ffffff", 0.3, 0.05)
son(T(8), "riser-synth", 0.34, "montée avant le drop", fin=T(8) + 0.05)
son(T(7.9), "aspiration", 0.24, "aspiration", fin=T(8))
HTML.append('<div id="noir-drop" class="ed-flash" style="background: #000"></div>')
j(f'tl.set("#noir-drop", {{ opacity: 1 }}, {T(7.9)});')
j(f'tl.set("#noir-drop", {{ opacity: 0 }}, {T(8)});')

# DROP
flash(T(8), "#ffffff", 1, 0.12)
inverse(T(8) + 0.1, 0.1)
glitch(T(8) + 0.2)
secousse(T(8), 34, 7)
son(T(8), "impact-basse", 0.55, "DROP")
son(T(8), "impact-futur", 0.32, "DROP")
for x in (8.25, 8.5, 8.75):
    flash(T(x), "#ffffff", 0.35, 0.05)

# Pendant le drop : coup de zoom de toute l'image sur chaque temps, flash coloré tous les 2 temps, inversion tous les 4
COULS = ["#ff2a55", "#00e5ff", "#dcfc1c", "#ffffff"]
for n in list(range(9, 39)) + list(range(41, 48)):
    j(f'tl.fromTo("#cam", {{ scale: {1.08 if n % 2 == 0 else 1.05} }}, {{ scale: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {T(n)});')
    if n % 2 == 0:
        flash(T(n), COULS[(n // 2) % 4], 0.28, 0.08)
    if n % 8 == 0:
        inverse(T(n), 0.034)
        glitch(T(n) + 0.05)
        son(T(n), "impact-tambour", 0.3, "coup fort")
    secousse(T(n) + 0.01, 14 if n % 2 == 0 else 9, 3)
for n in range(15, 39, 8):
    for q in (0.25, 0.5, 0.75):
        flash(T(n + q), "#ffffff", 0.3, 0.05)
# Trou des basses (temps 39) puis DEUXIÈME DROP (temps 40)
son(T(40), "riser-tech", 0.3, "remontée avant le 2e drop", fin=T(40) + 0.05)
HTML.append('<div id="noir-drop2" class="ed-flash" style="background: #000"></div>')
j(f'tl.set("#noir-drop2", {{ opacity: 1 }}, {T(39.88)});')
j(f'tl.set("#noir-drop2", {{ opacity: 0 }}, {T(40)});')
flash(T(40), "#ffffff", 1, 0.12)
inverse(T(40) + 0.1, 0.1)
glitch(T(40) + 0.2)
secousse(T(40), 34, 7)
son(T(40), "impact-basse", 0.55, "2e DROP")
son(T(40), "tonnerre-transition", 0.3, "2e DROP")
for x in (40.25, 40.5, 40.75):
    flash(T(x), "#ffffff", 0.35, 0.05)
# Petites secousses sur les kicks entre les temps
for k in KICKS:
    if T(8) < k < FIN - 0.1 and not (T(39) - 0.05 < k < T(40)) and min(abs(k - T(n)) for n in range(8, 49)) > 0.08:
        j(f'tl.to("#cam", {{ keyframes: [{{ y: 8, duration: 0.03 }}, {{ y: -5, duration: 0.03 }}, {{ y: 0, duration: 0.04 }}] }}, {r(k)});')
# Fin : le silence des basses (temps 23) → zoom lent, puis la boucle repart sur la même vidéo qu'au début
glitch(FIN - 0.1)
son(FIN - 0.05, "rewind-glitch", 0.3, "la boucle repart")

# ================================================================ ÉCRITURE
sons_html, libre = [], []
for k, (t0, nom, v, note, d) in enumerate(sorted(SONS)):
    piste = next((i for i, f in enumerate(libre) if f <= t0), None)
    if piste is None:
        libre.append(0)
        piste = len(libre) - 1
    libre[piste] = t0 + d + 0.01
    sons_html.append(f'<audio id="sfx-{k + 1:03d}" src="assets/sfx/{nom}.mp3" data-start="{t0}" data-duration="{d}" data-volume="{v}" '
                     f'data-track-index="{30 + piste}"></audio><!-- {note} -->')

NL = "\n"
page = f"""<!doctype html>
<html lang="fr" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      /* Edit rythmé (vidéo 18) : aucun texte, tout est calé sur les temps de la musique (tools/temps.json). */
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #fond {{ position: absolute; inset: 0; background: #000; }}
      #cam {{ position: absolute; left: -70px; top: -70px; width: 2060px; height: 1220px; overflow: hidden; transform-origin: 50% 50%; }}
      .ed-plan {{ position: absolute; left: 70px; top: 70px; width: 1920px; height: 1080px; object-fit: cover; transform-origin: 50% 50%; }}
      #vignette {{ position: absolute; inset: 0; background: radial-gradient(ellipse 75% 70% at 50% 50%, rgba(0, 0, 0, 0) 55%, rgba(0, 0, 0, 0.55) 100%); }}
      .ed-flash {{ position: absolute; inset: 0; opacity: 0; }}
      .ed-glitch {{ position: absolute; inset: 0; opacity: 0; mix-blend-mode: screen; }}
      .ed-glitch i {{ position: absolute; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="1920" data-height="1080">
      <div id="fond" class="clip" data-start="0" data-duration="{FIN}" data-track-index="0"></div>
      <div id="cam">
{NL.join("        " + v for v in vids)}
        <div id="vignette"></div>
      </div>
{NL.join("      " + h for h in HTML)}
      <audio id="musique" src="assets/music/son-edit.wav" data-start="0" data-duration="{FIN}" data-volume="1" data-track-index="10"></audio>
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
print(f"edit v3 écrit : {len(PLANS)} plans, {len(SONS)} bruitages, {len(JS)} lignes d'animation, fin à {FIN} s")
