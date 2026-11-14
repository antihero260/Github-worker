#!/usr/bin/env python3
"""Publicité de la JE-FPA (jefpa-site.pages.dev), format HORIZONTAL 1920×1080, sans personnage.

Demande : garder la voix de la vidéo fournie (assets/reference.mp4), faire une vidéo plus captivante, purement
publicitaire, qui se « balade » sur le site. Les passages du site sont filmés image par image par tools/capture.cjs
(assets/captures/*.mp4, 2880×1620, mise en page 1440×810) ; ici on les monte avec des mouvements de caméra,
des titres animés aux couleurs du site (Manrope, bleu #1f4bff, encre #05070d), les images du site, la musique
« Digital Clouds » (Mixkit) et des bruitages.

Écrit compositions/*.html et index.html. Ensuite : python3 tools/mixage.py /tmp/corelink (creux de la voix).
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent.parent
MOTS = json.loads((ICI / "assets/mots.json").read_text(encoding="utf-8"))
spec = __import__("importlib.util").util.spec_from_file_location("st", ICI / "tools/sous-titres.py")
st = __import__("importlib.util").util.module_from_spec(spec)
spec.loader.exec_module(st)
TEXTE = st.mots_du_script(ICI / "script.txt")
assert len(TEXTE) == len(MOTS)


def T(i):
    return MOTS[i]["start"]


def b(i):
    return round(T(i) - 0.12, 2)


W, H = 1920, 1080
BLEU, PROFOND, CLAIR, DOUX, ENCRE, ENCRE2, GRIS = "#1f4bff", "#1236d4", "#8ea6ff", "#eef2ff", "#05070d", "#0d1220", "#a3abbd"
K = 4 / 3  # px CSS de la capture (mise en page 1440×810) → px de l'image 1920×1080
FIN = 86.5
COUPES = [0, b(7), 15.64, b(43), 23.0, b(74), b(93), b(106), b(117), b(139), b(160), b(191), b(209), b(223), FIN]
NOMS = ["s01-ouverture", "s02-accueil", "s03-article", "s04-incertain", "s05-pas", "s06-conviction", "s07-cabinet",
        "s08-methode", "s09-poles", "s10-activites", "s11-bureaux", "s12-candidature", "s13-contact", "s14-fin"]
assert len(NOMS) == len(COUPES) - 1
# instant (temps de la vidéo) qui correspond à t = 0,5 s dans chaque capture (0,5 s d'avance filmée au début)
ANCRE = {"c01-accueil": 6.0, "c02-article": 15.6, "c03-conviction": 28.7, "c04-apropos": 35.3, "c05-poles": 44.6,
         "c06-actuariat": 47.0, "c07-data": 50.2, "c08-projets": 52.7, "c09-rdv": 54.0, "c10-journal": 55.5,
         "c11-bureaux": 58.5, "c12-collectif": 67.2, "c13-candidature": 70.3, "c14-clic": 75.7, "c15-contact": 77.4}
DUREE = {}
for c in ANCRE:
    f = ICI / "assets/captures" / f"{c}.mp4"
    if f.exists():
        DUREE[c] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                        capture_output=True, text=True).stdout.strip())

# ================================================================ SON
SFX = ICI / "assets/sfx"


def _pics():
    f = SFX / "pics.json"
    if f.exists():
        return json.loads(f.read_text())
    d = {}
    for m in sorted(SFX.glob("*.mp3")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(m), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, dtype=np.float32)
        w = 400
        n = len(x) // w
        e = (x[: n * w].reshape(n, w) ** 2).mean(1)
        d[m.stem] = {"pic": round(float(e.argmax()) * w / 8000, 3), "duree": round(len(x) / 8000, 3)}
    f.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    return d


PICS = _pics()
SONS = []
VOL_SFX = 0.75


def son(t, nom, v=0.4, note="", d=None, sur_pic=True):
    p = PICS[nom]
    debut = t - (p["pic"] if sur_pic else 0)
    SONS.append((round(max(0.0, debut), 2), nom, round(v * VOL_SFX, 3), note, round(min(d or p["duree"], p["duree"]), 2)))


TOURS = {}


def tour(liste):
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


WHOOSH = ["souffle-rapide", "swoosh-vol", "souffle-cine", "swoosh-accent", "fouet", "swoosh-court", "balaie-rapide"]
ZOOMS = ["zoom-air", "zoom-swipe", "zoom-futur", "zoom-in-out"]
POPS = ["pop-click", "pop-sec", "clic-positif", "bouton-tech"]
IMPACTS = ["impact-basse", "impact-futur", "impact-whoosh", "impact-tambour"]

# ================================================================ SCÈNE
class Scene:
    def __init__(self, k, titre):
        self.id, self.debut, self.fin, self.titre = NOMS[k], COUPES[k], COUPES[k + 1], titre
        self.premiere, self.derniere = k == 0, k == len(NOMS) - 1
        self.html, self.hors, self.js = [], [], []
        self.n_proxy = 0
        self.pistes = 4

    def L(self, g):
        return round(max(0.0, g - self.debut), 3)

    def j(self, ligne):
        self.js.append("    " + ligne)

    def add(self, h):
        self.html.append(h)

    def dessus(self, h):
        self.hors.append(h)

    def piste(self):
        self.pistes += 1
        return self.pistes

    def recadre(self, g, px, py, sc, d=0.6, ease="power2.inOut", flou=False):
        """Amène le point (px, py) au centre, grossi sc fois, sans jamais sortir de l'image."""
        if sc >= 1:
            px = min(max(px, 960 / sc), W - 960 / sc)
            py = min(max(py, 540 / sc), H - 540 / sc)
        x, y = round(-(px - 960) * sc), round(-(py - 540) * sc)
        self.j(f'tl.to("#{self.id}-cadre", {{ x: {x}, y: {y}, scale: {sc}, duration: {d}, ease: "{ease}" }}, {self.L(g)});')
        if flou:
            self.j(f'tl.to("#{self.id}-cadre", {{ keyframes: [{{ filter: "blur(8px)", duration: {round(d / 2, 3)} }}, {{ filter: "blur(0px)", duration: {round(d / 2, 3)} }}] }}, {self.L(g)});')

    def ecrire(self):
        duree = round(self.fin - self.debut, 3)
        if self.premiere:
            cam = [f'tl.fromTo("#{self.id}-cam", {{ scale: 1.0 }}, {{ scale: 1.03, duration: {round(duree - 0.25, 3)}, ease: "none" }}, 0);']
        else:
            cam = [f'tl.fromTo("#{self.id}-cam", {{ filter: "blur(16px)", scale: 1.1 }}, {{ filter: "blur(0px)", scale: 1, duration: 0.3, ease: "power3.out" }}, 0);',
                   f'tl.to("#{self.id}-cam", {{ scale: 1.03, duration: {round(duree - 0.6, 3)}, ease: "none" }}, 0.3);']
        if self.derniere:
            sortie = [f'tl.fromTo("#{self.id}-noir", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.9, ease: "power2.in" }}, {round(duree - 0.9, 3)});']
            self.hors.append(f'<div id="{self.id}-noir" style="position: absolute; inset: 0; background: #000; opacity: 0"></div>')
        else:
            sortie = [f'tl.to("#{self.id}-cam", {{ scale: 1.18, filter: "blur(16px)", duration: 0.24, ease: "power3.in" }}, {round(duree - 0.24, 3)});']
        dans = "\n        ".join(self.html)
        hors = "\n      ".join(self.hors)
        js = "\n".join("    " + c for c in cam) + "\n" + "\n".join(self.js) + "\n" + "\n".join("    " + c for c in sortie)
        page = f"""<!-- {self.titre} ({self.debut} → {self.fin} s). Écrit par tools/construire.py. -->
<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
  </style>
  <div id="root" data-composition-id="{self.id}" data-width="1920" data-height="1080">
    <div class="sc">
      <div id="{self.id}-cam" class="sc-cam">
        <div id="{self.id}-cadre" class="sc-cadre">
        {dans}
        </div>
      </div>
      {hors}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{self.id}"] = tl;
  </script>
</template>
"""
        (ICI / "compositions" / f"{self.id}.html").write_text(page, encoding="utf-8")


