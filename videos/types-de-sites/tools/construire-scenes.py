#!/usr/bin/env python3
"""Écrit les 10 scènes de « types-de-sites » (les 6 types de sites web, révélés un par un, avec du mystère et une caméra qui suit), le montage, le cadre,
les volets et les 5 métiers sous le film de la version verticale. Rafale de vraies vidéos en fond de CHAQUE scène et un faux
site professionnel par métier, rempli de vraies vidéos et photos. Style « Projecteur » + les effets
dynamiques de la vidéo 7 (volets, glitch, secousses) + un faux site premium « LUMEN » construit dans les scènes.

Attention : relancer ce script ÉCRASE compositions/s*.html et le <body> de index.html
(il faut ensuite relancer tools/mixage.py pour le carve et le limiteur des musiques).
Bibliothèque partagée : hyperframes-style/outils/projecteur.py. Les outils de son, de vidéo et de téléphone
viennent de videos/clavier-ia/tools/construire-scenes.py.
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
VOL_SFX = 0.7  # 421 bruitages en 96 s (très dense) : baissés pour rester vers −21 LUFS au total, comme le réglage validé


def b(i):
    """Coupure de scène juste avant le mot i."""
    return round(t_mot(i) - 0.12, 2)


FIN = 95.6
COUPES = [0] + [b(i) for i in (20, 37, 64, 92, 116, 146, 175, 218, 255)] + [FIN]
NOMS = ["s01-question", "s02-pas-du-tout", "s03-vitrine", "s04-ecommerce", "s05-portfolio", "s06-blog", "s07-landing", "s08-plateforme", "s09-vraie-question", "s10-abonne"]
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
    SONS.append((round(max(0.0, debut), 2), nom, round(v * VOL_SFX, 3), note, round(min(d or p["duree"], p["duree"]), 2)))


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



# ================================================================ ÉLÉMENTS AJOUTÉS POUR « agent-ia-n8n »
LOGOS.update({"n8n": ("logo-n8n.svg", "n8n"), "telegram": ("logo-telegram.svg", "Telegram"), "google": ("logo-google.svg", "Google"),
              "openai": ("logo-openai.svg", "OpenAI")})


def etape(s, sid, n, g, x=1440, y=128):
    """Bandeau « ÉTAPE n/5 » en haut à droite."""
    cam(s, f'<div id="{sid}" class="pj-etape" style="left: {x}px; top: {y}px; opacity: 0"><span>Étape</span><b>{n}</b><i>/5</i></div>')
    s.claque(f"#{sid}", g, 1.9)
    son(g, "impact-basse", 0.5, f"ÉTAPE {n}")
    son(g, tour(["swoosh-vitesse", "fusee-whoosh", "souffle-cine", "magie"]), 0.42, "bandeau étape")


def fenetre(s, wid, x, y, w, h, titre, corps, logo="logo-n8n.svg"):
    """Fenêtre d'application (barre de titre + corps)."""
    cam(s, f'<div id="{wid}" class="pj-fenetre" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0">'
           f'<div class="pj-fen-barre"><i></i><i></i><i></i><img src="assets/img/{logo}" alt="" /><span>{titre}</span></div>'
           f'<div class="pj-fen-corps">{corps}</div></div>')


def souris(s, cid, x, y):
    """Pointeur de souris (déplacé avec deplace(), clic avec clic())."""
    cam(s, f'<svg id="{cid}" class="pj-souris" style="left: {x}px; top: {y}px" viewBox="0 0 40 52">'
           '<path d="M3 3 L3 43 L13 33 L21 50 L28 47 L20 30 L35 30 Z" fill="#ffffff" stroke="#000000" stroke-width="3" stroke-linejoin="round" /></svg>')


def deplace(s, cid, g, x, y, x0, y0, d=0.45):
    """Amène la pointe du pointeur (placé au départ en x0, y0) sur (x, y)."""
    s.j(f'tl.to("#{cid}", {{ x: {x - x0}, y: {y - y0}, duration: {d}, ease: "power2.inOut" }}, {s.L(g)});')
    son(g + d * 0.4, tour(["papier-glisse", "souffle-air"]), 0.18, "la souris glisse")


def clic(s, cid, g, cible=None):
    s.j(f'tl.to("#{cid}", {{ keyframes: [{{ scale: 0.8, duration: 0.07 }}, {{ scale: 1, duration: 0.1 }}] }}, {s.L(g)});')
    son(g, tour(["souris", "souris-2", "clic", "bouton"]), 0.55, "clic de souris")
    if cible:
        s.j(f'tl.to("{cible}", {{ keyframes: [{{ scale: 0.93, duration: 0.07 }}, {{ scale: 1, duration: 0.12 }}] }}, {s.L(g)});')


ICONES = {
    "loupe": '<svg viewBox="0 0 40 40" style="width: 34px; height: 34px; margin-top: 11px"><circle cx="16" cy="16" r="11" fill="none" stroke="#000" stroke-width="5" />'
             '<path d="M24 24 L36 36" stroke="#000" stroke-width="6" stroke-linecap="round" /></svg>',
    "puce": '<svg viewBox="0 0 40 40" style="width: 34px; height: 34px; margin-top: 11px"><rect x="9" y="9" width="22" height="22" rx="3" fill="#000" />'
            '<path d="M14 3 V9 M20 3 V9 M26 3 V9 M14 31 V37 M20 31 V37 M26 31 V37 M3 14 H9 M3 20 H9 M3 26 H9 M31 14 H37 M31 20 H37 M31 26 H37" '
            'stroke="#000" stroke-width="3" /></svg>',
}


def noeud(s, nid, cx, cy, titre, sous="", icone="", w=300, h=110, agent=False):
    """Nœud de workflow (centré sur cx, cy). icone : nom d'un logo de assets/img ou texte court."""
    if icone.endswith(".svg"):
        ico = f'<img src="assets/img/{icone}" alt="" />'
    elif icone.startswith("svg:"):
        ico = f'<b class="pj-noeud-ico">{ICONES[icone[4:]]}</b>'
    else:
        ico = f'<b class="pj-noeud-ico">{icone}</b>'
    sous_html = f"<span>{sous}</span>" if sous else ""
    cam(s, f'<div id="{nid}" class="pj-noeud{" pj-noeud-agent" if agent else ""}" style="left: {cx - w // 2}px; top: {cy - h // 2}px; '
           f'width: {w}px; height: {h}px; opacity: 0">{ico}<div><b>{titre}</b>{sous_html}</div></div>')


def liens(s, lid, chemins):
    """Liaisons tracées (x1, y1, x2, y2, sens « h » ou « v », temps)."""
    traits = []
    for k, (x1, y1, x2, y2, sens, g) in enumerate(chemins):
        if sens == "h":
            dp = f"M{x1} {y1} C{x1 + 90} {y1} {x2 - 90} {y2} {x2} {y2}"
        else:
            dp = f"M{x1} {y1} C{x1} {y1 + 70} {x2} {y2 - 70} {x2} {y2}"
        traits.append(f'<path id="{lid}-{k}" d="{dp}" pathLength="100" fill="none" stroke="{ACCENT}" stroke-width="5" '
                      f'stroke-dasharray="100" stroke-dashoffset="100" />')
        if g is not None:
            s.j(f'tl.to("#{lid}-{k}", {{ attr: {{ "stroke-dashoffset": 0 }}, duration: 0.35, ease: "power2.out" }}, {s.L(g)});')
            son(g + 0.15, tour(["interrupteur", "bouton-tech", "switch-basse"]), 0.38, "liaison tracée")
        else:
            s.j(f'tl.set("#{lid}-{k}", {{ attr: {{ "stroke-dashoffset": 0 }} }}, 0);')
    cam(s, f'<svg id="{lid}" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: visible" '
           f'viewBox="0 0 1920 1080">{"".join(traits)}</svg>')


def telegram(s, tid, x, y, nom, bulles, w=420, h=740):
    """Conversation Telegram. bulles : (id, « moi » | « bot », html) ; cachées au départ."""
    b_html = "".join(f'<div id="{tid}-{bid}" class="pj-tg-bulle pj-tg-{cote}" style="opacity: 0">{html}</div>' for bid, cote, html in bulles)
    cam(s, f'<div id="{tid}" class="pj-tg" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px">'
           f'<div class="pj-tg-tete"><img src="assets/img/logo-telegram.svg" alt="" /><b>{nom}</b></div>'
           f'<div class="pj-tg-conv">{b_html}</div><div class="pj-tg-champ"><span>Message</span><i></i></div></div>')


def mots_bulle(tid, bid, i1, i2):
    """Texte d'une bulle écrit mot à mot avec la voix (mots i1..i2 du script)."""
    return " ".join(f'<span id="{tid}-{bid}-{i}" style="opacity: 0">{mot(i)}</span>' for i in range(i1, i2 + 1))


def ecrit_bulle(s, tid, bid, i1, i2, son_frappe=True):
    s.apparait(f"#{tid}-{bid}", t_mot(i1) - 0.08, 16)
    for i in range(i1, i2 + 1):
        s.montre(f"#{tid}-{bid}-{i}", t_mot(i))
    if son_frappe:
        son(t_mot(i1) - 0.05, "clavier-tel-3", 0.4, "message tapé", d=round(t_mot(i2) + 0.3 - t_mot(i1), 2), sur_pic=False)


def recoit(s, sel, g, v=0.5, nom=None):
    s.j(f'tl.fromTo("{sel}", {{ opacity: 0, y: 30, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.22, ease: "back.out(2)" }}, {s.L(g)});')
    son(g, nom or tour(["notif-magique", "notif-positive", "notif-indice"]), v, "message reçu")


def envoie(s, g):
    son(g, tour(["swoosh-court", "swoosh-accent", "fusee-whoosh"]), 0.42, "message envoyé")


def plein_cadre(s, pid, video, d, assombrir=0.55):
    """Vraie vidéo en plein cadre (dans la caméra), assombrie pour le texte."""
    cam(s, f'<div id="{pid}" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden">'
           f'<video id="{pid}-v" class="clip" src="assets/video/{video}.mp4" data-start="0" data-duration="{d}" data-track-index="5" '
           f'muted playsinline style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover"></video>'
           f'<div style="position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,{assombrir - 0.3}), rgba(0,0,0,{assombrir + 0.2}))"></div></div>')
    s.j(f'tl.fromTo("#{pid}", {{ scale: 1.0 }}, {{ scale: 1.1, duration: {d}, ease: "none" }}, 0);')


def impulsion(s, pid, points):
    """Point lumineux qui voyage de nœud en nœud : points = [(t, x, y), …]."""
    t0, x0, y0 = points[0]
    cam(s, f'<div id="{pid}" class="pj-impulsion" style="left: {x0 - 18}px; top: {y0 - 18}px; opacity: 0"></div>')
    s.j(f'tl.set("#{pid}", {{ opacity: 1 }}, {s.L(t0)});')
    for (ta, xa, ya), (tb, xb, yb) in zip(points, points[1:]):
        s.j(f'tl.to("#{pid}", {{ x: {xb - x0}, y: {yb - y0}, duration: {round(tb - ta, 3)}, ease: "power1.inOut" }}, {s.L(ta)});')
    s.j(f'tl.to("#{pid}", {{ opacity: 0, duration: 0.15 }}, {s.L(points[-1][0])});')


def brille(s, sel, g):
    s.j(f'tl.fromTo("{sel}", {{ boxShadow: "0 0 0px rgba(255, 90, 31, 0)" }}, {{ boxShadow: "0 0 50px rgba(255, 90, 31, 0.9)", duration: 0.25, '
        f'repeat: 1, yoyo: true, immediateRender: false }}, {s.L(g)});')


def puce_rayee(s, pid, texte, x, y, g, g_rature):
    cam(s, f'<div id="{pid}" style="position: absolute; left: {x}px; top: {y}px; width: 0; height: 0; opacity: 0">'
           f'<div class="pj-puce" style="color: #9a9a9a; border-color: #6a6a6a">{texte}'
           f'<i id="{pid}-r" style="position: absolute; left: -8px; right: -8px; top: 46%; height: 8px; background: {ACCENT}"></i></div></div>')
    s.j(f'tl.fromTo("#{pid}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.4)" }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{pid}-r", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.16 }}, {s.L(g_rature)});')
    son(g_rature, "buzz-faux", 0.35, "rayé")


def resultats(s, rid, x, y, w, n, ecart=104, visibles_a=None):
    """Cartes de résultats de recherche (icône + deux lignes grises)."""
    html = []
    for k in range(n):
        html.append(f'<div id="{rid}-{k}" class="pj-resultat" style="left: {x}px; top: {y + k * ecart}px; width: {w}px; opacity: 0">'
                    f'<i></i><div><b style="width: {60 + (k * 23) % 30}%"></b><b style="width: {80 - (k * 17) % 25}%"></b></div>'
                    f'<span id="{rid}-{k}-m" class="pj-resultat-marque"></span></div>')
    cam(s, "".join(html))
    if visibles_a is not None:
        s.j(f'tl.set([{", ".join(f"{chr(34)}#{rid}-{k}{chr(34)}" for k in range(n))}], {{ opacity: 1 }}, {s.L(visibles_a)});')


# ================================================================ ÉLÉMENTS DU CLASSEMENT
LOGOS.update({"deepseek": ("logo-deepseek.svg", "DeepSeek"), "perplexity": ("logo-perplexity.svg", "Perplexity"),
              "grok": ("logo-grok.svg", "Grok"), "midjourney": ("logo-midjourney.svg", "Midjourney"),
              "nanobanana": ("logo-gemini.svg", "Nano Banana"), "chatgptimg": ("logo-openai.svg", "ChatGPT Images"),
              "firefly": ("logo-adobe.svg", "Firefly"), "recraft": ("logo-recraft.svg", "Recraft"), "kling": ("logo-kling.svg", "Kling"),
              "seedance": ("logo-bytedance.svg", "Seedance"), "runway": ("logo-runway.svg", "Runway"),
              "elevenlabs": ("logo-elevenlabs.svg", "ElevenLabs"), "suno": ("logo-suno.svg", "Suno")})
RANGS_T = {"S": (ACCENT, "#000000"), "A": (CLAIR, "#000000"), "B": ("#8a8a8a", "#000000"), "C": ("#333333", CLAIR)}
ORDRE = "SABC"


class Tableau:
    """Tableau S/A/B/C. Les tuiles sont des éléments séparés (dans la caméra) posés sur les rangs."""

    def __init__(self, s, tid, x=700, y=220, w=1100, h=140, gap=10, titre=None, tuile=(150, 120), etiquette=130):
        self.s, self.tid, self.x, self.y, self.w, self.h, self.gap = s, tid, x, y, w, h, gap
        self.tw, self.th, self.lab = tuile[0], tuile[1], etiquette
        self.compte = {r: 0 for r in ORDRE}
        rangs = "".join(f'<div id="{tid}-r{r}" class="pj-rang" style="height: {h}px; margin-bottom: {gap}px">'
                        f'<b style="width: {etiquette}px; line-height: {h}px; font-size: {int(h * 0.62)}px; background: {RANGS_T[r][0]}; color: {RANGS_T[r][1]}">{r}</b>'
                        f'<div id="{tid}-c{r}" class="pj-rang-corps"></div></div>' for r in ORDRE)
        t = f'<div class="pj-label" style="position: absolute; left: 0; top: -62px"><span class="pj-k">{titre}</span></div>' if titre else ""
        cam(s, f'<div id="{tid}" class="pj-tableau" style="left: {x}px; top: {y}px; width: {w}px">{t}{rangs}</div>')

    def centre(self, r):
        i = ORDRE.index(r)
        return self.x + self.w // 2, self.y + i * (self.h + self.gap) + self.h // 2

    def place(self, cle, r, g=None, nom=None, v=0.5):
        """Pose un logo dans le rang r ; g = moment de la chute (None : déjà posé)."""
        k = self.compte[r]
        self.compte[r] += 1
        f, n = LOGOS[cle]
        n = nom or n
        i = ORDRE.index(r)
        x = self.x + self.lab + 14 + k * (self.tw + 10)
        y = self.y + i * (self.h + self.gap) + (self.h - self.th) // 2
        tid = f"{self.tid}-{cle}"
        img = round(self.th * 0.55)
        fs = max(20, round(self.th * 0.22))
        cam(self.s, f'<div id="{tid}" class="pj-tuile" style="left: {x}px; top: {y}px; width: {self.tw}px; height: {self.th}px; opacity: 0">'
                    f'<img src="assets/img/{f}" alt="" style="width: {img}px; height: {img}px" /><span style="font-size: {fs}px">{n}</span></div>')
        if g is None:
            self.s.j(f'tl.set("#{tid}", {{ opacity: 1 }}, 0);')
        else:
            self.s.j(f'tl.fromTo("#{tid}", {{ opacity: 0, y: -360, rotation: -12 }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.32, ease: "bounce.out" }}, {self.s.L(g)});')
            son(g - 0.05, tour(["swoosh-court", "souffle-air", "swoosh-accent", "fouet"]), 0.35, f"{n} tombe")
            son(g + 0.16, tour(["impact-cartoon", "impact-basse", "pop-click", "impact-futur"]), v, f"{n} en {r}")
        return tid

    def surligne(self, r, g, d=0.3):
        self.s.j(f'tl.fromTo("#{self.tid}-c{r}", {{ boxShadow: "inset 0 0 0px rgba(255, 90, 31, 0)" }}, '
                 f'{{ boxShadow: "inset 0 0 0 6px rgba(255, 90, 31, 0.9)", duration: {d}, immediateRender: false }}, {self.s.L(g)});')
        son(g, "bouton-tech", 0.35, f"rang {r}")

    def apparait(self, g, pas=0.1):
        for k, r in enumerate(ORDRE):
            self.s.glisse(f"#{self.tid}-r{r}", g + k * pas, 120)
            son(g + k * pas, tour(POPS), 0.36, f"rang {r}")


def montre_tableau(s, tid):
    s.j(f'tl.set(["#{tid}-rS", "#{tid}-rA", "#{tid}-rB", "#{tid}-rC"], {{ opacity: 1 }}, 0);')


def badge(s, sid, texte, n, g, x=1440, y=128):
    cam(s, f'<div id="{sid}" class="pj-etape" style="left: {x}px; top: {y}px; opacity: 0"><span>{texte}</span><b>{n}</b><i>/4</i></div>')
    s.claque(f"#{sid}", g, 1.9)
    son(g, "impact-basse", 0.5, f"catégorie {n}")


def categorie(s, p, n, titre, video, g):
    """Carte de catégorie : vraie vidéo plein cadre + grand titre + badge n/4."""
    plein_cadre(s, f"{p}-plein", video, round(s.fin - s.debut, 2), 0.6)
    cam(s, f'<div id="{p}-titre" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 330px; text-align: center; font-size: 170px; opacity: 0">{titre}</div>')
    badge(s, f"{p}-badge", "Catégorie", n, g)
    s.choc(f"#{p}-titre", g + 0.1)
    s.eclair(g + 0.1)
    son(g + 0.1, "impact-whoosh", 0.5, f"catégorie {titre}")


def ecran_apps(s, pid, x, y, cles, w=420, h=740):
    """Téléphone avec une grille d'applis (logos)."""
    tuiles = "".join(f'<div id="{pid}-a{k}" class="pj-appli"><img src="assets/img/{LOGOS[c][0]}" alt="" /></div>' for k, c in enumerate(cles))
    cam(s, f'<div id="{pid}" class="pj-tel" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px">'
           f'<div class="pj-tel-tete">Mes applis IA</div><div class="pj-apps">{tuiles}'
           f'<div id="{pid}-q" class="pj-appli pj-appli-q" style="opacity: 0">?</div></div></div>')


# ================================================================ ÉLÉMENTS DES SKILLS
LOGOS.update({"github": ("logo-github.svg", "GitHub")})


def badge5(s, sid, n, g, x=1470, y=128):
    cam(s, f'<div id="{sid}" class="pj-etape" style="left: {x}px; top: {y}px; opacity: 0"><span>Skill</span><b>{n}</b><i>/5</i></div>')
    s.claque(f"#{sid}", g, 1.9)
    son(g, "impact-basse", 0.5, f"skill {n}")
    son(g, tour(["swoosh-vitesse", "fusee-whoosh", "souffle-cine", "magie"]), 0.4, "bandeau skill")


def titre_skill(s, sid, nom, repo, etoiles, g, x=113, y=212):
    """Nom du skill (grand) + dépôt GitHub réel + nombre d'étoiles."""
    cam(s, f'<div id="{sid}" style="position: absolute; left: {x}px; top: {y}px; opacity: 0">'
           f'<div class="pj-impact" style="font-size: 96px">{nom}</div>'
           f'<div class="pj-repo"><img src="assets/img/logo-github.svg" alt="" />{repo}<b>★ {etoiles}</b></div></div>')
    s.glisse(f"#{sid}", g, -300)


def guide(s, pid, g_gauche, g_droite, g_fort, g_fin=None):
    """Petit personnage entre les deux écrans : montre la capture de gauche, puis celle de droite, puis réagit."""
    cam(s, perso(pid, 966, 800, 230))
    vit(s, pid, s.debut, s.fin - 0.2)
    pose(s, pid, g_gauche, 0.16, "back.out(2)", bg=110, tete=8)
    pose(s, pid, g_droite, 0.16, "back.out(2)", bg=0, bd=-110, tete=-8)
    pose(s, pid, g_fort, 0.12, bd=0, tete=0)
    victoire(s, pid, g_fort + 0.15, 1)
    if g_fin:
        acquiesce(s, pid, g_fin, 2)


def ecran(s, pid, x, y, w, h, video, tag=None, piste=5, rot=0):
    """Capture réelle (vidéo) dans un cadre ; rot : légère inclinaison du conteneur."""
    panneau(s, pid, x, y, w, h, ("video", video, 0, round(s.fin - s.debut, 2)), tag, piste)


CHAOS = ["site-ia-0", "tablette-web", "site-ia-3", "defile-tablette", "site-ia-6", "site-mode", "site-ia-1", "bureau-web",
         "site-ia-8", "recherche-web", "site-ia-4", "laptop-homme", "site-ia-9", "site-ia-2", "reflet-lunettes", "site-ia-7"]


def rafale(s, p, g0, pas, d):
    """Intro : vidéos de sites qui arrivent de tous les côtés et s'empilent très vite."""
    for k, v in enumerate(CHAOS):
        w = 720 + (k * 97) % 260
        h = round(w * 9 / 16)
        x = 60 + (k * 389) % (1920 - w - 120)
        y = 90 + (k * 233) % (980 - h - 160)
        rot = (k * 37) % 17 - 8
        dx, dy = [(-1500, 0), (1500, 0), (0, -1100), (0, 1100), (-1300, -900), (1300, 900), (1300, -900), (-1300, 900)][k % 8]
        cam(s, f'<div id="{p}-{k}" class="pj-rafale" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0">'
               f'<video id="{p}-{k}-v" class="clip" src="assets/video/{v}.mp4" data-start="0" data-duration="{d}" data-track-index="{5 + k % 3}" muted playsinline></video></div>')
        g = round(g0 + k * pas, 3)
        s.j(f'tl.fromTo("#{p}-{k}", {{ opacity: 1, x: {dx}, y: {dy}, rotation: {rot * 4}, scale: 1.3 }}, '
            f'{{ opacity: 1, x: 0, y: 0, rotation: {rot}, scale: 1, duration: 0.22, ease: "power4.out", immediateRender: false }}, {s.L(g)});')
        son(g + 0.1, tour(["fouet", "swoosh-court", "glitch-mini", "souffle-rapide", "declencheur", "swoosh-accent", "glitch-court", "souffle-air"]), 0.42, "vidéo qui arrive")
        if k % 4 == 3:
            son(g + 0.12, tour(["impact-cartoon", "glitch-cine", "impact-futur", "glitch-scifi"]), 0.4, "choc")


def mur(s, p, n_col, n_lig, x0, y0, w, gap, g, pas=0.03, accent=None):
    """Mur de captures de sites identiques (images)."""
    h = round(w * 9 / 16)
    html = []
    for r in range(n_lig):
        for c in range(n_col):
            k = r * n_col + c
            img = f"site-ia-{k % 10}-{(0.3, 2.0, 3.6)[(k // 10) % 3]}.jpg"
            bord = "outline: 6px solid #DCFC1C;" if accent == k else ""
            html.append(f'<div id="{p}-{k}" class="pj-tuile-site" style="left: {x0 + c * (w + gap)}px; top: {y0 + r * (h + gap)}px; width: {w}px; height: {h}px; {bord} opacity: 0">'
                        f'<img src="assets/img/{img}" alt="" /></div>')
            s.j(f'tl.fromTo("#{p}-{k}", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.16, ease: "back.out(2)" }}, {s.L(g + ((k * 7) % (n_col * n_lig)) * pas)});')
    cam(s, "".join(html))


def nuancier(s, p, x, y, g, couleurs=("#0F172A", "#F97316", "#FDE68A", "#14B8A6", "#E11D48", "#6366F1", "#A3E635", "#F5F5F4")):
    html = "".join(f'<i id="{p}-{k}" style="position: absolute; left: {x + k * 92}px; top: {y}px; width: 80px; height: 110px; border-radius: 12px; background: {c}; opacity: 0"></i>'
                   for k, c in enumerate(couleurs))
    cam(s, html)
    for k in range(len(couleurs)):
        s.j(f'tl.fromTo("#{p}-{k}", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.18, ease: "back.out(2)" }}, {s.L(g + k * 0.05)});')


# ================================================================ ÉLÉMENTS DYNAMIQUES (repris de la vidéo 7, en couleurs « Projecteur »)
import math
# Variante dynamique du style « Projecteur » : accent orange signal, coches vertes, fond « plan technique »,
# rubans de chantier, mots-chocs en glitch, secousses de caméra, volets rayés à chaque coupe, check-list en haut.
ACCENT = "#DCFC1C"
VERT = "#DCFC1C"
P.TETES["visiteur"] = P.TETES["toi"]

TRIANGLE = ('<svg viewBox="0 0 40 36" width="34" height="30"><path d="M20 2 L38 34 L2 34 Z" fill="#0C0C0C" />'
            '<rect x="18" y="12" width="4" height="12" fill="#DCFC1C" /><rect x="18" y="27" width="4" height="4" fill="#DCFC1C" /></svg>')
COCHE = '<svg viewBox="0 0 40 40" width="{w}" height="{w}"><path d="M8 21 L17 30 L33 11" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" /></svg>'
OEIL = ('<svg viewBox="0 0 80 50" width="80" height="50"><path d="M4 25 Q40 -8 76 25 Q40 58 4 25 Z" fill="none" stroke="currentColor" stroke-width="5" />'
        '<circle cx="40" cy="25" r="11" fill="currentColor" /></svg>')
