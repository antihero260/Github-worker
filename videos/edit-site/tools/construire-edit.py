#!/usr/bin/env python3
"""Écrit index.html de « edit-site » (vidéo 19, v7) : edit PRO cinématique sur « AVANGARD (Slowed) » (LONOWN).

Demande : « le 12, et je compte sur toi : toujours plus de travail et d'expertise », avec des extraits de films (libres :
Tears of Steel et Sintel de la Blender Foundation, CC BY) et les vidéos de la NASA (domaine public).
Son (tools/temps.json) : grille de 0,509 s calée sur le drop (16,333 s, temps 32). Intro sombre (0–15), attaques (15,5–27),
montée (28–31,8), DROP (32–47), outro sans basses (48–58).
Effets : tous ceux de la v6 (étalonnage, bandes cinémascope, grain, vignette, fuites de lumière, RGB, zoom traversant,
rotation, filé, stutter, écrans partagés, vrais ralentis) + fondus enchaînés, arrêts sur image, traînées de mouvement (echo),
effet miroir, ouverture en iris, bascule 3D, flou de zoom radial au drop, micro-éclairs sur les caisses claires.
Relancer ce script ÉCRASE index.html. (Version précédente sur Montagem Rugada : tools/construire-edit-v6-rugada.py.)
"""
import json
import math
import subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
TEMPS = json.loads((ICI / "tools/temps.json").read_text())
BEATS, KICKS, FIN, DROP = TEMPS["beats"], TEMPS["kicks"], TEMPS["fin"], TEMPS["drop"]
NB = len(BEATS) - 1


def T(x):
    n = int(math.floor(x))
    if n >= NB:
        return round(BEATS[-1], 3)
    return round(BEATS[n] + (x - n) * (BEATS[n + 1] - BEATS[n]), 3)


def r(x):
    return round(x, 3)


HTML, JS, OVER = [], [], []


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

# ================================================================ RÉSERVES (aucune vidéo de cuisine ni d'intérieur)
VID = ICI / "assets/video"


def garde(liste):
    return [f for f in liste if (VID / f"{f}.mp4").exists()]


SOMBRE = garde(["film-tos-ville-sombre", "nasa-artemis-allumage", "film-tos-invasion", "boxeur-sombre", "film-tos-ruines",
                "film-sintel-grotte", "film-tos-vaisseau", "eclair-nuages", "film-tos-labo", "silhouettes-fumee", "voiture-spot",
                "film-sintel-aile", "danseur-dos", "film-tos-soldat", "eclairs-nuit", "hacker-masque-ecrans"])
FILMS = garde(["film-tos-cyborg", "film-tos-robot-geant", "film-tos-bras-robot", "film-tos-hologramme", "film-tos-interface",
               "film-tos-fil-de-fer", "film-tos-projection", "film-tos-machines", "film-tos-armure", "film-tos-explosion",
               "film-tos-champ-bataille", "film-tos-arme", "film-tos-cerveau", "film-tos-holo-2", "film-tos-lumiere",
               "film-tos-robot", "film-sintel-dragon", "film-sintel-combat", "film-sintel-lutte", "film-sintel-regard",
               "film-sintel-course", "film-sintel-dragon-2", "film-sintel-rouge", "film-sintel-lance"])
NASA = garde(["nasa-artemis-feu", "nasa-booster-jet", "nasa-rocketlab-moteur", "nasa-artemis-decolle", "nasa-booster-face",
              "nasa-separation-1", "nasa-artemis-flamme", "nasa-booster-tuyere", "nasa-rocketlab-onboard", "nasa-artemis-lumiere",
              "nasa-booster-feu", "nasa-rocketlab-decolle", "nasa-separation-2", "nasa-booster-fumee", "nasa-artemis-tour"])
MOUVEMENT = garde(["danse-techno-neon", "moto-wheelie", "boxe-coups", "foule-saute", "rally-terre", "breakdance", "lasers-cyberpunk",
                   "voitures-vitesse", "festival-saute", "boxe-direct", "danse-rue-choregraphie", "skate-rampe", "foule-pogo",
                   "filles-barres-lumiere", "mma-combat", "danse-objectif", "karting", "danseur-masque-neon", "moto-tunnel-2",
                   "danse-silhouette-rouge", "boule-feu", "flammes-noir", "danse-fumee-violette", "skate-pirouette", "explosion-feu",
                   "danse-lumieres", "coureur-ville", "etincelles-feu", "lave-particules", "boxe-ko"])