# ================================================================ ÉLÉMENTS
def video(s, vid, clip, g, d, piste=None):
    """Balise <video> d'une capture, calée pour que l'instant g de la vidéo montre le bon moment de la capture."""
    m = round(0.5 + (g - ANCRE[clip]), 3)
    assert m >= -0.01, (clip, g, m)
    d = min(d, DUREE.get(clip, 99) - max(0, m) - 0.02)
    return (f'<video id="{vid}" class="clip" src="assets/captures/{clip}.mp4" data-start="{s.L(g)}" data-duration="{round(d, 3)}" '
            f'data-media-start="{max(0, m)}" data-track-index="{piste or s.piste()}" muted playsinline></video>')


def capture(s, cid, clip, g, d, z=1):
    """Capture du site en plein cadre (on « est » sur le site)."""
    s.add(f'<div id="{cid}" class="capt" style="z-index: {z}">{video(s, cid + "-v", clip, g, d)}</div>')
    if g > s.debut + 0.05:
        s.j(f'tl.set("#{cid}", {{ opacity: 0 }}, 0);')
        s.j(f'tl.set("#{cid}", {{ opacity: 1 }}, {s.L(g)});')
    if g + d < s.fin - 0.05:
        s.j(f'tl.set("#{cid}", {{ opacity: 0 }}, {s.L(g + d)});')


def fenetre(s, fid, clip, g, d, x, y, w, url, z=2):
    """Fenêtre de navigateur (barre d'adresse) qui contient une capture."""
    h = round(w * 9 / 16)
    s.add(f'<div id="{fid}" class="fen" style="left: {x}px; top: {y}px; width: {w}px; z-index: {z}">'
          f'<div class="fen-barre"><i></i><i></i><i></i><span>{url}</span></div>'
          f'<div class="fen-ecran" style="height: {h}px">{video(s, fid + "-v", clip, g, d)}</div></div>')
    return h + 46


def lignes(s, tid, html_lignes, x, y, taille, g, pas=0.12, coul="#fff", poids=800, align="left", w=None, fin=None, interligne=1.04):
    """Titre dont chaque ligne monte depuis un masque (révélation éditoriale)."""
    lw = f"width: {w}px; text-align: {align};" if w else ""
    inner = "".join(f'<span class="m"><span id="{tid}-{k}" class="mi">{l}</span></span>' for k, l in enumerate(html_lignes))
    s.add(f'<div id="{tid}" class="titre" style="left: {x}px; top: {y}px; font-size: {taille}px; color: {coul}; font-weight: {poids}; line-height: {interligne}; {lw}">{inner}</div>')
    for k in range(len(html_lignes)):
        s.j(f'tl.fromTo("#{tid}-{k}", {{ yPercent: 115 }}, {{ yPercent: 0, duration: 0.55, ease: "expo.out", immediateRender: true }}, {s.L(g + k * pas)});')
    if fin is not None:
        for k in range(len(html_lignes)):
            s.j(f'tl.to("#{tid}-{k}", {{ yPercent: -115, duration: 0.35, ease: "power3.in" }}, {s.L(fin + k * 0.05)});')


