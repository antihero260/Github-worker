#!/usr/bin/env python3
"""Écrit index.html de « edit-site » (vidéo 18, v5) : edit « de malade » sur l'univers IA / sites / vitesse.

Pas de texte, pas de voix. Musique choisie par l'utilisateur : « Phonk Drift Racing Montage » – Alex Morgan (CC BY 4.0),
extrait 86,376 → 120,880 s = 80 temps à ≈139 BPM (tools/temps.json) :
  temps 0–23  : MONTÉE EN TENSION (demande de l'utilisateur) : image sombre et désaturée, un plan tous les 2 temps, puis
                chaque temps, chaque demi-temps, chaque quart de temps ; la caméra avance, les secousses et les flashs
                grandissent, les couleurs reviennent ; noir juste avant le drop ;
  temps 24    : DROP : flash, inversion, glitch, grosse secousse, rafale ;
  temps 24–51 : un plan en mouvement sur chaque temps, un vrai site sur les demi-temps impairs, rafale de 4 en fin de phrase ;
  temps 52–55 : coupure des basses → nouvelle petite montée (plans qui accélèrent, zoom) ; noir ;
  temps 56    : 2e DROP ; temps 56–79 : un plan par demi-temps (plan en mouvement / vrai site), rafales ; boucle.
Relancer ce script ÉCRASE index.html.
"""
import json
import math
import subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
TEMPS = json.loads((ICI / "tools/temps.json").read_text())
BEATS, KICKS, FIN = TEMPS["beats"], TEMPS["kicks"], TEMPS["fin"]
DROP, COUPURE, DROP2, NB = TEMPS["drop"], TEMPS["coupure"], TEMPS["drop2"], len(TEMPS["beats"]) - 1


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


# ================================================================ SON
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

# ================================================================ RÉSERVES DE PLANS
VID = ICI / "assets/video"


def existe(f):
    return (VID / f"{f}.mp4").exists()


TENSION = ["eclair-nuages", "fumee-mouvement", "boxeur-sombre", "hacker-nuit", "eclairs-nuit", "encre-liquide", "danseur-dos",
           "hacker-masque-ecrans", "fumee-tourbillon", "serveurs-lumieres", "voiture-rouge-gros-plan", "coureur-depart",
           "doigts-tapent", "eclair-frappe", "trafic-pluie", "lasers-lunettes", "voiture-spot", "drapeau-course", "code-chiffres",
           "tunnel-trafic", "hologramme-adn", "ecrans-code", "fibre-optique", "eclair-ville", "moto-accelere", "serveurs-attaque",
           "neon-japon", "avenues-nuit", "voiture-compteur", "tokyo-train-nuit", "rayons-lumiere", "trou-de-ver", "tunnel-cubes",
           "neon-etincelles", "lignes-3d", "tunnel-rouge"]
MOUVEMENT = ["rally-terre", "danse-silhouette-rouge", "moto-wheelie", "foule-saute", "voitures-vitesse", "breakdance", "boxe-ko",
             "festival-saute", "danse-rue-choregraphie", "motos-route", "skate-rampe", "karting", "foule-pogo", "robot-danse",
             "course-neige", "danse-basket-nuit", "moto-tunnel-2", "voiture-blanche-coucher", "boxe-match", "foule-bras",
             "snowboard", "danse-lumieres", "rally-foret", "moto-wheelie-2", "dj-scene", "skate-pirouette", "conduite-nuit",
             "motos-terre", "danse-hiphop-groupe", "feux-artifice", "voiture-rouge-route", "basket-tir", "vr-combinaison",
             "danseur-couleurs", "foot-but", "lumieres-scene", "skate-bowl-2", "jogging-pont", "breakdance-2", "autoroute-nuit",
             "danse-rue-cinq", "vr-fille", "danse-fumee-violette", "skate-bowl", "explosion-feu", "danse-silhouette-energie",
             "moto-tunnel", "hologramme-gestes-vr", "trafic-nuit-tourne", "ville-nuit-aerien", "danse-fumee-2", "gamer-rgb"]