SITES = garde(["site-lamborghini", "spline-ai", "site-apple", "site-playstation", "framer-ai", "site-nvidia", "site-stripe",
               "site-mclaren", "site-visionpro", "site-figma", "site-xbox", "site-webflow", "site-netflix", "site-spline-site",
               "site-ubisoft", "site-vercel", "site-riot", "site-dji", "site-raycast", "site-iphone", "site-bolt", "site-discord",
               "site-gopro", "site-v0", "site-cursor", "site-twitch", "site-locomotive", "site-cuberto", "site-midjourney",
               "site-dribbble", "site-shopify", "site-notion", "site-wix", "site-squarespace", "spline", "volt-visite"])
RAMPES = garde([f"rampe-{n}" for n in ("moto-wheelie-2", "boxe-direct", "breakdance", "foule-pogo", "skate-rampe", "karting")])
CURSEUR = {}


def prend(reserve, cle):
    k = CURSEUR.get(cle, 0)
    CURSEUR[cle] = k + 1
    return reserve[k % len(reserve)]


def melange(n):
    """Alterne films, NASA et plans en mouvement pour que deux plans voisins ne se ressemblent jamais."""
    return [lambda: prend(FILMS, "f"), lambda: prend(MOUVEMENT, "m"), lambda: prend(NASA, "n"), lambda: prend(MOUVEMENT, "m")][n % 4]()


# ================================================================ LE MONTAGE (temps musical, vidéo, départ ou None, effet)
# effets : fondu (fondu enchaîné), pousse, coup, fouet, zoom (traversant), spin, tilt (bascule 3D), iris, miroir, echo
#          (traînée), gel (arrêt sur image), drop (avec flou de zoom radial), stutter, rampe, split
P = []
# A. Intro sombre (0 → 7,9 s) : un plan tous les 2 temps, fondus enchaînés, bandes cinémascope, image froide
P.append((0, "film-tos-robot", 1.0, "pousse"))
for n in (2, 4, 6):
    P.append((n, prend(SOMBRE, "o"), None, "fondu"))
for n in range(8, 15):  # la deuxième moitié de l'intro s'accélère déjà : un plan par temps
    P.append((n, prend(SOMBRE, "o") if n % 2 else melange(n), None, "fondu" if n < 11 else ["coup", "tilt", "zoom"][n % 3]))
# B. Les attaques arrivent (7,94 s → 14 s) : un plan par temps, transitions variées, arrêts sur image sur les attaques
P.append((15.5, "film-tos-explosion", 0.4, "drop"))
for n in range(16, 28):
    eff = ["coup", "tilt", "fouet", "zoom", "coup", "spin"][n % 6]
    P.append((n, melange(n), None, eff))
    if n >= 18 and n not in (22, 24):
        P.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
P += [(22.5, "GEL:gel-film-tos-robot-geant", None, "gel"), (24, "GEL:gel-nasa-booster-face", None, "gel")]
# C. La montée (14 → 16,3 s) : de plus en plus vite, fente noire, stroboscope d'images
P += [(28, melange(28), None, "zoom"), (28.5, prend(SITES, "s"), None, "fouet"), (29, melange(29), None, "spin"),
      (29.5, prend(SITES, "s"), None, "fouet"), (30, melange(30), None, "tilt"), (30.25, prend(SITES, "s"), None, "fouet"),
      (30.5, melange(31), None, "zoom"), (30.75, prend(SITES, "s"), None, "fouet")]
for q in range(5):
    P.append((round(31 + q / 6, 4), prend(SITES, "s") if q % 2 else melange(q), None, "fouet"))
# D. DROP (16,33 s → 24,5 s) : un plan par demi-temps, rafales au quart de temps, effets pro
P.append((32, "nasa-booster-allumage", 0.4, "drop"))
for x in (32.25, 32.5, 32.75):
    P.append((x, prend(SITES, "s"), None, "fouet"))
P.append((33, prend(RAMPES, "r"), 0.0, "rampe"))
P += [(34.5, "GEL:gel-boxe-direct", None, "gel"), (34.75, "GEL:gel-film-tos-cyborg", None, "gel"),
      (35, "GEL:gel-danse-silhouette-rouge", None, "gel")]  # le triple kick : trois arrêts sur image
P.append((35.5, prend(SITES, "s"), None, "fouet"))
SPECIAUX = {37: "echo", 41: "miroir", 43: "iris", 45: "echo", 46: "tilt"}
for n in range(36, 48):
    if n == 40:
        P.append((40, "SPLIT", None, "split"))
        P.append((40.5, prend(SITES, "s"), None, "fouet"))
        continue
    if n in (39, 47):  # fin de demi-phrase : rafale au quart de temps
        for q in (0, 0.25, 0.5, 0.75):
            P.append((n + q, prend(SITES, "s") if q in (0.25, 0.75) else melange(int(n + q * 4)), None, "fouet"))
        continue
    P.append((n, melange(n), None, SPECIAUX.get(n, ["coup", "zoom", "spin", "coup"][n % 4])))
    P.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
    if n % 2 == 0 and n not in SPECIAUX:
        P.append((n + 0.75, melange(n + 1), None, "fouet"))
