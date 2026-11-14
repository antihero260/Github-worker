#!/usr/bin/env python3
"""Lefinancier, vidéo 6 : « Ton salaire disparaît avant le 15 ? » (les petites dépenses oubliées, Lucas) — vertical natif 1080×1920.
Demandes pour cette vidéo : beaucoup plus de vraies vidéos de démonstration, musiques populaires, bons bruitages ;
règles de clarté : sujet écrit dans les 3 premières secondes, 3 chiffres au maximum à l'écran (15, 150 000, 2 300), règle à retenir à la fin.
Base reprise de la vidéo 4 (tontine-epargne) :

Demandes de l'utilisateur pour cette vidéo :
- plus de format horizontal : tout est composé directement en 1080×1920 (plus de film 16:9 dans un bandeau) ;
- des personnages verticaux et bleus (Tom bleu ciel, Emma bleu clair avec chignon, Hugo bleu profond avec casquette) ;
- plus de vidéos en arrière-plan des personnages : les vraies vidéos sont DANS la scène (télé, téléphone, bulle de
  pensée, panneau), et la caméra zoome dessus pour les montrer ;
- des éléments dessinés dans la scène et des bulles de dialogue.

Écrit : compositions/s*.html, compositions/sous-titres.html et index.html (en entier).
Il faut ensuite relancer tools/mixage.py (creux de la voix dans les musiques, sans baisse automatique).
Gestes des personnages : hyperframes-style/outils/projecteur.py (mêmes membres et mêmes pivots).
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI.parent.parent / "hyperframes-style" / "outils"))
import projecteur as P  # noqa: E402
from projecteur import (PARTIES, PIVOTS, Scene, acquiesce, cam, court, gratte, haussement, init, marche,  # noqa: E402,F401
                        non, oui, panique, parle, pose, pouce, repos, saut, t_mot, tremble, victoire, vit)

init(ICI)
T = t_mot
W, H = 1080, 1920
NUIT, CIEL, CLAIR, PROFOND, ARDOISE, OR, BLANC, GRIS, CORAIL = ("#0B1220", "#38BDF8", "#7DD3FC", "#0284C7", "#13203A",
                                                               "#F2B705", "#F1F5F9", "#94A3B8", "#FF6B6B")
TITRE = "Ton salaire disparaît avant le 15 ?"
VOL_SFX = 0.9
SOL = 1290  # ligne du sol (pieds des personnages)


def b(i):
    return round(T(i) - 0.12, 2)


FIN = 52.4
COUPES = [0] + [b(i) for i in (10, 23, 31, 50, 68, 83, 94, 113, 140)] + [FIN]
NOMS = ["s01-hook", "s02-salaire", "s03-lendemain", "s04-depenses", "s05-application", "s06-sortie", "s07-fige", "s08-oubliees", "s09-regle", "s10-abonne"]


class SV(Scene):
    """Scène verticale 1080×1920 : la caméra recadre autour du centre (540, 960)."""

    bornes = (0, 1080)

    def recadre(self, g, px, py, sc, d=0.24, flou=True):
        if sc >= 1:
            a, b_ = self.bornes
            px = min(max(px, a + 540 / sc), b_ - 540 / sc)
        x, y = round(-(px - 540) * sc), round(-(py - 960) * sc)
        self.j(f'tl.to("#{self.id}-cadre", {{ x: {x}, y: {y}, scale: {sc}, duration: {d}, ease: "power3.inOut" }}, {self.L(g)});')
        if flou:
            self.j(f'tl.to("#{self.id}-cadre", {{ keyframes: [{{ filter: "blur(9px)", duration: {round(d / 2, 3)} }}, {{ filter: "blur(0px)", duration: {round(d / 2, 3)} }}] }}, {self.L(g)});')

    def place(self, px, py, sc):
        """Position de caméra dès le début de la scène (sans mouvement)."""
        x, y = round(-(px - 540) * sc), round(-(py - 960) * sc)
        self.j(f'tl.set("#{self.id}-cadre", {{ x: {x}, y: {y}, scale: {sc} }}, 0);')

    def ecrire(self):
        duree = round(self.fin - self.debut, 3)
        if self.premiere:
            cam_js = [f'tl.fromTo("#{self.id}-cam", {{ scale: 1 }}, {{ scale: 1.04, duration: {round(duree - 0.2, 3)}, ease: "none" }}, 0);']
        else:
            cam_js = [f'tl.fromTo("#{self.id}-cam", {{ filter: "blur(14px)", scale: 1.12 }}, {{ filter: "blur(0px)", scale: 1, duration: 0.18, ease: "power2.out" }}, 0);',
                      f'tl.to("#{self.id}-cam", {{ scale: 1.04, duration: {round(duree - 0.4, 3)}, ease: "none" }}, 0.18);']
        if not self.derniere:
            sortie = [f'tl.to("#{self.id}-cam", {{ scale: 1.25, filter: "blur(14px)", duration: 0.2, ease: "power3.in" }}, {round(duree - 0.2, 3)});']
        else:
            sortie = [f'tl.fromTo("#{self.id}-noir", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "power2.in" }}, {round(duree - 0.6, 3)});']
            self.add(f'<div id="{self.id}-noir" style="position: absolute; inset: 0; background: #000; opacity: 0"></div>')
        dans = "\n        ".join(h[4:] for h in self.html if h.startswith("CAM:"))
        hors = "\n      ".join(h for h in self.html if not h.startswith("CAM:"))
        js = "\n".join("    " + c for c in cam_js) + "\n" + "\n".join(self.js) + "\n" + "\n".join("    " + c for c in sortie)
        page = f"""<!-- {self.titre} ({self.debut} → {self.fin} s). Écrit par tools/construire-scenes.py. -->
<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
  </style>
  <div id="root" data-composition-id="{self.id}" data-width="1080" data-height="1920">
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


def scene(k, titre):
    return SV(NOMS[k], COUPES[k], COUPES[k + 1], titre, premiere=(k == 0), derniere=(k == len(NOMS) - 1))


# ================================================================ SON
SFX = ICI / "assets/sfx"


def _pics():
    f = SFX / "pics.json"
    if f.exists():
        return json.loads(f.read_text())
    d = {}
    for m in sorted(SFX.glob("*.mp3")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(m), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, dtype=np.float32)
        w = 400
        n = len(x) // w
        e = (x[: n * w].reshape(n, w) ** 2).mean(1)
        d[m.stem] = {"pic": round(float(e.argmax()) * w / 8000, 3), "duree": round(len(x) / 8000, 3)}
    f.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    return d


PICS = _pics()
SONS = []


def son(t, nom, v=0.4, note="", d=None, sur_pic=True):
    p = PICS[nom]
    debut = t - (p["pic"] if sur_pic else 0)
    SONS.append((round(max(0.0, debut), 2), nom, round(v * VOL_SFX, 3), note, round(min(d or p["duree"], p["duree"]), 2)))


TOURS = {}


def tour(liste):
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


ZOOM_IN = ["zoom-air", "zoom-swipe", "zoom-futur", "zoom-impact", "zoom-in-out", "zoom-scifi"]
ZOOM_OUT = ["swoosh-court", "souffle-air", "swoosh-accent", "swoosh-tourbillon"]
POPS = ["pop-bulle", "pop-click", "pop-cartoon", "pop-sec", "pop-long"]
IMPACTS = ["impact-basse", "impact-tambour", "impact-whoosh", "impact-futur"]


def zoom(s, g, px, py, sc, d=0.3, v=0.5):
    s.recadre(g, px, py, sc, d)
    son(g + d / 2, tour(ZOOM_IN if sc > 1.02 else ZOOM_OUT), v, "rush de caméra")


def pano(s, g, px, py, sc=1.0, d=0.45, v=0.45):
    """Panoramique qui accompagne un déplacement (filé, avec souffle)."""
    s.recadre(g, px, py, sc, d)
    son(g + d / 2, tour(["swoosh-vitesse", "souffle-rapide", "swoosh-vol", "fouet"]), v, "panoramique")


def pop(t, v=0.42, note="apparition"):
    son(t, tour(POPS), v, note)


def impact(t, v=0.5, note="impact"):
    son(t, tour(IMPACTS), v, note)


# ================================================================ PERSONNAGES (verticaux et bleus)
BOUCHES = {"content": "M41 32 Q50 40 59 32", "triste": "M41 38 Q50 30 59 38", "o": "M45 34 Q50 42 55 34 Q50 27 45 34",
           "rire": "M39 30 Q50 46 61 30 Z", "neutre": "M43 34 L57 34"}
ACCESSOIRES = {
    "tom": '<path d="M28 12 Q34 -6 50 -4 Q66 -6 72 12 Q62 4 50 6 Q38 4 28 12 Z" fill="#0B1220" />',
    "emma": ('<circle cx="50" cy="-8" r="13" fill="#0B1220" /><path d="M27 18 Q28 -2 50 -2 Q72 -2 73 18 Q64 6 50 7 Q36 6 27 18 Z" fill="#0B1220" />'
             '<path d="M27 16 Q22 34 28 46" fill="none" stroke="#0B1220" stroke-width="7" stroke-linecap="round" />'),
    "hugo": '<path d="M26 12 Q28 -6 50 -6 Q72 -6 74 12 Z" fill="#0B1220" /><rect x="60" y="6" width="34" height="8" rx="4" fill="#0B1220" />',
    "autre": "",
    "lucas": '<path d="M28 14 Q30 -4 50 -3 Q70 -4 72 14 Q66 6 58 8 Q50 2 42 8 Q34 6 28 14 Z" fill="#0B1220" />',
    "banquier": '<path d="M27 12 Q30 -2 50 -2 Q70 -2 73 12 Q60 4 50 5 Q40 4 27 12 Z" fill="#0B1220" />',
}