CADENAS = ('<svg id="{id}" viewBox="0 0 120 150" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; overflow: visible; opacity: 0">'
           '<g id="{id}-anse"><path d="M30 70 L30 42 Q30 12 60 12 Q90 12 90 42 L90 70" fill="none" stroke="#ECECE8" stroke-width="14" stroke-linecap="round" /></g>'
           '<rect x="14" y="66" width="92" height="76" rx="14" fill="#DCFC1C" /><circle cx="60" cy="98" r="10" fill="#0C0C0C" />'
           '<rect x="56" y="100" width="8" height="22" rx="3" fill="#0C0C0C" /></svg>')


def secousse(s, g, amp=16):
    """Secousse de caméra sur un impact."""
    s.j(f'tl.fromTo("#{s.id}-cam", {{ x: 0, y: 0 }}, {{ keyframes: [{{ x: -{amp}, y: {amp // 2}, duration: 0.04 }}, {{ x: {amp}, y: -{amp // 2}, duration: 0.04 }}, '
        f'{{ x: -{amp // 2}, y: {amp // 3}, duration: 0.04 }}, {{ x: 0, y: 0, duration: 0.05 }}], immediateRender: false }}, {s.L(g)});')


def choc_mot(s, mid, texte, y, taille, g, fin=None, coul=None, x=0, w=1920):
    """Mot-choc en glitch (décalage cyan/rouge) qui s'écrase et tremble."""
    c = f"color: {coul}; " if coul else ""
    cam(s, f'<div id="{mid}" class="al-choc" style="left: {x}px; width: {w}px; top: {y}px; font-size: {taille}px; {c}opacity: 0">{texte}</div>')
    s.j(f'tl.fromTo("#{mid}", {{ opacity: 0, scale: 1.7, skewX: -14 }}, {{ opacity: 1, scale: 1, skewX: 0, duration: 0.14, ease: "power4.out" }}, {s.L(g)});')
    s.j(f'tl.to("#{mid}", {{ keyframes: [{{ x: -16, duration: 0.03 }}, {{ x: 12, duration: 0.03 }}, {{ x: -6, duration: 0.03 }}, {{ x: 0, duration: 0.03 }}] }}, {s.L(g + 0.14)});')
    if fin is not None:
        s.j(f'tl.to("#{mid}", {{ opacity: 0, scale: 0.85, duration: 0.12 }}, {s.L(fin)});')


def ruban(s, rid, y, rot, texte, g, sens=1, fin=None):
    """Ruban de chantier « ATTENTION » qui traverse l'image."""
    mots = " &nbsp;/&nbsp; ".join([texte] * 9)
    cam(s, f'<div id="{rid}" class="al-ruban" style="top: {y}px; transform: rotate({rot}deg); opacity: 0"><div id="{rid}-t" class="al-ruban-t">{mots}</div></div>')
    s.j(f'tl.fromTo("#{rid}", {{ opacity: 1, x: {-2700 * sens} }}, {{ opacity: 1, x: 0, duration: 0.2, ease: "power4.out", immediateRender: false }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{rid}-t", {{ x: 0 }}, {{ x: {-360 * sens}, duration: 2.4, ease: "none", immediateRender: false }}, {s.L(g)});')
    if fin is not None:
        s.j(f'tl.to("#{rid}", {{ x: {2700 * sens}, duration: 0.22, ease: "power3.in" }}, {s.L(fin)});')


def numero(s, nid, n, g, g_range):
    """Numéro géant du point (« 01 ») au centre, puis rangé en haut à gauche à côté du titre."""
    cam(s, f'<div id="{nid}" class="al-num" style="left: 113px; top: 150px; opacity: 0">{n}</div>')
    s.j(f'tl.fromTo("#{nid}", {{ opacity: 0, x: 690, y: 70, scale: 3.4 }}, {{ opacity: 1, x: 690, y: 70, scale: 2.2, duration: 0.16, ease: "power4.out" }}, {s.L(g)});')
    s.j(f'tl.to("#{nid}", {{ x: 0, y: 0, scale: 1, duration: 0.3, ease: "power3.inOut" }}, {s.L(g_range)});')
    son(g, "impact-basse", 0.55, f"point {n}")
    son(g, tour(["glitch-cine", "glitch-scifi", "glitch-rugit", "glitch-court"]), 0.38, f"numéro {n}")
    son(g_range + 0.15, tour(["swoosh-court", "swoosh-accent", "fouet"]), 0.36, "le numéro se range")
    secousse(s, g, 12)


def titre(s, tid, texte, g, taille=110, x=300, y=170, sous=None):
    st = f'<div class="al-sous">{sous}</div>' if sous else ""
    cam(s, f'<div id="{tid}" style="position: absolute; left: {x}px; top: {y}px; opacity: 0">{st}<div class="al-titre" style="font-size: {taille}px">{texte}</div></div>')
    s.j(f'tl.fromTo("#{tid}", {{ opacity: 0, x: -260, skewX: -18 }}, {{ opacity: 1, x: 0, skewX: 0, duration: 0.22, ease: "power4.out" }}, {s.L(g)});')
    son(g, tour(["swoosh-vitesse", "swoosh-monte", "fusee-whoosh"]), 0.36, "titre")


def navigateur(s, nid, x, y, w, h, url, corps, opacite=0):
    """Fenêtre de navigateur (barre avec 3 points et adresse) ; corps HTML libre."""
    cam(s, f'<div id="{nid}" class="al-nav" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: {opacite}">'
           f'<div class="al-nav-barre"><i></i><i></i><i></i><span>{url}</span></div><div class="al-nav-corps">{corps}</div></div>')


def video_html(vid, video, d, piste=5, style="", debut=0):
    return (f'<video id="{vid}" class="clip" src="assets/video/{video}.mp4" data-start="{round(debut, 2)}" data-duration="{d}" data-track-index="{piste}" '
            f'muted playsinline style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; {style}"></video>')


def popup(s, pid, titre_p, texte, x, y, g, w=520):
    cam(s, f'<div id="{pid}" class="al-popup" style="left: {x}px; top: {y}px; width: {w}px; opacity: 0">'
           f'<div class="al-popup-barre">{TRIANGLE}<span>{titre_p}</span></div><div class="al-popup-corps">{texte}</div></div>')
    s.j(f'tl.fromTo("#{pid}", {{ opacity: 0, scale: 0.3, rotation: {(-6, 5, -3, 4, -5)[len(pid) % 5]} }}, '
        f'{{ opacity: 1, scale: 1, rotation: 0, duration: 0.18, ease: "back.out(2.6)" }}, {s.L(g)});')
    son(g, tour(["erreur-scifi", "erreur-echec", "erreur-clic", "buzzer-faux", "signal-alerte"]), 0.42, f"pop-up {titre_p}")


def carte(s, cid, x, y, w, h, tete, corps, coul=None):
    c = f' style="background: {coul}"' if coul else ""
    cam(s, f'<div id="{cid}" class="al-carte" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0">'
           f'<div class="al-carte-tete"{c}>{tete}</div><div class="al-carte-corps">{corps}</div></div>')


def badge_ok(s, bid, texte, x, y, g, taille=34):
    """Pastille verte « ✓ texte » qui s'écrase (validation)."""
    cam(s, f'<div id="{bid}" class="al-ok" style="left: {x}px; top: {y}px; font-size: {taille}px; opacity: 0">{COCHE.format(w=taille + 8, c="#0C0C0C")}<span>{texte}</span></div>')
    s.j(f'tl.fromTo("#{bid}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.15, ease: "power4.in" }}, {s.L(g)});')
    son(g, tour(["coche", "mission-ok", "bonne-reponse", "glitch-ok"]), 0.42, f"validé : {texte}")


def scan(s, sid, x, y, w, h, g, d=0.7):
    """Ligne de scan qui balaie un cadre."""
    cam(s, f'<div id="{sid}" class="al-scan" style="left: {x}px; top: {y}px; width: {w}px; opacity: 0"></div>')
    s.j(f'tl.fromTo("#{sid}", {{ opacity: 1, y: 0 }}, {{ opacity: 1, y: {h}, duration: {d}, ease: "power1.inOut", immediateRender: false }}, {s.L(g)});')
    s.j(f'tl.to("#{sid}", {{ opacity: 0, duration: 0.1 }}, {s.L(g + d)});')
    son(g, tour(["scanner", "radar"]), 0.32, "scan")


def alerte_rouge(s, aid, g, n=3, periode=0.26):
    """Clignotement orange de toute l'image (hors caméra)."""
    s.add(f'<div id="{aid}" class="al-alerte"></div>')
    s.j(f'tl.fromTo("#{aid}", {{ opacity: 0 }}, {{ opacity: 0.42, duration: {periode / 2}, repeat: {n * 2 - 1}, yoyo: true, ease: "sine.inOut", immediateRender: false }}, {s.L(g)});')


def gros_plan(s, pid, video, d, assombrir=0.5, op=0):
    """Vraie vidéo plein cadre (masquée au départ si op=0)."""
    cam(s, f'<div id="{pid}" style="position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden; opacity: {op}">'
           f'{video_html(pid + "-v", video, d)}'
           f'<div style="position: absolute; inset: 0; background: rgba(11, 14, 20, {assombrir})"></div></div>')


# ================================================================ SITE DE DÉMO « LUMEN » (faux site premium animé)
# Le site est construit en HTML dans les scènes (net en 1080p) : chaque section est une fonction qui renvoie son HTML
# et place ses animations à partir du temps g (temps de la vidéo). Les conteneurs portent data-layout-ignore : pour le
# contrôle de mise en page, le site est une « vidéo » (ses textes passent sous les sous-titres en défilant).
import html as htmlmod
VIOLET, CYAN = "#7C5CFF", "#22D3EE"
CURSEUR = ('<svg id="{id}" class="ds-curseur" viewBox="0 0 40 52" style="left: {x}px; top: {y}px">'
           '<path d="M3 3 L3 43 L13 33 L21 50 L28 47 L20 30 L35 30 Z" fill="#ffffff" stroke="#000000" stroke-width="3" stroke-linejoin="round" /></svg>')


def lettres(p, lignes, cls="ds-h1", style=""):
    """Titre découpé en lettres (chaque ligne masque ses lettres qui montent)."""
    out = []
    for n, ligne in enumerate(lignes):
        spans = "".join(f'<span class="ds-l">{c if c != " " else "&nbsp;"}</span>' for c in ligne)
        out.append(f'<span id="{p}-ligne{n}" class="ds-ligne">{spans}</span>')
    return f'<div id="{p}-titre" class="{cls}" style="{style}">{"".join(out)}</div>'


def revele_lettres(s, p, g, d=0.7, pas=0.022):
    s.j(f'tl.fromTo("#{p}-titre .ds-l", {{ yPercent: 115, rotation: 8 }}, {{ yPercent: 0, rotation: 0, duration: {d}, ease: "expo.out", stagger: {pas}, immediateRender: true }}, {s.L(g)});')


def blobs(s, p, g, d):
    """Halos de couleur qui dérivent lentement (dégradés radiaux, sans flou coûteux)."""
    html = []
    for k, (c, x, y, r) in enumerate(((ACCENT, 1250, -200, 760), (VIOLET, -200, 300, 820), (CYAN, 900, 500, 640))):
        html.append(f'<i id="{p}-b{k}" class="ds-blob" style="left: {x}px; top: {y}px; width: {r}px; height: {r}px; '
                    f'background: radial-gradient(circle, {c}88 0%, {c}22 45%, transparent 70%)"></i>')
        s.j(f'tl.fromTo("#{p}-b{k}", {{ x: 0, y: 0, scale: 1 }}, {{ x: {(-160, 220, -120)[k]}, y: {(120, -90, -140)[k]}, scale: {(1.2, 0.9, 1.25)[k]}, duration: {round(max(d, 1), 2)}, ease: "sine.inOut" }}, {s.L(g)});')
    return "".join(html)


def sec_hero(s, p, g, d, video="tunnel-cubes", lignes=("Des expériences", "qui captivent."), nav=True):
    """Héro : vidéo de fond, halos, menu, titre en lettres qui montent, bouton avec reflet, cartes flottantes."""
    nav_html = (f'<div id="{p}-nav" class="ds-nav"><b>LUMEN</b><span>Studio</span><span>Projets</span><span>Services</span>'
                f'<span>Contact</span><em>Démarrer</em></div>') if nav else ""
    flots = "".join(f'<div id="{p}-f{k}" class="ds-flot" style="left: {x}px; top: {y}px">'
                    f'<div class="ds-flot-v">{video_html(f"{p}-f{k}-v", v, round(d, 2), 7, debut=s.L(g))}</div><span>{t}</span></div>'
                    for k, (v, t, x, y) in enumerate((("graphiste", "Identité · 2026", 1380, 560), ("interface-vr", "Expérience 3D", 1520, 250))))
    html = (f'<div id="{p}" class="ds-section ds-hero">{video_html(p + "-v", video, round(d, 2), debut=s.L(g))}<div class="ds-voile"></div>'
            f'{blobs(s, p, g, d)}{nav_html}{lettres(p, lignes)}'
            f'<p id="{p}-sous" class="ds-sous">Sites web, animations et identités qui donnent envie de rester.</p>'
            f'<div id="{p}-cta" class="ds-cta"><span>Voir nos projets</span><i id="{p}-reflet"></i></div>{flots}</div>')
    if nav:
        s.j(f'tl.fromTo("#{p}-nav", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, {s.L(g)});')
    revele_lettres(s, p, g + 0.05)
    s.j(f'tl.fromTo("#{p}-sous", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, {s.L(g + 0.35)});')
    s.j(f'tl.fromTo("#{p}-cta", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2)" }}, {s.L(g + 0.45)});')
    s.j(f'tl.fromTo("#{p}-reflet", {{ x: -260 }}, {{ x: 520, duration: 0.9, ease: "power2.inOut", repeat: {max(0, int(d / 1.4))}, repeatDelay: 0.5 }}, {s.L(g + 0.6)});')
    for k in range(2):
        s.j(f'tl.fromTo("#{p}-f{k}", {{ y: 120, opacity: 0, rotation: {(-8, 6)[k]} }}, {{ y: 0, opacity: 1, rotation: {(-3, 4)[k]}, duration: 0.7, ease: "expo.out" }}, {s.L(g + 0.25 + k * 0.12)});')
        s.j(f'tl.to("#{p}-f{k}", {{ y: {(-26, 22)[k]}, duration: 1.1, ease: "sine.inOut", repeat: {max(1, int(d / 1.1))}, yoyo: true }}, {s.L(g + 0.95)});')
    return html


def sec_services(s, p, g, d, defile=900):
    """Défilement : la page descend, le titre se révèle, les cartes montent une à une, les compteurs défilent."""
    cartes = "".join(f'<div id="{p}-c{k}" class="ds-carte" style="left: {140 + k * 560}px">'
                     f'<div class="ds-carte-v">{video_html(f"{p}-c{k}-v", v, round(d, 2), 6 + k % 2, debut=s.L(g))}</div><b>{t}</b><span>{u}</span></div>'
                     for k, (v, t, u) in enumerate((("web-design", "Sites vitrines", "Design sur mesure"), ("montage-video", "Motion design", "Animations fluides"),
                                                    ("photo-produit", "E-commerce", "Pages qui vendent"))))
    stats = "".join(f'<div class="ds-stat"><b id="{p}-n{k}">0</b><span>{t}</span></div>' for k, t in enumerate(("% de conversions", "projets livrés", "pays")))
    html = (f'<div id="{p}" class="ds-section ds-services">{blobs(s, p, g, d)}<div id="{p}-defile" class="ds-defile">'
            f'<div class="ds-petit">— Nos services</div>{lettres(p, ("Chaque pixel", "a une intention."), "ds-h2")}{cartes}'
            f'<div id="{p}-stats" class="ds-stats">{stats}</div></div></div>')
    s.j(f'tl.fromTo("#{p}-defile", {{ y: 0 }}, {{ y: -{defile}, duration: {round(d, 2)}, ease: "power2.inOut" }}, {s.L(g)});')
    revele_lettres(s, p, g + 0.02, 0.6, 0.02)
    for k in range(3):
        s.j(f'tl.fromTo("#{p}-c{k}", {{ y: 220, opacity: 0, scale: 0.9 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "expo.out" }}, {s.L(g + d * 0.22 + k * 0.1)});')
        s.j(f'tl.fromTo("#{p}-c{k}-v", {{ scale: 1.3 }}, {{ scale: 1, duration: 1.0, ease: "power2.out" }}, {s.L(g + d * 0.22 + k * 0.1)});')
    for k, n in enumerate((240, 120, 18)):
        s.compteur(f"#{p}-n{k}", g + d * 0.5, 0, n, max(0.5, d * 0.4))
    s.j(f'tl.fromTo("#{p}-stats", {{ y: 80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, {s.L(g + d * 0.45)});')
    return html


def montagne(k, n=9):
    """Silhouette de montagne (points fixes)."""
    pts = [(0, 900)]
    for i in range(n + 1):
        x = round(i * 1920 / n)
        y = round(300 + 120 * k + 140 * math.sin(i * 1.7 + k * 2.3) + 70 * math.sin(i * 3.1 + k))
        pts.append((x, y))
    pts.append((1920, 900))
    return " ".join(f"{x},{y}" for x, y in pts)


def sec_parallaxe(s, p, g, d, course=520):
    """Parallaxe : 5 plans de montagnes, la lune, les étoiles et le titre bougent à des vitesses différentes."""
    couleurs = ("#2a2350", "#211c43", "#191536", "#120f29", "#0a0818")
    plans = []
    for k, c in enumerate(couleurs):
        plans.append(f'<svg id="{p}-m{k}" class="ds-plan" viewBox="0 0 1920 900" preserveAspectRatio="none" style="z-index: {k + 2}">'
                     f'<polygon points="{montagne(k)}" fill="{c}" /></svg>')
        if k == 1:
            plans.append(f'<div id="{p}-mot" class="ds-para-mot" style="z-index: 3">Explorer</div>')
    etoiles = "".join(f'<i style="left: {(k * 263) % 1900}px; top: {(k * 131) % 520}px; width: {2 + k % 3}px; height: {2 + k % 3}px"></i>' for k in range(70))
    html = (f'<div id="{p}" class="ds-section ds-para"><div id="{p}-etoiles" class="ds-etoiles">{etoiles}</div>'
            f'<i id="{p}-lune" class="ds-lune"></i>{"".join(plans)}<div class="ds-para-sous">— Parallaxe</div></div>')
    for k in range(5):
        f = (0.12, 0.3, 0.55, 0.8, 1.05)[k]
        s.j(f'tl.fromTo("#{p}-m{k}", {{ y: {round(course * f * 0.6)} }}, {{ y: -{round(course * f)}, duration: {round(d, 2)}, ease: "power1.inOut" }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{p}-mot", {{ y: 160, scale: 0.9, opacity: 0.4 }}, {{ y: -{round(course * 0.2)}, scale: 1.08, opacity: 1, duration: {round(d, 2)}, ease: "power1.inOut" }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{p}-lune", {{ y: 60 }}, {{ y: -{round(course * 0.06)}, duration: {round(d, 2)}, ease: "power1.inOut" }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{p}-etoiles", {{ y: 0 }}, {{ y: -{round(course * 0.04)}, duration: {round(d, 2)}, ease: "none" }}, {s.L(g)});')
    return html


def sec_transitions(s, p, g, d):
    """Transitions entre sections : un cercle s'ouvre sur la section suivante, puis la troisième monte en volet."""
    html = (f'<div id="{p}" class="ds-section ds-trans">'
            f'<div id="{p}-a" class="ds-trans-a">{video_html(p + "-a-v", "ville-futur", round(d, 2), debut=s.L(g))}<div class="ds-voile"></div>'
            f'{lettres(p + "a", ("Vision",), "ds-h2 ds-blanc")}</div>'
            f'<div id="{p}-b" class="ds-trans-b">{lettres(p + "b", ("Fluide.",), "ds-geant")}</div>'
            f'<div id="{p}-c" class="ds-trans-c">' + "".join(f'<div id="{p}-c{k}" class="ds-tuile">{video_html(f"{p}-c{k}-v", v, round(d, 2), 6 + k, debut=s.L(g))}</div>'
                                                             for k, v in enumerate(("sphere-donnees", "lunettes-ecran", "encre-liquide"))) +
            f'{lettres(p + "c", ("Sans couture.",), "ds-h2 ds-blanc ds-bas")}</div></div>')
    revele_lettres(s, p + "a", g, 0.5)
    g_b, g_c = g + d * 0.18, g + d * 0.6
    s.j(f'tl.fromTo("#{p}-b", {{ clipPath: "circle(0% at 50% 50%)" }}, {{ clipPath: "circle(75% at 50% 50%)", duration: 0.7, ease: "expo.inOut" }}, {s.L(g_b)});')
    s.j(f'tl.fromTo("#{p}-a", {{ scale: 1 }}, {{ scale: 0.85, duration: 0.7, ease: "expo.inOut" }}, {s.L(g_b)});')
    revele_lettres(s, p + "b", g_b + 0.25, 0.6, 0.04)
    s.j(f'tl.fromTo("#{p}-c", {{ clipPath: "inset(100% 0% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.6, ease: "expo.inOut" }}, {s.L(g_c)});')
    s.j(f'tl.fromTo("#{p}-b", {{ y: 0 }}, {{ y: -300, duration: 0.6, ease: "expo.inOut" }}, {s.L(g_c)});')
    for k in range(3):
        s.j(f'tl.fromTo("#{p}-c{k}", {{ y: 300, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: "expo.out" }}, {s.L(g_c + 0.15 + k * 0.08)});')
    revele_lettres(s, p + "c", g_c + 0.3, 0.6)
    return html


def sec_survol(s, p, g, d, boutons_a=None):
    """Survol : le pointeur passe sur les cartes (elles pivotent en 3D, la lumière suit), puis sur les boutons (aimantés)."""
    cartes = "".join(f'<div id="{p}-c{k}" class="ds-carte3d" style="left: {200 + k * 540}px">'
                     f'<div class="ds-carte-v">{video_html(f"{p}-c{k}-v", v, round(d, 2), 6 + k % 2, debut=s.L(g))}</div>'
                     f'<i id="{p}-l{k}" class="ds-lumiere"></i><b>{t}</b></div>'
                     for k, (v, t) in enumerate((("interface-vr", "Réalité mixte"), ("graphiste", "Identité"), ("tunnel-cubes", "3D"))))
    boutons = (f'<div id="{p}-btn0" class="ds-btn"><i id="{p}-rem0"></i><span>Découvrir</span></div>'
               f'<div id="{p}-btn1" class="ds-btn ds-btn2"><i id="{p}-rem1"></i><span>Nous contacter</span></div>')
    html = (f'<div id="{p}" class="ds-section ds-survol">{blobs(s, p, g, d)}<div class="ds-petit ds-centre">— Projets</div>{cartes}'
            f'<div class="ds-btns">{boutons}</div>{CURSEUR.format(id=p + "-souris", x=1700, y=980)}</div>')
    ba = boutons_a if boutons_a is not None else g + d * 0.68
    pts = [(g + 0.05, 1700, 980)] + [(g + 0.2 + k * (ba - g - 0.3) / 3, 420 + k * 540, 400 + (k % 2) * 40) for k in range(3)] + [(ba, 850, 780), (ba + d * 0.16, 1080, 780)]
    for (ta, xa, ya), (tb, xb, yb) in zip(pts, pts[1:]):
        s.j(f'tl.to("#{p}-souris", {{ x: {xb - 1700}, y: {yb - 980}, duration: {round(max(0.12, tb - ta - 0.05), 3)}, ease: "power2.inOut" }}, {s.L(ta)});')
    for k in range(3):
        t_in = pts[k + 1][0]
        t_out = pts[k + 2][0] - 0.05
        s.j(f'tl.to("#{p}-c{k}", {{ y: -30, scale: 1.06, rotationY: {(-14, 10, 14)[k]}, rotationX: 8, transformPerspective: 900, boxShadow: "0 40px 90px rgba(220, 252, 28, 0.35)", duration: 0.25, ease: "power3.out" }}, {s.L(t_in)});')
        s.j(f'tl.fromTo("#{p}-l{k}", {{ opacity: 0, x: -120 }}, {{ opacity: 1, x: 120, duration: {round(max(0.2, t_out - t_in), 3)}, ease: "none" }}, {s.L(t_in)});')
        s.j(f'tl.fromTo("#{p}-c{k}-v", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.3, ease: "power2.out", immediateRender: false }}, {s.L(t_in)});')
        s.j(f'tl.to("#{p}-c{k}", {{ y: 0, scale: 1, rotationY: 0, rotationX: 0, boxShadow: "0 20px 50px rgba(0, 0, 0, 0.5)", duration: 0.25, ease: "power2.out" }}, {s.L(t_out)});')
        s.j(f'tl.to("#{p}-l{k}", {{ opacity: 0, duration: 0.2 }}, {s.L(t_out)});')
        son(t_in, tour(["pop-click", "clic", "bouton-tech", "pop-sec"]), 0.3, "survol d'une carte")
    for k in range(2):
        t_b = pts[4 + k][0]
        s.j(f'tl.fromTo("#{p}-rem{k}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.3, ease: "power3.out", immediateRender: true }}, {s.L(t_b)});')
        s.j(f'tl.to("#{p}-btn{k}", {{ x: {(-14, 14)[k]}, y: -8, scale: 1.08, color: "#000000", duration: 0.25, ease: "back.out(2)" }}, {s.L(t_b)});')
        if k == 0:
            s.j(f'tl.to("#{p}-btn0", {{ x: 0, y: 0, scale: 1, duration: 0.25 }}, {s.L(pts[5][0] - 0.02)});')
            s.j(f'tl.to("#{p}-rem0", {{ scaleX: 0, duration: 0.2 }}, {s.L(pts[5][0] - 0.02)});')
        son(t_b, tour(["bouton", "interrupteur", "clic-positif"]), 0.35, "survol d'un bouton")
    return html