# E. Outro (24,5 → 29,8 s) : les basses s'arrêtent, arrêt sur image, puis ralentis cinéma en fondus enchaînés, boucle
P.append((48, "GEL:gel-nasa-artemis-feu", None, "gel"))
P += [(49, "film-sintel-coucher", 0.2, "fondu"), (51, "nasa-artemis-ciel", 0.4, "fondu"), (53, "film-tos-fil-de-fer", 0.3, "echo"),
      (55, "nasa-rocketlab-ciel", 0.2, "fondu"), (57, "film-tos-robot", 0.3, "fondu")]
P.sort(key=lambda z: z[0])

DUREES, USAGES = {}, {}


def duree(f):
    if f not in DUREES:
        DUREES[f] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                          str(VID / f"{f}.mp4")], capture_output=True, text=True).stdout)
    return DUREES[f]


def depart_auto(f, d):
    u = USAGES.get(f, 0)
    USAGES[f] = u + 1
    marge = max(0.0, duree(f) - d - 0.12)
    if f.startswith("site-") or f in ("spline-ai", "framer-ai", "spline", "volt-visite"):
        return round(min(marge, 1.0 + u * 1.2), 2)
    return round((0.3 + u * 0.9) % marge, 2) if marge > 0.3 else 0.0


def video(vid, f, t0, d, depart, piste, style="", cls="ed-plan"):
    return (f'<video id="{vid}" class="clip {cls}" src="assets/video/{f}.mp4" data-start="{r(t0)}" data-duration="{r(d)}" '
            f'data-media-start="{depart}" data-track-index="{piste}" muted playsinline{style}></video>')