def perso(id_, cx, pieds, h, coul, genre="tom", lunettes=False):
    """Personnage articulé (tête, tronc, bras, jambes) avec visage : yeux qui clignent, pupilles, bouche."""
    w = round(h * 160 / 290)
    groupes = []
    for k, (forme, _) in PARTIES.items():
        visage = ""
        if k == "tete":
            forme = '<circle cx="50" cy="24" r="22" />'
            lun = (f'<g id="{id_}-lun" style="opacity: 0"><rect x="31" y="14" width="17" height="11" rx="4" fill="#0B1220" />'
                   f'<rect x="52" y="14" width="17" height="11" rx="4" fill="#0B1220" /><rect x="46" y="17" width="8" height="3" fill="#0B1220" /></g>') if lunettes else ""
            visage = (f'<g><g id="{id_}-yeux"><circle cx="41" cy="20" r="6.5" fill="#fff" /><circle cx="59" cy="20" r="6.5" fill="#fff" />'
                      f'<g id="{id_}-pup"><circle cx="42" cy="21" r="3" fill="#0B1220" /><circle cx="60" cy="21" r="3" fill="#0B1220" /></g></g>'
                      f'<path id="{id_}-bouche" d="{BOUCHES["content"]}" fill="none" stroke="#0B1220" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />'
                      f'{ACCESSOIRES[genre]}{lun}</g>')
        if k == "tronc":
            visage = ('<path d="M44 56 L56 56 L53 64 L57 104 L50 112 L43 104 L47 64 Z" fill="#0B1220" />' if genre in ("lucas", "banquier")
                      else '<rect x="30" y="60" width="40" height="7" rx="3.5" fill="rgba(11,18,32,0.25)" />')
        groupes.append(f'<g id="{id_}-{k}"><g class="c">{forme}</g><g class="p" style="--pc: {coul}">{forme}</g>{visage}</g>')
    return (f'<svg id="{id_}" class="perso" viewBox="-30 -20 160 290" '
            f'style="left: {cx - w // 2}px; top: {pieds - round(h * 268 / 290)}px; width: {w}px; height: {h}px">'
            f'<g id="{id_}-vie"><g id="{id_}-corps">{"".join(groupes)}</g></g></svg>')


def tete_y(pieds, h):
    """Haut de la tête du personnage, en pixels."""
    return pieds - round(h * 268 / 290) + round(h * 18 / 290)


def main_d(cx, pieds, h, angle):
    """Position (px) de la main droite quand le bras droit est tourné de `angle` degrés."""
    sc = h / 290
    gauche, haut = cx - round(h * 160 / 290) // 2, pieds - round(h * 268 / 290)
    a = math.radians(-angle)
    hx, hy = 89 + 80 * math.sin(a), 62 + 80 * math.cos(a)
    return round(gauche + (hx + 30) * sc), round(haut + (hy + 20) * sc)


def humeur(s, pid, g, h="content"):
    plein = "#0B1220" if h == "rire" else "none"
    s.j(f'tl.set("#{pid}-bouche", {{ attr: {{ d: "{BOUCHES[h]}", fill: "{plein}" }} }}, {s.L(g)});')


def cligne(s, pid, g0, g1, periode=2.3, decal=0.7):
    t = g0 + decal
    while t < g1 - 0.3:
        s.j(f'tl.to("#{pid}-yeux", {{ scaleY: 0.1, duration: 0.06, yoyo: true, repeat: 1, svgOrigin: "50 20" }}, {s.L(t)});')
        t += periode


def regarde(s, pid, g, dx, dy=0):
    s.j(f'tl.to("#{pid}-pup", {{ x: {dx}, y: {dy}, duration: 0.15 }}, {s.L(g)});')


def vivant(s, pid, g0=None, g1=None, amp=5, periode=0.42, decal=0.7):
    g0 = s.debut if g0 is None else g0
    g1 = s.fin - 0.2 if g1 is None else g1
    vit(s, pid, g0, g1, amp, periode)
    cligne(s, pid, g0, g1, 2.3 + decal / 3, decal)


def nom(s, nid, texte, x, y, g, coul=CIEL):
    cam(s, f'<div id="{nid}" class="nom" style="left: {x}px; top: {y}px; opacity: 0"><b style="background: {coul}">{texte}</b></div>')
    s.j(f'tl.fromTo("#{nid}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.4)", immediateRender: false }}, {s.L(g)});')
    pop(g, 0.36, f"nom {texte}")


def gouttes(s, gid, x, y, g, n=3):
    """Gouttes de sueur qui perlent (stress)."""
    for k in range(n):
        cam(s, f'<i id="{gid}-{k}" class="goutte" style="left: {x + k * 26}px; top: {y + (k % 2) * 18}px; opacity: 0"></i>')
        s.j(f'tl.fromTo("#{gid}-{k}", {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 30, duration: 0.5, repeat: 2, ease: "power1.in", immediateRender: false }}, {s.L(g + k * 0.15)});')
        s.j(f'tl.to("#{gid}-{k}", {{ opacity: 0, duration: 0.1 }}, {s.L(g + k * 0.15 + 1.5)});')


def dos(s, pid, g):
    """Tourne le dos (miroir)."""
    s.j(f'tl.to("#{pid}-corps", {{ scaleX: -1, transformOrigin: "50% 50%", duration: 0.16 }}, {s.L(g)});')
    s.j(f'tl.to("#{pid}-yeux", {{ opacity: 0, duration: 0.05 }}, {s.L(g + 0.08)});')
    s.j(f'tl.to("#{pid}-bouche", {{ opacity: 0, duration: 0.05 }}, {s.L(g + 0.08)});')


# ================================================================ DÉCORS
def decor_rue(s, k, x0=0, y0=0, jour=False, gauche=1080, droite=1080):
    """Rue la nuit (ou en journée) : ciel, immeubles éclairés, lampadaire, sol. Débord à gauche et à droite pour les panoramiques."""
    ciel = ("linear-gradient(180deg, #1d4ed8 0%, #38bdf8 55%, #bae6fd 100%)" if jour
            else "linear-gradient(180deg, #050a14 0%, #0b1a35 45%, #13305c 100%)")
    imm = []
    for dx in (0, 1080, 2160):
        for n, (x, w, h, c) in enumerate([(-20, 210, 520, "#0f2347"), (170, 170, 380, "#122a52"), (320, 240, 610, "#0d1f40"),
                                           (540, 190, 440, "#11284e"), (710, 230, 560, "#0e2244"), (920, 200, 400, "#122a52")]):
            imm.append(f'<div class="imm" style="left: {x + dx}px; top: {SOL - 120 - h}px; width: {w}px; height: {h}px; background-color: {c}"></div>')
    lune = '' if jour else '<i class="lune" style="left: 1900px; top: 330px"></i>'
    soleil = '<i class="soleil" style="left: 1880px; top: 320px"></i>' if jour else ''
    cam(s, f'<div class="decor" style="left: {x0 - gauche}px; top: {y0}px; width: {1080 + gauche + droite}px"><div style="position: absolute; left: {gauche - 1080}px; top: 0; width: 3240px; height: 1920px">'
           f'<div class="ciel" style="background: {ciel}"></div>{lune}{soleil}'
           f'{"".join(imm)}<div class="trottoir" style="top: {SOL - 120}px"></div><div class="sol" style="top: {SOL}px"></div>'
           f'<i class="lampe" style="left: 2020px; top: {SOL - 520}px"></i></div></div>')


def decor_chambre(s, k, x0=0, y0=0):
    """Chambre de Tom la nuit : mur, fenêtre, sol."""
    cam(s, f'<div class="decor" style="left: {x0 - 1080}px; top: {y0}px; width: 3240px"><div class="mur"></div>'
           f'<div class="fenetre" style="left: 1150px; top: 380px"><i class="lune" style="left: 150px; top: 40px; width: 70px; height: 70px"></i></div>'
           f'<div class="plinthe" style="top: {SOL - 20}px"></div><div class="parquet" style="top: {SOL}px"></div></div>')


# ================================================================ ÉLÉMENTS
def fcfa(n):
    return f"{n:,}".replace(",", " ")


def video_html(vid, f, debut, duree, piste):
    return (f'<video id="{vid}" class="clip" src="assets/video/{f}.mp4" data-start="{round(debut, 2)}" data-duration="{round(duree, 2)}" '
            f'data-track-index="{piste}" muted playsinline></video>')


PISTES = {}


def piste(s):
    PISTES[s.id] = PISTES.get(s.id, 4) + 1
    return PISTES[s.id]


def videos(s, p, items, fin=None, sons=True, son_v=0.34):
    """Pile de vraies vidéos dans un conteneur : une nouvelle à chaque temps donné (coupe sèche + léger zoom)."""
    out = []
    fin = s.fin if fin is None else fin
    for k, (t, f) in enumerate(items):
        t2 = items[k + 1][0] if k + 1 < len(items) else fin
        out.append(f'<div id="{p}-{k}" class="vplein" style="opacity: 0">{video_html(f"{p}-{k}-v", f, s.L(t), t2 - t + 0.1, piste(s))}</div>')
        s.j(f'tl.set("#{p}-{k}", {{ opacity: 1 }}, {s.L(t)});')
        s.j(f'tl.fromTo("#{p}-{k}", {{ scale: 1.18 }}, {{ scale: 1.02, duration: {round(max(0.2, t2 - t), 3)}, ease: "power2.out", immediateRender: false }}, {s.L(t)});')
        if k + 1 < len(items):
            s.j(f'tl.set("#{p}-{k}", {{ opacity: 0 }}, {s.L(t2 + 0.02)});')
        elif fin < s.fin:
            s.j(f'tl.set("#{p}-{k}", {{ opacity: 0 }}, {s.L(fin)});')
        if sons and k > 0:
            son(t, tour(["balaie-rapide", "fouet", "balaie-court", "swoosh-court", "declencheur", "balaie-air", "glitch-mini"]), son_v, f"vidéo : {f}")
    return "".join(out)


def ecran(s, eid, x, y, w, h, items, g, fin=None, style="tele", titre_e=""):
    """Écran DANS la scène (télé, panneau, écran de garage) qui contient de vraies vidéos."""
    pied = '<i class="tele-pied"></i>' if style == "tele" else ""
    tit = f'<b class="ecran-titre">{titre_e}</b>' if titre_e else ""
    cam(s, f'<div id="{eid}" class="ecran ecran-{style}" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0">'
           f'<div class="ecran-in">{videos(s, eid + "-v", items, fin)}</div>{tit}{pied}</div>')
    s.j(f'tl.fromTo("#{eid}", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(1.8)", immediateRender: false }}, {s.L(g)});')
    son(g, tour(["interrupteur", "bouton-tech", "pop-long"]), 0.4, f"écran {eid}")
    return x + w / 2, y + h / 2


