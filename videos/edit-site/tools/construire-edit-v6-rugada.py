#!/usr/bin/env python3
"""Écrit index.html de « edit-site » (vidéo 18, v6) : edit PRO cinématique sur « Montagem Rugada » (cape).

Demande : « prends le 5 et ses meilleurs moments, surtout le hook de la montée en tension constante, pas de vidéo cuisine,
on rentre dans la cinématique, beaucoup plus de vidéos et de sites, très bien rythmé, calé sur chaque image, et des effets
visuels dignes d'un montage Premiere Pro ».

Son (tools/temps.json) : 64 temps à ≈130 BPM. Intro sans basses (0–7), montée avec basses légères (8–21), silence (22–23),
3 coups secs (23,5 / 24,25 / 25), tension sans basses qui monte (25,5–31), DROP au temps 32 (14,91 s), 32 temps à fond.

Effets (tous calés sur les temps, déterministes, compatibles avec le rendu image par image) :
  étalonnage cinéma (froid et désaturé pendant la montée → bleu-orange chaud), bandes noires cinémascope qui se resserrent
  jusqu'à une fente avant le drop puis s'ouvrent d'un coup, grain de film, vignette, vraies fuites de lumière (vidéos en
  mode « écran »), aberration chromatique RGB (filtre SVG) sur les impacts, zoom traversant, transition en rotation,
  filé latéral avec flou de mouvement, stutter (même image répétée au quart de temps), écran partagé en 3, vrais ralentis
  avec accélération (rampe-*.mp4, préparés avec ffmpeg), flashs, inversion, glitch, stroboscope, secousses sur les kicks.
Relancer ce script ÉCRASE index.html.
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


TENSION = garde(["eclair-nuages", "boxeur-sombre", "fumee-mouvement", "hacker-nuit", "voiture-spot", "eclairs-nuit", "danseur-dos",
                 "trafic-pluie", "boxe-sac-silhouette", "flammes-noir", "hacker-masque-ecrans", "voiture-rouge-gros-plan",
                 "silhouettes-fumee", "coureur-depart", "ville-nuit-drone", "tunnel-trafic", "encre-liquide", "moto-accelere",
                 "drapeau-course", "coureur-sol", "avenues-nuit", "lave-particules", "voiture-compteur", "tunnel-neon-rouge",
                 "hacker-glitch", "danseur-masque-neon", "tokyo-train-nuit", "flammes-miroir", "eclair-frappe", "fumee-tourbillon",
                 "serveurs-lumieres", "ecrans-matrix", "fibre-optique", "code-chiffres"])
MOUVEMENT = garde(["rally-terre", "danse-techno-neon", "moto-wheelie", "boxe-coups", "foule-saute", "voitures-vitesse", "breakdance",
                   "lasers-cyberpunk", "festival-saute", "danse-rue-choregraphie", "motos-route", "boxe-direct", "skate-rampe",
                   "karting", "foule-pogo", "filles-barres-lumiere", "robot-danse", "course-neige", "mma-combat", "danse-basket-nuit",
                   "moto-tunnel-2", "voiture-blanche-coucher", "boxe-match", "danse-objectif", "foule-bras", "snowboard",
                   "danse-lumieres", "rally-foret", "moto-wheelie-2", "dj-scene", "skate-pirouette", "boule-feu", "conduite-nuit",
                   "motos-terre", "feux-artifice", "voiture-rouge-route", "basket-tir", "coureur-ville", "danseur-couleurs",
                   "foot-but", "lumieres-scene", "skate-bowl-2", "breakdance-2", "autoroute-nuit", "danse-rue-cinq",
                   "danse-fumee-violette", "explosion-feu", "boxe-ko", "danse-silhouette-energie", "moto-tunnel", "etincelles-feu",
                   "boxe-sac-bas", "danse-silhouette-rouge", "vr-combinaison", "gamer-rgb", "danse-fumee-2"])
SITES = garde(["site-lamborghini", "spline-ai", "site-apple", "site-playstation", "framer-ai", "site-nvidia", "site-stripe",
               "site-mclaren", "site-visionpro", "site-figma", "site-xbox", "site-webflow", "site-netflix", "site-spline-site",
               "site-ubisoft", "site-vercel", "site-riot", "site-dji", "site-raycast", "site-iphone", "site-bolt", "site-discord",
               "site-gopro", "site-v0", "site-cursor", "site-twitch", "site-locomotive", "site-cuberto", "site-midjourney",
               "site-dribbble", "site-shopify", "site-notion", "site-duolingo", "site-wix", "site-squarespace", "site-bruno-simon",
               "spline", "volt-visite"])
FX = garde(["etincelles", "rayons-lumiere", "paysage-neon", "neon-3d-route", "immeubles-futur", "retro-soleil", "explosion-particules",
            "main-hologramme", "lignes-3d", "trou-de-ver", "tunnel-cubes", "neon-etincelles", "tunnel-rouge"])
RAMPES = garde([f"rampe-{n}" for n in ("moto-wheelie-2", "breakdance", "boxe-ko", "skate-rampe", "foule-pogo",
                                         "voitures-vitesse", "karting", "danse-rue-choregraphie", "boxe-direct", "skate-pirouette",
                                         "motos-route", "rally-terre")])
CURSEUR = {}


def prend(reserve, cle):
    k = CURSEUR.get(cle, 0)
    CURSEUR[cle] = k + 1
    return reserve[k % len(reserve)]


# ================================================================ LE MONTAGE (temps musical, vidéo, départ ou None, effet)
# effets : pousse (zoom lent), coup (coup de zoom), fouet (filé latéral), zoom (zoom traversant), spin (rotation),
#          drop (impact), stutter (même image, coups de zoom secs), rampe (ralenti avec accélération), split (écran en 3)
P = []
# Intro cinématique sans basses (temps 0–7) : un plan tous les 2 temps, bandes noires, image froide
P += [(0, "voiture-spot", 0.4, "pousse"), (2, "boxeur-sombre", 0.3, "pousse"), (4, "eclair-nuages", 0.3, "pousse"),
      (6, "danseur-dos", 0.2, "pousse"), (7.5, "hacker-nuit", 0.5, "coup")]
# Montée avec basses légères (temps 8–21) : un plan par temps, transitions variées
for n in range(8, 22):
    eff = ["coup", "fouet", "zoom", "coup", "spin", "fouet", "coup"][n % 7]
    P.append((n, prend(TENSION, "t"), None, eff))
    if n >= 16 and n % 2 == 1:
        P.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
# Deux kicks (21,5 / 22) : stutter
st = prend(TENSION, "t")
P += [(21.5, st, 0.8, "stutter"), (21.75, st, 0.8, "stutter")]
# Silence (22 → 23,5) : un seul plan qui pousse, image qui retient son souffle
P.append((22, "silhouettes-fumee", 0.6, "pousse"))
# Trois coups secs (23,5 / 24,25 / 25) : trois plans coupés net
P += [(23.5, "boule-feu", 0.3, "drop"), (24.25, prend(SITES, "s"), None, "coup"), (25, "boxe-direct", 0.4, "drop")]
# Tension sans basses qui monte (25,5 → 32) : de plus en plus vite jusqu'à la fente noire
P += [(26, prend(TENSION, "t"), None, "zoom"), (27, prend(SITES, "s"), None, "fouet"), (28, prend(TENSION, "t"), None, "spin"),
      (28.5, prend(SITES, "s"), None, "fouet"), (29, prend(TENSION, "t"), None, "zoom"), (29.5, prend(SITES, "s"), None, "fouet")]
for q in range(12):  # temps 30 à 32 : un plan par sixième de temps (stroboscope d'images)
    x = 30 + q / 6
    P.append((round(x, 4), prend(SITES, "s") if q % 2 else prend(TENSION, "t"), None, "fouet"))
# DROP (temps 32) et les 4 phrases de 8 temps
for ph in range(4):
    p = DROP + 8 * ph
    P.append((p, "explosion-feu" if ph == 0 else prend(RAMPES, "r"), 0.3 if ph == 0 else 0.0, "drop" if ph == 0 else "rampe"))
    if ph == 0:
        for x in (32.25, 32.5, 32.75):
            P.append((x, prend(SITES, "s"), None, "fouet"))
        P.append((33, prend(RAMPES, "r"), 0.0, "rampe"))
    for n in range(p + 2, p + 7):
        P.append((n, prend(MOUVEMENT, "m"), None, ["coup", "zoom", "spin", "coup", "fouet"][n % 5]))
        P.append((n + 0.5, prend(SITES, "s"), None, "fouet"))
        if n == p + 4:  # le double kick syncopé (x,75) : stutter
            m = prend(MOUVEMENT, "m")
            P[-1] = (n + 0.5, P[-1][1], None, "fouet")
            P.append((n + 0.75, m, 0.5, "stutter"))
    if ph < 3:
        P.append((p + 7, "SPLIT", None, "split"))
        P.append((p + 7.5, prend(FX, "x"), None, "fouet"))
        P.append((p + 7.75, prend(SITES, "s"), None, "fouet"))
    else:
        P.append((p + 7, "voiture-spot", 0.4, "pousse"))  # fin : retour au plan du début (boucle)
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
    return (f'<video id="{vid}" class="clip {cls}" src="assets/video/{f}.mp4" data-start="{t0}" data-duration="{r(d)}" '
            f'data-media-start="{depart}" data-track-index="{piste}" muted playsinline{style}></video>')


vids = []
for k, (x, f, depart, eff) in enumerate(P):
    t0 = 0.0 if k == 0 else T(x)
    t1 = T(P[k + 1][0]) if k + 1 < len(P) else FIN
    d = t1 - t0
    pid = f"p{k:03d}"
    if eff == "split":  # écran partagé en 3 : trois vrais sites qui glissent en alternance haut / bas
        panneaux = []
        for i in range(3):
            fs = prend(SITES, "s")
            dep = depart_auto(fs, d)
            panneaux.append(f'<div class="ed-tiers" style="left: {i * 640}px">' +
                            video(f"{pid}-{i}", fs, t0, d, dep, 20 + i, cls="ed-tiers-v") + '</div>')
            j(f'tl.fromTo("#{pid}-{i}", {{ yPercent: {-110 if i % 2 == 0 else 110} }}, {{ yPercent: 0, duration: 0.12, ease: "power4.out", immediateRender: false }}, {r(t0 + i * 0.03)});')
        vids.append(f'<div id="{pid}" class="ed-split" style="opacity: 0">{"".join(panneaux)}</div>')
        j(f'tl.set("#{pid}", {{ opacity: 1 }}, {t0});')
        j(f'tl.set("#{pid}", {{ opacity: 0 }}, {t1});')
        son(t0, "glitch-court", 0.3, "écran partagé")
        continue
    if depart is None:
        depart = depart_auto(f, d)
    else:
        USAGES[f] = USAGES.get(f, 0) + 1
    if depart + d > duree(f) - 0.04:  # jamais au-delà de la fin du fichier (sinon image noire)
        depart = round(max(0.0, duree(f) - d - 0.05), 2)
    vids.append(video(pid, f, t0, d, depart, 1 + k % 2))
    sel = f"#{pid}"
    if eff == "pousse":
        j(f'tl.fromTo("{sel}", {{ scale: 1.0 }}, {{ scale: 1.22, duration: {r(d)}, ease: "none", immediateRender: false }}, {t0});')
    elif eff == "coup":
        j(f'tl.fromTo("{sel}", {{ scale: 1.18 }}, {{ scale: 1.02, duration: {r(min(0.24, d))}, ease: "power3.out", immediateRender: false }}, {t0});')
    elif eff == "fouet":
        sens = 1 if k % 2 else -1
        j(f'tl.fromTo("{sel}", {{ x: {sens * 160}, scale: 1.12, filter: "blur(16px)" }}, {{ x: 0, scale: 1.04, filter: "blur(0px)", duration: {r(min(0.08, d))}, ease: "power3.out", immediateRender: false }}, {t0});')
    elif eff == "zoom":  # zoom traversant : le plan précédent fonce vers la caméra, le nouveau arrive de loin
        if k > 0:
            j(f'tl.to("#p{k - 1:03d}", {{ scale: 2.4, filter: "blur(18px)", duration: 0.1, ease: "power3.in" }}, {r(t0 - 0.1)});')
        j(f'tl.fromTo("{sel}", {{ scale: 0.6, filter: "blur(14px)" }}, {{ scale: 1.04, filter: "blur(0px)", duration: {r(min(0.18, d))}, ease: "power3.out", immediateRender: false }}, {t0});')
    elif eff == "spin":
        sens = 1 if k % 2 else -1
        j(f'tl.fromTo("{sel}", {{ rotation: {sens * 18}, scale: 1.45, filter: "blur(14px)" }}, {{ rotation: 0, scale: 1.04, filter: "blur(0px)", duration: {r(min(0.2, d))}, ease: "power3.out", immediateRender: false }}, {t0});')
    elif eff == "drop":
        j(f'tl.fromTo("{sel}", {{ scale: 1.7 }}, {{ scale: 1.05, duration: {r(min(0.3, d))}, ease: "power4.out", immediateRender: false }}, {t0});')
    elif eff == "stutter":
        j(f'tl.fromTo("{sel}", {{ scale: 1.25, x: {30 if k % 2 else -30} }}, {{ scale: 1.1, x: 0, duration: {r(min(0.06, d))}, ease: "none", immediateRender: false }}, {t0});')
    elif eff == "rampe":
        j(f'tl.fromTo("{sel}", {{ scale: 1.35 }}, {{ scale: 1.02, duration: 0.35, ease: "power3.out", immediateRender: false }}, {t0});')
        j(f'tl.to("{sel}", {{ scale: 1.12, duration: {r(max(0.05, d - 0.35))}, ease: "power1.in" }}, {r(t0 + 0.35)});')
    if k > 0 and (x * 4) == int(x * 4) and (x * 4) % 2 == 0:
        son(t0, tour(WHOOSH), 0.15 if eff == "fouet" else 0.24, f"coupe {f}")


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


FROID = "saturate(0.35) contrast(1.18) brightness(0.72) hue-rotate(0deg)"
CHAUD = "saturate(1.3) contrast(1.12) brightness(1.02) hue-rotate(0deg)"

# ---- Intro + montée : image froide qui se réchauffe, bandes cinémascope, fuites de lumière
j(f'tl.set("#grade", {{ filter: "{FROID}" }}, 0);')
j('tl.set(".ed-bande", { height: 150 }, 0);')
j('tl.set("#teinte", { opacity: 0.15 }, 0);')
grade(T(8), r(T(22) - T(8)), "saturate(0.95) contrast(1.15) brightness(0.92) hue-rotate(0deg)", "power1.in")
j(f'tl.to("#teinte", {{ opacity: 0.45, duration: {r(T(22) - T(8))}, ease: "none" }}, {T(8)});')
fuite(T(0), 2.6, 0.55, "fuite-bleue")
fuite(T(4), 2.4, 0.5, "fuite-ambre")
son(T(0.2), "intro-mystere", 0.3, "ouverture cinéma")
for x in (7.5,):
    flash(T(x), "#ffffff", 0.35, 0.08)
    rgb(T(x), 18)
    secousse(T(x), 14, 4)
    son(T(x), "impact-basse", 0.4, "premier kick")
for n in range(8, 22):
    j(f'tl.fromTo("#cam", {{ scale: {round(1.03 + 0.04 * (n - 8) / 13, 3)} }}, {{ scale: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {T(n)});')
    secousse(T(n) + 0.01, round(4 + 10 * (n - 8) / 13, 1), 3)
    if n % 2 == 0:
        flash(T(n), "#ffffff", round(0.08 + 0.2 * (n - 8) / 13, 2), 0.06)
        rgb(T(n), round(8 + 14 * (n - 8) / 13))
    if n % 4 == 0:
        fuite(T(n), 1.2, 0.6)
son(T(8), "battements", 0.3, "cœur qui bat")
bandes(T(16), 120, 0.4)
# ---- Stutter (21,5) et SILENCE (22 → 23,5)
for x in (21.5, 21.75):
    flash(T(x), "#ffffff", 0.4, 0.04)
    secousse(T(x), 16, 3)
bandes(T(22), 260, 0.35, "power3.out")
grade(T(22), 0.3, "saturate(0.2) contrast(1.3) brightness(0.6) hue-rotate(0deg)", "power2.out")
son(T(22), "aspiration", 0.3, "le son se retient")
son(T(22.1), "battement-mystere", 0.32, "silence tendu")
# ---- Trois coups secs
for x, nom in ((23.5, "impact-basse"), (24.25, "impact-tambour"), (25, "impact-futur")):
    flash(T(x), "#ffffff", 0.9, 0.08)
    inverse(T(x) + 0.04, 0.05)
    rgb(T(x), 30, 0.2)
    secousse(T(x), 28, 5)
    son(T(x), nom, 0.45, "coup sec")
grade(T(23.5), 0.15, "saturate(1.05) contrast(1.2) brightness(0.95) hue-rotate(0deg)")
bandes(T(23.5), 170, 0.12, "power4.out")
# ---- Tension sans basses (25,5 → 32) : la fente se resserre, la caméra avance, stroboscope
bandes(T(26), 320, r(T(31.85) - T(26)), "power2.in")
j(f'tl.fromTo("#cam", {{ scale: 1 }}, {{ scale: 1.22, duration: {r(T(31.9) - T(26))}, ease: "power3.in", immediateRender: false }}, {T(26)});')
for x in (26, 27, 28, 28.5, 29, 29.5):
    flash(T(x), "#ffffff", 0.25, 0.05)
    rgb(T(x), 16)
    secousse(T(x), 12, 3)
for q in range(12):
    x = 30 + q / 6
    flash(T(x), "#ffffff" if q % 2 else "#000000", 0.35, 0.03)
son(T(DROP), "riser-trailer", 0.38, "montée avant le drop", fin=T(DROP) + 0.05)
son(T(DROP), "riser-synth", 0.24, "montée avant le drop", fin=T(DROP) + 0.05)
son(T(26), "roulement-suspense", 0.24, "roulement")
noir(T(31.9), T(DROP))
# ---- DROP : les bandes s'ouvrent d'un coup, couleurs bleu-orange chaudes
j(f'tl.set("#cam", {{ scale: 1 }}, {T(DROP)});')
bandes(T(DROP), 0, 0.12, "power4.out")
grade(T(DROP), 0.1, CHAUD)
j(f'tl.set("#teinte", {{ opacity: 0.5 }}, {T(DROP)});')
flash(T(DROP), "#ffffff", 1, 0.14)
inverse(T(DROP) + 0.12, 0.1)
rgb(T(DROP), 40, 0.3)
glitch(T(DROP) + 0.22)
secousse(T(DROP), 40, 8)
fuite(T(DROP), 1.2, 0.6, "flare-soleil")
son(T(DROP), "impact-basse", 0.6, "DROP")
son(T(DROP), "impact-futur", 0.34, "DROP")
son(T(DROP), "tonnerre-transition", 0.28, "DROP")
# ---- Pendant le drop : un coup de zoom par temps, couleurs, RGB, fuites de lumière par phrase
COULS = ["#ff2a55", "#00e5ff", "#ffb347", "#ffffff"]
for n in range(DROP + 1, NB):
    j(f'tl.fromTo("#cam", {{ scale: {1.09 if n % 2 == 0 else 1.05} }}, {{ scale: 1, duration: 0.26, ease: "power3.out", immediateRender: false }}, {T(n)});')
    secousse(T(n) + 0.01, 15 if n % 2 == 0 else 9, 3)
    if n % 2 == 0:
        flash(T(n), COULS[(n // 2) % 4], 0.24, 0.07)
        rgb(T(n), 14, 0.12)
    if (n - DROP) % 8 == 0:
        flash(T(n), "#ffffff", 0.8, 0.1)
        inverse(T(n) + 0.05, 0.04)
        rgb(T(n), 32, 0.22)
        glitch(T(n) + 0.06)
        fuite(T(n), 1.2, 0.55)
        son(T(n), "impact-basse", 0.42, "début de phrase")
    if (n - DROP) % 8 == 7 and n < NB - 1:
        glitch(T(n))
        for q in (0.5, 0.75):
            flash(T(n + q), "#ffffff", 0.35, 0.05)
    if (n - DROP) % 8 == 4:
        flash(T(n + 0.75), "#ffffff", 0.5, 0.05)
        rgb(T(n + 0.75), 26, 0.14)
        son(T(n + 0.75), "impact-tambour", 0.3, "double kick")
# Petites secousses sur les kicks entre les temps
for k in KICKS:
    if T(DROP) < k < FIN - 0.1 and min(abs(k - T(n)) for n in range(DROP, NB + 1)) > 0.06:
        j(f'tl.to("#cam", {{ keyframes: [{{ y: 7, duration: 0.025 }}, {{ y: -4, duration: 0.025 }}, {{ y: 0, duration: 0.03 }}] }}, {r(k)});')
# Fin : les bandes et le froid reviennent pour boucler sur l'intro
bandes(T(NB - 1), 150, r(FIN - T(NB - 1)), "power2.in")
grade(T(NB - 1), r(FIN - T(NB - 1)), FROID, "power2.in")
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
      /* Edit pro (vidéo 18, v6) : aucun texte, tout est calé sur les temps de « Montagem Rugada » (tools/temps.json). */
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
print(f"edit v6 écrit : {len(P)} plans (+{sum(1 for z in P if z[1] == 'SPLIT')} écrans partagés), {len(uniques)} vidéos différentes "
      f"dont {len(sites)} sites, {len(SONS)} bruitages, fin à {FIN} s")