def sec_chaos(s, p, g, d):
    """Contre-exemple : tout bouge dans tous les sens."""
    cartes = "".join(f'<div id="{p}-c{k}" class="ds-carte" style="left: {140 + k * 560}px; top: 420px">'
                     f'<div class="ds-carte-v">{video_html(f"{p}-c{k}-v", v, round(d, 2), 6 + k % 2, debut=s.L(g))}</div><b>{t}</b></div>'
                     for k, (v, t) in enumerate((("site-ia-0", "PROMO !!!"), ("site-mode", "WOW !!!"), ("site-ia-2", "CLIQUE ICI"))))
    html = (f'<div id="{p}" class="ds-section ds-chaos"><i id="{p}-fond" class="ds-chaos-fond"></i>'
            f'{lettres(p, ("BIENVENUE !!!",), "ds-h1 ds-chaos-titre")}{cartes}'
            f'<div id="{p}-band" class="ds-chaos-band">★ SUPER PROMO ★ CLIQUE ★ SUPER PROMO ★ CLIQUE ★ SUPER PROMO ★</div></div>')
    n = max(2, int(d / 0.22))
    s.j(f'tl.to("#{p}-fond", {{ rotation: 360, duration: {round(d, 2)}, ease: "none" }}, {s.L(g)});')
    s.j(f'tl.to("#{p}-titre .ds-l", {{ rotation: 360, y: -40, duration: 0.5, ease: "none", stagger: {{ each: 0.04, repeat: {max(1, int(d / 0.5))} }} }}, {s.L(g)});')
    for k in range(3):
        s.j(f'tl.to("#{p}-c{k}", {{ y: {(-120, 90, -80)[k]}, rotation: {(25, -30, 40)[k]}, scale: {(1.25, 0.8, 1.2)[k]}, duration: 0.22, ease: "sine.inOut", repeat: {n}, yoyo: true }}, {s.L(g + k * 0.05)});')
    s.j(f'tl.fromTo("#{p}-band", {{ x: 0 }}, {{ x: -900, duration: {round(d, 2)}, ease: "none" }}, {s.L(g)});')
    s.j(f'tl.to("#{p}-band", {{ rotation: 6, duration: 0.15, repeat: {n}, yoyo: true }}, {s.L(g)});')
    return html


def plein_site(s, sid, html, op=0):
    """Section du site en plein cadre (dans la caméra)."""
    cam(s, f'<div id="{sid}" class="ds-plein" data-layout-ignore style="opacity: {op}">{html}</div>')


def site_fenetre(s, fid, html, x=110, y=96, w=1500, url="lumen-studio.fr", op=0):
    """Section du site dans une fenêtre de navigateur (contenu 1920×1080 réduit)."""
    k = round(w / 1920, 4)
    cam(s, f'<div id="{fid}" class="ds-fenetre" data-layout-ignore style="left: {x}px; top: {y}px; width: {w}px; height: {round(w * 9 / 16) + 52}px; opacity: {op}">'
           f'<div class="ds-fen-barre"><i></i><i></i><i></i><span>{url}</span></div>'
           f'<div class="ds-fen-vue" style="width: {w}px; height: {round(w * 9 / 16)}px"><div class="ds-fen-echelle" style="transform: scale({k})">{html}</div></div></div>')


def guide_droite(s, pid, g_montre, g_fort, g_fin=None, cx=1765, pieds=900, h=300):
    """Personnage dans la marge de droite : il montre le site, puis réagit."""
    cam(s, perso(pid, cx, pieds, h))
    vit(s, pid, s.debut, s.fin - 0.2)
    pose(s, pid, g_montre, 0.16, "back.out(2)", bg=95, tete=8)
    pose(s, pid, g_fort, 0.12, "back.out(2)", bg=150, bd=-150, tete=-6)
    saut(s, pid, g_fort + 0.02, 30)
    if g_fin:
        pouce(s, pid, g_fin)


def etiquette(s, eid, texte, g, x=150, y=70, rot=-4, taille=72):
    tampon(s, eid, texte, x, y, g, rot, taille)
    son(g, "impact-basse", 0.45, f"étiquette {texte}")
    son(g, tour(["scintille-whoosh", "swoosh-accent", "balaie-rapide"]), 0.38, "étiquette")


# ================================================================ ÉLÉMENTS DE LA VIDÉO 9 (vitesse, traînées)
LOGOS.update({"cloudflare": ("logo-cloudflare.svg", "Cloudflare"), "vercel": ("logo-vercel.svg", "Vercel"), "react": ("logo-react.svg", "React"),
              "google": ("logo-google.svg", "Google")})
ROUGE = "#FF4D4D"


def course_trace(s, pid, cx, pieds, h, g0, g1, dx, n=4, genre="toi"):
    """Le personnage court en laissant des traces : des copies de plus en plus transparentes le suivent."""
    for k in range(n, 0, -1):
        tid = f"{pid}-t{k}"
        cam(s, perso(tid, cx, pieds, h, genre))
        s.j(f'tl.set("#{tid}", {{ opacity: {round(0.55 / k, 2)} }}, 0);')
        court(s, tid, g0 + k * 0.045, g1 + k * 0.045, dx)
    cam(s, perso(pid, cx, pieds, h, genre))
    court(s, pid, g0, g1, dx)


def slam_trace(s, mid, texte, y, taille, g, fin=None, coul=None, x=0, w=1920, sens=1):
    """Mot qui arrive à toute vitesse en laissant une traînée (ombres étirées qui se résorbent)."""
    c = coul or ACCENT
    cam(s, f'<div id="{mid}" class="al-choc" style="left: {x}px; width: {w}px; top: {y}px; font-size: {taille}px; color: {c}; opacity: 0">{texte}</div>')
    ombres = ", ".join(f"{-sens * 60 * k}px 0 rgba(220, 252, 28, {round(0.45 / k, 2)})" for k in range(1, 6))
    s.j(f'tl.fromTo("#{mid}", {{ opacity: 1, x: {sens * -900}, skewX: {sens * -25}, textShadow: "{ombres}" }}, '
        f'{{ opacity: 1, x: 0, skewX: 0, textShadow: "0px 0 rgba(220, 252, 28, 0), 0px 0 rgba(220, 252, 28, 0), 0px 0 rgba(220, 252, 28, 0), 0px 0 rgba(220, 252, 28, 0), 0px 0 rgba(220, 252, 28, 0)", '
        f'duration: 0.32, ease: "expo.out", immediateRender: false }}, {s.L(g)});')
    if fin is not None:
        s.j(f'tl.to("#{mid}", {{ opacity: 0, x: {sens * 500}, duration: 0.18, ease: "power3.in" }}, {s.L(fin)});')


def chrono(s, cid, x, y, g0, g1, de=0.0, a=10.0, taille=220, coul="#FFFFFF"):
    """Chronomètre « 0,0 s » qui défile (virgule française)."""
    cam(s, f'<div id="{cid}" class="vt-chrono" style="left: {x}px; top: {y}px; font-size: {taille}px; color: {coul}; opacity: 0"><b id="{cid}-n">0,0</b><span>s</span></div>')
    s.n_proxy += 1
    p = f"ch{s.n_proxy}"
    s.j(f'const {p} = {{ v: {de} }};')
    s.j(f'tl.fromTo({p}, {{ v: {de} }}, {{ v: {a}, duration: {round(g1 - g0, 3)}, ease: "none", immediateRender: false, '
        f'onUpdate: () => {{ document.querySelector("#{cid}-n").textContent = {p}.v.toFixed(1).replace(".", ","); }} }}, {s.L(g0)});')


def page_qui_charge(s, pid, x, y, w, h, g):
    """Navigateur avec page blanche : squelettes qui clignotent, roue qui tourne, barre de progression bloquée."""
    sq = "".join(f'<i class="vt-sq" style="left: {a}px; top: {b}px; width: {c}px; height: {d}px"></i>'
                 for a, b, c, d in ((60, 60, 520, 60), (60, 150, 760, 34), (60, 200, 640, 34), (60, 290, 300, 240), (390, 290, 300, 240), (720, 290, 300, 240)))
    corps = (f'<div class="vt-page">{sq}<div id="{pid}-roue" class="vt-roue"></div><div class="vt-barre"><i id="{pid}-prog"></i></div>'
             f'<div class="vt-charge">Chargement…</div></div>')
    navigateur(s, pid, x, y, w, h, "ton-site.fr", corps)
    s.j(f'tl.set("#{pid}", {{ opacity: 1 }}, {s.L(g)});')
    s.j(f'tl.to("#{pid}-roue", {{ rotation: 360 * 8, duration: 4, ease: "none" }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{pid}-prog", {{ scaleX: 0 }}, {{ scaleX: 0.22, duration: 0.6, ease: "power2.out" }}, {s.L(g)});')
    s.j(f'tl.to("#{pid}-prog", {{ scaleX: 0.27, duration: 2.5, ease: "none" }}, {s.L(g + 0.6)});')
    s.j(f'tl.to("#{pid} .vt-sq", {{ opacity: 0.35, duration: 0.45, repeat: 7, yoyo: true, ease: "sine.inOut", stagger: 0.08 }}, {s.L(g)});')


def jauge(s, jid, x, y, g, de, a, d=0.9, taille=300, titre_j="Performances"):
    """Jauge de score façon Lighthouse (cercle qui se remplit, couleur selon le score)."""
    r = 120
    L = round(2 * math.pi * r, 1)
    cam(s, f'<div id="{jid}" class="vt-jauge" style="left: {x}px; top: {y}px; width: {taille}px; opacity: 0">'
           f'<svg viewBox="0 0 300 300" width="{taille}" height="{taille}"><circle cx="150" cy="150" r="{r}" fill="none" stroke="#2a2a2a" stroke-width="22" />'
           f'<circle id="{jid}-arc" cx="150" cy="150" r="{r}" fill="none" stroke="{ROUGE}" stroke-width="22" stroke-linecap="round" '
           f'stroke-dasharray="{L}" stroke-dashoffset="{L}" transform="rotate(-90 150 150)" /></svg>'
           f'<b id="{jid}-n">0</b><span>{titre_j}</span></div>')
    s.j(f'tl.fromTo("#{jid}", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }}, {s.L(g)});')
    s.n_proxy += 1
    p = f"j{s.n_proxy}"
    s.j(f'const {p} = {{ v: {de} }};')
    s.j(f'tl.fromTo({p}, {{ v: {de} }}, {{ v: {a}, duration: {d}, ease: "power2.out", immediateRender: false, onUpdate: () => {{ '
        f'const v = Math.round({p}.v); document.querySelector("#{jid}-n").textContent = v; '
        f'const c = v >= 90 ? "#0CCE6B" : (v >= 50 ? "#FFA400" : "{ROUGE}"); '
        f'const arc = document.querySelector("#{jid}-arc"); arc.setAttribute("stroke-dashoffset", {L} * (1 - v / 100)); arc.setAttribute("stroke", c); '
        f'document.querySelector("#{jid}-n").style.color = c; }} }}, {s.L(g + 0.1)});')


def cascade(s, cid, x, y, lignes, g, pas=0.12):
    """Chronologie de chargement (cascade réseau) : barres de longueur variable, en rouge les ressources lourdes."""
    html = []
    for k, (nom, debut, long, lourd) in enumerate(lignes):
        c = ROUGE if lourd else "#4a9eff"
        html.append(f'<div class="vt-res" style="top: {k * 58}px"><span>{nom}</span><i id="{cid}-{k}" style="left: {220 + debut}px; width: {long}px; background: {c}"></i></div>')
        s.j(f'tl.fromTo("#{cid}-{k}", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.35, ease: "power2.out" }}, {s.L(g + k * pas)});')
    cam(s, f'<div id="{cid}" class="vt-cascade" style="left: {x}px; top: {y}px; opacity: 0"><div class="vt-cas-tete">Chargement de la page</div>'
           f'<div class="vt-cas-corps">{"".join(html)}</div></div>')
    s.apparait(f"#{cid}", g - 0.1, 30)


def suggestion(s, sid, texte, x, y, g, ok=True):
    ic = COCHE.format(w=34, c="#0C0C0C") if ok else TRIANGLE
    cl = "vt-sugg" if ok else "vt-sugg vt-pb"
    cam(s, f'<div id="{sid}" class="{cl}" style="left: {x}px; top: {y}px; opacity: 0"><i>{ic}</i><span>{texte}</span></div>')
    s.j(f'tl.fromTo("#{sid}", {{ opacity: 0, x: 120 }}, {{ opacity: 1, x: 0, duration: 0.22, ease: "back.out(2)" }}, {s.L(g)});')
    son(g, tour(["pop-click", "coche", "pop-sec", "bonne-reponse"]) if ok else tour(["erreur-clic", "buzz-faux", "erreur-scifi"]), 0.4, texte)


def poids(s, pid, nom, x, y, w, de, a, unite_de, unite_a, g, d=0.8):
    """Barre de poids de fichier qui fond (ex. 4,8 Mo → 320 Ko)."""
    cam(s, f'<div id="{pid}" class="vt-poids" style="left: {x}px; top: {y}px; width: {w}px; opacity: 0"><span>{nom}</span>'
           f'<div class="vt-poids-piste"><i id="{pid}-b"></i></div><b id="{pid}-n">{de} {unite_de}</b></div>')
    s.apparait(f"#{pid}", g - 0.15, 20)
    s.j(f'tl.fromTo("#{pid}-b", {{ scaleX: 1, backgroundColor: "{ROUGE}" }}, {{ scaleX: {round(max(0.06, 1 - 0.93), 2)}, backgroundColor: "#0CCE6B", duration: {d}, ease: "power3.inOut", immediateRender: false }}, {s.L(g)});')
    s.j(f'tl.set("#{pid}-n", {{ opacity: 0 }}, {s.L(g + d * 0.5)});')
    cam(s, f'<b id="{pid}-n2" class="vt-poids-n2" style="left: {x + w - 230}px; top: {y + 4}px; opacity: 0">{a} {unite_a}</b>')
    s.j(f'tl.set("#{pid}-n2", {{ opacity: 1 }}, {s.L(g + d * 0.5)});')
    son(g, tour(["swoosh-monte", "balaie", "zoom-in-out"]), 0.36, f"{nom} fond")


# ================================================================ ÉLÉMENTS DE LA VIDÉO 10 (SEO)
LOGOS.update({"google": ("logo-google.svg", "Google")})
ROUGE = "#FF4D4D"


def media_plein(mid, kind, f, debut_local, duree, piste=5):
    """Vraie vidéo ou vraie photo en plein cadre (cachée au départ)."""
    if kind == "v":
        m = (f'<video id="{mid}-v" class="clip" src="assets/video/{f}.mp4" data-start="{round(debut_local, 2)}" data-duration="{round(duree, 2)}" '
             f'data-track-index="{piste}" muted playsinline style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover"></video>')
    else:
        m = f'<img src="assets/img/{f}.jpg" alt="" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover" />'
    return f'<div id="{mid}" class="sx-plein" style="opacity: 0">{m}</div>'


def rafale_mots(s, p, items, fin):
    """Une vraie vidéo ou photo par mot : coupe sèche, petit coup de zoom, flash et rush."""
    for k, (t, kind, f) in enumerate(items):
        t2 = items[k + 1][0] if k + 1 < len(items) else fin
        mid = f"{p}-{k}"
        cam(s, media_plein(mid, kind, f, s.L(t), t2 - t + 0.1, 5 + k % 3))
        s.j(f'tl.set("#{mid}", {{ opacity: 1 }}, {s.L(t)});')
        sens = (1, -1)[k % 2]
        s.j(f'tl.fromTo("#{mid}", {{ scale: {1.22 if k % 3 == 0 else 1.12}, x: {sens * (60 if k % 3 == 1 else 0)}, rotation: {sens * (2 if k % 4 == 2 else 0)} }}, '
            f'{{ scale: 1.02, x: 0, rotation: 0, duration: {round(max(0.2, t2 - t), 3)}, ease: "power2.out", immediateRender: false }}, {s.L(t)});')
        if k + 1 < len(items):
            s.j(f'tl.set("#{mid}", {{ opacity: 0 }}, {s.L(t2 + 0.02)});')
        if k % 6 == 0:
            s.eclair(t)
        son(t, tour(["balaie-rapide", "fouet", "balaie-court", "swoosh-court", "declencheur", "balaie-air", "glitch-mini", "souffle-rapide"]), 0.42, f"coupe {f}")
        if k % 4 == 1:
            son(t, tour(["impact-futur", "impact-cartoon", "glitch-court", "impact-whoosh"]), 0.34, "choc")


def barre_google(s, bid, x, y, w, texte, g0, g1, resultat=None, g_res=None):
    """Barre de recherche façon moteur de recherche : texte tapé, puis « Aucun résultat »."""
    spans = "".join(f'<span id="{bid}-c{k}" style="opacity: 0">{c if c != " " else "&nbsp;"}</span>' for k, c in enumerate(texte))
    res = f'<div id="{bid}-res" class="sx-res" style="opacity: 0">{resultat}</div>' if resultat else ""
    cam(s, f'<div id="{bid}" class="sx-barre" style="left: {x}px; top: {y}px; width: {w}px; opacity: 0">'
           f'<div class="sx-champ"><svg viewBox="0 0 24 24" width="40" height="40"><circle cx="10" cy="10" r="7" fill="none" stroke="#9aa0a6" stroke-width="2.5" />'
           f'<path d="M15 15 L22 22" stroke="#9aa0a6" stroke-width="2.5" stroke-linecap="round" /></svg><div>{spans}</div></div>{res}</div>')
    s.j(f'tl.fromTo("#{bid}", {{ opacity: 0, y: 40, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.18, ease: "back.out(2)" }}, {s.L(g0 - 0.1)});')
    for k in range(len(texte)):
        s.montre(f"#{bid}-c{k}", g0 + k * (g1 - g0) / len(texte))
    son(g0, "clavier-ordi", 0.42, "on tape la recherche", d=round(g1 - g0, 2))
    if resultat:
        s.j(f'tl.fromTo("#{bid}-res", {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 0, duration: 0.15 }}, {s.L(g_res)});')
        son(g_res, "erreur-echec", 0.42, "aucun résultat")


def liste_pb(s, p, x, y, lignes, g0, pas, ok=False, w=740):
    for k, t in enumerate(lignes):
        suggestion(s, f"{p}{k}", t, x, y + k * 78, g0 + k * pas, ok)


def suggestion(s, sid, texte, x, y, g, ok=True):
    ic = COCHE.format(w=34, c="#0C0C0C") if ok else TRIANGLE
    cl = "sx-sugg" if ok else "sx-sugg sx-pb"
    cam(s, f'<div id="{sid}" class="{cl}" style="left: {x}px; top: {y}px; opacity: 0"><i>{ic}</i><span>{texte}</span></div>')
    s.j(f'tl.fromTo("#{sid}", {{ opacity: 0, x: 120 }}, {{ opacity: 1, x: 0, duration: 0.22, ease: "back.out(2)" }}, {s.L(g)});')
    son(g, tour(["pop-click", "coche", "pop-sec", "bonne-reponse"]) if ok else tour(["erreur-clic", "buzz-faux", "erreur-scifi"]), 0.4, texte)


def photo_carte(s, pid, f, x, y, w, h, g, rot=0, tag=None, kind="img", piste=6):
    """Vraie photo (ou vidéo) en carte, qui arrive en tournant."""
    if kind == "img":
        m = f'<img src="assets/img/{f}.jpg" alt="" />'
    else:
        m = (f'<video id="{pid}-v" class="clip" src="assets/video/{f}.mp4" data-start="{s.L(g)}" data-duration="{round(s.fin - g, 2)}" '
             f'data-track-index="{piste}" muted playsinline></video>')
    t = f'<div class="pj-panneau-tag">{tag}</div>' if tag else ""
    cam(s, f'<div id="{pid}" class="pj-panneau sx-photo" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; transform: rotate({rot}deg); opacity: 0">{m}{t}</div>')
    s.j(f'tl.fromTo("#{pid}", {{ opacity: 0, scale: 1.6, rotation: {rot * 3} }}, {{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.22, ease: "back.out(1.8)" }}, {s.L(g)});')
    son(g, tour(["flashs-photo" if "flashs-photo" in PICS else "photo", "photo", "pop-long", "declencheur"]), 0.34, f"photo {f}")


def code_carte(s, cid, x, y, w, lignes, g0, pas=0.1, titre_c="schema.json"):
    l = "".join(f'<div id="{cid}-{k}" class="al-code-l" style="opacity: 0"><i>{k + 1:02d}</i>{htmlmod.escape(c)}</div>' for k, c in enumerate(lignes))
    navigateur(s, cid, x, y, w, 70 + 46 * len(lignes) + 40, titre_c, f'<div class="al-code" style="font-size: 27px">{l}</div>')
    s.apparait(f"#{cid}", g0 - 0.15, 30)
    for k in range(len(lignes)):
        s.montre(f"#{cid}-{k}", g0 + k * pas)
    son(g0, "clavier-ordi-2", 0.4, "code", d=round(pas * len(lignes), 2))


def resultat_riche(s, rid, x, y, g):
    """Résultat de recherche enrichi (étoiles, prix, disponibilité) grâce aux données structurées."""
    cam(s, f'<div id="{rid}" class="sx-riche" style="left: {x}px; top: {y}px; opacity: 0">'
           f'<span class="sx-url">ton-site.fr › boutique</span><b>Lampe design en bois — Ton Site</b>'
           f'<div class="sx-etoiles"><i id="{rid}-et">★★★★★</i> 4,8 (126 avis) · 49,00 € · En stock</div>'
           f'<p>Lampe artisanale en chêne massif, livrée en 48 h.</p></div>')
    s.j(f'tl.fromTo("#{rid}", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "back.out(2)" }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{rid}-et", {{ clipPath: "inset(0% 100% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.5, ease: "power2.out" }}, {s.L(g + 0.2)});')
    son(g + 0.2, "scintille", 0.42, "étoiles")


def arbre(s, aid, x, y, g0, pas=0.16):
    """Plan du site : page d'accueil → rubriques → pages, avec leurs URL et les liens internes."""
    noeuds = [("Accueil", "/", 380, 0), ("Services", "/services", 60, 190), ("Blog", "/blog", 380, 190), ("Contact", "/contact", 700, 190),
              ("Création de site", "/services/creation-site", 0, 390), ("SEO", "/services/seo", 260, 390), ("Article 1", "/blog/guide-seo", 520, 390)]
    liens = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 6)]
    traits = "".join(f'<line id="{aid}-l{k}" x1="{noeuds[a][2] + 110}" y1="{noeuds[a][3] + 70}" x2="{noeuds[b][2] + 110}" y2="{noeuds[b][3]}" '
                     f'stroke="#DCFC1C" stroke-width="4" />' for k, (a, b) in enumerate(liens))
    blocs = "".join(f'<div id="{aid}-n{k}" class="sx-noeud" style="left: {nx}px; top: {ny}px; opacity: 0"><b>{n}</b><span id="{aid}-u{k}" style="opacity: 0">{u}</span></div>'
                    for k, (n, u, nx, ny) in enumerate(noeuds))
    cam(s, f'<div id="{aid}" class="sx-arbre" style="left: {x}px; top: {y}px"><svg class="sx-traits" viewBox="0 0 920 500" width="920" height="500">{traits}</svg>{blocs}</div>')
    for k in range(len(noeuds)):
        s.j(f'tl.fromTo("#{aid}-n{k}", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.4)" }}, {s.L(g0 + k * pas)});')
        pop(g0 + k * pas, 0.34, "page")
    for k in range(len(liens)):
        s.j(f'tl.fromTo("#{aid}-l{k}", {{ strokeDasharray: 400, strokeDashoffset: 400 }}, {{ strokeDashoffset: 0, duration: 0.3, ease: "power2.out" }}, {s.L(g0 + 0.15 + k * pas)});')
    return noeuds


# ================================================================ ÉLÉMENTS DE LA VIDÉO 11 (sites 3D immersifs)
LOGOS.update({"framer": ("logo-framer.svg", "Framer"), "spline": ("logo-spline.png", "Spline")})


def fond(s, p, mots, fichiers, voile=0.5, flash=False):
    """Rafale de vraies vidéos/photos en fond de scène : une nouvelle tous les 1–2 mots, puis un voile sombre."""
    items = [(s.debut if k == 0 else t_mot(i), "i" if f.endswith(".jpg") else "v", f.replace(".jpg", "")) for k, (i, f) in enumerate(zip(mots, fichiers))]
    rafale_mots(s, p, items, s.fin, flash)
    if voile:
        cam(s, f'<div id="{p}-voile" style="position: absolute; inset: 0; background: rgba(12, 12, 12, {voile})"></div>')


def rafale_mots(s, p, items, fin, flash=True):
    """Une vraie vidéo ou photo par mot : coupe sèche, coup de zoom, rush (et flash si demandé)."""
    for k, (t, kind, f) in enumerate(items):
        t2 = items[k + 1][0] if k + 1 < len(items) else fin
        mid = f"{p}-{k}"
        cam(s, media_plein(mid, kind, f, s.L(t), t2 - t + 0.1, 5 + k % 3))
        s.j(f'tl.set("#{mid}", {{ opacity: 1 }}, {s.L(t)});')
        sens = (1, -1)[k % 2]
        s.j(f'tl.fromTo("#{mid}", {{ scale: {1.22 if k % 3 == 0 else 1.12}, x: {sens * (60 if k % 3 == 1 else 0)}, rotation: {sens * (2 if k % 4 == 2 else 0)} }}, '
            f'{{ scale: 1.02, x: 0, rotation: 0, duration: {round(max(0.2, t2 - t), 3)}, ease: "power2.out", immediateRender: false }}, {s.L(t)});')
        if k + 1 < len(items):
            s.j(f'tl.set("#{mid}", {{ opacity: 0 }}, {s.L(t2 + 0.02)});')
        if flash and k % 6 == 0 and k > 0:
            s.eclair(t)
        if k > 0:
            son(t, tour(["balaie-rapide", "fouet", "balaie-court", "swoosh-court", "declencheur", "balaie-air", "glitch-mini", "souffle-rapide"]), 0.4, f"coupe {f}")
        if k % 4 == 1:
            son(t, tour(["impact-futur", "impact-cartoon", "glitch-court", "impact-whoosh"]), 0.32, "choc")


def objet3d(s, oid, f, x, y, w, h, g, rot=0):
    """Photo d'objet 3D en carte flottante (elle flotte en continu)."""
    cam(s, f'<div id="{oid}" class="pj-panneau sx-photo td-objet" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; transform: rotate({rot}deg); opacity: 0">'
           f'<img src="assets/img/{f}.jpg" alt="" /></div>')
    s.j(f'tl.fromTo("#{oid}", {{ opacity: 0, scale: 0.3, rotationY: 70, transformPerspective: 900 }}, {{ opacity: 1, scale: 1, rotationY: 0, duration: 0.35, ease: "back.out(1.8)" }}, {s.L(g)});')
    s.j(f'tl.to("#{oid}", {{ y: -18, duration: 0.9, ease: "sine.inOut", repeat: {max(1, int((s.fin - g) / 0.9))}, yoyo: true }}, {s.L(g + 0.35)});')
    son(g, tour(["jeu-balayage", "scifi-positif", "pop-long", "magie"]), 0.36, f"objet 3D {f}")


def invite(s, iid, texte, x, y, w, g0, g1, logo="logo-spline.png", titre_i="Décris ton idée"):
    """Champ de demande à l'IA, tapé mot à mot."""
    mots_i = texte.split(" ")
    spans = " ".join(f'<span id="{iid}-w{k}" style="opacity: 0">{m}</span>' for k, m in enumerate(mots_i))
    cam(s, f'<div id="{iid}" class="al-chat" style="left: {x}px; top: {y}px; width: {w}px; opacity: 0"><div class="al-chat-tete"><img src="assets/img/{logo}" alt="" />'
           f'<span>{titre_i}</span></div><div class="al-chat-champ" style="min-height: 0; font-size: 42px">{spans}</div></div>')
    s.j(f'tl.fromTo("#{iid}", {{ opacity: 0, y: 80, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.22, ease: "back.out(1.8)" }}, {s.L(g0 - 0.2)});')
    for k in range(len(mots_i)):
        s.montre(f"#{iid}-w{k}", g0 + k * (g1 - g0) / len(mots_i))
    son(g0, "clavier-ordi-2", 0.42, "on tape la demande", d=round(g1 - g0, 2))