def zoom_ecran(s, g, x, y, w, h, retour, d=0.32, marge=0.94):
    """La caméra plonge dans l'écran (il remplit l'image), puis revient au plan `retour` = (px, py, sc, t)."""
    sc = round(min(W / w, H / h) * marge, 3)
    zoom(s, g, x + w / 2, y + h / 2, sc, d, 0.5)
    px, py, sc2, t = retour
    zoom(s, t, px, py, sc2, d, 0.42)


def bulle(s, bid, texte, x, y, g, fin=None, queue="g", w=None, taille=46, pensee=False):
    """Bulle de dialogue blanche avec sa pointe (queue : g = pointe en bas à gauche, d = en bas à droite)."""
    style_w = f"width: {w}px; white-space: normal;" if w else ""
    cls = "bulle pensee" if pensee else "bulle"
    cam(s, f'<div id="{bid}" class="{cls} q-{queue}" style="left: {x}px; top: {y}px; font-size: {taille}px; {style_w} opacity: 0">{texte}</div>')
    origine = "10% 100%" if queue == "g" else "90% 100%"
    s.j(f'tl.fromTo("#{bid}", {{ opacity: 0, scale: 0.2, transformOrigin: "{origine}" }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.4)", immediateRender: false }}, {s.L(g)});')
    son(g, tour(["pop-bulle", "pop-cartoon", "pop-click"]), 0.42, "bulle")
    if fin is not None:
        s.j(f'tl.to("#{bid}", {{ opacity: 0, scale: 0.7, duration: 0.14 }}, {s.L(fin)});')


def bulle_video(s, bid, cx, cy, r, items, g, fin, vers):
    """Bulle de pensée ronde qui contient une vraie vidéo, reliée à la tête par trois petits ronds."""
    vx, vy = vers
    ronds = "".join(f'<i class="rond" id="{bid}-r{k}" style="left: {round(vx + (cx - vx) * f - 14 * (3 - k))}px; top: {round(vy + (cy + r - vy) * f - 14 * (3 - k))}px; '
                    f'width: {28 * (3 - k)}px; height: {28 * (3 - k)}px; opacity: 0"></i>' for k, f in enumerate((0.15, 0.4, 0.7)))
    cam(s, ronds + f'<div id="{bid}" class="pensee-video" style="left: {cx - r}px; top: {cy - r}px; width: {2 * r}px; height: {2 * r}px; opacity: 0">'
           f'{videos(s, bid + "-v", items, fin)}</div>')
    for k in range(3):
        s.j(f'tl.fromTo("#{bid}-r{k}", {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "back.out(3)", immediateRender: false }}, {s.L(g + k * 0.06)});')
        s.j(f'tl.to("#{bid}-r{k}", {{ opacity: 0, duration: 0.12 }}, {s.L(fin)});')
    s.j(f'tl.fromTo("#{bid}", {{ opacity: 0, scale: 0.2 }}, {{ opacity: 1, scale: 1, duration: 0.26, ease: "back.out(1.9)", immediateRender: false }}, {s.L(g + 0.15)});')
    s.j(f'tl.to("#{bid}", {{ opacity: 0, scale: 0.5, duration: 0.16 }}, {s.L(fin)});')
    son(g, "magie", 0.4, "bulle de pensée")


def apparait(s, sel, g, d=0.22, dy=60, s0=0.7):
    s.j(f'tl.fromTo("{sel}", {{ opacity: 0, y: {dy}, scale: {s0} }}, {{ opacity: 1, y: 0, scale: 1, duration: {d}, ease: "back.out(1.8)", immediateRender: false }}, {s.L(g)});')


def claque(s, sel, g, s0=2.0, d=0.16):
    s.j(f'tl.fromTo("{sel}", {{ opacity: 0, scale: {s0} }}, {{ opacity: 1, scale: 1, duration: {d}, ease: "power4.in", immediateRender: false }}, {s.L(g)});')


def cache(s, sel, g, d=0.15):
    s.j(f'tl.to("{sel}", {{ opacity: 0, duration: {d} }}, {s.L(g)});')


def secousse(s, g, amp=18):
    s.j(f'tl.to("#{s.id}-cam", {{ keyframes: [{{ x: -{amp}, duration: 0.03 }}, {{ x: {amp}, duration: 0.04 }}, {{ x: -{amp // 2}, duration: 0.04 }}, {{ x: 0, duration: 0.03 }}] }}, {s.L(g)});')


def flash(s, g, coul="#ffffff"):
    fid = f"{s.id}-flash-{len(s.html)}"
    s.add(f'<div id="{fid}" style="position: absolute; inset: 0; background: {coul}; opacity: 0"></div>')
    s.j(f'tl.fromTo("#{fid}", {{ opacity: 0.9 }}, {{ opacity: 0, duration: 0.2, immediateRender: false }}, {s.L(g)});')


def texte(s, tid, html, x, y, taille, g, coul=BLANC, w=None, fin=None, cls="gros", rot=0, entree="claque"):
    """Texte en surimpression (Anton, contour bleu nuit) centré sur x si w est donné."""
    lw = f"width: {w}px; text-align: center;" if w else ""
    cam(s, f'<div id="{tid}" class="{cls}" style="left: {x}px; top: {y}px; font-size: {taille}px; color: {coul}; {lw} transform: rotate({rot}deg); opacity: 0">{html}</div>')
    if entree == "claque":
        claque(s, f"#{tid}", g)
    else:
        apparait(s, f"#{tid}", g)
    if fin is not None:
        cache(s, f"#{tid}", fin)


def compteur(s, sel, g, de, a, d, suffixe=""):
    s.n_proxy += 1
    p = f"p{s.n_proxy}"
    s.j(f'const {p} = {{ v: {de} }};')
    s.j(f'tl.fromTo({p}, {{ v: {de} }}, {{ v: {a}, duration: {d}, ease: "power2.out", immediateRender: false, '
        f'onUpdate: () => {{ document.querySelector("{sel}").textContent = String(Math.round({p}.v)).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, "\\u202f") + "{suffixe}"; }} }}, {s.L(g)});')


def piece(pid, x, y, txt="25 000", taille=110, op=0):
    return (f'<div id="{pid}" class="piece" style="left: {x - taille // 2}px; top: {y - taille // 2}px; width: {taille}px; height: {taille}px; '
            f'font-size: {round(taille * 0.2)}px; opacity: {op}"><span>{txt}</span></div>')


def vole(s, vid, x0, y0, x1, y1, g, n=6, pas=0.08, txt="", taille=90, d=0.5, sons=True, arc=-160):
    """Pièces qui volent d'un point à un autre (en arc)."""
    for k in range(n):
        gk = g + k * pas
        cam(s, piece(f"{vid}-{k}", x0, y0, txt, taille))
        s.j(f'tl.set("#{vid}-{k}", {{ opacity: 1 }}, {s.L(gk)});')
        s.j(f'tl.fromTo("#{vid}-{k}", {{ x: 0 }}, {{ x: {x1 - x0}, duration: {d}, ease: "power1.inOut", immediateRender: false }}, {s.L(gk)});')
        s.j(f'tl.fromTo("#{vid}-{k}", {{ y: 0 }}, {{ keyframes: [{{ y: {arc}, duration: {d / 2}, ease: "power2.out" }}, {{ y: {y1 - y0}, duration: {d / 2}, ease: "power2.in" }}] }}, {s.L(gk)});')
        s.j(f'tl.set("#{vid}-{k}", {{ opacity: 0 }}, {s.L(gk + d)});')
        if sons and k % 2 == 0:
            son(gk + d, tour(["piece-gagne", "pieces", "pieces-2"]), 0.3, "pièce")


def billets(s, bid, g, n=16, d=1.6, y0=-200):
    """Pluie de billets dessinés (stylisés, pas des reproductions)."""
    for k in range(n):
        x = 40 + (k * 211) % 1000
        r = (k * 47) % 60 - 30
        dy = 1400 + (k * 83) % 500
        gk = g + (k * 0.071) % 0.5
        cam(s, f'<div id="{bid}-{k}" class="billet" data-layout-allow-overlap style="left: {x}px; top: {y0}px; opacity: 0"><b>FCFA</b><span>BILLET</span></div>')
        s.j(f'tl.fromTo("#{bid}-{k}", {{ opacity: 1, y: 0, rotation: {r} }}, {{ opacity: 1, y: {dy}, rotation: {r + 200}, duration: {d}, ease: "power1.in", immediateRender: false }}, {s.L(gk)});')
        s.j(f'tl.set("#{bid}-{k}", {{ opacity: 0 }}, {s.L(gk + d)});')
    son(g, "papiers", 0.36, "pluie de billets")


def confettis(s, cid, g, cx, cy, n=26, rayon=460):
    for k in range(n):
        ang = k * 2.39996
        dist = rayon * (0.45 + 0.55 * ((k * 37) % 11) / 10)
        dx, dy = round(math.cos(ang) * dist), round(math.sin(ang) * dist * 0.8 - 160)
        coul = (CIEL, OR, BLANC, CLAIR)[k % 4]
        cam(s, f'<i id="{cid}-{k}" style="position: absolute; left: {cx}px; top: {cy}px; width: {22 if k % 2 else 14}px; height: {12 if k % 2 else 14}px; background: {coul}; opacity: 0"></i>')
        s.j(f'tl.fromTo("#{cid}-{k}", {{ x: 0, y: 0, rotation: 0, opacity: 1 }}, {{ x: {dx}, y: {dy + 320}, rotation: {(k * 97) % 540 - 270}, opacity: 0, duration: 1.4, ease: "power2.out", immediateRender: false }}, {s.L(g)});')
    son(g, "paillettes", 0.38, "confettis")