def mots(s, tid, liste, x, y, taille, coul="#fff", accent=(), w=None, align="left", poids=800):
    """Mots qui apparaissent exactement quand la voix les dit : liste de (texte, temps)."""
    lw = f"width: {w}px; text-align: {align};" if w else ""
    spans = []
    for k, (m, t) in enumerate(liste):
        c = BLEU if k in accent else coul
        spans.append(f'<span class="m"><span id="{tid}-{k}" class="mi" style="color: {c}">{m}</span></span>')
        s.j(f'tl.fromTo("#{tid}-{k}", {{ yPercent: 115 }}, {{ yPercent: 0, duration: 0.45, ease: "expo.out", immediateRender: true }}, {s.L(t)});')
    s.add(f'<div id="{tid}" class="titre en-ligne" style="left: {x}px; top: {y}px; font-size: {taille}px; color: {coul}; font-weight: {poids}; {lw}">{" ".join(spans)}</div>')


def puce(s, pid, texte, x, y, g, fin=None, fond=BLEU, coul="#fff", taille=30):
    s.dessus(f'<div id="{pid}" class="puce" style="left: {x}px; top: {y}px; background: {fond}; color: {coul}; font-size: {taille}px; opacity: 0">{texte}</div>')
    s.j(f'tl.fromTo("#{pid}", {{ opacity: 0, y: 24, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2)", immediateRender: false }}, {s.L(g)});')
    son(g, tour(POPS), 0.35, f"puce {texte}")
    if fin is not None:
        s.j(f'tl.to("#{pid}", {{ opacity: 0, y: -16, duration: 0.25 }}, {s.L(fin)});')


def image(s, iid, f, g, d, de=1.14, a=1.0, x0=0, x1=0, voile=0.45):
    """Image du site en plein cadre, mouvement lent (Ken Burns) et voile sombre."""
    s.add(f'<div id="{iid}" class="img-plein"><img src="assets/img/{f}" alt="" /><i style="opacity: {voile}"></i></div>')
    s.j(f'tl.fromTo("#{iid} img", {{ scale: {de}, xPercent: {x0} }}, {{ scale: {a}, xPercent: {x1}, duration: {d}, ease: "none", immediateRender: true }}, {s.L(g)});')


def zoom(s, g, px, py, sc, d=0.7, v=0.4, ease="power3.inOut"):
    s.recadre(g, px, py, sc, d, ease)
    son(g + d * 0.4, tour(ZOOMS if sc > 1.02 else WHOOSH), v, "mouvement de caméra")


def balayage(s, g, coul="rgba(142, 166, 255, 0.55)"):
    """Reflet lumineux qui traverse l'image."""
    bid = f"{s.id}-bal-{len(s.hors)}"
    s.dessus(f'<div id="{bid}" class="balayage" style="background: linear-gradient(100deg, transparent 0%, {coul} 50%, transparent 100%)"></div>')
    s.j(f'tl.fromTo("#{bid}", {{ xPercent: -120 }}, {{ xPercent: 220, duration: 0.9, ease: "power2.inOut", immediateRender: true }}, {s.L(g)});')


def flash(s, g, coul="#fff", force=0.85):
    fid = f"{s.id}-fl-{len(s.hors)}"
    s.dessus(f'<div id="{fid}" style="position: absolute; inset: 0; background: {coul}; opacity: 0; pointer-events: none"></div>')
    s.j(f'tl.fromTo("#{fid}", {{ opacity: {force} }}, {{ opacity: 0, duration: 0.25, immediateRender: false }}, {s.L(g)});')


def cadre_focus(s, fid, x, y, w, h, g, fin):
    """Rectangle bleu qui entoure un détail du site au moment où on en parle."""
    s.add(f'<div id="{fid}" class="focus" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0"></div>')
    s.j(f'tl.fromTo("#{fid}", {{ opacity: 0, scale: 1.15 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {s.L(g)});')
    s.j(f'tl.to("#{fid}", {{ opacity: 0, duration: 0.2 }}, {s.L(fin)});')
    son(g, "autofocus" if "autofocus" in PICS else tour(POPS), 0.3, "focus")


def compteur(s, sel, g, de, a, d):
    s.n_proxy += 1
    p = f"p{s.n_proxy}"
    s.j(f'const {p} = {{ v: {de} }};')
    s.j(f'tl.fromTo({p}, {{ v: {de} }}, {{ v: {a}, duration: {d}, ease: "power2.out", immediateRender: false, '
        f'onUpdate: () => {{ document.querySelector("{sel}").textContent = String(Math.round({p}.v)); }} }}, {s.L(g)});')


def c(x, y):
    """Coordonnées CSS de la capture → image."""
    return round(x * K), round(y * K)


CACHER_ST = []  # intervalles où les sous-titres sont masqués (le texte est déjà à l'écran en grand)

# ================================================================ S01 OUVERTURE : l'université, l'UFR
s = Scene(0, "Ouverture : Université Félix Houphouët-Boigny, UFR Mathématiques et Informatique")
image(s, "o-ufr", "ufr-mathematiques-1360.webp", 0, s.fin, de=1.22, a=1.02, voile=0.5)
for k, (f, t) in enumerate([("convergence-1536.webp", 0), ("onde-donnees-1536.webp", 0.12), ("risque-partage-1536.webp", 0.24)]):
    s.add(f'<div id="o-r{k}" class="img-plein" style="z-index: 3"><img src="assets/img/{f}" alt="" /></div>')
    s.j(f'tl.set("#o-r{k}", {{ opacity: 1 }}, {t});')
    s.j(f'tl.fromTo("#o-r{k} img", {{ scale: 1.25 }}, {{ scale: 1.1, duration: 0.14, ease: "none", immediateRender: true }}, {t});')
    s.j(f'tl.set("#o-r{k}", {{ opacity: 0 }}, {t + 0.12});')