FONDU = 0.4
vids = []
for k, (x, f, depart, eff) in enumerate(P):
    t0 = 0.0 if k == 0 else T(x)
    t1 = T(P[k + 1][0]) if k + 1 < len(P) else FIN
    suivant_fondu = k + 1 < len(P) and P[k + 1][3] == "fondu"
    d = t1 - t0 + (FONDU if suivant_fondu else 0)  # chevauche le plan suivant pendant son fondu
    pid = f"p{k:03d}"
    if eff == "split":  # écran partagé en 3 : trois vrais sites qui glissent en alternance haut / bas
        panneaux = []
        for i in range(3):
            fs = prend(SITES, "s")
            dep = depart_auto(fs, d)
            panneaux.append(f'<div class="ed-tiers" style="left: {i * 640}px">' + video(f"{pid}-{i}", fs, t0, d, dep, 20 + i, cls="ed-tiers-v") + '</div>')
            j(f'tl.fromTo("#{pid}-{i}", {{ yPercent: {-110 if i % 2 == 0 else 110} }}, {{ yPercent: 0, duration: 0.12, ease: "power4.out", immediateRender: false }}, {r(t0 + i * 0.03)});')
        vids.append(f'<div id="{pid}" class="ed-split" style="opacity: 0">{"".join(panneaux)}</div>')
        j(f'tl.set("#{pid}", {{ opacity: 1 }}, {r(t0)});')
        j(f'tl.set("#{pid}", {{ opacity: 0 }}, {r(t1)});')
        son(t0, "glitch-court", 0.3, "écran partagé")
        continue
    if f.startswith("GEL:"):  # arrêt sur image : image fixe qui cogne, se dé-sature et zoome
        img = f[4:]
        vids.append(f'<img id="{pid}" class="clip ed-plan" src="assets/img/{img}.jpg" data-start="{r(t0)}" data-duration="{r(d)}" data-track-index="{1 + k % 2}" alt="" />')
        j(f'tl.fromTo("#{pid}", {{ scale: 1.3, filter: "saturate(0) contrast(1.6) brightness(1.4)" }}, {{ scale: 1.08, filter: "saturate(0.6) contrast(1.25) brightness(1)", duration: {r(min(0.3, d))}, ease: "power4.out", immediateRender: false }}, {r(t0)});')
        son(t0, "obturateur", 0.32, "arrêt sur image")
        continue
    if depart is None:
        depart = depart_auto(f, d)
    else:
        USAGES[f] = USAGES.get(f, 0) + 1
    if depart + d > duree(f) - 0.04:  # jamais au-delà de la fin du fichier
        depart = round(max(0.0, duree(f) - d - 0.05), 2)
    vids.append(video(pid, f, t0, d, depart, 1 + k % 2))
    sel = f"#{pid}"
    if eff == "fondu":
        j(f'tl.fromTo("{sel}", {{ opacity: 0, scale: 1.08 }}, {{ opacity: 1, scale: 1.0, duration: {FONDU}, ease: "sine.inOut", immediateRender: false }}, {r(t0)});')
        j(f'tl.to("{sel}", {{ scale: 1.16, duration: {r(max(0.1, d - FONDU))}, ease: "none" }}, {r(t0 + FONDU)});')
    elif eff == "pousse":
        j(f'tl.fromTo("{sel}", {{ scale: 1.0 }}, {{ scale: 1.2, duration: {r(d)}, ease: "none", immediateRender: false }}, {r(t0)});')
    elif eff == "coup":
        j(f'tl.fromTo("{sel}", {{ scale: 1.18 }}, {{ scale: 1.02, duration: {r(min(0.24, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "fouet":
        sens = 1 if k % 2 else -1
        j(f'tl.fromTo("{sel}", {{ x: {sens * 160}, scale: 1.12, filter: "blur(16px)" }}, {{ x: 0, scale: 1.04, filter: "blur(0px)", duration: {r(min(0.08, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "zoom":
        if k > 0 and not P[k - 1][1].startswith(("GEL:", "SPLIT")):
            j(f'tl.to("#p{k - 1:03d}", {{ scale: 2.4, filter: "blur(18px)", duration: 0.1, ease: "power3.in" }}, {r(t0 - 0.1)});')
        j(f'tl.fromTo("{sel}", {{ scale: 0.6, filter: "blur(14px)" }}, {{ scale: 1.04, filter: "blur(0px)", duration: {r(min(0.18, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "spin":
        sens = 1 if k % 2 else -1
        j(f'tl.fromTo("{sel}", {{ rotation: {sens * 18}, scale: 1.45, filter: "blur(14px)" }}, {{ rotation: 0, scale: 1.04, filter: "blur(0px)", duration: {r(min(0.2, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "tilt":  # bascule 3D en perspective
        sens = 1 if k % 2 else -1
        j(f'tl.fromTo("{sel}", {{ rotationY: {sens * 38}, transformPerspective: 1400, scale: 1.25, filter: "blur(8px)" }}, {{ rotationY: 0, scale: 1.04, filter: "blur(0px)", duration: {r(min(0.22, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "iris":  # ouverture en iris (cercle qui s'agrandit)
        j(f'tl.fromTo("{sel}", {{ clipPath: "circle(0% at 50% 50%)" }}, {{ clipPath: "circle(80% at 50% 50%)", duration: {r(min(0.22, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "miroir":  # effet miroir : la moitié gauche se reflète à droite
        vids.append(video(f"{pid}-m", f, t0, d, depart, 25, style=' style="transform: scaleX(-1); clip-path: inset(0 50% 0 0)"', cls="ed-plan ed-miroir"))
        j(f'tl.fromTo("{sel}", {{ scale: 1.14 }}, {{ scale: 1.0, duration: 0.2, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "echo":  # traînée de mouvement : deux copies décalées dans le temps, en mode écran
        for i, (dec, op) in enumerate(((0.1, 0.5), (0.2, 0.28))):
            vids.append(video(f"{pid}-e{i}", f, t0, d, round(max(0.0, depart - dec), 2), 26 + i, style=f' style="opacity: {op}"', cls="ed-plan ed-echo"))
        j(f'tl.fromTo("{sel}", {{ scale: 1.15 }}, {{ scale: 1.02, duration: 0.25, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "drop":  # impact + flou de zoom radial (3 copies agrandies qui s'effacent)
        j(f'tl.fromTo("{sel}", {{ scale: 1.7 }}, {{ scale: 1.05, duration: {r(min(0.3, d))}, ease: "power4.out", immediateRender: false }}, {r(t0)});')
        for i, (sc, op) in enumerate(((1.1, 0.4), (1.22, 0.26), (1.36, 0.16))):
            rid = f"{pid}-z{i}"
            vids.append(video(rid, f, t0, min(d, 0.5) - 0.02 * (i + 1), round(depart + 0.01 * (i + 1), 2), 28 + i, style=f' style="opacity: 0"', cls="ed-plan ed-echo"))
            j(f'tl.fromTo("#{rid}", {{ scale: {sc * 1.5}, opacity: {op} }}, {{ scale: {sc}, opacity: 0, duration: 0.45, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "stutter":
        j(f'tl.fromTo("{sel}", {{ scale: 1.25, x: {30 if k % 2 else -30} }}, {{ scale: 1.1, x: 0, duration: {r(min(0.06, d))}, ease: "none", immediateRender: false }}, {r(t0)});')
    elif eff == "rampe":
        j(f'tl.fromTo("{sel}", {{ scale: 1.35 }}, {{ scale: 1.02, duration: 0.35, ease: "power3.out", immediateRender: false }}, {r(t0)});')
        j(f'tl.to("{sel}", {{ scale: 1.12, duration: {r(max(0.05, d - 0.35))}, ease: "power1.in" }}, {r(t0 + 0.35)});')
    if k > 0 and (x * 4) == int(x * 4) and (x * 4) % 2 == 0 and eff != "fondu":
        son(t0, tour(WHOOSH), 0.15 if eff == "fouet" else 0.24, f"coupe {f}")
    if eff == "fondu":
        son(t0, "souffle-cine", 0.2, "fondu enchaîné")


# ================================================================ EFFETS GLOBAUX
def flash(t, coul="#ffffff", op=0.5, d=0.07):
    k = len(OVER)
    OVER.append(f'<div id="fl{k}" class="ed-flash" style="background: {coul}"></div>')
    j(f'tl.set("#fl{k}", {{ opacity: {op} }}, {r(t)});')
    j(f'tl.to("#fl{k}", {{ opacity: 0, duration: {d}, ease: "power2.out" }}, {r(t + 0.034)});')


def glitch(t):
    k = len(OVER)
    barres = "".join(f'<i style="top: {y}px; height: {h}px; background: {c}; left: {x}px; width: {w}px"></i>'
                     for y, h, c, x, w in ((120, 30, "#ff2a55", 0, 1920), (380, 14, "#00e5ff", 300, 1620), (590, 46, "#ffffff", 0, 1200),
                                           (800, 20, "#ff2a55", 600, 1320), (960, 12, "#00e5ff", 0, 1920)))
    OVER.append(f'<div id="gl{k}" class="ed-glitch">{barres}</div>')
    j(f'tl.set("#gl{k}", {{ opacity: 0.85, x: -50 }}, {r(t)});')
    j(f'tl.set("#gl{k}", {{ opacity: 0.6, x: 40 }}, {r(t + 0.034)});')
    j(f'tl.set("#gl{k}", {{ opacity: 0 }}, {r(t + 0.1)});')


def secousse(t, amp=18, n=4):
    kf = [f'{{ x: {r(amp * (1 - k / n) * (1 if k % 2 == 0 else -1))}, y: {r(amp * 0.6 * (1 - k / n) * (-1 if k % 2 == 0 else 1))}, '
          f'rotation: {r(amp * 0.05 * (1 - k / n) * (1 if k % 2 else -1))}, duration: 0.035 }}' for k in range(n)]
    kf.append('{ x: 0, y: 0, rotation: 0, duration: 0.04 }')
    j(f'tl.to("#cam", {{ keyframes: [{", ".join(kf)}] }}, {r(t)});')


def rgb(t, force=22, d=0.16):
    """Aberration chromatique : les canaux rouge et bleu s'écartent puis se recalent (filtre SVG #rgb)."""
    j(f'tl.set("#rgbw", {{ filter: "url(#rgb)" }}, {r(t)});')
    j(f'tl.fromTo("#rgb-r", {{ attr: {{ dx: {force} }} }}, {{ attr: {{ dx: 0 }}, duration: {d}, ease: "power2.out", immediateRender: false }}, {r(t)});')
    j(f'tl.fromTo("#rgb-b", {{ attr: {{ dx: {-force} }} }}, {{ attr: {{ dx: 0 }}, duration: {d}, ease: "power2.out", immediateRender: false }}, {r(t)});')
    j(f'tl.set("#rgbw", {{ filter: "none" }}, {r(t + d + 0.01)});')


def inverse(t, d=0.067):
    j(f'tl.set("#cam", {{ filter: "invert(1)" }}, {r(t)});')
    j(f'tl.set("#cam", {{ filter: "invert(0)" }}, {r(t + d)});')


def noir(t0, t1):
    k = len(OVER)
    OVER.append(f'<div id="nr{k}" class="ed-flash" style="background: #000"></div>')
    j(f'tl.set("#nr{k}", {{ opacity: 1 }}, {r(t0)});')
    j(f'tl.set("#nr{k}", {{ opacity: 0 }}, {r(t1)});')


FUITES = ["fuite-ambre", "fuite-rouge", "fuite-bleue", "fuite-violette", "fuite-spirale", "flare-soleil"]


def fuite(t, d=1.2, op=0.75, nom=None):
    """Vraie fuite de lumière (vidéo) posée en mode écran sur l'image."""
    nom = nom or tour(FUITES)
    k = len(OVER)
    OVER.append(f'<video id="lk{k}" class="clip ed-fuite" src="assets/fx/{nom}.mp4" data-start="{r(t)}" data-duration="{r(d)}" '
                f'data-media-start="0.3" data-track-index="{40 + k % 3}" muted playsinline></video>')
    j(f'tl.fromTo("#lk{k}", {{ opacity: 0 }}, {{ opacity: {op}, duration: {r(d * 0.3)}, ease: "sine.out", immediateRender: false }}, {r(t)});')
    j(f'tl.to("#lk{k}", {{ opacity: 0, duration: {r(d * 0.5)}, ease: "sine.in" }}, {r(t + d * 0.5)});')


def bandes(t, h, d=0.2, ease="power3.inOut"):
    """Bandes noires cinémascope : h = hauteur de chaque bande (138 px = format 2,39:1)."""
    j(f'tl.to(".ed-bande", {{ height: {h}, duration: {d}, ease: "{ease}" }}, {r(t)});')


def grade(t, d, filtre, ease="none"):
    j(f'tl.to("#grade", {{ filter: "{filtre}", duration: {d}, ease: "{ease}" }}, {r(t)});')


FROID = "saturate(0.35) contrast(1.2) brightness(0.7) sepia(0)"
TIEDE = "saturate(0.9) contrast(1.15) brightness(0.92) sepia(0)"
CHAUD = "saturate(1.3) contrast(1.12) brightness(1.02) sepia(0)"
FILM = "saturate(0.55) contrast(1.1) brightness(0.85) sepia(0.35)"
D0, FB = T(DROP), T(TEMPS["fin_basses"])

# ---- A. Intro sombre
j(f'tl.set("#grade", {{ filter: "{FROID}" }}, 0);')
j('tl.set(".ed-bande", { height: 150 }, 0);')
j('tl.set("#teinte", { opacity: 0.2 }, 0);')
fuite(0.0, 3.0, 0.5, "fuite-bleue")
fuite(T(6), 2.6, 0.45, "fuite-violette")
fuite(T(12), 2.4, 0.5, "fuite-ambre")
son(0.05, "intro-mystere", 0.32, "ouverture cinéma")
son(T(6), "battements", 0.26, "cœur qui bat")
for n in list(range(2, 8, 2)) + list(range(8, 15)):
    j(f'tl.fromTo("#cam", {{ scale: 1.03 }}, {{ scale: 1, duration: 0.45, ease: "sine.out", immediateRender: false }}, {T(n)});')
# ---- B. Les attaques
grade(T(15.5), r(T(28) - T(15.5)), TIEDE, "power1.in")
j(f'tl.to("#teinte", {{ opacity: 0.45, duration: {r(T(28) - T(15.5))}, ease: "none" }}, {T(15.5)});')
flash(T(15.5), "#ffffff", 0.6, 0.1)
rgb(T(15.5), 26, 0.2)
secousse(T(15.5), 20, 5)
son(T(15.5), "impact-basse", 0.42, "première attaque")
for n in range(16, 28):
    j(f'tl.fromTo("#cam", {{ scale: {round(1.03 + 0.04 * (n - 16) / 11, 3)} }}, {{ scale: 1, duration: 0.32, ease: "power3.out", immediateRender: false }}, {T(n)});')
    secousse(T(n) + 0.01, round(5 + 10 * (n - 16) / 11, 1), 3)
    if n % 2 == 0:
        flash(T(n), "#ffffff", round(0.1 + 0.18 * (n - 16) / 11, 2), 0.06)
        rgb(T(n), round(10 + 12 * (n - 16) / 11))
    if n % 4 == 0:
        fuite(T(n), 1.2, 0.55)
for x in (22.5, 24):
    flash(T(x), "#ffffff", 0.8, 0.08)
    rgb(T(x), 30, 0.22)
    secousse(T(x), 24, 5)
    son(T(x), "impact-tambour", 0.38, "arrêt sur image")
bandes(T(20), 120, 0.4)
# ---- C. La montée
bandes(T(28), 330, r(T(31.85) - T(28)), "power2.in")
grade(T(28), r(T(31.85) - T(28)), "saturate(0.7) contrast(1.35) brightness(0.85) sepia(0)", "power2.in")
j(f'tl.fromTo("#cam", {{ scale: 1 }}, {{ scale: 1.24, duration: {r(T(31.9) - T(28))}, ease: "power3.in", immediateRender: false }}, {T(28)});')
for x in (28, 28.5, 29, 29.5, 30, 30.25, 30.5, 30.75):
    flash(T(x), "#ffffff", 0.25, 0.05)
    rgb(T(x), 16)
    secousse(T(x), 12, 3)
for q in range(5):
    flash(T(31 + q / 6), "#ffffff" if q % 2 else "#000000", 0.4, 0.03)
son(D0, "riser-trailer", 0.38, "montée avant le drop", fin=D0 + 0.05)
son(D0, "riser-synth", 0.24, "montée avant le drop", fin=D0 + 0.05)
son(T(28), "roulement-suspense", 0.24, "roulement")
son(T(31.6), "aspiration", 0.28, "aspiration", fin=D0)
noir(T(31.85), D0)
# ---- D. DROP
j(f'tl.set("#cam", {{ scale: 1 }}, {D0});')
bandes(D0, 0, 0.12, "power4.out")
grade(D0, 0.1, CHAUD)
j(f'tl.set("#teinte", {{ opacity: 0.55 }}, {D0});')
flash(D0, "#ffffff", 1, 0.14)
inverse(D0 + 0.12, 0.1)
rgb(D0, 42, 0.32)
glitch(D0 + 0.22)
secousse(D0, 42, 8)
fuite(D0, 1.2, 0.6, "flare-soleil")
son(D0, "impact-basse", 0.6, "DROP")
son(D0, "impact-futur", 0.34, "DROP")
son(D0, "tonnerre-transition", 0.28, "DROP")
for x in (34.5, 34.75, 35):  # triple kick
    flash(T(x), "#ffffff", 0.7, 0.05)
    inverse(T(x) + 0.03, 0.04)
    rgb(T(x), 34, 0.16)
    secousse(T(x), 26, 4)
    son(T(x), "impact-tambour", 0.36, "triple kick")
COULS = ["#ff2a55", "#00e5ff", "#ffb347", "#ffffff"]
for n in range(DROP + 1, TEMPS["fin_basses"]):
    j(f'tl.fromTo("#cam", {{ scale: {1.09 if n % 2 == 0 else 1.05} }}, {{ scale: 1, duration: 0.28, ease: "power3.out", immediateRender: false }}, {T(n)});')
    secousse(T(n) + 0.01, 15 if n % 2 == 0 else 9, 3)
    if n % 2 == 0:
        flash(T(n), COULS[(n // 2) % 4], 0.24, 0.07)
        rgb(T(n), 14, 0.12)
    if n in (36, 40, 44):
        flash(T(n), "#ffffff", 0.75, 0.1)
        inverse(T(n) + 0.05, 0.04)
        rgb(T(n), 30, 0.22)
        glitch(T(n) + 0.06)
        fuite(T(n), 1.1, 0.5)
        son(T(n), "impact-basse", 0.4, "début de demi-phrase")
    if n in (39, 47):
        glitch(T(n))
        for q in (0.25, 0.5, 0.75):
            flash(T(n + q), "#ffffff", 0.35, 0.05)
for k in KICKS:  # petites secousses sur les kicks entre les temps
    if D0 < k < FB and min(abs(k - T(n)) for n in range(DROP, TEMPS["fin_basses"] + 1)) > 0.06:
        j(f'tl.to("#cam", {{ keyframes: [{{ y: 7, duration: 0.025 }}, {{ y: -4, duration: 0.025 }}, {{ y: 0, duration: 0.03 }}] }}, {r(k)});')
for a in TEMPS["attaques"]:  # micro-éclairs sur les caisses claires du drop
    if D0 + 0.1 < a < FB and min(abs(a - T(n / 2)) for n in range(2 * DROP, 2 * TEMPS["fin_basses"])) > 0.05:
        flash(a, "#ffffff", 0.14, 0.04)
# ---- E. Outro : arrêt sur image, ralentis cinéma, couleur pellicule, les bandes se referment, boucle
flash(FB, "#ffffff", 0.9, 0.12)
rgb(FB, 36, 0.3)
secousse(FB, 30, 6)
son(FB, "impact-basse", 0.5, "fin des basses")
son(FB + 0.05, "souffle-cine", 0.3, "retombée")
grade(FB, 1.2, FILM, "power2.out")
j(f'tl.to("#teinte", {{ opacity: 0.25, duration: 1.2, ease: "none" }}, {FB});')
bandes(FB + 0.3, 150, 1.4, "power2.inOut")
fuite(T(49), 2.8, 0.55, "fuite-ambre")
fuite(T(53), 2.8, 0.5, "fuite-spirale")
grade(T(56), r(FIN - T(56)), FROID, "power1.in")
son(FIN - 0.05, "rewind-glitch", 0.26, "la boucle repart")

# ================================================================ ÉCRITURE
sons_html, libre = [], []
for k, (t0, nom, v, note, d) in enumerate(sorted(SONS)):
    piste = next((i for i, f in enumerate(libre) if f <= t0), None)
    if piste is None:
        libre.append(0)
        piste = len(libre) - 1
    libre[piste] = t0 + d + 0.01
    sons_html.append(f'<audio id="sfx-{k + 1:03d}" src="assets/sfx/{nom}.mp3" data-start="{t0}" data-duration="{d}" data-volume="{v}" '
                     f'data-track-index="{50 + piste}"></audio><!-- {note} -->')

GRAIN = ("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
         "type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' "
         "height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")
NL = "\n"
page = f"""<!doctype html>
<html lang="fr" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      /* Edit pro (vidéo 19, v7) : aucun texte, tout est calé sur les temps de « AVANGARD » (tools/temps.json). */
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #000; }}
      #fond {{ position: absolute; inset: 0; background: #000; }}
      #rgbw, #grade {{ position: absolute; inset: 0; }}
      #cam {{ position: absolute; left: -70px; top: -70px; width: 2060px; height: 1220px; overflow: hidden; transform-origin: 50% 50%; }}
      .ed-plan {{ position: absolute; left: 70px; top: 70px; width: 1920px; height: 1080px; object-fit: cover; transform-origin: 50% 50%; }}
      .ed-split {{ position: absolute; left: 70px; top: 70px; width: 1920px; height: 1080px; background: #000; }}
      .ed-tiers {{ position: absolute; top: 0; width: 632px; height: 1080px; overflow: hidden; }}
      .ed-tiers-v {{ position: absolute; left: -330px; top: 0; width: 1292px; height: 1080px; object-fit: cover; }}
      #teinte {{ position: absolute; inset: 0; mix-blend-mode: soft-light;
        background: linear-gradient(180deg, rgba(0, 110, 130, 0.9) 0%, rgba(0, 60, 80, 0.6) 45%, rgba(255, 140, 50, 0.7) 100%); }}
      #vignette {{ position: absolute; inset: 0; background: radial-gradient(ellipse 72% 68% at 50% 50%, rgba(0, 0, 0, 0) 50%, rgba(0, 0, 0, 0.7) 100%); }}
      #grain {{ position: absolute; inset: -50%; width: 200%; height: 200%; opacity: 0.13; background: url("{GRAIN}");
        animation: ed-grain 0.4s steps(1) infinite; mix-blend-mode: overlay; }}
      @keyframes ed-grain {{ 0%, 100% {{ transform: translate(0, 0); }} 20% {{ transform: translate(-6%, 4%); }}
        40% {{ transform: translate(5%, -7%); }} 60% {{ transform: translate(-4%, 8%); }} 80% {{ transform: translate(7%, 3%); }} }}
      .ed-fuite {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; mix-blend-mode: screen; opacity: 0; }}
      .ed-flash {{ position: absolute; inset: 0; opacity: 0; }}
      .ed-glitch {{ position: absolute; inset: 0; opacity: 0; mix-blend-mode: screen; }}
      .ed-glitch i {{ position: absolute; }}
      .ed-bande {{ position: absolute; left: 0; width: 1920px; height: 0; background: #000; }}
      .ed-echo {{ mix-blend-mode: screen; }}
      #bande-h {{ top: 0; }}
      #bande-b {{ bottom: 0; }}
    </style>
  </head>
  <body>
    <svg width="0" height="0" style="position: absolute">
      <filter id="rgb" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
        <feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r" />
        <feOffset id="rgb-r" in="r" dx="0" dy="0" result="ro" />
        <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g" />
        <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b" />
        <feOffset id="rgb-b" in="b" dx="0" dy="0" result="bo" />
        <feBlend in="ro" in2="g" mode="screen" result="rg" />
        <feBlend in="rg" in2="bo" mode="screen" />
      </filter>
    </svg>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="1920" data-height="1080">
      <div id="fond" class="clip" data-start="0" data-duration="{FIN}" data-track-index="0"></div>
      <div id="rgbw">
        <div id="grade">
          <div id="cam">
{NL.join("            " + v for v in vids)}
          </div>
          <div id="teinte"></div>
        </div>
{NL.join("        " + h for h in OVER)}
      </div>
      <div id="vignette"></div>
      <div style="position: absolute; inset: 0; overflow: hidden"><div id="grain"></div></div>
      <div id="bande-h" class="ed-bande"></div>
      <div id="bande-b" class="ed-bande"></div>
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
plans = [z for z in P if z[1] != "SPLIT"]
uniques = {f for _, f, _, _ in plans} | {f for f in USAGES}
sites = {f for f in uniques if f in SITES}
print(f"edit v7 écrit : {len(P)} plans (+{sum(1 for z in P if z[1] == 'SPLIT')} écrans partagés), {len(uniques)} vidéos différentes "
      f"dont {len(sites)} sites, {len(SONS)} bruitages, fin à {FIN} s")