def tampon(s, tid, txt, x, y, g, rot=-10, taille=96, coul=CORAIL):
    cam(s, f'<div id="{tid}" class="tampon" data-layout-allow-overlap style="left: {x}px; top: {y}px; font-size: {taille}px; color: {coul}; border-color: {coul}; transform: rotate({rot}deg); opacity: 0">{txt}</div>')
    s.j(f'tl.fromTo("#{tid}", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.in", immediateRender: false }}, {s.L(g)});')
    secousse(s, g + 0.14, 12)
    son(g + 0.14, "marteau", 0.45, f"tampon {txt}")


def etiquette(s, eid, html, x, y, g, fond=CIEL, coul=NUIT, taille=54, rot=-3, fin=None):
    cam(s, f'<div id="{eid}" class="etiq" style="left: {x}px; top: {y}px; font-size: {taille}px; background: {fond}; color: {coul}; transform: rotate({rot}deg); opacity: 0">{html}</div>')
    s.j(f'tl.fromTo("#{eid}", {{ opacity: 0, x: -80 }}, {{ opacity: 1, x: 0, duration: 0.2, ease: "power4.out", immediateRender: false }}, {s.L(g)});')
    son(g, tour(["swoosh-court", "balaie-petit", "pop-sec"]), 0.38, "étiquette")
    if fin is not None:
        cache(s, f"#{eid}", fin)


def telephone(s, tid, x, y, w, h, contenu, g=None, op=0):
    cam(s, f'<div id="{tid}" class="tel" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: {op}">'
           f'<i class="tel-cam"></i><div class="tel-ecran">{contenu}</div></div>')
    if g is not None:
        apparait(s, f"#{tid}", g, 0.25, 200, 0.8)
        son(g, "swoosh-monte", 0.42, "téléphone")


def message(s, mid, auteur, txt, g, moi=False):
    cls = "msg moi" if moi else "msg"
    s.j(f'tl.fromTo("#{mid}", {{ opacity: 0, y: 40, scale: 0.8 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, {s.L(g)});')
    son(g, tour(["notif-indice", "notif-positive", "notif-magique"]), 0.45, f"message {auteur}")
    return f'<div id="{mid}" class="{cls}" style="opacity: 0"><b>{auteur}</b>{txt}</div>'


def appel(s, aid, qui, x, y, g, fin):
    cam(s, f'<div id="{aid}" class="appel" style="left: {x}px; top: {y}px; opacity: 0"><i class="appel-ic"></i><div><b>Appel entrant</b><span>{qui}</span></div></div>')
    s.j(f'tl.fromTo("#{aid}", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.2)", immediateRender: false }}, {s.L(g)});')
    s.j(f'tl.to("#{aid}", {{ rotation: 4, duration: 0.06, repeat: {max(1, int((fin - g) / 0.06) - 4)}, yoyo: true, ease: "none" }}, {s.L(g + 0.2)});')
    cache(s, f"#{aid}", fin)
    son(g, "sonnerie", 0.32, f"appel {qui}", d=min(1.8, fin - g + 0.2))


def moto(mid, x, y, w=520, op=0):
    """Moto d'occasion dessinée (vue de profil)."""
    return (f'<svg id="{mid}" class="moto" viewBox="0 0 260 150" style="left: {x}px; top: {y}px; width: {w}px; height: {round(w * 150 / 260)}px; opacity: {op}">'
            '<circle cx="52" cy="112" r="34" fill="#0B1220" stroke="#e2e8f0" stroke-width="8" /><circle cx="52" cy="112" r="10" fill="#94a3b8" />'
            '<circle cx="208" cy="112" r="34" fill="#0B1220" stroke="#e2e8f0" stroke-width="8" /><circle cx="208" cy="112" r="10" fill="#94a3b8" />'
            '<path d="M52 112 L96 70 L170 70 L208 112" fill="none" stroke="#0B1220" stroke-width="10" stroke-linejoin="round" />'
            '<path d="M84 64 Q120 40 170 52 L190 74 L104 82 Z" fill="#38BDF8" stroke="#0B1220" stroke-width="6" stroke-linejoin="round" />'
            '<path d="M70 58 L128 54 L124 66 L76 68 Z" fill="#0B1220" />'
            '<path d="M176 56 L196 22 L214 20" fill="none" stroke="#0B1220" stroke-width="9" stroke-linecap="round" />'
            '<circle cx="222" cy="58" r="11" fill="#F2B705" stroke="#0B1220" stroke-width="5" />'
            '<rect x="112" y="80" width="46" height="22" rx="6" fill="#64748b" stroke="#0B1220" stroke-width="5" /></svg>')


def cadenas_html():
    return ('<svg viewBox="0 0 120 150" width="54" height="68"><path d="M30 70 L30 42 Q30 12 60 12 Q90 12 90 42 L90 70" fill="none" stroke="#F1F5F9" stroke-width="14" stroke-linecap="round" />'
            '<rect x="14" y="66" width="92" height="76" rx="14" fill="#38BDF8" /></svg>')



# ================================================================ DÉCORS PROPRES À LA VIDÉO 5 (magasin, banque, bureau) ET ÉLÉMENTS
def decor_magasin(s, k):
    """Intérieur du magasin : mur, étagères garnies, comptoir, sol."""
    etag = []
    for r, y in enumerate((420, 600, 780)):
        etag.append(f'<div class="etagere" style="left: 1100px; top: {y}px; width: 1200px"></div>')
        for n in range(9):
            coul = ("#38BDF8", "#F2B705", "#7DD3FC", "#F1F5F9", "#0284C7")[(n + r) % 5]
            h = 70 + (n * 23 + r * 17) % 60
            etag.append(f'<i class="produit" style="left: {1130 + n * 125}px; top: {y - h}px; height: {h}px; background: {coul}"></i>')
    cam(s, f'<div class="decor" style="left: -1080px; top: 0; width: 3240px"><div class="mur-magasin"></div>{"".join(etag)}'
           f'<div class="plinthe" style="top: {SOL - 20}px"></div><div class="parquet" style="top: {SOL}px"></div></div>')


def facade_banque(fid, x, y, w=620):
    cols = "".join(f'<i style="left: {40 + k * (w - 120) // 4}px"></i>' for k in range(5))
    return (f'<div id="{fid}" class="banque-fac" style="left: {x}px; top: {y}px; width: {w}px"><div class="banque-toit"></div>'
            f'<b>BANQUE</b><div class="banque-cols">{cols}</div><div class="banque-marche"></div></div>')


def coffre(cid, x, y, montant="10 000 000 F", titre_c="RÉSERVE"):
    return (f'<div id="{cid}" class="coffre" style="left: {x}px; top: {y}px; opacity: 0"><span>{titre_c}</span><b>{montant}</b>'
            f'<i class="coffre-roue"></i></div>')


def ligne_calc(lid, label, valeur, x, y, w=900, coul="#F1F5F9", taille=64, cachee=True):
    """Ligne d'un calcul ou d'un tableau, verrouillée (cadenas) jusqu'à sa révélation."""
    cad = f'<em id="{lid}-q">{cadenas_html()}</em>' if cachee else ""
    op = 0 if cachee else 1
    return (f'<div id="{lid}" class="ligne-calc" style="left: {x}px; top: {y}px; width: {w}px"><span>{label}</span>'
            f'<b id="{lid}-v" style="color: {coul}; font-size: {taille}px; opacity: {op}">{valeur}</b>{cad}</div>')


def revele(s, lid, g, son_nom="revelation"):
    s.j(f'tl.to("#{lid}-q", {{ opacity: 0, scale: 0.3, duration: 0.12 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{lid}-v", {{ opacity: 0, scale: 1.7 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2)", immediateRender: false }}, {s.L(g + 0.04)});')
    s.j(f'tl.fromTo("#{lid}", {{ backgroundColor: "rgba(56, 189, 248, 0.35)" }}, {{ backgroundColor: "rgba(19, 32, 58, 0.92)", duration: 0.6, immediateRender: false }}, {s.L(g)});')
    son(g, son_nom if son_nom in PICS else "deverrouille", 0.42, f"révélation {lid}")


def interrogations(s, qid, x, y, g, n=3):
    for k in range(n):
        cam(s, f'<div id="{qid}-{k}" class="gros" style="left: {x + k * 70}px; top: {y - (k % 2) * 40}px; font-size: {90 + k * 20}px; color: {OR}; opacity: 0">?</div>')
        s.j(f'tl.fromTo("#{qid}-{k}", {{ opacity: 0, y: 40, rotation: -20 }}, {{ opacity: 1, y: 0, rotation: {(-10, 8, -4)[k % 3]}, duration: 0.25, ease: "back.out(2.5)", immediateRender: false }}, {s.L(g + k * 0.12)});')
        s.j(f'tl.to("#{qid}-{k}", {{ y: -18, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {s.L(g + 0.3 + k * 0.12)});')


# ================================================================ ÉLÉMENTS PROPRES À LA VIDÉO 6 (icônes, app de paiement, jauge, ticket, règle)
ICONES = {
    "cafe": ('<path d="M18 38 H70 V62 Q70 84 44 84 Q18 84 18 62 Z" fill="#F1F5F9" stroke="#0B1220" stroke-width="6" />'
             '<path d="M70 46 Q88 46 88 58 Q88 70 70 70" fill="none" stroke="#0B1220" stroke-width="6" />'
             '<path d="M32 12 Q38 20 32 28 M46 10 Q52 18 46 26 M60 12 Q66 20 60 28" fill="none" stroke="#38BDF8" stroke-width="5" stroke-linecap="round" />'),
    "taxi": ('<rect x="34" y="18" width="32" height="12" rx="3" fill="#F2B705" stroke="#0B1220" stroke-width="5" />'
             '<path d="M14 60 L24 36 H76 L86 60 Z" fill="#F2B705" stroke="#0B1220" stroke-width="6" stroke-linejoin="round" />'
             '<path d="M30 56 L36 42 H64 L70 56 Z" fill="#7DD3FC" stroke="#0B1220" stroke-width="4" />'
             '<rect x="8" y="58" width="84" height="20" rx="6" fill="#F2B705" stroke="#0B1220" stroke-width="6" />'
             '<circle cx="28" cy="80" r="9" fill="#0B1220" /><circle cx="72" cy="80" r="9" fill="#0B1220" />'),
    "credit": ('<rect x="28" y="8" width="44" height="84" rx="10" fill="#0B1220" stroke="#F1F5F9" stroke-width="4" />'
               '<rect x="34" y="20" width="32" height="56" rx="3" fill="#38BDF8" />'
               '<path d="M40 64 V58 M48 64 V50 M56 64 V42 M62 64 V34" stroke="#0B1220" stroke-width="5" stroke-linecap="round" />'),
    "livraison": ('<path d="M14 34 L50 18 L86 34 L86 74 L50 90 L14 74 Z" fill="#c08a4a" stroke="#0B1220" stroke-width="6" stroke-linejoin="round" />'
                  '<path d="M14 34 L50 50 L86 34 M50 50 V90" fill="none" stroke="#0B1220" stroke-width="6" />'
                  '<path d="M32 26 L68 42" stroke="#F1F5F9" stroke-width="6" />'),
}
LIBELLES = {"cafe": "Petit déj", "taxi": "Taxi", "credit": "Crédit", "livraison": "Livraison"}