# ================================================================ ÉLÉMENTS DE LA VIDÉO 12 (5 sites de business)
def site_metier(s, p, g, d, marque, lignes, slogan, media, cartes, cta, couleur="#DCFC1C", defile=None, widgets=(), url=None):
    """Faux site professionnel d'un métier (1920×1080) : menu, héro avec vraie vidéo, cartes avec vraies photos,
    défilement vers les cartes, et fenêtres (réservation, devis…) qui apparaissent à leur moment."""
    kind, f = media
    if kind == "v":
        m = video_html(f"{p}-hv", f, round(d, 2), 6, "", s.L(g))
    else:
        m = f'<img src="assets/img/{f}.jpg" alt="" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover" />'
    cs = "".join(f'<div id="{p}-c{k}" class="bz-carte"><div class="bz-carte-img"><img src="assets/img/{im}.jpg" alt="" /></div><b>{t}</b><span>{u}</span></div>'
                 for k, (im, t, u) in enumerate(cartes))
    ws = "".join(f'<div id="{p}-w{k}" class="bz-widget" style="opacity: 0">{h}</div>' for k, (gw, h) in enumerate(widgets))
    html = (f'<div id="{p}" class="ds-section bz-page" style="--bz: {couleur}"><div id="{p}-defile" class="bz-defile">'
            f'<div class="bz-nav"><b>{marque}</b><span>Accueil</span><span>Services</span><span>Avis</span><span>Contact</span><em>{cta}</em></div>'
            f'{lettres(p, lignes, "ds-h1 bz-h1")}<p class="bz-slogan">{slogan}</p><div class="bz-cta">{cta}</div>'
            f'<div class="bz-hero-media">{m}</div><div class="bz-cartes">{cs}</div></div>{ws}</div>')
    revele_lettres(s, p, g + 0.05, 0.6, 0.025)
    s.j(f'tl.fromTo("#{p} .bz-hero-media", {{ scale: 1.15, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.6, ease: "expo.out" }}, {s.L(g)});')
    for k in range(len(cartes)):
        s.j(f'tl.fromTo("#{p}-c{k}", {{ y: 160, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "expo.out" }}, {s.L(g + 0.35 + k * 0.1)});')
    if defile:
        s.j(f'tl.to("#{p}-defile", {{ y: -470, duration: 0.6, ease: "power3.inOut" }}, {s.L(defile)});')
        son(defile, tour(["balaie", "balaie-air", "pages-defilent"]), 0.4, "le site défile")
    for k, (gw, h) in enumerate(widgets):
        s.j(f'tl.fromTo("#{p}-w{k}", {{ opacity: 0, y: 80, scale: 0.85 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.8)" }}, {s.L(gw)});')
        if k > 0:
            s.j(f'tl.to("#{p}-w{k - 1}", {{ opacity: 0, y: -40, duration: 0.15 }}, {s.L(gw - 0.05)});')
        son(gw, tour(["pop-long", "notif-positive", "clic-positif", "pop-bulle"]), 0.42, "fenêtre du site")
    return html


def w_form(titre_w, champs, bouton):
    ch = "".join(f'<div class="bz-champ"><span>{c}</span><b>{v}</b></div>' for c, v in champs)
    return f'<div class="bz-w-tete">{titre_w}</div>{ch}<div class="bz-w-btn">{bouton}</div>'


def scene_metier(k_sc, n, nom, mots_fond, fichiers, i_num, i_nom, fonctions, site_args, toi_x=650):
    """Scène d'un métier : rafale de vraies vidéos en fond, numéro + titre, fonctions qui claquent, le site à droite."""
    s = scene(k_sc, f"Scène {k_sc + 1} · {n}. {nom}")
    fond(s, f"{NOMS[k_sc][:3]}-f", mots_fond, fichiers, 0.55)
    numero(s, f"{NOMS[k_sc][:3]}-n", f"0{n}", t_mot(i_num), t_mot(i_nom) - 0.15)
    titre(s, f"{NOMS[k_sc][:3]}-titre", nom, t_mot(i_nom), 100, 300, 175)
    p = f"{NOMS[k_sc][:3]}-site"
    g_site = t_mot(i_nom) + 0.25
    site_fenetre(s, f"{NOMS[k_sc][:3]}-fen", site_metier(s, p, g_site, s.fin - g_site + 0.2, **site_args), 840, 290, 960,
                 site_args.get("url", "mon-client.fr"))
    s.j(f'tl.fromTo("#{NOMS[k_sc][:3]}-fen", {{ opacity: 0, x: 600, rotationY: -25, transformPerspective: 1400 }}, {{ opacity: 1, x: 0, rotationY: 0, duration: 0.4, ease: "expo.out" }}, {s.L(g_site)});')
    son(g_site, tour(["balaie-rapide", "scintille-whoosh", "balaie-air"]), 0.45, "le site arrive")
    for j, (t, i) in enumerate(fonctions):
        puce(s, f"{NOMS[k_sc][:3]}-p{j}", t, 400, 360 + j * 88, t_mot(i))
        son(t_mot(i), tour(["pop-click", "pop-sec", "coche", "pop-bulle"]), 0.42, t)
        son(t_mot(i), tour(["impact-futur", "impact-cartoon", "glitch-court"]), 0.3, "choc")
    cam(s, perso(f"{NOMS[k_sc][:3]}-toi", toi_x, 860, 180))
    vit(s, f"{NOMS[k_sc][:3]}-toi", s.debut, s.fin - 0.2)
    pose(s, f"{NOMS[k_sc][:3]}-toi", g_site + 0.2, 0.16, "back.out(2)", bd=-100, tete=-8)
    victoire(s, f"{NOMS[k_sc][:3]}-toi", t_mot(fonctions[-1][1]) + 0.2, 1)
    zoom(s, g_site + 0.4, 960, 560, 1.07)
    return s


# ================================================================ ÉLÉMENTS DE LA VIDÉO 13 (types de sites : mystère, caméra qui suit)
LOGOS.update({"netflix": ("logo-netflix.svg", "Netflix"), "airbnb": ("logo-airbnb.svg", "Airbnb")})
NUIT = "rgba(6, 6, 8, 0.88)"


def _borne(px, py, sc):
    """Garde le recadrage dans l'image (jamais de bord vide)."""
    if sc <= 1:
        return 960, 540
    mx, my = 960 / sc, 540 / sc
    return min(max(px, mx), 1920 - mx), min(max(py, my), 1080 - my)


def suit(s, points, sc, d0=0.3, v=0.42):
    """Caméra qui SUIT l'action : recadrage filé sur le 1er point, puis panoramiques doux de point en point.
    points : [(t, px, py), ...] — à chaque t, la caméra repart vers le point suivant."""
    t0, px, py = points[0]
    px, py = _borne(px, py, sc)
    zoom(s, t0, px, py, sc, d0, v)
    for k in range(1, len(points)):
        ta = points[k - 1][0] + (d0 if k == 1 else 0)
        tb, xb, yb = points[k]
        xb, yb = _borne(xb, yb, sc)
        x, y = round(-(xb - 960) * sc), round(-(yb - 540) * sc)
        d = round(max(0.25, tb - ta), 3)
        s.j(f'tl.to("#{s.id}-cadre", {{ x: {x}, y: {y}, scale: {sc}, duration: {d}, ease: "sine.inOut" }}, {s.L(ta)});')
        son(ta + 0.05, tour(["souffle-air", "balaie-air", "swoosh-vol", "balaie-petit"]), 0.3, "la caméra suit")


def pano(s, g, d, px, py, sc):
    """Panoramique continu (la caméra accompagne un déplacement), sans coup de zoom."""
    px, py = _borne(px, py, sc)
    s.j(f'tl.to("#{s.id}-cadre", {{ x: {round(-(px - 960) * sc)}, y: {round(-(py - 540) * sc)}, scale: {sc}, duration: {d}, ease: "sine.inOut" }}, {s.L(g)});')


def carte_mystere_html(p, n, nom, x, y, w=520, h=660, taille_nom=104):
    cad = CADENAS.format(id=f"{p}-cad", x=round(w / 2 - 50), y=h - 200, w=100, h=125)
    return (f'<div id="{p}" class="my-carte" data-layout-allow-overlap style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0">'
            f'<div id="{p}-dos" class="my-face my-dos"><span class="my-num">Type n°{n}</span><b>?</b>{cad}</div>'
            f'<div id="{p}-avant" class="my-face my-avant"><span class="my-num">Type n°{n}</span><b style="font-size: {taille_nom}px">{nom}</b></div></div>')


def mystere(s, p, n, g_num, g_nom, nom, taille_nom=104):
    """Le mystère : nuit + projecteur, carte face cachée (« ? », cadenas) pendant le silence après le numéro ;
    la caméra s'approche lentement ; sur le nom, le cadenas saute, la carte se retourne (flash, choc), puis s'envole."""
    cam(s, f'<div id="{p}-nuit" class="my-nuit" style="opacity: 0"></div>')
    cam(s, carte_mystere_html(p, n, nom, 700, 150, 520, 660, taille_nom))
    s.j(f'tl.set("#{p}-nuit", {{ opacity: 1 }}, {s.L(g_num - 0.02)});')
    s.j(f'tl.fromTo("#{p}", {{ opacity: 0, y: -760, rotation: -14 }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.34, ease: "back.out(1.6)" }}, {s.L(g_num)});')
    s.j(f'tl.set("#{p}-cad", {{ opacity: 1 }}, {s.L(g_num)});')
    attente = round(g_nom - g_num - 0.45, 3)
    if attente > 0.2:
        n_rep = max(1, int(attente / 0.08))
        s.j(f'tl.fromTo("#{p}", {{ x: -5 }}, {{ x: 5, duration: 0.04, repeat: {n_rep}, yoyo: true, ease: "none", immediateRender: false }}, {s.L(g_num + 0.38)});')
    s.j(f'tl.to("#{p}-cad-anse", {{ y: -26, duration: 0.1, ease: "back.out(3)" }}, {s.L(g_nom - 0.1)});')
    s.j(f'tl.to("#{p}-cad", {{ opacity: 0, y: 120, rotation: 25, duration: 0.25 }}, {s.L(g_nom + 0.02)});')
    s.j(f'tl.to("#{p}", {{ rotationY: 180, transformPerspective: 1600, duration: 0.32, ease: "power3.inOut" }}, {s.L(g_nom - 0.05)});')
    s.j(f'tl.to("#{p}-nuit", {{ opacity: 0, duration: 0.3 }}, {s.L(g_nom + 0.1)});')
    # (pas d'opacité sur la carte 3D elle-même : elle aplatirait la carte et montrerait le dos à l'envers)
    s.j(f'tl.to("#{p}", {{ x: -560, y: -250, scale: 0.25, duration: 0.3, ease: "power3.in" }}, {s.L(g_nom + 0.7)});')
    s.j(f'tl.to(["#{p}-avant", "#{p}-dos"], {{ opacity: 0, duration: 0.3, ease: "power3.in" }}, {s.L(g_nom + 0.7)});')
    # la caméra s'approche lentement pendant le silence, puis repart d'un coup sur le nom
    s.j(f'tl.to("#{s.id}-cadre", {{ x: 0, y: {round(-(480 - 540) * 1.16)}, scale: 1.16, duration: {round(g_nom - g_num - 0.1, 3)}, ease: "power1.in" }}, {s.L(g_num + 0.05)});')
    s.eclair(g_nom + 0.12)
    secousse(s, g_nom + 0.12, 20)
    zoom(s, g_nom + 0.75, 960, 540, 1.0, 0.3, 0.45, "zoom-out")
    son(g_num, "coup-mystere", 0.55, f"carte mystère {n}")
    son(g_num + 0.05, "battements", 0.42, "cœur qui bat", sur_pic=False)
    son(g_nom - 0.02, "roulement-suspense", 0.42, "roulement avant la révélation")
    son(g_nom - 0.1, tour(["deverrouille", "deverrouille-2", "verrou"]), 0.45, "le cadenas saute")
    son(g_nom + 0.12, "revelation", 0.5, f"révélation : {nom}")
    son(g_nom + 0.12, "impact-basse", 0.55, "choc de la révélation")
    son(g_nom + 0.7, tour(["swoosh-court", "swoosh-accent", "fouet"]), 0.36, "la carte s'envole")


def titre_type(s, p, n, nom, g, taille=96):
    cam(s, f'<div id="{p}-n" class="al-num" style="left: 113px; top: 150px; font-size: 118px; opacity: 0">0{n}</div>')
    s.j(f'tl.fromTo("#{p}-n", {{ opacity: 0, scale: 1.8 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.out" }}, {s.L(g)});')
    titre(s, f"{p}-t", nom, g + 0.05, taille, 280, 168)


def _img(s, p, k, im, g, d):
    if im.startswith("v:"):
        return video_html(f"{p}-cv{k}", im[2:], round(d, 2), 7, "", s.L(g))
    return f'<img src="assets/img/{im}.jpg" alt="" />'


def site_type(s, p, g, d, marque, lignes, slogan, media, cartes, cta, couleur="#DCFC1C", defile=None, widgets=(), menu=True, extra=""):
    """Faux site 1920×1080 (comme site_metier) : cartes en photo OU en vraie vidéo (« v:nom »), menu facultatif,
    HTML en plus (panier, badges…), défilement et fenêtres qui apparaissent quand la voix les cite."""
    kind, f = media
    if kind == "v":
        m = video_html(f"{p}-hv", f, round(d, 2), 6, "", s.L(g))
    else:
        m = f'<img src="assets/img/{f}.jpg" alt="" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover" />'
    cs = "".join(f'<div id="{p}-c{k}" class="bz-carte"><div class="bz-carte-img">{_img(s, p, k, im, g, d)}</div><b>{t}</b><span>{u}</span></div>'
                 for k, (im, t, u) in enumerate(cartes))
    ws = "".join(f'<div id="{p}-w{k}" class="bz-widget" style="opacity: 0">{h}</div>' for k, (gw, h) in enumerate(widgets))
    nav = "<span>Accueil</span><span>Services</span><span>Avis</span><span>Contact</span>" if menu else ""
    html = (f'<div id="{p}" class="ds-section bz-page" style="--bz: {couleur}"><div id="{p}-defile" class="bz-defile">'
            f'<div class="bz-nav"><b>{marque}</b>{nav}<em>{cta}</em></div>'
            f'{lettres(p, lignes, "ds-h1 bz-h1")}<p class="bz-slogan">{slogan}</p><div class="bz-cta">{cta}</div>'
            f'<div class="bz-hero-media">{m}</div><div class="bz-cartes">{cs}</div></div>{extra}{ws}</div>')
    revele_lettres(s, p, g + 0.05, 0.6, 0.025)
    s.j(f'tl.fromTo("#{p} .bz-hero-media", {{ scale: 1.15, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.6, ease: "expo.out" }}, {s.L(g)});')
    for k in range(len(cartes)):
        s.j(f'tl.fromTo("#{p}-c{k}", {{ y: 160, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "expo.out" }}, {s.L(g + 0.35 + k * 0.1)});')
    if defile:
        s.j(f'tl.to("#{p}-defile", {{ y: -470, duration: 0.6, ease: "power3.inOut" }}, {s.L(defile)});')
        son(defile, tour(["balaie", "balaie-air", "pages-defilent"]), 0.4, "le site défile")
    for k, (gw, h) in enumerate(widgets):
        s.j(f'tl.fromTo("#{p}-w{k}", {{ opacity: 0, y: 80, scale: 0.85 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.8)" }}, {s.L(gw)});')
        if k > 0:
            s.j(f'tl.to("#{p}-w{k - 1}", {{ opacity: 0, y: -40, duration: 0.15 }}, {s.L(gw - 0.05)});')
        son(gw, tour(["pop-long", "notif-positive", "clic-positif", "pop-bulle"]), 0.42, "fenêtre du site")
    return html


def scene_type(k_sc, n, nom, i_num, i_nom, mots_fond, fichiers, fonctions, site_args, url, taille_titre=96, taille_carte=104, pts_en_plus=()):
    """Scène d'un type de site : rafale de vraies vidéos, carte mystère révélée sur le nom, titre, site, fonctions qui
    claquent ; la caméra SUIT : à chaque fonction elle va vers l'étiquette, puis vers la fenêtre du site qui s'ouvre."""
    s = scene(k_sc, f"Scène {k_sc + 1} · {n}. {nom}")
    pre = NOMS[k_sc][:3]
    fond(s, f"{pre}-f", mots_fond, fichiers, 0.55)
    g_num, g_nom = T(i_num), T(i_nom)
    # le personnage s'approche sur la pointe des pieds pendant le mystère, sursaute à la révélation
    cam(s, perso(f"{pre}-toi", 300, 860, 180))
    vit(s, f"{pre}-toi", s.debut, s.fin - 0.2)
    marche(s, f"{pre}-toi", g_num + 0.1, g_nom - 0.1, 260)
    pose(s, f"{pre}-toi", g_nom + 0.1, 0.12, "back.out(2)", bg=150, bd=-150, tete=-8)
    saut(s, f"{pre}-toi", g_nom + 0.1, 36)
    mystere(s, f"{pre}-m", n, g_num, g_nom, nom, taille_carte)
    g_t = g_nom + 0.82
    titre_type(s, pre, n, nom, g_t, taille_titre)
    p = f"{pre}-site"
    g_site = g_t + 0.12
    site_fenetre(s, f"{pre}-fen", site_type(s, p, g_site, s.fin - g_site + 0.2, **site_args), 840, 290, 960, url)
    s.j(f'tl.fromTo("#{pre}-fen", {{ opacity: 0, x: 700, rotationY: -28, transformPerspective: 1400 }}, {{ opacity: 1, x: 0, rotationY: 0, duration: 0.45, ease: "expo.out" }}, {s.L(g_site)});')
    son(g_site, tour(["balaie-rapide", "scintille-whoosh", "balaie-air"]), 0.45, "le site arrive")
    pose(s, f"{pre}-toi", g_site + 0.3, 0.16, "back.out(2)", bd=-100, tete=-8)
    for j, (t, i) in enumerate(fonctions):
        puce(s, f"{pre}-p{j}", t, 400, 360 + j * 88, T(i))
        son(T(i), tour(["pop-click", "pop-sec", "coche", "pop-bulle"]), 0.42, t)
        son(T(i), tour(["impact-futur", "impact-cartoon", "glitch-court"]), 0.3, "choc")
    victoire(s, f"{pre}-toi", T(fonctions[-1][1]) + 0.25, 1)
    # caméra qui suit : la fenêtre qui arrive, puis chaque fonction (étiquette à gauche → fenêtre du site à droite)
    pts = [(g_site + 0.12, 1500, 560), (g_site + 0.72, 1300, 560)]
    for j, (t, i) in enumerate(fonctions):
        ti = T(i)
        if ti - pts[-1][0] < 0.5:
            continue
        pts.append((ti - 0.05, 700, 360 + j * 88 + 120))
        pts.append((ti + 0.55, 1350, 560))
    # pts_en_plus : paires (début, fin) d'un moment à suivre ailleurs ; les autres points de la caméra s'effacent pendant ce moment
    for a_, b_ in zip(pts_en_plus[::2], pts_en_plus[1::2]):
        pts = [q for q in pts if not a_[0] - 0.3 <= q[0] <= b_[0] + 0.3]
    pts = sorted(pts + list(pts_en_plus))
    pts = [q for k, q in enumerate(pts) if k == 0 or q[0] - pts[k - 1][0] >= 0.3]
    fin_suivi = max(pts[-1][0] + 0.02, min(s.fin - 0.6, pts[-1][0] + 0.9))
    suit(s, pts, 1.3)
    zoom(s, fin_suivi, 960, 540, 1.0, 0.3, 0.42, "zoom-out")
    return s, pre, p


def compteur_html(cid, valeur):
    return f'<b id="{cid}">{valeur}</b>'


# ================================================================ SCÈNES
T = t_mot
# ---------------------------------------------------------------- S1 : hook — « un site web = un logo, des images, un bouton ? »
s = scene(0, "Scène 1 · « Tu penses qu'un site web, c'est forcément une page avec un logo, quelques images et un bouton pour contacter l'entreprise ? »")
HOOK = [(0.0, "v", "tape-laptop"), (T(1), "v", "web-design"), (T(3), "v", "homme-laptop"), (T(4), "v", "web-design"), (T(6), "v", "tel-scroll"),
        (T(7), "v", "macbook-pro"), (T(8), "v", "site-mode"), (T(9), "v", "souris-main"), (T(11), "v", "port-wireframe"), (T(12), "v", "photo-produit"),
        (T(13), "v", "port-photos-ecran"), (T(14), "v", "achat-laptop"), (T(16), "v", "ecom-defile-page"), (T(17), "v", "laptop-homme"),
        (T(18), "v", "entrepreneur-tel"), (T(19), "v", "reflechit-laptop")]
rafale_mots(s, "s01-r", HOOK, s.fin)
cam(s, '<div id="s01-voile" style="position: absolute; inset: 0; background: rgba(12, 12, 12, 0.42)"></div>')
slam_trace(s, "s01-eg", "Un site web =", 40, 120, 0.04)
son(0.04, "impact-whoosh", 0.5, "UN SITE WEB")
s.eclair(T(3))
son(T(3), "impact-futur", 0.4, "site web")
BASE = ('<div class="ty-base"><div id="s01-logo" class="ty-logo" style="opacity: 0"><i></i>LOGO</div>'
        '<div class="ty-menu"><span></span><span></span><span></span></div>'
        '<div class="ty-imgs">' + "".join(f'<div id="s01-im{k}" class="ty-im" style="opacity: 0"><img src="assets/img/{f}.jpg" alt="" /></div>'
                                          for k, f in enumerate(("paysage-mer", "st-boutique-vetements", "blog-bureau-lampe"))) + '</div>'
        '<div id="s01-btn" class="ty-btn" style="opacity: 0">Contactez-nous</div></div>')
navigateur(s, "s01-nav", 560, 190, 800, 540, "mon-entreprise.fr", BASE)
s.j(f'tl.fromTo("#s01-nav", {{ opacity: 0, scale: 0.5, rotation: -6 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "back.out(1.8)" }}, {s.L(T(7))});')
son(T(7), "pop-long", 0.45, "une page")
s.j(f'tl.fromTo("#s01-logo", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.in" }}, {s.L(T(11))});')
son(T(11), "impact-cartoon", 0.45, "logo")
for k in range(3):
    s.j(f'tl.fromTo("#s01-im{k}", {{ opacity: 0, y: 60, scale: 0.6 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {s.L(T(13) + k * 0.12)});')
    son(T(13) + k * 0.12, tour(POPS), 0.4, "image")
s.j(f'tl.fromTo("#s01-btn", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.6)" }}, {s.L(T(16))});')
son(T(16), "clic-positif", 0.45, "bouton")
for k, (txt, g, x, y) in enumerate((("Logo +", T(11), 880, 230), ("Images +", T(13), 1180, 330), ("Bouton ?", T(16), 1150, 650))):
    cam(s, f'<div id="s01-et{k}" class="ty-etiq" style="left: {x}px; top: {y}px; opacity: 0">{txt}</div>')
    s.j(f'tl.fromTo("#s01-et{k}", {{ opacity: 0, x: 200, skewX: -20 }}, {{ opacity: 1, x: 0, skewX: 0, duration: 0.2, ease: "power4.out" }}, {s.L(g + 0.05)});')
    son(g + 0.05, tour(["swoosh-court", "fouet", "swoosh-accent"]), 0.36, txt)
# souris qui clique sur le bouton
souris(s, "s01-souris", 1250, 880)
s.j(f'tl.fromTo("#s01-souris", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {s.L(T(17))});')
deplace(s, "s01-souris", T(17), 990, 650, 1250, 880, 0.35)
clic(s, "s01-souris", T(18) + 0.1, "#s01-btn")
# point d'interrogation géant
cam(s, '<div id="s01-q" class="ty-q" style="opacity: 0">?</div>')
s.j(f'tl.fromTo("#s01-q", {{ opacity: 0, scale: 3, rotation: 30 }}, {{ opacity: 1, scale: 1, rotation: -8, duration: 0.25, ease: "back.out(1.6)" }}, {s.L(T(19) + 0.2)});')
son(T(19) + 0.2, "coup-mystere", 0.5, "le grand ?")
cam(s, perso("s01-toi", 1730, 900, 230))
vit(s, "s01-toi", s.debut, s.fin - 0.2)
gratte(s, "s01-toi", T(5))
pose(s, "s01-toi", T(11) + 0.1, 0.16, "back.out(2)", bg=110, tete=8)
pose(s, "s01-toi", T(16) + 0.1, 0.16, "back.out(2)", bg=80, tete=4)
haussement(s, "s01-toi", T(19) + 0.2)
# la caméra suit : le logo, les images, le bouton, puis recule sur le « ? »
suit(s, [(T(11) - 0.05, 700, 320), (T(13) - 0.05, 960, 470), (T(16) - 0.05, 960, 640), (T(18), 980, 650)], 1.55, 0.25)
zoom(s, T(19), 960, 540, 1.0, 0.28, 0.45, "zoom-out")
s.ecrire()

# ---------------------------------------------------------------- S2 : pas du tout ! 6 types… cachés
s = scene(1, "Scène 2 · « Pas du tout ! Il existe plusieurs types de sites web, et chacun répond à un besoin précis. »")
fond(s, "s02-f", (20, 23, 25, 26, 28, 30, 31, 32, 35), ("myst-fumee", "myst-rideaux", "myst-oeil-laptop", "myst-porte-cadenas", "myst-danseur-noir",
     "myst-sablier", "myst-point-interro", "myst-fumee-blanche", "trou-de-ver"), 0.5, True)