SITES = ["site-apple", "spline-ai", "site-stripe", "site-figma", "framer-ai", "site-notion", "site-webflow", "cafe-anims", "site-vercel",
         "volt-visite", "site-spline-site", "site-nike", "cafe-survol", "spline", "site-raycast", "site-bolt", "site-v0", "site-cursor",
         "site-locomotive", "site-cuberto", "site-midjourney", "site-shopify", "site-duolingo", "site-wix", "site-squarespace",
         "site-bruno-simon", "cafe-defile", "hologramme-navigateur", "hologramme-web", "hologramme-paiement"]
FX = ["etincelles", "fumee-tourbillon", "eclair-frappe", "rayons-lumiere", "paysage-neon", "neon-3d-route", "immeubles-futur",
      "retro-soleil", "ecrans-matrix", "explosion-particules", "supernova", "main-hologramme", "appareils-futur", "eclair-nuages"]
TENSION, MOUVEMENT, SITES, FX = ([f for f in L if existe(f)] for L in (TENSION, MOUVEMENT, SITES, FX))
CURSEUR = {}


def prend(reserve, cle):
    k = CURSEUR.get(cle, 0)
    CURSEUR[cle] = k + 1
    return reserve[k % len(reserve)]


PLANS = []  # (temps, vidéo, départ ou None, effet)
# ---- MONTÉE EN TENSION (temps 0 à 23)
for x in range(0, 8, 2):
    PLANS.append((x, prend(TENSION, "t"), None, "pousse"))
for x in range(8, 16):
    PLANS.append((x, prend(TENSION, "t"), None, "coup"))
for n in range(16, 20):
    PLANS.append((n, prend(TENSION, "t"), None, "coup"))
    PLANS.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
for n in range(20, 23):
    for q in (0, 0.25, 0.5, 0.75):
        PLANS.append((n + q, prend(SITES, "s") if q in (0.25, 0.75) else prend(TENSION, "t"), None, "fouet"))
PLANS.append((23, "danse-silhouette-rouge", 0.8, "pousse"))
PLANS.append((23.5, "explosion-particules", 1.2, "fouet"))
# ---- DROP (temps 24) et phrases suivantes
PLANS.append((DROP, "supernova", 1.6, "drop"))
for x in (24.25, 24.5, 24.75):
    PLANS.append((x, prend(SITES, "s"), None, "fouet"))
for n in range(DROP + 1, COUPURE):
    if (n - DROP) % 8 == 7:
        for q in (0, 0.25, 0.5, 0.75):
            PLANS.append((n + q, prend(SITES, "s") if q in (0.25, 0.75) else prend(FX, "x"), None, "fouet"))
    else:
        PLANS.append((n, prend(MOUVEMENT, "m"), None, "coup"))
        if n % 2 == 1:
            PLANS.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
# ---- COUPURE DES BASSES (temps 52 à 55) : nouvelle petite montée
PLANS.append((COUPURE, "eclair-frappe", 0.6, "pousse"))
PLANS.append((COUPURE + 1, prend(TENSION, "t"), None, "pousse"))
for x in (54, 54.5, 55, 55.25, 55.5, 55.75):
    PLANS.append((x, prend(SITES, "s") if x in (54.5, 55.25, 55.75) else prend(TENSION, "t"), None, "fouet"))
# ---- 2e DROP (temps 56 → fin) : un plan par demi-temps
PLANS.append((DROP2, "explosion-feu", 0.4, "drop"))
for x in (56.25, 56.5, 56.75):
    PLANS.append((x, prend(SITES, "s"), None, "fouet"))
for n in range(DROP2 + 1, NB - 1):
    if (n - DROP2) % 8 == 7:
        for q in (0, 0.25, 0.5, 0.75):
            PLANS.append((n + q, prend(SITES, "s") if q in (0.25, 0.75) else prend(FX, "x"), None, "fouet"))
    else:
        PLANS.append((n, prend(MOUVEMENT, "m"), None, "coup"))
        PLANS.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
PLANS.append((NB - 1, "eclair-nuages", 0.3, "pousse"))  # retour au calme : la boucle repart sur la montée

DUREES, USAGES = {}, {}


def duree(f):
    if f not in DUREES:
        DUREES[f] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                          str(VID / f"{f}.mp4")], capture_output=True, text=True).stdout)
    return DUREES[f]