def icone(n, t=80, ident=""):
    i = f' id="{ident}"' if ident else ""
    return f'<svg{i} class="ico" viewBox="0 0 100 100" width="{t}" height="{t}">{ICONES[n]}</svg>'


def tx(tid, n, lib=None, note="payé"):
    return f'<div id="{tid}" class="tx">{icone(n, 54)}<span>{lib or LIBELLES[n]}</span><em>{note}</em></div>'


def puce(s, pid, n, lib, x, y, g, taille=46, note=""):
    em = f"<em>{note}</em>" if note else ""
    cam(s, f'<div id="{pid}" class="puce" style="left: {x}px; top: {y}px; font-size: {taille}px; opacity: 0">{icone(n, round(taille * 1.5))}<div>{em}{lib}</div></div>')
    s.j(f'tl.fromTo("#{pid}", {{ opacity: 0, x: -120, scale: 0.7 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.22, ease: "back.out(2)", immediateRender: false }}, {s.L(g)});')
    son(g, tour(["pop-cartoon", "pop-bulle", "pop-click"]), 0.42, f"puce {lib}")


def paye(t, v=0.42):
    """Petit bruit de paiement validé (caisse ou notification)."""
    son(t, tour(["scanner-caisse", "notif-positive", "pieces-tintent", "notif-indice"]), v, "paiement")


def tap(s, tid, x, y, g):
    """Doigt qui tape l'écran : rond qui s'élargit."""
    cam(s, f'<i id="{tid}" class="tap" style="left: {x - 50}px; top: {y - 50}px; opacity: 0"></i>')
    s.j(f'tl.fromTo("#{tid}", {{ opacity: 0.9, scale: 0.3 }}, {{ opacity: 0, scale: 1.4, duration: 0.35, ease: "power2.out", immediateRender: false }}, {s.L(g)});')
    son(g, "clic", 0.5, "tape l'écran")


def ralenti_gris(s, g, d=0.15):
    s.j(f'tl.to("#{s.id}-cadre", {{ filter: "grayscale(1) contrast(1.2) brightness(0.8)", duration: {d} }}, {s.L(g)});')


# ================================================================ SCÈNE 1 : HOOK (0 → 3,5 s) : le sujet écrit en clair, une vraie vidéo par mot
s = scene(0, "Hook : ton salaire disparaît avant le 15 du mois ? Voici pourquoi.")
items = [(0, "compteuse-machine"), (T(1), "stk-cash-rotation"), (T(2), "plus-argent-poches"), (T(3), "billets-tombent"), (T(5), "feu-pieton"),
         (T(6), "horloge-billets"), (T(7), "portefeuille-vide"), (T(8), "mains-tete"), (T(9), "frustre-tel")]
cam(s, f'<div id="h-plein" class="plein">{videos(s, "h-v", items, son_v=0.4)}</div><div class="voile-bas"></div>')
son(0.0, "trailer-impact", 0.6, "début")
son(0.02, "whoosh-cine", 0.45, "début")
texte(s, "h-t1", "TON SALAIRE", 0, 640, 150, 0.02, BLANC, w=1080, fin=T(3) - 0.02)
texte(s, "h-t2", "DISPARAÎT", 0, 800, 190, T(2), CIEL, w=1080)
son(T(2), "glitch-cine", 0.5, "disparaît")
billets(s, "h-b", T(2) + 0.05, 12, 1.3)
s.j(f'tl.to("#h-t2", {{ opacity: 0, y: -90, filter: "blur(18px)", scale: 1.3, duration: 0.3, ease: "power2.in" }}, {s.L(T(3) - 0.05)});')
cam(s, '<div id="h-cal" class="calendrier" data-layout-allow-overlap style="left: 290px; top: 560px; opacity: 0"><span>AVANT LE</span><b>15</b></div>'
       '<svg id="h-rond" viewBox="0 0 520 300" data-layout-allow-overlap style="position: absolute; left: 280px; top: 720px; width: 520px; height: 300px; opacity: 0">'
       '<ellipse cx="260" cy="150" rx="230" ry="130" fill="none" stroke="#FF6B6B" stroke-width="16" stroke-dasharray="1500" stroke-dashoffset="1500" id="h-rond-t" /></svg>')
apparait(s, "#h-cal", T(3), 0.2, 120, 0.6)
son(T(3), "swoosh-monte", 0.45, "calendrier")
s.j(f'tl.fromTo("#h-cal b", {{ scale: 2.2 }}, {{ scale: 1, duration: 0.16, ease: "power4.in", immediateRender: false }}, {s.L(T(5))});')
impact(T(5), 0.6, "15")
secousse(s, T(5) + 0.1, 20)
s.j(f'tl.set("#h-rond", {{ opacity: 1 }}, {s.L(T(6))});')
s.j(f'tl.to("#h-rond-t", {{ strokeDashoffset: 0, duration: 0.35, ease: "power2.out" }}, {s.L(T(6))});')
son(T(6), "stylo", 0.45, "entoure le 15")
s.j(f'tl.to("#h-cal", {{ rotation: -6, duration: 0.06, yoyo: true, repeat: 5 }}, {s.L(T(7))});')
texte(s, "h-pq", "VOICI POURQUOI", 160, 1090, 96, T(8), NUIT, cls="gros bande", rot=-4)
son(T(8) - 0.5, "riser-tech", 0.35, "montée vers voici pourquoi", d=0.6)
impact(T(8), 0.55, "voici pourquoi")
flash(s, T(8))
secousse(s, T(8) + 0.05, 16)
s.ecrire()

# ================================================================ SCÈNE 2 : Lucas touche 150 000 FCFA ; il veut une moto
s = scene(1, "Lucas vient de toucher 150 000 FCFA ; il veut économiser pour une moto")
decor_chambre(s, "r")
cam(s, perso("r-lucas", 290, SOL, 640, CIEL, "lucas"))
vivant(s, "r-lucas")
nom(s, "r-nom", "LUCAS", 200, 640, s.debut + 0.1)
regarde(s, "r-lucas", s.debut, 4, -2)
app = ('<div class="app"><div class="app-tete">Mon compte</div><div class="app-solde"><i id="r-solde">0</i> F</div>'
       '<div id="r-notif" class="app-notif" style="opacity: 0"><b>SALAIRE REÇU</b><span>Virement de l’employeur</span></div></div>')
telephone(s, "r-tel", 600, 470, 380, 760, app, g=T(11) - 0.1)
s.j(f'tl.fromTo("#r-notif", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, {s.L(T(13))});')
son(T(13), "notif-magique", 0.5, "salaire reçu")
zoom(s, T(13) - 0.1, 790, 820, 1.6, 0.26)
compteur(s, "#r-solde", T(14), 0, 150000, 0.75)
son(T(14), "compteur", 0.42, "150 000", d=0.75)
son(T(14) + 0.78, "sac-argent", 0.5, "150 000")
s.j(f'tl.fromTo("#r-tel", {{ scale: 1 }}, {{ scale: 1.06, duration: 0.1, yoyo: true, repeat: 1, immediateRender: false }}, {s.L(T(14) + 0.78)});')
zoom(s, T(15) + 0.2, 540, 960, 1.0, 0.3)
victoire(s, "r-lucas", T(15) + 0.25, 1)
humeur(s, "r-lucas", T(15) + 0.25, "rire")
confettis(s, "r-cf", T(15) + 0.3, 790, 700, 16, 300)
cache(s, "#r-tel", T(16) + 0.1, 0.2)
humeur(s, "r-lucas", T(17), "content")
regarde(s, "r-lucas", T(17), 3, -5)
bulle_video(s, "r-pen", 690, 640, 280, [(T(17), "moto-face"), (T(19), "moto-compteur"), (T(21), "moto-accelere")], T(17) - 0.1, s.fin - 0.15, (400, 740))
zoom_ecran(s, T(18), 410, 360, 560, 560, (540, 960, 1.0, T(22) - 0.1), d=0.3)
pose(s, "r-lucas", T(20), 0.2, bd=-150)
etiquette(s, "r-obj", "OBJECTIF : MOTO", 470, 980, T(22), OR, NUIT, 64, -3)
s.ecrire()

