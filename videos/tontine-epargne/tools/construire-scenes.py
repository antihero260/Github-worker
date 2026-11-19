#!/usr/bin/env python3
"""Lefinancier, vidéo 4 : « Tontine ou compte épargne ? » — PREMIÈRE VIDÉO EN VERTICAL NATIF (1080×1920).

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
TITRE = "Tontine ou compte épargne ?"
VOL_SFX = 0.9
SOL = 1290  # ligne du sol (pieds des personnages)


def b(i):
    return round(T(i) - 0.12, 2)


FIN = 62.6
COUPES = [0] + [b(i) for i in (19, 43, 56, 83, 109, 125, 145, 160)] + [FIN]
NOMS = ["s01-hook", "s02-tontine", "s03-moto", "s04-galere", "s05-emma", "s06-versements", "s07-zero", "s08-bilan", "s09-abonne"]


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
            visage = '<rect x="30" y="60" width="40" height="7" rx="3.5" fill="rgba(11,18,32,0.25)" />'
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
        cam(s, f'<div id="{bid}-{k}" class="billet" data-layout-allow-overlap style="left: {x}px; top: {y0}px; opacity: 0"><b>10 000</b><span>FRANCS CFA</span></div>')
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
    cam(s, f'<div id="{tid}" class="tampon" style="left: {x}px; top: {y}px; font-size: {taille}px; color: {coul}; border-color: {coul}; transform: rotate({rot}deg); opacity: 0">{txt}</div>')
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


# ================================================================ SCÈNE 1 : HOOK (vraies vidéos plein cadre, une par mot)
s = scene(0, "Hook : 250 000 FCFA d'un coup… 9 mois plus tard il vend son téléphone")
items = [(0, "billets-liasse"), (T(1), "compteuse-billets"), (T(2), "stk-cash-rotation"), (T(2) + 0.37, "stk-billets-100"), (T(3), "billets-tombent"),
         (T(3) + 0.37, "stk-billets-feuillete"), (T(4), "plus-d-argent"), (T(5), "portefeuille-plein"), (T(6), "stk-horloge-approche"),
         (T(8), "horloge-temps"), (T(10), "myst-sablier")]
cam(s, f'<div id="h-plein" class="plein">{videos(s, "h-v", items, T(11))}</div><div class="voile-bas"></div>')
# Tom présenté dès le premier mot
cam(s, f'<div id="h-tom" class="avatar" style="left: 60px; top: 640px; opacity: 0">{perso("h-tomp", 130, 470, 480, CIEL, "tom")}<b>TOM</b></div>')
apparait(s, "#h-tom", 0.02, 0.2, 40, 0.5)
son(0.0, "impact-basse", 0.55, "début")
son(0.02, "pop-long", 0.4, "Tom")
cache(s, "#h-tom", T(2) - 0.05)
# 250 000 FCFA
cam(s, f'<div id="h-n" class="gros" style="left: 0; top: 760px; width: 1080px; text-align: center; font-size: 230px; color: {OR}; opacity: 0">0</div>')
claque(s, "#h-n", T(2))
compteur(s, "#h-n", T(2), 0, 250000, 0.75)
son(T(2), "compteur", 0.4, "compteur", d=0.8)
son(T(2) + 0.75, "scanner-caisse", 0.45, "250 000")
texte(s, "h-f", "FCFA", 0, 1000, 130, T(3), BLANC, w=1080)
impact(T(3), 0.5, "FCFA")
billets(s, "h-b", T(2) + 0.2, 18, 1.7)
texte(s, "h-coup", "D’UN COUP", 120, 560, 120, T(4), NUIT, cls="gros bande", rot=-6)
son(T(4), "impact-whoosh", 0.5, "d'un coup")
for sel in ("#h-n", "#h-f", "#h-coup"):
    cache(s, sel, T(6) - 0.02, 0.06)
# MAIS : glitch, image qui perd ses couleurs, calendrier qui défile 1 → 9 mois
flash(s, T(6))
son(T(6), "glitch-cine", 0.5, "mais")
s.j(f'tl.to("#h-plein", {{ filter: "grayscale(1) brightness(0.55)", duration: 0.1 }}, {s.L(T(6))});')
secousse(s, T(6), 22)
cam(s, f'<div id="h-cal" class="calendrier" style="left: 290px; top: 640px; opacity: 0"><span>MOIS</span><b id="h-cal-n">1</b></div>')
claque(s, "#h-cal", T(7), 1.6)
compteur(s, "#h-cal-n", T(7), 1, 9, 0.75)
son(T(7), "tic-tac", 0.45, "les mois défilent", d=0.9)
texte(s, "h-tard", "PLUS TARD", 0, 1060, 120, T(9), BLANC, w=1080)
son(T(9), "impact-tambour", 0.45, "plus tard")
# Plan dessiné : Tom vend son téléphone à un acheteur, dans la rue
cam(s, '<div id="h-rue" style="position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; opacity: 0">')
decor_rue(s, "h")
cam(s, perso("h-tom2", 360, SOL, 640, CIEL, "tom"))
cam(s, perso("h-ach", 830, SOL, 600, "#1e3a8a", "hugo"))
mx, my = main_d(360, SOL, 640, -78)
cam(s, f'<div id="h-tel" class="mini-tel" style="left: {mx - 40}px; top: {my - 70}px"></div>')
cam(s, '</div>')
s.j(f'tl.fromTo("#h-rue", {{ opacity: 0, y: 300 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: "power3.out", immediateRender: false }}, {s.L(T(11))});')
son(T(11), "swoosh-vitesse", 0.45, "plan de la rue")
vivant(s, "h-tom2", T(11))
vivant(s, "h-ach", T(11), decal=1.2)
humeur(s, "h-tom2", T(11), "triste")
regarde(s, "h-tom2", T(11), 3)
regarde(s, "h-ach", T(11), -3)
pose(s, "h-tom2", T(11), 0.01, bd=-78)
pose(s, "h-ach", T(13), 0.2, bg=60)
s.j(f'tl.to("#h-tel", {{ x: 250, y: 30, duration: 0.35, ease: "power2.inOut" }}, {s.L(T(14))});')
son(T(14), "swoosh-court", 0.4, "il tend le téléphone")
tampon(s, "h-vendu", "VENDU", 600, 760, T(14) + 0.3, -12, 92)
vole(s, "h-pay", 800, 1000, 470, 1030, T(15), 3, 0.08, "F", 70)
bulle(s, "h-bul", "C’est pour ma <em>tontine</em>…", 70, 560, T(16), queue="g", w=560)
zoom(s, T(18), 360, 900, 1.45, 0.3)
son(T(18), "impact-basse", 0.5, "tontine")
s.ecrire()

# ================================================================ SCÈNE 2 : la moto, l'ami, la tontine de 10 (la caméra descend vers le cercle)
s = scene(1, "Il veut une moto, un ami lui propose une tontine de 10 personnes à 25 000 F")
decor_rue(s, "t")
cam(s, perso("t-tom", 330, SOL, 640, CIEL, "tom", lunettes=False))
cam(s, perso("t-hugo", 1290, SOL, 620, PROFOND, "hugo"))
vivant(s, "t-tom")
vivant(s, "t-hugo", T(28), decal=1.3)
humeur(s, "t-tom", s.debut, "content")
regarde(s, "t-tom", s.debut, 2, -3)
bulle_video(s, "t-pen", 600, 560, 250, [(T(20), "moto-accelere"), (T(23), "motos-route"), (T(24) - 0.1, "meca-moto")], T(20), T(26) - 0.15, (430, 820))
zoom_ecran(s, T(22) - 0.05, 350, 310, 500, 500, (540, 960, 1.0, T(24) + 0.2))
texte(s, "t-occ", "MOTO D’OCCASION", 420, 330, 40, T(23), NUIT, cls="gros bande", rot=-4, fin=T(25))
pose(s, "t-tom", T(20), 0.2, bd=-150)
pose(s, "t-tom", T(23), 0.2, bd=0)
etiquette(s, "t-job", "NOUVEAU BOULOT · LUNDI", 120, 560, T(26), OR, NUIT, 50, -4, fin=T(31))
pouce(s, "t-tom", T(27))
saut(s, "t-tom", T(27), 28)
son(T(26), "notif-positive", 0.42, "nouveau boulot")
# Hugo arrive en marchant, la caméra suit
marche(s, "t-hugo", T(28), T(31) - 0.05, -470)
regarde(s, "t-tom", T(28), 4)
regarde(s, "t-hugo", T(28), -4)
nom(s, "t-nh", "HUGO, SON AMI", 820, 690, T(29), PROFOND)
pano(s, T(28), 640, 960, 1.08, 0.6)
bulle(s, "t-bh", "Rejoins notre <em>tontine</em> !", 300, 400, T(31), queue="d", fin=T(35) - 0.2)
parle(s, "t-hugo", T(31), T(34))
s.j(f'tl.fromTo("#t-bh em", {{ color: "#0B1220" }}, {{ color: "{PROFOND}", duration: 0.1, immediateRender: false }}, {s.L(T(33))});')
oui(s, "t-tom", T(33) + 0.1)
humeur(s, "t-tom", T(33), "o")
# la caméra descend vers le cercle des 10 personnes (monde en dessous : y + 1920)
Y = 1920
cam(s, f'<div class="decor" style="left: 0; top: {Y}px"><div class="ciel" style="background: radial-gradient(ellipse 70% 50% at 50% 55%, #16346a 0%, #0b1220 75%)"></div>'
       f'<div class="sol" style="top: {SOL}px"></div></div>')
cx0, cy0 = 540, Y + 930
cam(s, f'<div id="t-caisse" class="caisse" style="left: {cx0 - 150}px; top: {cy0 - 90}px"><b>CAISSE</b><i id="t-cn">0</i></div>')
POS = []
for k in range(10):
    a = math.pi / 2 + k * 2 * math.pi / 10
    px, py = round(cx0 + 440 * math.cos(a)), round(cy0 + 300 * math.sin(a) + 60)
    POS.append((px, py))
ordre = sorted(range(10), key=lambda k: POS[k][1])
for k in ordre:
    px, py = POS[k]
    coul = CIEL if k == 0 else (CLAIR, PROFOND, "#60A5FA", "#1D4ED8")[k % 4]
    cam(s, perso(f"t-p{k}", px, py, 180, coul, "tom" if k == 0 else ("emma", "hugo", "autre")[k % 3]))
pano(s, T(34) - 0.35, 540, Y + 960, 1.0, 0.5)
for k in range(10):
    g = T(35) + k * 0.075
    apparait(s, f"#t-p{k}", g, 0.18, 50, 0.4)
    vivant(s, f"t-p{k}", g + 0.2, decal=0.3 + k * 0.17)
    if k % 2 == 0:
        pop(g, 0.32, f"membre {k + 1}")
nom(s, "t-ntom", "TOM", POS[0][0], POS[0][1] - 205, T(35) + 0.05)
texte(s, "t-10", "10 PERSONNES", 0, Y + 350, 110, T(36), BLANC, w=1080, fin=T(41))
impact(T(36), 0.45, "10 personnes")
for k in range(10):
    px, py = POS[k]
    vole(s, f"t-c{k}", px, py - 120, cx0, cy0, T(38) + k * 0.06, 1, 0, "25 000", 86, 0.45, sons=(k % 3 == 0), arc=-120)
etiquette(s, "t-25", "25 000 F PAR MOIS", 250, Y + 470, T(39), OR, NUIT, 62, -3)
zoom(s, T(41), cx0, cy0 - 40, 1.35, 0.35)
compteur(s, "#t-cn", T(41) + 0.1, 0, 250000, 0.7)
son(T(41) + 0.1, "compteur", 0.4, "la caisse se remplit", d=0.7)
son(T(41) + 0.8, "scanner-caisse", 0.45, "250 000 dans la caisse")
s.ecrire()

# ================================================================ SCÈNE 3 : mois 1, Tom reçoit 250 000, achète la moto, fier comme jamais
s = scene(2, "Premier mois : Tom reçoit 250 000 et achète sa moto, fier comme jamais")
s.bornes = (0, 2160)
decor_rue(s, "m", droite=0)
decor_rue(s, "m2", x0=1080, jour=True, gauche=0)
cam(s, f'<div id="m-caisse" class="caisse" style="left: 560px; top: 990px"><b>CAISSE</b><i>250 000</i></div>')
cam(s, perso("m-tom", 300, SOL, 640, CIEL, "tom"))
vivant(s, "m-tom")
cam(s, f'<div id="m-cal" class="calendrier petit" style="left: 470px; top: 380px; opacity: 0"><span>MOIS</span><b>1</b></div>')
claque(s, "#m-cal", T(43), 1.8)
son(T(43), "page", 0.45, "mois 1")
regarde(s, "m-tom", T(45), 4, 2)
saut(s, "m-tom", T(45), 30)
humeur(s, "m-tom", T(45), "o")
s.j(f'tl.to("#m-caisse", {{ scale: 1.15, duration: 0.1, yoyo: true, repeat: 1 }}, {s.L(T(46))});')
vole(s, "m-v", 700, 1040, 330, 920, T(46), 7, 0.06, "F", 80, 0.45)
cam(s, f'<div id="m-cpt" class="compte" style="left: 70px; top: 450px; opacity: 0"><span>COMPTE DE TOM</span><b>+<i id="m-cn">0</i> F</b></div>')
apparait(s, "#m-cpt", T(47), 0.25)
compteur(s, "#m-cn", T(48) - 0.1, 0, 250000, 0.6)
son(T(48), "piece-gagne", 0.5, "250 000 reçus")
victoire(s, "m-tom", T(48) + 0.2)
humeur(s, "m-tom", T(48), "rire")
cache(s, "#m-cal", T(49) - 0.1)
cache(s, "#m-cpt", T(49) - 0.1)
# il part au garage (à droite) : la caméra suit, l'écran du garage montre les motos
court(s, "m-tom", T(49) - 0.25, T(49) + 0.35, 1180)
pano(s, T(49) - 0.25, 1620, 960, 1.0, 0.55)
cam(s, '<div id="m-ens" class="enseigne" style="left: 1150px; top: 340px">MOTOS D’OCCASION</div>')
ex, ey = ecran(s, "m-ec", 1170, 450, 340, 560, [(T(49), "meca-moto"), (T(50) + 0.35, "moto-wheelie"), (T(51) + 0.3, "motos-route")], T(49) - 0.3, style="panneau")
zoom_ecran(s, T(50), 1170, 450, 340, 560, (1620, 960, 1.0, T(52) - 0.25))
cam(s, moto("m-moto", 1540, 1000, 500))
apparait(s, "#m-moto", T(52) - 0.2, 0.25, 120)
son(T(52), "moto-demarre", 0.5, "la moto démarre")
cam(s, f'<div id="m-sur" style="position: absolute; left: 0; top: 0; width: 1px; height: 1px; opacity: 0">{perso("m-tom2", 1752, 1308, 520, CIEL, "tom", lunettes=True)}</div>')
s.j(f'tl.set("#m-tom", {{ opacity: 0 }}, {s.L(T(52) - 0.2)});')
s.j(f'tl.set("#m-sur", {{ opacity: 1 }}, {s.L(T(52) - 0.2)});')
pose(s, "m-tom2", T(52) - 0.2, 0.01, jg=-32, jd=-22, bd=-72, bg=-64)
vivant(s, "m-tom2", T(52), amp=3)
humeur(s, "m-tom2", T(52), "content")
s.j(f'tl.fromTo("#m-tom2-lun", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.18, ease: "bounce.out", immediateRender: false }}, {s.L(T(53))});')
son(T(53), "scintille", 0.45, "lunettes de soleil")
pose(s, "m-tom2", T(53) + 0.1, 0.18, bg=150, bd=-150)
humeur(s, "m-tom2", T(53) + 0.1, "rire")
cache(s, "#m-ens", T(53))
cache(s, "#m-ec", T(53))
texte(s, "m-fier", "FIER COMME JAMAIS", 1140, 380, 92, T(53) + 0.05, NUIT, cls="gros bande", rot=-5)
confettis(s, "m-cf", T(54), 1750, 760)
zoom(s, T(53) - 0.05, 1700, 900, 1.15, 0.3)
s.j(f'tl.to(["#m-moto", "#m-sur"], {{ x: 60, duration: 0.5, ease: "power2.in" }}, {s.L(T(55))});')
son(T(55), "moto-accelere", 0.38, "il accélère", d=0.9)
s.ecrire()

# ================================================================ SCÈNE 4 : le salaire tarde, le groupe réclame, il vend son téléphone, il évite les appels
s = scene(3, "Le salaire tarde, le groupe réclame, Tom vend son téléphone et évite les appels")
decor_chambre(s, "g")
cam(s, '<div id="g-horloge" class="horloge" style="left: 500px; top: 420px"><i id="g-ah" class="aig h"></i><i id="g-am" class="aig m"></i></div>')
tx, ty = ecran(s, "g-tv", 720, 350, 290, 470, [(s.debut, "portefeuille-vide"), (T(58), "calcul-depenses"), (T(61), "frustree-compte"), (T(62) + 0.3, "inquiet-homme")], s.debut + 0.05)
cam(s, perso("g-tom", 330, SOL, 640, CIEL, "tom"))
vivant(s, "g-tom")
humeur(s, "g-tom", s.debut, "neutre")
regarde(s, "g-tom", s.debut, 4, -2)
cam(s, '<div id="g-notif" class="notif" style="left: 90px; top: 330px; opacity: 0"><b>BANQUE</b><span>Salaire de novembre</span><em><i class="spin" id="g-spin"></i>EN ATTENTE…</em></div>')
apparait(s, "#g-notif", T(57), 0.25, -80, 1)
son(T(57), "notif-indice", 0.45, "notif salaire")
s.j(f'tl.to("#g-spin", {{ rotation: 1440, duration: 3, ease: "none" }}, {s.L(T(57))});')
s.j(f'tl.to("#g-am", {{ rotation: 1440, duration: 1.4, ease: "power1.inOut" }}, {s.L(T(59))});')
s.j(f'tl.to("#g-ah", {{ rotation: 120, duration: 1.4, ease: "power1.inOut" }}, {s.L(T(59))});')
son(T(59), "tic-tac", 0.45, "le temps passe", d=1.4)
gratte(s, "g-tom", T(59))
humeur(s, "g-tom", T(59), "triste")
cache(s, "#g-notif", T(60) + 0.2)
zoom_ecran(s, T(61) - 0.1, 720, 350, 290, 470, (540, 960, 1.0, T(62) + 0.55), d=0.28)
# le groupe réclame : le téléphone de Tom monte, les messages tombent
chat = (f'<div class="chat-tete"><i></i><div><b>Tontine du quartier</b><span>10 membres</span></div></div>'
        + message(s, "g-m1", "Hugo", "Tom, ta cotisation ?", T(64))
        + message(s, "g-m2", "Léa", "On attend tes 25 000 F !", T(66))
        + message(s, "g-m3", "Max", "Tom ???", T(66) + 0.45)
        + message(s, "g-m4", "Hugo", "C’est le tour de Léa ce mois-ci", T(67) - 0.15))
telephone(s, "g-tel", 260, 470, 560, 960, f'<div class="chat">{chat}</div>', T(62) + 0.1)
zoom(s, T(63), 540, 900, 1.14, 0.3)
tremble(s, "g-tom", T(64), 0.8)
gouttes(s, "g-sueur", 380, 760, T(64))
s.j(f'tl.to("#g-tel", {{ y: 1300, opacity: 0, duration: 0.25, ease: "power2.in" }}, {s.L(T(67) + 0.1)});')
zoom(s, T(67) + 0.1, 540, 960, 1.0, 0.25)
# donc il vend son téléphone à un acheteur
cam(s, perso("g-ach", 1300, SOL, 600, "#1e3a8a", "hugo"))
marche(s, "g-ach", T(67), T(69) - 0.05, -470)
vivant(s, "g-ach", T(69))
regarde(s, "g-ach", T(68), -4)
mx, my = main_d(330, SOL, 640, -78)
cam(s, f'<div id="g-mt" class="mini-tel" style="left: {mx - 40}px; top: {my - 70}px; opacity: 0"></div>')
pose(s, "g-tom", T(69), 0.2, bd=-78)
s.j(f'tl.set("#g-mt", {{ opacity: 1 }}, {s.L(T(69) + 0.15)});')
regarde(s, "g-tom", T(69), 4)
s.j(f'tl.to("#g-mt", {{ x: 280, y: 20, duration: 0.35, ease: "power2.inOut" }}, {s.L(T(71))});')
son(T(71), "swoosh-court", 0.4, "il donne son téléphone")
pose(s, "g-ach", T(71) + 0.2, 0.2, bg=60)
tampon(s, "g-vendu", "VENDU", 540, 700, T(71) + 0.4, -10, 86)
cache(s, "#g-vendu", T(76))
vole(s, "g-pay", 830, 1000, 420, 1020, T(73) - 0.2, 3, 0.08, "F", 70)
etiquette(s, "g-coti", "−25 000 F → TONTINE", 150, 520, T(75), OR, NUIT, 56, -3, fin=T(77))
pose(s, "g-tom", T(73), 0.2, bd=0)
s.j(f'tl.to("#g-ach", {{ x: "+=700", duration: 0.5, ease: "power2.in" }}, {s.L(T(76))});')
s.j(f'tl.set("#g-mt", {{ opacity: 0 }}, {s.L(T(76))});')
# il évite les appels
appel(s, "g-a1", "Hugo · Tontine", 520, 400, T(77), T(83) - 0.3)
appel(s, "g-a2", "Léa · Tontine", 520, 590, T(80), T(83) - 0.3)
appel(s, "g-a3", "Max · Tontine", 520, 780, T(82), T(83) - 0.3)
dos(s, "g-tom", T(77) + 0.15)
pose(s, "g-tom", T(78), 0.2, bg=160, bd=-160)
non(s, "g-tom", T(80) + 0.2)
zoom(s, T(79), 540, 900, 1.08, 0.3)
bulle(s, "g-bul", "Je réponds pas…", 90, 530, T(81), queue="d")
s.ecrire()

# ================================================================ SCÈNE 5 : Emma, sa sœur, épargne 25 000 par mois sur un compte à 3,5 %
s = scene(4, "Sa sœur Emma épargne 25 000 par mois sur un compte rémunéré à 3,5 % par an, sans frais")
decor_rue(s, "e", jour=True)
cam(s, perso("e-tom", 190, SOL, 420, CIEL, "tom"))
vivant(s, "e-tom", s.debut, T(86), amp=3)
humeur(s, "e-tom", s.debut, "triste")
cam(s, perso("e-emma", 1350, SOL, 560, CLAIR, "emma"))
marche(s, "e-emma", T(83) - 0.1, T(85) + 0.2, -550)
vivant(s, "e-emma", T(85) + 0.2, decal=1.0)
regarde(s, "e-emma", T(84), -3)
regarde(s, "e-tom", T(84), 4)
nom(s, "e-ne", "EMMA, SA SŒUR", 800, 730, T(85), CLAIR)
cache(s, "#e-ne", T(88) - 0.1)
zoom(s, T(83), 640, 960, 1.08, 0.5)
marche(s, "e-tom", T(86), T(87) + 0.3, -420)
pouce(s, "e-emma", T(86))
humeur(s, "e-emma", T(86), "content")
zoom(s, T(87), 540, 960, 1.0, 0.3)
# le compte épargne (carte) et l'écran vertical où la caméra plonge (vraies vidéos)
cam(s, '<div id="e-cpt" class="compte" style="left: 50px; top: 360px; width: 610px; opacity: 0"><span>COMPTE ÉPARGNE · EMMA</span><b><i id="e-cn">0</i> F</b></div>')
apparait(s, "#e-cpt", T(87) + 0.05, 0.25)
son(T(87) + 0.05, "pop-long", 0.42, "compte épargne")
ecran(s, "e-ec", 710, 340, 300, 440, [(T(87), "tirelire"), (T(89) + 0.1, "bocal-pieces"), (T(92), "pieces-tombent"), (T(96), "tel-banque")], T(87) + 0.1, style="panneau")
zoom_ecran(s, T(88), 710, 340, 300, 440, (540, 960, 1.0, T(90) - 0.05), d=0.3)
# 25 000 chaque mois : les pièces tombent dans le compte
for k, g in enumerate((T(91), T(92), T(93), T(94))):
    ex, ey = main_d(800, SOL, 560, -150)
    vole(s, f"e-p{k}", ex, ey, 360, 470, g, 1, 0, "25 000", 96, 0.4, arc=-200)
compteur(s, "#e-cn", T(91) + 0.4, 0, 100000, 1.2)
pose(s, "e-emma", T(91) - 0.1, 0.18, bd=-150)
pose(s, "e-emma", T(94) + 0.4, 0.18, bd=0)
cam(s, '<div id="e-mois" class="mois" style="left: 50px; top: 590px">' + "".join(f'<b id="e-mo{k}" style="opacity: 0">{m}</b>' for k, m in enumerate(("JAN", "FÉV", "MAR", "AVR"))) + '</div>')
for k, g in enumerate((T(91) + 0.3, T(92) + 0.3, T(93) + 0.3, T(94) + 0.3)):
    claque(s, f"#e-mo{k}", g, 1.6)
# rémunéré à 3,5 % par an
s.j(f'tl.to("#e-cpt", {{ boxShadow: "0 0 90px rgba(56, 189, 248, 0.9)", duration: 0.25, yoyo: true, repeat: 3 }}, {s.L(T(97))});')
son(T(97), "scintille-whoosh", 0.4, "rémunéré")
son(T(99) - 0.6, "riser-synth", 0.38, "avant 3,5 %", d=0.6, sur_pic=False)
cam(s, '<div id="e-taux" class="badge-taux" data-layout-allow-overlap style="left: 130px; top: 330px; opacity: 0"><b>3,5 %</b><span id="e-an" style="opacity: 0">PAR AN</span></div>')
claque(s, "#e-taux", T(99), 2.2)
impact(T(99), 0.55, "3,5 %")
secousse(s, T(99), 16)
claque(s, "#e-an", T(101), 1.6)
pop(T(101), 0.4, "par an")
cache(s, "#e-taux", T(103) - 0.05)
zoom(s, T(99), 380, 560, 1.15, 0.25)
zoom(s, T(103), 540, 960, 1.0, 0.25)
cam(s, f'<div id="e-frais" class="ligne-ok" style="left: 50px; top: 720px; opacity: 0">Frais de tenue : <b>0 F</b><i id="e-ok" style="opacity: 0">✓</i></div>')
apparait(s, "#e-frais", T(104), 0.2, 40)
son(T(104), "pop-click", 0.4, "frais")
claque(s, "#e-ok", T(106), 2)
son(T(106), "coche", 0.5, "coche")
cache(s, "#e-ec", T(108) - 0.1)
cam(s, '<div id="e-banque" class="banque" style="left: 745px; top: 420px; opacity: 0"><i class="toit"></i><b>BANQUE</b><span></span><span></span><span></span></div>')
apparait(s, "#e-banque", T(108) - 0.05, 0.25)
son(T(108), "cloche-boutique", 0.4, "la banque")
acquiesce(s, "e-emma", T(107))
s.ecrire()

# ================================================================ SCÈNE 6 : dix versements (cases mystère) → 250 000 + 4 000 F d'intérêts
s = scene(5, "Après dix versements : 250 000 mis de côté et environ 4 000 F d'intérêts bruts")
decor_rue(s, "v", jour=True)
cam(s, perso("v-emma", 230, SOL, 560, CLAIR, "emma"))
vivant(s, "v-emma")
humeur(s, "v-emma", s.debut, "content")
regarde(s, "v-emma", s.debut, 4, -4)
cases = []
for k in range(10):
    x, y = 70 + (k % 5) * 190, 340 + (k // 5) * 190
    cases.append(f'<div id="v-c{k}" class="case" style="left: {x}px; top: {y}px"><em>{k + 1}</em><span id="v-q{k}">{cadenas_html()}</span>'
                 f'<b id="v-n{k}" style="opacity: 0">25 000</b></div>')
cam(s, "".join(cases))
for k in range(10):
    apparait(s, f"#v-c{k}", s.debut + 0.05 + k * 0.03, 0.18, 40, 0.5)
son(s.debut + 0.1, "verrou", 0.4, "les 10 cases")
texte(s, "v-dix", "10 VERSEMENTS", 400, 720, 92, T(110), BLANC, w=660, entree="monte", fin=T(116))
for k in range(10):
    g = T(110) + 0.05 + k * 0.13
    s.j(f'tl.to("#v-q{k}", {{ opacity: 0, scale: 0.3, duration: 0.1 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#v-n{k}", {{ opacity: 0, scale: 1.8 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "back.out(2)", immediateRender: false }}, {s.L(g + 0.05)});')
    s.j(f'tl.to("#v-c{k}", {{ borderColor: "{OR}", backgroundColor: "#1d2f52", duration: 0.1 }}, {s.L(g)});')
    son(g, tour(["deverrouille", "piece-gagne", "deverrouille-2", "pieces"]), 0.3, f"case {k + 1}")
cam(s, f'<div id="v-tot" class="compte" style="left: 470px; top: 780px; opacity: 0"><span>MIS DE CÔTÉ</span><b><i id="v-tn">0</i> F</b></div>')
apparait(s, "#v-tot", T(116), 0.22)
compteur(s, "#v-tn", T(116), 0, 250000, 0.8)
son(T(117), "scanner-caisse", 0.45, "250 000")
pouce(s, "v-emma", T(117))
# et gagné… ? (carte mystère qui se retourne : vraie vidéo de pièces derrière)
cam(s, f'<div id="v-mys" class="mystere" style="left: 470px; top: 1000px; opacity: 0"><b id="v-mq">?</b>'
       f'<div id="v-mr" class="mys-rev" style="opacity: 0">{videos(s, "v-mv", [(T(121) - 0.05, "pieces-tombent"), (T(123), "piles-or-argent")], sons=False)}'
       f'<div class="mys-txt"><b>+4 000 F</b><span id="v-int" style="opacity: 0">D’INTÉRÊTS</span><em id="v-brut" style="opacity: 0">bruts (avant impôts)</em></div></div></div>')
apparait(s, "#v-mys", T(118), 0.25)
son(T(118), "battement-mystere", 0.4, "carte mystère", d=1.0)
s.j(f'tl.to("#v-mq", {{ scale: 1.25, duration: 0.18, yoyo: true, repeat: 3 }}, {s.L(T(119))});')
son(T(121) - 0.5, "riser-trailer", 0.35, "avant la révélation", d=0.5, sur_pic=False)
s.j(f'tl.to("#v-mys", {{ rotationY: 90, duration: 0.12, ease: "power2.in" }}, {s.L(T(121) - 0.12)});')
s.j(f'tl.set("#v-mq", {{ opacity: 0 }}, {s.L(T(121))});')
s.j(f'tl.set("#v-mr", {{ opacity: 1 }}, {s.L(T(121))});')
s.j(f'tl.to("#v-mys", {{ rotationY: 0, duration: 0.14, ease: "power2.out" }}, {s.L(T(121))});')
son(T(121), "revelation", 0.5, "+4 000 F")
zoom(s, T(121), 735, 1130, 1.45, 0.3)
claque(s, "#v-int", T(123), 1.6)
s.j(f'tl.set("#v-brut", {{ opacity: 1 }}, {s.L(T(124))});')
pop(T(124), 0.38, "bruts")
victoire(s, "v-emma", T(122))
humeur(s, "v-emma", T(122), "rire")
confettis(s, "v-cf", T(121) + 0.1, 735, 1050)
zoom(s, T(124) + 0.2, 540, 960, 1.0, 0.3)
s.ecrire()

# ================================================================ SCÈNE 7 : Tom, zéro intérêt ; c'était son propre argent, reçu en avance ; 9 cotisations à payer
s = scene(6, "Tom : zéro intérêt, c'était son propre argent reçu en avance, il doit encore 9 cotisations")
decor_chambre(s, "z")
cam(s, perso("z-tom", 540, SOL, 600, CIEL, "tom"))
vivant(s, "z-tom")
humeur(s, "z-tom", s.debut, "triste")
regarde(s, "z-tom", s.debut, 0, -4)
s.place(540, 1000, 1.25)
nom(s, "z-n", "TOM", 540, 640, T(125))
cache(s, "#z-n", T(129) - 0.1)
zoom(s, T(126), 540, 960, 1.0, 0.3)
texte(s, "z-0", "0 F", 0, 300, 330, T(129), CORAIL, w=1080, fin=T(131) - 0.1)
son(T(129), "erreur-echec", 0.5, "zéro")
impact(T(129), 0.55, "zéro")
secousse(s, T(129), 24)
texte(s, "z-int", "D’INTÉRÊTS", 0, 660, 90, T(130), BLANC, w=1080, fin=T(131) - 0.1)
haussement(s, "z-tom", T(130))
# les 250 000 se divisent en 10 pièces… qui étaient les siennes
cam(s, f'<div id="z-bloc" class="compte" style="left: 290px; top: 360px; opacity: 0"><span>REÇU AU MOIS 1</span><b>250 000 F</b></div>')
claque(s, "#z-bloc", T(132), 1.6)
son(T(132), "impact-whoosh", 0.45, "250 000")
cache(s, "#z-bloc", T(133) + 0.15, 0.1)
ZP = [(140 + (k % 5) * 200, 420 + (k // 5) * 200) for k in range(10)]
for k, (x, y) in enumerate(ZP):
    cam(s, piece(f"z-p{k}", x, y, f"M{k + 1}", 150))
    s.j(f'tl.fromTo("#z-p{k}", {{ opacity: 0, x: {540 - x}, y: {460 - y}, scale: 0.3 }}, {{ opacity: 1, x: 0, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.6)", immediateRender: false }}, {s.L(T(133) + 0.15 + k * 0.03)});')
son(T(133) + 0.15, "pieces", 0.45, "10 pièces")
texte(s, "z-sien", "SON PROPRE ARGENT", 0, 860, 84, T(135), NUIT, w=1080, cls="gros bande-c", fin=T(140))
pose(s, "z-tom", T(135), 0.2, bd=-150, bg=40)
son(T(135), "impact-basse", 0.45, "son propre argent")
# reçu en avance : flèche du temps qui revient au mois 1
cam(s, f'<div id="z-temps" class="frise" style="left: 90px; top: 360px; opacity: 0"><span>Mois 1</span><i></i><span>Mois 10</span><b id="z-fl">◀</b></div>')
s.j(f'tl.to({json.dumps([f"#z-p{k}" for k in range(10)])}, {{ y: 110, duration: 0.25 }}, {s.L(T(137))});')
apparait(s, "#z-temps", T(137), 0.2, -40)
s.j(f'tl.fromTo("#z-fl", {{ x: 700 }}, {{ x: 0, duration: 0.5, ease: "power2.out", immediateRender: false }}, {s.L(T(138))});')
son(T(137), "rembobine-magie", 0.45, "reçu en avance")
texte(s, "z-av", "EN AVANCE", 560, 470, 70, T(139), NUIT, cls="gros bande", rot=-4, fin=T(140) + 0.05)
gratte(s, "z-tom", T(138))
# il doit encore 9 cotisations : 9 pièces deviennent des cases verrouillées
cache(s, "#z-temps", T(140))
for k in range(1, 10):
    g = T(141) + (k - 1) * 0.1
    x, y = ZP[k]
    cam(s, f'<div id="z-l{k}" class="case dette" style="left: {x - 80}px; top: {y + 30}px; opacity: 0"><em>M{k + 1}</em><span>{cadenas_html()}</span><b>À PAYER</b></div>')
    s.j(f'tl.to("#z-p{k}", {{ opacity: 0, scale: 0.4, duration: 0.08 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#z-l{k}", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power4.in", immediateRender: false }}, {s.L(g)});')
    son(g + 0.1, tour(["verrou", "erreur-clic", "verrou"]), 0.32, f"cotisation {k + 1} à payer")
s.j(f'tl.to("#z-p0", {{ opacity: 0.35, duration: 0.1 }}, {s.L(T(141))});')
texte(s, "z-9", "9 × 25 000 = 225 000 F", 0, 900, 82, T(144), BLANC, w=1080, cls="gros bande-n")
impact(T(144), 0.5, "225 000")
panique(s, "z-tom", T(143), 1.0)
humeur(s, "z-tom", T(143), "o")
gouttes(s, "z-g", 590, 800, T(143))
zoom(s, T(142), 540, 820, 1.12, 0.3)
s.ecrire()

# ================================================================ SCÈNE 8 : bilan (gauche : tontine, plus tôt ; droite : compte, doucement)
s = scene(7, "La tontine donne une grosse somme plus tôt ; le compte fait travailler doucement ton argent")
cam(s, '<div class="moitie" style="left: 0; background: linear-gradient(180deg, #0b1a35, #13305c)"></div>'
       '<div class="moitie" style="left: 540px; background: linear-gradient(180deg, #1d4ed8, #38bdf8)"></div>'
       f'<div class="sol" style="top: {SOL}px"></div><div class="sep"></div>')
cam(s, f'<div class="tete-col" style="left: 0">TONTINE</div><div class="tete-col" style="left: 540px">COMPTE</div>')
cam(s, perso("b-tom", 190, SOL, 340, CIEL, "tom"))
cam(s, perso("b-emma", 890, SOL, 340, CLAIR, "emma"))
vivant(s, "b-tom")
vivant(s, "b-emma", decal=1.1)
ecran(s, "b-e1", 80, 440, 380, 450, [(s.debut, "stk-cash-rotation"), (T(149), "billets-liasse"), (T(151), "compteuse-billets")], s.debut + 0.05, style="panneau")
ecran(s, "b-e2", 620, 440, 380, 450, [(s.debut, "plante-pousse"), (T(156), "arrose-plante"), (T(158), "plantes-poussent")], s.debut + 0.1, style="panneau")
s.j(f'tl.to("#b-e2", {{ opacity: 0.35, duration: 0.15 }}, {s.L(s.debut + 0.35)});')
zoom(s, T(146) - 0.1, 270, 860, 1.25, 0.35)
cam(s, f'<div id="b-sac" class="sac" style="left: 300px; top: 1100px; width: 200px; height: 170px; opacity: 0"><b style="font-size: 36px">250 000 F</b></div>')
claque(s, "#b-sac", T(149), 1.8)
son(T(149), "piece-gagne", 0.45, "grosse somme")
victoire(s, "b-tom", T(149), 1)
humeur(s, "b-tom", T(149), "rire")
etiquette(s, "b-tot", "PLUS TÔT", 110, 920, T(151), OR, NUIT, 64, -4)
son(T(151), "swoosh-vitesse", 0.42, "plus tôt")
# le compte, à droite
s.j(f'tl.to("#b-e2", {{ opacity: 1, duration: 0.15 }}, {s.L(T(153))});')
s.j(f'tl.to("#b-e1", {{ opacity: 0.35, duration: 0.15 }}, {s.L(T(153))});')
pano(s, T(153) - 0.1, 810, 860, 1.25, 0.45)
cam(s, f'<div id="b-pile" class="pile" style="left: 580px; top: 990px">' + "".join(f'<i id="b-pi{k}" style="opacity: 0"></i>' for k in range(6)) + '</div>')
for k in range(6):
    claque(s, f"#b-pi{k}", T(155) + k * 0.35, 1.5)
    son(T(155) + k * 0.35, tour(["piece-gagne", "pieces-2"]), 0.28, "pièce sur la pile")
etiquette(s, "b-dou", "DOUCEMENT", 640, 920, T(157), CIEL, NUIT, 64, 3)
pouce(s, "b-emma", T(156))
humeur(s, "b-emma", T(156), "content")
zoom(s, T(159) - 0.1, 540, 900, 1.0, 0.35)
s.j(f'tl.to(["#b-e1", "#b-e2"], {{ opacity: 1, duration: 0.15 }}, {s.L(T(159))});')
s.ecrire()

# ================================================================ SCÈNE 9 : abonne-toi, tu préfères quoi ?
s = scene(8, "Abonne-toi à Lefinancier : tu préfères quoi ?")
cam(s, '<div class="decor"><div class="ciel" style="background: radial-gradient(ellipse 80% 60% at 50% 40%, #16346a 0%, #0b1220 80%)"></div>'
       f'<div class="sol" style="top: {SOL}px"></div></div>')
cam(s, '<div id="f-carte" class="profil" style="left: 140px; top: 330px; opacity: 0"><img src="assets/img/profil.png" alt="" />'
       '<div><b>Lefinancier</b><span>L’argent expliqué simplement</span></div>'
       '<div id="f-btn" class="btn">S’abonner</div><div id="f-ok" class="btn ok" style="opacity: 0">Abonné ✓</div></div>')
apparait(s, "#f-carte", s.debut + 0.05, 0.3, 120)
son(s.debut + 0.05, "swoosh-monte", 0.42, "carte profil")
cam(s, '<svg id="f-souris" class="souris" viewBox="0 0 40 52" style="left: 980px; top: 900px"><path d="M4 2 L4 40 L14 31 L21 48 L28 45 L21 29 L34 29 Z" fill="#fff" stroke="#0B1220" stroke-width="3" stroke-linejoin="round" /></svg>')
s.j(f'tl.to("#f-souris", {{ x: -270, y: -380, duration: 0.45, ease: "power2.inOut" }}, {s.L(T(161) - 0.4)});')
s.j(f'tl.to("#f-souris", {{ scale: 0.8, duration: 0.07, yoyo: true, repeat: 1 }}, {s.L(T(162))});')
s.j(f'tl.set("#f-btn", {{ opacity: 0 }}, {s.L(T(162) + 0.07)});')
s.j(f'tl.set("#f-ok", {{ opacity: 1 }}, {s.L(T(162) + 0.07)});')
son(T(162), "clic-souris", 0.5, "clic s'abonner")
son(T(162) + 0.1, "notif-positive", 0.42, "abonné")
confettis(s, "f-cf", T(162) + 0.1, 720, 620, 18, 340)
s.j(f'tl.to("#f-souris", {{ opacity: 0, duration: 0.15 }}, {s.L(T(163))});')
cam(s, perso("f-tom", 250, SOL, 420, CIEL, "tom"))
cam(s, perso("f-emma", 830, SOL, 420, CLAIR, "emma"))
for p, g in (("f-tom", T(163)), ("f-emma", T(163) + 0.1)):
    apparait(s, f"#{p}", g, 0.25, 100, 0.6)
    vivant(s, p, g + 0.2)
cam(s, f'<div id="f-c1" class="choix" style="left: 70px; top: 760px; opacity: 0">TONTINE</div>'
       f'<div id="f-c2" class="choix c2" style="left: 560px; top: 760px; opacity: 0">COMPTE</div>'
       f'<div id="f-vs" class="vs" style="left: 470px; top: 770px; opacity: 0">OU</div>')
claque(s, "#f-c1", T(163), 1.6)
claque(s, "#f-c2", T(164), 1.6)
claque(s, "#f-vs", T(164) + 0.15, 2)
impact(T(163), 0.45, "tontine")
impact(T(164), 0.45, "compte")
texte(s, "f-q", "?", 0, 900, 300, T(165), OR, w=1080)
s.j(f'tl.to("#f-q", {{ y: -30, duration: 0.25, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {s.L(T(165) + 0.2)});')
son(T(165), "surprise-cartoon", 0.42, "tu préfères quoi ?")
pose(s, "f-tom", T(163), 0.2, bd=-150)
pose(s, "f-emma", T(164), 0.2, bg=150)
etiquette(s, "f-com", "DIS-LE EN COMMENTAIRE", 300, 1180, T(165) + 0.3, BLANC, NUIT, 42, -2)
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

MUSIQUES = [  # fichiers à −18,1 / −17,1 / −17,1 LUFS → ≈ −21 LUFS pour une voix à −15
    (0, "partie-1-waka-floka-type", COUPES[3], 0.71),
    (COUPES[3], "partie-2-g-eazy-nba-type", round(COUPES[5] - COUPES[3], 2), 0.63),
    (COUPES[5], "partie-3-try-me", round(FIN - COUPES[5], 2), 0.63),
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