son(0.0, "impact-basse", 0.6, "ouverture")
son(0.12, "glitch-mini", 0.35, "rafale d'images")
s.add('<div class="degrade-g"></div>')
flash(s, 0.36, "#fff", 0.7)
puce(s, "o-lieu", "Abidjan · Côte d’Ivoire", 120, 300, 0.42, fin=T(3) - 0.25, fond="rgba(255,255,255,0.12)")
mots(s, "o-u", [("Université", T(0)), ("Félix", T(1)), ("Houphouët-Boigny", T(2))], 120, 370, 96, w=1650)
s.j(f'tl.to("#o-u", {{ y: -150, opacity: 0.35, scale: 0.62, transformOrigin: "0% 0%", duration: 0.6, ease: "power3.inOut" }}, {s.L(T(3) - 0.2)});')
mots(s, "o-ufr-t", [("UFR", T(3)), ("Mathématiques", T(4)), ("et", T(5)), ("Informatique", T(6))], 120, 560, 92, accent=(1, 3), w=1500)
s.add(f'<div id="o-trait" class="trait" style="left: 124px; top: 790px; width: 420px"></div>')
s.j(f'tl.fromTo("#o-trait", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.8, ease: "expo.out", immediateRender: true }}, {s.L(T(3))});')
balayage(s, 2.8)
son(T(3), "swoosh-monte", 0.35, "UFR")
s.recadre(0.4, 900, 520, 1.04, 5.4, "none")
CACHER_ST.append((0, s.fin))
s.ecrire()

# ================================================================ S02 ACCUEIL : la filière, la JE-FPA (on arrive sur le site)
s = Scene(1, "Accueil du site : une filière à part, la FPA ; au cœur, la Junior Entreprise JE-FPA")
s.add('<div class="fond-sombre"></div>')
fenetre(s, "a-fen", "c01-accueil", s.debut, s.fin - s.debut, 0, 0, 1920, "jefpa-site.pages.dev")
s.j(f'tl.fromTo("#a-fen", {{ scale: 0.62, rotationY: -18, rotationX: 8, y: 60 }}, {{ scale: 1.045, rotationY: 0, rotationX: 0, y: -23, duration: 1.1, ease: "expo.inOut", immediateRender: true }}, 0);')
son(s.debut + 0.1, "swoosh-monte", 0.45, "le site arrive")
puce(s, "a-url", "jefpa-site.pages.dev", 760, 70, s.debut + 0.2, fin=s.debut + 1.0, fond=ENCRE)
# la filière (texte en bas à gauche du site)
zoom(s, T(15) - 0.25, 520, 620, 1.22, 1.0)
puce(s, "a-p1", "Filière Professionnalisée Actuariat", 120, 800, T(16), fin=T(19) - 0.1, fond=ENCRE, taille=44)
zoom(s, T(19), 960, 540, 1.0, 0.7)
# le titre, puis le logo
zoom(s, T(25) - 0.3, 420, 470, 1.35, 1.6, ease="power2.inOut")
lx, ly = c(160, 51)
zoom(s, T(31) - 0.2, lx, ly, 3.0, 0.7)
balayage(s, T(32))
son(T(32), "scintille", 0.4, "logo JE-FPA")
puce(s, "a-p2", "Junior Entreprise", 60, 210, T(29), fin=s.fin - 0.25)
s.ecrire()

# ================================================================ S03 ARTICLE : mettre des chiffres sur l'incertain
s = Scene(2, "Article animé : l'imprévu arrive, comment s'y préparer ? — en actuariat, des chiffres sur l'incertain")
capture(s, "r-c", "c02-article", s.debut, s.fin - s.debut)
zoom(s, s.debut + 0.1, 520, 520, 1.35, 1.2, ease="power2.out")
zoom(s, T(38) - 0.2, 380, 640, 1.8, 0.7)
puce(s, "r-p", "Lecture animée · Le journal", 120, 890, T(35), fin=s.fin - 0.25)
s.ecrire()

# ================================================================ S04 L'INCERTAIN : un sinistre, une retraite, un avenir
s = Scene(3, "Un sinistre, une retraite, un avenir qu'on ne connaît pas encore")
image(s, "i-img", "risque-partage-1536.webp", s.debut, s.fin - s.debut, de=1.05, a=1.22, voile=0.55)
s.add('<div class="degrade-g"></div>')
lignes(s, "i-1", ["Un sinistre."], 140, 250, 120, T(43), fin=None)
lignes(s, "i-2", ["Une retraite."], 140, 400, 120, T(45))
lignes(s, "i-3", ["Un <span style='color: #8ea6ff'>avenir</span>"], 140, 550, 120, T(47))
mots(s, "i-4", [("qu’on", T(49)), ("ne", T(50)), ("connaît", T(51)), ("pas", T(52)), ("encore.", T(53))], 146, 720, 56, coul="#d6dcff", poids=600)
for t, n in ((T(43), "un sinistre"), (T(45), "une retraite"), (T(47), "un avenir")):
    son(t, tour(IMPACTS), 0.38, n)
s.j(f'tl.to(["#i-1", "#i-2"], {{ opacity: 0.35, duration: 0.3 }}, {s.L(T(47))});')
CACHER_ST.append((s.debut, s.fin))
s.ecrire()