# ================================================================ SCÈNE 3 : mais dès le lendemain, il commence à dépenser
s = scene(2, "Mais dès le lendemain, il commence à dépenser")
decor_rue(s, "l", jour=True)
cam(s, f'<div id="l-nuit" style="position: absolute; left: -1080px; top: 0; width: 3240px; height: 1920px; background: rgba(4, 10, 30, 0.78)"></div>')
ecran(s, "l-ec", 560, 400, 440, 560, [(s.debut, "stk-reveil-sonne"), (T(26), "cafe-latte-art"), (T(28), "caisse-carte"), (T(29), "ecom-tel-carte")], s.debut, style="panneau")
s.place(780, 680, 2.2)
son(s.debut + 0.1, "alarme-alerte", 0.32, "réveil", d=0.9)
zoom(s, T(26) - 0.1, 540, 960, 1.0, 0.35)
s.j(f'tl.to("#l-nuit", {{ opacity: 0, duration: 0.4 }}, {s.L(T(26))});')
son(T(26), "lumiere", 0.45, "le jour se lève")
etiquette(s, "l-lend", "LE LENDEMAIN", 60, 400, T(26) + 0.05, CIEL, NUIT, 64, -3, fin=T(28) - 0.05)
cam(s, perso("l-lucas", 60, SOL, 560, CIEL, "lucas"))
marche(s, "l-lucas", T(26), T(28), 220)
vivant(s, "l-lucas", T(28))
regarde(s, "l-lucas", T(28), 4, -2)
texte(s, "l-dep", "IL COMMENCE<br>À DÉPENSER", 40, 360, 92, T(28), NUIT, cls="gros bande", rot=-3)
son(T(28), "impact-whoosh", 0.5, "il commence à dépenser")
pose(s, "l-lucas", T(28) + 0.1, 0.2, bd=-70)
zoom_ecran(s, T(29), 560, 400, 440, 560, (540, 960, 1.0, s.fin - 0.25), d=0.24)
paye(T(30), 0.45)
s.ecrire()

# ================================================================ SCÈNE 4 : petit déjeuner payé par Wave, taxi, crédit, livraison… la jauge se vide
s = scene(3, "Un petit déjeuner payé par Wave, une course en taxi, un crédit téléphonique, une livraison parce qu'il est fatigué")
cam(s, '<div class="decor"><div class="ciel" style="background: radial-gradient(ellipse 90% 60% at 50% 35%, #15305e 0%, #0b1220 75%)"></div></div>')
items = [(s.debut, "petit-dej"), (T(33), "oeufs-poele"), (T(34), "cafe-paie-tel"), (T(36), "paiement-tel"),
         (T(37), "taxi-cab"), (T(39), "taxi-nuit"), (T(40), "taxi-voie"),
         (T(41), "texto-parc"), (T(42), "tel-tape"), (T(43), "homme-sms"),
         (T(44), "lit-scroll-food"), (T(45), "livreur-casque"), (T(46), "livreur-pizza"), (T(48), "mange-tele")]
ecran(s, "d-ec", 50, 290, 980, 500, items, s.debut, style="panneau")
cam(s, '<div id="d-jauge" class="jauge" style="left: 50px; top: 815px; width: 980px"><i id="d-j"></i><b>SOLDE</b></div>')
cam(s, perso("d-lucas", 850, 1370, 430, CIEL, "lucas"))
vivant(s, "d-lucas")
regarde(s, "d-lucas", s.debut, -4, -4)
depenses = [("cafe", "Petit déj", "payé par Wave", T(33), 0.78), ("taxi", "Taxi", "une course", T(40), 0.58), ("credit", "Crédit", "téléphone", T(42) + 0.1, 0.4),
            ("livraison", "Livraison", "parce qu’il est fatigué", T(45), 0.22)]
for k, (n, lib, note, g, reste) in enumerate(depenses):
    puce(s, f"d-p{k}", n, lib, 40, 905 + k * 118, g, 52, note)
    paye(g + 0.12, 0.45)
    s.j(f'tl.to("#d-j", {{ scaleX: {reste}, duration: 0.35, ease: "power2.out" }}, {s.L(g + 0.1)});')
    s.j(f'tl.fromTo("#d-jauge", {{ x: 0 }}, {{ keyframes: [{{ x: -10, duration: 0.04 }}, {{ x: 10, duration: 0.04 }}, {{ x: 0, duration: 0.04 }}] }}, {s.L(g + 0.1)});')
    vole(s, f"d-v{k}", round(50 + 980 * reste), 845, round(50 + 980 * reste) + 120, 680, g + 0.15, 3, 0.07, "F", 60, 0.45, sons=False, arc=-120)
    pose(s, "d-lucas", g, 0.15, bd=-60)
    pose(s, "d-lucas", g + 0.45, 0.2, bd=0)
son(T(37), "klaxon", 0.35, "taxi")
son(T(42), "clavier-tel", 0.4, "crédit téléphonique", d=0.8)
son(T(46), "sonnette", 0.45, "livraison")
son(T(33), "grille-poele", 0.28, "petit déjeuner", d=0.9)
# recadrages : on plonge dans l'écran à chaque dépense, on ressort quand l'étiquette tombe
for g_in, g_out in ((s.debut + 0.05, T(33) - 0.15), (T(37) - 0.05, T(40) - 0.15), (T(41) - 0.05, T(42) + 0.1), (T(44) - 0.12, T(45) + 0.15)):
    zoom(s, g_in, 540, 540, 1.1, 0.22, 0.45)
    zoom(s, g_out, 540, 960, 1.0, 0.22, 0.4)
pose(s, "d-lucas", T(48), 0.25, bg=150, bd=-150)
humeur(s, "d-lucas", T(48), "o")
pose(s, "d-lucas", T(49) + 0.3, 0.25, bg=0, bd=0)
s.ecrire()

# ================================================================ SCÈNE 5 : rien de grave, non ? Il ne regarde que les grosses dépenses
s = scene(4, "Rien de grave, non ? Mais dans son application, il ne regarde que les grosses dépenses")
decor_rue(s, "a", jour=True)
cam(s, perso("a-lucas", 270, SOL, 620, CIEL, "lucas"))
vivant(s, "a-lucas")
regarde(s, "a-lucas", s.debut, 4, -3)
bulle(s, "a-b", "Rien de grave !", 400, 540, T(50) - 0.05, fin=T(54) - 0.05, taille=60)
haussement(s, "a-lucas", T(51))
humeur(s, "a-lucas", T(50), "rire")
lignes = "".join(tx(f"a-t{k}", n) for k, n in enumerate(["cafe", "taxi", "credit", "livraison", "cafe", "taxi", "livraison"]))
app = ('<div class="app"><div class="app-tete">Mes dépenses</div>'
       '<div class="app-filtre"><span id="a-f1" class="on">Tout</span><span id="a-f2">Grosses dépenses</span></div>'
       f'<div id="a-liste">{lignes}</div><div id="a-vide" class="app-vide" style="opacity: 0"><b>Aucune grosse dépense</b><span>Tout va bien…</span></div></div>')
telephone(s, "a-tel", 570, 400, 420, 860, app, g=T(57) - 0.1)
zoom(s, T(58), 780, 830, 2.0, 0.3)
tap(s, "a-tap", 860, 556, T(63) - 0.15)
s.j(f'tl.set("#a-f1", {{ className: "" }}, {s.L(T(63) - 0.1)});')
s.j(f'tl.set("#a-f2", {{ className: "on" }}, {s.L(T(63) - 0.1)});')
for k in range(7):
    s.j(f'tl.to("#a-t{k}", {{ opacity: 0, x: 200, filter: "blur(10px)", duration: 0.18, ease: "power2.in" }}, {s.L(T(63) + 0.2 + k * 0.05)});')
son(T(63) + 0.2, "aspiration-air", 0.45, "les petites dépenses disparaissent de la vue")
apparait(s, "#a-vide", T(65), 0.22, 40)
son(T(65), "bonne-reponse", 0.42, "aucune grosse dépense")
zoom(s, T(67) + 0.3, 540, 960, 1.0, 0.3)
pouce(s, "a-lucas", T(67) + 0.35)
humeur(s, "a-lucas", T(67) + 0.35, "content")
s.ecrire()

# ================================================================ SCÈNE 6 : donc il continue ; quelques jours plus tard, son ami propose une sortie
s = scene(5, "Donc il continue sans s'inquiéter ; quelques jours plus tard, son ami lui propose une sortie")
s.bornes = (0, 2160)
decor_rue(s, "o", jour=True, droite=1080)
ecran(s, "o-pan", 1180, 380, 420, 560, [(s.debut, "cafe-cappuccino"), (T(70), "resto-burgers"), (T(71), "sacs-shopping"), (T(72), "taxi-voie")], s.debut, style="panneau", titre_e="")
cam(s, perso("o-lucas", 260, SOL, 560, CIEL, "lucas"))
cam(s, perso("o-hugo", 2000, SOL, 580, PROFOND, "hugo"))
marche(s, "o-lucas", s.debut + 0.05, T(73), 600)
humeur(s, "o-lucas", s.debut, "content")
pano(s, s.debut + 0.1, 900, 960, 1.0, 1.6)
for k, (n, g) in enumerate([("cafe", T(69)), ("taxi", T(70) + 0.1), ("credit", T(71) + 0.15), ("livraison", T(72) + 0.1)]):
    x = 300 + round(600 * (g - s.debut) / (T(73) - s.debut))
    cam(s, f'<div id="o-i{k}" class="ico-bulle" style="left: {x}px; top: 640px; opacity: 0">{icone(n, 90)}</div>')
    s.j(f'tl.fromTo("#o-i{k}", {{ opacity: 0, y: 40, scale: 0.4 }}, {{ opacity: 1, y: -60, scale: 1, duration: 0.25, ease: "back.out(2)", immediateRender: false }}, {s.L(g)});')
    s.j(f'tl.to("#o-i{k}", {{ opacity: 0, y: -160, duration: 0.3 }}, {s.L(g + 0.45)});')
    paye(g, 0.36)
vivant(s, "o-lucas", T(73))
s.add('<div id="o-cal" class="cal-pages" style="left: 330px; top: 390px; opacity: 0">'
      + "".join(f'<div class="page-cal" data-layout-allow-overlap id="o-pg{k}" style="z-index: {10 - k}"><span>JOUR</span><b>{j}</b></div>' for k, j in enumerate(["LUN", "MAR", "MER", "JEU"]))
      + '</div><div id="o-plus" class="gros bande" style="left: 60px; top: 790px; width: 960px; text-align: center; font-size: 72px; color: #0B1220; opacity: 0">QUELQUES JOURS PLUS TARD</div>')