vids = []
for k, (x, f, depart, effet) in enumerate(PLANS):
    t0 = T(x)
    t1 = T(PLANS[k + 1][0]) if k + 1 < len(PLANS) else FIN
    if depart is None:
        u = USAGES.get(f, 0)
        marge = max(0.0, duree(f) - (t1 - t0) - 0.15)
        if f.startswith("site-") or f in ("spline-ai", "framer-ai", "spline", "cafe-defile", "volt-visite", "cafe-anims", "cafe-survol"):
            depart = round(min(marge, 1.2 + u * 1.3), 2)
        else:
            depart = round((0.3 + u * 1.1) % marge, 2) if marge > 0.3 else 0.0
    USAGES[f] = USAGES.get(f, 0) + 1
    vids.append(f'<video id="p{k:03d}" class="clip ed-plan" src="assets/video/{f}.mp4" data-start="{t0}" data-duration="{r(t1 - t0)}" '
                f'data-media-start="{depart}" data-track-index="{1 + k % 2}" muted playsinline></video>')
    pid = f"#p{k:03d}"
    if effet == "pousse":
        j(f'tl.fromTo("{pid}", {{ scale: 1.0 }}, {{ scale: 1.2, duration: {r(t1 - t0)}, ease: "none", immediateRender: false }}, {t0});')
    elif effet == "coup":
        j(f'tl.fromTo("{pid}", {{ scale: 1.16 }}, {{ scale: 1.02, duration: 0.26, ease: "power3.out", immediateRender: false }}, {t0});')
        if t1 - t0 > 0.3:
            j(f'tl.to("{pid}", {{ scale: 1.08, duration: {r(t1 - t0 - 0.26)}, ease: "none" }}, {r(t0 + 0.26)});')
    elif effet == "fouet":
        sens = 1 if k % 2 else -1
        j(f'tl.fromTo("{pid}", {{ x: {sens * 140}, scale: 1.12, filter: "blur(14px)" }}, {{ x: 0, scale: 1.04, filter: "blur(0px)", duration: 0.08, ease: "power3.out", immediateRender: false }}, {t0});')
    elif effet == "drop":
        j(f'tl.fromTo("{pid}", {{ scale: 1.6 }}, {{ scale: 1.05, duration: 0.25, ease: "power4.out", immediateRender: false }}, {t0});')
    if k > 0 and not (x != int(x) and (x * 4) % 2 == 1):  # pas de whoosh sur les quarts de temps
        son(t0, tour(WHOOSH), 0.16 if effet == "fouet" else 0.26, f"coupe {f}")


# ================================================================ EFFETS
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


NORMAL = "invert(0) saturate(1.25) contrast(1.08) brightness(1)"


def inverse(t, d=0.067):
    j(f'tl.set("#cam", {{ filter: "invert(1) saturate(1.4) contrast(1.08) brightness(1)" }}, {r(t)});')
    j(f'tl.set("#cam", {{ filter: "{NORMAL}" }}, {r(t + d)});')


def noir(t0, t1):
    k = len(HTML)
    HTML.append(f'<div id="nr{k}" class="ed-flash" style="background: #000"></div>')
    j(f'tl.set("#nr{k}", {{ opacity: 1 }}, {r(t0)});')
    j(f'tl.set("#nr{k}", {{ opacity: 0 }}, {r(t1)});')


def drop(t, nom):
    flash(t, "#ffffff", 1, 0.12)
    inverse(t + 0.1, 0.1)
    glitch(t + 0.2)
    secousse(t, 36, 7)
    son(t, "impact-basse", 0.55, nom)
    son(t, "impact-futur", 0.32, nom)
    son(t, "tonnerre-transition", 0.26, nom)
    for q in (0.25, 0.5, 0.75):
        flash(t + q * (T(DROP + 1) - T(DROP)), "#ffffff", 0.35, 0.05)