navigateur(s, "s02-nav", 560, 190, 800, 540, "mon-entreprise.fr", BASE.replace('id="s01-', 'id="s02-').replace('style="opacity: 0"', ""), opacite=1)
s.j(f'tl.to("#s02-nav", {{ keyframes: [{{ x: -14, duration: 0.03 }}, {{ x: 14, duration: 0.03 }}, {{ x: -8, duration: 0.03 }}, {{ x: 0, duration: 0.03 }}] }}, {s.L(T(20) - 0.05)});')
s.j(f'tl.to("#s02-nav", {{ scale: 1.6, rotation: 14, opacity: 0, filter: "blur(18px)", duration: 0.28, ease: "power3.in" }}, {s.L(T(20) + 0.1)});')
choc_mot(s, "s02-pdt", "Pas du tout !", 330, 260, T(20), T(23) - 0.1)
s.eclair(T(20))
secousse(s, T(20), 26)
son(T(20), "impact-basse", 0.65, "PAS DU TOUT")
son(T(20), "glitch-rugit", 0.45, "PAS DU TOUT")
son(T(20) + 0.1, "verre-casse" if "verre-casse" in PICS else "glitch-data", 0.4, "la page vole en éclats")
# 6 cartes face cachée : on ne sait pas encore lesquelles
for k in range(6):
    x = 105 + k * 290
    cam(s, f'<div id="s02-c{k}" class="my-mini" style="left: {x}px; top: 250px; opacity: 0"><span>Type n°{k + 1}</span><b>?</b>'
           + CADENAS.format(id=f"s02-c{k}-cad", x=95, y=300, w=70, h=88).replace("opacity: 0", "opacity: 1") + '</div>')
    g = T(25) + k * 0.2
    s.j(f'tl.fromTo("#s02-c{k}", {{ opacity: 0, y: -600, rotation: {(-12, 9, -6, 11, -8, 7)[k]} }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.3, ease: "back.out(1.6)" }}, {s.L(g)});')
    son(g, tour(["impact-tambour", "coup-mystere", "impact-futur"]), 0.4, f"carte cachée {k + 1}")
son(T(25), "battement-mystere", 0.45, "mystère", sur_pic=False)
slam_trace(s, "s02-types", "Plusieurs types", 90, 120, T(25))
s.j(f'tl.to(".my-mini", {{ keyframes: [{{ rotation: -4, duration: 0.07 }}, {{ rotation: 4, duration: 0.07 }}, {{ rotation: -2, duration: 0.07 }}, {{ rotation: 0, duration: 0.07 }}], stagger: 0.07 }}, {s.L(T(31))});')
son(T(31), "tic-tac", 0.4, "chacun son besoin")
tampon(s, "s02-besoin", "1 besoin = 1 type", 1130, 735, T(33), -5, 70)
son(T(33), "impact-basse", 0.5, "besoin précis")
son(T(36), "notif-indice", 0.4, "précis")
cam(s, perso("s02-toi", 120, 900, 170))
vit(s, "s02-toi", s.debut, s.fin - 0.2)
non(s, "s02-toi", T(20) + 0.05)
pose(s, "s02-toi", T(25) + 0.1, 0.16, "back.out(2)", bg=150, bd=-150, tete=-6)
saut(s, "s02-toi", T(25) + 0.1, 30)
gratte(s, "s02-toi", T(32))
# la caméra suit l'arrivée des cartes de gauche à droite, puis recule pour les montrer toutes
suit(s, [(T(25) - 0.05, 300, 420), (T(25) + 1.1, 1620, 420)], 1.45, 0.25)
zoom(s, T(25) + 1.25, 960, 520, 1.0, 0.3, 0.45, "zoom-out")
zoom(s, T(35), 960, 560, 1.06)
s.ecrire()

# ---------------------------------------------------------------- S3 à S8 : les 6 types, révélés un par un
W1 = [(T(52), '<div class="bz-w-tete">Nos services</div><div class="bz-tarifs"><p>Conseil déco <b>sur RDV</b></p><p>Aménagement <b>sur devis</b></p><p>Ateliers <b>chaque samedi</b></p></div>'),
      (T(54), '<div class="bz-w-tete">Tarifs</div><div class="bz-tarifs"><p>Conseil 1 h <b>45 €</b></p><p>Atelier <b>25 €</b></p><p>Projet complet <b>dès 490 €</b></p></div>'),
      (T(56), '<div class="bz-w-tete">Nos réalisations</div><div class="ty-galerie"><img src="assets/img/st-caisse-boutique.jpg" alt="" /><img src="assets/img/design-livres.jpg" alt="" />'
              '<img src="assets/img/blog-bureau-lampe.jpg" alt="" /><img src="assets/img/st-epicerie-sourire.jpg" alt="" /></div>'),
      (T(63), w_form("Nous contacter", [("Nom", "Julie R."), ("E-mail", "julie@mail.fr"), ("Message", "Un devis ?")], "Envoyer"))]
s, pre, p = scene_type(2, 1, "Site vitrine", 37, 40, (37, 41, 43, 46, 48, 50, 52, 54, 56, 58, 60, 63),
                       ("myst-fumee", "boutique-vetements", "vit-poignee", "caisse-boutique", "epicerie-sourire", "vit-reunion", "salon-brushing",
                        "resto-chefs", "creatifs-internet", "plombier-chantier", "entrepreneure", "poignee-mains"),
                       [("Services", 52), ("Tarifs", 54), ("Réalisations", 56), ("Contact", 63)],
                       dict(marque="ATELIER ÉLISE", lignes=("Créations", "uniques."), slogan="Boutique déco à Lyon, du mardi au samedi.", media=("v", "boutique-vetements"),
                            cartes=[("st-boutique-vetements", "Conseil déco", "sur rendez-vous"), ("st-caisse-boutique", "Ateliers", "dès 25 €"), ("st-epicerie-sourire", "Réalisations", "+120 projets")],
                            cta="Nous contacter", defile=T(56), widgets=W1), "atelier-elise.fr",
                       pts_en_plus=[(T(43) - 0.1, 640, 560), (T(46) + 0.3, 1300, 560)])
# la carte de visite qui devient numérique
cam(s, '<div id="s03-cv" class="ty-cv" style="opacity: 0"><b>ATELIER ÉLISE</b><span>Boutique déco · Lyon</span><span>06 12 34 56 78</span><em>atelier-elise.fr</em></div>')
s.j(f'tl.fromTo("#s03-cv", {{ opacity: 0, rotationY: -90, transformPerspective: 1200 }}, {{ opacity: 1, rotationY: 0, duration: 0.3, ease: "back.out(1.6)" }}, {s.L(T(43))});')
son(T(43), "papier-glisse", 0.45, "carte de visite")
s.j(f'tl.to("#s03-cv", {{ keyframes: [{{ x: 10, skewX: 8, filter: "hue-rotate(90deg)", duration: 0.05 }}, {{ x: -10, skewX: -8, filter: "hue-rotate(0deg)", duration: 0.05 }}, {{ x: 0, skewX: 0, duration: 0.05 }}] }}, {s.L(T(46))});')
s.j(f'tl.to("#s03-cv", {{ x: 900, y: -60, scale: 0.15, opacity: 0, duration: 0.4, ease: "power3.in" }}, {s.L(T(46) + 0.35)});')
son(T(46), "glitch-data", 0.42, "numérique")
son(T(46) + 0.35, "aspiration", 0.36, "elle rentre dans le site")
s.ecrire()

PANIER = ('<div class="ty-panier"><svg viewBox="0 0 48 48" width="56" height="56"><path d="M6 8 H13 L18 32 H38 L42 16 H15" fill="none" stroke="#ECECE8" stroke-width="4" stroke-linejoin="round" />'
          '<circle cx="20" cy="40" r="3.5" fill="#ECECE8" /><circle cx="36" cy="40" r="3.5" fill="#ECECE8" /></svg>'
          '<i id="s04-site-nb0">0</i><i id="s04-site-nb1" style="opacity: 0">1</i><i id="s04-site-nb2" style="opacity: 0">2</i></div>'
          '<div id="s04-site-vol" class="ty-vol" style="opacity: 0"><img src="assets/img/basket-orange.jpg" alt="" /></div>'
          '<div id="s04-site-vol2" class="ty-vol" style="left: 860px; opacity: 0"><img src="assets/img/casque-blanc.jpg" alt="" /></div>')
W2 = [(T(84), w_form("Paiement sécurisé", [("Carte", "•••• 4242"), ("Expire", "08/28"), ("Total", "218 €")], "Payer 218 €")),
      (T(89), '<div class="bz-w-tete">Suivi de commande</div><div class="ty-etapes"><p class="ok">Commandée</p><p class="ok">Expédiée</p><p id="s04-livre">Livrée demain</p></div>'
              '<div class="bz-barre"><i id="s04-prog"></i></div>')]
s, pre, p = scene_type(3, 2, "Site e-commerce", 64, 67, (64, 68, 70, 73, 75, 77, 79, 81, 83, 84, 87, 89),
                       ("myst-sablier", "ecom-mode-site", "ecom-sacs-blanc", "ecom-paie-caisse", "ecom-couple-laptop", "ecom-article-tel", "ecom-femme-achete",
                        "ecom-defile-page", "ecom-carte-ordi", "ecom-tel-carte", "ecom-colis-scotch", "ecom-livraison-femme"),
                       [("Produits", 79), ("Panier", 83), ("Paiement en ligne", 84), ("Suivi des commandes", 89)],
                       dict(marque="URBAN SHOP", lignes=("Le style", "en un clic."), slogan="Livraison offerte dès 50 €.", media=("v", "ecom-mode-site"),
                            cartes=[("basket-orange", "Basket Volt", "89 €"), ("casque-blanc", "Casque Air", "129 €"), ("montre-cuir", "Montre Classic", "159 €")],
                            cta="Voir la boutique", couleur="#FF9F1C", defile=T(77), widgets=W2, extra=PANIER, menu=False), "urban-shop.fr", 92, 88)
tampon(s, "s04-vente", "On vend !", 150, 690, T(73), -6, 70)
son(T(73), "scanner-caisse", 0.45, "la vente")
for k in range(4):
    son(T(73) + 0.1 + k * 0.1, tour(["pieces", "pieces-2", "piece-gagne"]), 0.34, "pièces")
for k, (sel, g) in enumerate((("vol", T(81) + 0.05), ("vol2", T(83) - 0.1))):
    s.j(f'tl.fromTo("#s04-site-{sel}", {{ opacity: 1, x: 0, y: 0, scale: 1 }}, {{ opacity: 0.2, x: {(1077, 500)[k]}, y: -350, scale: 0.15, duration: 0.45, ease: "power2.in", immediateRender: false }}, {s.L(g)});')
    s.j(f'tl.set("#s04-site-{sel}", {{ opacity: 0 }}, {s.L(g + 0.46)});')
    s.j(f'tl.set("#s04-site-nb{k}", {{ opacity: 0 }}, {s.L(g + 0.45)});')
    s.j(f'tl.fromTo("#s04-site-nb{k + 1}", {{ opacity: 1, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }}, {s.L(g + 0.45)});')
    son(g, "swoosh-monte", 0.36, "au panier")
    son(g + 0.45, "pop-cartoon", 0.42, "panier +1")
s.j(f'tl.fromTo("#s04-prog", {{ scaleX: 0 }}, {{ scaleX: 0.8, duration: 0.9, ease: "power2.out", immediateRender: false }}, {s.L(T(90))});')
son(T(85), "clic-positif", 0.42, "payer")
son(T(86), "mission-ok", 0.42, "paiement accepté")
son(T(90), "vent-roulement", 0.34, "le colis roule")
s.ecrire()

W3 = [(T(110), '<div class="bz-w-tete">Meilleurs projets</div><div class="ty-galerie"><img src="assets/img/paysage-coucher.jpg" alt="" /><img src="assets/img/design-abstrait.jpg" alt="" />'
               '<img src="assets/img/paysage-montagnes.jpg" alt="" /><img src="assets/img/design-livres.jpg" alt="" /></div>'),
      (T(113), '<div class="bz-w-tete">Nouveau message</div><div class="ty-msg"><b>Studio Kora</b><p>« On adore ton travail ! Tu es dispo pour un projet ? »</p></div><div class="bz-w-btn">Répondre</div>')]
s, pre, p = scene_type(4, 3, "Portfolio", 92, 94, (92, 95, 97, 100, 101, 102, 103, 105, 108, 110, 113),
                       ("myst-danseur-noir", "port-photographe", "port-peintre", "port-pinceau", "port-graphiste-couleurs", "port-objectif", "port-programmeur",
                        "port-poterie", "port-photos-ecran", "port-design-tablette", "vit-poignee"),
                       [("Graphistes", 101), ("Photographes", 102), ("Développeurs", 103), ("Créateurs", 105)],
                       dict(marque="LÉA MOREAU", lignes=("Photographe", "& designer."), slogan="Portraits, paysages et identités visuelles.", media=("v", "port-photographe"),
                            cartes=[("paysage-lac", "Série « Lacs »", "Photographie"), ("design-affiches", "Affiches", "Design graphique"), ("paysage-mer", "Bord de mer", "Photographie")],
                            cta="Me contacter", couleur="#B794FF", defile=T(108), widgets=W3), "lea-moreau.fr")
tampon(s, "s05-talent", "Ton talent", 150, 690, T(100), -5, 74)
son(T(100), "trophee-magique", 0.42, "ton talent")
son(T(102), "obturateur", 0.42, "photographes")
son(T(103), "clavier-ordi", 0.36, "développeurs", d=0.6)
son(T(113), "notif-magique", 0.45, "un client écrit")
s.ecrire()

W4 = [(T(141), '<div class="bz-w-tete">Ton audience</div><div class="ty-gros"><b id="s06-aud">0</b><span>abonnés à la newsletter</span></div>'),
      (T(145), '<div class="bz-w-tete">Trafic du site</div><div class="ty-graphe">' + "".join(f'<i id="s06-g{k}" style="height: {h}%"></i>' for k, h in enumerate((18, 26, 34, 47, 62, 80, 100)))
               + '</div><div class="ty-hausse">+240 % de visites</div>')]
s, pre, p = scene_type(5, 4, "Blog / média", 116, 118, (116, 119, 122, 126, 129, 130, 131, 133, 136, 139, 141, 143, 145),
                       ("myst-oeil-laptop", "blog-ecrit-crayon", "blog-podcast", "blog-journaliste", "blog-journal-pov", "blog-reporter", "blog-tablette",
                        "blog-lit-actus", "blog-micro", "blog-vlog-rue", "land-foule", "blog-influenceuse", "plat-ecrans"),
                       [("Articles", 129), ("Actualités", 130), ("Conseils", 131), ("Analyses", 133)],
                       dict(marque="LE MAG DIGITAL", lignes=("Comprendre", "le web."), slogan="Articles, actus et conseils chaque semaine.", media=("v", "blog-podcast"),
                            cartes=[("blog-macbook-bois", "Créer son site avec l’IA", "Article · 6 min"), ("blog-imac", "Les actus du web", "Actualité"), ("blog-carnet", "5 conseils pour débuter", "Conseil")],
                            cta="S’abonner", couleur="#4DD8FF", defile=T(129), widgets=W4), "le-mag-digital.fr", 96, 96)
s.compteur("#s06-aud", T(141) + 0.2, 0, 12480, 1.2)
son(T(141) + 0.2, "compteur", 0.4, "l'audience grimpe", d=1.2)
for k in range(7):
    s.j(f'tl.fromTo("#s06-g{k}", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.3, ease: "back.out(1.6)", immediateRender: false }}, {s.L(T(145) + 0.15 + k * 0.06)});')
son(T(145) + 0.15, "swoosh-monte", 0.42, "le trafic monte")
son(T(126), "stylo", 0.4, "publier")
s.ecrire()

W5 = [(T(164), '<div class="bz-w-tete">Offre de lancement</div><div class="ty-gros"><b>9,99 €</b><span><s>19,99 €</s> · aujourd’hui seulement</span></div><div class="bz-w-btn">Acheter</div>'),
      (T(167), w_form("Rejoins la liste", [("Prénom", "Sarah"), ("E-mail", "sarah@mail.fr")], "Je m’inscris")),
      (T(172), '<div class="bz-w-tete">Télécharge l’app</div><div class="ty-stores"><span>App Store</span><span>Google Play</span></div><div class="ty-gros"><b>4,8 ★</b><span>50 000 téléchargements</span></div>')]
s, pre, p = scene_type(6, 5, "Landing page", 146, 148, (146, 150, 153, 155, 157, 159, 161, 164, 166, 167, 169, 172),
                       ("myst-rideaux", "land-scroll-app", "land-foule", "ecom-tel-carte", "land-app-bar", "land-sms-content", "land-notifs", "ecom-carte-tel",
                        "achat-laptop", "land-montre", "tel-tape", "land-scroll-app"),
                       [("Vendre un produit", 164), ("Récupérer des contacts", 167), ("Télécharger une app", 172)],
                       dict(marque="FITPULSE", lignes=("Ton coach", "dans ta poche."), slogan="L’app qui crée ton programme en 30 secondes.", media=("i", "app-tel-main"),
                            cartes=[("app-ecran-couleurs", "Programmes", "personnalisés"), ("app-dashboard", "Suivi", "en temps réel"), ("st-port-design-tablette", "Coach IA", "24 h / 24")],
                            cta="Télécharger l’app", couleur="#3DFFA2", widgets=W5, menu=False), "fitpulse.app",
                       pts_en_plus=[(T(155) - 0.1, 620, 600), (T(160), 1300, 560)])
# l'entonnoir : 1 000 visiteurs → 87 clients
cam(s, '<div id="s07-ent" class="ty-entonnoir" style="opacity: 0"><div class="ty-ent-h"><b id="s07-vis">0</b><span>visiteurs</span></div>'
       '<svg viewBox="0 0 400 260" width="400" height="260"><path d="M10 10 H390 L240 150 V250 H160 V150 Z" fill="rgba(61, 255, 162, 0.16)" stroke="#3DFFA2" stroke-width="6" stroke-linejoin="round" /></svg>'
       + "".join(f'<i id="s07-pt{k}" class="ty-pt" style="left: {40 + (k * 53) % 320}px"></i>' for k in range(12)) +
       '<div class="ty-ent-b"><b id="s07-cli">0</b><span>clients</span></div></div>')
s.j(f'tl.fromTo("#s07-ent", {{ opacity: 0, x: -300 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "expo.out" }}, {s.L(T(155))});')
son(T(155), "swoosh-vitesse", 0.4, "convertir")
s.compteur("#s07-vis", T(155) + 0.1, 0, 1000, 0.8)
for k in range(12):
    g = T(156) + k * 0.12
    s.j(f'tl.fromTo("#s07-pt{k}", {{ opacity: 1, y: 0, x: 0 }}, {{ opacity: {1 if k % 4 == 0 else 0}, y: 230, x: {200 - (40 + (k * 53) % 320)}, duration: 0.5, ease: "power2.in", immediateRender: false }}, {s.L(g)});')
s.compteur("#s07-cli", T(158), 0, 87, 0.9)
son(T(158), "compteur", 0.36, "les clients", d=0.9)
son(T(159), "piece-gagne", 0.45, "clients !")
s.j(f'tl.to("#s07-ent", {{ opacity: 0, x: -300, duration: 0.2 }}, {s.L(T(163) - 0.05)});')
cam(s, '<div id="s07-cible" class="ty-cible" style="opacity: 0"><i></i><i></i><i></i></div>')
s.j(f'tl.fromTo("#s07-cible", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.in" }}, {s.L(T(163))});')
s.j(f'tl.to("#s07-cible", {{ opacity: 0, duration: 0.15 }}, {s.L(T(164) - 0.1)});')
son(T(163), "impact-futur", 0.45, "précis : dans le mille")
son(T(172) + 0.3, "jeu-deblocage", 0.42, "téléchargé")
s.ecrire()

W6 = [(T(199), w_form("Créer un compte", [("Pseudo", "karim_dev"), ("E-mail", "karim@mail.fr"), ("Mot de passe", "••••••••")], "C’est parti")),
      (T(202), '<div class="bz-w-tete">Karim a publié</div><div class="ty-post"><img src="assets/img/paysage-cascade.jpg" alt="" /><p><b id="s08-like">♥ 1,2 k</b><span>348 commentaires</span></p></div>'),
      (T(203), '<div class="bz-w-tete">Messages</div><div class="ty-chat"><p class="l">Tu as fini le module 3 ?</p><p class="r">Oui ! On révise ensemble ?</p><p class="l">Go, ce soir 20 h</p></div>'),
      (T(215), '<div class="bz-w-tete">Formation : créer un site</div><div class="ty-gros"><b>Module 4 / 6</b><span>Ta progression</span></div><div class="bz-barre"><i id="s08-prog"></i></div>')]
s, pre, p = scene_type(7, 6, "Plateforme web", 175, 177, (175, 179, 182, 185, 188, 193, 196, 199, 202, 203, 205, 207, 210, 211, 215),
                       ("myst-porte-cadenas", "interface-vr", "hologramme-social", "mains-digital", "plat-ecrans", "blog-lit-journal", "plat-groupe",
                        "plat-lit-laptop", "plat-jeu-amis", "plat-visio", "plat-salut-visio", "plat-amis-rue", "plat-telecommande", "plat-hotel-pano", "plat-cours-ligne"),
                       [("Créer un compte", 199), ("Interagir", 202), ("Échanger", 203), ("Fonctionnalités", 207)],
                       dict(marque="HUBLO", lignes=("Apprends,", "partage, échange."), slogan="Crée ton compte et rejoins 2 millions de membres.", media=("v", "plat-groupe"),
                            cartes=[("v:plat-cours-ligne", "Formations", "1 200 cours"), ("v:plat-film-lit", "Films & séries", "en streaming"), ("v:plat-hotel-pano", "Logements", "partout dans le monde")],
                            cta="Créer un compte", couleur="#FF5FA2", defile=T(196), widgets=W6), "hublo.app", 92, 92,
                       pts_en_plus=[(T(184) - 0.1, 620, 560), (T(188), 1300, 560), (T(210) - 0.15, 960, 480), (T(213) + 0.1, 1300, 560)])
# « un autre niveau »
cam(s, '<div id="s08-niv" class="ty-niveau" style="opacity: 0"><span>Niveau</span><b>MAX</b></div>')
s.j(f'tl.fromTo("#s08-niv", {{ opacity: 0, y: 200, scale: 0.4 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {s.L(T(184))});')
s.j(f'tl.to("#s08-niv", {{ opacity: 0, y: -120, duration: 0.2 }}, {s.L(T(188))});')
son(T(184), "power-up", 0.5, "un autre niveau")
son(T(184), "impact-basse", 0.45, "un autre niveau")
puce_rayee(s, "s08-info", "Consulter des infos", 400, 380, T(190), T(193) + 0.2)
s.j(f'tl.to("#s08-info", {{ opacity: 0, duration: 0.15 }}, {s.L(T(198) - 0.1)});')
son(T(202) + 0.3, "pop-bulle", 0.4, "j'aime")
for k in range(3):
    son(T(203) + 0.1 + k * 0.22, tour(["pop-bulle", "pop-sec", "notif-positive"]), 0.38, "message")
# Netflix, Airbnb : les vrais exemples
for k, (cle, ti) in enumerate((("netflix", T(210)), ("airbnb", T(211)))):
    cam(s, carte_logo(f"s08-l{k}", cle, 560 + k * 430, 250, 380))
    s.j(f'tl.fromTo("#s08-l{k}", {{ opacity: 0, scale: 2.2, rotation: {(-10, 8)[k]} }}, {{ opacity: 1, scale: 1, rotation: {(-4, 3)[k]}, duration: 0.2, ease: "power4.in" }}, {s.L(ti)});')
    s.j(f'tl.to("#s08-l{k}", {{ opacity: 0, scale: 0.6, y: -80, duration: 0.2 }}, {s.L(T(214) - 0.05)});')
    son(ti, "impact-basse", 0.5, cle)
    son(ti, tour(["glitch-cine", "glitch-scifi"]), 0.36, cle)
s.eclair(T(210))
s.j(f'tl.fromTo("#s08-prog", {{ scaleX: 0 }}, {{ scaleX: 0.66, duration: 0.8, ease: "power2.out", immediateRender: false }}, {s.L(T(216))});')
son(T(216), "mission-ok", 0.4, "formation")
s.ecrire()

# ---------------------------------------------------------------- S9 : la vraie question
s = scene(8, "Scène 9 · « Et voilà pourquoi tous les sites web ne se construisent pas de la même manière. La vraie question… »")
fond(s, "s09-f", (218, 221, 223, 227, 230, 233, 236, 240, 244, 247, 249, 251, 253),
     ("ecom-mode-site", "port-photographe", "blog-podcast", "land-scroll-app", "plat-groupe", "myst-fumee", "myst-oeil-laptop", "reflechit-laptop",
      "homme-laptop", "myst-point-interro", "myst-sablier", "entrepreneure", "myst-fumee-blanche"), 0.55, True)
SIX = [("Vitrine", "atelier-elise.fr", "boutique-vetements"), ("E-commerce", "urban-shop.fr", "ecom-mode-site"), ("Portfolio", "lea-moreau.fr", "port-photographe"),
       ("Blog", "le-mag-digital.fr", "blog-podcast"), ("Landing", "fitpulse.app", "land-scroll-app"), ("Plateforme", "hublo.app", "plat-groupe")]
TAILLES = [(90, 150, 520, 300), (680, 120, 560, 330), (1300, 160, 520, 290), (120, 520, 480, 300), (690, 520, 560, 300), (1310, 500, 520, 330)]
for k, ((lab, u, v), (x, y, w, h)) in enumerate(zip(SIX, TAILLES)):
    navigateur(s, f"s09-m{k}", x, y, w, h, u, f'<div class="al-nav-video">{video_html(f"s09-m{k}-v", v, round(T(233) - T(218) + 0.3, 2), 6 + k % 2, "", s.L(T(218)))}</div>'
               f'<div class="ty-lab">{lab}</div>')
    g = T(220) + k * 0.16
    s.j(f'tl.fromTo("#s09-m{k}", {{ opacity: 0, scale: 0.4, rotation: {(-7, 5, -4, 6, -5, 4)[k]} }}, {{ opacity: 1, scale: 1, rotation: {(-2, 1, -1, 2, -1, 1)[k]}, duration: 0.26, ease: "back.out(2)" }}, {s.L(g)});')
    son(g, tour(["pop-click", "pop-sec", "jeu-deblocage", "pop-bulle"]), 0.4, f"site {lab}")
