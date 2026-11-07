#!/usr/bin/env python3
"""Écrit index.html de « edit-site » : un edit rythmé SANS voix off, calé image par image sur la musique.

Musique : « Phonk Remix » de HoliznaCC0 (CC0), extrait 5,270 → 20,876 s du morceau = 24 temps à 92,3 BPM.
  temps 0 à 7  : intro (mélodie seule) → rafale de vraies vidéos, un mot qui claque par temps, accélération ;
  temps 8      : DROP (les basses arrivent) → flash, impact, le navigateur s'écrase ;
  temps 9 à 18 : le site VOLT s'assemble bloc par bloc, un bloc par temps, la caméra suit chaque bloc ;
  temps 19 à 23: d'autres sites (café, chaîne), « FAIT PAR L'IA. », « EN 1 PROMPT. », « COMMENTE SITE » ;
  fin (temps 24) = retour sur la 1ʳᵉ image : la vidéo boucle.
Les temps viennent de librosa (tools/temps.json) ; les kicks servent aux petites secousses.

Relancer ce script ÉCRASE index.html.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI.parent.parent / "hyperframes-style" / "outils"))
from projecteur import perso, PIVOTS  # noqa: E402

TEMPS = json.loads((ICI / "tools/temps.json").read_text())
BEATS, KICKS = TEMPS["beats"], TEMPS["kicks"]
FIN = TEMPS["fin"]


def T(x):
    """Temps (s) du temps musical x (fractionnaire possible)."""
    n = int(math.floor(x))
    if n >= len(BEATS) - 1:
        return round(BEATS[-1] + (x - (len(BEATS) - 1)) * (BEATS[-1] - BEATS[-2]), 3)
    return round(BEATS[n] + (x - n) * (BEATS[n + 1] - BEATS[n]), 3)


HTML, JS, CSS = [], [], []


def j(ligne):
    JS.append("      " + ligne)


def r(x):
    return round(x, 3)


# ================================================================ SON
SFX = ICI / "assets/sfx"
PICS = json.loads((SFX / "pics.json").read_text())
SONS = []


def son(t, nom, v=0.4, note="", sur_pic=True, d=None, fin=None):
    p = PICS[nom]
    debut = t - (p["pic"] if sur_pic else 0)
    if debut < 0:
        debut = 0.0
    duree = min(p["duree"], d or 99, FIN - debut, (fin - debut) if fin else 99)
    if duree > 0.05:
        SONS.append((r(debut), nom, round(v, 3), note, r(duree)))


TOURS = {}


def tour(liste):
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


WHOOSH = ["souffle-rapide", "swoosh-court", "fouet", "swoosh-vol", "balaie-rapide", "swoosh-accent", "souffle-cine", "balaie-court"]
GLITCH = ["glitch-mini", "declencheur", "glitch-court", "obturateur-num"]
POPS = ["pop-click", "pop-sec", "pop-bulle", "pop-cartoon"]
IMPACTS = ["impact-tambour", "impact-cartoon", "impact-futur"]

# ================================================================ CAMÉRA
# #cam : coups de zoom et secousses sur le rythme (tout bouge) ; #scene : recadrages qui suivent les blocs.


def punch(t, f=1.07, d=0.32):
    j(f'tl.fromTo("#cam", {{ scale: {f} }}, {{ scale: 1, duration: {d}, ease: "power3.out", immediateRender: false }}, {r(t)});')


def secousse(t, amp=18, n=4):
    kf = []
    for k in range(n):
        a = amp * (1 - k / n)
        kf.append(f'{{ x: {r(a * (1 if k % 2 == 0 else -1))}, y: {r(a * 0.6 * (-1 if k % 2 == 0 else 1))}, rotation: {r(a * 0.04 * (1 if k % 2 else -1))}, duration: 0.035 }}')
    kf.append('{ x: 0, y: 0, rotation: 0, duration: 0.04 }')
    j(f'tl.to("#cam", {{ keyframes: [{", ".join(kf)}] }}, {r(t)});')


def recadre(t, px, py, sc, d=0.22, ease="power3.inOut"):
    x, y = round(-(px - 960) * sc), round(-(py - 540) * sc)
    j(f'tl.to("#scene", {{ x: {x}, y: {y}, scale: {sc}, duration: {d}, ease: "{ease}" }}, {r(t)});')
    j(f'tl.to("#scene", {{ keyframes: [{{ filter: "blur(8px)", duration: {r(d / 2)} }}, {{ filter: "blur(0px)", duration: {r(d / 2)} }}] }}, {r(t)});')
    son(t + d / 2, tour(["zoom-air", "zoom-swipe", "zoom-futur", "zoom-vide", "zoom-scifi"]), 0.3, "la caméra suit")


def eclair(t, coul="#ffffff", d=0.07, op=0.9):
    k = len(HTML)
    HTML.append(f'<div id="eclair-{k}" class="ed-eclair" style="background: {coul}"></div>')
    j(f'tl.set("#eclair-{k}", {{ opacity: {op} }}, {r(t)});')
    j(f'tl.to("#eclair-{k}", {{ opacity: 0, duration: {d}, ease: "power2.out" }}, {r(t + 0.034)});')


def barres_glitch(t):
    k = len(HTML)
    barres = "".join(
        f'<i style="top: {y}px; height: {h}px; background: {c}; left: {x}px; width: {w}px"></i>'
        for y, h, c, x, w in ((140, 26, "#ff2a55", 0, 1920), (402, 12, "#00e5ff", 260, 1660), (611, 40, "#ffffff", 0, 1300),
                             (820, 18, "#ff2a55", 500, 1420), (955, 10, "#00e5ff", 0, 1920)))
    HTML.append(f'<div id="glitch-{k}" class="ed-glitch">{barres}</div>')
    j(f'tl.set("#glitch-{k}", {{ opacity: 0.85, x: -40 }}, {r(t)});')
    j(f'tl.set("#glitch-{k}", {{ opacity: 0.6, x: 30 }}, {r(t + 0.034)});')
    j(f'tl.set("#glitch-{k}", {{ opacity: 0 }}, {r(t + 0.1)});')


# ================================================================ FOND : vraies vidéos qui changent sur le rythme
FOND = []  # (début, fin, fichier)


def fond(t0, t1, f):
    FOND.append((r(t0), r(t1), f))


# ================================================================ TEXTES QUI CLAQUENT
def mot(mid, texte, t0, t1, taille=210, coul="#FFFFFF", y=540, entree=True, zoom_fin=None):
    HTML.append(f'<div id="{mid}" class="ed-mot" style="top: {y}px; font-size: {taille}px; color: {coul}; opacity: 0">{texte}</div>')
    if entree:
        j(f'tl.fromTo("#{mid}", {{ opacity: 0, scale: 1.45 }}, {{ opacity: 1, scale: 1, duration: 0.1, ease: "power4.out", immediateRender: false }}, {r(t0)});')
    else:
        j(f'tl.set("#{mid}", {{ opacity: 1 }}, {r(t0)});')
    if zoom_fin:
        j(f'tl.to("#{mid}", {{ scale: {zoom_fin}, duration: {r(t1 - t0 - 0.12)}, ease: "power2.in" }}, {r(t0 + 0.12)});')
    j(f'tl.set("#{mid}", {{ opacity: 0 }}, {r(t1)});')


# ================================================================ PERSONNAGE (pictogramme articulé de projecteur.py)
class _S:
    debut = 0

    @staticmethod
    def L(g):
        return r(max(0.0, g))

    @staticmethod
    def j(ligne):
        j(ligne.strip())


S = _S()


def pose(pid, g, d=0.14, ease="power2.out", **angles):
    for k, v in angles.items():
        j(f'tl.to("#{pid}-{k}", {{ rotation: {v}, svgOrigin: "{PIVOTS[k]}", duration: {d}, ease: "{ease}" }}, {r(g)});')


def hoche(pid, g):
    j(f'tl.to("#{pid}-tete", {{ svgOrigin: "{PIVOTS["tete"]}", keyframes: [{{ rotation: 12, y: 5, duration: 0.09 }}, {{ rotation: 0, y: 0, duration: 0.16 }}] }}, {r(g)});')
    j(f'tl.to("#{pid}-corps", {{ keyframes: [{{ y: 8, duration: 0.09 }}, {{ y: 0, duration: 0.16 }}] }}, {r(g)});')


def saut(pid, g, h=40):
    j(f'tl.to("#{pid}-corps", {{ keyframes: [{{ y: -{h}, duration: 0.13, ease: "power2.out" }}, {{ y: 0, duration: 0.15, ease: "power2.in" }}] }}, {r(g)});')


# ================================================================ NAVIGATEUR ET SITE VOLT (assemblé bloc par bloc)
NX, NY, NW = 300, 66, 1320  # fenêtre du navigateur dans le film
K = NW / 1280  # échelle page (1280 px CSS) → film
BARRE = 46
PAGE_Y = NY + BARRE


def film_xy(x, y, defile=0):
    """Point de la page VOLT (px CSS) → point du film."""
    return NX + x * K, PAGE_Y + (y - defile) * K


BOITES = {"menu": [0, 0, 1280, 81], "titre": [51, 241, 583, 170], "texte": [51, 431, 460, 42], "bouton": [51, 505, 236, 49],
          "photo": [674, 120, 555, 555], "titre-produits": [51, 825, 1178, 46], "p0": [51, 899, 279, 412], "p1": [351, 899, 279, 412],
          "p2": [650, 899, 279, 412], "p3": [949, 899, 279, 412]}
DEFILE = 780  # défilement vers les produits


def bloc(nom):
    x, y, w, h = BOITES[nom]
    return f'<img id="b-{nom}" class="ed-bloc" src="assets/img/volt-{nom}.png" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0" alt="" />'


# ================================================================ LE MONTAGE, TEMPS PAR TEMPS
# ---- INTRO (temps 0 à 7) : une vraie vidéo par temps, puis par demi-temps, puis par quart de temps
intro = [(0, "hacker-glitch"), (1, "code-chiffres"), (2, "hacker-nuit"), (3, "serveurs-attaque"), (4, "neon-japon"),
         (5, "doigts-tapent"), (6, "hacker-masque-ecrans"), (6.5, "robot-yeux"), (7, "tunnel-rouge"), (7.25, "gamer-rgb"),
         (7.5, "ecrans-code"), (7.75, "fibre-optique")]
for k, (x, f) in enumerate(intro):
    t1 = T(intro[k + 1][0]) if k + 1 < len(intro) else T(7.9)
    fond(T(x), t1, f)
    if x > 0:
        son(T(x), tour(WHOOSH) if x < 7 else tour(GLITCH), 0.42 if x < 7 else 0.36, f"coupe {f}")
        if x == int(x) and x < 7:
            punch(T(x), 1.05, 0.3)
        else:
            punch(T(x), 1.03, 0.14)
HTML.append('<div id="noir-avant-drop" class="ed-noir" style="opacity: 0"></div>')
j(f'tl.set("#noir-avant-drop", {{ opacity: 1 }}, {T(7.9)});')
j(f'tl.set("#noir-avant-drop", {{ opacity: 0 }}, {T(8)});')

# SANS TEXTE (demande de l'utilisateur) : la montée se fait à l'image, la caméra fonce vers le drop
j(f'tl.fromTo("#fonds-intro", {{ scale: 1 }}, {{ scale: 1.5, duration: {r(T(7.9) - T(7))}, ease: "power2.in", immediateRender: false }}, {T(7)});')
j(f'tl.set("#fonds-intro", {{ scale: 1 }}, {T(8)});')
son(0.0, "impact-basse", 0.5, "ouverture")
son(0.02, "glitch-court", 0.34, "ouverture")
for x, nom in ((2, "impact-tambour"), (4, "impact-cartoon"), (6, "coup-mystere"), (7, "impact-futur")):
    son(T(x) + 0.02, nom, 0.4, "mot qui claque")
    secousse(T(x) + 0.02, 12, 3)
son(T(8), "riser-synth", 0.42, "montée avant le drop", fin=T(8) + 0.08)
son(T(7.9), "aspiration", 0.3, "aspiration avant le drop", fin=T(8))
for x in (7.25, 7.5, 7.75):
    eclair(T(x), "#ffffff", 0.05, 0.25)

# ---- DROP (temps 8)
eclair(T(8), "#ffffff", 0.12, 1)
barres_glitch(T(8) + 0.1)
secousse(T(8), 30, 6)
punch(T(8), 1.15, 0.45)
son(T(8), "impact-basse", 0.62, "DROP")
son(T(8), "impact-futur", 0.4, "DROP")
son(T(8), "tonnerre-transition", 0.3, "DROP")

# Fond du drop : une vraie vidéo par temps, assombrie, derrière le navigateur
drop_fond = ["ville-nuit-aerien", "tokyo-train-nuit", "trafic-nuit-tourne", "voiture-compteur", "neon-etincelles", "serveurs-lumieres",
             "voiture-rouge-spot", "hacker-darkweb", "robot-danse", "code-chiffres", "neon-japon", "fibre-optique", "hacker-glitch",
             "tokyo-train-nuit", "voiture-compteur", "ville-nuit-aerien"]
for k, f in enumerate(drop_fond):
    fond(T(8 + k), T(9 + k) if k < len(drop_fond) - 1 else FIN, f)
j(f'tl.set("#voile", {{ opacity: 0.66 }}, {T(8)});')

# Navigateur (vide) qui s'écrase sur le drop
HTML.append(f'''<div id="scene" class="ed-scene">
        <div id="nav" class="ed-nav" style="left: {NX}px; top: {NY}px; width: {NW}px; height: {round(BARRE + 720 * K)}px; opacity: 0">
          <div class="ed-nav-barre"><i></i><i></i><i></i><span id="url" data-layout-ignore>volt-sneakers.ci</span></div>
          <div class="ed-page-fenetre" style="height: {round(720 * K)}px">
            <div id="page" class="ed-page" style="transform: scale({K:.5f})">
              {"".join(bloc(n) for n in BOITES)}
              <img id="b-panier" class="ed-bloc" src="assets/img/volt-panier.png" style="left: 900px; top: {DEFILE}px; width: 380px; height: 720px; opacity: 0" alt="" />
            </div>
            <video id="v-cafe" class="clip ed-dans-nav" src="assets/video/cafe-hero-plein.mp4" data-start="{T(19)}" data-duration="{r(T(19.5) - T(19))}" data-track-index="6" muted playsinline></video>
            <img id="i-lecodeur" class="ed-dans-nav" src="assets/img/lecodeur-final.png" style="opacity: 0" alt="" />
            <img id="i-volt-final" class="ed-dans-nav" src="assets/img/volt-ecran.png" style="opacity: 0" alt="" />
          </div>
        </div>
        <div id="tel" class="ed-tel" style="left: 96px; top: 190px; opacity: 0">
          <div class="ed-tel-ecran"><img id="tel-volt" src="assets/img/volt-mobile.png" alt="" />
            <video id="tel-cafe" class="clip" src="assets/video/cafe-mobile.mp4" data-start="{T(19)}" data-duration="{r(T(19.5) - T(19))}" data-track-index="7" muted playsinline></video>
            <video id="tel-lecodeur" class="clip" src="assets/video/lecodeur-mobile.mp4" data-start="{T(19.5)}" data-duration="{r(T(20) - T(19.5))}" data-track-index="7" muted playsinline></video>
          </div>
        </div>
      </div>''')
j(f'tl.fromTo("#nav", {{ opacity: 0, scale: 1.35, rotation: -4 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.16, ease: "power4.out", immediateRender: false }}, {T(8)});')
j(f'tl.set("#perso", {{ opacity: 1 }}, {T(8)});')
j(f'tl.fromTo("#toi", {{ y: 300 }}, {{ y: 0, duration: 0.22, ease: "back.out(1.6)", immediateRender: false }}, {T(8)});')
pose("toi", T(8), 0.14, "back.out(2)", bg=150, bd=-150, tete=-8)
saut("toi", T(8) + 0.05, 50)
pose("toi", T(9) - 0.1, 0.16, bg=0, bd=0, tete=0)
# tête qui bat la mesure sur chaque temps du drop
for n in range(9, 24):
    if n not in (18, 22, 23):
        hoche("toi", T(n))

# URL tapée (temps 8 → 9)
url = "volt-sneakers.ci"
for k in range(len(url) + 1):
    j(f'tl.set("#url", {{ textContent: {json.dumps(url[:k] + ("|" if k < len(url) else ""))} }}, {r(T(8) + 0.12 + k * 0.028)});')
son(T(8) + 0.14, "clavier-ordi", 0.3, "l'URL se tape", sur_pic=False, d=0.5)

# Un bloc par temps, la caméra suit le bloc qui arrive
def arrive(nom, t, de="haut", note=""):
    dx, dy, rot = {"haut": (0, -140, 0), "gauche": (-420, 0, -6), "droite": (420, 0, 8), "bas": (0, 120, 0)}[de]
    j(f'tl.fromTo("#b-{nom}", {{ opacity: 0, x: {dx}, y: {dy}, rotation: {rot}, scale: 1.12 }}, {{ opacity: 1, x: 0, y: 0, rotation: 0, scale: 1, duration: 0.16, ease: "power4.out", immediateRender: false }}, {r(t)});')
    son(t + 0.02, tour(POPS), 0.42, note or nom)


def centre(nom, defile=0):
    x, y, w, h = BOITES[nom]
    return film_xy(x + w / 2, y + h / 2, defile)


def bras_vers(g, cote="bd"):
    pose("toi", g, 0.12, "back.out(2.5)", **{cote: -120 if cote == "bd" else 120})
    pose("toi", g + 0.42, 0.16, **{cote: 0})


arrive("menu", T(9), "haut", "le menu")
recadre(T(9) - 0.08, 960, 150, 1.3)
bras_vers(T(9))
arrive("titre", T(10), "gauche", "le titre")
recadre(T(10) - 0.08, *centre("titre"), 1.45)
secousse(T(10) + 0.12, 14, 3)
bras_vers(T(10), "bg")
arrive("photo", T(11), "droite", "la photo")
recadre(T(11) - 0.08, *centre("photo"), 1.2)
secousse(T(11) + 0.12, 14, 3)
j(f'tl.fromTo("#b-texte", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.14, immediateRender: false }}, {T(11.5)});')
son(T(11.5), "papier-glisse", 0.25, "le texte")
arrive("bouton", T(12), "bas", "le bouton")
j(f'tl.fromTo("#b-bouton", {{ filter: "drop-shadow(0 0 0px #DCFC1C)" }}, {{ filter: "drop-shadow(0 0 22px #DCFC1C)", duration: 0.2, yoyo: true, repeat: 1, immediateRender: false }}, {T(12) + 0.16});')
son(T(12) + 0.05, "clic-positif", 0.4, "clic sur le bouton")
recadre(T(12) - 0.08, *film_xy(420, 470), 1.25)
bras_vers(T(12))

# Défilement vers les produits (temps 13)
j(f'tl.to("#page", {{ y: {-DEFILE}, duration: 0.24, ease: "power3.inOut" }}, {T(13) - 0.1});')
recadre(T(13) - 0.1, 960, 470, 1.0)
son(T(13), "swoosh-vitesse", 0.42, "défilement vers les produits")
eclair(T(13), "#DCFC1C", 0.06, 0.35)
barres_glitch(T(13))
arrive("titre-produits", T(13) + 0.12, "gauche", "les plus vendues")
for k, x in enumerate((14, 14.5, 15, 15.5)):
    arrive(f"p{k}", T(x), "bas", f"produit {k + 1}")
    px, py = centre(f"p{k}", DEFILE)
    recadre(T(x) - 0.06, px, py, 1.38 if k % 2 == 0 else 1.32, 0.18)
    if x == int(x):
        secousse(T(x) + 0.1, 10, 3)
# Panier (temps 16)
j(f'tl.fromTo("#b-panier", {{ opacity: 1, x: 420 }}, {{ opacity: 1, x: 0, duration: 0.2, ease: "power4.out", immediateRender: false }}, {T(16)});')
recadre(T(16) - 0.08, *film_xy(1090, DEFILE + 360, DEFILE), 1.2)
son(T(16) + 0.05, "scanner-caisse", 0.45, "panier")
son(T(16), tour(WHOOSH), 0.36, "le panier glisse")
bras_vers(T(16), "bg")
# Téléphone (temps 17) : la version mobile défile
j(f'tl.fromTo("#tel", {{ opacity: 0, y: 700, rotation: 14 }}, {{ opacity: 1, y: 0, rotation: -6, duration: 0.2, ease: "power4.out", immediateRender: false }}, {T(17)});')
j(f'tl.fromTo("#tel-volt", {{ y: 0 }}, {{ y: -1150, duration: {r(T(19) - T(17) - 0.1)}, ease: "power1.inOut", immediateRender: false }}, {T(17) + 0.2});')
recadre(T(17) - 0.08, 760, 540, 1.0)
son(T(17), "swoosh-monte", 0.42, "le téléphone arrive")
son(T(17) + 0.16, "impact-tambour", 0.36, "le téléphone se pose")
secousse(T(17) + 0.16, 16, 4)
# Site complet (temps 18)
son(T(18) + 0.12, "impact-cartoon", 0.4, "tampon")
son(T(18) + 0.12, "cloche-succes", 0.36, "site complet")
secousse(T(18) + 0.13, 20, 4)
pose("toi", T(18), 0.14, "back.out(2)", bg=165, bd=-165, tete=-8)
saut("toi", T(18) + 0.05, 46)
saut("toi", T(18) + 0.36, 30)
pose("toi", T(19) - 0.08, 0.14, bg=0, bd=0, tete=0)
confetti = []
for k in range(26):
    ang = k * 2.39996
    dist = 460 * (0.45 + 0.55 * ((k * 37) % 11) / 10)
    dx, dy = round(math.cos(ang) * dist), round(math.sin(ang) * dist * 0.7 - 120)
    coul = "#DCFC1C" if k % 3 else "#ECECE8"
    w, h = (20, 11) if k % 2 else (13, 13)
    confetti.append(f'<i id="cf-{k}" class="ed-cf" style="width: {w}px; height: {h}px; background: {coul}"></i>')
    j(f'tl.fromTo("#cf-{k}", {{ x: 0, y: 0, rotation: 0, opacity: 1 }}, {{ x: {dx}, y: {dy + 280}, rotation: {(k * 97) % 540 - 270}, opacity: 0, duration: 1.2, ease: "power2.out", immediateRender: false }}, {T(18) + 0.12});')
HTML.append(f'<div class="ed-confettis" style="left: 1380px; top: 760px">{"".join(confetti)}</div>')
son(T(18) + 0.14, "paillettes", 0.3, "confettis")

# D'autres sites, un par temps (temps 19, 20) puis retour sur VOLT
def change_site(t, url_txt, puce, sel_on=None, sel_off=None):
    if sel_off:
        j(f'tl.set("{sel_off}", {{ opacity: 0 }}, {r(t)});')
    if sel_on:
        j(f'tl.set("{sel_on}", {{ opacity: 1 }}, {r(t)});')
    j(f'tl.set("#url", {{ textContent: {json.dumps(url_txt)} }}, {r(t)});')
    j(f'tl.fromTo("#nav", {{ x: 160, filter: "blur(10px)" }}, {{ x: 0, filter: "blur(0px)", duration: 0.16, ease: "power3.out", immediateRender: false }}, {r(t)});')
    eclair(t, "#ffffff", 0.06, 0.55)
    son(t, "fouet", 0.42, f"site suivant : {puce}")
    son(t + 0.04, "obturateur", 0.32, "déclic")


j(f'tl.set("#tel-volt", {{ opacity: 0 }}, {T(19)});')
change_site(T(19), "cafe-aurore.ci", "Un café")
recadre(T(19) - 0.06, 960, 520, 1.06, 0.16)
change_site(T(19.5), "lecodeur.fr", "Une chaîne", "#i-lecodeur")
recadre(T(19.5) - 0.06, 900, 560, 1.12, 0.16)
change_site(T(20), "volt-sneakers.ci", "Une boutique", "#i-volt-final", "#i-lecodeur")
j(f'tl.set("#tel-volt", {{ opacity: 1, y: 0 }}, {T(20)});')
recadre(T(20) - 0.06, 960, 540, 1.0, 0.16)

# Les mots de la fin, sur le site (temps 21 → 24)
# Fin SANS TEXTE (temps 20 → 24) : la caméra tourne autour du site, un flash et un zoom par temps, puis la boucle repart
recadre(T(21) - 0.06, *film_xy(950, 400), 1.35, 0.18)
recadre(T(22) - 0.06, 260, 640, 1.3, 0.18)
recadre(T(23) - 0.06, 960, 540, 1.0, 0.2)
for x in (21, 22, 23):
    eclair(T(x), "#ffffff", 0.06, 0.45)
    son(T(x), IMPACTS[x % 3], 0.42, "coup de fin")
    secousse(T(x) + 0.02, 18, 4)
barres_glitch(T(23.5))
j(f'tl.to("#cam", {{ scale: 1.25, rotation: -3, duration: {r(FIN - T(23.5))}, ease: "power3.in" }}, {T(23.5)});')
eclair(FIN - 0.05, "#000000", 0.05, 1)
pose("toi", T(21), 0.14, "back.out(2)", bg=165, bd=-165, tete=-8)
saut("toi", T(21) + 0.05, 44)
saut("toi", T(22) + 0.05, 30)
saut("toi", T(23) + 0.05, 30)
son(FIN - 0.05, "rewind-glitch", 0.36, "la boucle repart")
HTML.append(f'<div id="perso" style="position: absolute; inset: 0; opacity: 0">{perso("toi", 1760, 1030, 330, "toi")}</div>')

# Coups de zoom sur chaque temps du drop, petites secousses sur les kicks entre les temps
for n in range(9, 24):
    punch(T(n), 1.06 if n % 2 == 0 else 1.04, 0.3)
for k in KICKS:
    if T(8) < k < FIN - 0.1 and min(abs(k - T(n)) for n in range(8, 25)) > 0.08:
        j(f'tl.to("#cam", {{ keyframes: [{{ y: 7, duration: 0.03 }}, {{ y: -4, duration: 0.03 }}, {{ y: 0, duration: 0.04 }}] }}, {r(k)});')

# ================================================================ ÉCRITURE
fond_html = []
for k, (t0, t1, f) in enumerate(FOND):
    fond_html.append(f'<video id="f-{k}" class="clip ed-fond" src="assets/video/{f}.mp4" data-start="{t0}" data-duration="{r(t1 - t0)}" '
                     f'data-track-index="{2 + k % 2}" muted playsinline></video>')

CSS_EDIT = """
      .ed-cam { position: absolute; inset: 0; transform-origin: 50% 50%; }
      .ed-fond { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }
      #voile { position: absolute; inset: 0; background: #050507; opacity: 0.42; }
      .ed-scene { position: absolute; inset: 0; transform-origin: 50% 50%; }
      .ed-mot { position: absolute; left: 0; width: 1920px; transform: translateY(-50%); text-align: center; font-family: "Anton", sans-serif;
        line-height: 1; text-transform: uppercase; white-space: nowrap; letter-spacing: 0.01em;
        text-shadow: -7px 0 0 rgba(255, 42, 85, 0.85), 7px 0 0 rgba(0, 229, 255, 0.85), 0 14px 50px rgba(0, 0, 0, 0.8); }
      .ed-commente { display: flex; align-items: center; justify-content: center; gap: 34px; font-size: 170px; color: #fff; }
      .ed-commente b { display: inline-block; font-weight: 400; background: #DCFC1C; color: #0a0a06; padding: 4px 34px 14px; text-shadow: none; }
      .ed-noir { position: absolute; inset: 0; background: #000; }
      .ed-eclair { position: absolute; inset: 0; opacity: 0; }
      .ed-glitch { position: absolute; inset: 0; opacity: 0; mix-blend-mode: screen; }
      .ed-glitch i { position: absolute; }
      .ed-nav { position: absolute; border-radius: 18px; overflow: hidden; background: #0d0d10; border: 3px solid #2c2c33;
        box-shadow: 0 40px 120px rgba(0, 0, 0, 0.85), 0 0 60px rgba(220, 252, 28, 0.12); }
      .ed-nav-barre { height: 46px; display: flex; align-items: center; gap: 10px; padding: 0 18px; background: #0a0a0c; border-bottom: 1px solid #222; }
      .ed-nav-barre i { width: 13px; height: 13px; border-radius: 50%; background: #444; }
      .ed-nav-barre i:first-child { background: #DCFC1C; }
      .ed-nav-barre span { margin-left: 14px; font: 600 21px/1 "JetBrains Mono", ui-monospace, monospace; color: #b8b8b8; white-space: nowrap; }
      .ed-page-fenetre { position: relative; overflow: hidden; }
      .ed-page { position: absolute; left: 0; top: 0; width: 1280px; height: 1700px; transform-origin: 0 0; }
      .ed-bloc { position: absolute; display: block; }
      .ed-dans-nav { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; object-position: top; }
      .ed-tel { position: absolute; width: 300px; height: 610px; border: 11px solid #0c0c0c; border-radius: 46px; overflow: hidden; background: #0d0d10;
        box-shadow: 0 40px 100px rgba(0, 0, 0, 0.85), 0 0 0 3px #3a3a3a; }
      .ed-tel-ecran { position: absolute; inset: 0; overflow: hidden; }
      .ed-tel-ecran img { position: absolute; left: 0; top: 0; width: 100%; }
      .ed-tel-ecran video { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; object-position: top; }
      .ed-sticker { font-size: 92px; box-shadow: 12px 12px 0 #000; }
      .ed-puce { position: absolute; padding: 12px 30px 16px; background: #fe2c55; color: #fff; font-family: "Anton", sans-serif; font-size: 64px;
        line-height: 1; text-transform: uppercase; white-space: nowrap; box-shadow: 10px 10px 0 #000; }
      .ed-confettis { position: absolute; width: 0; height: 0; }
      .ed-cf { position: absolute; left: 0; top: 0; opacity: 0; }
"""

tete = (ICI / "tools/tete.html").read_text()
tete = tete.replace('data-resolution="landscape"', 'data-resolution="landscape"')
sons_html = []
libre = []  # fin du dernier son de chaque piste
for k, (t0, nom, v, note, d) in enumerate(sorted(SONS)):
    piste = next((i for i, f in enumerate(libre) if f <= t0), None)
    if piste is None:
        libre.append(0)
        piste = len(libre) - 1
    libre[piste] = t0 + d + 0.01
    sons_html.append(f'<audio id="sfx-{k + 1:03d}" src="assets/sfx/{nom}.mp3" data-start="{t0}" data-duration="{d}" data-volume="{v}" '
                     f'data-track-index="{30 + piste}"></audio><!-- {note} -->')
page = tete + CSS_EDIT + """    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="%(fin)s" data-width="1920" data-height="1080">
      <div id="fond" class="clip" data-start="0" data-duration="%(fin)s" data-track-index="0"></div>
      <div id="cam" class="ed-cam">
        <div id="fonds-intro" class="ed-cam">
        %(fonds)s
        </div>
        <div id="voile"></div>
        %(corps)s
      </div>
      <audio id="musique" src="assets/music/phonk-remix-holiznacc0.wav" data-start="0" data-duration="%(fin)s" data-volume="1" data-track-index="10"></audio>
      %(sons)s
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
%(js)s
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""" % {"fin": FIN, "fonds": "\n        ".join(fond_html), "corps": "\n      ".join(HTML), "sons": "\n      ".join(sons_html), "js": "\n".join(JS)}
(ICI / "index.html").write_text(page, encoding="utf-8")
print(f"edit écrit : {len(FOND)} vidéos de fond, {len(SONS)} bruitages, {len(JS)} lignes d'animation, fin à {FIN} s")