# ---- La montée en tension : couleurs éteintes qui reviennent, caméra qui avance, secousses et flashs qui grandissent
j(f'tl.fromTo("#cam", {{ filter: "invert(0) saturate(0.25) contrast(1.15) brightness(0.62)" }}, {{ filter: "{NORMAL}", duration: {T(23)}, ease: "power2.in", immediateRender: true }}, 0);')
j(f'tl.fromTo("#cam", {{ scale: 1 }}, {{ scale: 1.14, duration: {r(T(23.9))}, ease: "power3.in", immediateRender: true }}, 0);')
j(f'tl.set("#cam", {{ scale: 1 }}, {T(DROP)});')
for n in range(8, 24, 2):
    flash(T(n), "#ffffff", round(0.08 + 0.25 * (n - 8) / 16, 2), 0.07)
for n in range(12, 24):
    secousse(T(n) + 0.01, round(4 + 14 * (n - 12) / 12, 1), 3)
son(T(4), "battements", 0.34, "cœur qui bat (tension)")
son(T(12), "roulement-suspense", 0.26, "roulement (tension)")
son(T(DROP), "riser-trailer", 0.36, "montée avant le drop", fin=T(DROP) + 0.05)
son(T(DROP), "riser-synth", 0.26, "montée avant le drop", fin=T(DROP) + 0.05)
son(T(23.75), "aspiration", 0.26, "aspiration", fin=T(DROP))
noir(T(23.85), T(DROP))
drop(T(DROP), "DROP")

# ---- Pendant les drops : coup de zoom sur chaque temps, flash coloré tous les 2 temps, inversion + glitch toutes les phrases
COULS = ["#ff2a55", "#00e5ff", "#dcfc1c", "#ffffff"]
for n in list(range(DROP + 1, COUPURE)) + list(range(DROP2 + 1, NB)):
    j(f'tl.fromTo("#cam", {{ scale: {1.08 if n % 2 == 0 else 1.05} }}, {{ scale: 1, duration: 0.26, ease: "power3.out", immediateRender: false }}, {T(n)});')
    if n % 2 == 0:
        flash(T(n), COULS[(n // 2) % 4], 0.26, 0.07)
    if (n - DROP) % 8 == 0:
        inverse(T(n), 0.034)
        glitch(T(n) + 0.05)
        son(T(n), "impact-tambour", 0.3, "coup fort")
    secousse(T(n) + 0.01, 14 if n % 2 == 0 else 9, 3)
    if (n - DROP) % 8 == 7:
        for q in (0.25, 0.5, 0.75):
            flash(T(n + q), "#ffffff", 0.3, 0.05)
# ---- Coupure des basses : petite montée, puis 2e drop
j(f'tl.fromTo("#cam", {{ scale: 1 }}, {{ scale: 1.12, duration: {r(T(DROP2 - 0.1) - T(COUPURE))}, ease: "power3.in", immediateRender: false }}, {T(COUPURE)});')
j(f'tl.set("#cam", {{ scale: 1 }}, {T(DROP2)});')
for x in (54, 54.5, 55, 55.25, 55.5, 55.75):
    flash(T(x), "#ffffff", 0.28, 0.05)
    secousse(T(x) + 0.01, 10, 3)
son(T(DROP2), "riser-tech", 0.32, "remontée avant le 2e drop", fin=T(DROP2) + 0.05)
noir(T(DROP2 - 0.15), T(DROP2))
drop(T(DROP2), "2e DROP")
# ---- Petites secousses sur les kicks entre les temps
for k in KICKS:
    if T(DROP) < k < FIN - 0.1 and not (T(COUPURE) - 0.05 < k < T(DROP2)) and min(abs(k - T(n)) for n in range(DROP, NB + 1)) > 0.06:
        j(f'tl.to("#cam", {{ keyframes: [{{ y: 7, duration: 0.025 }}, {{ y: -4, duration: 0.025 }}, {{ y: 0, duration: 0.03 }}] }}, {r(k)});')
glitch(FIN - 0.1)

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
      /* Edit rythmé (vidéo 18, v5) : aucun texte, tout est calé sur les temps de la musique (tools/temps.json). */
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
uniques = len({f for _, f, _, _ in PLANS})
sites = len({f for _, f, _, _ in PLANS if f in SITES})
print(f"edit v5 écrit : {len(PLANS)} plans, {uniques} vidéos différentes dont {sites} sites, {len(SONS)} bruitages, fin à {FIN} s")
