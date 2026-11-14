#!/usr/bin/env python3
"""Lefinancier, vidéo 5 : « Pourquoi les riches empruntent ? » (l'effet de levier, Lucas) — vertical natif 1080×1920.
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
TITRE = "Pourquoi les riches empruntent ?"
VOL_SFX = 0.9
SOL = 1290  # ligne du sol (pieds des personnages)


def b(i):
    return round(T(i) - 0.12, 2)


FIN = 63.0
COUPES = [0] + [b(i) for i in (17, 29, 39, 47, 61, 78, 96, 112, 139, 160)] + [FIN]
NOMS = ["s01-hook", "s02-magasin", "s03-banque", "s04-investit", "s05-associe", "s06-calculs", "s07-si-tout-marche", "s08-ralentit", "s09-tableau", "s10-levier", "s11-abonne"]


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


# ================================================================ SCÈNE 1 : HOOK (vraies vidéos, 10 millions… mais il emprunte 5 millions)
s = scene(0, "Hook : Lucas a 10 millions… mais il emprunte quand même 5 millions à la banque")
items = [(0, "billets-liasse"), (T(2), "stk-cash-rotation"), (T(3), "compteuse-billets"), (T(5), "riche-billets"), (T(6), "coffre-fort"),
         (T(7), "tel-banque"), (T(9), "signature"), (T(11), "immo-contrat"), (T(12), "stk-billets-feuillete"), (T(14), "poignee-mains"), (T(16), "billets-tombent")]
cam(s, f'<div id="h-plein" class="plein">{videos(s, "h-v", items)}</div><div class="voile-bas"></div>')
cam(s, f'<div id="h-av" class="avatar" style="left: 60px; top: 640px; opacity: 0">{perso("h-lucas", 130, 470, 480, CIEL, "lucas")}<b>LUCAS</b></div>')
apparait(s, "#h-av", 0.02, 0.2, 40, 0.5)
cache(s, "#h-av", T(2) - 0.05)
son(0.0, "impact-basse", 0.55, "début")
son(0.02, "pop-long", 0.4, "Lucas")
cam(s, f'<div id="h-n" class="gros" style="left: 0; top: 760px; width: 1080px; text-align: center; font-size: 170px; color: {OR}; opacity: 0">0</div>')
claque(s, "#h-n", T(2))
compteur(s, "#h-n", T(2), 0, 10000000, 0.9, " F")
son(T(2), "compteur", 0.4, "10 millions", d=0.9)
son(T(2) + 0.9, "scanner-caisse", 0.45, "10 millions")
texte(s, "h-cpt", "SUR SON COMPTE", 0, 980, 90, T(4), BLANC, w=1080, fin=T(7) - 0.02)
cache(s, "#h-n", T(7) - 0.02, 0.06)
flash(s, T(7))
son(T(7), "glitch-cine", 0.5, "mais")
secousse(s, T(7), 22)
s.j(f'tl.to("#h-plein", {{ filter: "saturate(0.4) brightness(0.6)", duration: 0.1 }}, {s.L(T(7))});')
texte(s, "h-emp", "IL EMPRUNTE", 120, 560, 120, T(9), NUIT, cls="gros bande", rot=-5)
son(T(9), "impact-whoosh", 0.5, "il emprunte")
cam(s, f'<div id="h-5" class="gros" style="left: 0; top: 760px; width: 1080px; text-align: center; font-size: 170px; color: {BLANC}; opacity: 0">+5 000 000 F</div>')
claque(s, "#h-5", T(12))
impact(T(12), 0.55, "5 millions")
tampon(s, "h-banque", "À LA BANQUE", 300, 1000, T(15), -8, 84, CIEL)
billets(s, "h-b", T(12) + 0.1, 14, 1.6)
s.ecrire()

# ================================================================ SCÈNE 2 : un deuxième magasin à Abidjan, sans vider sa réserve
s = scene(1, "Il veut ouvrir un deuxième magasin à Abidjan sans vider sa réserve")
decor_rue(s, "m", jour=True)
cam(s, perso("m-lucas", 330, SOL, 640, CIEL, "lucas"))
vivant(s, "m-lucas")
regarde(s, "m-lucas", s.debut, 3, -4)
bulle_video(s, "m-pen", 620, 560, 250, [(T(19) - 0.2, "boutique-vetements"), (T(22), "caisse-boutique"), (T(24), "epicerie-sourire")], T(18) - 0.1, T(25) - 0.2, (440, 820))
zoom_ecran(s, T(20) - 0.05, 370, 310, 500, 500, (540, 960, 1.0, T(24) + 0.2))
pose(s, "m-lucas", T(19), 0.2, bd=-150)
pose(s, "m-lucas", T(24), 0.2, bd=0)
etiquette(s, "m-2e", "2<sup>e</sup> MAGASIN · ABIDJAN", 380, 380, T(24) + 0.2, OR, NUIT, 58, -3, fin=T(28) + 0.2)
cam(s, coffre("m-coffre", 600, 760))
apparait(s, "#m-coffre", T(25), 0.3, 120)
son(T(25), "verrou", 0.45, "la réserve")
tampon(s, "m-int", "INTACTE", 640, 1090, T(28), -8, 70, CIEL)
pouce(s, "m-lucas", T(27))
humeur(s, "m-lucas", T(27), "rire")
s.ecrire()

# ================================================================ SCÈNE 3 : la banque prête à 7 % sur un an
s = scene(2, "La banque lui prête à 7 % sur un an")
decor_rue(s, "b", jour=True)
cam(s, facade_banque("b-fac", 400, 470, 620))
cam(s, perso("b-lucas", 230, SOL, 600, CIEL, "lucas"))
cam(s, perso("b-ban", 880, SOL, 600, "#1e3a8a", "banquier"))
vivant(s, "b-lucas")
vivant(s, "b-ban", decal=1.2)
regarde(s, "b-lucas", s.debut, 4)
regarde(s, "b-ban", s.debut, -4)
bulle(s, "b-bul", "Prêt accordé !", 520, 420, T(31), queue="d")
parle(s, "b-ban", T(31), T(33))
cam(s, '<div id="b-ctr" class="contrat" style="left: 360px; top: 640px; opacity: 0"><span>CONTRAT DE PRÊT</span><b>5 000 000 F</b><i></i><i></i><i style="width: 60%"></i></div>')
apparait(s, "#b-ctr", T(30), 0.3, 80)
son(T(30), "papier-glisse", 0.4, "contrat")
cam(s, f'<div id="b-taux" class="badge-taux" data-layout-allow-overlap style="left: 320px; top: 360px; opacity: 0"><b>7 %</b><span id="b-an" style="opacity: 0">SUR 1 AN</span></div>')
cache(s, "#b-bul", T(34) - 0.1)
cache(s, "#b-ctr", T(34) - 0.1)
claque(s, "#b-taux", T(34), 2.2)
impact(T(34), 0.55, "7 %")
secousse(s, T(34), 14)
claque(s, "#b-an", T(38), 1.6)
pop(T(38), 0.4, "sur un an")
zoom(s, T(34) - 0.05, 540, 600, 1.15, 0.25)
s.ecrire()

# ================================================================ SCÈNE 4 : il investit les 5 millions dans son commerce
s = scene(3, "Lucas investit les 5 millions dans son commerce")
decor_rue(s, "i", jour=True)
cam(s, '<div class="enseigne" style="left: 540px; top: 400px">LUCAS · MAGASIN 2</div>')
cam(s, '<div class="vitrine-fond" style="left: 520px; top: 480px; width: 520px; height: 680px"></div>')
ecran(s, "i-vit", 560, 520, 440, 600, [(s.debut, "caisse-boutique"), (T(43), "vetements"), (T(45), "caisse-carte")], s.debut + 0.05, style="panneau")
cam(s, perso("i-lucas", 230, SOL, 600, CIEL, "lucas"))
vivant(s, "i-lucas")
regarde(s, "i-lucas", s.debut, 4)
cam(s, '<div id="i-sac" class="sac" style="left: 260px; top: 860px; width: 170px; height: 150px"><b style="font-size: 30px">5 M</b></div>')
pose(s, "i-lucas", T(40), 0.2, bd=-60)
vole(s, "i-v", 340, 900, 780, 820, T(42), 8, 0.07, "F", 80, 0.5)
s.j(f'tl.to("#i-sac", {{ scale: 0.4, opacity: 0, duration: 0.5 }}, {s.L(T(42) + 0.3)});')
etiquette(s, "i-lab", "5 000 000 F → COMMERCE", 60, 380, T(43), OR, NUIT, 54, -3)
zoom_ecran(s, T(44), 560, 520, 440, 600, (540, 960, 1.0, s.fin - 0.35), d=0.3)
s.ecrire()

# ================================================================ SCÈNE 5 : l'associé trouve ça absurde
s = scene(4, "Son associé trouve ça absurde : pourquoi payer des intérêts quand on a déjà l'argent ?")
decor_magasin(s, "a")
cam(s, perso("a-lucas", 280, SOL, 620, CIEL, "lucas"))
cam(s, perso("a-hugo", 1300, SOL, 620, PROFOND, "hugo"))
vivant(s, "a-lucas")
marche(s, "a-hugo", T(47) - 0.1, T(49), -480)
vivant(s, "a-hugo", T(49), decal=1.3)
regarde(s, "a-lucas", T(47), 4)
regarde(s, "a-hugo", T(47), -4)
nom(s, "a-nh", "HUGO, SON ASSOCIÉ", 820, 700, T(48), PROFOND)
cache(s, "#a-nh", T(51) - 0.1)
texte(s, "a-abs", "ABSURDE ?!", 330, 420, 130, T(51), CORAIL, rot=-6, fin=T(52) + 0.6)
impact(T(51), 0.5, "absurde")
bulle(s, "a-b1", "Pourquoi payer<br><em>des intérêts</em>…", 390, 400, T(52) + 0.1, queue="d", fin=T(57) - 0.1)
bulle(s, "a-b2", "…quand on a<br>déjà l’argent ?!", 390, 400, T(57), queue="d")
parle(s, "a-hugo", T(52), T(60))
pose(s, "a-hugo", T(56), 0.2, bg=120)
haussement(s, "a-lucas", T(55))
humeur(s, "a-lucas", T(55), "o")
interrogations(s, "a-q", 120, 640, T(59))
zoom(s, T(52), 760, 820, 1.1, 0.4)
s.ecrire()

# ================================================================ SCÈNE 6 : les calculs de Lucas : 12 % → 600 000
s = scene(5, "Mais Lucas a fait ses calculs : il espère gagner 12 %, soit 600 000 FCFA")
decor_chambre(s, "c")
ecran(s, "c-ec", 720, 360, 290, 470, [(s.debut, "analyse-graphes"), (T(65), "calcul-depenses"), (T(68), "bourse-profit")], s.debut + 0.05)
cam(s, perso("c-lucas", 870, SOL, 480, CIEL, "lucas"))
vivant(s, "c-lucas")
regarde(s, "c-lucas", s.debut, 4, -3)
humeur(s, "c-lucas", T(62), "content")
pouce(s, "c-lucas", T(62))
zoom_ecran(s, T(63) - 0.05, 720, 360, 290, 470, (540, 960, 1.0, T(67) - 0.2), d=0.28)
cam(s, '<div id="c-carte" class="compte" style="left: 70px; top: 380px; width: 620px; opacity: 0"><span>GAIN ESPÉRÉ</span><b id="c-taux" style="font-size: 130px; color: #F2B705">12 %</b></div>')
apparait(s, "#c-carte", T(68) - 0.05, 0.25)
s.j(f'tl.fromTo("#c-taux", {{ opacity: 0, scale: 1.8 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, {s.L(T(70))});')
impact(T(70), 0.5, "12 %")
cam(s, ligne_calc("c-l1", "5 000 000 × 12 %", "", 70, 680, 620, cachee=False))
apparait(s, "#c-l1", T(73), 0.2, 30)
son(T(73), "pop-click", 0.38, "calcul")
cam(s, f'<div id="c-res" class="gros" style="left: 70px; top: 800px; font-size: 120px; color: {OR}; opacity: 0">= <i id="c-res-n" style="font-style: normal">0</i> F</div>')
claque(s, "#c-res", T(76) - 0.05, 1.6)
compteur(s, "#c-res-n", T(76), 0, 600000, 0.7)
son(T(76), "compteur", 0.4, "600 000", d=0.7)
son(T(76) + 0.7, "piece-gagne", 0.5, "600 000")
victoire(s, "c-lucas", T(76) + 0.4, 1)
humeur(s, "c-lucas", T(76) + 0.4, "rire")
s.ecrire()

# ================================================================ SCÈNE 7 : si tout marche : 600 000 − 350 000 = 250 000 (avant frais et impôts)
s = scene(6, "Si tout marche : 350 000 FCFA d'intérêts, 250 000 de différence, avant frais et impôts")
decor_chambre(s, "t")
cam(s, perso("t-lucas", 950, SOL, 480, CIEL, "lucas"))
vivant(s, "t-lucas")
regarde(s, "t-lucas", s.debut, -4, -3)
texte(s, "t-si", "SI TOUT MARCHE…", 60, 360, 84, T(79), NUIT, cls="gros bande", rot=-3)
son(T(79), "swoosh-monte", 0.4, "si tout marche")
cam(s, ligne_calc("t-g", "Gain", "+600 000 F", 60, 500, 760, coul=OR, cachee=False))
apparait(s, "#t-g", T(80), 0.25, 40)
son(T(80), "pop-long", 0.38, "gain")
cam(s, ligne_calc("t-i", "Intérêts (7 %)", "−350 000 F", 60, 640, 760, coul=CORAIL))
apparait(s, "#t-i", T(83) - 0.3, 0.2, 40)
revele(s, "t-i", T(84))
cam(s, f'<div id="t-trait" class="trait-calc" style="left: 60px; top: 780px; width: 760px"></div>')
s.j(f'tl.fromTo("#t-trait", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.3, ease: "power3.out", immediateRender: true }}, {s.L(T(88))});')
cam(s, ligne_calc("t-d", "Différence", "+250 000 F", 60, 810, 760, coul=CIEL, taille=84))
apparait(s, "#t-d", T(88), 0.2, 40)
revele(s, "t-d", T(89), "piece-gagne")
victoire(s, "t-lucas", T(89) + 0.2, 2)
humeur(s, "t-lucas", T(89) + 0.2, "rire")
confettis(s, "t-cf", T(89) + 0.2, 440, 860, 20, 380)
cam(s, '<div id="t-note" class="note" style="left: 60px; top: 990px; opacity: 0">* avant frais et impôts</div>')
apparait(s, "#t-note", T(92), 0.25, 20)
son(T(92), "notif-indice", 0.38, "avant frais et impôts")
zoom(s, T(89), 440, 860, 1.12, 0.3)
zoom(s, T(92) - 0.1, 440, 900, 1.2, 0.4)
s.ecrire()

# ================================================================ SCÈNE 8 : les clients se font attendre, la mensualité ne ralentit pas
s = scene(7, "Sauf que les clients se font attendre : les ventes ralentissent, la mensualité non")
decor_magasin(s, "r")
cam(s, '<div id="r-horloge" class="horloge" style="left: 840px; top: 380px"><i id="r-ah" class="aig h"></i><i id="r-am" class="aig m"></i></div>')
cam(s, '<div class="comptoir" style="left: 80px; top: 1040px; width: 620px"></div>')
cam(s, perso("r-lucas", 390, 1120, 560, CIEL, "lucas"))
vivant(s, "r-lucas")
humeur(s, "r-lucas", s.debut, "neutre")
regarde(s, "r-lucas", s.debut, 3, -2)
ecran(s, "r-tv", 60, 360, 300, 480, [(s.debut, "resto-vide-lumiere"), (T(102), "inquiet-homme"), (T(106), "graphe-perte")], s.debut + 0.05)
zoom_ecran(s, T(98), 60, 360, 300, 480, (540, 960, 1.0, T(102) - 0.1), d=0.28)
s.j(f'tl.to("#r-am", {{ rotation: 1080, duration: 1.6, ease: "power1.inOut" }}, {s.L(T(100))});')
s.j(f'tl.to("#r-ah", {{ rotation: 90, duration: 1.6, ease: "power1.inOut" }}, {s.L(T(100))});')
son(T(100), "tic-tac", 0.45, "les clients se font attendre", d=1.5)
gratte(s, "r-lucas", T(102))
humeur(s, "r-lucas", T(102), "triste")
cam(s, '<div id="r-ventes" class="ventes" style="left: 420px; top: 560px; opacity: 0"><span>VENTES</span>'
       + "".join(f'<i id="r-bv{k}" style="height: {h}px"></i>' for k, h in enumerate((180, 160, 120, 80, 45))) + '</div>')
apparait(s, "#r-ventes", T(103), 0.25, 60)
for k, (h, f) in enumerate(((220, 1), (200, 0.85), (150, 0.6), (100, 0.4), (60, 0.25))):
    s.j(f'tl.fromTo("#r-bv{k}", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.25, ease: "power2.out", immediateRender: true }}, {s.L(T(104) + k * 0.12)});')
son(T(105), "erreur-echec", 0.4, "les ventes ralentissent")
cam(s, '<div id="r-mens" class="compte" style="left: 420px; top: 880px; width: 600px; opacity: 0"><span>MENSUALITÉ DU PRÊT</span><b style="font-size: 64px">À PAYER · CHAQUE MOIS</b></div>')
apparait(s, "#r-mens", T(107), 0.25, 60)
son(T(107), "notif-indice", 0.42, "la mensualité")
tampon(s, "r-tamp", "NE RALENTIT PAS", 470, 1070, T(110), -6, 64, CORAIL)
gouttes(s, "r-g", 430, 600, T(110))
s.ecrire()

# ================================================================ SCÈNE 9 : le tableau : 4 % → 200 000, −350 000, perte 150 000
s = scene(8, "Lucas ouvre son tableau : à 4 %, il gagne 200 000 mais doit 350 000 d'intérêts : il perd 150 000")
decor_chambre(s, "x")
cam(s, perso("x-lucas", 880, SOL, 400, CIEL, "lucas"))
vivant(s, "x-lucas")
humeur(s, "x-lucas", s.debut, "neutre")
regarde(s, "x-lucas", s.debut, -4, -4)
cam(s, '<div id="x-tab" class="tableur" style="left: 50px; top: 350px; width: 980px; height: 600px; opacity: 0"><div class="tab-tete"><i></i><i></i><i></i><span>Tableau de Lucas · scénario prudent</span></div></div>')
s.j(f'tl.fromTo("#x-tab", {{ opacity: 0, scale: 0.6, y: 120 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.35, ease: "back.out(1.6)", immediateRender: false }}, {s.L(T(113))});')
son(T(113), "swoosh-monte", 0.45, "le tableau s'ouvre")
LIG = [("x-r", "Rendement", "4 %", OR, T(122)), ("x-g", "Gain", "+200 000 F", BLANC, T(126)), ("x-i", "Intérêts", "−350 000 F", CORAIL, T(130))]
for k, (lid, lab, val, coul, g) in enumerate(LIG):
    cam(s, ligne_calc(lid, lab, val, 90, 450 + k * 120, 900, coul=coul))
    apparait(s, f"#{lid}", T(113) + 0.3 + k * 0.08, 0.2, 30)
    revele(s, lid, g)
cam(s, '<div id="x-12" class="barre-12" style="left: 650px; top: 455px; opacity: 0">12 %</div>')
s.j(f'tl.fromTo("#x-12", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15, immediateRender: false }}, {s.L(T(116))});')
s.j(f'tl.to("#x-12", {{ opacity: 0, duration: 0.15 }}, {s.L(T(122) - 0.1)});')
cam(s, '<div id="x-12-r" class="rature" style="left: 640px; top: 500px; width: 230px"></div>')
s.j(f'tl.fromTo("#x-12-r", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.18, ease: "power2.out", immediateRender: true }}, {s.L(T(119))});')
s.j(f'tl.to("#x-12-r", {{ opacity: 0, duration: 0.15 }}, {s.L(T(122) - 0.1)});')
son(T(119), "stylo", 0.4, "12 % barré")
cam(s, f'<div id="x-trait" class="trait-calc" style="left: 90px; top: 800px; width: 900px"></div>')
s.j(f'tl.fromTo("#x-trait", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.3, immediateRender: true }}, {s.L(T(133) - 0.3)});')
cam(s, ligne_calc("x-p", "Résultat", "−150 000 F", 90, 820, 900, coul=CORAIL, taille=84))
apparait(s, "#x-p", T(133) - 0.2, 0.2, 30)
revele(s, "x-p", T(134), "erreur-echec")
tampon(s, "x-perte", "PERTE", 700, 345, T(134) + 0.15, -10, 80, CORAIL)
cam(s, '<div id="x-note" class="note" style="left: 60px; top: 975px; opacity: 0">… sans compter les frais</div>')
apparait(s, "#x-note", T(135), 0.25, 20)
panique(s, "x-lucas", T(134), 1.0)
humeur(s, "x-lucas", T(132), "o")
gouttes(s, "x-g2", 900, 900, T(134))
zoom(s, T(122) - 0.1, 540, 700, 1.06, 0.3)
zoom(s, T(134) - 0.1, 540, 820, 1.1, 0.3)
zoom(s, T(135) + 0.3, 540, 960, 1.0, 0.4)
s.ecrire()

# ================================================================ SCÈNE 10 : l'effet de levier (le levier qui soulève, puis qui retombe)
s = scene(9, "Voilà l'effet de levier : l'argent emprunté pour gagner davantage ; si le rendement baisse, la dette reste entière")
cam(s, '<div class="decor"><div class="ciel" style="background: radial-gradient(ellipse 80% 60% at 50% 45%, #16346a 0%, #0b1220 80%)"></div>'
       f'<div class="sol" style="top: {SOL}px"></div></div>')
texte(s, "l-tit", "L’EFFET DE LEVIER", 0, 360, 110, T(140), BLANC, w=1080)
son(T(140), "impact-futur", 0.5, "effet de levier")
ecran(s, "l-ec", 720, 520, 290, 400, [(s.debut, "bourse-profit"), (T(151), "bourse-baisse"), (T(155), "graphe-perte")], s.debut + 0.05, style="panneau")
cam(s, '<svg id="l-pivot" class="pivot" viewBox="0 0 200 160" style="left: 300px; top: 1130px"><path d="M100 6 L190 156 L10 156 Z" fill="#38BDF8" stroke="#0B1220" stroke-width="10" stroke-linejoin="round" /></svg>')
cam(s, '<div id="l-plan" class="planche" style="left: 60px; top: 1110px; width: 680px"></div>')
cam(s, '<div id="l-emp" class="bloc" style="left: 70px; top: 960px; opacity: 0"><b>5 M</b><span>EMPRUNTÉS</span></div>')
cam(s, '<div id="l-gain" class="pile-gain" style="left: 520px; top: 830px; opacity: 0">' + "".join(f'<i id="l-p{k}"></i>' for k in range(6)) + '<span>GAIN</span></div>')
cam(s, '<div id="l-dette" class="bloc dette" data-layout-allow-overlap style="left: 60px; top: 500px; opacity: 0"><b>DETTE</b><span>5 000 000 F</span></div>')
s.j('tl.set("#l-plan", { rotation: 0, transformOrigin: "50% 50%" }, 0);')
apparait(s, "#l-emp", T(144), 0.3, -120)
son(T(144), "marteau", 0.45, "argent emprunté")
s.j(f'tl.to(["#l-plan", "#l-emp", "#l-gain"], {{ rotation: -9, transformOrigin: "400px 50%", duration: 0.5, ease: "back.out(1.6)" }}, {s.L(T(146))});')
s.j(f'tl.set("#l-gain", {{ opacity: 1 }}, {s.L(T(146))});')
for k in range(6):
    claque(s, f"#l-p{k}", T(146) + 0.1 + k * 0.18, 1.6)
    son(T(146) + 0.1 + k * 0.18, tour(["piece-gagne", "pieces-2"]), 0.3, "le gain monte")
etiquette(s, "l-plus", "GAGNER DAVANTAGE", 500, 720, T(149), OR, NUIT, 46, -4)
# mais si le rendement baisse : la pile fond, la dette tombe
s.j(f'tl.to(["#l-p5", "#l-p4", "#l-p3", "#l-p2"], {{ opacity: 0, scale: 0.4, duration: 0.15, stagger: 0.1 }}, {s.L(T(155))});')
s.j(f'tl.to("#l-plus", {{ opacity: 0, duration: 0.2 }}, {s.L(T(152))});')
son(T(155), "erreur-echec", 0.45, "le rendement baisse")
s.j(f'tl.to(["#l-plan", "#l-emp", "#l-gain"], {{ rotation: 10, transformOrigin: "400px 50%", duration: 0.35, ease: "power3.in" }}, {s.L(T(157) - 0.1)});')
s.j(f'tl.fromTo("#l-dette", {{ opacity: 0, y: -400 }}, {{ opacity: 1, y: 440, duration: 0.4, ease: "power3.in", immediateRender: false }}, {s.L(T(157) - 0.3)});')
son(T(157), "impact-basse", 0.6, "la dette tombe")
secousse(s, T(157) + 0.1, 26)
tampon(s, "l-ent", "RESTE ENTIÈRE", 380, 1000, T(159), -8, 72, CORAIL)
zoom_ecran(s, T(152), 720, 520, 290, 400, (540, 960, 1.0, T(155) - 0.05), d=0.25)
zoom(s, T(157), 400, 1000, 1.15, 0.3)
s.ecrire()

# ================================================================ SCÈNE 11 : abonne-toi ; tu aurais pris ce risque ?
s = scene(10, "Abonne-toi à Lefinancier : tu aurais pris ce risque ?")
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
cam(s, perso("f-lucas", 250, SOL, 420, CIEL, "lucas"))
cam(s, perso("f-hugo", 830, SOL, 420, PROFOND, "hugo"))
for p, g in (("f-lucas", T(163) - 0.3), ("f-hugo", T(163) - 0.2)):
    apparait(s, f"#{p}", g, 0.25, 100, 0.6)
    vivant(s, p, g + 0.2)
texte(s, "f-q", "TU AURAIS PRIS CE RISQUE ?", 0, 680, 74, T(163), BLANC, w=1080)
cam(s, f'<div id="f-c1" class="choix" style="left: 70px; top: 790px; opacity: 0">OUI</div>'
       f'<div id="f-c2" class="choix c2" style="left: 560px; top: 790px; opacity: 0">NON</div>')
claque(s, "#f-c1", T(165), 1.6)
claque(s, "#f-c2", T(166), 1.6)
impact(T(165), 0.42, "oui")
impact(T(166), 0.42, "non")
pose(s, "f-lucas", T(165), 0.2, bd=-150)
pose(s, "f-hugo", T(166), 0.2, bg=150)
etiquette(s, "f-com", "DIS-LE EN COMMENTAIRE", 300, 1180, T(167) + 0.2, BLANC, NUIT, 42, -2)
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

MUSIQUES = [  # fichiers à −17,1 / −17,1 / −18,8 LUFS → ≈ −21 LUFS pour une voix à −15
    (0, "partie-1-lord-knows", COUPES[4], 0.63),
    (COUPES[4], "partie-2-trap-hamza", round(COUPES[7] - COUPES[4], 2), 0.63),
    (COUPES[7], "partie-3-solution", round(FIN - COUPES[7], 2), 0.74),
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
