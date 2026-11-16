#!/usr/bin/env python3
"""Edit Claude v2, FAÇON EDIT D'ANIME, vertical 1080×1920, sur « Close Eyes » (DVRST), extrait officiel de 30 s (non libre,
choisi par l'utilisateur : à publier avec le son TikTok). Pas de voix, pas de sous-titres, pas de dates : seulement les noms.

Les coupes et les effets tombent sur les VRAIES frappes du son (détectées dans assets/music/son-edit.wav) :
  intro 0–4,98 (sombre, ralenti, logo qui scintille sur les frappes 0 / 0,46 / 0,93 / 2,36)
  montée 4,98–18,75 : accent toutes les 2,497 s (4,98 · 9,98 · 12,48 · 14,97 · 17,47) + petites frappes à +0,47 et +0,94
  silence 18,75–19,96 : image figée, qui se décolore et s'approche, montée inversée
  DROP 19,96 → fin : une frappe toutes les 0,312 s → une coupe par frappe, secousse, zoom, flash, RGB, stroboscope.
Effets (déterministes, image par image) : plans « velocity » (accéléré puis ralenti, assets/vel, tools/preparer-velocity.sh),
secousses avec flou de mouvement, zoom-claque, flash blanc, flash inversé, aberration RVB (filtre SVG), stroboscope, vraies fuites
de lumière en mode écran, étalonnage froid → chaud, grain, vignette, bandes noires, textes qui claquent avec lueur et tremblement.
Relancer ce script ÉCRASE index.html.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent.parent
FIN = 29.95
TERRA, CREME = "#D97757", "#F0EEE6"
NL = "\n"


def r(x):
    return round(x, 3)


# ================================================================ FRAPPES DU SON
def frappes():
    sr = 22050
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ICI / "assets/music/son-edit.wav"), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    hop, n = 110, 1024
    fr = (len(x) - n) // hop
    S = np.log1p(np.abs(np.fft.rfft(np.stack([x[i * hop:i * hop + n] * np.hanning(n) for i in range(fr)]), axis=1)))
    flux = np.maximum(0, np.diff(S, axis=0)).sum(1)
    t = np.arange(len(flux)) * hop / sr + hop / sr
    thr = np.percentile(flux, 97)
    pk = [round(float(t[i]), 3) for i in range(1, len(flux) - 1) if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
    out = []
    for p in pk:  # une frappe au plus toutes les 0,12 s
        if not out or p - out[-1] > 0.12:
            out.append(p)
    return out


HITS = frappes()
DROP = next(h for h in HITS if h > 19.5)
ACCENTS = [4.984, 9.977, 12.477, 14.971, 17.47]
SOUS = [h for h in HITS if 5.3 < h < 18.6 and all(abs(h - a) > 0.2 for a in ACCENTS)]
DROP_HITS = [h for h in HITS if h >= DROP and h < FIN - 0.15]

JS, VIDS, OVER, SONS = [], [], [], []


def j(l):
    JS.append("      " + l)


# ================================================================ SON (bruitages calés sur les frappes)
SFX = ICI / "assets/sfx"
PICS = json.loads((SFX / "pics.json").read_text())


def son(t, nom, v=0.3, note="", sur_pic=True, d=None):
    p = PICS[nom]
    debut = max(0.0, t - (p["pic"] if sur_pic else 0))
    duree = min(p["duree"], d or 99, FIN - debut)
    if duree > 0.05:
        SONS.append((r(debut), nom, round(v, 3), note, r(duree)))


TOURS = {}


def tour(liste):
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


WHOOSH = ["whoosh-cine", "whoosh-fusee", "swoosh-vitesse", "whoosh-metal", "fouet", "balaie-rapide"]


# ================================================================ PLANS
def plan(src, t0, t1, eff="coup", depart=0.0, k=0):
    vid = f"p{len(VIDS):03d}"
    VIDS.append(f'<video id="{vid}" class="clip ed-plan" src="assets/{src}.mp4" data-start="{r(t0)}" data-duration="{r(t1 - t0 + 0.03)}" '
                f'data-media-start="{depart}" data-track-index="{1 + len(VIDS) % 2}" muted playsinline style="opacity: 0"></video>')
    j(f'tl.set("#{vid}", {{ opacity: 1 }}, {r(t0)});')
    j(f'tl.set("#{vid}", {{ opacity: 0 }}, {r(t1 + 0.02)});')
    d = t1 - t0
    sel = f"#{vid}"
    if eff == "coup":
        j(f'tl.fromTo("{sel}", {{ scale: 1.3 }}, {{ scale: 1.04, duration: {r(min(0.25, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "pousse":
        j(f'tl.fromTo("{sel}", {{ scale: 1.0 }}, {{ scale: 1.25, duration: {r(d)}, ease: "none", immediateRender: false }}, {r(t0)});')
    elif eff == "fouet":
        s = 1 if k % 2 else -1
        j(f'tl.fromTo("{sel}", {{ x: {s * 260}, scale: 1.15, filter: "blur(20px)" }}, {{ x: 0, scale: 1.04, filter: "blur(0px)", duration: {r(min(0.09, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "spin":
        s = 1 if k % 2 else -1
        j(f'tl.fromTo("{sel}", {{ rotation: {s * 22}, scale: 1.5, filter: "blur(16px)" }}, {{ rotation: 0, scale: 1.05, filter: "blur(0px)", duration: {r(min(0.18, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "zoom":
        j(f'tl.fromTo("{sel}", {{ scale: 0.55, filter: "blur(16px)" }}, {{ scale: 1.05, filter: "blur(0px)", duration: {r(min(0.16, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif eff == "drop":
        j(f'tl.fromTo("{sel}", {{ scale: 1.8 }}, {{ scale: 1.05, duration: {r(min(0.3, d))}, ease: "power4.out", immediateRender: false }}, {r(t0)});')
    elif eff == "tilt":
        s = 1 if k % 2 else -1
        j(f'tl.fromTo("{sel}", {{ rotationY: {s * 35}, scale: 1.3 }}, {{ rotationY: 0, scale: 1.05, duration: {r(min(0.2, d))}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    return vid


# ================================================================ EFFETS
def flash(t, coul="#ffffff", op=0.8, d=0.07):
    k = len(OVER)
    OVER.append(f'<div id="fl{k}" class="ed-flash" style="background: {coul}"></div>')
    j(f'tl.set("#fl{k}", {{ opacity: {op} }}, {r(t)});')
    j(f'tl.to("#fl{k}", {{ opacity: 0, duration: {d}, ease: "power2.out" }}, {r(t + 0.034)});')


def secousse(t, amp=26, n=5):
    kf = [f'{{ x: {r(amp * (1 - k / n) * (1 if k % 2 == 0 else -1))}, y: {r(amp * 0.7 * (1 - k / n) * (-1 if k % 2 == 0 else 1))}, '
          f'rotation: {r(amp * 0.06 * (1 - k / n) * (1 if k % 2 else -1))}, duration: 0.033 }}' for k in range(n)]
    kf.append('{ x: 0, y: 0, rotation: 0, duration: 0.04 }')
    j(f'tl.to("#cam", {{ keyframes: [{", ".join(kf)}] }}, {r(t)});')
    j(f'tl.fromTo("#flou", {{ filter: "blur({min(10, amp // 3)}px)" }}, {{ filter: "blur(0px)", duration: 0.12, immediateRender: false }}, {r(t)});')


def punch(t, s=1.12, d=0.22):
    j(f'tl.fromTo("#zoom", {{ scale: {s} }}, {{ scale: 1, duration: {d}, ease: "power3.out", immediateRender: false }}, {r(t)});')


def rgb(t, force=26, d=0.16):
    j(f'tl.set("#rgbw", {{ filter: "url(#rgb)" }}, {r(t)});')
    j(f'tl.fromTo("#rgb-r", {{ attr: {{ dx: {force} }} }}, {{ attr: {{ dx: 0 }}, duration: {d}, ease: "power2.out", immediateRender: false }}, {r(t)});')
    j(f'tl.fromTo("#rgb-b", {{ attr: {{ dx: {-force} }} }}, {{ attr: {{ dx: 0 }}, duration: {d}, ease: "power2.out", immediateRender: false }}, {r(t)});')
    j(f'tl.set("#rgbw", {{ filter: "none" }}, {r(t + d + 0.01)});')


def inverse(t, d=0.067):
    j(f'tl.set("#cam", {{ filter: "invert(1)" }}, {r(t)});')
    j(f'tl.set("#cam", {{ filter: "invert(0)" }}, {r(t + d)});')


def fuite(t, d=1.2, op=0.75, nom="fuite-ambre"):
    k = len(OVER)
    OVER.append(f'<video id="lk{k}" class="clip ed-fuite" src="assets/fx/{nom}.mp4" data-start="{r(t)}" data-duration="{r(d)}" '
                f'data-media-start="0.3" data-track-index="{40 + k % 3}" muted playsinline style="opacity: 0"></video>')
    j(f'tl.fromTo("#lk{k}", {{ opacity: 0 }}, {{ opacity: {op}, duration: {r(d * 0.3)}, ease: "sine.out", immediateRender: false }}, {r(t)});')
    j(f'tl.to("#lk{k}", {{ opacity: 0, duration: {r(d * 0.5)}, ease: "sine.in" }}, {r(t + d * 0.5)});')


def grade(t, d, filtre, ease="none"):
    j(f'tl.to("#grade", {{ filter: "{filtre}", duration: {d}, ease: "{ease}" }}, {r(t)});')


def bandes(t, h, d=0.2):
    j(f'tl.to(".ed-bande", {{ height: {h}, duration: {d}, ease: "power3.inOut" }}, {r(t)});')


NOMS = []


def nom(txt, t, t1, taille=200, sous="CLAUDE", style="claque", y=820):
    """Nom qui claque, avec lueur, ombre RVB et tremblement (pas de date)."""
    k = len(NOMS)
    i = f"n{k}"
    s = f"<span>{sous}</span>" if sous else ""
    NOMS.append(f'<div id="{i}" class="ed-nom" style="top: {y}px; opacity: 0">{s}<b style="font-size: {taille}px">{txt}</b></div>')
    if style == "claque":
        j(f'tl.fromTo("#{i}", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1, duration: 0.1, ease: "power4.in", immediateRender: false }}, {r(t)});')
    elif style == "glisse":
        j(f'tl.fromTo("#{i}", {{ opacity: 0, x: -500, skewX: 25 }}, {{ opacity: 1, x: 0, skewX: 0, duration: 0.1, ease: "power3.out", immediateRender: false }}, {r(t)});')
    else:
        j(f'tl.fromTo("#{i}", {{ opacity: 0, rotationX: 90 }}, {{ opacity: 1, rotationX: 0, duration: 0.12, ease: "back.out(2)", immediateRender: false }}, {r(t)});')
    j(f'tl.fromTo("#{i} b", {{ textShadow: "-16px 0 0 #00e5ff, 16px 0 0 #ff2a6d, 0 0 60px rgba(217,119,87,1)" }}, '
      f'{{ textShadow: "0px 0 0 #00e5ff, 0px 0 0 #ff2a6d, 0 0 40px rgba(217,119,87,0.8)", duration: 0.18, immediateRender: false }}, {r(t)});')
    j(f'tl.to("#{i}", {{ x: 6, duration: 0.04, yoyo: true, repeat: {max(1, int((t1 - t - 0.1) / 0.04))}, ease: "none" }}, {r(t + 0.1)});')
    j(f'tl.set("#{i}", {{ opacity: 0 }}, {r(t1 - 0.01)});')


# ================================================================ 1. INTRO (0 → 4,98) : sombre et lent, le logo scintille sur les frappes
j('tl.set("#grade", { filter: "saturate(0.3) contrast(1.25) brightness(0.65)" }, 0);')
j('tl.set(".ed-bande", { height: 230 }, 0);')
plan("video/robot-yeux", 0.0, 2.36, "pousse", 0.5)
plan("captures/docs-modeles-tableau", 2.36, 4.984, "pousse", 0.6)
OVER.append('<div id="logo" class="ed-logo" style="opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /></div>')
for t, op in ((0.0, 1), (0.46, 0.25), (0.47, 1), (0.93, 0.2), (0.94, 1)):
    j(f'tl.set("#logo", {{ opacity: {op} }}, {r(t)});')
j('tl.fromTo("#logo", { scale: 0.8 }, { scale: 1.15, duration: 2.3, ease: "none", immediateRender: false }, 0);')
j('tl.fromTo("#logo img", { rotation: 0 }, { rotation: 90, duration: 2.3, ease: "none", immediateRender: false }, 0);')
j('tl.to("#logo", { opacity: 0, scale: 2.2, duration: 0.25, ease: "power3.in" }, 2.15);')
for t in (0.0, 0.46, 0.93):
    rgb(t, 18, 0.14)
    son(t, "glitch-mini", 0.22, "scintillement du logo")
son(0.0, "intro-mystere", 0.3, "ouverture")
flash(2.36, "#ffffff", 0.6)
son(2.36, "whoosh-tunnel", 0.35, "passage au tableau des modèles")
fuite(0.2, 2.4, 0.45, "fuite-bleue")
fuite(2.5, 2.4, 0.5, "fuite-ambre")
grade(2.36, 2.6, "saturate(0.7) contrast(1.2) brightness(0.8)", "power1.in")
son(4.0, "riser-tech", 0.3, "montée vers le premier accent", d=0.98)

# ================================================================ 2. MONTÉE (4,98 → 18,75) : un accent par mesure, petites frappes, noms des familles
bandes(4.984, 0, 0.15)
grade(4.984, 0.3, "saturate(1.15) contrast(1.15) brightness(0.95)")
FAMILLES = [("HAIKU", "vel/vel-tunnel-virtuel-bleu"), ("SONNET", "vel/vel-main-hologramme"), ("OPUS", "vel/vel-eclair-ville"),
            ("MYTHOS", "vel/vel-supernova"), ("FABLE", "vel/vel-trou-de-ver")]
REMPL = ["rap-doigts-tapent", "rap-serveurs-lumieres", "rap-ecrans-matrix", "rap-traces-lumiere", "rap-data-center", "rap-neon-3d-route",
         "rap-globe-reseau", "rap-lasers", "rap-clavier-gros-plan", "rap-main-hologramme", "rap-particules-lumineuses", "rap-claude-code-site"]
coupes = sorted(ACCENTS + SOUS)
for k, t0 in enumerate(coupes):
    t1 = coupes[k + 1] if k + 1 < len(coupes) else 18.75
    if t0 in ACCENTS:
        a = ACCENTS.index(t0)
        fam, src = FAMILLES[a]
        plan(src, t0, t1, "drop", 0.0, k)
        nom(fam, t0, min(t1, t0 + 1.8), 260, "CLAUDE", ("claque", "glisse", "tourne")[a % 3])
        son(t0, "trailer-impact", 0.55, f"accent {fam}")
        son(t0, tour(WHOOSH), 0.4, "souffle de l'accent")
        flash(t0, "#ffffff", 0.9)
        secousse(t0 + 0.02, 34)
        punch(t0, 1.18, 0.3)
        rgb(t0, 30, 0.2)
        fuite(t0, 1.6, 0.55, ("fuite-ambre", "fuite-rouge", "flare-soleil", "fuite-violette", "fuite-spirale")[a])
    else:
        plan("vel/" + REMPL[k % len(REMPL)], t0, t1, ("fouet", "spin", "zoom", "tilt")[k % 4], 0.2, k)
        son(t0, tour(["glitch-mini", "obturateur", "swoosh-court", "glitch-court"]), 0.3, "petite frappe")
        secousse(t0, 14, 4)
        punch(t0, 1.07, 0.18)
        if k % 2:
            flash(t0, TERRA, 0.35)
# le long passage calme entre 5,9 et 9,98 : la vraie page de claude.com au ralenti
plan("captures/claude-accueil", 6.4, 9.977, "pousse", 0.5)
flash(6.4, "#ffffff", 0.4)
son(6.4, "whoosh-cine", 0.3, "page claude.com")

# ================================================================ 3. SILENCE (18,75 → DROP) : image figée qui se décolore et s'approche
OVER.append(f'<div id="fige" class="ed-fige" style="opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /></div>')
plan("video/robot-yeux", 18.75, DROP, "pousse", 3.5)
j(f'tl.set("#fige", {{ opacity: 1 }}, 18.75);')
j(f'tl.fromTo("#fige", {{ scale: 0.4 }}, {{ scale: 1.6, duration: {r(DROP - 18.75)}, ease: "power2.in", immediateRender: false }}, 18.75);')
j(f'tl.set("#fige", {{ opacity: 0 }}, {r(DROP)});')
grade(18.75, r(DROP - 18.75), "saturate(0) contrast(1.4) brightness(0.55)", "power2.in")
bandes(18.75, 520, r(DROP - 18.75))
son(18.75, "rembobine-magie", 0.45, "montée inversée", d=DROP - 18.75)
son(18.8, "aspiration-air", 0.4, "aspiration avant le drop")

# ================================================================ 4. DROP : une coupe par frappe, noms sans dates
bandes(DROP, 0, 0.06)
grade(DROP, 0.05, "saturate(1.35) contrast(1.2) brightness(1.05)")
son(DROP, "tonnerre-transition", 0.5, "DROP")
son(DROP, "trailer-impact-2", 0.6, "DROP")
flash(DROP, "#ffffff", 1.0, 0.12)
inverse(DROP + 0.05)
DROP_SRC = ["vel-nasa-artemis-decolle", "rap-foule-saute", "rap-lasers", "vel-explosion-particules", "rap-dj-scene", "rap-traces-lumiere",
            "vel-robot-danse", "rap-feux-artifice", "rap-nasa-booster-feu", "rap-public-mains", "vel-fusee", "rap-lumieres-scene",
            "rap-fusee", "vel-neon-3d-route", "rap-eclair-ville", "rap-supernova",
            "rap-robot-yeux", "vel-data-center", "rap-tunnel-virtuel-bleu", "vel-globe-reseau", "rap-serveurs-lumieres", "vel-particules-lumineuses",
            "rap-claude-code-site", "vel-lumieres-scene", "rap-robot-danse", "vel-traces-lumiere"]
NOMS_DROP = ["OPUS 5.5", "SONNET 5.5", "HAIKU 5.5", "FABLE 5.2", "MYTHOS 5.2", "OPUS 5", "SONNET 5", "FABLE 5", "OPUS 4.8", "OPUS 4.7",
             "SONNET 4.6", "OPUS 4.5", "SONNET 4.5", "HAIKU 4.5", "OPUS 4", "SONNET 3.7", "OPUS 3", "CLAUDE 2"]
EFFETS = ["drop", "fouet", "spin", "coup", "zoom", "fouet", "tilt", "coup"]
fin_drop = 28.7
dh = [h for h in DROP_HITS if h < fin_drop]
for k, t0 in enumerate(dh):
    t1 = dh[k + 1] if k + 1 < len(dh) else fin_drop
    src = DROP_SRC[k % len(DROP_SRC)]
    plan("vel/" + src, t0, t1, EFFETS[k % len(EFFETS)], round((k * 0.37) % 0.9, 2), k)
    secousse(t0 + 0.01, 30 if k % 2 == 0 else 18)
    punch(t0, 1.14 if k % 2 == 0 else 1.07, r(min(0.2, (t1 - t0) - 0.01)))
    if k % 2 == 0:
        n = NOMS_DROP[(k // 2) % len(NOMS_DROP)]
        nom(n, t0, min(t1 + (dh[k + 2] - t1 if k + 2 < len(dh) else 0.3), fin_drop), 190 if len(n) <= 8 else 160, "CLAUDE", ("claque", "glisse", "tourne")[(k // 2) % 3])
        flash(t0, "#ffffff" if (k // 2) % 2 == 0 else TERRA, 0.55)
        son(t0, tour(["impact-basse", "impact-tambour", "impact-futur"]), 0.3, f"nom {n}")
    else:
        rgb(t0, 22, 0.12)
        j(f'tl.fromTo("#strobe", {{ opacity: 0.45 }}, {{ opacity: 0, duration: 0.06, immediateRender: false }}, {r(t0)});')
    if k % 8 == 7:
        inverse(t0)
        son(t0, "obturateur", 0.3, "flash inversé")
    son(t0, tour(WHOOSH), 0.18, "coupe du drop")
for t in (DROP, 22.46, 24.96, 27.45):
    fuite(t, 1.4, 0.6, tour(["flare-soleil", "fuite-rouge", "fuite-ambre", "fuite-spirale"]))
OVER.append('<div id="strobe" class="ed-flash" style="background: #fff"></div>')

# ================================================================ 5. FIN (28,7 → 29,95) : le logo et « CLAUDE »
plan("vel/vel-trou-de-ver", fin_drop, FIN, "drop", 0.0)
OVER.append('<div id="fin-logo" class="ed-logo" style="top: 520px; opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /></div>')
j(f'tl.fromTo("#fin-logo", {{ opacity: 0, scale: 3 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power4.in", immediateRender: false }}, {fin_drop});')
j(f'tl.fromTo("#fin-logo img", {{ rotation: 0 }}, {{ rotation: 120, duration: {r(FIN - fin_drop)}, ease: "power2.out", immediateRender: false }}, {fin_drop});')
nom("CLAUDE", fin_drop + 0.31, FIN, 300, "", "claque", 1000)
flash(fin_drop, "#ffffff", 1.0, 0.12)
secousse(fin_drop + 0.02, 40)
son(fin_drop, "trailer-impact", 0.55, "fin")
j(f'tl.fromTo("#fondu", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, immediateRender: false }}, {r(FIN - 0.25)});')
OVER.append('<div id="fondu" class="ed-flash" style="background: #000"></div>')

# ================================================================ ÉCRITURE
_vus = set()
SONS[:] = [x for x in SONS if not ((x[0], x[1]) in _vus or _vus.add((x[0], x[1])))]
pistes, sons_html = {}, []
for n, (d0, f, v, note, dd) in enumerate(sorted(SONS), start=1):
    p = 30
    while pistes.get(p, -1) > d0 - 0.01:
        p += 1
    pistes[p] = d0 + dd
    sons_html.append(f'<audio id="sfx-{n:03d}" src="assets/sfx/{f}.mp3" data-start="{d0}" data-duration="{dd}" data-volume="{v}" data-track-index="{p}"></audio><!-- {note} -->')
GRAIN = ("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
         "type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' "
         "height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")
page = f"""<!doctype html>
<html lang="fr" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      /* Edit Claude façon edit d'anime (écrit par tools/construire-edit-anime.py). */
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.woff2") format("woff2"); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #fond {{ position: absolute; inset: 0; background: #000; }}
      #rgbw, #grade, #flou, #zoom {{ position: absolute; inset: 0; }}
      #zoom {{ transform-origin: 50% 50%; }}
      #cam {{ position: absolute; left: -80px; top: -80px; width: 1240px; height: 2080px; overflow: hidden; transform-origin: 50% 50%; perspective: 1400px; }}
      .ed-plan {{ position: absolute; left: 80px; top: 80px; width: 1080px; height: 1920px; object-fit: cover; transform-origin: 50% 50%; }}
      #teinte {{ position: absolute; inset: 0; mix-blend-mode: soft-light; opacity: 0.35;
        background: linear-gradient(180deg, rgba(0, 90, 140, 0.9) 0%, rgba(20, 20, 40, 0.5) 45%, rgba(217, 119, 87, 0.9) 100%); }}
      #vignette {{ position: absolute; inset: 0; background: radial-gradient(ellipse 75% 62% at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.75) 100%); }}
      #grain {{ position: absolute; inset: -50%; width: 200%; height: 200%; opacity: 0.12; background: url("{GRAIN}");
        animation: ed-grain 0.4s steps(1) infinite; mix-blend-mode: overlay; }}
      @keyframes ed-grain {{ 0%, 100% {{ transform: translate(0, 0); }} 20% {{ transform: translate(-6%, 4%); }}
        40% {{ transform: translate(5%, -7%); }} 60% {{ transform: translate(-4%, 8%); }} 80% {{ transform: translate(7%, 3%); }} }}
      .ed-fuite {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; mix-blend-mode: screen; }}
      .ed-flash {{ position: absolute; inset: 0; opacity: 0; }}
      .ed-bande {{ position: absolute; left: 0; width: 1080px; height: 0; background: #000; z-index: 5; }}
      #bande-h {{ top: 0; }}
      #bande-b {{ bottom: 0; }}
      .ed-logo {{ position: absolute; left: 290px; top: 710px; width: 500px; height: 500px; filter: drop-shadow(0 0 70px rgba(217,119,87,0.95)); }}
      .ed-logo img, .ed-fige img {{ width: 100%; height: 100%; }}
      .ed-fige {{ position: absolute; left: 240px; top: 660px; width: 600px; height: 600px; filter: drop-shadow(0 0 90px rgba(255,255,255,0.6)) grayscale(1) brightness(1.6); }}
      #noms {{ position: absolute; inset: 0; z-index: 4; perspective: 1200px; }}
      .ed-nom {{ position: absolute; left: 0; width: 1080px; text-align: center; }}
      .ed-nom span {{ display: inline-block; font-family: "Anton", sans-serif; font-size: 70px; letter-spacing: 16px; color: #0b0b0b; background: {TERRA};
        padding: 4px 22px 0 38px; transform: skewX(-12deg); }}
      .ed-nom b {{ display: block; font-family: "Anton", sans-serif; font-weight: 400; font-style: italic; line-height: 1; color: {CREME}; margin-top: 10px;
        -webkit-text-stroke: 12px #0b0b0b; paint-order: stroke fill; white-space: nowrap; transform: skewX(-8deg); }}
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
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="1080" data-height="1920">
      <div id="fond" class="clip" data-start="0" data-duration="{FIN}" data-track-index="0"></div>
      <div id="rgbw">
        <div id="grade">
          <div id="flou"><div id="zoom">
            <div id="cam">
{NL.join("              " + v for v in VIDS)}
            </div>
          </div></div>
          <div id="teinte"></div>
{NL.join("          " + h for h in OVER)}
        </div>
        <div id="noms">
{NL.join("          " + h for h in NOMS)}
        </div>
      </div>
      <div id="vignette"></div>
      <div style="position: absolute; inset: 0; overflow: hidden"><div id="grain"></div></div>
      <div id="bande-h" class="ed-bande"></div>
      <div id="bande-b" class="ed-bande"></div>
      <audio id="musique" src="assets/music/son-edit.wav" data-start="0" data-duration="{FIN}" data-volume="1" data-track-index="20"></audio>
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
print(f"edit anime : {len(VIDS)} plans, {len(NOMS)} noms, {len(SONS)} bruitages ; drop {DROP} s, {len(DROP_HITS)} frappes au drop, {len(SOUS)} petites frappes ; fin {FIN} s")