s.j(f'tl.to([{", ".join(f"{chr(34)}#s09-m{k}{chr(34)}" for k in range(6))}], {{ opacity: 0, scale: 0.6, duration: 0.2, stagger: 0.03 }}, {s.L(T(233) - 0.2)});')
# la vraie question
cam(s, f'<div id="s09-nuit" class="my-nuit" style="opacity: 0"></div>')
s.j(f'tl.fromTo("#s09-nuit", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {s.L(T(233))});')
choc_mot(s, "s09-vq", "La vraie question", 150, 150, T(234), T(240) - 0.1)
son(T(233), "battement-mystere", 0.5, "la vraie question", sur_pic=False)
son(T(234), "coup-mystere", 0.5, "LA VRAIE QUESTION")
invite(s, "s09-q1", "Comment créer un site web avec l’IA ?", 360, 380, 1200, T(240), T(246) + 0.3, "logo-claude.svg", "Ta question")
cam(s, '<i id="s09-rat" style="position: absolute; left: 400px; top: 500px; width: 1120px; height: 18px; background: #DCFC1C; transform-origin: 0% 50%; transform: scaleX(0)"></i>')
s.rature("#s09-rat", T(247))
son(T(247), "buzz-faux", 0.45, "pas seulement")
s.j(f'tl.to("#s09-q1", {{ opacity: 0, scale: 0.8, y: -160, duration: 0.3 }}, {s.L(T(248))});')
s.j(f'tl.to("#s09-rat", {{ opacity: 0, duration: 0.2 }}, {s.L(T(248))});')
cam(s, '<div id="s09-q2" class="ty-grande-q" style="opacity: 0"><span id="s09-q2a">Quel problème</span><span id="s09-q2b">mon site va-t-il</span><span id="s09-q2c">résoudre ?</span></div>')
s.j(f'tl.set("#s09-q2", {{ opacity: 1 }}, {s.L(T(249))});')
for k, (sel, g) in enumerate((("a", T(249)), ("b", T(251)), ("c", T(254)))):
    s.j(f'tl.fromTo("#s09-q2{sel}", {{ opacity: 0, scale: 1.8, skewX: -14 }}, {{ opacity: 1, scale: 1, skewX: 0, duration: 0.16, ease: "power4.out" }}, {s.L(g)});')
    son(g, ("impact-basse", "impact-futur", "impact-whoosh")[k], 0.55, "QUEL PROBLÈME")
secousse(s, T(249), 20)
s.eclair(T(254))
son(T(250), "riser-trailer", 0.38, "monte vers « résoudre »", sur_pic=False)
cam(s, perso("s09-toi", 1720, 900, 220))
vit(s, "s09-toi", s.debut, s.fin - 0.2)
pose(s, "s09-toi", T(220), 0.16, "back.out(2)", bg=150, bd=-150, tete=-6)
gratte(s, "s09-toi", T(236))
non(s, "s09-toi", T(247))
pose(s, "s09-toi", T(254), 0.14, "back.out(2)", bd=-120, tete=-10)
saut(s, "s09-toi", T(254), 30)
# la caméra glisse sur la mosaïque de sites, puis s'approche de la question
suit(s, [(T(221), 380, 300), (T(224), 1560, 300), (T(227), 1560, 680), (T(230), 380, 680)], 1.5, 0.25)
zoom(s, T(231), 960, 540, 1.0, 0.3, 0.42, "zoom-out")
s.j(f'tl.to("#{s.id}-cadre", {{ x: 0, y: 0, scale: 1.12, duration: {round(T(254) - T(249), 3)}, ease: "power1.in" }}, {s.L(T(249))});')
s.ecrire()

# ---------------------------------------------------------------- S10 : abonne-toi
s = scene(9, "Scène 10 · « Abonne-toi à Gausscode. »")
fond(s, "s10-f", (255, 257), ("trou-de-ver", "creatifs-internet"), 0.5)
cam(s, f'<div id="s10-abo" class="al-abo" style="opacity: 0"><i class="al-abo-av">G</i><div class="al-abo-txt"><b>Gausscode</b><span>Crée avec l’IA</span></div>'
       f'<div id="s10-btn" class="al-abo-btn"><span id="s10-b1">S’abonner</span><span id="s10-b2" style="opacity: 0">Abonné</span></div>'
       f'<svg id="s10-cloche" viewBox="0 0 40 40" width="46" height="46"><path d="M20 4 C12 4 10 11 10 17 L10 25 L6 30 L34 30 L30 25 L30 17 C30 11 28 4 20 4 Z" fill="#ECECE8" />'
       f'<circle cx="20" cy="34" r="4" fill="#ECECE8" /></svg></div>')
s.j(f'tl.fromTo("#s10-abo", {{ opacity: 0, x: 900, skewX: -20 }}, {{ opacity: 1, x: 0, skewX: 0, duration: 0.35, ease: "expo.out" }}, {s.L(T(255))});')
son(T(255), "balaie-rapide", 0.45, "abonne-toi")
souris(s, "s10-souris", 1500, 1000)
s.j(f'tl.fromTo("#s10-souris", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {s.L(T(255) + 0.1)});')
deplace(s, "s10-souris", T(255) + 0.1, 1240, 760, 1500, 1000, 0.3)
clic(s, "s10-souris", T(258), "#s10-btn")
s.j(f'tl.to("#s10-btn", {{ backgroundColor: "#3a3a3a", color: "#ECECE8", duration: 0.1 }}, {s.L(T(258))});')
s.j(f'tl.set("#s10-b1", {{ opacity: 0 }}, {s.L(T(258))});')
s.j(f'tl.set("#s10-b2", {{ opacity: 1 }}, {s.L(T(258))});')
s.j(f'tl.fromTo("#s10-cloche", {{ rotation: 0 }}, {{ keyframes: [{{ rotation: -22, duration: 0.07 }}, {{ rotation: 22, duration: 0.07 }}, {{ rotation: -14, duration: 0.07 }}, {{ rotation: 10, duration: 0.07 }}, {{ rotation: 0, duration: 0.07 }}], transformOrigin: "50% 10%", immediateRender: false }}, {s.L(T(258) + 0.3)});')
son(T(258) + 0.3, "cloche-succes", 0.42, "cloche")
confettis(s, "s10-conf", T(258) + 0.1, 1240, 760, 26, 420)
cam(s, perso("s10-toi", 1780, 940, 240))
vit(s, "s10-toi", s.debut, s.fin - 0.2)
victoire(s, "s10-toi", T(258) + 0.1, 2)
zoom(s, T(255) + 0.4, 1100, 620, 1.12)
s.ecrire()

# ================================================================ SONS GÉNÉRAUX
for k, c in enumerate(COUPES[1:-1], start=1):
    son(c, tour(TRANSITIONS + ["balaie-rapide", "balaie-air"]), 0.44, f"volet vers {NOMS[k]}")
son(0.02, "impact-whoosh", 0.6, "ouverture")
son(0.03, "intro-mystere", 0.4, "ouverture mystérieuse", sur_pic=False)

MUSIQUES = [  # (début, fichier, durée, volume) — 0,63 ≈ −21 LUFS (5–6 dB sous la voix, réglage validé)
    (0, "partie-1-arab-nights", 33.4, 0.63),           # intro mystérieuse sous la question, le drop tombe sur « Pas du tout ! »
    (32.58, "partie-2-g-eazy-nba-type", 34.2, 0.63),   # le drop tombe sur « portfolio »
    (66.38, "partie-3-head-bang", round(FIN - 66.38, 2), 0.63),  # le drop tombe sur « plateforme »
]
MASQUES = []
_vus = set()
SONS[:] = [x for x in SONS if not ((x[0], x[1]) in _vus or _vus.add((x[0], x[1])))]

