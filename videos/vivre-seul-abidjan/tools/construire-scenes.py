#!/usr/bin/env python3
"""Lefinancier : « Combien ça coûte vraiment de vivre seul à Abidjan ? » — vertical natif 1080×1920, 2 min 10.
Texte écrit par une autre IA (prompt approfondi finance/prompt-vivre-seul-abidjan.txt), voix MiniMax de l'utilisateur.
Lucas quitte la maison familiale : loyer (quartier populaire / Cocody), caution et avance, commission, équipement,
coût d'entrée, factures de la première semaine, dépenses de chaque mois, budget face au SMIG, repère salarial, totaux,
fin claire « À RETENIR » / « À FAIRE ». Version longue (jusqu'à 12 chiffres, annoncés un par un).
Base technique reprise de videos/enveloppes (personnages bleus articulés, décors dessinés, vraies vidéos DANS la scène
avec zoom de caméra, bulles, cases mystère, bruitages à chaque mouvement).
Écrit : compositions/s*.html, compositions/sous-titres.html et index.html.
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
TITRE = "Vivre seul à Abidjan"
VOL_SFX = 0.9
SOL = 1290  # ligne du sol (pieds des personnages)


def b(i):
    return round(T(i) - 0.12, 2)


FIN = 130.4
COUPES = [0] + [b(i) for i in (14, 25, 49, 74, 111, 126, 150, 183, 227, 245, 269, 295)] + [FIN]
NOMS = ["s01-hook", "s02-studio", "s03-quartiers", "s04-caution", "s05-entree", "s06-factures", "s07-chaque-mois", "s08-smig",
        "s09-repere", "s10-comprend", "s11-total", "s12-retenir", "s13-abonne"]


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


# ================================================================ ÉLÉMENTS PROPRES À CETTE VIDÉO (prix, factures, barres, matelas)
def prix(s, pid, label, montant, x, y, g, w=460, coul=CIEL, taille=88, compte_de=None, d_compte=0.6):
    """Étiquette de prix (label + montant) ; le montant peut défiler depuis compte_de."""
    cam(s, f'<div id="{pid}" class="compte" style="left: {x}px; top: {y}px; width: {w}px; border-color: {coul}; opacity: 0">'
           f'<span>{label}</span><b style="font-size: {taille}px"><span id="{pid}-n" style="display: inline; font-size: inherit; color: inherit">{fcfa(montant)}</span> F</b></div>')
    claque(s, f"#{pid}", g, 1.7)
    impact(g, 0.5, f"prix {label}")
    if compte_de is not None:
        compteur(s, f"#{pid}-n", g, compte_de, montant, d_compte)
        son(g, "compteur", 0.3, "le montant défile", d=d_compte + 0.1)


def facture(s, fid, titre_f, sous, x, y, g, coul=CIEL, rot=0):
    """Facture qui tombe dans la scène (papier blanc, en-tête de couleur)."""
    cam(s, f'<div id="{fid}" class="contrat facture" data-layout-allow-overlap style="left: {x}px; top: {y}px; width: 300px; transform: rotate({rot}deg); opacity: 0">'
           f'<span style="color: {coul}">FACTURE</span><b>{titre_f}</b><em>{sous}</em><i></i><i style="width: 70%"></i></div>')
    s.j(f'tl.fromTo("#{fid}", {{ opacity: 0, y: -520, rotation: {rot - 25} }}, {{ opacity: 1, y: 0, rotation: {rot}, duration: 0.32, ease: "back.out(1.5)", immediateRender: false }}, {s.L(g)});')
    son(g, tour(["papier-glisse", "papiers", "page"]), 0.42, f"facture {titre_f}")
    son(g + 0.28, tour(["notif-indice", "notif-positive"]), 0.36, "facture arrivée")


def barre_v(bid, x, bas, w, h, coul, label, montant_html, op=0):
    """Barre verticale (comparaison budget / revenu), qui pousse depuis le bas."""
    return (f'<div id="{bid}" class="barre-v" style="left: {x}px; top: {bas - h}px; width: {w}px; height: {h}px; opacity: {op}">'
            f'<i id="{bid}-i" style="background: {coul}"></i><b>{montant_html}</b><span>{label}</span></div>')


def pousse(s, bid, g, d=0.5):
    s.j(f'tl.set("#{bid}", {{ opacity: 1 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{bid}-i", {{ scaleY: 0 }}, {{ scaleY: 1, duration: {d}, ease: "power3.out", immediateRender: false }}, {s.L(g)});')
    son(g, "swoosh-monte", 0.42, f"barre {bid}")


def matelas(mid, x, y, w=420, op=0):
    return f'<div id="{mid}" class="matelas" data-layout-allow-overlap style="left: {x}px; top: {y}px; width: {w}px; opacity: {op}"><i></i><i></i><i></i></div>'


def liste_achats(s, lid, x, y, items, temps):
    """Liste « À ACHETER » : chaque ligne apparaît (et se coche) au moment où la voix la dit."""
    lignes = "".join(f'<p id="{lid}-{k}" style="opacity: 0"><i class="c" style="background: {(CIEL, CLAIR, OR, PROFOND, CIEL, CLAIR)[k % 6]}"></i>'
                     f'<span class="mot-liste">{t}</span><b class="ok">✓</b></p>' for k, t in enumerate(items))
    cam(s, f'<div id="{lid}" class="carnet" style="left: {x}px; top: {y}px; width: 470px; opacity: 0"><h3>À ACHETER</h3>{lignes}</div>')
    for k, g in enumerate(temps):
        s.j(f'tl.set("#{lid}-{k}", {{ opacity: 1 }}, {s.L(g)});')
        s.j(f'tl.fromTo("#{lid}-{k}", {{ x: -40 }}, {{ x: 0, duration: 0.14, immediateRender: false }}, {s.L(g)});')
        son(g, tour(["pop-click", "stylo", "pop-sec", "coche"]), 0.36, f"achat {items[k]}")


def fond_nuit(s, a="#16346a"):
    cam(s, f'<div class="decor"><div class="ciel" style="background: radial-gradient(ellipse 90% 60% at 50% 40%, {a} 0%, #0b1220 78%)"></div></div>')


def maison_html(hid, x, y, w, h, coul, titre_m):
    """Petite façade dessinée (quartier) avec fenêtres éclairées et toit."""
    fen = "".join(f'<i style="left: {24 + (k % 3) * (w - 48) // 3}px; top: {70 + (k // 3) * 90}px"></i>' for k in range(6 if h > 330 else 3))
    return (f'<div id="{hid}" class="maison" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; --c: {coul}; opacity: 0">'
            f'<em class="toit"></em>{fen}<b>{titre_m}</b><u class="porte"></u></div>')


# ================================================================ SCÈNE 1 : HOOK (0 → 5,8 s) : quitter la maison ? combien coûte vraiment vivre seul à Abidjan
s = scene(0, "Hook : tu veux quitter la maison familiale ? Voici combien coûte vraiment vivre seul à Abidjan")
items = [(0, "cartons-couple"), (T(1), "emmenagement"), (T(2), "carton-vetements"), (T(3), "cle-remise"), (T(4), "studio-interieur"),
         (T(6), "immeubles-aerien"), (T(7), "billets-liasse"), (T(8), "depenses-revenus"), (T(9), "plus-un-sou"), (T(10), "lit-telephone"),
         (T(11), "ville-nuit-aerien"), (T(12), "billets-tombent"), (T(13), "immeuble-ville")]
cam(s, f'<div id="h-plein" class="plein">{videos(s, "h-v", items, son_v=0.44)}</div><div class="voile-bas"></div>')
son(0.0, "trailer-impact", 0.6, "début")
son(0.02, "whoosh-cine", 0.45, "début")
texte(s, "h-t1", "QUITTER LA MAISON<br>DES PARENTS ?", 0, 560, 120, 0.02, BLANC, w=1080, fin=T(6) - 0.04)
secousse(s, T(4), 16)
son(T(4), "trousseau", 0.5, "clés")
texte(s, "h-sujet", "VIVRE SEUL<br>À ABIDJAN", 140, 540, 150, T(6), NUIT, cls="gros bande", rot=-3)
impact(T(6), 0.6, "sujet")
flash(s, T(6))
texte(s, "h-q", "COMBIEN ÇA COÛTE<br>VRAIMENT ?", 0, 900, 104, T(7), OR, w=1080)
son(T(7), "glitch-cine", 0.5, "combien")
interrogations(s, "h-qq", 760, 380, T(9))
son(T(12) - 0.4, "riser-tech", 0.35, "montée", d=0.5)
zoom(s, T(12), 540, 760, 1.12, 0.22)
s.ecrire()

# ================================================================ SCÈNE 2 : Lucas a trouvé un studio ; il pense que le loyer suffit
s = scene(1, "Lucas a trouvé un studio et pense que le loyer suffit")
s.bornes = (0, 1700)
decor_rue(s, "r", jour=True, droite=620)
cx, cy = ecran(s, "r-st", 560, 390, 470, 600, [(s.debut, "immeuble-ciel"), (T(17), "studio-interieur"), (T(19), "cle-remise")], s.debut, style="panneau", titre_e="STUDIO À LOUER")
cam(s, perso("r-lucas", 250, SOL, 600, CIEL, "lucas"))
marche(s, "r-lucas", s.debut + 0.05, T(17), 120)
vivant(s, "r-lucas", T(17))
nom(s, "r-nom", "LUCAS", 250, 600, T(14) + 0.05)
cache(s, "#r-nom", T(20))
s.place(540, 900, 1.05)
zoom_ecran(s, T(17), 560, 390, 470, 600, (540, 960, 1.0, T(19) + 0.2), d=0.26)
son(T(19), "trousseau", 0.5, "les clés")
pouce(s, "r-lucas", T(20))
humeur(s, "r-lucas", T(20), "rire")
bulle(s, "r-b", "Le loyer,<br>et c’est tout !", 90, 470, T(20) + 0.1, w=470, taille=50, pensee=True)
etiquette(s, "r-l", "LOYER = TOUT ?", 560, 1060, T(23), OR, NUIT, 60, -3)
interrogations(s, "r-q", 800, 980, T(24))
zoom(s, T(23) - 0.05, 420, 760, 1.18, 0.26)
s.ecrire()

# ================================================================ SCÈNE 3 : le loyer : 65 000 F en quartier populaire, ~110 000 F à Cocody (la caméra suit Lucas)
s = scene(2, "Dans un quartier populaire, il vise 65 000 francs par mois ; à Cocody, autour de 110 000")
s.bornes = (0, 2160)
decor_rue(s, "q", jour=True, droite=1080)
ecran(s, "q-p1", 120, 420, 460, 520, [(s.debut, "ville-nuit-marche"), (T(28), "marche-tomates"), (T(31), "taxi-voie")], s.debut, style="panneau", titre_e="QUARTIER POPULAIRE")
ecran(s, "q-p2", 1240, 420, 460, 520, [(s.debut, "immeuble-ville"), (T(40), "immeubles-aerien"), (T(44), "chambre-fenetre")], s.debut, style="panneau", titre_e="COCODY")
cam(s, perso("q-lucas", 660, SOL, 560, CIEL, "lucas"))
vivant(s, "q-lucas", s.debut, T(36))
regarde(s, "q-lucas", s.debut, -4, -3)
s.place(420, 900, 1.0)
zoom(s, T(27), 350, 700, 1.25, 0.28)
prix(s, "q-x1", "LOYER / MOIS", 65000, 130, 800, T(31), 440, CIEL, 84, compte_de=0)
zoom(s, T(33), 420, 900, 1.0, 0.3)
marche(s, "q-lucas", T(36), T(42), 700)
pano(s, T(36) + 0.1, 1300, 900, 1.0, 0.8)
regarde(s, "q-lucas", T(42), 4, -3)
vivant(s, "q-lucas", T(42))
zoom(s, T(44), 1470, 700, 1.25, 0.28)
prix(s, "q-x2", "LOYER / MOIS", 110000, 1250, 800, T(47), 440, OR, 84, compte_de=65000)
tampon(s, "q-t", "MÊME STUDIO", 1260, 360, T(40), -6, 64, OR)
humeur(s, "q-lucas", T(47), "o")
zoom(s, T(48) - 0.1, 1100, 900, 1.0, 0.25)
s.ecrire()

# ================================================================ SCÈNE 4 : avant même de poser son matelas : la caution et l'avance (la loi encadre ces sommes)
s = scene(3, "Avant même de poser son matelas, le propriétaire réclame la caution et l'avance ; la loi encadre ces sommes")
decor_chambre(s, "c")
cam(s, perso("c-lucas", 300, SOL, 600, CIEL, "lucas"))
cam(s, matelas("c-mat", 120, 900, 420, 1))
vivant(s, "c-lucas")
humeur(s, "c-lucas", s.debut, "content")
pose(s, "c-lucas", s.debut + 0.1, 0.2, bd=-60, bg=60)
s.j(f'tl.to("#c-mat", {{ y: 220, duration: 0.5, ease: "bounce.out" }}, {s.L(T(53))});')
son(T(53) + 0.3, "impact-cartoon", 0.4, "le matelas tombe presque")
cam(s, perso("c-prop", 840, SOL, 640, PROFOND, "banquier"))
s.j(f'tl.fromTo("#c-prop", {{ x: 500 }}, {{ x: 0, duration: 0.5, ease: "power2.out", immediateRender: false }}, {s.L(T(56))});')
son(T(56), "swoosh-vitesse", 0.45, "le propriétaire entre")
vivant(s, "c-prop", T(56) + 0.5, decal=0.2)
nom(s, "c-nom", "LE PROPRIÉTAIRE", 760, 660, T(57), PROFOND)
s.j('tl.set("#c-nom b", { color: "#F1F5F9" }, 0);')
parle(s, "c-prop", T(57), T(62) + 0.4)
bulle(s, "c-b", "La caution !<br>Et l’avance !", 470, 400, T(60), fin=T(63) - 0.05, queue="d", w=460, taille=54)
humeur(s, "c-lucas", T(60), "o")
gouttes(s, "c-g", 380, 450, T(60))
zoom(s, T(57) - 0.1, 700, 760, 1.15, 0.28)
cam(s, '<div id="c-doc" class="contrat" style="left: 330px; top: 560px; width: 420px; opacity: 0"><span>BAIL D’HABITATION</span><b>CAUTION<br>+ AVANCE</b><i></i><i style="width: 80%"></i><i style="width: 60%"></i></div>')
apparait(s, "#c-doc", T(63), 0.25, 120, 0.6)
son(T(63), "feuillette", 0.45, "le contrat")
etiquette(s, "c-loi", "ENCADRÉES PAR LA LOI", 250, 1000, T(65), OR, NUIT, 58, -3)
zoom(s, T(64), 540, 760, 1.25, 0.3)
ecran(s, "c-ec", 600, 360, 420, 300, [(T(67), "immo-contrat"), (T(70), "signature")], T(67) - 0.1, style="tele")
zoom_ecran(s, T(68), 600, 360, 420, 300, (540, 960, 1.0, T(72) + 0.1), d=0.26)
s.ecrire()

# ================================================================ SCÈNE 5 : commission du démarcheur, équipement, coût d'entrée 400 000 / 550 000
s = scene(4, "Le démarcheur demande sa commission, Lucas doit tout acheter : il faut environ 400 000 F pour entrer (550 000 dans un quartier plus cher)")
decor_chambre(s, "e")
cam(s, perso("e-dem", 830, SOL, 600, CLAIR, "hugo"))
vivant(s, "e-dem", decal=0.3)
nom(s, "e-nom", "LE DÉMARCHEUR", 820, 600, s.debut + 0.15, CLAIR)
parle(s, "e-dem", T(75), T(78) + 0.4)
bulle(s, "e-b", "Ma commission,<br>s’il te plaît !", 300, 430, T(74) + 0.05, fin=T(79) - 0.05, queue="d", w=520, taille=50)
pouce(s, "e-dem", T(78), "bd")
cam(s, perso("e-lucas", 230, SOL, 560, CIEL, "lucas"))
vivant(s, "e-lucas")
humeur(s, "e-lucas", T(76), "triste")
s.place(620, 820, 1.1)
vole(s, "e-pc", 300, 900, 820, 820, T(78) + 0.1, 4, 0.08, "F", 80, 0.45)
zoom(s, T(79), 540, 960, 1.0, 0.28)
cache(s, "#e-nom", T(79))
s.j(f'tl.to("#e-dem", {{ x: 600, opacity: 0, duration: 0.4, ease: "power2.in" }}, {s.L(T(79) + 0.1)});')
liste_achats(s, "e-l", 520, 360, ["MATELAS", "VENTILATEUR", "RÉCHAUD", "BOUTEILLES", "MARMITE", "RIDEAU"], [T(82), T(83), T(84), T(85), T(86), T(88)])
apparait(s, "#e-l", T(81), 0.25, 80)
ecran(s, "e-ec", 60, 380, 420, 330, [(T(82), "lit-telephone"), (T(83), "chambre-fenetre"), (T(84), "gaz-flamme"), (T(85), "eau-achat"), (T(86), "oeufs-poele"), (T(88), "rideaux-soleil")], T(81) + 0.05, style="tele", fin=T(89))
for k, g in enumerate([T(82), T(84), T(86), T(88)]):
    paye(g + 0.1, 0.32)
zoom(s, T(82) - 0.1, 540, 640, 1.18, 0.3)
cache(s, "#e-l", T(89))
cache(s, "#e-ec", T(89))
zoom(s, T(89), 540, 900, 1.0, 0.3)
texte(s, "e-ce", "COÛT D’ENTRÉE", 0, 380, 110, T(90), OR, w=1080)
son(T(90), "battement-mystere", 0.4, "il découvre")
cam(s, f'<div id="e-m1" class="mystere" style="left: 40px; top: 560px; width: 480px; height: 300px; opacity: 0"><b id="e-m1-q">?</b>'
       f'<div id="e-m1-r" class="mys-txt" style="opacity: 0"><span>QUARTIER POPULAIRE</span><b style="font-size: 104px">400 000 F</b><em>pour entrer</em></div></div>')
cam(s, f'<div id="e-m2" class="mystere" style="left: 560px; top: 560px; width: 480px; height: 300px; opacity: 0"><b id="e-m2-q">?</b>'
       f'<div id="e-m2-r" class="mys-txt" style="opacity: 0"><span>QUARTIER PLUS CHER</span><b style="font-size: 104px">550 000 F</b><em>pour entrer</em></div></div>')
apparait(s, "#e-m1", T(90) + 0.05, 0.25, 80)
apparait(s, "#e-m2", T(90) + 0.12, 0.25, 80)
for n, g in (("e-m1", T(94)), ("e-m2", T(104))):
    s.j(f'tl.to("#{n}-q", {{ opacity: 0, scale: 0.3, duration: 0.12 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{n}-r", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2)", immediateRender: false }}, {s.L(g + 0.04)});')
    son(g, "revelation", 0.45, f"révélation {n}")
    impact(g + 0.05, 0.55, "coût d'entrée")
    flash(s, g)
zoom(s, T(94) - 0.1, 400, 700, 1.15, 0.26)
pano(s, T(104) - 0.12, 680, 700, 1.15, 0.3)
zoom(s, T(108), 540, 900, 1.0, 0.28)
panique(s, "e-lucas", T(105), 1.0)
humeur(s, "e-lucas", T(104), "o")
secousse(s, T(104) + 0.1, 18)
s.ecrire()

# ================================================================ SCÈNE 6 : il signe, soulagé ; mais la première semaine : CIE, eau, gaz
s = scene(5, "Il signe, soulagé. Mais la première semaine, la CIE, l'eau et le gaz arrivent déjà")
decor_chambre(s, "f")
cam(s, perso("f-lucas", 260, SOL, 600, CIEL, "lucas"))
vivant(s, "f-lucas")
ecran(s, "f-ec", 560, 380, 460, 340, [(s.debut, "signature"), (T(113), "immo-cle-poignee"), (T(119), "compteur-electrique"), (T(120), "robinet-goutte"), (T(123), "gaz-flamme")], s.debut, style="tele")
son(T(112), "stylo", 0.5, "il signe")
victoire(s, "f-lucas", T(113), 1)
humeur(s, "f-lucas", T(113), "rire")
son(T(113) + 0.1, "cloche-succes", 0.4, "soulagé")
s.place(540, 760, 1.12)
cam(s, '<div id="f-cal" class="calendrier petit" data-layout-allow-overlap style="left: 80px; top: 360px; opacity: 0"><span>SEMAINE</span><b>1</b></div>')
apparait(s, "#f-cal", T(115), 0.24, 80)
son(T(115), "tic-tac", 0.4, "première semaine", d=1.0)
zoom(s, T(114), 540, 900, 1.0, 0.3)
facture(s, "f-f1", "CIE", "électricité", 420, 820, T(119), CIEL, -8)
facture(s, "f-f2", "EAU", "SODECI", 600, 900, T(120), CLAIR, 6)
facture(s, "f-f3", "GAZ", "bouteille", 760, 800, T(123), OR, -4)
humeur(s, "f-lucas", T(119), "o")
regarde(s, "f-lucas", T(119), 5, 2)
gratte(s, "f-lucas", T(124))
zoom(s, T(123) + 0.2, 600, 900, 1.15, 0.26)
s.ecrire()

# ================================================================ SCÈNE 7 : chaque mois : manger, se déplacer, crédit internet, savon, entretien, imprévus
s = scene(6, "Chaque mois, il faut manger, se déplacer, acheter du crédit internet, du savon, des produits d'entretien et garder une marge pour les imprévus")
fond_nuit(s)
cam(s, '<div id="m-cal" class="page-cal" data-layout-allow-overlap style="left: 330px; top: 350px; width: 420px; height: 250px; opacity: 0"><span>CHAQUE MOIS</span><b style="font-size: 110px; line-height: 150px">↻</b></div>')
apparait(s, "#m-cal", s.debut + 0.05, 0.24, 80)
son(s.debut + 0.05, "swoosh-monte", 0.42, "chaque mois")
mots_m = [("MANGER", T(131), [(T(131), "marche-legumes"), (T(132), "cuisine-legumes")]),
          ("SE DÉPLACER", T(133), [(T(133), "taxi-voie")]),
          ("CRÉDIT INTERNET", T(136), [(T(136), "tel-tape")]),
          ("SAVON", T(139), [(T(139), "vaisselle-savon")]),
          ("ENTRETIEN", T(141), [(T(141), "menage-maison")]),
          ("IMPRÉVUS", T(146), [(T(146), "myst-point-interro"), (T(148), "choc-mains-tete")])]
tous = [it for _, _, its in mots_m for it in its]
ecran(s, "m-ec", 60, 640, 960, 470, tous, T(131) - 0.05, style="panneau")
for k, (lab, g, _) in enumerate(mots_m):
    etiquette(s, f"m-e{k}", lab, (70, 520)[k % 2], 620, g, (CIEL, CLAIR, OR, BLANC, CLAIR, CORAIL)[k], NUIT, 56, (-3, 3)[k % 2], fin=(mots_m[k + 1][1] - 0.02 if k + 1 < len(mots_m) else None))
    son(g, tour(["pop-cartoon", "pop-bulle", "pop-click"]), 0.38, lab)
zoom(s, T(131) - 0.1, 540, 880, 1.12, 0.3)
pano(s, T(136) - 0.1, 540, 860, 1.18, 0.3)
pano(s, T(141) - 0.1, 540, 880, 1.12, 0.3)
zoom_ecran(s, T(146), 60, 640, 960, 470, (540, 960, 1.0, T(149) - 0.05), d=0.24)
son(T(148), "erreur-clic", 0.4, "imprévus")
s.ecrire()

# ================================================================ SCÈNE 8 : budget du mois vs SMIG 75 000 : il manque 135 000 (populaire) / 225 000 (Cocody)
s = scene(7, "En cuisinant et en prenant les transports collectifs, son budget dépasse largement le SMIG de 75 000 : il manque 135 000 / 225 000")
fond_nuit(s, "#15305e")
ecran(s, "b-ec", 560, 360, 460, 330, [(s.debut, "couple-cuisine"), (T(154), "bus-texto")], s.debut, style="tele", fin=T(159) - 0.05)
cam(s, perso("b-lucas", 250, SOL, 470, CIEL, "lucas"))
vivant(s, "b-lucas")
etiquette(s, "b-c", "IL CUISINE", 90, 420, T(151), CIEL, NUIT, 54, -3, fin=T(154) - 0.05)
etiquette(s, "b-t", "TRANSPORTS COLLECTIFS", 60, 420, T(154), CLAIR, NUIT, 50, 2, fin=T(158) - 0.05)
s.place(700, 600, 1.15)
zoom(s, T(158), 540, 900, 1.0, 0.3)
cache(s, "#b-ec", T(159) - 0.1)
BAS = 1150
cam(s, barre_v("b-bud", 440, BAS, 260, 680, "linear-gradient(180deg, #FF6B6B, #b91c1c)", "BUDGET DU MOIS", "?"))
cam(s, barre_v("b-smig", 750, BAS, 260, 240, "linear-gradient(180deg, #38BDF8, #0284C7)", "SMIG", "75 000 F"))
pousse(s, "b-bud", T(159), 0.7)
son(T(161), "alarme-alerte", 0.32, "dépasse largement", d=0.8)
pousse(s, "b-smig", T(164))
s.j(f'tl.fromTo("#b-smig b", {{ scale: 1.6 }}, {{ scale: 1, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, {s.L(T(166))});')
impact(T(166), 0.5, "75 000")
humeur(s, "b-lucas", T(161), "o")
gouttes(s, "b-g", 330, 420, T(161))
cam(s, '<div id="b-ecart" class="ecart" data-layout-allow-overlap style="left: 750px; top: 470px; width: 260px; height: 440px; opacity: 0"></div>')
s.j(f'tl.fromTo("#b-ecart", {{ opacity: 0, scaleY: 0, transformOrigin: "50% 100%" }}, {{ opacity: 1, scaleY: 1, duration: 0.3, ease: "power2.out", immediateRender: false }}, {s.L(T(170))});')
son(T(170), "buzz-basse", 0.42, "il manque")
texte(s, "b-man", "IL MANQUE", 70, 350, 84, T(170), CORAIL)
prix(s, "b-p1", "QUARTIER POPULAIRE", -135000, 60, 470, T(171), 360, CORAIL, 64)
prix(s, "b-p2", "COCODY", -225000, 60, 700, T(179), 360, CORAIL, 64)
panique(s, "b-lucas", T(179), 0.8)
zoom(s, T(171) - 0.1, 540, 760, 1.08, 0.26)
zoom(s, T(181), 540, 900, 1.0, 0.28)
s.ecrire()

# ================================================================ SCÈNE 9 : un autre repère : ~114 000 F (revenu moyen des jeunes salariés d'Abidjan, cité par la voix) ; il manque encore 96 000 / 196 000
s = scene(8, "Un autre repère : environ 114 000 F de revenu moyen chez les jeunes salariés ; pas garanti ; il manquerait encore 96 000 / 196 000")
fond_nuit(s)
ecran(s, "o-ec", 60, 360, 960, 420, [(s.debut, "depenses-revenus"), (T(193), "separe-budgets"), (T(200), "stress-tete"), (T(208), "frustree-compte")], s.debut, style="panneau")
etiquette(s, "o-r", "AUTRE REPÈRE", 80, 340, T(186), OR, NUIT, 54, -3)
prix(s, "o-x", "REVENU MOYEN DES JEUNES SALARIÉS", 114000, 140, 820, T(189), 800, OR, 110, compte_de=75000, d_compte=0.7)
zoom(s, T(189) - 0.1, 540, 900, 1.12, 0.28)
tampon(s, "o-t", "PAS GARANTI", 300, 1060, T(204), -8, 90, CORAIL)
son(T(206), "erreur-echec", 0.4, "pas garanti")
zoom(s, T(208), 540, 960, 1.0, 0.3)
cache(s, "#o-x", T(209))
cache(s, "#o-t", T(209))
cache(s, "#o-ec", T(209))
cache(s, "#o-r", T(209))
texte(s, "o-m", "IL MANQUE ENCORE", 0, 420, 100, T(213), CORAIL, w=1080)
son(T(213), "buzz-basse", 0.42, "il manquerait encore")
prix(s, "o-p1", "QUARTIER POPULAIRE", -96000, 120, 620, T(215), 840, CORAIL, 100)
prix(s, "o-p2", "COCODY", -196000, 120, 900, T(223), 840, CORAIL, 100)
zoom(s, T(215) - 0.1, 540, 820, 1.08, 0.26)
pano(s, T(223) - 0.1, 540, 900, 1.08, 0.26)
zoom(s, T(226), 540, 900, 1.0, 0.25)
s.ecrire()

# ================================================================ SCÈNE 10 : Lucas comprend : calculer le coût d'entrée ET le coût de chaque mois, avant de signer
s = scene(9, "Lucas comprend qu'il aurait dû calculer le coût d'entrée et le coût de chaque mois avant de signer")
decor_chambre(s, "k")
cam(s, perso("k-lucas", 250, SOL, 600, CIEL, "lucas"))
vivant(s, "k-lucas")
gratte(s, "k-lucas", T(228))
humeur(s, "k-lucas", T(228), "neutre")
cam(s, '<svg id="k-amp" viewBox="0 0 100 130" style="position: absolute; left: 200px; top: 300px; width: 110px; height: 143px; opacity: 0">'
       '<path d="M50 8 Q86 8 86 46 Q86 66 68 80 L68 96 L32 96 L32 80 Q14 66 14 46 Q14 8 50 8 Z" fill="#F2B705" stroke="#0B1220" stroke-width="6" />'
       '<rect x="32" y="100" width="36" height="20" rx="6" fill="#94A3B8" stroke="#0B1220" stroke-width="5" /></svg>')
claque(s, "#k-amp", T(228) + 0.2, 2.0)
son(T(228) + 0.2, "lumiere", 0.45, "il comprend")
ecran(s, "k-ec", 580, 360, 440, 320, [(T(232), "calculatrice"), (T(236), "recus-calcul"), (T(242), "notes-stylo")], T(231), style="tele")
cam(s, '<div id="k-b1" class="bloc" style="left: 470px; top: 760px; width: 270px; opacity: 0"><b>COÛT</b><span>D’ENTRÉE</span></div>'
       '<div id="k-plus" class="gros" style="left: 760px; top: 770px; font-size: 110px; color: #F2B705; opacity: 0">+</div>'
       '<div id="k-b2" class="bloc" style="left: 800px; top: 760px; width: 250px; background: #F2B705; opacity: 0"><b>COÛT</b><span>DE CHAQUE MOIS</span></div>')
claque(s, "#k-b1", T(234), 1.8)
impact(T(234), 0.45, "coût d'entrée")
claque(s, "#k-plus", T(236), 2)
claque(s, "#k-b2", T(238), 1.8)
impact(T(238), 0.45, "coût de chaque mois")
etiquette(s, "k-av", "AVANT DE SIGNER", 500, 980, T(242), CORAIL, BLANC, 56, -3)
acquiesce(s, "k-lucas", T(242))
zoom(s, T(233), 760, 820, 1.25, 0.28)
zoom(s, T(242) - 0.05, 540, 900, 1.05, 0.25)
s.ecrire()

# ================================================================ SCÈNE 11 : donc : ~210 000 F / mois (quartier populaire), 300 000 F (quartier plus cher)
s = scene(10, "Donc, vivre seul à Abidjan demande environ 210 000 francs par mois dans un quartier populaire, et 300 000 dans un quartier plus cher")
fond_nuit(s, "#1a3b78")
texte(s, "t-d", "VIVRE SEUL À ABIDJAN", 0, 360, 92, s.debut + 0.1, BLANC, w=1080)
son(s.debut + 0.1, "whoosh-tunnel", 0.45, "donc")
cam(s, maison_html("t-h1", 70, 520, 440, 360, CIEL, "POPULAIRE") + maison_html("t-h2", 570, 520, 440, 360, OR, "PLUS CHER"))
apparait(s, "#t-h1", T(247), 0.24, 80)
apparait(s, "#t-h2", T(247) + 0.08, 0.24, 80)
son(T(247), "swoosh-tourbillon", 0.4, "les deux quartiers")
prix(s, "t-p1", "PAR MOIS", 210000, 70, 920, T(252), 440, CIEL, 84, compte_de=0, d_compte=0.7)
prix(s, "t-p2", "PAR MOIS", 300000, 570, 920, T(262), 440, OR, 84, compte_de=210000, d_compte=0.6)
cache(s, "#t-d", T(252) - 0.15)
zoom(s, T(252) - 0.1, 330, 860, 1.18, 0.26)
pano(s, T(262) - 0.1, 750, 860, 1.18, 0.28)
zoom(s, T(266), 540, 900, 1.0, 0.28)
confettis(s, "t-cf", T(266), 540, 760, 18, 380)
s.ecrire()

# ================================================================ SCÈNE 12 : À RETENIR / À FAIRE
s = scene(11, "Retiens ça : l'indépendance se prépare avec le budget complet, pas seulement le loyer. À faire : additionne tes dépenses d'entrée et tes dépenses mensuelles avant de chercher")
fond_nuit(s)
ecran(s, "z-ec", 60, 340, 960, 300, [(s.debut, "separe-budgets"), (T(276), "calcul-depenses"), (T(284), "notes-stylo"), (T(290), "cle-remise")], s.debut, style="panneau")
cam(s, '<div id="z-carte" class="regle fin-carte" style="left: 60px; top: 680px; opacity: 0">'
       '<h3>À RETENIR</h3><p id="z-r" style="opacity: 0; font-size: 60px"><span id="z-sur" class="surl"></span><span class="txt">L’INDÉPENDANCE SE PRÉPARE AVEC LE BUDGET COMPLET, PAS SEULEMENT LE LOYER.</span></p>'
       '<h3 id="z-h2" class="h-faire" style="opacity: 0">À FAIRE</h3><p id="z-f" class="faire" style="opacity: 0; font-size: 50px">ADDITIONNE TES DÉPENSES D’ENTRÉE ET TES DÉPENSES MENSUELLES AVANT DE CHERCHER.<b id="z-ok" class="coche-ok" style="opacity: 0">✓</b></p></div>')
apparait(s, "#z-carte", T(269), 0.28, 120, 0.8)
son(T(269), "whoosh-tunnel", 0.45, "carte retiens ça")
apparait(s, "#z-r", T(271), 0.22, 30)
impact(T(271), 0.5, "l'indépendance")
s.j(f'tl.fromTo("#z-sur", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power2.out", immediateRender: false }}, {s.L(T(276))});')
son(T(276), "scintille-whoosh", 0.45, "budget complet")
zoom(s, T(271) - 0.1, 540, 860, 1.1, 0.3)
pano(s, T(282), 540, 1060, 1.1, 0.35)
apparait(s, "#z-h2", T(282), 0.2, 30)
apparait(s, "#z-f", T(284), 0.22, 30)
son(T(284), "pop-long", 0.45, "à faire")
s.j(f'tl.fromTo("#z-ok", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2)", immediateRender: false }}, {s.L(T(294))});')
son(T(294), "coche", 0.5, "coché")
zoom(s, T(292), 540, 960, 1.0, 0.35)
s.ecrire()

# ================================================================ SCÈNE 13 : abonne-toi ; tu prévois combien pour ton premier logement ?
s = scene(12, "Abonne-toi à Lefinancier. Tu prévois combien pour ton premier logement ?")
fond_nuit(s)
cam(s, '<div id="a-carte" class="profil" style="left: 140px; top: 330px; opacity: 0"><img src="assets/img/profil.png" alt="" />'
       '<div><b>Lefinancier</b><span>L’argent expliqué simplement</span></div>'
       '<div id="a-btn" class="btn">S’abonner</div><div id="a-ok" class="btn ok" style="opacity: 0">Abonné ✓</div></div>')
apparait(s, "#a-carte", s.debut + 0.05, 0.3, 120)
son(s.debut + 0.05, "swoosh-monte", 0.42, "carte profil")
cam(s, '<svg id="a-souris" class="souris" viewBox="0 0 40 52" style="left: 980px; top: 900px"><path d="M4 2 L4 40 L14 31 L21 48 L28 45 L21 29 L34 29 Z" fill="#fff" stroke="#0B1220" stroke-width="3" stroke-linejoin="round" /></svg>')
s.j(f'tl.to("#a-souris", {{ x: -300, y: -330, duration: 0.4, ease: "power2.inOut" }}, {s.L(T(296) - 0.3)});')
s.j(f'tl.to("#a-souris", {{ scale: 0.8, duration: 0.07, yoyo: true, repeat: 1 }}, {s.L(T(297))});')
s.j(f'tl.set("#a-btn", {{ opacity: 0 }}, {s.L(T(297) + 0.07)});')
s.j(f'tl.set("#a-ok", {{ opacity: 1 }}, {s.L(T(297) + 0.07)});')
son(T(297), "clic-souris", 0.5, "clic s'abonner")
son(T(297) + 0.1, "notif-positive", 0.42, "abonné")
confettis(s, "a-cf", T(297) + 0.1, 720, 620, 18, 340)
s.j(f'tl.to("#a-souris", {{ opacity: 0, duration: 0.15 }}, {s.L(T(298))});')
texte(s, "a-q", "TU PRÉVOIS COMBIEN<br>POUR TON PREMIER<br>LOGEMENT ?", 0, 720, 72, T(298), BLANC, w=1080)
cam(s, maison_html("a-h", 400, 1010, 280, 250, CIEL, "MOI"))
apparait(s, "#a-h", T(299), 0.24, 60)
son(T(299), "pop-cartoon", 0.4, "maison")
etiquette(s, "a-com", "DIS-LE EN COMMENTAIRE", 300, 1280, T(300), BLANC, NUIT, 40, -2)
s.ecrire()
# ================================================================ SOUS-TITRES (verticaux)
def ecrire_sous_titres():
    groupes, cur = [], []
    for i, m in enumerate(P.MOTS):
        cur.append(i)
        mot = P.TEXTE[i]
        suivant = P.TEXTE[i + 1] if i + 1 < len(P.TEXTE) else ""
        nombre = mot.isdigit() and suivant.rstrip(".,;:!?").isdigit()   # « 65 » + « 000 » : jamais coupés
        n_mots = len(cur) - sum(1 for j in cur if P.TEXTE[j].rstrip(".,;:!?") == "000")
        if not nombre and (mot[-1] in ".,;:!?…" or n_mots >= 3 or len(" ".join(P.TEXTE[j] for j in cur)) >= 18):
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

MUSIQUES = [  # Mixkit populaires (page hip-hop) : fichiers à −11,9 / −16,6 / −13,0 LUFS → ≈ −21 LUFS pour une voix à −15
    (0, "partie-1-hip-hop-02", COUPES[5], 0.35),
    (COUPES[5], "partie-2-complicated", round(COUPES[10] - COUPES[5], 2), 0.6),
    (COUPES[10], "partie-3-sweet-september", round(FIN - COUPES[10], 2), 0.4),
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
