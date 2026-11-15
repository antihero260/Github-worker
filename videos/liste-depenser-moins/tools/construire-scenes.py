#!/usr/bin/env python3
"""Lefinancier, vidéo 8 : « 10 techniques pour dépenser moins » (format liste, compte à rebours 10 → 1, Lucas) — vertical natif 1080×1920.
Demande : « surpasse-toi, qu'on ne puisse pas scroller tellement c'est intéressant ». Fin À RETENIR / À FAIRE.
Aucun chiffre affiché hors des numéros de la liste.
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
TITRE = "10 techniques pour dépenser moins"
VOL_SFX = 0.9
SOL = 1290  # ligne du sol (pieds des personnages)


def b(i):
    return round(T(i) - 0.12, 2)


FIN = 69.0
COUPES = [0] + [b(i) for i in (13, 25, 37, 49, 61, 72, 83, 97, 107, 121, 134, 147, 167)] + [FIN]
NOMS = ["s01-hook", "s02-n10", "s03-n9", "s04-n8", "s05-n7", "s06-n6", "s07-relance", "s08-n5", "s09-n4", "s10-n3", "s11-n2", "s12-n1", "s13-retenir", "s14-abonne"]


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


# ================================================================ ÉLÉMENTS PROPRES À LA VIDÉO 7 (enveloppes, carnet, salaire découpé, carte de fin)
ENV = [("loyer", "LOYER<br>+ FACTURES", CIEL), ("nourriture", "NOURRITURE<br>+ TRANSPORT", CLAIR), ("epargne", "ÉPARGNE", OR), ("loisirs", "LOISIRS", PROFOND)]


def env_mini(eid, x, y, w, coul, label="", op=0, cls=""):
    h = round(w * 0.66)
    return (f'<div id="{eid}" class="env petit {cls}" data-layout-allow-overlap style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; --c: {coul}; '
            f'font-size: {round(w * 0.13)}px; opacity: {op}"><b style="color: {BLANC if coul == PROFOND else NUIT}">{label}</b></div>')


def enveloppe(s, eid, x, y, coul, label, items, g_rev):
    """Grande enveloppe fermée « ? » ; à g_rev, une carte-vidéo sort de l'enveloppe et le nom apparaît."""
    cam(s, f'<div id="{eid}" class="envw" style="left: {x}px; top: {y}px">'
           f'<div id="{eid}-c" class="env-carte">{videos(s, eid + "-v", items)}</div>'
           f'<div class="env" style="--c: {coul}"><i id="{eid}-q" class="q">?</i><b id="{eid}-l" style="opacity: 0; color: {BLANC if coul == PROFOND else NUIT}">{label}</b></div></div>')
    s.j(f'tl.to("#{eid}-c", {{ y: -215, duration: 0.3, ease: "back.out(1.6)" }}, {s.L(g_rev)});')
    s.j(f'tl.to("#{eid}-q", {{ opacity: 0, scale: 0.3, duration: 0.12 }}, {s.L(g_rev)});')
    s.j(f'tl.fromTo("#{eid}-l", {{ opacity: 0, scale: 1.8 }}, {{ opacity: 1, scale: 1, duration: 0.16, ease: "power4.in", immediateRender: false }}, {s.L(g_rev + 0.05)});')
    son(g_rev, "revelation", 0.42, f"enveloppe {eid}")
    son(g_rev + 0.05, "papier-glisse", 0.35, "la carte sort")


def insert(s, iid, f, g, fin, v=0.45):
    """Vraie vidéo plein cadre, par-dessus la scène (coupe sèche)."""
    s.add(f'<div id="{iid}" class="plein" style="opacity: 0"><div class="vplein">{video_html(iid + "-v", f, s.L(g), fin - g + 0.05, piste(s))}</div></div>')
    s.j(f'tl.set("#{iid}", {{ opacity: 1 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{iid}", {{ scale: 1.25 }}, {{ scale: 1, duration: {round(fin - g, 3)}, ease: "power2.out", immediateRender: false }}, {s.L(g)});')
    s.j(f'tl.set("#{iid}", {{ opacity: 0 }}, {s.L(fin)});')
    son(g, tour(["whoosh-cine", "whoosh-stutter", "glitch-mini", "whoosh-metal"]), v, f"insert {f}")