# ================================================================ S05 LE PAS : exercice en classe / vraie question d'entreprise
s = Scene(4, "Entre un exercice corrigé en classe et une vraie question posée par une entreprise, il y a un pas")
s.add('<div id="p-g" class="moitie" style="left: 0; background: #ffffff"></div><div id="p-d" class="moitie" style="left: 960px; background: #1f4bff"></div>')
s.j(f'tl.fromTo("#p-g", {{ yPercent: -100 }}, {{ yPercent: 0, duration: 0.6, ease: "expo.out", immediateRender: true }}, 0);')
s.j(f'tl.fromTo("#p-d", {{ yPercent: 100 }}, {{ yPercent: 0, duration: 0.6, ease: "expo.out", immediateRender: true }}, {s.L(T(61) - 0.3)});')
s.add(f'<div class="etiq-sc" style="left: 120px; top: 250px; color: {BLEU}">Entre</div>')
lignes(s, "p-1", ["un exercice", "corrigé en classe"], 120, 310, 86, T(56), coul=ENCRE)
s.add(f'<div id="p-et" class="etiq-sc" style="left: 1080px; top: 250px; color: #dfe5ff; opacity: 0">et</div>')
s.j(f'tl.to("#p-et", {{ opacity: 1, duration: 0.2 }}, {s.L(T(61))});')
lignes(s, "p-2", ["une vraie question", "posée par", "une entreprise"], 1080, 310, 86, T(62), coul="#fff")
s.j(f'tl.to("#p-g", {{ x: -480, duration: 0.7, ease: "expo.inOut" }}, {s.L(T(69) - 0.25)});')
s.j(f'tl.to("#p-d", {{ x: 480, duration: 0.7, ease: "expo.inOut" }}, {s.L(T(69) - 0.25)});')
s.j(f'tl.to("#p-1", {{ x: -480, duration: 0.7, ease: "expo.inOut" }}, {s.L(T(69) - 0.25)});')
s.j(f'tl.to(["#p-2", "#p-et"], {{ x: 480, duration: 0.7, ease: "expo.inOut" }}, {s.L(T(69) - 0.25)});')
s.add(f'<div id="p-pas" class="pas" style="opacity: 0"><span>il y a</span><b>un pas.</b></div>')
s.j(f'tl.fromTo("#p-pas", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.8)", immediateRender: false }}, {s.L(T(69))});')
son(T(56), "papier-glisse", 0.35, "exercice")
son(T(62), "swoosh-monte", 0.4, "vraie question")
son(T(69) - 0.2, "swoosh-tourbillon", 0.4, "les deux mondes s'écartent")
son(T(72), "impact-basse", 0.5, "un pas")
CACHER_ST.append((s.debut, s.fin))
s.ecrire()

# ================================================================ S06 CONVICTION : née en 2023
s = Scene(5, "La JE-FPA est née en 2023 pour aider les étudiants à franchir ce pas avant même leur diplôme")
capture(s, "v-c", "c03-conviction", s.debut, s.fin - s.debut)
s.dessus('<div id="v-an" class="annee" style="opacity: 0"><b id="v-an-n">2020</b><span>Naissance de la JE-FPA</span></div>')
s.j(f'tl.fromTo("#v-an", {{ opacity: 0, x: 80 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out", immediateRender: false }}, {s.L(T(79) - 0.3)});')
compteur(s, "#v-an-n", T(79) - 0.3, 2019, 2023, 0.7)
s.j(f'tl.to("#v-an", {{ opacity: 0, x: 80, duration: 0.3 }}, {s.L(T(83))});')
son(T(79), "compteur", 0.3, "2023", d=0.7)
son(T(79) + 0.4, "impact-futur", 0.42, "2023")
zoom(s, T(80), 700, 500, 1.25, 1.8, ease="power2.inOut")
zoom(s, T(88) - 0.2, 960, 540, 1.0, 0.7)
s.ecrire()

# ================================================================ S07 CABINET : un collectif d'étudiants qui travaillent comme un vrai cabinet
s = Scene(6, "Une Junior Entreprise, c'est un collectif d'étudiants qui travaillent comme un vrai cabinet")
capture(s, "b-c", "c04-apropos", s.debut, s.fin - s.debut)
zoom(s, s.debut + 0.05, 500, 460, 1.3, 1.4, ease="power2.out")
zoom(s, T(98) - 0.4, 820, 560, 1.18, 0.9)
puce(s, "b-p1", "Un collectif d’étudiants", 120, 870, T(98), fin=T(103) - 0.1)
puce(s, "b-p2", "comme un vrai cabinet", 120, 870, T(103), fin=s.fin - 0.25, fond=ENCRE)
s.ecrire()

# ================================================================ S08 MÉTHODE : comprendre, cadrer, analyser, expliquer
s = Scene(7, "Comprendre la question, cadrer le travail, analyser, puis expliquer les résultats")
image(s, "m-img", "onde-donnees-1536.webp", s.debut, s.fin - s.debut, de=1.18, a=1.04, x0=4, x1=-4, voile=0.62)
s.add(f'<div class="etiq-sc" style="left: 140px; top: 210px; color: {CLAIR}">Notre méthode</div>')
s.add('<div id="m-ligne" class="m-ligne"></div>')
ETAPES = [("01", "Comprendre", "la question", T(106)), ("02", "Cadrer", "le travail", T(109)), ("03", "Analyser", "les données", T(112)), ("04", "Expliquer", "les résultats", T(114))]
for k, (n, a, sous, t) in enumerate(ETAPES):
    x = 140 + k * 430
    s.add(f'<div id="m-e{k}" class="etape" style="left: {x}px; top: 470px; opacity: 0.18"><i></i><em>{n}</em><b>{a}</b><span>{sous}</span></div>')
    s.j(f'tl.to("#m-e{k}", {{ opacity: 1, duration: 0.25 }}, {s.L(t)});')
    s.j(f'tl.fromTo("#m-e{k} b", {{ yPercent: 60, opacity: 0 }}, {{ yPercent: 0, opacity: 1, duration: 0.45, ease: "expo.out", immediateRender: false }}, {s.L(t)});')
    s.j(f'tl.fromTo("#m-e{k} i", {{ scale: 0.4 }}, {{ scale: 1, duration: 0.4, ease: "back.out(3)", immediateRender: false }}, {s.L(t)});')
    son(t, tour(["clic-positif", "bouton-tech", "notif-indice", "coche"]), 0.4, a)