apparait(s, "#o-cal", T(73) - 0.05, 0.2, 80)
for k in range(3):
    s.j(f'tl.to("#o-pg{k}", {{ rotationX: 100, y: -200, opacity: 0, transformOrigin: "50% 0%", duration: 0.2, ease: "power2.in" }}, {s.L(T(73) + 0.25 + k * 0.28)});')
    son(T(73) + 0.25 + k * 0.28, "feuillette", 0.36, "page de calendrier")
claque(s, "#o-plus", T(74))
son(T(74), "impact-tambour", 0.45, "quelques jours plus tard")
cache(s, "#o-cal", T(77) + 0.2)
cache(s, "#o-plus", T(78) - 0.05)
pano(s, T(76), 1300, 960, 1.0, 0.5)
marche(s, "o-hugo", T(76), T(78) + 0.2, -420)
vivant(s, "o-hugo", T(78) + 0.2, decal=1.1)
regarde(s, "o-lucas", T(77), 4)
regarde(s, "o-hugo", T(78), -4)
nom(s, "o-nh", "HUGO, SON AMI", 1420, 600, T(78), PROFOND)
cache(s, "#o-nh", T(80) - 0.1)
bulle(s, "o-b", "On sort ce soir ?", 1110, 470, T(78) + 0.15, queue="d")
parle(s, "o-hugo", T(80), s.fin - 0.2)
pose(s, "o-hugo", T(80), 0.2, bg=130)
pouce(s, "o-lucas", T(82))
humeur(s, "o-lucas", T(82), "rire")
zoom(s, T(80) - 0.1, 1300, 860, 1.12, 0.3)
s.ecrire()

# ================================================================ SCÈNE 7 : Lucas ouvre Wave pour payer… et reste figé devant son solde
s = scene(6, "Lucas ouvre Wave pour payer et reste figé devant son solde")
decor_rue(s, "f", jour=True)
cam(s, perso("f-lucas", 250, SOL + 180, 820, CIEL, "lucas"))
cam(s, perso("f-hugo", 1010, SOL + 120, 700, PROFOND, "hugo"))
vivant(s, "f-lucas", g1=T(90))
vivant(s, "f-hugo", g1=T(90), decal=1.2)
regarde(s, "f-lucas", s.debut, 4, 2)
regarde(s, "f-hugo", s.debut, -4, 2)
app = ('<div class="app"><div class="app-tete">Paiement mobile</div><div id="f-payer" class="app-btn">PAYER LA SORTIE</div>'
       '<div class="app-tete" style="margin-top: 40px">Mon solde</div><div class="app-solde" style="font-size: 110px"><i id="f-cache">• • • •</i>'
       '<i id="f-vrai" style="display: none; color: #FF6B6B">2 300 F</i></div>'
       '<div id="f-alerte" class="app-alerte" style="opacity: 0">Solde insuffisant</div></div>')
telephone(s, "f-tel", 470, 400, 420, 860, app, g=T(84) - 0.1)
pose(s, "f-lucas", T(84) - 0.1, 0.2, bd=-75)
zoom(s, T(85) - 0.05, 680, 830, 2.0, 0.3)
tap(s, "f-tap", 680, 560, T(86) + 0.1)
s.j(f'tl.fromTo("#f-payer", {{ scale: 1 }}, {{ scale: 0.92, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }}, {s.L(T(86) + 0.1)});')
son(T(88), "roulement-suspense", 0.4, "suspense", d=0.9)
s.j(f'tl.to("#f-cache", {{ opacity: 0.2, duration: 0.1, yoyo: true, repeat: 5 }}, {s.L(T(88))});')
s.j(f'tl.set("#f-cache", {{ display: "none" }}, {s.L(T(90))});')
s.j(f'tl.set("#f-vrai", {{ display: "inline" }}, {s.L(T(90))});')
s.j(f'tl.fromTo("#f-vrai", {{ scale: 2 }}, {{ scale: 1, duration: 0.14, ease: "power4.in", immediateRender: false }}, {s.L(T(90))});')
apparait(s, "#f-alerte", T(90) + 0.15, 0.18, 30)
son(T(90), "trailer-impact-2", 0.6, "figé")
son(T(90) + 0.05, "erreur-echec", 0.4, "solde insuffisant")
flash(s, T(90), "#FF6B6B")
secousse(s, T(90) + 0.05, 24)
ralenti_gris(s, T(90) + 0.4)
zoom(s, T(91) - 0.05, 540, 900, 1.0, 0.3)
humeur(s, "f-lucas", T(91), "o")
gouttes(s, "f-g", 330, 520, T(91) + 0.1)
son(T(91), "battements", 0.45, "cœur qui bat", d=1.4)
texte(s, "f-fige", "FIGÉ.", 560, 1050, 140, T(91) + 0.2, CORAIL, rot=-6)
s.add(f'<div id="f-ins" class="plein" style="opacity: 0"><div class="vplein">{video_html("f-ins-v", "choc-mains-tete", s.L(T(93) - 0.05), s.fin - T(93) + 0.1, piste(s))}</div></div>')
s.j(f'tl.set("#f-ins", {{ opacity: 1 }}, {s.L(T(93) - 0.05)});')
s.j(f'tl.fromTo("#f-ins", {{ scale: 1.2 }}, {{ scale: 1, duration: 0.5, immediateRender: false }}, {s.L(T(93) - 0.05)});')
son(T(93) - 0.05, "glitch-rugit", 0.45, "réaction")
s.ecrire()

# ================================================================ SCÈNE 8 : le pire ? Aucun objet important : l'argent est parti dans des dépenses oubliées
s = scene(7, "Le pire ? Il n'a acheté aucun objet important : son argent est parti dans des dépenses oubliées")
decor_chambre(s, "p")
cam(s, perso("p-lucas", 860, SOL, 520, CIEL, "lucas"))
vivant(s, "p-lucas")
humeur(s, "p-lucas", s.debut, "triste")
regarde(s, "p-lucas", s.debut, -4, 0)
texte(s, "p-pire", "LE PIRE ?", 0, 380, 150, T(94), BLANC, w=1080, fin=T(96) + 0.3)
son(T(94), "impact-basse", 0.55, "le pire")
cam(s, f'<div id="p-moto" class="fantome" style="left: 60px; top: 720px; opacity: 0">{moto("p-m", 0, 0, 560, 1)}</div>')
apparait(s, "#p-moto", T(96), 0.25, 60)
son(T(96), "magie", 0.35, "la moto rêvée")
tampon(s, "p-aucun", "AUCUN ACHAT", 110, 820, T(99), -10, 92, CORAIL)
gratte(s, "p-lucas", T(98))
s.j(f'tl.to("#p-moto, #p-aucun", {{ opacity: 0, scale: 0.6, duration: 0.2 }}, {s.L(T(102) - 0.15)});')
lignes = [("cafe", "Petit déj"), ("taxi", "Taxi"), ("credit", "Crédit"), ("livraison", "Livraison"), ("cafe", "Café"), ("taxi", "Taxi"), ("livraison", "Livraison"), ("credit", "Crédit")]
cam(s, '<div id="p-recu" class="recu" style="left: 60px; top: 360px; opacity: 0"><h3>TES DÉPENSES</h3>'
       + "".join(f'<p id="p-l{k}" style="opacity: 0">{icone(n, 48)}<span>{lib}</span><em>oubliée</em></p>' for k, (n, lib) in enumerate(lignes)) + '</div>')
s.j(f'tl.fromTo("#p-recu", {{ opacity: 0, y: -500 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out", immediateRender: false }}, {s.L(T(102))});')
son(T(102), "papier-glisse", 0.45, "le ticket se déroule")
for k in range(len(lignes)):
    g = T(103) + k * 0.42
    s.j(f'tl.fromTo("#p-l{k}", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.14, immediateRender: false }}, {s.L(g)});')
    son(g, tour(["revelation", "pop-click", "clic", "pop-sec"]), 0.38, f"ligne {lignes[k][1]}")
ecran(s, "p-ec", 660, 360, 380, 400, [(T(103), "ticket-imprime"), (T(105), "recus-calcul"), (T(107), "comptage-billets"), (T(109), "calculatrice")], T(103) - 0.1, style="tele")
zoom_ecran(s, T(105) - 0.05, 660, 360, 380, 400, (540, 960, 1.0, T(109) + 0.4), d=0.28)
tampon(s, "p-oub", "OUBLIÉES", 150, 1000, T(112), -12, 110, CORAIL)
humeur(s, "p-lucas", T(112), "o")
s.ecrire()

# ================================================================ SCÈNE 9 : la règle à retenir
s = scene(8, "Voilà pourquoi : ce ne sont pas les grosses dépenses qui te ruinent, mais celles que tu ne remarques plus")
cam(s, '<div class="decor"><div class="ciel" style="background: radial-gradient(ellipse 90% 60% at 50% 40%, #16346a 0%, #0b1220 78%)"></div></div>')
cam(s, perso("v-lucas", 210, SOL, 540, CIEL, "lucas"))
vivant(s, "v-lucas", g1=T(121))
regarde(s, "v-lucas", s.debut, 4, -3)
ecran(s, "v-ec", 420, 380, 620, 760, [(s.debut, "pieces-tombent"), (T(115), "portefeuille-vide"), (T(117), "plus-d-argent"), (T(119), "frustree-compte")], s.debut, style="panneau")
zoom(s, s.debut + 0.1, 730, 760, 1.35, 0.3)
pose(s, "v-lucas", T(116), 0.2, bd=-110)
zoom(s, T(119) - 0.05, 540, 960, 1.0, 0.3)
s.add('<div id="v-regle" class="regle" style="left: 60px; top: 380px; opacity: 0"><h3>À RETENIR</h3>'
      '<p id="v-l1" style="opacity: 0">CE QUI TE RUINE :</p>'
      '<p id="v-l2" class="gris" style="opacity: 0; font-size: 54px">PAS TOUJOURS LES GROSSES DÉPENSES<i id="v-rat" class="rat"></i></p>'
      '<p id="v-l3" class="fort" style="opacity: 0"><span id="v-sur" class="surl"></span><span class="txt">LES PETITES QUE TU NE REMARQUES PLUS</span></p></div>')