def jauge_hud(s, jid, x, y, w, texte_j, depart=1.0):
    s.add(f'<div id="{jid}" class="jauge" style="left: {x}px; top: {y}px; width: {w}px; opacity: 0; z-index: 20"><i id="{jid}-i"></i><b>{texte_j}</b></div>')
    s.j(f'tl.set("#{jid}-i", {{ scaleX: {depart} }}, 0);')


def vide_jauge(s, jid, g, reste, rouge=False):
    coul = ', background: "linear-gradient(90deg, #b91c1c, #FF6B6B)"' if rouge else ""
    s.j(f'tl.to("#{jid}-i", {{ scaleX: {reste}{coul}, duration: 0.35, ease: "power2.out" }}, {s.L(g)});')
    s.j(f'tl.to("#{jid}", {{ keyframes: [{{ x: -10, duration: 0.04 }}, {{ x: 10, duration: 0.04 }}, {{ x: 0, duration: 0.04 }}] }}, {s.L(g)});')


# ================================================================ ÉLÉMENTS PROPRES À LA VIDÉO 8 (liste « 10 techniques ») : icônes, gros numéro, bande de progression
ICONES.update({
    "trajet": ('<path d="M50 8 C30 8 18 24 18 40 C18 62 50 92 50 92 C50 92 82 62 82 40 C82 24 70 8 50 8 Z" fill="#38BDF8" stroke="#0B1220" stroke-width="6" />'
               '<circle cx="50" cy="40" r="12" fill="#F1F5F9" stroke="#0B1220" stroke-width="5" />'),
    "panier": ('<path d="M12 40 H88 L78 86 H22 Z" fill="#c08a4a" stroke="#0B1220" stroke-width="6" stroke-linejoin="round" />'
               '<path d="M30 40 L44 14 M70 40 L56 14" stroke="#0B1220" stroke-width="6" stroke-linecap="round" />'
               '<circle cx="40" cy="36" r="9" fill="#FF6B6B" stroke="#0B1220" stroke-width="4" /><circle cx="60" cy="34" r="9" fill="#F2B705" stroke="#0B1220" stroke-width="4" />'),
    "bouteille": ('<rect x="38" y="6" width="24" height="12" rx="3" fill="#0B1220" />'
                  '<path d="M36 18 H64 V30 Q74 36 74 48 V86 Q74 94 66 94 H34 Q26 94 26 86 V48 Q26 36 36 30 Z" fill="#7DD3FC" stroke="#0B1220" stroke-width="6" />'
                  '<rect x="29" y="56" width="42" height="16" fill="#38BDF8" />'),
    "marmite": ('<path d="M14 44 H86 V72 Q86 88 70 88 H30 Q14 88 14 72 Z" fill="#94A3B8" stroke="#0B1220" stroke-width="6" />'
                '<rect x="8" y="38" width="84" height="10" rx="5" fill="#0B1220" />'
                '<path d="M36 30 Q40 20 36 12 M52 30 Q56 20 52 12 M68 30 Q72 20 68 12" stroke="#38BDF8" stroke-width="5" fill="none" stroke-linecap="round" />'),
    "ciseaux": ('<rect x="8" y="22" width="64" height="44" rx="8" fill="#38BDF8" stroke="#0B1220" stroke-width="6" /><rect x="8" y="34" width="64" height="8" fill="#0B1220" />'
                '<path d="M60 70 L36 44 M76 56 L44 32" stroke="#FF6B6B" stroke-width="7" stroke-linecap="round" />'
                '<circle cx="66" cy="78" r="10" fill="#F1F5F9" stroke="#0B1220" stroke-width="6" /><circle cx="84" cy="62" r="10" fill="#F1F5F9" stroke="#0B1220" stroke-width="6" />'),
    "echange": ('<path d="M16 38 H72 L58 24 M84 64 H28 L42 78" fill="none" stroke="#0284C7" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" />'),
    "balance": ('<path d="M50 14 V84 M26 86 H74 M18 30 H82" stroke="#0B1220" stroke-width="6" stroke-linecap="round" />'
                '<path d="M18 30 L6 56 H30 Z M82 30 L70 56 H94 Z" fill="#F2B705" stroke="#0B1220" stroke-width="5" stroke-linejoin="round" />'),
    "lune": ('<path d="M62 10 A40 40 0 1 0 90 66 A32 32 0 1 1 62 10 Z" fill="#F2B705" stroke="#0B1220" stroke-width="6" stroke-linejoin="round" />'
             '<circle cx="24" cy="20" r="5" fill="#7DD3FC" /><circle cx="84" cy="22" r="4" fill="#7DD3FC" />'),
    "liste": ('<rect x="20" y="8" width="60" height="84" rx="8" fill="#F1F5F9" stroke="#0B1220" stroke-width="6" />'
              '<path d="M34 30 H68 M34 46 H68 M34 62 H58" stroke="#0B1220" stroke-width="6" stroke-linecap="round" />'
              '<path d="M24 76 L32 84 L46 70" fill="none" stroke="#0284C7" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />'),
    "plafond": ('<rect x="10" y="34" width="80" height="52" rx="10" fill="#0284C7" stroke="#0B1220" stroke-width="6" />'
                '<rect x="60" y="50" width="30" height="18" rx="6" fill="#F2B705" stroke="#0B1220" stroke-width="5" />'
                '<path d="M4 18 H96" stroke="#FF6B6B" stroke-width="9" stroke-dasharray="14 8" />'),
})
NUMS = list(range(10, 0, -1))


