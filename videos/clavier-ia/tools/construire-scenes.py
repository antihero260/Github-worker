#!/usr/bin/env python3
"""Écrit les 16 scènes de « clavier-ia » dans compositions/, le montage (index.html) et les masques du cadre.

Attention : relancer ce script ÉCRASE compositions/s*.html et le <body> de index.html
(il faut ensuite relancer tools/mixage.py pour le carve et le limiteur des musiques).
Bibliothèque partagée : hyperframes-style/outils/projecteur.py.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI.parent.parent / "hyperframes-style" / "outils"))
from projecteur import *  # noqa: E402,F403
from projecteur import Scene, init, t_mot  # noqa: E402
import projecteur as P  # noqa: E402

init(ICI)

ACCENT, CLAIR = "#DCFC1C", "#ECECE8"


def b(i):
    """Coupure de scène juste avant le mot i."""
    return round(t_mot(i) - 0.12, 2)


FIN = 96.0
COUPES = [0, b(22), b(40), b(62), b(67), b(88), b(98), b(119), b(143), b(159), b(176), b(195), b(205), b(228),
          b(255), b(271), FIN]
NOMS = ["s01-ia-connues", "s02-capables", "s03-tous-les-jours", "s04-clavier", "s05-suggestions", "s06-comment",
        "s07-modeles", "s08-analyse", "s09-exemple", "s10-pourquoi", "s11-habitudes", "s12-attention",
        "s13-calcule", "s14-principe", "s15-prochaine-fois", "s16-souviens-toi"]
assert len(NOMS) == len(COUPES) - 1


def scene(k, titre):
    return Scene(NOMS[k], COUPES[k], COUPES[k + 1], titre, premiere=(k == 0), derniere=(k == len(NOMS) - 1))


def mot(i):
    return P.TEXTE[i].replace("« ", "").replace(" »", "").replace("«", "").replace("»", "")


# ================================================================ SON
SFX = ICI / "assets/sfx"


def _pics():
    """Moment le plus fort de chaque bruitage (pour caler ce pic sur l'image) et sa durée."""
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
SONS = []  # (début, fichier, volume, note, durée)


def son(t, nom, v=0.4, note="", d=None, sur_pic=True):
    """Place un bruitage : par défaut son pic tombe exactement sur t."""
    p = PICS[nom]
    debut = t - (p["pic"] if sur_pic else 0)
    SONS.append((round(max(0.0, debut), 2), nom, v, note, round(min(d or p["duree"], p["duree"]), 2)))


TOURS = {}


def tour(liste):
    """Fait tourner les variantes d'un même type de son (moins répétitif)."""
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


ZOOM_IN = ["zoom-air", "zoom-swipe", "zoom-futur", "zoom-impact", "zoom-vide", "zoom-in-out", "zoom-scifi"]
ZOOM_OUT = ["swoosh-court", "souffle-air", "swoosh-accent", "swoosh-tourbillon"]
TRANSITIONS = ["souffle-rapide", "souffle-cine", "swoosh-vol", "souffle-air", "swoosh-court", "fouet", "swoosh-accent"]
POPS = ["pop-bulle", "pop-click", "pop-cartoon", "pop-sec", "pop-long"]


def zoom(s, g, px, py, sc, d=0.26, v=0.5, nom=None):
    """Recadrage filé + son de rush (zoom avant ou arrière)."""
    s.recadre(g, px, py, sc, d)
    son(g + d / 2, nom or tour(ZOOM_IN if sc > 1 else ZOOM_OUT), v, "rush de zoom")


def pop(t, v=0.42, note="apparition"):
    son(t, tour(POPS), v, note)


# ================================================================ ÉLÉMENTS
LOGOS = {"chatgpt": ("logo-openai.svg", "ChatGPT"), "claude": ("logo-claude.svg", "Claude"), "gemini": ("logo-gemini.svg", "Gemini")}


def carte_logo(cid, cle, x, y, w=230):
    f, nom = LOGOS[cle]
    return (f'<div id="{cid}" class="pj-logo" style="left: {x}px; top: {y}px; width: {w}px; opacity: 0">'
            f'<img src="assets/img/{f}" alt="{nom}" style="width: {w - 96}px; height: {w - 96}px" />'
            f'<div class="pj-logo-nom">{nom}</div></div>')


def panneau(s, pid, x, y, w, h, media, tag=None, piste=5):
    """Cadre photo/vidéo réel. media = ("video", fichier, début local, durée) ou ("img", fichier)."""
    if media[0] == "video":
        _, f, ds, dd = media
        m = (f'<video id="{pid}-v" class="clip" src="assets/video/{f}.mp4" data-start="{round(ds, 2)}" '
             f'data-duration="{round(dd, 2)}" data-track-index="{piste}" muted playsinline></video>')
    else:
        m = f'<img src="assets/img/{media[1]}" alt="" />'
    t = f'<div id="{pid}-tag" class="pj-panneau-tag">{tag}</div>' if tag else ""
    cam(s, f'<div id="{pid}" class="pj-panneau" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0">{m}'
           f'<div class="pj-equerres" style="left: -18px; top: -18px; right: -18px; bottom: -18px"><i></i><i></i><i></i><i></i></div>{t}</div>')


RANGS = ["AZERTYUIOP", "QSDFGHJKLM", "WXCVBN"]


def telephone(s, tid, x, y, champ=(), sugg=(), conv="", w=380, h=740):
    """Téléphone dessiné : champ de saisie (mots cachés), barre de 3 suggestions (jeux superposés), clavier AZERTY."""
    cellules = []
    for c in range(3):
        spans = "".join(f'<span id="{tid}-s{k}-{c}" style="opacity: 0">{mots[c]}</span>' for k, mots in enumerate(sugg))
        cellules.append(f'<div id="{tid}-c{c}" class="pj-tel-cell">{spans}</div>')
    touches = "".join('<div class="pj-tel-rang">' + "".join(f'<i id="{tid}-k{L}">{L}</i>' for L in r) + "</div>" for r in RANGS)
    touches += f'<div class="pj-tel-rang"><i id="{tid}-kesp" class="pj-tel-esp">espace</i></div>'
    mots_champ = " ".join(f'<span id="{tid}-w{k}" style="opacity: 0">{m}</span>' for k, m in enumerate(champ))
    cam(s, f'<div id="{tid}" class="pj-tel" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px">'
           f'<div class="pj-tel-tete">Messages</div><div id="{tid}-conv" class="pj-tel-conv">{conv}</div>'
           f'<div class="pj-tel-champ">{mots_champ}<b id="{tid}-curseur" class="pj-tel-curseur"></b></div>'
           f'<div class="pj-tel-sugg">{"".join(cellules)}</div><div class="pj-tel-clavier" data-layout-ignore>{touches}</div></div>')


SANS_ACCENT = str.maketrans("ÀÂÄÇÉÈÊËÎÏÔÖÙÛÜ", "AAACEEEEIIOOUUU")


def frappe(s, tid, texte, g0, g1):
    """Les touches du mot s'allument une à une entre g0 et g1, puis la barre d'espace."""
    lettres = [c for c in texte.upper().translate(SANS_ACCENT) if any(c in r for r in RANGS)] + ["esp"]
    pas = (g1 - g0) / max(1, len(lettres))
    dernier = {}
    for k, c in enumerate(lettres):
        t = round(g0 + k * pas, 3)
        if t - dernier.get(c, -9) < 0.13:
            continue
        dernier[c] = t
        s.j(f'tl.fromTo("#{tid}-k{c}", {{ backgroundColor: "{ACCENT}", color: "#000000" }}, '
            f'{{ backgroundColor: "#333333", color: "{CLAIR}", duration: 0.12, immediateRender: false }}, {s.L(t)});')


def tape_champ(s, tid, mots_temps, v=0.42, fin=None):
    """Mots du champ qui apparaissent à leurs temps (avec touches et son de clavier de téléphone)."""
    for k, (_, t, t_fin) in enumerate(mots_temps):
        s.montre(f"#{tid}-w{k}", t)
        frappe(s, tid, mots_temps[k][0], round(t - 0.25, 3), round(t_fin, 3))
    g0, g1 = mots_temps[0][1] - 0.25, fin or mots_temps[-1][2]
    son(g0, "clavier-tel-3", v, "frappe sur le téléphone", d=round(g1 - g0, 2), sur_pic=False)


def montre_sugg(s, tid, k, g, avant=None):
    if avant is not None:
        s.j(f'tl.to(["#{tid}-s{avant}-0", "#{tid}-s{avant}-1", "#{tid}-s{avant}-2"], {{ opacity: 0, duration: 0.08 }}, {s.L(g - 0.1)});')
    for c in range(3):
        s.j(f'tl.fromTo("#{tid}-s{k}-{c}", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.16, ease: "back.out(2)" }}, {s.L(g + c * 0.07)});')
    son(g, "notif-indice", 0.45, "suggestions")


def choisit(s, tid, c, g):
    s.j(f'tl.to("#{tid}-c{c}", {{ backgroundColor: "{ACCENT}", color: "#000000", duration: 0.08 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{tid}-c{c}", {{ scale: 1 }}, {{ keyframes: [{{ scale: 1.12, duration: 0.08 }}, {{ scale: 1, duration: 0.12 }}] }}, {s.L(g)});')
    son(g, "clic-positif", 0.45, "suggestion choisie")


def curseur(s, tid, g0, g1):
    n = max(1, int((g1 - g0) / 0.5) - 1)
    s.j(f'tl.fromTo("#{tid}-curseur", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.25, repeat: {n}, yoyo: true, ease: "steps(1)", immediateRender: false }}, {s.L(g0)});')


def serif_tape(s, sid, i1, i2, x, y, taille, largeur=1700, accent=()):
    spans = []
    for i in range(i1, i2 + 1):
        style = f' style="color: {ACCENT}"' if i in accent else ""
        spans.append(f'<span id="{sid}-{i}"{style}>{mot(i)}</span>')
        s.montre(f"#{sid}-{i}", t_mot(i))
    cam(s, f'<div id="{sid}" class="pj-serif" style="left: {x}px; top: {y}px; width: {largeur}px; font-size: {taille}px">{" ".join(spans)}</div>')


def carte_noire(s, cid, texte, g, taille=320):
    s.add(f'<div id="{cid}-noir" style="position: absolute; inset: 0; background: #000; opacity: 0"></div>'
          f'<div id="{cid}" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: {540 - taille // 2 - 20}px; '
          f'text-align: center; font-size: {taille}px; opacity: 0">{texte}</div>')
    s.j(f'tl.set("#{cid}-noir", {{ opacity: 1 }}, {s.L(g)});')
    s.choc(f"#{cid}", g)
    s.eclair(g)


def cache_carte_noire(s, cid, g):
    s.j(f'tl.set(["#{cid}-noir", "#{cid}"], {{ opacity: 0 }}, {s.L(g)});')


def barres(s, bid, x, y, w, lignes, g0, pas=0.28, ecart=128):
    html = []
    for k, (m, pct) in enumerate(lignes):
        html.append(f'<div id="{bid}-{k}" class="pj-barre" style="left: {x}px; top: {y + k * ecart}px; width: {w}px; opacity: 0">'
                    f'<div class="pj-barre-mot">{m}</div><div class="pj-barre-piste"><i id="{bid}-{k}-f"></i></div>'
                    f'<div id="{bid}-{k}-p" class="pj-barre-pct">0 %</div></div>')
        g = g0 + k * pas
        s.glisse(f"#{bid}-{k}", g, 140)
        s.j(f'tl.fromTo("#{bid}-{k}-f", {{ scaleX: 0 }}, {{ scaleX: {pct / 100}, duration: 0.6, ease: "power2.out" }}, {s.L(g + 0.1)});')
        s.compteur(f"#{bid}-{k}-p", g + 0.1, 0, pct, 0.6, "pct")
        pop(g, 0.38, "barre")
    cam(s, "".join(html))


def pensee(s, pid, texte, x, y, g, fin=None, taille=54):
    cam(s, f'<div id="{pid}" style="position: absolute; left: {x}px; top: {y}px; opacity: 0; transform-origin: 10% 100%">'
           f'<div class="pj-serif pj-pensee" style="position: relative; font-size: {taille}px">{texte}</div>'
           f'<i class="pj-bulle-rond" style="left: 30px; top: calc(100% + 14px); width: 34px; height: 34px"></i>'
           f'<i class="pj-bulle-rond" style="left: 6px; top: calc(100% + 58px); width: 20px; height: 20px"></i></div>')
    s.j(f'tl.fromTo("#{pid}", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.2)" }}, {s.L(g)});')
    if fin is not None:
        s.j(f'tl.to("#{pid}", {{ opacity: 0, scale: 0.8, duration: 0.15 }}, {s.L(fin)});')


def puce(s, pid, texte, x, y, g, style=""):
    """Étiquette centrée sur (x, y) : le conteneur (taille nulle) est animé, la puce est centrée dedans."""
    cam(s, f'<div id="{pid}" style="position: absolute; left: {x}px; top: {y}px; width: 0; height: 0; opacity: 0">'
           f'<div class="pj-puce" style="{style}">{texte}</div></div>')
    s.j(f'tl.fromTo("#{pid}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.4)" }}, {s.L(g)});')


def pluie(s, rid, g, d, n=54):
    """Pluie qui tombe devant la scène (positions fixes, répétitions finies)."""
    gouttes = []
    for k in range(n):
        x, y0 = (k * 97 + 31) % 1920, -((k * 53) % 420) - 90
        gouttes.append(f'<i id="{rid}-{k}" style="position: absolute; left: {x}px; top: {y0}px; width: 4px; height: {60 + (k * 13) % 50}px; '
                       f'background: rgba(236, 236, 232, 0.5); opacity: 0"></i>')
        duree = round(0.55 + (k % 5) * 0.06, 2)
        rep = max(1, int(d / duree) - 1)
        s.j(f'tl.fromTo("#{rid}-{k}", {{ y: 0, opacity: 1 }}, {{ y: 1400, opacity: 1, duration: {duree}, repeat: {rep}, ease: "none", immediateRender: false }}, {s.L(g + (k % 7) * 0.05)});')
    s.add(f'<div id="{rid}" style="position: absolute; inset: 0; overflow: hidden; pointer-events: none">{"".join(gouttes)}</div>')
    s.j(f'tl.to("#{rid}", {{ opacity: 0, duration: 0.3 }}, {s.L(g + d)});')


def mini_papiers(s, pid, n, depart, cible, g0, pas=0.1):
    html = []
    for k in range(n):
        x0, y0 = depart[0] + (k * 61) % 320, depart[1] - (k * 37) % 140
        lignes = "".join(f'<div style="height: 8px; width: {w}%; background: #b4b4ae; margin-top: 10px"></div>' for w in (90, 70, 84, 60, 78))
        html.append(f'<div id="{pid}-{k}" class="pj-mini-papier" style="left: {x0}px; top: {y0}px; opacity: 0">{lignes}</div>')
        s.j(f'tl.fromTo("#{pid}-{k}", {{ x: 0, y: 0, rotation: {(k * 47) % 60 - 30}, scale: 1, opacity: 1 }}, '
            f'{{ x: {cible[0] - x0 - 48}, y: {cible[1] - y0 - 62}, rotation: 0, scale: 0.15, opacity: 0, duration: 0.6, ease: "power2.in", immediateRender: false }}, {s.L(g0 + k * pas)});')
    cam(s, "".join(html))


# ================================================================ SCÈNES
# ---------------------------------------------------------------- S1 : les IA que tout le monde connaît
s = scene(0, "Scène 1 · « Quand on parle d'intelligence artificielle… ChatGPT, Claude ou Gemini. »")
cam(s, projecteur(700))
cam(s, perso("s01-toi", 560, 800, 420))
serif_tape(s, "s01-dit", 0, 4, 113, 200, 84, 980, accent=(3, 4))
s.add(hud_g("s01-hud", "Intelligence artificielle", "Ce qui vient à l'esprit"))
for k, (cle, i) in enumerate((("chatgpt", 18), ("claude", 19), ("gemini", 21))):
    cam(s, carte_logo(f"s01-logo{k}", cle, 930 + k * 270, 250))
    s.claque(f"#s01-logo{k}", t_mot(i), 1.7)
    pop(t_mot(i), 0.45, f"logo {cle}")
marche(s, "s01-toi", 0.1, 1.3, 180)
vit(s, "s01-toi", 1.35, s.fin - 0.2)
gratte(s, "s01-toi", t_mot(6))
pensee(s, "s01-pense", "Hmm… l'IA ?", 800, 250, t_mot(8), fin=t_mot(15))
pop(t_mot(8), 0.35, "bulle de pensée")
s.cache("#s01-dit", t_mot(8) - 0.12)
pose(s, "s01-toi", t_mot(17), 0.16, "back.out(2)", bd=-100, tete=-8)
zoom(s, t_mot(17) - 0.1, 1240, 440, 1.22)
saut(s, "s01-toi", t_mot(19), 26)
pose(s, "s01-toi", t_mot(21), 0.14, "back.out(2)", bd=-150)
saut(s, "s01-toi", t_mot(21), 34)
zoom(s, t_mot(21) + 0.4, 960, 540, 1.0)
acquiesce(s, "s01-toi", t_mot(21) + 0.45, 2)
s.ecrire()

# ---------------------------------------------------------------- S2 : ce que savent faire ces IA
s = scene(1, "Scène 2 · « Des IA capables de répondre à nos questions, de rédiger des textes, ou même de créer des images. »")
cam(s, projecteur(560))
cam(s, perso("s02-ia", 560, 800, 430, "ia"))
icones = (
    '<b class="pj-icone">?</b>',
    '<b class="pj-icone" style="font-size: 44px">Aa</b>',
    '<b class="pj-icone"><svg viewBox="0 0 60 48" style="width: 56px; height: 46px"><rect x="3" y="3" width="54" height="42" fill="none" stroke="#000" stroke-width="6" />'
    '<path d="M8 40 L24 20 L34 32 L42 24 L54 40 Z" fill="#000" /><circle cx="44" cy="14" r="5" fill="#000" /></svg></b>',
)
textes = ("Répondre à tes questions", "Rédiger des textes", "Créer des images")
for k in range(3):
    cam(s, f'<div id="s02-cap{k}" class="pj-carte" style="left: 960px; top: {170 + k * 205}px; width: 820px; padding: 26px 30px; '
           f'text-align: left; font-size: 56px; white-space: nowrap; opacity: 0">{icones[k]}{textes[k]}</div>')
s.add(hud_g("s02-hud", "Les IA connues", "Ce qu'elles savent faire"))
s.j(f'tl.set("#s02-ia", {{ x: -760 }}, 0);')
court(s, "s02-ia", s.debut + 0.05, t_mot(24), 760)
son(s.debut + 0.3, "swoosh-vitesse", 0.4, "l'IA arrive en courant")
vit(s, "s02-ia", t_mot(24) + 0.05, s.fin - 0.2)
for k, i in enumerate((26, 31, 37)):
    s.glisse(f"#s02-cap{k}", t_mot(i), 320)
    son(t_mot(i), tour(["swoosh-accent", "swoosh-court", "swoosh-vol"]), 0.42, "carte qui glisse")
    pose(s, "s02-ia", t_mot(i), 0.14, "back.out(2)", bd=-100 - k * 22, tete=-6)
parle(s, "s02-ia", t_mot(27), t_mot(30), "bg")
zoom(s, t_mot(26) - 0.12, 1150, 400, 1.12)
zoom(s, t_mot(31) - 0.12, 1150, 480, 1.12)
zoom(s, t_mot(37) - 0.12, 1150, 560, 1.15)
saut(s, "s02-ia", t_mot(37), 34)
acquiesce(s, "s02-ia", t_mot(39), 2)
s.ecrire()

# ---------------------------------------------------------------- S3 : quelque chose que tu utilises tous les jours
s = scene(2, "Scène 3 · « …quelque chose que tu utilises probablement tous les jours sans même réaliser qu'il fait appel à l'IA. »")
d3 = round(s.fin - s.debut, 2)
panneau(s, "s03-vid", 150, 236, 860, 484, ("video", "cuisine-telephone", 0, d3), "Toi · tous les jours", piste=5)
cam(s, perso("s03-toi", 1460, 800, 420))
cam(s, projecteur(1460, op=0.8))
cam(s, '<div id="s03-q" class="pj-impact" style="position: absolute; left: 1610px; top: 170px; font-size: 240px; opacity: 0">?</div>')
jours = "".join(f'<div id="s03-j{k}" class="pj-jour">{j}</div>' for k, j in enumerate("LMMJVSD"))
cam(s, f'<div id="s03-semaine" style="position: absolute; left: 150px; top: 748px; display: flex; gap: 14px; opacity: 0">{jours}</div>')
s.add(hud_g("s03-hud", "Sans le savoir", "Tous les jours"))
s.glisse("#s03-vid", t_mot(40), -500)
son(t_mot(40), "swoosh-vitesse", 0.42, "la vidéo glisse")
vit(s, "s03-toi", s.debut, s.fin - 0.2)
s.claque("#s03-q", t_mot(44), 1.9)
pop(t_mot(44), 0.45, "point d'interrogation")
gratte(s, "s03-toi", t_mot(45))
marche(s, "s03-toi", t_mot(48) + 0.2, t_mot(50) - 0.1, -160)
s.apparait("#s03-semaine", t_mot(50), 20)
for k in range(7):
    s.j(f'tl.to("#s03-j{k}", {{ backgroundColor: "{ACCENT}", color: "#000000", duration: 0.06 }}, {s.L(t_mot(50) + 0.1 + k * 0.09)});')
for k in range(0, 7, 2):
    son(t_mot(50) + 0.1 + k * 0.09, "coche", 0.4, "jour coché")
zoom(s, t_mot(50) - 0.1, 600, 600, 1.12)
pose(s, "s03-toi", t_mot(50), 0.16, "back.out(2)", bg=100, tete=6)
haussement(s, "s03-toi", t_mot(54))
tampon(s, "s03-ia", "IA ?", 700, 300, t_mot(60), -8, 120)
son(t_mot(60), "impact-basse", 0.55, "tampon IA ?")
zoom(s, t_mot(60) - 0.15, 640, 470, 1.25)
saut(s, "s03-toi", t_mot(60), 30)
s.ecrire()

# ---------------------------------------------------------------- S4 : le clavier de ton téléphone (vraie vidéo plein cadre)
s = scene(3, "Scène 4 · « Le clavier de ton téléphone. »")
d4 = round(s.fin - s.debut, 2)
cam(s, f'<div id="s04-plein" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden">'
       f'<video id="s04-v" class="clip" src="assets/video/clavier-gros-plan.mp4" data-start="0" data-duration="{d4}" data-track-index="5" '
       f'muted playsinline style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover"></video>'
       f'<div style="position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.25), rgba(0,0,0,0.72))"></div></div>')
cam(s, '<div id="s04-t1" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 250px; text-align: center; font-size: 230px; opacity: 0">Le clavier</div>')
cam(s, '<div id="s04-t2" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 500px; text-align: center; font-size: 130px; color: #ECECE8; text-shadow: none; opacity: 0">de ton téléphone.</div>')
s.add(hud_g("s04-hud", "La réponse", "Dans ta poche"))
s.choc("#s04-t1", t_mot(63))
s.eclair(t_mot(62))
son(t_mot(62), "impact-whoosh", 0.6, "révélation : le clavier")
s.glisse("#s04-t2", t_mot(64), 260)
son(t_mot(64), "swoosh-accent", 0.42, "texte qui glisse")
s.j(f'tl.fromTo("#s04-plein", {{ scale: 1.0 }}, {{ scale: 1.12, duration: {d4}, ease: "none" }}, 0);')
zoom(s, t_mot(65) - 0.1, 960, 520, 1.12)
s.ecrire()

# ---------------------------------------------------------------- S5 : le mot suivant proposé
s = scene(4, "Scène 5 · « …ton téléphone te propose automatiquement le mot suivant. »")
cam(s, projecteur(560))
cam(s, perso("s05-toi", 560, 800, 420))
telephone(s, "s05-tel", 1090, 110, champ=("Je", "suis", "en", "retard"),
          sugg=(("route", "retard", "train"),),
          conv='<div class="pj-tel-bulle" style="right: 16px; top: 30px">On se rejoint à 8 h ?</div>')
s.add(hud_g("s05-hud", "Ton téléphone", "Te souffle le mot suivant"))
s.j('tl.set("#s05-tel", { y: 700, opacity: 0 }, 0);')
s.j(f'tl.to("#s05-tel", {{ y: 0, opacity: 1, duration: 0.32, ease: "back.out(1.4)" }}, {s.L(t_mot(67))});')
son(t_mot(67) + 0.2, "swoosh-monte", 0.45, "le téléphone monte")
vit(s, "s05-toi", s.debut, s.fin - 0.2)
pose(s, "s05-toi", t_mot(71), 0.16, "back.out(2)", bd=-80, tete=-6)
oui(s, "s05-toi", t_mot(72))
tape(s, "s05-toi", t_mot(75) - 0.3, t_mot(80))
curseur(s, "s05-tel", s.debut + 0.3, t_mot(75) - 0.3)
tape_champ(s, "s05-tel", [("Je", t_mot(75), t_mot(76)), ("suis", t_mot(77), t_mot(78)), ("en", t_mot(79), t_mot(80))])
zoom(s, t_mot(75) - 0.35, 1100, 440, 1.2)
montre_sugg(s, "s05-tel", 0, t_mot(83))
zoom(s, t_mot(83) - 0.12, 1280, 520, 1.55)
saut(s, "s05-toi", t_mot(84), 36)
pose(s, "s05-toi", t_mot(84), 0.14, "back.out(2)", bg=150, bd=-150)
choisit(s, "s05-tel", 1, t_mot(86))
s.montre("#s05-tel-w3", t_mot(86) + 0.12)
s.ecrire()

# ---------------------------------------------------------------- S6 : comment fait-il ?
s = scene(5, "Scène 6 · « Mais comment fait-il pour deviner ce que tu vas écrire ? »")
cam(s, projecteur(960))
cam(s, perso("s06-toi", 960, 800, 430))
serif_tape(s, "s06-dit", 89, 97, 110, 220, 66, 1700, accent=(92,))
s.css.append("    #s06-dit { text-align: center; }")
for k, (x, y, t, i) in enumerate(((500, 450, 150, 89), (1300, 430, 200, 92), (1540, 580, 130, 96))):
    cam(s, f'<div id="s06-q{k}" class="pj-impact" style="position: absolute; left: {x}px; top: {y}px; font-size: {t}px; opacity: 0">?</div>')
    s.claque(f"#s06-q{k}", t_mot(i), 2)
    pop(t_mot(i), 0.42, "point d'interrogation")
s.add(hud_g("s06-hud", "Question", "Comment devine-t-il ?"))
vit(s, "s06-toi", s.debut, s.fin - 0.2)
gratte(s, "s06-toi", t_mot(89))
pose(s, "s06-toi", t_mot(92), 0.12, bd=0, tete=0)
haussement(s, "s06-toi", t_mot(93))
vertiges(s, "s06-toi", t_mot(95), 960, 330, 1.0)
zoom(s, t_mot(91), 960, 520, 1.12)
s.ecrire()

# ---------------------------------------------------------------- S7 : des modèles entraînés sur beaucoup de texte
s = scene(6, "Scène 7 · « …des modèles entraînés sur de grandes quantités de texte pour apprendre les relations entre les mots. »")
cam(s, projecteur(560))
cam(s, perso("s07-ia", 560, 800, 410, "ia"))
cam(s, '<div id="s07-modele" class="pj-sticker" style="left: 400px; top: 200px; font-size: 64px; opacity: 0">Modèle</div>')
segs = "".join('<i class="s07-seg" style="flex: 1; height: 34px; background: #2a2a2a"></i>' for _ in range(10))
cam(s, f'<div id="s07-jauge" style="position: absolute; left: 1030px; top: 300px; width: 720px; opacity: 0">'
       f'<div class="pj-label" style="position: static"><span class="pj-k">Textes lus</span><span class="pj-d">Livres, articles, messages…</span></div>'
       f'<div style="display: flex; gap: 8px; margin-top: 16px">{segs}</div>'
       f'<div id="s07-pct" class="pj-stat" style="position: static; font-size: 72px; margin-top: 10px">0 %</div></div>')
mini_papiers(s, "s07-pap", 16, (1300, -170), (560, 430), t_mot(107) - 0.2, 0.09)
# le réseau des mots
noeuds = {"il va": (1130, 330), "pleuvoir": (1470, 250), "nuages": (1430, 520), "ciel": (1760, 400), "gris": (1150, 610),
          "parapluie": (1720, 650)}
liens = (("ciel", "nuages"), ("nuages", "pleuvoir"), ("il va", "pleuvoir"), ("ciel", "gris"), ("pleuvoir", "parapluie"),
         ("gris", "nuages"), ("ciel", "pleuvoir"))
traits = []
for k, (a, c) in enumerate(liens):
    (x1, y1), (x2, y2) = noeuds[a], noeuds[c]
    long_ = round(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    traits.append(f'<line id="s07-l{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ACCENT}" stroke-width="5" '
                  f'stroke-dasharray="{long_}" stroke-dashoffset="{long_}" />')
    s.j(f'tl.to("#s07-l{k}", {{ attr: {{ "stroke-dashoffset": 0 }}, duration: 0.3, ease: "power2.out" }}, {s.L(t_mot(115) + 0.1 + k * 0.1)});')
cam(s, f'<svg id="s07-reseau" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: visible" viewBox="0 0 1920 1080">{"".join(traits)}</svg>')
for k, (m, (x, y)) in enumerate(noeuds.items()):
    puce(s, f"s07-n{k}", m, x, y, t_mot(115) + k * 0.09)
son(t_mot(115), "glitch-ok", 0.42, "réseau des mots")
pop(t_mot(115) + 0.2, 0.36)
pop(t_mot(115) + 0.45, 0.36)
serif_tape(s, "s07-dit", 98, 102, 900, 300, 84, 900, accent=(101,))
s.add(hud_g("s07-hud", "En réalité", "Un modèle entraîné"))
vit(s, "s07-ia", s.debut, s.fin - 0.2)
parle(s, "s07-ia", t_mot(99), t_mot(103))
s.cache("#s07-dit", t_mot(104) - 0.15)
s.claque("#s07-modele", t_mot(104), 1.8)
son(t_mot(104), "impact-cartoon", 0.5, "étiquette MODÈLE")
zoom(s, t_mot(104) - 0.12, 560, 400, 1.3)
zoom(s, t_mot(107) - 0.25, 960, 540, 1.0)
s.apparait("#s07-jauge", t_mot(108))
s.j(f'tl.to(".s07-seg", {{ backgroundColor: "{ACCENT}", duration: 0.04, stagger: 0.14 }}, {s.L(t_mot(108))});')
s.compteur("#s07-pct", t_mot(108), 0, 100, 1.4, "pct")
for k in range(3):
    son(t_mot(107) + k * 0.5, tour(["swoosh-court", "souffle-air", "swoosh-accent"]), 0.38, "les textes volent vers le modèle")
son(t_mot(109), "glitch-data", 0.3, "données absorbées")
tape(s, "s07-ia", t_mot(108), t_mot(112))
grossit(s, "s07-ia", t_mot(112), 1.12)
s.cache("#s07-jauge", t_mot(114))
s.cache("#s07-modele", t_mot(114))
zoom(s, t_mot(115) - 0.12, 1420, 450, 1.22)
pose(s, "s07-ia", t_mot(115), 0.16, "back.out(2)", bd=-100, tete=-8)
acquiesce(s, "s07-ia", t_mot(117), 2)
s.ecrire()

# ---------------------------------------------------------------- S8 : il analyse, le contexte, les mots probables
s = scene(7, "Scène 8 · « Il analyse ce que tu viens d'écrire, tient compte du contexte et évalue les mots les plus probables. »")
d8 = round(s.fin - s.debut, 2)
panneau(s, "s08-vid", 113, 190, 780, 439, ("video", "rue-telephone", 0, d8), "Ce que tu viens d'écrire", piste=5)
cam(s, '<div id="s08-scan" style="position: absolute; left: 113px; top: 190px; width: 780px; height: 10px; background: #DCFC1C; '
       'box-shadow: 0 0 30px rgba(220, 252, 28, 0.9); opacity: 0"></div>')
cam(s, '<div id="s08-ctx" class="pj-label" style="left: 113px; top: 680px; opacity: 0"><span class="pj-k">Contexte</span>'
       '<span class="pj-d" style="color: #ECECE8">« Je suis en… »</span></div>')
cam(s, perso("s08-ia", 1010, 800, 300, "ia"))
barres(s, "s08-b", 1140, 220, 660, (("retard", 64), ("route", 23), ("train", 13)), t_mot(131))
cam(s, '<div id="s08-choix" class="pj-sticker" style="left: 1500px; top: 560px; font-size: 54px; opacity: 0">→ Proposé</div>')
s.add(hud_g("s08-hud", "Analyse", "Contexte + probabilités", "opacity: 0"))
s.apparait("#s08-hud", s.debut + 0.1)
s.apparait("#s08-vid", s.debut + 0.05, 40)
vit(s, "s08-ia", s.debut, s.fin - 0.2)
s.j(f'tl.set("#s08-scan", {{ opacity: 1 }}, {s.L(t_mot(120))});')
s.j(f'tl.fromTo("#s08-scan", {{ y: 0 }}, {{ y: 429, duration: 0.6, repeat: 2, yoyo: true, ease: "sine.inOut", immediateRender: false }}, {s.L(t_mot(120))});')
s.j(f'tl.to("#s08-scan", {{ opacity: 0, duration: 0.1 }}, {s.L(t_mot(120) + 1.85)});')
son(t_mot(120), "zoom-scifi", 0.42, "balayage d'analyse")
son(t_mot(120) + 0.7, "glitch-court", 0.3, "analyse")
pose(s, "s08-ia", t_mot(120), 0.16, "back.out(2)", bg=110, tete=8)
zoom(s, t_mot(120) - 0.15, 520, 420, 1.25)
zoom(s, t_mot(126) - 0.1, 960, 540, 1.0)
s.apparait("#s08-ctx", t_mot(127))
son(t_mot(129), "coche", 0.45, "contexte")
pose(s, "s08-ia", t_mot(129), 0.12, bg=0)
acquiesce(s, "s08-ia", t_mot(129), 2)
s.cache("#s08-ctx", t_mot(131) - 0.1)
zoom(s, t_mot(131) - 0.15, 1400, 400, 1.22)
pose(s, "s08-ia", t_mot(132), 0.16, "back.out(2)", bd=-105, tete=-8)
s.j(f'tl.to("#s08-b-0", {{ keyframes: [{{ scale: 1.06, duration: 0.1 }}, {{ scale: 1, duration: 0.14 }}] }}, {s.L(t_mot(142))});')
s.claque("#s08-choix", t_mot(142), 1.8)
son(t_mot(142), "bonne-reponse", 0.45, "mot proposé")
saut(s, "s08-ia", t_mot(142), 30)
s.ecrire()

# ---------------------------------------------------------------- S9 : « Le ciel est couvert, il va… » → « pleuvoir »
s = scene(8, "Scène 9 · « Imagine que tu écrives : « Le ciel est couvert, il va… » Ton clavier peut te proposer « pleuvoir ». »")
panneau(s, "s09-ciel", 113, 200, 760, 427, ("img", "photo-nuages-pluie.jpg"), "Le ciel est couvert")
champ9 = [mot(i) for i in range(147, 153)] + ["pleuvoir"]
telephone(s, "s09-tel", 1010, 100, champ=champ9, sugg=(("pleuvoir", "faire", "être"),))
cam(s, perso("s09-toi", 1660, 800, 380))
s.add(hud_g("s09-hud", "Exemple", "Ton clavier devine"))
vit(s, "s09-toi", s.debut, s.fin - 0.2)
pose(s, "s09-toi", t_mot(143), 0.16, "back.out(2)", bg=100, tete=6)
s.glisse("#s09-ciel", t_mot(147) + 0.1, -400)
son(t_mot(147) + 0.1, "swoosh-vol", 0.4, "photo du ciel")
son(t_mot(148), "tonnerre", 0.32, "ciel couvert", d=3.5)
tape(s, "s09-toi", t_mot(147) - 0.2, t_mot(153))
curseur(s, "s09-tel", s.debut + 0.2, t_mot(147) - 0.3)
mt = [(champ9[k], t_mot(147 + k), t_mot(148 + k)) for k in range(6)]
tape_champ(s, "s09-tel", mt)
zoom(s, t_mot(147) - 0.3, 1200, 400, 1.35)
son(t_mot(158), "riser-synth", 0.38, "montée vers « pleuvoir »")
montre_sugg(s, "s09-tel", 0, t_mot(155))
zoom(s, t_mot(155) - 0.12, 1200, 480, 1.55)
choisit(s, "s09-tel", 0, t_mot(158))
s.montre("#s09-tel-w6", t_mot(158) + 0.1)
s.eclair(t_mot(158))
son(t_mot(158), "impact-futur", 0.55, "PLEUVOIR")
pluie(s, "s09-pluie", t_mot(158), s.fin - t_mot(158) - 0.1)
son(t_mot(158), "pluie", 0.3, "la pluie tombe", d=round(s.fin - t_mot(158) + 0.4, 2), sur_pic=False)
zoom(s, t_mot(158) + 0.35, 1150, 520, 1.0)
victoire(s, "s09-toi", t_mot(158), 2)
s.ecrire()

# ---------------------------------------------------------------- S10 : pourquoi ? parce qu'il l'a appris
s = scene(9, "Scène 10 · « Pourquoi ? Parce qu'il a appris qu'après une phrase comme celle-ci, « pleuvoir » est une suite probable. »")
cam(s, projecteur(420))
cam(s, perso("s10-ia", 420, 800, 380, "ia"))
phrases = ("« Le ciel est couvert, il va <b>pleuvoir</b>. »", "« Ciel gris ce matin : il va <b>pleuvoir</b>. »",
           "« Nuages noirs… il va <b>pleuvoir</b> ! »")
lignes = "".join(f'<div id="s10-ph{k}" class="pj-ligne-appris" style="opacity: 0">{p}</div>' for k, p in enumerate(phrases))
cam(s, f'<div id="s10-memoire" class="pj-papier" style="left: 760px; top: 180px; width: 1050px; padding: 30px 40px; opacity: 0">'
       f'<div class="pj-label" style="position: static; color: #0a0a06">Textes déjà vus</div>{lignes}</div>')
tampon(s, "s10-prob", "Suite probable ✓", 1080, 620, t_mot(174), -5, 80)
s.add(hud_g("s10-hud", "Pourquoi ?", "Il l'a appris"))
carte_noire(s, "s10-carte", "Pourquoi ?", t_mot(159), 300)
son(t_mot(159), "impact-basse", 0.6, "POURQUOI ?")
cache_carte_noire(s, "s10-carte", t_mot(160) - 0.05)
son(t_mot(160) - 0.05, "swoosh-court", 0.4, "retour à la scène")
vit(s, "s10-ia", s.debut, s.fin - 0.2)
parle(s, "s10-ia", t_mot(160), t_mot(163) - 0.25, "bg")
s.apparait("#s10-memoire", t_mot(163) - 0.1)
for k, i in enumerate((163, 165, 167)):
    s.glisse(f"#s10-ph{k}", t_mot(i), 200)
    pop(t_mot(i), 0.36, "phrase apprise")
s.j(f'tl.to("#s10-memoire b", {{ backgroundColor: "{ACCENT}", duration: 0.06, stagger: 0.12 }}, {s.L(t_mot(171))});')
son(t_mot(171), "etincelles", 0.38, "« pleuvoir » surligné")
pose(s, "s10-ia", t_mot(163), 0.16, "back.out(2)", bd=-100, tete=-8)
zoom(s, t_mot(163) - 0.2, 1280, 340, 1.25)
zoom(s, t_mot(171) - 0.15, 1280, 400, 1.4)
zoom(s, t_mot(174) - 0.15, 1000, 520, 1.0)
son(t_mot(174), "impact-cartoon", 0.5, "tampon suite probable")
pouce(s, "s10-ia", t_mot(175))
saut(s, "s10-ia", t_mot(175), 28)
s.ecrire()

# ---------------------------------------------------------------- S11 : il s'adapte à tes habitudes
s = scene(10, "Scène 11 · « …certains claviers peuvent aussi s'adapter à tes habitudes de saisie pour améliorer leurs suggestions. »")
cam(s, projecteur(380))
cam(s, perso("s11-toi", 380, 800, 400))
telephone(s, "s11-tel", 1400, 100, sugg=(("bonjour", "merci", "oui"), ("à plus !", "mdr", "grave")),
          conv='<div class="pj-tel-bulle" style="left: 16px; top: 30px; background: #2a2a2a; color: #ECECE8">Tu viens ce soir ?</div>')
cam(s, '<div id="s11-carte" class="pj-papier" style="left: 700px; top: 190px; width: 560px; padding: 28px 34px; opacity: 0">'
       '<h3 style="font-size: 72px">Tes habitudes</h3></div>')
for k, m in enumerate(("« mdr »", "« à plus ! »", "« ok ça marche »")):
    puce(s, f"s11-h{k}", m, 980, 400 + k * 92, t_mot(188) + k * 0.16, "font-family: 'Instrument Serif', serif; font-style: italic; text-transform: none; font-size: 50px")
tampon(s, "s11-ok", "Adapté à toi", 1430, 330, t_mot(192) + 0.1, -6, 70)
s.add(hud_g("s11-hud", "Et ce n'est pas tout", "Il apprend tes habitudes"))
s.j(f'tl.set(["#s11-tel-s0-0", "#s11-tel-s0-1", "#s11-tel-s0-2"], {{ opacity: 1 }}, 0);')
vit(s, "s11-toi", s.debut, s.fin - 0.2)
pose(s, "s11-toi", t_mot(176), 0.14, "back.out(2)", bd=-140, tete=-6)
saut(s, "s11-toi", t_mot(178), 26)
zoom(s, t_mot(176) - 0.05, 960, 520, 1.12)
tape(s, "s11-toi", t_mot(181), t_mot(186))
son(t_mot(181), "clavier-tel", 0.36, "il tape ses messages", d=round(t_mot(186) - t_mot(181), 2), sur_pic=False)
s.apparait("#s11-carte", t_mot(185))
son(t_mot(185), "swoosh-monte", 0.4, "carte habitudes")
for k in range(3):
    pop(t_mot(188) + k * 0.16, 0.38, "habitude")
zoom(s, t_mot(187) - 0.1, 980, 460, 1.25)
# les habitudes filent dans le téléphone
for k in range(3):
    s.j(f'tl.to("#s11-h{k}", {{ x: {1590 - 980}, y: {640 - 400 - k * 92}, scale: 0.3, opacity: 0, duration: 0.4, ease: "power2.in" }}, {s.L(t_mot(191) + k * 0.08)});')
son(t_mot(191) + 0.2, "zoom-futur", 0.45, "les habitudes entrent dans le téléphone")
s.cache("#s11-carte", t_mot(191) + 0.3)
zoom(s, t_mot(191) + 0.05, 1590, 480, 1.2)
montre_sugg(s, "s11-tel", 1, t_mot(192) + 0.1, avant=0)
son(t_mot(193), "notif-positive", 0.42, "suggestions améliorées")
pouce(s, "s11-toi", t_mot(193))
s.ecrire()

# ---------------------------------------------------------------- S12 : attention, il ne lit pas dans tes pensées
s = scene(11, "Scène 12 · « Mais attention : ton téléphone ne lit pas dans tes pensées. »")
cam(s, projecteur(640))
cam(s, perso("s12-toi", 640, 800, 420))
telephone(s, "s12-tel", 1350, 120, sugg=(("…", "…", "…"),))
cam(s, '<div id="s12-lire" class="pj-impact" style="position: absolute; left: 980px; top: 360px; font-size: 96px; color: #ECECE8; text-shadow: none; opacity: 0">'
       'Lire tes pensées<div id="s12-rature" style="position: absolute; left: -10px; right: -10px; top: 48%; height: 14px; background: #DCFC1C"></div></div>')
s.add(hud_g("s12-hud", "Attention", "Pas de télépathie"))
carte_noire(s, "s12-carte", "Attention", t_mot(196), 300)
son(t_mot(196), "impact-futur", 0.6, "ATTENTION")
cache_carte_noire(s, "s12-carte", t_mot(197) - 0.05)
son(t_mot(197) - 0.05, "swoosh-court", 0.4, "retour à la scène")
s.j(f'tl.set(["#s12-tel-s0-0", "#s12-tel-s0-1", "#s12-tel-s0-2"], {{ opacity: 1 }}, 0);')
s.j('tl.set("#s12-rature", { scaleX: 0, transformOrigin: "0% 50%" }, 0);')
vit(s, "s12-toi", s.debut, s.fin - 0.2)
pensee(s, "s12-pense", "Pizza ce soir ?", 760, 170, t_mot(198), taille=58)
pop(t_mot(198), 0.4, "pensée")
non(s, "s12-toi", t_mot(200))
s.apparait("#s12-lire", t_mot(200))
s.j(f'tl.to("#s12-rature", {{ scaleX: 1, duration: 0.16, ease: "power2.out" }}, {s.L(t_mot(204))});')
son(t_mot(204), "buzz-faux", 0.42, "rayé : lire tes pensées")
zoom(s, t_mot(199) - 0.1, 1250, 420, 1.2)
haussement(s, "s12-toi", t_mot(204))
s.ecrire()

# ---------------------------------------------------------------- S13 : il calcule la suite la plus probable
s = scene(12, "Scène 13 · « Il ne sait pas ce que tu veux dire. Il calcule simplement la suite la plus probable… »")
cam(s, projecteur(560))
cam(s, perso("s13-ia", 560, 800, 410, "ia"))
barres(s, "s13-b", 1060, 200, 760, (("pleuvoir", 87), ("neiger", 9), ("danser", 4)), t_mot(216) + 0.1)
cam(s, '<div id="s13-top" class="pj-sticker" style="left: 1250px; top: 548px; font-size: 50px; opacity: 0">↑ La plus probable</div>')
for k, m in enumerate(("Mots d'avant", "Contexte", "Tes habitudes")):
    puce(s, f"s13-i{k}", m, 1170 + k * 270, 730, t_mot(226) + k * 0.14, "font-size: 38px")
s.add(hud_g("s13-hud", "Calcul", "La suite probable"))
vit(s, "s13-ia", s.debut, s.fin - 0.2)
bulle(s, "s13-b1", "Ce que tu veux dire ?", 700, 230, t_mot(208), 50, fin=t_mot(215))
pop(t_mot(208), 0.4, "bulle")
haussement(s, "s13-ia", t_mot(209))
non(s, "s13-ia", t_mot(211))
zoom(s, t_mot(207) - 0.1, 760, 380, 1.3)
zoom(s, t_mot(215), 960, 540, 1.0)
tape(s, "s13-ia", t_mot(216), t_mot(222))
son(t_mot(216), "clavier-bit", 0.32, "le modèle calcule", d=round(t_mot(222) - t_mot(216), 2), sur_pic=False)
son(t_mot(216), "glitch-court", 0.36, "calcul")
s.claque("#s13-top", t_mot(222), 1.8)
son(t_mot(222), "bonne-reponse", 0.45, "la plus probable")
s.j(f'tl.to("#s13-b-0", {{ keyframes: [{{ scale: 1.06, duration: 0.1 }}, {{ scale: 1, duration: 0.14 }}] }}, {s.L(t_mot(222))});')
zoom(s, t_mot(221) - 0.1, 1400, 380, 1.2)
for k in range(3):
    pop(t_mot(226) + k * 0.14, 0.36, "information disponible")
zoom(s, t_mot(225) - 0.1, 1300, 540, 1.1)
pose(s, "s13-ia", t_mot(226), 0.16, "back.out(2)", bd=-110, tete=-8)
saut(s, "s13-ia", t_mot(227), 26)
s.ecrire()

# ---------------------------------------------------------------- S14 : un principe fondamental (avant → après)
s = scene(13, "Scène 14 · « Un principe fondamental… utiliser ce qui vient avant pour anticiper ce qui pourrait venir après. »")
cam(s, projecteur(470) + projecteur(780, op=0.8))
cam(s, perso("s14-toi", 470, 800, 380))
cam(s, perso("s14-ia", 780, 800, 360, "ia"))
cam(s, '<div id="s14-titre" class="pj-serif" style="left: 113px; top: 160px; width: 1700px; font-size: 120px">'
       '<span id="s14-t0">Un principe</span> <span id="s14-t1" style="color: #DCFC1C">fondamental.</span></div>')
for k, (cle, i) in enumerate((("chatgpt", 235), ("claude", 236), ("gemini", 237))):
    cam(s, carte_logo(f"s14-logo{k}", cle, 1000 + k * 270, 200, 210))
cam(s, '<div id="s14-langage" class="pj-sticker" style="left: 1120px; top: 500px; font-size: 60px; opacity: 0">Le langage</div>')
# frise avant → après
frise = [("ciel", 1080), ("couvert", 1290), ("il va", 1500)]
for k, (m, x) in enumerate(frise):
    puce(s, f"s14-f{k}", m, x, 640, t_mot(243) + k * 0.15)
cam(s, '<div id="s14-avant" class="pj-label" style="left: 1010px; top: 540px; opacity: 0"><span class="pj-k">Avant</span></div>')
cam(s, '<div id="s14-fleche" style="position: absolute; left: 1600px; top: 632px; width: 90px; height: 16px; background: #DCFC1C; transform-origin: 0% 50%"></div>')
cam(s, '<div id="s14-q" style="position: absolute; left: 1760px; top: 640px; width: 0; height: 0; opacity: 0">'
       '<div class="pj-puce" style="border-style: dashed">?</div></div>')
cam(s, '<div id="s14-rep" style="position: absolute; left: 1760px; top: 640px; width: 0; height: 0; opacity: 0">'
       '<div class="pj-puce" style="background: #DCFC1C; color: #000">pleuvoir</div></div>')
cam(s, '<div id="s14-apres" class="pj-label" style="left: 1690px; top: 540px; opacity: 0"><span class="pj-k">Après</span></div>')
s.add(hud_g("s14-hud", "Le principe", "Avant → après"))
s.j('tl.set("#s14-fleche", { scaleX: 0 }, 0);')
s.j('tl.set(["#s14-t0", "#s14-t1"], { opacity: 0 }, 0);')
s.claque("#s14-t0", t_mot(230), 1.4)
s.choc("#s14-t1", t_mot(232))
s.eclair(t_mot(232))
son(t_mot(230), "swoosh-accent", 0.4, "principe")
son(t_mot(232), "impact-whoosh", 0.55, "FONDAMENTAL")
vit(s, "s14-toi", s.debut, s.fin - 0.2)
vit(s, "s14-ia", s.debut, s.fin - 0.2)
oui(s, "s14-toi", t_mot(231))
saut(s, "s14-toi", t_mot(232), 26)
zoom(s, t_mot(231) - 0.1, 760, 300, 1.2)
s.cache("#s14-titre", t_mot(235) - 0.15)
zoom(s, t_mot(234) - 0.1, 1290, 420, 1.15)
for k, i in enumerate((235, 236, 237)):
    s.claque(f"#s14-logo{k}", t_mot(i), 1.7)
    pop(t_mot(i), 0.42, "logo")
pose(s, "s14-ia", t_mot(235), 0.16, "back.out(2)", bd=-110, tete=-8)
s.claque("#s14-langage", t_mot(242), 1.8)
son(t_mot(242), "impact-cartoon", 0.5, "LE LANGAGE")
saut(s, "s14-ia", t_mot(242), 28)
pose(s, "s14-ia", t_mot(243), 0.12, bd=0, tete=0)
s.j(f'tl.to(["#s14-logo0", "#s14-logo1", "#s14-logo2"], {{ opacity: 0.25, duration: 0.2 }}, {s.L(t_mot(243))});')
s.cache("#s14-langage", t_mot(243) - 0.1)
zoom(s, t_mot(243) - 0.15, 1400, 600, 1.3)
s.apparait("#s14-avant", t_mot(243))
for k in range(3):
    pop(t_mot(243) + k * 0.15, 0.36, "mot d'avant")
parle(s, "s14-ia", t_mot(244), t_mot(249))
pose(s, "s14-toi", t_mot(245), 0.16, "back.out(2)", bd=-95, tete=-6)
s.j(f'tl.to("#s14-fleche", {{ scaleX: 1, duration: 0.3, ease: "power2.out" }}, {s.L(t_mot(249))});')
son(t_mot(249) + 0.15, "swoosh-vitesse", 0.42, "anticiper")
s.j(f'tl.fromTo("#s14-q", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.4)" }}, {s.L(t_mot(251))});')
pop(t_mot(251), 0.4, "point d'interrogation")
s.apparait("#s14-apres", t_mot(252))
son(t_mot(254), "riser-trailer", 0.35, "montée vers APRÈS")
s.j(f'tl.to("#s14-q", {{ opacity: 0, duration: 0.08 }}, {s.L(t_mot(254))});')
s.j(f'tl.fromTo("#s14-rep", {{ opacity: 0, scale: 1.8 }}, {{ opacity: 1, scale: 1, duration: 0.16, ease: "power4.out" }}, {s.L(t_mot(254))});')
son(t_mot(254), "impact-basse", 0.55, "après = pleuvoir")
zoom(s, t_mot(254) - 0.1, 1560, 610, 1.45)
victoire(s, "s14-toi", t_mot(254), 1)
pouce(s, "s14-ia", t_mot(254) + 0.1)
s.ecrire()

# ---------------------------------------------------------------- S15 : la prochaine fois…
s = scene(14, "Scène 15 · « La prochaine fois que ton clavier te proposera un mot avant même que tu l'aies écrit, »")
d15 = round(s.fin - s.debut, 2)
panneau(s, "s15-vid", 400, 214, 980, 551, ("video", "mains-tapent", 0, d15), "La prochaine fois", piste=5)
cam(s, '<div id="s15-sugg" class="pj-barre-sugg" style="left: 400px; top: 701px; width: 980px; opacity: 0">'
       '<span>pleuvoir</span><span style="background: #DCFC1C; color: #000">demain</span><span>bientôt</span></div>')
cam(s, perso("s15-toi", 1640, 800, 380))
tampon(s, "s15-avant", "Avant toi !", 1060, 270, t_mot(265), 6, 84)
s.add(hud_g("s15-hud", "Bientôt", "Dans ta poche"))
s.apparait("#s15-vid", s.debut + 0.02, 40)
s.j(f'tl.set("#s15-toi", {{ x: 360 }}, 0);')
marche(s, "s15-toi", s.debut + 0.05, t_mot(258), -360)
son(s.debut + 0.3, "swoosh-court", 0.35, "il arrive")
vit(s, "s15-toi", t_mot(258) + 0.05, s.fin - 0.2)
s.apparait("#s15-sugg", t_mot(262), 40)
son(t_mot(262), "notif-indice", 0.45, "suggestion sur la vidéo")
pose(s, "s15-toi", t_mot(262), 0.16, "back.out(2)", bg=105, tete=6)
zoom(s, t_mot(262) - 0.12, 890, 600, 1.25)
son(t_mot(265), "impact-cartoon", 0.5, "tampon avant toi")
zoom(s, t_mot(266), 960, 540, 1.0)
saut(s, "s15-toi", t_mot(265), 30)
haussement(s, "s15-toi", t_mot(268))
s.ecrire()

# ---------------------------------------------------------------- S16 : souviens-toi
s = scene(15, "Scène 16 · « souviens-toi : tu viens d'utiliser une forme d'IA, sans même ouvrir ChatGPT. »")
cam(s, projecteur(760))
cam(s, perso("s16-toi", 760, 800, 420))
cam(s, '<div id="s16-dit" class="pj-serif" style="left: 113px; top: 170px; font-size: 120px"><span id="s16-dit-0">Souviens-toi.</span></div>')
s.montre("#s16-dit-0", t_mot(271))
telephone(s, "s16-tel", 1300, 110, sugg=(("pleuvoir", "demain", "bientôt"),))
cam(s, '<div id="s16-halo" style="position: absolute; left: 1250px; top: 60px; width: 480px; height: 840px; border-radius: 70px; '
       'box-shadow: 0 0 80px 20px rgba(220, 252, 28, 0.55); opacity: 0"></div>')
tampon(s, "s16-ia", "IA", 1420, 300, t_mot(277), -8, 150)
cam(s, carte_logo("s16-gpt", "chatgpt", 230, 330, 220))
cam(s, '<div id="s16-x" class="pj-x" style="left: 230px; top: 330px; width: 220px; height: 300px; opacity: 0"></div>')
s.add(hud_g("s16-hud", "Souviens-toi", "Tu viens d'utiliser une IA"))
s.j(f'tl.set(["#s16-tel-s0-0", "#s16-tel-s0-1", "#s16-tel-s0-2"], {{ opacity: 1 }}, 0);')
son(t_mot(271), "swoosh-accent", 0.4, "souviens-toi")
vit(s, "s16-toi", s.debut, s.fin - 0.9)
grossit(s, "s16-toi", t_mot(271), 1.15)
pose(s, "s16-toi", t_mot(272), 0.16, "back.out(2)", bd=-70, tete=-6)
zoom(s, t_mot(271) - 0.1, 760, 420, 1.2)
s.cache("#s16-dit", t_mot(274))
s.j(f'tl.to("#s16-halo", {{ opacity: 1, duration: 0.3 }}, {s.L(t_mot(277))});')
son(t_mot(277), "impact-basse", 0.55, "tampon IA")
son(t_mot(277) + 0.2, "etincelles", 0.4, "le téléphone brille")
zoom(s, t_mot(276) - 0.1, 1480, 430, 1.25)
pose(s, "s16-toi", t_mot(277), 0.16, "back.out(2)", bd=-120)
zoom(s, t_mot(279) - 0.1, 960, 540, 1.0)
s.claque("#s16-gpt", t_mot(281), 1.7)
pop(t_mot(281), 0.42, "logo ChatGPT")
s.croix("#s16-x", t_mot(282) + 0.15)
son(t_mot(282) + 0.15, "fouet", 0.5, "ChatGPT barré")
victoire(s, "s16-toi", t_mot(282) + 0.5, 2)
confettis(s, "s16-conf", t_mot(282) + 0.5, 1490, 360)
son(t_mot(282) + 0.5, "cloche-succes", 0.42, "final")
s.ecrire()

# ================================================================ SONS GÉNÉRAUX
for k, c in enumerate(COUPES[1:-1], start=1):
    if NOMS[k] in ("s10-pourquoi", "s12-attention"):
        continue  # la carte noire a son propre impact
    son(c, tour(TRANSITIONS), 0.48, f"transition vers {NOMS[k]}")
son(t_mot(62), "riser-trailer", 0.38, "montée vers « le clavier »")
son(t_mot(228), "riser-tech", 0.32, "montée vers le principe fondamental")
son(t_mot(196), "swell-court", 0.35, "montée vers ATTENTION")
son(t_mot(271), "riser-synth", 0.3, "montée vers souviens-toi")

# Fichiers calibrés vers −16,9 LUFS ; volume 0,79 (−2 dB) → environ −19 LUFS, soit 4 dB sous la voix (−15),
# sans baisse automatique pendant la parole (voir tools/mixage.py).
MUSIQUES = [  # (début, fichier, durée, volume)
    (0, "partie-1-curiosity", 21.0, 0.79),
    (20.2, "partie-2-ideas", 44.9, 0.79),
    (64.3, "partie-3-motivating", 31.7, 0.79),
]


# ================================================================ MONTAGE (index.html) ET CADRE
CSS = """      /* ---- clavier-ia : début (écrit par tools/construire-scenes.py) ---- */
      .pj-cadre > .pj-horizon {
        left: -800px;
        width: 3520px;
      }
      .pj-logo {
        position: absolute;
        background: #141414;
        border: 3px solid #4a4a4a;
        padding: 34px 0 20px;
        text-align: center;
        box-shadow: 0 24px 70px rgba(0, 0, 0, 0.65);
      }
      .pj-logo img {
        display: block;
        margin: 0 auto;
      }
      .pj-logo-nom {
        font-family: "Anton", sans-serif;
        font-size: 44px;
        line-height: 1;
        color: var(--color-light);
        text-transform: uppercase;
        margin-top: 18px;
      }
      .pj-panneau {
        position: absolute;
        background: #000;
        outline: 3px solid var(--color-light);
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7);
      }
      .pj-panneau > video,
      .pj-panneau > img {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .pj-panneau-tag {
        position: absolute;
        left: 0;
        top: 0;
        background: var(--color-accent);
        color: #000;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 8px 16px;
        white-space: nowrap;
      }
      .pj-tel {
        position: absolute;
        display: flex;
        flex-direction: column;
        background: #0f0f0f;
        border: 8px solid #2c2c2c;
        border-radius: 52px;
        overflow: hidden;
        box-shadow: 0 40px 100px rgba(0, 0, 0, 0.75);
      }
      .pj-tel-tete {
        flex: none;
        height: 74px;
        padding-top: 20px;
        text-align: center;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 28px;
        color: #a3a3a3;
        border-bottom: 2px solid #232323;
      }
      .pj-tel-conv {
        flex: 1;
        position: relative;
      }
      .pj-tel-bulle {
        position: absolute;
        max-width: 280px;
        padding: 12px 18px;
        border-radius: 22px;
        background: var(--color-accent);
        color: #000;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 24px;
        line-height: 1.25;
      }
      .pj-tel-champ {
        flex: none;
        margin: 8px 14px;
        min-height: 64px;
        padding: 14px 18px;
        border-radius: 26px;
        background: #262626;
        font-family: "Inter", sans-serif;
        font-weight: 500;
        font-size: 25px;
        line-height: 1.3;
        color: var(--color-light);
      }
      .pj-tel-curseur {
        display: inline-block;
        width: 3px;
        height: 28px;
        background: var(--color-accent);
        vertical-align: -5px;
        margin-left: 3px;
      }
      .pj-tel-sugg {
        flex: none;
        display: flex;
        height: 64px;
        background: #1a1a1a;
        border-top: 2px solid #232323;
      }
      .pj-tel-cell {
        flex: 1;
        position: relative;
        border-left: 2px solid #2e2e2e;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 24px;
        color: var(--color-light);
      }
      .pj-tel-cell:first-child {
        border-left: none;
      }
      .pj-tel-cell span {
        position: absolute;
        left: 0;
        right: 0;
        top: 0;
        line-height: 62px;
        text-align: center;
        white-space: nowrap;
      }
      .pj-tel-clavier {
        flex: none;
        height: 270px;
        padding: 14px 6px 0;
        background: #1a1a1a;
      }
      .pj-tel-rang {
        display: flex;
        justify-content: center;
        gap: 5px;
        margin-bottom: 9px;
      }
      .pj-tel-rang i {
        flex: none;
        width: 31px;
        height: 50px;
        border-radius: 7px;
        background: #333333;
        color: var(--color-light);
        font-style: normal;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 20px;
        line-height: 50px;
        text-align: center;
      }
      .pj-tel-rang i.pj-tel-esp {
        width: 200px;
        font-size: 18px;
        color: #a3a3a3;
      }
      .pj-jour {
        width: 76px;
        height: 76px;
        border: 4px solid var(--color-light);
        font-family: "Anton", sans-serif;
        font-size: 40px;
        line-height: 68px;
        text-align: center;
        color: var(--color-light);
      }
      .pj-icone {
        display: inline-block;
        width: 78px;
        height: 78px;
        margin-right: 26px;
        background: var(--color-accent);
        color: #000;
        font-family: "Anton", sans-serif;
        font-size: 58px;
        font-weight: 400;
        line-height: 78px;
        text-align: center;
        vertical-align: -14px;
      }
      .pj-icone svg {
        vertical-align: -6px;
      }
      .pj-mini-papier {
        position: absolute;
        width: 96px;
        height: 124px;
        padding: 12px 12px;
        background: var(--color-light);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
      }
      .pj-puce {
        position: absolute;
        transform: translate(-50%, -50%);
        white-space: nowrap;
        background: #1c1c1c;
        border: 4px solid var(--color-accent);
        color: var(--color-light);
        font-family: "Anton", sans-serif;
        font-size: 46px;
        line-height: 1;
        padding: 10px 22px 12px;
        text-transform: uppercase;
      }
      .pj-pensee {
        background: var(--color-light);
        color: #0a0a06;
        padding: 14px 34px 18px;
        border-radius: 60px;
        white-space: nowrap;
      }
      .pj-bulle-rond {
        position: absolute;
        border-radius: 50%;
        background: var(--color-light);
      }
      .pj-barre {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 24px;
      }
      .pj-barre-mot {
        flex: none;
        width: 250px;
        font-family: "Anton", sans-serif;
        font-size: 58px;
        line-height: 1;
        color: var(--color-light);
        text-transform: uppercase;
      }
      .pj-barre-piste {
        flex: 1;
        position: relative;
        height: 36px;
        background: #2a2a2a;
      }
      .pj-barre-piste i {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background: var(--color-accent);
        transform-origin: 0% 50%;
      }
      .pj-barre-pct {
        flex: none;
        width: 140px;
        text-align: right;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 42px;
        color: var(--color-accent);
      }
      .pj-ligne-appris {
        font-family: "Instrument Serif", serif;
        font-style: italic;
        font-size: 56px;
        line-height: 1.25;
        margin-top: 18px;
        white-space: nowrap;
      }
      .pj-ligne-appris b {
        font-weight: 400;
        padding: 0 6px;
      }
      .pj-barre-sugg {
        position: absolute;
        display: flex;
        height: 64px;
        background: rgba(20, 20, 20, 0.88);
      }
      .pj-barre-sugg span {
        flex: 1;
        text-align: center;
        line-height: 64px;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 30px;
        color: var(--color-light);
      }
      /* ---- clavier-ia : fin ---- */
"""


def ecrire_index():
    f = ICI / "index.html"
    h = f.read_text(encoding="utf-8")
    h = re.sub(r"      /\* ---- clavier-ia : début.*?/\* ---- clavier-ia : fin ---- \*/\n", "", h, flags=re.S)
    h = h.replace("    </style>\n  </head>", CSS + "    </style>\n  </head>", 1)
    lignes = [f'      <div id="fond" class="clip" data-start="0" data-duration="{FIN}" data-track-index="0"></div>', ""]
    for k, nom in enumerate(NOMS):
        d0, d1 = COUPES[k], COUPES[k + 1]
        lignes.append(f'      <div id="{nom}" data-composition-id="{nom}" data-composition-src="compositions/{nom}.html"\n'
                      f'        data-start="{d0}" data-duration="{round(d1 - d0, 2)}" data-track-index="1" data-track-kind="graphics"\n'
                      f'        data-width="1920" data-height="1080" style="z-index: 10"></div>')
    lignes += ["",
               f'      <div id="cadre" data-composition-id="cadre" data-composition-src="compositions/cadre.html"\n'
               f'        data-start="0" data-duration="{FIN}" data-track-index="2" data-track-kind="graphics"\n'
               f'        data-width="1920" data-height="1080" style="z-index: 40"></div>',
               f'      <div id="sous-titres" data-composition-id="sous-titres" data-composition-src="compositions/sous-titres.html"\n'
               f'        data-start="0" data-duration="{FIN}" data-track-index="3" data-track-kind="captions"\n'
               f'        data-width="1920" data-height="1080" style="z-index: 50"></div>', "",
               '      <audio id="voix" src="assets/audio/voix.mp3" data-start="0" data-track-index="10"></audio>']
    for k, (d0, nom, dd, v) in enumerate(MUSIQUES):
        lignes.append(f'      <audio id="musique-{k + 1}" src="assets/music/{nom}.mp3" data-start="{d0}" data-duration="{dd}" '
                      f'data-volume="{v}" data-track-index="{11 + k % 2}"></audio>')
    pistes = {}
    for n, (d0, nom, v, note, dd) in enumerate(sorted(SONS), start=1):
        p = 30
        while pistes.get(p, -1) > d0 - 0.01:
            p += 1
        dd = round(min(dd, FIN - d0), 2)
        pistes[p] = d0 + dd
        lignes.append(f'      <audio id="sfx-{n:02d}" src="assets/sfx/{nom}.mp3" data-start="{d0}" data-duration="{dd}" '
                      f'data-volume="{v}" data-track-index="{p}"></audio><!-- {note} -->')
    corps = "\n".join(lignes)
    h = re.sub(r"(<div\n      id=\"root\"\n      data-composition-id=\"main\"\n      data-start=\"0\"\n      data-duration=\")[\d.]+(\"\n.*?>\n)(.*?)(\n    </div>\n    <script>)",
               lambda m: m.group(1) + str(FIN) + m.group(2) + corps + m.group(4), h, count=1, flags=re.S)
    f.write_text(h, encoding="utf-8")
    return len(SONS)


def ecrire_cadre():
    f = ICI / "compositions/cadre.html"
    h = f.read_text(encoding="utf-8")
    masques = [(t_mot(159), t_mot(160) - 0.05, "« POURQUOI ? »"), (t_mot(196), t_mot(197) - 0.05, "« ATTENTION »")]
    bloc = "\n".join(f"    masquer({round(a, 2)}, {round(c, 2)}); // {n}" for a, c, n in masques)
    h = re.sub(r"(    }\n)((?:    masquer\(.*\n)+)", lambda m: m.group(1) + bloc + "\n", h, count=1)
    f.write_text(h, encoding="utf-8")


n = ecrire_index()
ecrire_cadre()
print(f"{len(NOMS)} scènes écrites, {n} bruitages placés, fin à {FIN} s")