apparait(s, "#v-regle", T(121) - 0.05, 0.28, 120, 0.8)
cache(s, "#v-lucas", T(121) + 0.2)
cache(s, "#v-ec", T(121) + 0.2)
son(T(121) - 0.05, "whoosh-tunnel", 0.45, "carte règle")
apparait(s, "#v-l1", T(121) + 0.1, 0.2, 30)
apparait(s, "#v-l2", T(126), 0.2, 30)
pop(T(126), 0.42, "grosses dépenses")
s.j(f'tl.fromTo("#v-rat", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out", immediateRender: false }}, {s.L(T(131) - 0.1)});')
son(T(131) - 0.1, "stylo", 0.45, "rature")
apparait(s, "#v-l3", T(132), 0.22, 30)
impact(T(132), 0.5, "les petites")
s.j(f'tl.fromTo("#v-sur", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power2.out", immediateRender: false }}, {s.L(T(137))});')
son(T(137), "scintille-whoosh", 0.45, "surligné")
s.j(f'tl.to("#v-regle", {{ scale: 1.04, duration: 0.15, yoyo: true, repeat: 1 }}, {s.L(T(139))});')
son(T(139), "cloche-succes", 0.42, "règle complète")
s.ecrire()

# ================================================================ SCÈNE 10 : abonne-toi ; quelle petite dépense te coûte le plus cher ?
s = scene(9, "Abonne-toi à Lefinancier : quelle petite dépense te coûte le plus cher ?")
cam(s, '<div class="decor"><div class="ciel" style="background: radial-gradient(ellipse 80% 60% at 50% 40%, #16346a 0%, #0b1220 80%)"></div></div>')
cam(s, '<div id="z-carte" class="profil" style="left: 140px; top: 330px; opacity: 0"><img src="assets/img/profil.png" alt="" />'
       '<div><b>Lefinancier</b><span>L’argent expliqué simplement</span></div>'
       '<div id="z-btn" class="btn">S’abonner</div><div id="z-ok" class="btn ok" style="opacity: 0">Abonné ✓</div></div>')
apparait(s, "#z-carte", s.debut + 0.05, 0.3, 120)
son(s.debut + 0.05, "swoosh-monte", 0.42, "carte profil")
cam(s, '<svg id="z-souris" class="souris" viewBox="0 0 40 52" style="left: 980px; top: 900px"><path d="M4 2 L4 40 L14 31 L21 48 L28 45 L21 29 L34 29 Z" fill="#fff" stroke="#0B1220" stroke-width="3" stroke-linejoin="round" /></svg>')
s.j(f'tl.to("#z-souris", {{ x: -300, y: -330, duration: 0.4, ease: "power2.inOut" }}, {s.L(T(141) - 0.3)});')
s.j(f'tl.to("#z-souris", {{ scale: 0.8, duration: 0.07, yoyo: true, repeat: 1 }}, {s.L(T(142))});')
s.j(f'tl.set("#z-btn", {{ opacity: 0 }}, {s.L(T(142) + 0.07)});')
s.j(f'tl.set("#z-ok", {{ opacity: 1 }}, {s.L(T(142) + 0.07)});')
son(T(142), "clic-souris", 0.5, "clic s'abonner")
son(T(142) + 0.1, "notif-positive", 0.42, "abonné")
confettis(s, "z-cf", T(142) + 0.1, 720, 620, 18, 340)
s.j(f'tl.to("#z-souris", {{ opacity: 0, duration: 0.15 }}, {s.L(T(143))});')
texte(s, "z-q", "QUELLE PETITE DÉPENSE<br>TE COÛTE LE PLUS CHER ?", 0, 730, 74, T(143), BLANC, w=1080)
for k, n in enumerate(["cafe", "taxi", "credit", "livraison"]):
    x, y = (60, 560)[k % 2], (930, 1110)[k // 2]
    cam(s, f'<div id="z-c{k}" class="choix-ic" style="left: {x}px; top: {y}px; opacity: 0">{icone(n, 96)}<b>{LIBELLES[n]}</b></div>')
    claque(s, f"#z-c{k}", T(143) + 0.25 + k * 0.3, 1.6)
    impact(T(143) + 0.25 + k * 0.3, 0.36, LIBELLES[n])
etiquette(s, "z-com", "DIS-LE EN COMMENTAIRE", 290, 1290, T(147), BLANC, NUIT, 42, -2)
s.ecrire()

# ================================================================ SOUS-TITRES (verticaux)
def ecrire_sous_titres():
    groupes, cur = [], []
    for i, m in enumerate(P.MOTS):
        cur.append(i)
        mot = P.TEXTE[i]
        if mot[-1] in ".,;:!?…" or len(cur) >= 3 or len(" ".join(P.TEXTE[j] for j in cur)) >= 16:
            groupes.append(cur)
            cur = []
    if cur:
        groupes.append(cur)
    html, js = [], []
    for n, g in enumerate(groupes):
        t0 = P.MOTS[g[0]]["start"]
        t1 = P.MOTS[groupes[n + 1][0]]["start"] if n + 1 < len(groupes) else min(FIN - 0.3, P.MOTS[g[-1]]["end"] + 0.5)
        spans = []
        for i in g:
            mot = P.TEXTE[i].replace("_", " ").replace("« ", "").replace(" »", "")
            chiffre = any(c.isdigit() for c in mot)
            spans.append(f'<span id="st-{i}" class="st-mot{" st-n" if chiffre else ""}" style="display: none">{mot}</span>')
            js.append(f'    tl.set("#st-{i}", {{ display: "inline-block" }}, {P.MOTS[i]["start"]});')
            js.append(f'    tl.fromTo("#st-{i}", {{ scale: 1.15 }}, {{ scale: 1, duration: 0.12, ease: "back.out(2)", immediateRender: false }}, {P.MOTS[i]["start"]});')
        html.append(f'    <div id="st-g{n}" class="st-groupe" data-layout-ignore style="opacity: 0"><div class="st-bandeau">{" ".join(spans)}</div></div>')
        js.append(f'    tl.set("#st-g{n}", {{ opacity: 1 }}, {t0});')
        js.append(f'    tl.set("#st-g{n}", {{ opacity: 0 }}, {round(t1 - 0.01, 3)});')
    page = f"""<!-- Sous-titres mot à mot, format vertical (écrit par tools/construire-scenes.py). -->
<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .st-groupe {{ position: absolute; left: 40px; width: 1000px; top: 1395px; text-align: center; }}
    .st-bandeau {{ display: inline-block; background: #EEEEEA; color: #08101E; font-family: "Anton", sans-serif; font-size: 86px;
      line-height: 1; padding: 14px 24px 12px; text-transform: uppercase; box-shadow: 0 18px 50px rgba(0, 0, 0, 0.55); }}
    .st-n {{ color: #0284C7; }}
  </style>
  <div id="root" data-composition-id="sous-titres" data-width="1080" data-height="1920">
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
    return len(groupes)


# ================================================================ SONS GÉNÉRAUX ET MUSIQUES
for k, c in enumerate(COUPES[1:-1], start=1):
    son(c, tour(["souffle-rapide", "souffle-cine", "swoosh-vol", "fouet", "swoosh-accent", "balaie-rapide"]), 0.46, f"transition vers {NOMS[k]}")

MUSIQUES = [  # Mixkit populaires, fichiers à −16,1 / −12,4 / −13,0 LUFS → ≈ −21 LUFS pour une voix à −15
    (0, "partie-1-praise-the-lord", COUPES[4], 0.56),
    (COUPES[4], "partie-2-greed", round(COUPES[8] - COUPES[4], 2), 0.37),
    (COUPES[8], "partie-3-sweet-september", round(FIN - COUPES[8], 2), 0.40),
]
_vus = set()
SONS[:] = [x for x in SONS if x[2] > 0 and not ((x[0], x[1]) in _vus or _vus.add((x[0], x[1])))]

CSS = (ICI / "tools/styles.css").read_text(encoding="utf-8")


def ecrire_index():
    lignes = [f'      <div id="fond" class="clip" data-start="0" data-duration="{FIN}" data-track-index="0"></div>']
    for k, n in enumerate(NOMS):
        d0, d1 = COUPES[k], COUPES[k + 1]
        lignes.append(f'      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{d0}" '
                      f'data-duration="{round(d1 - d0, 2)}" data-track-index="1" data-width="1080" data-height="1920" style="z-index: 10"></div>')
    lignes.append(f'      <div id="titre" class="clip" data-layout-allow-overlap data-start="0" data-duration="{FIN}" data-track-index="2"><b>{TITRE}</b></div>')
    lignes.append(f'      <div id="sous-titres" data-composition-id="sous-titres" data-composition-src="compositions/sous-titres.html" data-start="0" '
                  f'data-duration="{FIN}" data-track-index="3" data-width="1080" data-height="1920" style="z-index: 50"></div>')
    lignes.append('      <audio id="voix" src="assets/audio/voix.mp3" data-start="0" data-track-index="10"></audio>')
    for k, (d0, f, dd, v) in enumerate(MUSIQUES):
        lignes.append(f'      <audio id="musique-{k + 1}" src="assets/music/{f}.mp3" data-start="{d0}" data-duration="{dd}" data-volume="{v}" data-track-index="{11 + k % 2}"></audio>')
    pistes = {}
    for n, (d0, f, v, note, dd) in enumerate(sorted(SONS), start=1):
        p = 30
        while pistes.get(p, -1) > d0 - 0.01:
            p += 1
        dd = round(min(dd, FIN - d0), 2)
        pistes[p] = d0 + dd
        lignes.append(f'      <audio id="sfx-{n:03d}" src="assets/sfx/{f}.mp3" data-start="{d0}" data-duration="{dd}" data-volume="{v}" data-track-index="{p}"></audio><!-- {note} -->')
    corps = "\n".join(lignes)
    page = f"""<!doctype html>
<html lang="fr" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="1080" data-height="1920">
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


n_g = ecrire_sous_titres()
ecrire_index()
print(f"{len(NOMS)} scènes, {len(SONS)} bruitages, {n_g} groupes de sous-titres, durée {FIN} s")
print("coupes :", COUPES)