def bande(s, actuel, mystere=False):
    """Bande de progression 10 → 1 : numéros passés cochés, numéro en cours en or, la n° 1 cachée « ? »."""
    cases = []
    for k, n in enumerate(NUMS):
        cls = "fait" if n > actuel else ("actuel" if n == actuel else "")
        txt = "?" if (n == 1 and actuel != 1) else str(n)
        cases.append(f'<i id="{s.id}-b{n}" class="case-b {cls}">{txt}</i>')
    s.add(f'<div id="{s.id}-bande" class="bande-num">{"".join(cases)}</div>')
    if actuel and not mystere:
        s.j(f'tl.fromTo("#{s.id}-b{actuel}", {{ scale: 1 }}, {{ scale: 1.35, duration: 0.14, yoyo: true, repeat: 3, immediateRender: false }}, {s.L(s.debut + 0.1)});')
    if mystere:
        s.j(f'tl.fromTo("#{s.id}-b1", {{ scale: 1, rotation: 0 }}, {{ scale: 1.5, rotation: 10, duration: 0.1, yoyo: true, repeat: 9, immediateRender: false }}, {s.L(T(76))});')


def fond_rayons(s, coul="#16346a"):
    cam(s, f'<div class="decor"><div class="ciel" style="background: radial-gradient(ellipse 90% 60% at 50% 45%, {coul} 0%, #0b1220 78%)"></div>'
           f'<i id="{s.id}-ray" class="rayons"></i></div>')
    s.j(f'tl.fromTo("#{s.id}-ray", {{ rotation: 0 }}, {{ rotation: 60, duration: {round(s.fin - s.debut, 2)}, ease: "none" }}, 0);')