s.j(f'tl.fromTo("#m-ligne", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {round(T(114) - T(106) + 0.4, 2)}, ease: "none", immediateRender: true }}, {s.L(T(106))});')
s.recadre(s.debut, 1100, 560, 1.06, s.fin - s.debut, "none")
CACHER_ST.append((s.debut, s.fin))
s.ecrire()

# ================================================================ S09 PÔLES : deux pôles, actuariat, data science
s = Scene(8, "Deux pôles : l'actuariat pour mesurer le risque, la data science pour faire parler les données")
capture(s, "q-c1", "c05-poles", s.debut, T(123) - 0.15 - s.debut)
capture(s, "q-c2", "c06-actuariat", T(123) - 0.15, T(131) - T(123), z=2)
capture(s, "q-c3", "c07-data", T(131) - 0.15, s.fin - T(131) + 0.15, z=3)
s.add('<div id="q-volet" class="volet"></div>')
s.j('tl.set("#q-volet", { xPercent: -101 }, 0);')
for t in (T(123) - 0.15, T(131) - 0.15):
    s.j(f'tl.set("#q-volet", {{ xPercent: -101 }}, {s.L(t - 0.19)});')
    s.j(f'tl.to("#q-volet", {{ keyframes: [{{ xPercent: 0, duration: 0.18, ease: "power3.in" }}, {{ xPercent: 101, duration: 0.22, ease: "power3.out" }}] }}, {s.L(t - 0.18)});')
    son(t, tour(WHOOSH), 0.45, "volet bleu")
s.dessus('<div id="q-2" class="gros-chiffre" style="opacity: 0"><b>2</b><span>pôles</span></div>')
s.j(f'tl.fromTo("#q-2", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "expo.out", immediateRender: false }}, {s.L(T(121))});')
s.j(f'tl.to("#q-2", {{ opacity: 0, duration: 0.2 }}, {s.L(T(123) - 0.3)});')
son(T(121), "impact-futur", 0.45, "deux pôles")
zoom(s, s.debut + 0.05, 500, 400, 1.2, 1.6, ease="power2.out")
zoom(s, T(123) - 0.15, 960, 540, 1.0, 0.01)
zoom(s, T(124), 520, 330, 1.45, 2.4, ease="power2.inOut")
zoom(s, T(131) - 0.15, 960, 540, 1.0, 0.01)
zoom(s, T(134), 520, 330, 1.45, 1.8, ease="power2.inOut")
puce(s, "q-pa", "Pôle Actuariat", 120, 870, T(123), fin=T(131) - 0.3)
puce(s, "q-pd", "Pôle Data Science", 120, 870, T(131), fin=s.fin - 0.25)
s.ecrire()

# ================================================================ S10 ACTIVITÉS : projets, ateliers, journal (trois fenêtres)
s = Scene(9, "On y mène des projets, on y anime des ateliers, et on écrit dans un journal")
s.add('<div class="fond-sombre"><i class="halo"></i></div>')
FEN = [("w-1", "c08-projets", T(141) - 0.2, 150, 170, "jefpa-site.pages.dev/pages/projets", "Projets"),
       ("w-2", "c09-rdv", T(146) - 0.2, 470, 250, "jefpa-site.pages.dev/pages/evenements", "Ateliers"),
       ("w-3", "c10-journal", T(151) - 0.2, 790, 330, "jefpa-site.pages.dev/pages/articles", "Journal")]
for k, (fid, clip, g, x, y, url, lab) in enumerate(FEN):
    g0 = max(g, s.debut)
    fenetre(s, fid, clip, g0, s.fin - g0, x, y, 980, url, z=2 + k)
    s.j(f'tl.fromTo("#{fid}", {{ opacity: 0, x: 500, rotationY: -25, scale: 0.85 }}, {{ opacity: 1, x: 0, rotationY: -8, scale: 1, duration: 0.6, ease: "expo.out", immediateRender: true }}, {s.L(g0)});')
    son(g0, tour(WHOOSH), 0.42, f"fenêtre {lab}")
    puce(s, f"w-p{k}", lab, x + 20, y - 70, g0 + 0.15, fond=BLEU if k != 1 else ENCRE)
    if k < 2:
        s.j(f'tl.to("#{fid}", {{ x: -60, opacity: 0.55, filter: "blur(2px)", duration: 0.5 }}, {s.L(FEN[k + 1][2])});')
# la dernière fenêtre s'agrandit : on entre dans le journal
capture(s, "w-plein", "c10-journal", T(155), s.fin - T(155), z=9)
s.j(f'tl.fromTo("#w-plein", {{ x: 790, y: 376, scale: {round(980 / 1920, 4)}, rotationY: -8, transformOrigin: "0% 0%" }}, {{ x: 0, y: 0, scale: 1, rotationY: 0, duration: 0.8, ease: "expo.inOut", immediateRender: false }}, {s.L(T(155))});')
s.j(f'tl.set("#w-3", {{ opacity: 0 }}, {s.L(T(155) + 0.02)});')
s.j(f'tl.to(["#w-p0", "#w-p1", "#w-p2"], {{ opacity: 0, duration: 0.2 }}, {s.L(T(155))});')
son(T(155) + 0.3, "zoom-expand" if "zoom-expand" in PICS else "zoom-air", 0.4, "on entre dans le journal")
s.ecrire()