CHECK = [(lab, T(i), COUPES[k + 3]) for k, (lab, i) in enumerate((("Vitrine", 40), ("E-commerce", 67), ("Portfolio", 94), ("Blog", 118), ("Landing", 148), ("Plateforme", 177)))]
CHECK_TITRE = "6 types de sites"
CHECK_DEBUT = t_mot(25)
# ================================================================ MONTAGE (index.html) ET CADRE
CSS = """      /* ---- styles générés : début (tools/construire-scenes.py) ---- */
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
      .pj-etape {
        position: absolute;
        display: flex;
        align-items: baseline;
        gap: 14px;
        background: var(--color-accent);
        color: #000;
        font-family: "Anton", sans-serif;
        padding: 8px 26px 12px;
        text-transform: uppercase;
        white-space: nowrap;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      }
      .pj-etape span {
        font-size: 56px;
      }
      .pj-etape b {
        font-size: 100px;
        font-weight: 400;
        line-height: 0.9;
      }
      .pj-etape i {
        font-style: normal;
        font-size: 46px;
        opacity: 0.6;
      }
      .pj-fenetre {
        position: absolute;
        display: flex;
        flex-direction: column;
        background: #151515;
        border: 2px solid #3a3a3a;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 40px 100px rgba(0, 0, 0, 0.75);
      }
      .pj-fen-barre {
        flex: none;
        height: 58px;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0 20px;
        background: #1f1f1f;
        border-bottom: 2px solid #2c2c2c;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        color: #a3a3a3;
        white-space: nowrap;
      }
      .pj-fen-barre i {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #3a3a3a;
      }
      .pj-fen-barre img {
        height: 30px;
        margin-left: 14px;
      }
      .pj-fen-corps {
        flex: 1;
        position: relative;
        display: flex;
      }
      .pj-fen-vide {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 34px;
        color: var(--color-light);
      }
      .pj-fen-vide b {
        width: 110px;
        height: 110px;
        border-radius: 22px;
        background: #ea4b71;
        color: #fff;
        font-size: 90px;
        line-height: 100px;
        text-align: center;
      }
      .pj-fen-cote {
        flex: none;
        width: 300px;
        padding: 24px 16px;
        background: #1b1b1b;
        border-right: 2px solid #2c2c2c;
      }
      .pj-fen-nav {
        height: 66px;
        margin-bottom: 8px;
        padding: 0 18px;
        border-radius: 12px;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 30px;
        line-height: 66px;
        color: var(--color-light);
        white-space: nowrap;
      }
      .pj-fen-main {
        flex: 1;
        position: relative;
      }
      .pj-fen-h {
        position: absolute;
        left: 40px;
        top: 30px;
        font-family: "Anton", sans-serif;
        font-size: 60px;
        color: var(--color-light);
        text-transform: uppercase;
      }
      .pj-fen-vide2 {
        position: absolute;
        left: 0;
        right: 0;
        top: 200px;
        text-align: center;
        font-family: "Inter", sans-serif;
        font-weight: 500;
        font-size: 32px;
        color: #a3a3a3;
      }
      .pj-fen-bouton {
        position: absolute;
        left: 328px;
        top: 300px;
        width: 340px;
        height: 76px;
        border-radius: 14px;
        background: #ea4b71;
        color: #fff;
        font-family: "Inter", sans-serif;
        font-weight: 700;
        font-size: 32px;
        line-height: 76px;
        text-align: center;
        white-space: nowrap;
      }
      .pj-fen-carte {
        position: absolute;
        left: 40px;
        top: 120px;
        width: 560px;
        padding: 26px 30px;
        border: 4px solid var(--color-accent);
        border-radius: 16px;
        background: #23260f;
        font-family: "Inter", sans-serif;
        color: var(--color-light);
      }
      .pj-fen-carte b {
        display: block;
        font-size: 40px;
      }
      .pj-fen-carte span {
        display: block;
        margin-top: 6px;
        font-size: 30px;
        color: #a3a3a3;
      }
      .pj-fen-texte {
        padding: 34px 40px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 42px;
        line-height: 1.5;
        color: var(--color-light);
      }
      .pj-fen-form {
        flex: 1;
        padding: 40px 50px;
        font-family: "Inter", sans-serif;
        color: var(--color-light);
      }
      .pj-fen-form label {
        display: block;
        font-weight: 600;
        font-size: 34px;
        margin-bottom: 16px;
      }
      .pj-fen-champ {
        height: 84px;
        padding: 0 26px;
        border: 3px solid #4a4a4a;
        border-radius: 14px;
        background: #0f0f0f;
        font-size: 44px;
        line-height: 78px;
        letter-spacing: 0.1em;
      }
      .pj-fen-ligne {
        display: flex;
        align-items: center;
        gap: 40px;
        margin-top: 50px;
      }
      .pj-fen-ok {
        font-family: "Anton", sans-serif;
        font-size: 56px;
        color: var(--color-accent);
        text-transform: uppercase;
      }
      .pj-souris {
        position: absolute;
        width: 46px;
        height: 60px;
        overflow: visible;
        transform-origin: 3px 3px;
      }
      .pj-noeud {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 0 22px;
        background: #1e1e1e;
        border: 3px solid #4a4a4a;
        border-radius: 18px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        color: var(--color-light);
        white-space: nowrap;
      }
      .pj-noeud-agent {
        border-color: var(--color-accent);
        background: #23260f;
      }
      .pj-noeud img {
        flex: none;
        width: 58px;
        height: 58px;
      }
      .pj-noeud > div > b {
        display: block;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 40px;
        line-height: 1;
        text-transform: uppercase;
      }
      .pj-noeud > div > span {
        display: block;
        margin-top: 6px;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 28px;
        color: #a3a3a3;
      }
      .pj-noeud-ico {
        flex: none;
        width: 58px;
        height: 58px;
        border-radius: 12px;
        background: var(--color-accent);
        color: #000;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 32px;
        line-height: 58px;
        text-align: center;
      }
      .pj-tg {
        position: absolute;
        display: flex;
        flex-direction: column;
        background: #0e1621;
        border: 8px solid #2c2c2c;
        border-radius: 52px;
        overflow: hidden;
        box-shadow: 0 40px 100px rgba(0, 0, 0, 0.75);
      }
      .pj-tg-tete {
        flex: none;
        height: 104px;
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 22px 26px 0;
        background: #17212b;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 30px;
        color: var(--color-light);
        white-space: nowrap;
      }
      .pj-tg-tete img {
        width: 54px;
        height: 54px;
      }
      .pj-tg-conv {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 14px;
        padding: 22px 16px;
        overflow: hidden;
      }
      .pj-tg-bulle {
        max-width: 88%;
        padding: 14px 20px;
        border-radius: 22px;
        font-family: "Inter", sans-serif;
        font-weight: 500;
        font-size: 28px;
        line-height: 1.3;
        color: var(--color-light);
      }
      .pj-tg-moi {
        align-self: flex-end;
        background: #2b5278;
      }
      .pj-tg-bot {
        align-self: flex-start;
        background: #182533;
      }
      .pj-tg-bulle b {
        color: var(--color-accent);
      }
      .pj-tg-bulle u {
        color: #6ab2f2;
      }
      .pj-tg-champ {
        flex: none;
        height: 88px;
        display: flex;
        align-items: center;
        padding: 0 26px;
        background: #17212b;
        font-family: "Inter", sans-serif;
        font-size: 30px;
        color: #8a9aab;
      }
      .pj-tg-champ i {
        margin-left: auto;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #2aabee;
      }
      .pj-jeton {
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        color: var(--color-accent);
      }
      .pj-jeton-vol {
        position: absolute;
        padding: 10px 26px;
        background: var(--color-accent);
        color: #000;
        font-family: "Anton", sans-serif;
        font-size: 50px;
        text-transform: uppercase;
        box-shadow: 0 0 40px rgba(220, 252, 28, 0.7);
      }
      .pj-impulsion {
        position: absolute;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--color-accent);
        box-shadow: 0 0 30px 12px rgba(220, 252, 28, 0.7);
      }
      .pj-recherche {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 12px;
        height: 84px;
        padding: 0 28px;
        border-radius: 42px;
        background: var(--color-light);
        color: #0a0a06;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 36px;
        white-space: nowrap;
      }
      .pj-loupe {
        width: 32px;
        height: 32px;
        margin-right: 10px;
        border: 6px solid #0a0a06;
        border-radius: 50%;
      }
      .pj-resultat {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 20px;
        height: 88px;
        padding: 0 22px;
        border: 3px solid #3a3a3a;
        border-radius: 14px;
        background: #1a1a1a;
      }
      .pj-resultat > i {
        flex: none;
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: #4a4a4a;
      }
      .pj-resultat > div {
        flex: 1;
      }
      .pj-resultat > div > b {
        display: block;
        height: 14px;
        margin: 8px 0;
        background: #5a5a5a;
      }
      .pj-resultat-marque {
        flex: none;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        opacity: 0;
      }
      .pj-liste {
        position: absolute;
      }
      .pj-option {
        display: flex;
        align-items: center;
        gap: 26px;
        height: 110px;
        margin-bottom: 18px;
        padding: 0 30px;
        border: 4px solid #3a3a3a;
        border-radius: 18px;
        background: #1a1a1a;
        font-family: "Anton", sans-serif;
        font-size: 54px;
        color: var(--color-light);
        text-transform: uppercase;
      }
      .pj-option img {
        width: 64px;
        height: 64px;
      }
      .pj-option > i {
        margin-left: auto;
        width: 44px;
        height: 44px;
        border: 5px solid var(--color-light);
        border-radius: 50%;
      }
      .pj-res-ligne {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-top: 26px;
      }
      .pj-res-ligne > div {
        height: 16px;
        background: #bdbdb8;
      }
      .pj-res-ligne span {
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 30px;
        color: #2b5278;
        text-decoration: underline;
        white-space: nowrap;
      }
      .pj-publier {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 34px;
        padding: 30px 40px;
        border: 3px solid #3a3a3a;
        border-radius: 24px;
        background: #1a1a1a;
        font-family: "Anton", sans-serif;
        font-size: 80px;
        color: var(--color-light);
        text-transform: uppercase;
      }
      .pj-inter {
        position: relative;
        width: 200px;
        height: 104px;
        border-radius: 52px;
        background: #3a3a3a;
      }
      .pj-inter i {
        position: absolute;
        left: 8px;
        top: 8px;
        width: 88px;
        height: 88px;
        border-radius: 50%;
        background: #fff;
      }
      .pj-tableau {
        position: absolute;
      }
      .pj-rang {
        display: flex;
        opacity: 0;
      }
      .pj-rang > b {
        flex: none;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        text-align: center;
      }
      .pj-rang-corps {
        flex: 1;
        background: #161616;
        border: 2px solid #2e2e2e;
      }
      .pj-tuile {
        position: absolute;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        background: #222222;
        border: 3px solid #4a4a4a;
        border-radius: 14px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
      }
      .pj-tuile span {
        font-family: "Anton", sans-serif;
        line-height: 1;
        color: var(--color-light);
        text-transform: uppercase;
        white-space: nowrap;
      }
      .pj-apps {
        flex: 1;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 22px;
        padding: 34px 30px;
        align-content: start;
        position: relative;
      }
      .pj-appli {
        height: 104px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 24px;
        background: #262626;
      }
      .pj-appli img {
        width: 64px;
        height: 64px;
      }
      .pj-appli-q {
        position: absolute;
        left: 130px;
        top: 220px;
        width: 140px;
        height: 140px;
        background: var(--color-accent);
        font-family: "Anton", sans-serif;
        font-size: 110px;
        color: #000;
      }
      .pj-rafale {
        position: absolute;
        overflow: hidden;
        border: 3px solid #ffffff22;
        border-radius: 12px;
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.8);
        background: #000;
      }
      .pj-rafale > video {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .pj-tuile-site {
        position: absolute;
        overflow: hidden;
        border-radius: 10px;
        border: 2px solid #ffffff22;
        background: #000;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
      }
      .pj-tuile-site > img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }
      .pj-num {
        position: absolute;
        left: 10px;
        top: 8px;
        width: 56px;
        height: 56px;
        background: var(--color-accent);
        color: #000;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 40px;
        line-height: 56px;
        text-align: center;
      }
      .pj-repo {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-top: 14px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 30px;
        color: var(--color-light);
        white-space: nowrap;
      }
      .pj-repo img {
        width: 40px;
        height: 40px;
      }
      .pj-repo b {
        margin-left: 10px;
        padding: 4px 14px;
        background: var(--color-accent);
        color: #000;
      }
      .pj-typo {
        position: absolute;
        width: 178px;
        height: 200px;
        padding-top: 20px;
        border: 3px solid #3a3a3a;
        border-radius: 16px;
        background: #161616;
        color: var(--color-light);
        font-size: 96px;
        line-height: 1;
        text-align: center;
      }
      .pj-typo span {
        display: block;
        margin-top: 18px;
        font-family: "JetBrains Mono", monospace;
        font-style: normal;
        font-weight: 700;
        font-size: 18px;
        color: #a3a3a3;
      }
      .pj-c-btn {
        display: inline-block;
        padding: 22px 46px;
        border-radius: 14px;
        background: #fafafa;
        color: #09090b;
        font-family: "Inter", sans-serif;
        font-weight: 700;
        font-size: 36px;
      }
      .pj-c-input {
        width: 520px;
        padding: 22px 28px;
        border: 3px solid #3f3f46;
        border-radius: 14px;
        background: #09090b;
        color: #a1a1aa;
        font-family: "Inter", sans-serif;
        font-size: 32px;
      }
      .pj-c-card {
        width: 520px;
        padding: 28px 32px;
        border: 3px solid #3f3f46;
        border-radius: 18px;
        background: #18181b;
        font-family: "Inter", sans-serif;
        color: #fafafa;
      }
      .pj-c-card b {
        display: block;
        font-size: 38px;
      }
      .pj-c-card span {
        display: block;
        margin-top: 8px;
        font-size: 28px;
        color: #a1a1aa;
      }
      .pj-photo {
        position: absolute;
        width: 380px;
        padding: 12px 12px 40px;
        background: #f5f5f4;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
      }
      .pj-photo img {
        display: block;
        width: 100%;
        height: 200px;
        object-fit: cover;
      }
      .pj-toast {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 22px 30px;
        border: 2px solid #3f3f46;
        border-radius: 16px;
        background: #18181b;
        color: #fafafa;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 32px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        white-space: nowrap;
      }
      .pj-toast b {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--color-accent);
        color: #000;
        text-align: center;
        line-height: 44px;
      }
      /* ---- Éléments dynamiques (al-) et site de démo (ds-) ---- */
      :root {
        --vert: #dcfc1c;
      }
      .pj-visiteur-perso .c * {
        fill: #ecece8;
        stroke: #ecece8;
      }
      .pj-visiteur-perso .p * {
        fill: #1b2235;
      }
      .al-choc {
        position: absolute;
        font-family: "Anton", sans-serif;
        color: var(--color-accent);
        text-transform: uppercase;
        text-align: center;
        line-height: 0.9;
        white-space: nowrap;
        text-shadow:
          -7px 0 rgba(0, 229, 255, 0.75),
          7px 0 rgba(255, 46, 99, 0.75),
          0 0 60px var(--accent-glow);
      }
      .al-ruban {
        position: absolute;
        left: -300px;
        width: 2520px;
        height: 118px;
        overflow: hidden;
        background: var(--color-accent);
        border-top: 16px solid transparent;
        border-bottom: 16px solid transparent;
        border-image: repeating-linear-gradient(-45deg, #0c0c0c 0 18px, var(--color-accent) 18px 36px) 16;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      }
      .al-ruban-t {
        font-family: "Anton", sans-serif;
        font-size: 66px;
        line-height: 86px;
        color: #0c0c0c;
        text-transform: uppercase;
        white-space: nowrap;
        letter-spacing: 0.04em;
      }
      .al-num {
        position: absolute;
        font-family: "Anton", sans-serif;
        font-size: 130px;
        line-height: 1;
        color: transparent;
        -webkit-text-stroke: 4px var(--color-accent);
        transform-origin: 0% 0%;
      }
      .al-titre {
        font-family: "Anton", sans-serif;
        color: #ffffff;
        text-transform: uppercase;
        line-height: 1;
        white-space: nowrap;
        text-shadow: 6px 6px 0 var(--color-accent);
      }
      .al-sous {
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 30px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--color-accent);
        margin-bottom: 20px;
      }
      .al-tuile {
        position: absolute;
        overflow: hidden;
        background: #000;
        outline: 3px solid #0c0c0c;
      }
      .al-nav {
        position: absolute;
        display: flex;
        flex-direction: column;
        background: #111522;
        border: 3px solid #2e3650;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 40px 110px rgba(0, 0, 0, 0.75);
      }
      .al-nav-barre {
        display: flex;
        align-items: center;
        gap: 12px;
        height: 58px;
        padding: 0 22px;
        background: #1a2033;
        flex-shrink: 0;
      }
      .al-nav-barre i {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #3a4462;
      }
      .al-nav-barre i:first-child {
        background: var(--color-accent);
      }
      .al-nav-barre span {
        margin-left: 18px;
        flex: 1;
        background: #0c0c0c;
        border-radius: 20px;
        padding: 6px 22px;
        font-family: "JetBrains Mono", monospace;
        font-size: 24px;
        color: #a8b0c8;
      }
      .al-nav-corps {
        position: relative;
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }
      .al-nav-video {
        position: relative;
        flex: 1;
        overflow: hidden;
      }
      .al-nav-pied {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 110px;
        padding: 0 30px;
        background: #151a2a;
        flex-shrink: 0;
      }
      .al-nav-pied span {
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        color: #a8b0c8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
      }
      .al-bouton {
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-size: 48px;
        line-height: 1;
        padding: 14px 44px 16px;
        text-transform: uppercase;
        border-radius: 12px;
        box-shadow: 0 8px 0 var(--accent-shade);
      }
      .al-bouton-l {
        text-align: center;
        margin-top: 22px;
      }
      .al-inter {
        position: relative;
        width: 130px;
        height: 64px;
        border-radius: 32px;
        background: #3a4462;
      }
      .al-inter i {
        position: absolute;
        left: 6px;
        top: 6px;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: #ecece8;
      }
      .al-popup {
        position: absolute;
        background: #ecece8;
        border: 4px solid #0c0c0c;
        box-shadow: 14px 14px 0 rgba(0, 0, 0, 0.55);
      }
      .al-popup-barre {
        display: flex;
        align-items: center;
        gap: 14px;
        background: var(--color-accent);
        padding: 8px 16px;
        font-family: "Anton", sans-serif;
        font-size: 40px;
        line-height: 1.1;
        color: #0c0c0c;
        text-transform: uppercase;
      }
      .al-popup-corps {
        padding: 18px 22px 22px;
        font-family: "Inter", sans-serif;
        font-weight: 800;
        font-size: 38px;
        color: #0c0c0c;
        white-space: nowrap;
      }
      .al-carte {
        position: absolute;
        display: flex;
        flex-direction: column;
        background: #111522;
        border: 3px solid #2e3650;
        box-shadow: 0 34px 100px rgba(0, 0, 0, 0.7);
        overflow: hidden;
      }
      .al-carte-tete {
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-size: 46px;
        line-height: 1;
        padding: 12px 24px 14px;
        text-transform: uppercase;
        white-space: nowrap;
        flex-shrink: 0;
      }
      .al-carte-corps {
        position: relative;
        flex: 1;
        padding: 18px 26px;
      }
      .al-carte-video {
        position: absolute;
        inset: 0;
      }
      .al-id {
        display: flex;
        align-items: center;
        gap: 26px;
      }
      .al-id p {
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        color: #ecece8;
        line-height: 1.6;
        white-space: nowrap;
      }
      .al-id p b {
        display: inline-block;
        height: 18px;
        background: #3a4462;
        vertical-align: middle;
      }
      .al-mini {
        position: relative;
        width: 150px;
        height: 110px;
        overflow: hidden;
        flex-shrink: 0;
        outline: 3px solid var(--color-accent);
      }
      .al-ok {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 8px;
        background: var(--vert);
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        line-height: 1;
        padding: 6px 20px 8px 10px;
        text-transform: uppercase;
        white-space: nowrap;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
      }
      .al-scan {
        position: absolute;
        height: 6px;
        background: var(--color-accent);
        box-shadow: 0 0 30px 8px var(--accent-glow);
      }
      .al-alerte {
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse at center, rgba(220, 252, 28, 0.25), rgba(255, 40, 20, 0.85));
        opacity: 0;
        pointer-events: none;
      }
      .al-liste {
        position: absolute;
        width: 760px;
        background: #111522;
        border: 3px solid #2e3650;
        box-shadow: 0 40px 110px rgba(0, 0, 0, 0.75);
      }
      .al-liste-tete {
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-size: 50px;
        line-height: 1;
        padding: 14px 28px 16px;
        text-transform: uppercase;
      }
      .al-ligne5 {
        display: flex;
        align-items: center;
        gap: 24px;
        height: 96px;
        padding: 0 30px;
        border-top: 2px solid #232a40;
      }
      .al-ligne5 b {
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 56px;
        color: var(--color-accent);
        width: 40px;
      }
      .al-ligne5 span {
        height: 26px;
        background: #2e3650;
      }
      .al-case {
        display: inline-block;
        flex-shrink: 0;
        width: 48px;
        height: 48px;
        border: 5px solid var(--color-accent);
        border-radius: 8px;
      }
      .al-dossier {
        position: absolute;
        width: 200px;
        height: 150px;
        background: var(--color-accent);
        border-radius: 8px 22px 12px 12px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      }
      .al-dossier b {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 22px;
        text-align: center;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 40px;
        color: #0c0c0c;
        text-transform: uppercase;
      }
      .al-oeil {
        position: absolute;
        width: 150px;
        text-align: center;
        color: #8a93ab;
      }
      .al-oeil span {
        position: absolute;
        left: 0;
        right: 0;
        top: 58px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 20px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: #0c0c0c;
        padding: 3px 0;
      }
      .al-oeil .al-actif {
        background: var(--color-accent);
        color: #0c0c0c;
      }
      .al-voile {
        position: absolute;
        inset: 0;
        background: rgba(11, 14, 20, 0.45);
      }
      .al-banniere {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        background: #ffffff;
        padding: 18px 26px 22px;
        box-shadow: 0 -20px 60px rgba(0, 0, 0, 0.5);
      }
      .al-banniere p {
        font-family: "Inter", sans-serif;
        font-weight: 700;
        font-size: 30px;
        color: #0c0c0c;
        margin-bottom: 14px;
      }
      .al-banniere div {
        display: flex;
        gap: 16px;
      }
      .al-banniere span {
        font-family: "Inter", sans-serif;
        font-weight: 800;
        font-size: 26px;
        padding: 12px 22px;
        border-radius: 8px;
      }
      .al-b2 {
        border: 3px solid #0c0c0c;
        color: #0c0c0c;
      }
      .al-b1 {
        background: var(--color-accent);
        color: #0c0c0c;
        margin-left: auto;
      }
      .al-surligne {
        position: absolute;
        border: 5px solid var(--color-accent);
        border-radius: 6px;
        box-shadow: 0 0 30px var(--accent-glow);
      }
      .al-produit {
        display: flex;
        align-items: center;
        gap: 22px;
        padding: 14px 0;
        border-bottom: 2px solid #232a40;
        font-family: "Inter", sans-serif;
        font-weight: 700;
        font-size: 34px;
        color: #ecece8;
      }
      .al-produit i {
        width: 64px;
        height: 64px;
        border-radius: 10px;
      }
      .al-produit b {
        margin-left: auto;
        font-family: "JetBrains Mono", monospace;
      }
      .al-total {
        display: flex;
        justify-content: space-between;
        padding: 16px 0;
        font-family: "Anton", sans-serif;
        font-size: 44px;
        color: #ffffff;
        text-transform: uppercase;
      }
      .al-cgv {
        display: flex;
        align-items: center;
        gap: 18px;
        font-family: "Inter", sans-serif;
        font-weight: 700;
        font-size: 28px;
        color: #ecece8;
        white-space: nowrap;
      }
      .al-copy {
        position: absolute;
        font-family: "Inter", sans-serif;
        font-weight: 900;
        font-size: 190px;
        line-height: 1;
        color: var(--color-accent);
        text-shadow: 0 0 60px var(--accent-glow);
      }
      .al-typos {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 22px;
        background: #ecece8;
        font-size: 96px;
        color: #0c0c0c;
      }
      .al-bonus {
        position: absolute;
        font-family: "Anton", sans-serif;
        font-size: 92px;
        line-height: 1;
        padding: 10px 30px 14px;
        color: #0c0c0c;
        text-transform: uppercase;
        background: repeating-linear-gradient(-45deg, var(--color-accent) 0 26px, #ffb347 26px 52px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      }
      .al-champ {
        margin-bottom: 16px;
      }
      .al-champ span {
        display: block;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 24px;
        color: #a8b0c8;
        text-transform: uppercase;
        margin-bottom: 6px;
      }
      .al-champ b {
        display: block;
        height: 50px;
        border: 3px solid #3a4462;
        border-radius: 8px;
        background: linear-gradient(90deg, #2e3650 0 60%, transparent 60%) 16px 16px / 70% 18px no-repeat, #0c0c0c;
      }
      .al-https {
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        color: var(--vert);
      }
      .al-https svg {
        width: 26px;
        height: 32px;
      }
      .al-etoiles i {
        position: absolute;
        width: 46px;
        height: 46px;
        background: #ffffff;
        clip-path: polygon(50% 0, 61% 39%, 100% 50%, 61% 61%, 50% 100%, 39% 61%, 0 50%, 39% 39%);
      }
      .al-etoiles i:nth-child(1) { left: 40px; top: 60px; }
      .al-etoiles i:nth-child(2) { left: 640px; top: 90px; width: 60px; height: 60px; }
      .al-etoiles i:nth-child(3) { left: 330px; top: 20px; width: 34px; height: 34px; }
      .al-etoiles i:nth-child(4) { left: 90px; top: 400px; width: 30px; height: 30px; }
      .al-etoiles i:nth-child(5) { left: 680px; top: 380px; }
      .al-etoiles {
        position: absolute;
        pointer-events: none;
      }
      .al-item {
        display: flex;
        align-items: center;
        gap: 22px;
        height: 76px;
        font-family: "Anton", sans-serif;
        font-size: 46px;
        color: #ffffff;
        text-transform: uppercase;
      }
      .al-egal {
        position: absolute;
        width: 110px;
      }
      .al-egal i {
        display: block;
        height: 26px;
        margin-bottom: 26px;
        background: var(--vert);
        transform-origin: 50% 50%;
      }
      /* ---- Site de démo « LUMEN » (ds-) ---- */
      .ds-plein {
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
      }
      .ds-fenetre {
        position: absolute;
        background: #0a0a0a;
        border: 2px solid #3a3a3a;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 50px 120px rgba(0, 0, 0, 0.8);
      }
      .ds-fen-barre {
        display: flex;
        align-items: center;
        gap: 10px;
        height: 52px;
        padding: 0 20px;
        background: #1b1b1b;
      }
      .ds-fen-barre i {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #4a4a4a;
      }
      .ds-fen-barre i:first-child {
        background: var(--color-accent);
      }
      .ds-fen-barre span {
        margin-left: 16px;
        flex: 1;
        background: #0c0c0c;
        border-radius: 18px;
        padding: 5px 20px;
        font-family: "JetBrains Mono", monospace;
        font-size: 22px;
        color: #a8a8a8;
      }
      .ds-fen-vue {
        position: relative;
        overflow: hidden;
      }
      .ds-fen-echelle {
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 1080px;
        transform-origin: 0 0;
      }
      .ds-section {
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #07070b;
        font-family: "Inter", sans-serif;
        color: #ffffff;
      }
      .ds-section > video {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .ds-voile {
        position: absolute;
        inset: 0;
        background: linear-gradient(100deg, rgba(7, 7, 11, 0.92) 25%, rgba(7, 7, 11, 0.35) 70%, rgba(7, 7, 11, 0.6));
      }
      .ds-blob {
        position: absolute;
        border-radius: 50%;
        mix-blend-mode: screen;
      }
      .ds-nav {
        position: absolute;
        left: 120px;
        right: 120px;
        top: 50px;
        display: flex;
        align-items: center;
        gap: 46px;
        font-size: 24px;
        font-weight: 500;
        color: #c9c9d1;
      }
      .ds-nav b {
        font-weight: 800;
        font-size: 32px;
        letter-spacing: 0.22em;
        color: #ffffff;
        margin-right: auto;
      }
      .ds-nav em {
        font-style: normal;
        font-weight: 700;
        color: #07070b;
        background: #ffffff;
        padding: 12px 28px;
        border-radius: 40px;
      }
      .ds-h1,
      .ds-h2,
      .ds-geant {
        position: absolute;
        left: 120px;
        font-weight: 800;
        letter-spacing: -0.045em;
        line-height: 0.98;
      }
      .ds-h1 {
        top: 260px;
        font-size: 150px;
      }
      .ds-h2 {
        top: 170px;
        font-size: 110px;
      }
      .ds-geant {
        left: 0;
        width: 1920px;
        top: 330px;
        text-align: center;
        font-size: 330px;
        color: #0c0c0c;
      }
      .ds-ligne {
        display: block;
        overflow: hidden;
        padding-bottom: 0.2em;
        margin-bottom: -0.14em;
      }
      .ds-l {
        display: inline-block;
      }
      .ds-sous {
        position: absolute;
        left: 124px;
        top: 600px;
        width: 760px;
        font-size: 34px;
        line-height: 1.4;
        color: #b9b9c6;
      }
      .ds-cta {
        position: absolute;
        left: 124px;
        top: 740px;
        padding: 26px 54px;
        border-radius: 60px;
        background: var(--color-accent);
        color: #07070b;
        font-size: 30px;
        font-weight: 800;
        overflow: hidden;
      }
      .ds-cta i {
        position: absolute;
        left: 0;
        top: -20px;
        width: 90px;
        height: 140px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.85), transparent);
        transform: skewX(-20deg);
      }
      .ds-flot {
        position: absolute;
        width: 380px;
        padding: 14px;
        border-radius: 26px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.22);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
      }
      .ds-flot-v {
        position: relative;
        height: 230px;
        border-radius: 16px;
        overflow: hidden;
      }
      .ds-flot span {
        display: block;
        margin: 12px 8px 2px;
        font-size: 24px;
        font-weight: 600;
        color: #e6e6ee;
      }
      .ds-services {
        background: #0b0b12;
      }
      .ds-defile {
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 2100px;
      }
      .ds-petit {
        position: absolute;
        left: 124px;
        top: 110px;
        font-size: 28px;
        font-weight: 600;
        letter-spacing: 0.1em;
        color: var(--color-accent);
        text-transform: uppercase;
      }
      .ds-centre {
        left: 0;
        width: 1920px;
        text-align: center;
      }
      .ds-carte {
        position: absolute;
        top: 560px;
        width: 520px;
        height: 640px;
        border-radius: 28px;
        background: #15151f;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      }
      .ds-carte-v {
        position: relative;
        height: 470px;
        overflow: hidden;
      }
      .ds-carte b,
      .ds-carte3d b {
        display: block;
        margin: 26px 30px 6px;
        font-size: 40px;
        font-weight: 800;
        letter-spacing: -0.02em;
      }
      .ds-carte span {
        display: block;
        margin: 0 30px;
        font-size: 26px;
        color: #9a9aab;
      }
      .ds-stats {
        position: absolute;
        left: 140px;
        top: 1330px;
        display: flex;
        gap: 140px;
      }
      .ds-stat b {
        display: block;
        font-size: 120px;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: var(--color-accent);
      }
      .ds-stat span {
        font-size: 30px;
        color: #9a9aab;
      }
      .ds-para {
        background: linear-gradient(to bottom, #090716 0%, #1d1440 55%, #3a1f5c 100%);
      }
      .ds-etoiles i {
        position: absolute;
        border-radius: 50%;
        background: #ffffff;
        opacity: 0.8;
      }
      .ds-etoiles {
        position: absolute;
        inset: 0;
      }
      .ds-lune {
        position: absolute;
        left: 1320px;
        top: 130px;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #ffffff, #d9d4ff 60%, #8f86c9);
        box-shadow: 0 0 120px rgba(200, 190, 255, 0.6);
      }
      .ds-plan {
        position: absolute;
        left: 0;
        top: 280px;
        width: 1920px;
        height: 900px;
      }
      .ds-para-mot {
        position: absolute;
        left: 0;
        width: 1920px;
        top: 250px;
        text-align: center;
        font-size: 300px;
        font-weight: 900;
        letter-spacing: -0.05em;
        color: #ffffff;
      }
      .ds-para-sous {
        position: absolute;
        left: 124px;
        top: 90px;
        z-index: 9;
        font-size: 28px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--color-accent);
      }
      .ds-trans-a,
      .ds-trans-b,
      .ds-trans-c {
        position: absolute;
        inset: 0;
        overflow: hidden;
      }
      .ds-trans-a > video {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .ds-trans-b {
        background: var(--color-accent);
        clip-path: circle(0% at 50% 50%);
      }
      .ds-trans-c {
        background: #07070b;
        clip-path: inset(100% 0% 0% 0%);
      }
      .ds-blanc {
        color: #ffffff;
        top: 420px;
      }
      .ds-bas {
        top: 760px;
      }
      .ds-tuile {
        position: absolute;
        top: 140px;
        width: 540px;
        height: 560px;
        border-radius: 26px;
        overflow: hidden;
      }
      .ds-tuile:nth-child(1) {
        left: 120px;
      }
      .ds-tuile:nth-child(2) {
        left: 690px;
      }
      .ds-tuile:nth-child(3) {
        left: 1260px;
      }
      .ds-survol {
        background: #0b0b12;
      }
      .ds-carte3d {
        position: absolute;
        top: 170px;
        width: 500px;
        height: 500px;
        border-radius: 28px;
        background: #15151f;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      }
      .ds-carte3d .ds-carte-v {
        height: 390px;
      }
      .ds-lumiere {
        position: absolute;
        left: 60px;
        top: 40px;
        width: 380px;
        height: 380px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.45), transparent 65%);
        mix-blend-mode: overlay;
        opacity: 0;
      }
      .ds-btns {
        position: absolute;
        left: 0;
        width: 1920px;
        top: 730px;
        display: flex;
        justify-content: center;
        gap: 40px;
      }
      .ds-btn {
        position: relative;
        padding: 26px 60px;
        border-radius: 60px;
        border: 3px solid var(--color-accent);
        color: #ffffff;
        font-size: 32px;
        font-weight: 800;
        overflow: hidden;
      }
      .ds-btn i {
        position: absolute;
        inset: 0;
        background: var(--color-accent);
        transform-origin: 0% 50%;
        transform: scaleX(0);
      }
      .ds-btn span {
        position: relative;
      }
      .ds-curseur {
        position: absolute;
        width: 46px;
        height: 60px;
        z-index: 20;
      }
      .ds-chaos {
        background: #ff00aa;
      }
      .ds-chaos-fond {
        position: absolute;
        left: -500px;
        top: -900px;
        width: 2900px;
        height: 2900px;
        background: conic-gradient(#ff0040, #ffdd00, #00ff66, #00c8ff, #9b00ff, #ff0040);
        opacity: 0.85;
      }
      .ds-chaos-titre {
        top: 110px;
        font-size: 170px;
        color: #ffff00;
        text-shadow: 8px 8px 0 #0000ff;
      }
      .ds-chaos-band {
        position: absolute;
        left: 0;
        top: 950px;
        white-space: nowrap;
        font-size: 64px;
        font-weight: 900;
        color: #000000;
        background: #ffff00;
        padding: 8px 0;
        width: 4000px;
      }
      .ds-prix {
        position: absolute;
        left: 0;
        width: 1920px;
        top: 280px;
        text-align: center;
        font-family: "Anton", sans-serif;
        font-size: 300px;
        line-height: 1;
        color: var(--color-accent);
        text-shadow:
          0 0 40px var(--accent-glow),
          0 12px 0 #000000;
        white-space: nowrap;
      }
      .ds-prix span {
        margin-left: 30px;
      }
      .al-code {
        padding: 26px 30px;
        font-family: "JetBrains Mono", monospace;
        font-size: 30px;
        line-height: 1.55;
        color: #e6e6e6;
      }
      .al-code-l {
        white-space: pre;
      }
      .al-code-l i {
        font-style: normal;
        color: #5a5a5a;
        margin-right: 24px;
      }
      .al-chat {
        position: absolute;
        left: 210px;
        top: 250px;
        width: 1200px;
        background: #151515;
        border: 2px solid #3a3a3a;
        border-radius: 26px;
        box-shadow: 0 40px 110px rgba(0, 0, 0, 0.75);
        padding: 30px 36px 32px;
      }
      .al-chat-tete {
        display: flex;
        align-items: center;
        gap: 16px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #9a9a9a;
        margin-bottom: 22px;
      }
      .al-chat-tete img {
        width: 44px;
        height: 44px;
      }
      .al-chat-champ {
        min-height: 230px;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 52px;
        line-height: 1.3;
        color: #ffffff;
      }
      .al-chat-cur {
        display: inline-block;
        width: 4px;
        height: 54px;
        margin-left: 6px;
        vertical-align: middle;
        background: var(--color-accent);
      }
      .al-chat-env {
        margin-top: 22px;
        margin-left: auto;
        width: 240px;
        text-align: center;
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-size: 44px;
        padding: 10px 0 12px;
        border-radius: 14px;
        text-transform: uppercase;
      }
      .al-abo {
        position: absolute;
        left: 600px;
        top: 700px;
        display: flex;
        align-items: center;
        gap: 26px;
        padding: 22px 34px;
        border-radius: 70px;
        background: rgba(12, 12, 12, 0.92);
        border: 2px solid #3a3a3a;
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7);
      }
      .al-abo-av {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-style: normal;
        font-size: 60px;
        line-height: 90px;
        text-align: center;
      }
      .al-abo b {
        display: block;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 52px;
        line-height: 1;
        color: #ffffff;
        text-transform: uppercase;
      }
      .al-abo-txt > span {
        font-family: "JetBrains Mono", monospace;
        font-size: 24px;
        color: #9a9a9a;
      }
      .al-abo-btn {
        position: relative;
        width: 300px;
        height: 84px;
        border-radius: 42px;
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-size: 44px;
        text-transform: uppercase;
      }
      .al-abo-btn span {
        position: absolute;
        left: 0;
        right: 0;
        top: 12px;
        text-align: center;
      }
      /* ---- Vidéo 9 : vitesse (vt-) ---- */
      .vt-chrono {
        position: absolute;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        line-height: 1;
        white-space: nowrap;
        text-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
      }
      .vt-chrono span {
        font-size: 0.45em;
        margin-left: 12px;
      }
      .vt-page {
        position: relative;
        width: 100%;
        height: 100%;
        background: #f4f4f2;
      }
      .vt-sq,
      .vt-sq2 {
        position: absolute;
        background: #dcdcd8;
        border-radius: 10px;
      }
      .vt-sq2 {
        inset: 0;
      }
      .vt-roue {
        position: absolute;
        left: calc(50% - 50px);
        top: 170px;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 12px solid #cfcfcb;
        border-top-color: #4a9eff;
      }
      .vt-barre {
        position: absolute;
        left: 0;
        right: 0;
        top: 0;
        height: 8px;
        background: #e4e4e0;
      }
      .vt-barre i {
        position: absolute;
        inset: 0;
        background: #4a9eff;
        transform-origin: 0% 50%;
      }
      .vt-charge {
        position: absolute;
        left: 0;
        right: 0;
        top: 300px;
        text-align: center;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 34px;
        color: #5e5e5a;
      }
      .vt-ferme {
        position: absolute;
        left: 150px;
        top: 90px;
        display: flex;
        align-items: center;
        gap: 40px;
        background: #2a2a2a;
        border-radius: 14px 14px 0 0;
        padding: 10px 26px;
        font-family: "Inter", sans-serif;
        font-size: 28px;
        color: #ececec;
      }
      .vt-ferme b {
        font-size: 40px;
        color: #ff4d4d;
      }
      .vt-ia {
        position: absolute;
        left: 1320px;
        top: 330px;
        font-family: "Anton", sans-serif;
        font-size: 300px;
        line-height: 1;
        color: var(--color-accent);
        text-shadow: 0 0 50px var(--accent-glow);
      }
      .vt-jauge {
        position: absolute;
        text-align: center;
      }
      .vt-jauge svg {
        display: block;
      }
      .vt-jauge b {
        position: absolute;
        left: 0;
        right: 0;
        top: 34%;
        font-family: "Inter", sans-serif;
        font-weight: 800;
        font-size: 96px;
        line-height: 1;
        color: #ff4d4d;
      }
      .vt-jauge span {
        display: block;
        margin-top: 14px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 26px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #ececec;
        white-space: nowrap;
      }
      .vt-cascade,
      .vt-scripts {
        position: absolute;
        width: 780px;
        background: #141414;
        border: 2px solid #3a3a3a;
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7);
      }
      .vt-scripts {
        left: 1060px;
        top: 380px;
        width: 700px;
      }
      .vt-cas-tete {
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-size: 40px;
        line-height: 1;
        padding: 12px 22px 14px;
        text-transform: uppercase;
      }
      .vt-cas-corps {
        position: relative;
        height: 360px;
        margin: 20px 0;
      }
      .vt-res {
        position: absolute;
        left: 0;
        right: 0;
        height: 40px;
      }
      .vt-res span {
        position: absolute;
        left: 22px;
        top: 4px;
        font-family: "JetBrains Mono", monospace;
        font-size: 24px;
        color: #c8c8c8;
      }
      .vt-res i {
        position: absolute;
        top: 6px;
        height: 28px;
        border-radius: 6px;
      }
      .vt-sugg {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 16px;
        background: #ececec;
        padding: 12px 22px 12px 12px;
        font-family: "Inter", sans-serif;
        font-weight: 700;
        font-size: 30px;
        color: #0c0c0c;
        white-space: nowrap;
        box-shadow: 0 16px 50px rgba(0, 0, 0, 0.5);
      }
      .vt-sugg i {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 46px;
        height: 46px;
        background: var(--color-accent);
        border-radius: 8px;
      }
      .vt-pb {
        font-size: 25px;
      }
      .vt-pb i {
        background: #ff4d4d;
      }
      .vt-poids {
        position: absolute;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        color: #ececec;
      }
      .vt-poids span {
        display: block;
        margin-bottom: 10px;
      }
      .vt-poids-piste {
        position: relative;
        width: 100%;
        height: 26px;
        border-radius: 13px;
        background: #2a2a2a;
        overflow: hidden;
      }
      .vt-poids-piste i {
        position: absolute;
        inset: 0;
        transform-origin: 0% 50%;
        background: #ff4d4d;
      }
      .vt-poids > b {
        position: absolute;
        right: 0;
        top: 0;
      }
      .vt-poids-n2 {
        position: absolute;
        width: 230px;
        text-align: right;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        color: #0cce6b;
      }
      .vt-js {
        position: relative;
        margin: 14px 22px;
        padding: 10px 18px;
        background: #1e1e1e;
        border-left: 6px solid #4a9eff;
        font-family: "JetBrains Mono", monospace;
        font-size: 28px;
        color: #ececec;
      }
      .vt-inutile {
        border-left-color: #ff4d4d;
      }
      .vt-js i {
        position: absolute;
        left: 10px;
        right: 10px;
        top: 50%;
        height: 6px;
        margin-top: -3px;
        background: #ff4d4d;
        transform: scaleX(0);
        transform-origin: 0% 50%;
      }
      .vt-lazy {
        position: absolute;
        left: 730px;
        top: 330px;
        width: 460px;
        height: 500px;
        background: #141414;
        border: 2px solid #3a3a3a;
        overflow: hidden;
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7);
      }
      .vt-lazy-tete {
        position: relative;
        z-index: 2;
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 24px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 8px 14px;
      }
      .vt-lazy-corps {
        position: absolute;
        left: 20px;
        top: 70px;
        width: 420px;
      }
      .vt-diff {
        position: relative;
        width: 420px;
        height: 240px;
        margin-bottom: 20px;
        border-radius: 14px;
        overflow: hidden;
        background: #202020;
      }
      .vt-jsbloc {
        position: absolute;
        background: var(--color-accent);
        color: #0c0c0c;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 28px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 8px 16px;
      }
      .vt-exemple {
        position: absolute;
        left: 1380px;
        top: 360px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 26px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #9a9a9a;
      }
      /* ---- Vidéo 10 : référencement (sx-) ---- */
      .sx-plein {
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #000;
      }
      .sx-photo > img,
      .sx-photo > video {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .sx-barre {
        position: absolute;
        background: #ffffff;
        border-radius: 40px;
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.6);
        overflow: hidden;
      }
      .sx-champ {
        display: flex;
        align-items: center;
        gap: 22px;
        height: 96px;
        padding: 0 36px;
        font-family: "Inter", sans-serif;
        font-size: 44px;
        color: #202124;
      }
      .sx-res {
        border-top: 1px solid #e0e0e0;
        padding: 22px 40px 28px;
        font-family: "Inter", sans-serif;
        font-weight: 600;
        font-size: 34px;
        color: #c5221f;
      }
      .sx-sugg {
        position: absolute;
        display: flex;
        align-items: center;
        gap: 16px;
        background: #ececec;
        padding: 12px 22px 12px 12px;
        font-family: "Inter", sans-serif;
        font-weight: 700;
        font-size: 30px;
        color: #0c0c0c;
        white-space: nowrap;
        box-shadow: 0 16px 50px rgba(0, 0, 0, 0.5);
      }
      .sx-sugg i {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 46px;
        height: 46px;
        background: var(--color-accent);
        border-radius: 8px;
      }
      .sx-pb i {
        background: #ff4d4d;
      }
      .sx-riche {
        position: absolute;
        width: 820px;
        background: #ffffff;
        border-radius: 14px;
        padding: 22px 28px;
        font-family: "Inter", sans-serif;
        color: #202124;
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.6);
      }
      .sx-url {
        display: block;
        font-size: 22px;
        color: #4d5156;
      }
      .sx-riche b {
        display: block;
        margin: 6px 0;
        font-size: 32px;
        font-weight: 600;
        color: #1a0dab;
      }
      .sx-etoiles {
        font-size: 24px;
        color: #4d5156;
      }
      .sx-etoiles i {
        font-style: normal;
        color: #f9ab00;
        font-size: 28px;
      }
      .sx-riche p {
        margin-top: 6px;
        font-size: 24px;
        color: #4d5156;
      }
      .sx-arbre {
        position: absolute;
        width: 920px;
        height: 500px;
      }
      .sx-traits {
        position: absolute;
        left: 0;
        top: 0;
      }
      .sx-noeud {
        position: absolute;
        width: 220px;
        height: 70px;
        background: #141414;
        border: 3px solid var(--color-accent);
        border-radius: 12px;
        text-align: center;
      }
      .sx-noeud b {
        display: block;
        margin-top: 8px;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 30px;
        line-height: 1;
        color: #ffffff;
        text-transform: uppercase;
        white-space: nowrap;
      }
      .sx-noeud span {
        display: block;
        margin-top: 4px;
        font-family: "JetBrains Mono", monospace;
        font-size: 17px;
        color: var(--color-accent);
        white-space: nowrap;
      }
      .sx-hud {
        position: absolute;
        background: rgba(12, 12, 12, 0.8);
        padding: 10px 22px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 36px;
        color: #ececec;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      .sx-hud b {
        color: #ff4d4d;
      }
      .sx-ex {
        left: 1060px;
        top: 330px;
      }
      /* ---- Vidéo 11 : sites 3D (td-) ---- */
      .td-molette {
        position: absolute;
        left: 880px;
        top: 560px;
        width: 160px;
        text-align: center;
        opacity: 0;
      }
      .td-molette::before {
        content: "";
        display: block;
        margin: 0 auto;
        width: 110px;
        height: 170px;
        border: 6px solid #ececec;
        border-radius: 60px;
      }
      .td-molette i {
        position: absolute;
        left: 72px;
        top: 34px;
        width: 16px;
        height: 34px;
        border-radius: 8px;
        background: var(--color-accent);
      }
      .td-molette span {
        display: block;
        margin-top: 14px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 24px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #ececec;
      }
      .td-tel {
        position: absolute;
        left: 760px;
        top: 300px;
        width: 300px;
        height: 560px;
        border: 10px solid #2c2c2c;
        border-radius: 46px;
        background: #000;
        overflow: hidden;
        box-shadow: 0 40px 100px rgba(0, 0, 0, 0.8);
      }
      .td-tel-ecran {
        position: absolute;
        inset: 0;
      }
      /* ---- Vidéo 12 : sites de métiers (bz-) ---- */
      .bz-page {
        background: #0e0e10;
      }
      .bz-defile {
        position: absolute;
        left: 0;
        top: 0;
        width: 1920px;
        height: 1700px;
      }
      .bz-nav {
        position: absolute;
        left: 120px;
        right: 120px;
        top: 46px;
        display: flex;
        align-items: center;
        gap: 46px;
        font-family: "Inter", sans-serif;
        font-size: 28px;
        font-weight: 600;
        color: #d6d6d6;
      }
      .bz-nav b {
        margin-right: auto;
        font-size: 40px;
        font-weight: 900;
        letter-spacing: 0.08em;
        color: var(--bz);
      }
      .bz-nav em {
        font-style: normal;
        font-weight: 800;
        color: #0c0c0c;
        background: var(--bz);
        padding: 14px 30px;
        border-radius: 40px;
      }
      .bz-h1 {
        top: 210px;
        font-size: 128px;
      }
      .bz-slogan {
        position: absolute;
        left: 124px;
        top: 520px;
        width: 820px;
        font-family: "Inter", sans-serif;
        font-size: 40px;
        line-height: 1.35;
        color: #bdbdbd;
      }
      .bz-cta {
        position: absolute;
        left: 124px;
        top: 650px;
        padding: 26px 56px;
        border-radius: 60px;
        background: var(--bz);
        color: #0c0c0c;
        font-family: "Inter", sans-serif;
        font-size: 36px;
        font-weight: 800;
      }
      .bz-hero-media {
        position: absolute;
        left: 1040px;
        top: 170px;
        width: 760px;
        height: 520px;
        border-radius: 30px;
        overflow: hidden;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6);
      }
      .bz-cartes {
        position: absolute;
        left: 120px;
        top: 790px;
        display: flex;
        gap: 50px;
      }
      .bz-carte {
        width: 527px;
        border-radius: 26px;
        background: #19191d;
        overflow: hidden;
      }
      .bz-carte-img {
        height: 340px;
        overflow: hidden;
      }
      .bz-carte-img img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .bz-carte b {
        display: block;
        margin: 24px 30px 6px;
        font-family: "Inter", sans-serif;
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
      }
      .bz-carte span {
        display: block;
        margin: 0 30px 28px;
        font-family: "Inter", sans-serif;
        font-size: 36px;
        font-weight: 700;
        color: var(--bz);
      }
      .bz-widget {
        position: absolute;
        left: 1000px;
        top: 200px;
        width: 820px;
        background: #ffffff;
        border-radius: 28px;
        padding: 36px 44px 40px;
        font-family: "Inter", sans-serif;
        color: #0c0c0c;
        box-shadow: 0 40px 120px rgba(0, 0, 0, 0.7);
        z-index: 5;
      }
      .bz-w-tete {
        font-size: 52px;
        font-weight: 900;
        margin-bottom: 22px;
      }
      .bz-champ {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 22px;
        margin-bottom: 14px;
        border: 3px solid #e2e2e2;
        border-radius: 14px;
        font-size: 38px;
      }
      .bz-champ span {
        color: #777;
        font-weight: 600;
      }
      .bz-champ b {
        font-weight: 800;
      }
      .bz-w-btn {
        margin-top: 22px;
        text-align: center;
        padding: 22px 0;
        border-radius: 16px;
        background: #0c0c0c;
        color: #ffffff;
        font-size: 40px;
        font-weight: 800;
      }
      .bz-w-img {
        position: relative;
        height: 420px;
        border-radius: 18px;
        overflow: hidden;
      }
      .bz-w-img img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .bz-360 {
        position: absolute;
        right: 20px;
        bottom: 20px;
        font-style: normal;
        background: #0c0c0c;
        color: #ffffff;
        font-size: 40px;
        font-weight: 900;
        padding: 10px 22px;
        border-radius: 40px;
      }
      .bz-tarifs p,
      .bz-suivi p,
      .bz-avis p {
        display: flex;
        justify-content: space-between;
        padding: 16px 0;
        border-bottom: 2px solid #ececec;
        font-size: 40px;
        font-weight: 600;
      }
      .bz-avis p {
        font-size: 34px;
      }
      .bz-creneaux {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
      }
      .bz-creneaux i {
        font-style: normal;
        text-align: center;
        padding: 22px 0;
        border: 3px solid #e2e2e2;
        border-radius: 14px;
        font-size: 40px;
        font-weight: 800;
      }
      .bz-barre {
        margin-top: 22px;
        height: 30px;
        border-radius: 15px;
        background: #ececec;
        overflow: hidden;
      }
      .bz-barre i {
        display: block;
        height: 100%;
        background: #0c0c0c;
        transform-origin: 0% 50%;
        transform: scaleX(0);
      }
      /* ---- vidéo 13 : mystère et types de sites ---- */
      .pj-logo img {
        object-fit: contain;
      }
      .my-nuit {
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse 34% 46% at 50% 44%, rgba(6, 6, 8, 0.2) 0%, rgba(6, 6, 8, 0.93) 100%);
      }
      .my-carte {
        position: absolute;
        transform-style: preserve-3d;
      }
      .my-face {
        position: absolute;
        inset: 0;
        border-radius: 36px;
        backface-visibility: hidden;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 40px 120px rgba(0, 0, 0, 0.8);
      }
      .my-dos {
        background: repeating-linear-gradient(-45deg, #141414 0 26px, #0c0c0c 26px 52px);
        border: 6px solid #dcfc1c;
      }
      .my-dos b {
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 380px;
        line-height: 1;
        color: #dcfc1c;
        text-shadow:
          -8px 0 rgba(0, 229, 255, 0.7),
          8px 0 rgba(255, 46, 99, 0.7),
          0 0 80px rgba(220, 252, 28, 0.5);
        margin-bottom: 90px;
      }
      .my-avant {
        background: #dcfc1c;
        transform: rotateY(180deg);
        padding: 0 30px;
      }
      .my-avant b {
        font-family: "Anton", sans-serif;
        font-weight: 400;
        line-height: 1;
        color: #0c0c0c;
        text-transform: uppercase;
        text-align: center;
      }
      .my-num {
        position: absolute;
        top: 34px;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 34px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #ecece8;
      }
      .my-avant .my-num {
        color: #0c0c0c;
      }
      .my-mini {
        position: absolute;
        width: 260px;
        height: 420px;
        border-radius: 26px;
        border: 5px solid #dcfc1c;
        background: repeating-linear-gradient(-45deg, #141414 0 20px, #0c0c0c 20px 40px);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.75);
      }
      .my-mini span {
        position: absolute;
        top: 22px;
        left: 0;
        right: 0;
        text-align: center;
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 26px;
        color: #ecece8;
        text-transform: uppercase;
      }
      .my-mini b {
        position: absolute;
        top: 64px;
        left: 0;
        right: 0;
        text-align: center;
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 200px;
        line-height: 1;
        color: #dcfc1c;
      }
      .ty-base {
        position: absolute;
        inset: 0;
        background: #f4f4f0;
      }
      .ty-logo {
        position: absolute;
        left: 40px;
        top: 30px;
        display: flex;
        align-items: center;
        gap: 14px;
        font-family: "Anton", sans-serif;
        font-size: 44px;
        color: #0c0c0c;
      }
      .ty-logo i {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: #0c0c0c;
      }
      .ty-menu {
        position: absolute;
        right: 40px;
        top: 44px;
        display: flex;
        gap: 18px;
      }
      .ty-menu span {
        width: 80px;
        height: 14px;
        border-radius: 7px;
        background: #c9c9c4;
      }
      .ty-imgs {
        position: absolute;
        left: 40px;
        right: 40px;
        top: 130px;
        display: flex;
        gap: 20px;
      }
      .ty-im {
        flex: 1;
        height: 180px;
        border-radius: 14px;
        overflow: hidden;
      }
      .ty-im img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .ty-btn {
        position: absolute;
        left: 240px;
        top: 360px;
        width: 320px;
        padding: 22px 0;
        text-align: center;
        border-radius: 40px;
        background: #0c0c0c;
        color: #ffffff;
        font-family: "Inter", sans-serif;
        font-size: 30px;
        font-weight: 800;
      }
      .ty-etiq {
        position: absolute;
        padding: 6px 26px;
        background: #dcfc1c;
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-size: 72px;
        line-height: 1.1;
        text-transform: uppercase;
        transform: rotate(-4deg);
        box-shadow: 10px 10px 0 #0c0c0c;
      }
      .ty-q {
        position: absolute;
        left: 80px;
        top: 40px;
        font-family: "Anton", sans-serif;
        font-size: 640px;
        line-height: 1;
        color: #dcfc1c;
        text-shadow:
          -10px 0 rgba(0, 229, 255, 0.7),
          10px 0 rgba(255, 46, 99, 0.7),
          0 0 90px rgba(220, 252, 28, 0.5);
      }
      .ty-cv {
        position: absolute;
        left: 150px;
        top: 380px;
        width: 560px;
        height: 320px;
        padding: 40px 44px;
        box-sizing: border-box;
        border-radius: 22px;
        background: #f6f3ea;
        color: #0c0c0c;
        font-family: "Inter", sans-serif;
        box-shadow: 0 40px 100px rgba(0, 0, 0, 0.7);
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
      .ty-cv b {
        font-family: "Anton", sans-serif;
        font-weight: 400;
        font-size: 64px;
        line-height: 1;
        margin-bottom: 14px;
      }
      .ty-cv span {
        font-size: 30px;
        font-weight: 600;
        color: #4a4a4a;
      }
      .ty-cv em {
        margin-top: auto;
        font-style: normal;
        font-size: 30px;
        font-weight: 800;
      }
      .ty-galerie {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
      }
      .ty-galerie img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
      }
      .ty-panier {
        position: absolute;
        left: 1330px;
        top: 34px;
        width: 70px;
        height: 70px;
      }
      .ty-panier i {
        position: absolute;
        right: -10px;
        top: -10px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--bz);
        color: #0c0c0c;
        font-family: "Inter", sans-serif;
        font-style: normal;
        font-size: 26px;
        font-weight: 900;
        text-align: center;
        line-height: 40px;
      }
      .ty-vol {
        position: absolute;
        left: 283px;
        top: 420px;
        width: 200px;
        height: 140px;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        z-index: 6;
      }
      .ty-vol img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .ty-etapes p {
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 14px 0;
        font-size: 40px;
        font-weight: 700;
        color: #8a8a8a;
      }
      .ty-etapes p::before {
        content: "";
        width: 26px;
        height: 26px;
        border-radius: 50%;
        border: 4px solid #c9c9c9;
      }
      .ty-etapes p.ok {
        color: #0c0c0c;
      }
      .ty-etapes p.ok::before {
        background: #1fbf63;
        border-color: #1fbf63;
      }
      .ty-msg b {
        display: block;
        font-size: 40px;
        font-weight: 900;
        margin-bottom: 10px;
      }
      .ty-msg p {
        font-size: 38px;
        line-height: 1.35;
        color: #333333;
      }
      .ty-gros {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin: 10px 0;
      }
      .ty-gros b {
        font-size: 104px;
        font-weight: 900;
        line-height: 1;
      }
      .ty-gros span {
        font-size: 34px;
        font-weight: 600;
        color: #6a6a6a;
      }
      .ty-graphe {
        display: flex;
        align-items: flex-end;
        gap: 18px;
        height: 260px;
        padding-bottom: 6px;
        border-bottom: 3px solid #e2e2e2;
      }
      .ty-graphe i {
        flex: 1;
        border-radius: 10px 10px 0 0;
        background: #0c0c0c;
        transform-origin: 50% 100%;
      }
      .ty-graphe i:last-child {
        background: #1fbf63;
      }
      .ty-hausse {
        margin-top: 18px;
        font-size: 46px;
        font-weight: 900;
        color: #11994d;
      }
      .ty-stores {
        display: flex;
        gap: 18px;
        margin-bottom: 18px;
      }
      .ty-stores span {
        padding: 20px 32px;
        border-radius: 16px;
        background: #0c0c0c;
        color: #ffffff;
        font-size: 36px;
        font-weight: 800;
      }
      .ty-post img {
        width: 100%;
        height: 300px;
        object-fit: cover;
        border-radius: 14px;
      }
      .ty-post p {
        display: flex;
        justify-content: space-between;
        margin-top: 16px;
        font-size: 36px;
        font-weight: 700;
      }
      .ty-post p b {
        color: #e8335f;
      }
      .ty-chat p {
        width: fit-content;
        max-width: 80%;
        margin: 12px 0;
        padding: 16px 26px;
        border-radius: 26px;
        background: #eeeeee;
        font-size: 36px;
        font-weight: 600;
      }
      .ty-chat p.r {
        margin-left: auto;
        background: var(--bz);
      }
      .ty-entonnoir {
        position: absolute;
        left: 160px;
        top: 330px;
        width: 400px;
        height: 520px;
      }
      .ty-entonnoir svg {
        position: absolute;
        left: 0;
        top: 120px;
      }
      .ty-ent-h,
      .ty-ent-b {
        position: absolute;
        left: 0;
        right: 0;
        display: flex;
        align-items: baseline;
        justify-content: center;
        gap: 14px;
        font-family: "Anton", sans-serif;
        text-transform: uppercase;
        color: #ecece8;
      }
      .ty-ent-h {
        top: 0;
      }
      .ty-ent-b {
        top: 400px;
      }
      .ty-ent-h b,
      .ty-ent-b b {
        font-weight: 400;
        font-size: 96px;
        line-height: 1;
      }
      .ty-ent-b b {
        color: #3dffa2;
      }
      .ty-ent-h span,
      .ty-ent-b span {
        font-size: 44px;
      }
      .ty-pt {
        position: absolute;
        top: 130px;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #ecece8;
      }
      .ty-cible {
        position: absolute;
        left: 250px;
        top: 360px;
        width: 300px;
        height: 300px;
      }
      .ty-cible i {
        position: absolute;
        border-radius: 50%;
        border: 14px solid #3dffa2;
      }
      .ty-cible i:nth-child(1) {
        inset: 0;
      }
      .ty-cible i:nth-child(2) {
        inset: 60px;
      }
      .ty-cible i:nth-child(3) {
        inset: 120px;
        background: #3dffa2;
      }
      .ty-niveau {
        position: absolute;
        left: 170px;
        top: 330px;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: "Anton", sans-serif;
        text-transform: uppercase;
      }
      .ty-niveau span {
        font-size: 64px;
        color: #ecece8;
      }
      .ty-niveau b {
        font-weight: 400;
        font-size: 230px;
        line-height: 1;
        color: #ff5fa2;
        text-shadow: 0 0 70px rgba(255, 95, 162, 0.6);
      }
      .ty-lab {
        position: absolute;
        left: 18px;
        bottom: 18px;
        padding: 4px 18px;
        background: #dcfc1c;
        color: #0c0c0c;
        font-family: "Anton", sans-serif;
        font-size: 44px;
        line-height: 1.1;
        text-transform: uppercase;
      }
      .ty-grande-q {
        position: absolute;
        left: 0;
        width: 1920px;
        top: 250px;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: "Anton", sans-serif;
        text-transform: uppercase;
        line-height: 1.02;
      }
      .ty-grande-q span {
        font-size: 150px;
        color: #ffffff;
        white-space: nowrap;
      }
      .ty-grande-q span:last-child {
        color: #dcfc1c;
        text-shadow:
          -7px 0 rgba(0, 229, 255, 0.75),
          7px 0 rgba(255, 46, 99, 0.75),
          0 0 60px rgba(220, 252, 28, 0.45);
      }
      /* ---- styles générés : fin ---- */
"""