def technique(k, num, iN, iP, nom, items, ic, geste, or_=False, fin_scene=True):
    """Une technique : gros numéro qui claque puis devient badge, carte du nom, écran de vraies vidéos, Lucas et son icône."""
    s = scene(k, f"Numéro {num} : {nom}")
    fond_rayons(s, "#4a3a08" if or_ else "#16346a")
    gN = s.debut
    gNom = T(iN + 2)
    ecran(s, f"t{num}-ec", 60, 420, 960, 580, items, gNom - 0.08, style="panneau")
    if or_:
        s.j(f'tl.set("#t{num}-ec", {{ borderColor: "#F2B705" }}, 0);')
    s.add(f'<div id="t{num}-big" class="num-big{" num-or" if or_ else ""}" data-layout-allow-overlap><span>NUMÉRO</span><b>{num}</b></div>')
    s.j(f'tl.fromTo("#t{num}-big", {{ scale: 2.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "power4.in", immediateRender: false }}, {s.L(gN + 0.02)});')
    s.j(f'tl.to("#t{num}-big span", {{ opacity: 0, duration: 0.1 }}, {s.L(gNom - 0.15)});')
    s.j(f'tl.to("#t{num}-big", {{ x: -390, y: -370, scale: 0.3, duration: 0.3, ease: "power3.inOut" }}, {s.L(gNom - 0.15)});')
    son(gN + 0.18, "impact-basse" if not or_ else "trailer-impact", 0.6, f"numéro {num}")
    son(gN + 0.02, tour(["whoosh-cine", "whoosh-fusee", "whoosh-metal", "whoosh-stutter"]), 0.45, "numéro qui arrive")
    son(T(iN + 1), tour(["impact-tambour", "impact-futur", "impact-whoosh"]), 0.45, f"chiffre {num}")
    secousse(s, gN + 0.2, 22)
    flash(s, gN + 0.18, "#F2B705" if or_ else "#ffffff")
    s.place(540, 960, 1.1)
    zoom(s, gNom - 0.15, 540, 960, 1.0, 0.3)
    s.add(f'<div id="t{num}-nom" class="tech-nom{" nom-or" if or_ else ""}" style="left: 60px; top: 1030px; opacity: 0">{nom}</div>')
    claque(s, f"#t{num}-nom", gNom, 1.7)
    son(gNom, tour(["pop-long", "swoosh-accent", "whoosh-pop"]), 0.45, f"nom {nom}")
    s.add(perso(f"t{num}-lucas", 920, 1335, 330, CIEL, "lucas"))
    vivant(s, f"t{num}-lucas")
    regarde(s, f"t{num}-lucas", s.debut, -4, -3)
    s.add(f'<div id="t{num}-ic" class="ico-bulle" style="left: 860px; top: 860px; opacity: 0">{icone(ic, 92)}</div>')
    s.j(f'tl.fromTo("#t{num}-ic", {{ opacity: 0, scale: 0.2, rotation: -40 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.25, ease: "back.out(2.4)", immediateRender: false }}, {s.L(T(iP))});')
    s.j(f'tl.to("#t{num}-ic", {{ y: -14, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {s.L(T(iP) + 0.3)});')
    son(T(iP), tour(["pop-cartoon", "pop-bulle", "pop-click"]), 0.42, f"icône {ic}")
    geste(s, f"t{num}-lucas", T(iP))
    zoom(s, T(iP) - 0.1, 540, 700, 1.12, 0.28)
    pano(s, T(iP) + 0.9, 620, 760, 1.12, 0.5)
    zoom(s, s.fin - 0.55, 540, 960, 1.0, 0.25)
    bande(s, num)
    if fin_scene:
        s.ecrire()
    return s


# ================================================================ SCÈNE 1 : HOOK (0 → 4,8 s) : une vraie vidéo par mot, puis la mosaïque des 10 techniques
s = scene(0, "Hook : 10 techniques pour dépenser moins sans te priver. Lucas les teste cette semaine.")
items = [(0, "billets-tombent"), (T(1), "compteuse-machine"), (T(2), "sacs-shopping"), (T(3), "plus-argent-poches"), (T(4), "portefeuille-vide-2"),
         (T(5), "stk-cash-rotation"), (T(6), "poings-joie"), (T(7), "homme-tel-joie")]