# ================================================================ S11 BUREAUX : trois bureaux, trois présidents, chaque génération
s = Scene(10, "Depuis 2023, trois bureaux : Anicet Apeli, Miezan Océane, Kouassi Enoch ; chaque génération construit")
capture(s, "u-c1", "c11-bureaux", s.debut, T(182) - 0.15 - s.debut)
capture(s, "u-c2", "c12-collectif", T(182) - 0.15, s.fin - T(182) + 0.15, z=2)
s.dessus('<div id="u-3" class="gros-chiffre droite" style="opacity: 0"><b>3</b><span>bureaux</span></div>')
s.j(f'tl.fromTo("#u-3", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "expo.out", immediateRender: false }}, {s.L(T(162))});')
s.j(f'tl.to("#u-3", {{ opacity: 0, duration: 0.25 }}, {s.L(T(169) - 0.2)});')
son(T(162), "impact-futur", 0.42, "trois bureaux")
zoom(s, s.debut + 0.1, 600, 420, 1.15, 1.6, ease="power2.out")
# les trois noms (frise : CSS x ≈ 60, 507, 952 ; y ≈ 405)
for k, (x, i) in enumerate(((60, 170), (507, 174), (952, 180))):
    px, py = c(x + 110, 400)
    zoom(s, T(i) - 0.25, px, py, 2.0, 0.55)
    cadre_focus(s, f"u-f{k}", x * K - 16, 352 * K, 300, 120, T(i), T(i) + 1.0 if k < 2 else T(182) - 0.4)
    son(T(i), tour(["notif-positive", "clic-positif", "notif-magique"]), 0.38, "un président")
zoom(s, T(182) - 0.4, 960, 540, 1.0, 0.25)
s.j(f'tl.set("#{s.id}-cadre", {{ x: 0, y: 0, scale: 1 }}, {s.L(T(182) - 0.14)});')
zoom(s, T(183), 900, 620, 1.12, 2.5, ease="power1.inOut")
puce(s, "u-p", "Chaque génération construit sur la précédente", 120, 870, T(183), fin=s.fin - 0.25, fond=ENCRE)
s.ecrire()

# ================================================================ S12 CANDIDATURE : Licence 3, Master 1, Master 2 ; ta place est à construire
s = Scene(11, "Tu es en Licence 3, Master 1 ou Master 2 Actuariat ? Ta place est à construire")
capture(s, "k-c", "c13-candidature", s.debut, s.fin - s.debut)
zoom(s, s.debut + 0.05, 520, 420, 1.25, 0.3, ease="power2.out")
for k, (x, i) in enumerate(((280, 194), (744, 197), (1200, 201))):
    zoom(s, T(i) - 0.2, x, 700, 1.7, 0.5)
zoom(s, T(204) - 0.3, 960, 540, 1.0, 0.5)
s.dessus('<div id="k-bande" class="bande"><span>Ta place est</span><b>à construire.</b></div>')
s.j(f'tl.fromTo("#k-bande", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.55, ease: "expo.inOut", immediateRender: true }}, {s.L(T(204) - 0.1)});')
son(T(204), "impact-whoosh", 0.45, "ta place")
CACHER_ST.append((T(204) - 0.1, s.fin))
s.ecrire()

# ================================================================ S13 CONTACT : vous êtes une organisation ? parlons-en
s = Scene(12, "Vous êtes une organisation, avec une question sur vos chiffres ou vos données ? Parlons-en")
capture(s, "t-c1", "c14-clic", s.debut, 77.4 - 0.12 - s.debut)
capture(s, "t-c2", "c15-contact", 77.4 - 0.12, s.fin - 77.28, z=2)
lx, ly = c(1252, 48)
zoom(s, s.debut + 0.3, lx - 120, ly + 60, 1.9, 0.9)
son(75.7 + 1.0 + 0.1, "clic-souris", 0.5, "clic Parlons de votre projet")
flash(s, 77.28, BLEU, 0.9)
son(77.28, tour(WHOOSH), 0.45, "page contact")
s.j(f'tl.set("#{s.id}-cadre", {{ x: 0, y: 0, scale: 1 }}, {s.L(77.28)});')
zoom(s, 77.4 + 1.0, *c(1040, 380), 1.6, 0.8)
son(77.4 + 1.4, "clavier-ordi", 0.38, "on tape", d=2.2, sur_pic=False)
s.dessus('<div id="t-parlons" class="parlons" style="opacity: 0">Parlons-en.</div>')
s.j(f'tl.fromTo("#t-parlons", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out", immediateRender: false }}, {s.L(T(222))});')
son(T(222), "impact-basse", 0.5, "parlons-en")
CACHER_ST.append((T(222), s.fin))
s.ecrire()

# ================================================================ S14 FIN : JE-FPA, l'ambition se construit ensemble
s = Scene(13, "JE-FPA. L'ambition se construit ensemble.")
image(s, "f-img", "convergence-1536.webp", s.debut, s.fin - s.debut, de=1.25, a=1.05, voile=0.5)
s.add('<div id="f-logo" class="logo-fin"><img src="assets/img/logo-recadre.png" alt="JE-FPA" /></div>')
s.j(f'tl.fromTo("#f-logo", {{ opacity: 0, scale: 0.6, y: 40 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.7, ease: "back.out(1.6)", immediateRender: true }}, {s.L(T(223))});')
son(T(223), "trophee-magique" if "trophee-magique" in PICS else "magie", 0.45, "logo")
lignes(s, "f-t", ["L’ambition", "se construit", "<span style='color: #8ea6ff'>ensemble.</span>"], 900, 290, 110, T(224), pas=0.45)
s.add('<div id="f-url" class="url-fin" style="opacity: 0">jefpa-site.pages.dev</div>')
s.j(f'tl.fromTo("#f-url", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "expo.out", immediateRender: false }}, {s.L(T(227) + 0.5)});')
s.add('<div id="f-li" class="li-fin" style="opacity: 0">Junior Entreprise FPA · UFHB · Abidjan</div>')
s.j(f'tl.fromTo("#f-li", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, immediateRender: false }}, {s.L(T(227) + 0.8)});')
balayage(s, T(224))
son(T(227) + 0.5, "cloche-succes", 0.4, "fin")
CACHER_ST.append((s.debut, s.fin))
s.ecrire()