def ecrire_index():
    f = ICI / "index.html"
    h = f.read_text(encoding="utf-8")
    h = re.sub(r"      /\* ---- (clavier-ia|styles générés) : début.*?/\* ---- (clavier-ia|styles générés) : fin ---- \*/\n", "", h, flags=re.S)
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
               f'      <div id="volets" data-composition-id="volets" data-composition-src="compositions/volets.html"\n'
               f'        data-start="0" data-duration="{FIN}" data-track-index="5" data-track-kind="graphics"\n'
               f'        data-width="1920" data-height="1080" style="z-index: 45"></div>',
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
    bloc = "\n".join(f"    masquer({round(a, 2)}, {round(c, 2)}); // {n}" for a, c, n in MASQUES) or "    // aucune carte plein écran"
    h = re.sub(r"(    function masquer\(debut, fin\) \{\n.*?\n    \}\n)(.*?)(    window\.__timelines)", lambda m: m.group(1) + bloc + "\n" + m.group(3),
               h, count=1, flags=re.S)
    f.write_text(h, encoding="utf-8")


def ecrire_volets():
    """Volet rayé (orange / bleu nuit) qui balaie l'image à chaque coupe et cache le raccord."""
    bandes, js = [], []
    for k, c in enumerate(COUPES[1:-1]):
        bandes.append(f'    <div id="vo-{k}" class="vo-bande"><i class="vo-r"></i><i class="vo-p"></i><i class="vo-r"></i></div>')
        js.append(f'    tl.fromTo("#vo-{k}", {{ x: 0 }}, {{ x: 5100, duration: 0.46, ease: "power2.inOut", immediateRender: false }}, {round(c - 0.23, 3)});')
    page = f"""<!-- Volets de transition du style « Alerte » (écrit par tools/construire-scenes.py). -->
<template>
  <style>
    #root {{
      position: absolute;
      inset: 0;
      overflow: hidden;
      pointer-events: none;
    }}
    .vo-bande {{
      position: absolute;
      left: -2700px;
      top: -300px;
      width: 2300px;
      height: 1680px;
      display: flex;
      transform: skewX(-18deg);
    }}
    .vo-r {{
      width: 170px;
      background: repeating-linear-gradient(-45deg, #dcfc1c 0 32px, #0c0c0c 32px 64px);
    }}
    .vo-p {{
      flex: 1;
      background: #0c0c0c;
    }}
  </style>
  <div id="root" data-composition-id="volets" data-width="1920" data-height="1080">
{chr(10).join(bandes)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["volets"] = tl;
  </script>
</template>
"""
    (ICI / "compositions/volets.html").write_text(page, encoding="utf-8")


def ecrire_check():
    """Les 6 types SOUS le film, dans la version verticale (../types-de-sites-vertical/index.html), en MYSTÈRE :
    6 cases verrouillées « ? » ; chacune se retourne et dévoile son nom au moment où la voix le dit, puis se valide."""
    cases, js = [], []
    cad = ('<svg class="ck-cad" viewBox="0 0 120 150" width="34" height="42"><path d="M30 70 L30 42 Q30 12 60 12 Q90 12 90 42 L90 70" fill="none" stroke="#ECECE8" stroke-width="14" stroke-linecap="round" />'
           '<rect x="14" y="66" width="92" height="76" rx="14" fill="#DCFC1C" /></svg>')
    for k, (m, g_act, g_ok) in enumerate(CHECK):
        cases.append(f'        <div id="ck-{k}" class="ck-case"><b>{k + 1}</b><span id="ck-q{k}" class="ck-q">?</span><span id="ck-n{k}" class="ck-nom" style="opacity: 0">{m}</span>'
                     f'<i id="ck-c{k}" class="ck-c">{cad}</i><i id="ck-v{k}" class="ck-v">{COCHE.format(w=34, c="#0C0C0C")}</i></div>')
        js.append(f'      tl.to("#ck-{k}", {{ keyframes: [{{ x: -6, duration: 0.05 }}, {{ x: 6, duration: 0.05 }}, {{ x: -4, duration: 0.05 }}, {{ x: 0, duration: 0.05 }}] }}, {round(g_act - 0.9, 3)});')
        js.append(f'      tl.to("#ck-{k}", {{ rotationY: 360, transformPerspective: 800, duration: 0.4, ease: "power3.inOut" }}, {round(g_act - 0.05, 3)});')
        js.append(f'      tl.set("#ck-q{k}", {{ opacity: 0 }}, {round(g_act + 0.15, 3)});')
        js.append(f'      tl.set("#ck-c{k}", {{ opacity: 0 }}, {round(g_act + 0.15, 3)});')
        js.append(f'      tl.set("#ck-n{k}", {{ opacity: 1 }}, {round(g_act + 0.15, 3)});')
        js.append(f'      tl.set("#ck-{k}", {{ backgroundImage: "none" }}, {round(g_act + 0.15, 3)});')
        js.append(f'      tl.to("#ck-{k}", {{ borderColor: "#DCFC1C", backgroundColor: "rgba(220, 252, 28, 0.3)", scale: 1.08, duration: 0.18 }}, {round(g_act + 0.15, 3)});')
        js.append(f'      tl.to("#ck-{k}", {{ borderColor: "#DCFC1C", backgroundColor: "#DCFC1C", color: "#0C0C0C", scale: 1, duration: 0.16 }}, {round(g_ok - 0.05, 3)});')
        js.append(f'      tl.fromTo("#ck-v{k}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.in", immediateRender: false }}, {round(g_ok - 0.05, 3)});')
    js.append(f'      tl.fromTo("#ck-barre", {{ opacity: 0, y: 80 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.8)" }}, {round(CHECK_DEBUT, 3)});')
    js.append(f'      tl.fromTo(".ck-case", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)", stagger: 0.2, immediateRender: false }}, {round(CHECK_DEBUT, 3)});')
    largeur = round((1028 - 12 * (len(CHECK) - 1)) / len(CHECK))
    css = """      @font-face {
        font-family: "Anton";
        src: url("assets/fonts/Anton-Regular.woff2") format("woff2");
        font-weight: 400;
      }
      #ck-barre {
        position: absolute;
        left: 26px;
        top: 1318px;
        width: 1028px;
      }
      #ck-tete {
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 30px;
        letter-spacing: 0.15em;
        color: #dcfc1c;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 18px;
      }
      #ck-cases {
        display: flex;
        gap: 12px;
      }
      .ck-case {
        position: relative;
        width: 248px;
        height: 150px;
        border: 4px solid #3a4462;
        background: repeating-linear-gradient(-45deg, #141414 0 14px, #0c0c0c 14px 28px);
        color: #ecece8;
        font-family: "Anton", sans-serif;
        text-transform: uppercase;
        box-sizing: border-box;
      }
      .ck-case b {
        position: absolute;
        left: 12px;
        top: 6px;
        font-weight: 400;
        font-size: 40px;
        line-height: 1;
      }
      .ck-q {
        position: absolute;
        left: 0;
        right: 0;
        top: 22px;
        text-align: center;
        font-size: 96px;
        line-height: 1;
        color: #dcfc1c;
      }
      .ck-nom {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 16px;
        text-align: center;
        font-size: 30px;
        line-height: 1;
        white-space: nowrap;
      }
      .ck-c {
        position: absolute;
        right: 8px;
        top: 8px;
      }
      .ck-v {
        position: absolute;
        right: 8px;
        top: 8px;
        opacity: 0;
      }
""".replace("width: 248px;", f"width: {largeur}px;")
    html = (f'      <div id="ck-barre" class="clip" data-start="0" data-duration="{FIN}" data-track-index="3" style="opacity: 0">\n'
            f'        <div id="ck-tete">{CHECK_TITRE}</div>\n        <div id="ck-cases">\n' + "\n".join("  " + c for c in cases) +
            "\n        </div>\n      </div>")
    f = ICI.parent / "types-de-sites-vertical/index.html"
    h = f.read_text(encoding="utf-8")
    h = re.sub(r"(      /\* check : début \*/\n).*?(      /\* check : fin \*/)", lambda m: m.group(1) + css + m.group(2), h, flags=re.S)
    h = re.sub(r"(      <!-- check : début -->\n).*?(      <!-- check : fin -->)", lambda m: m.group(1) + html + "\n" + m.group(2), h, flags=re.S)
    h = re.sub(r"(      // check : début\n).*?(      // check : fin)", lambda m: m.group(1) + "\n".join(js) + "\n" + m.group(2), h, flags=re.S)
    f.write_text(h, encoding="utf-8")


def couleurs_alerte():
    """Remplace l'accent vert-jaune du style « Projecteur » par l'orange du style « Alerte » dans les scènes."""
    for f in (ICI / "compositions").glob("s*.html"):
        h = f.read_text(encoding="utf-8")
        h = h.replace("#DCFC1C", ACCENT).replace("#dcfc1c", ACCENT).replace("rgba(220, 252, 28", "rgba(220, 252, 28")
        f.write_text(h, encoding="utf-8")
    st = ICI / "compositions/sous-titres.html"
    h = st.read_text(encoding="utf-8")
    if "style Alerte" not in h:
        h = h.replace("    .st-mot {\n", "    /* style Alerte */\n    .st-bandeau {\n      box-shadow: 10px 10px 0 #dcfc1c;\n      transform: skewX(-6deg);\n    }\n    .st-mot {\n", 1)
        st.write_text(h, encoding="utf-8")


for nom in NOMS:
    contenu = (ICI / "compositions" / f"{nom}.html").read_text(encoding="utf-8")
    assert not re.search(rf'(?<![-\w])id="{nom}"|"#{nom}"', contenu), f"un élément porte l'identifiant de la scène {nom}"
ecrire_volets()
ecrire_check()
n = ecrire_index()
ecrire_cadre()
print(f"{len(NOMS)} scènes écrites, {n} bruitages placés, fin à {FIN} s")