cam(s, f'<div id="h-plein" class="plein">{videos(s, "h-v", items, fin=T(8), son_v=0.42)}</div><div class="voile-bas"></div>')
son(0.0, "trailer-impact", 0.62, "début")
son(0.02, "whoosh-cine", 0.45, "début")
cam(s, '<div id="h-10" class="num-big hook-10" data-layout-allow-overlap style="opacity: 0"><b>10</b><span>TECHNIQUES</span></div>')
claque(s, "#h-10", 0.02, 2.4)
secousse(s, 0.18, 24)
cache(s, "#h-10", T(2) - 0.03, 0.08)
texte(s, "h-t2", "POUR DÉPENSER<br>MOINS", 0, 660, 150, T(2), BLANC, w=1080, fin=T(5) - 0.03)
son(T(3), "glitch-cine", 0.45, "dépenser moins")
texte(s, "h-t3", "SANS TE PRIVER", 90, 760, 110, T(5), NUIT, cls="gros bande", rot=-3, fin=T(8) - 0.03)
impact(T(5), 0.55, "sans te priver")
flash(s, T(8))
premiers = ["pas-rue", "marche-fruits", "bouteille-parc", "couple-cuisine", "montre-notifs", "perceuse-bois", "prix-etiquettes", "lune-monte", "todo-liste", "grillade-rue"]
tuiles = []
for k, (n, f) in enumerate(zip(NUMS, premiers)):
    x, y = (30, 550)[k % 2], 330 + (k // 2) * 205
    tuiles.append(f'<div id="h-u{k}" class="tuile" style="left: {x}px; top: {y}px; opacity: 0">{video_html(f"h-u{k}-v", f, s.L(T(8)), s.fin - T(8) + 0.1, piste(s))}'
                  f'<b>{"?" if n == 1 else n}</b></div>')
cam(s, f'<div id="h-mos" class="plein" style="background: #0B1220; opacity: 0">{"".join(tuiles)}</div>')
s.j(f'tl.set("#h-mos", {{ opacity: 1 }}, {s.L(T(8))});')
for k in range(10):
    g = T(8) + k * 0.1
    s.j(f'tl.fromTo("#h-u{k}", {{ opacity: 0, scale: 0.3, rotation: {(-12, 12)[k % 2]} }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, {s.L(g)});')
    son(g, tour(["pop-sec", "pop-click", "balaie-petit", "pop-cartoon"]), 0.34, f"tuile {k}")
cam(s, f'<div id="h-av" class="avatar" style="left: 455px; top: 760px; opacity: 0">{perso("h-lucas", 85, 300, 300, CIEL, "lucas")}<b>LUCAS</b></div>')
apparait(s, "#h-av", T(8) + 0.2, 0.25, 60, 0.4)
son(T(8) + 0.2, "magie", 0.45, "Lucas")
zoom(s, T(10), 540, 840, 1.04, 0.3)
s.ecrire()

# ================================================================ LES TECHNIQUES 10 À 6
technique(1, 10, 13, 18, "Vérifie ton trajet", [(T(15) - 0.1, "carte-tel"), (T(18), "taxi-cab"), (T(21), "pas-rue"), (T(23), "passage-pieton")], "trajet",
          lambda s, p, g: marche(s, p, g, g + 1.6, 0))
technique(2, 9, 25, 30, "Regroupe tes courses", [(T(27) - 0.1, "courses-sac"), (T(30), "marche-fruits"), (T(33), "fruits-rue"), (T(35), "caddie-courses")], "panier",
          lambda s, p, g: pose(s, p, g, 0.2, bd=-70, bg=70))
technique(3, 8, 37, 42, "Emporte ta bouteille", [(T(39) - 0.1, "bouteille-parc"), (T(42), "eau-achat"), (T(46), "bouteille-bois")], "bouteille",
          lambda s, p, g: pose(s, p, g, 0.2, bd=-150))
technique(4, 7, 49, 54, "Prépare tes repas", [(T(51) - 0.1, "boite-repas"), (T(54), "couple-cuisine"), (T(57), "livreur-pizza"), (T(59), "dejeuner-prepare")], "marmite",
          lambda s, p, g: acquiesce(s, p, g))
technique(5, 6, 61, 67, "Coupe les achats automatiques", [(T(63) - 0.1, "montre-notifs"), (T(67), "reveil-messages"), (T(70), "ecom-carte-ordi")], "ciseaux",
          lambda s, p, g: non(s, p, g))

# ================================================================ SCÈNE 7 : relance « Et attends la numéro 1 : elle change ta façon de dépenser »
s = scene(6, "Et attends la numéro 1 : elle change ta façon de dépenser")
fond_rayons(s, "#3a1640")
ecran(s, "r-ec", 190, 380, 700, 440, [(s.debut, "myst-sablier"), (T(75), "stk-horloge-approche"), (T(78), "myst-point-interro")], s.debut, style="tele")
cam(s, f'<div id="r-carte" class="carte-mys" style="left: 190px; top: 880px; opacity: 0"><b>N°1</b><i class="cad">{cadenas_html()}</i></div>')
apparait(s, "#r-carte", T(74), 0.25, 80, 0.6)
son(T(74), "battement-mystere", 0.45, "carte mystère")
s.j(f'tl.to("#r-carte", {{ rotation: 3, duration: 0.07, yoyo: true, repeat: 13, ease: "none" }}, {s.L(T(76))});')
son(T(76), "verrou", 0.45, "verrouillée")
zoom(s, T(76) - 0.1, 540, 1000, 1.35, 0.28)
zoom(s, T(80), 540, 960, 1.0, 0.3)
son(T(80), "riser-trailer", 0.38, "montée vers la suite", d=1.6)
cam(s, perso("r-lucas", 920, 1335, 330, CIEL, "lucas"))
vivant(s, "r-lucas")
gratte(s, "r-lucas", T(77))
humeur(s, "r-lucas", T(77), "o")
interrogations(s, "r-q", 820, 920, T(78))
bande(s, 5.5, mystere=True)
s.ecrire()

# ================================================================ LES TECHNIQUES 5 À 2
technique(7, 5, 83, 88, "Emprunte avant d’acheter", [(T(85) - 0.1, "perceuse-bois"), (T(88), "atelier-outils"), (T(93), "voisins-cadeaux")], "echange",
          lambda s, p, g: pose(s, p, g, 0.2, bg=100))
technique(8, 4, 97, 102, "Compare les prix", [(T(99) - 0.1, "prix-etiquettes"), (T(102), "primeur"), (T(104), "marche-tomates")], "balance",
          lambda s, p, g: (regarde(s, p, g, -5), regarde(s, p, g + 0.5, 5), regarde(s, p, g + 1.0, -5)))
technique(9, 3, 107, 112, "Attends avant d’acheter", [(T(109) - 0.1, "ecom-tel-carte"), (T(112), "lune-monte"), (T(115), "dort-bouche"), (T(118), "reveil-eteint")], "lune",
          lambda s, p, g: P.bras_croises(s, p, g))
technique(10, 2, 121, 126, "Écris ta liste", [(T(123) - 0.1, "todo-liste"), (T(126), "supermarche-frigo"), (T(128), "achat-tomates")], "liste",
          lambda s, p, g: pose(s, p, g, 0.2, bd=-60))

# ================================================================ SCÈNE 12 : NUMÉRO 1 (traitement à part : roulement, or, nouvelle musique, confettis, jauge plafond)
s = technique(11, 1, 134, 142, "Fixe ton plafond avant de sortir", [(T(136) - 0.1, "portefeuille-cash"), (T(142), "compta-depenses"), (T(145), "grillade-rue"), (T(146), "grill-boutique")],
              "plafond", lambda s, p, g: victoire(s, p, g, 2), or_=True, fin_scene=False)
confettis(s, "u-cf", s.debut + 0.2, 540, 900, 30, 520)
son(s.debut + 0.2, "victoire-tambours", 0.4, "numéro 1")
s.add('<div id="u-j" class="jauge-plafond" style="left: 110px; top: 880px; width: 860px; opacity: 0"><i id="u-ji"></i><em></em><b>PLAFOND</b></div>')
apparait(s, "#u-j", T(142) - 0.1, 0.2, 40)
s.j(f'tl.fromTo("#u-ji", {{ scaleX: 0 }}, {{ scaleX: 0.72, duration: 1.3, ease: "power1.in", immediateRender: false }}, {s.L(T(142))});')
son(T(142), "compteur", 0.35, "la sortie se remplit", d=1.3)
s.j(f'tl.to("#u-j", {{ keyframes: [{{ x: -12, duration: 0.04 }}, {{ x: 12, duration: 0.04 }}, {{ x: 0, duration: 0.04 }}] }}, {s.L(T(142) + 1.32)});')
son(T(142) + 1.32, "verrou", 0.5, "plafond atteint : stop")
tampon(s, "u-stop", "STOP", 700, 820, T(142) + 1.35, -8, 70, CORAIL)
s.ecrire()

# ================================================================ SCÈNE 13 : À RETENIR / À FAIRE
s = scene(12, "Retiens ça : chaque dépense doit avoir une place dans ton budget. À faire : fixe ton plafond avant ta prochaine sortie")
fond_rayons(s)
ecran(s, "f-ec", 60, 330, 960, 380, [(s.debut, "budget-separe"), (T(152), "repartir-depenses"), (T(158), "portefeuille-cash"), (T(163), "notes-stylo")], s.debut, style="panneau")
cam(s, '<div id="f-carte" class="regle fin-carte" style="left: 60px; top: 760px; opacity: 0">'
       '<h3>À RETENIR</h3><p id="f-r" style="opacity: 0"><span id="f-sur" class="surl"></span><span class="txt">CHAQUE DÉPENSE DOIT AVOIR UNE PLACE DANS TON BUDGET.</span></p>'
       '<h3 id="f-h2" class="h-faire" style="opacity: 0">À FAIRE</h3><p id="f-f" class="faire" style="opacity: 0">FIXE TON PLAFOND AVANT TA PROCHAINE SORTIE.<b id="f-ok" class="coche-ok" style="opacity: 0">✓</b></p></div>')
apparait(s, "#f-carte", T(147), 0.28, 120, 0.8)
son(T(147), "whoosh-tunnel", 0.45, "carte retiens ça")
zoom(s, T(148), 540, 880, 1.16, 0.3)
apparait(s, "#f-r", T(149), 0.22, 30)
impact(T(149), 0.5, "chaque dépense")
s.j(f'tl.fromTo("#f-sur", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power2.out", immediateRender: false }}, {s.L(T(154))});')
son(T(154), "scintille-whoosh", 0.45, "une place dans ton budget")
pano(s, T(158) - 0.1, 540, 1080, 1.12, 0.35)
apparait(s, "#f-h2", T(158), 0.2, 30)
apparait(s, "#f-f", T(160), 0.22, 30)
son(T(160), "pop-long", 0.45, "à faire")
s.j(f'tl.fromTo("#f-ok", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2)", immediateRender: false }}, {s.L(T(166))});')
son(T(166), "coche", 0.5, "coché")
zoom(s, T(165), 540, 960, 1.0, 0.3)
s.ecrire()

# ================================================================ SCÈNE 14 : abonne-toi ; laquelle vas-tu tester ?
s = scene(13, "Abonne-toi à Lefinancier : laquelle vas-tu tester ?")
fond_rayons(s)
cam(s, '<div id="z-carte" class="profil" style="left: 140px; top: 330px; opacity: 0"><img src="assets/img/profil.png" alt="" />'
       '<div><b>Lefinancier</b><span>L’argent expliqué simplement</span></div>'
       '<div id="z-btn" class="btn">S’abonner</div><div id="z-ok" class="btn ok" style="opacity: 0">Abonné ✓</div></div>')
apparait(s, "#z-carte", s.debut + 0.05, 0.3, 120)
son(s.debut + 0.05, "swoosh-monte", 0.42, "carte profil")
cam(s, '<svg id="z-souris" class="souris" viewBox="0 0 40 52" style="left: 980px; top: 900px"><path d="M4 2 L4 40 L14 31 L21 48 L28 45 L21 29 L34 29 Z" fill="#fff" stroke="#0B1220" stroke-width="3" stroke-linejoin="round" /></svg>')
s.j(f'tl.to("#z-souris", {{ x: -300, y: -330, duration: 0.4, ease: "power2.inOut" }}, {s.L(T(168) - 0.3)});')
s.j(f'tl.to("#z-souris", {{ scale: 0.8, duration: 0.07, yoyo: true, repeat: 1 }}, {s.L(T(168) + 0.1)});')
s.j(f'tl.set("#z-btn", {{ opacity: 0 }}, {s.L(T(168) + 0.17)});')
s.j(f'tl.set("#z-ok", {{ opacity: 1 }}, {s.L(T(168) + 0.17)});')
son(T(168) + 0.1, "clic-souris", 0.5, "clic s'abonner")
son(T(168) + 0.2, "notif-positive", 0.42, "abonné")
confettis(s, "z-cf", T(168) + 0.2, 720, 620, 18, 340)
s.j(f'tl.to("#z-souris", {{ opacity: 0, duration: 0.15 }}, {s.L(T(170) - 0.2)});')
texte(s, "z-q", "LAQUELLE VAS-TU TESTER ?", 0, 690, 80, T(170), BLANC, w=1080)
ics = ["trajet", "panier", "bouteille", "marmite", "ciseaux", "echange", "balance", "lune", "liste", "plafond"]
for k, (n, ic) in enumerate(zip(NUMS, ics)):
    x, y = 70 + (k % 5) * 192, 830 + (k // 5) * 230
    cam(s, f'<div id="z-c{k}" class="choix-num{" or" if n == 1 else ""}" style="left: {x}px; top: {y}px; opacity: 0">{icone(ic, 80)}<b>{n}</b></div>')
    claque(s, f"#z-c{k}", T(170) + 0.15 + k * 0.09, 1.7)
    son(T(170) + 0.15 + k * 0.09, tour(["pop-sec", "pop-click", "pop-cartoon"]), 0.34, f"choix {n}")
s.j(f'tl.to("#z-c9", {{ scale: 1.15, duration: 0.15, yoyo: true, repeat: 3 }}, {s.L(T(170) + 1.2)});')
etiquette(s, "z-com", "DIS-LE EN COMMENTAIRE", 300, 1300, T(171), BLANC, NUIT, 40, -2)
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

MUSIQUES = [  # Mixkit populaires, fichiers à −13,3 / −14,2 / −9,7 LUFS → ≈ −21 LUFS pour une voix à −15 ; la 3e démarre sur la numéro 1
    (0, "partie-1-cbpd", COUPES[5], 0.41),
    (COUPES[5], "partie-2-need-for-speed", round(COUPES[11] - COUPES[5], 2), 0.46),
    (COUPES[11], "partie-3-deep-urban-drop", round(FIN - COUPES[11], 2), 0.27),
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