# ================================================================ SOUS-TITRES (discrets, bas de l'image)
def cache(t):
    return any(a - 0.01 <= t < z for a, z in CACHER_ST)


def ecrire_sous_titres():
    groupes, cur = [], []
    for i in range(len(MOTS)):
        cur.append(i)
        m = TEXTE[i]
        if m[-1] in ".,;:!?…" and len(" ".join(TEXTE[j] for j in cur)) > 14 or len(cur) >= 7 or len(" ".join(TEXTE[j] for j in cur)) >= 40:
            groupes.append(cur)
            cur = []
    if cur:
        groupes.append(cur)
    html, js = [], []
    for n, g in enumerate(groupes):
        t0 = MOTS[g[0]]["start"]
        t1 = MOTS[groupes[n + 1][0]]["start"] if n + 1 < len(groupes) else MOTS[g[-1]]["end"] + 0.6
        if cache(t0):
            continue
        for a, z in CACHER_ST:
            if t0 < a < t1:
                t1 = a
        spans = []
        for i in g:
            spans.append(f'<span id="st-{i}" style="opacity: 0.35">{TEXTE[i]}</span>')
            js.append(f'    tl.set("#st-{i}", {{ opacity: 1 }}, {MOTS[i]["start"]});')
        html.append(f'    <div id="st-g{n}" class="st" data-layout-ignore style="opacity: 0"><div>{" ".join(spans)}</div></div>')
        js.append(f'    tl.fromTo("#st-g{n}", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.15, immediateRender: false }}, {t0});')
        js.append(f'    tl.set("#st-g{n}", {{ opacity: 0 }}, {round(t1 - 0.02, 3)});')
    page = f"""<!-- Sous-titres discrets (écrit par tools/construire.py). -->
<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .st {{ position: absolute; left: 160px; width: 1600px; top: 968px; text-align: center; }}
    .st div {{ display: inline-block; font-family: "Manrope", sans-serif; font-weight: 700; font-size: 38px; line-height: 1.25; color: #fff;
      background: rgba(5, 7, 13, 0.62); padding: 10px 26px; border-radius: 14px; }}
  </style>
  <div id="root" data-composition-id="sous-titres" data-width="1920" data-height="1080">
{chr(10).join(html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["sous-titres"] = tl;
  </script>
</template>
"""
    (ICI / "compositions/sous-titres.html").write_text(page, encoding="utf-8")
    return len(html)


# ================================================================ SONS GÉNÉRAUX, MUSIQUE, INDEX
for k, cc in enumerate(COUPES[1:-1], start=1):
    son(cc, tour(WHOOSH), 0.42, f"transition vers {NOMS[k]}")
son(COUPES[-2] - 1.6, "riser-synth", 0.3, "montée vers la fin", d=1.6, sur_pic=False)
_vus = set()
SONS[:] = [x for x in SONS if not ((x[0], x[1]) in _vus or _vus.add((x[0], x[1])))]
# Demande de l'utilisateur : garder la piste d'origine de sa vidéo (voix + ancienne musique), sans musique ajoutée.
MUSIQUE = None  # avant : ("digital-clouds", 0.4)

CSS = (ICI / "tools/styles.css").read_text(encoding="utf-8")


def ecrire_index():
    l = [f'      <div id="fond" class="clip" data-start="0" data-duration="{FIN}" data-track-index="0"></div>']
    for k, n in enumerate(NOMS):
        d0, d1 = COUPES[k], COUPES[k + 1]
        l.append(f'      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{d0}" '
                 f'data-duration="{round(d1 - d0, 2)}" data-track-index="1" data-width="1920" data-height="1080" style="z-index: 10"></div>')
    l.append(f'      <div id="sous-titres" data-composition-id="sous-titres" data-composition-src="compositions/sous-titres.html" data-start="0" '
             f'data-duration="{FIN}" data-track-index="3" data-width="1920" data-height="1080" style="z-index: 50"></div>')
    l.append(f'      <audio id="voix" src="assets/audio/piste-originale.mp3" data-start="0" data-duration="{FIN}" data-fade-out="1.5" data-track-index="10"></audio>')
    if MUSIQUE:
        l.append(f'      <audio id="musique-1" src="assets/music/{MUSIQUE[0]}.mp3" data-start="0" data-duration="{FIN}" data-volume="{MUSIQUE[1]}" data-fade-out="2.5" data-track-index="11"></audio>')
    pistes = {}
    for n, (d0, f, v, note, dd) in enumerate(sorted(SONS), start=1):
        p = 30
        while pistes.get(p, -1) > d0 - 0.01:
            p += 1
        dd = round(min(dd, FIN - d0), 2)
        pistes[p] = d0 + dd
        l.append(f'      <audio id="sfx-{n:03d}" src="assets/sfx/{f}.mp3" data-start="{d0}" data-duration="{dd}" data-volume="{v}" data-track-index="{p}"></audio><!-- {note} -->')
    corps = "\n".join(l)
    page = f"""<!doctype html>
<html lang="fr" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="1920" data-height="1080">
{corps}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (ICI / "index.html").write_text(page, encoding="utf-8")


n_st = ecrire_sous_titres()
ecrire_index()
print(f"{len(NOMS)} scènes, {len(SONS)} bruitages, {n_st} sous-titres, durée {FIN} s")
print("coupes :", COUPES)
