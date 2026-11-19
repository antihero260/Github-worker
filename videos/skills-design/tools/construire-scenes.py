#!/usr/bin/env python3
"""Écrit les 9 scènes de « skills-design » (5 skills GitHub pour un design qui sort du lot), le montage et le cadre.

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
VOL_SFX = 1.0  # bruitages au même niveau que la vidéo 3 (l'utilisateur : « les bruitages sont bons »)


def b(i):
    """Coupure de scène juste avant le mot i."""
    return round(t_mot(i) - 0.12, 2)


FIN = 60.6
COUPES = [0] + [b(i) for i in (14, 27, 35, 42, 66, 92, 109, 130)] + [FIN]
NOMS = ["s01-rafale", "s02-tous-pareils", "s03-noye", "s04-cinq-skills", "s05-frontend-design", "s06-ui-ux-pro-max",
        "s07-shadcn", "s08-taste-skill", "s09-emil"]
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
    s.j(f'tl.fromTo("{sel}", {{ boxShadow: "0 0 0px rgba(220, 252, 28, 0)" }}, {{ boxShadow: "0 0 50px rgba(220, 252, 28, 0.9)", duration: 0.25, '
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
        self.s.j(f'tl.fromTo("#{self.tid}-c{r}", {{ boxShadow: "inset 0 0 0px rgba(220, 252, 28, 0)" }}, '
                 f'{{ boxShadow: "inset 0 0 0 6px rgba(220, 252, 28, 0.9)", duration: {d}, immediateRender: false }}, {self.s.L(g)});')
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


# ================================================================ SCÈNES
# ---------------------------------------------------------------- S1 : rafale de sites générés par l'IA
s = scene(0, "Scène 1 · « Tu viens de créer ton site avec l'IA. Il fonctionne, il est même joli… »")
d1 = round(s.fin - s.debut, 2)
rafale(s, "s01-r", 0.0, 0.24, d1)
cam(s, perso("s01-toi", 960, 800, 300))
vit(s, "s01-toi", 0, s.fin - 0.2)
pose(s, "s01-toi", t_mot(9), 0.16, "back.out(2)", bd=-150, bg=150)
saut(s, "s01-toi", t_mot(9), 30)
pouce(s, "s01-toi", t_mot(12))
s.j(f'tl.fromTo("#s01-cam", {{ x: 0 }}, {{ keyframes: [{{ x: -12, duration: 0.05 }}, {{ x: 10, duration: 0.05 }}, {{ x: -6, duration: 0.05 }}, {{ x: 0, duration: 0.05 }}], immediateRender: false }}, {s.L(1.0)});')
zoom(s, t_mot(10), 960, 520, 1.15)
s.ecrire()

# ---------------------------------------------------------------- S2 : tous pareils
s = scene(1, "Scène 2 · « …mais il ressemble à des milliers d'autres : mêmes structures, mêmes cartes, mêmes dégradés. »")
mur(s, "s02-m", 6, 5, 70, 110, 290, 16, t_mot(16), 0.035)
for k, (m, i, x, y) in enumerate((("Mêmes structures", 22, 220, 260), ("Mêmes cartes", 24, 760, 470), ("Mêmes dégradés", 26, 1200, 680))):
    tampon(s, f"s02-t{k}", m, x, y, t_mot(i), (-6, 4, -3)[k], 84)
    son(t_mot(i), tour(["impact-basse", "impact-cartoon", "impact-futur"]), 0.5, m)
s.add(hud_g("s02-hud", "Des milliers", "Tous pareils"))
son(t_mot(16), "glitch-data", 0.3, "le mur apparaît")
son(t_mot(19), "parasite-whoosh", 0.38, "des milliers")
zoom(s, t_mot(19), 960, 540, 0.85, nom="zoom-out")
zoom(s, t_mot(22) - 0.1, 500, 330, 1.25)
s.cache("#s02-t0", t_mot(24) - 0.15)
zoom(s, t_mot(24) - 0.1, 1000, 520, 1.25)
s.cache("#s02-t1", t_mot(26) - 0.15)
zoom(s, t_mot(26) - 0.1, 1420, 720, 1.25)
s.ecrire()

# ---------------------------------------------------------------- S3 : ton site se noie dans la masse
s = scene(2, "Scène 3 · « Résultat : ton site se noie dans la masse. »")
mur(s, "s03-m", 9, 7, 30, 60, 196, 10, s.debut, 0.008, accent=31)
cam(s, perso("s03-toi", 1700, 800, 320))
tampon(s, "s03-noye-t", "Noyé dans la masse", 560, 420, t_mot(31), -5, 96)
s.add(hud_g("s03-hud", "Résultat", "Invisible"))
vit(s, "s03-toi", s.debut, s.fin - 0.2)
zoom(s, s.debut + 0.05, 960, 470, 1.6)
son(t_mot(27), "swell-court", 0.35, "résultat")
zoom(s, t_mot(30) - 0.1, 960, 540, 0.9, nom="zoom-out")
s.j(f'tl.to("#s03-m-31", {{ scale: 0.4, opacity: 0.3, duration: 0.6, ease: "power2.in" }}, {s.L(t_mot(31))});')
son(t_mot(31), "impact-basse", 0.55, "noyé")
chute(s, "s03-toi", t_mot(32), 500, 25)
son(t_mot(32), "souffle-cine", 0.4, "il tombe")
s.ecrire()

# ---------------------------------------------------------------- S4 : 5 skills GitHub
s = scene(3, "Scène 4 · « Voici cinq skills GitHub pour éviter ça. »")
cam(s, carte_logo("s04-gh", "github", 860, 150, 200))
cam(s, '<div id="s04-t" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 430px; text-align: center; font-size: 170px; opacity: 0">5 skills GitHub</div>')
for k, v in enumerate(("frontend-design-haut", "ui-ux-pro-max-haut", "shadcn-haut", "taste-skill-haut", "emil-design-eng-haut")):
    cam(s, f'<div id="s04-c{k}" class="pj-tuile-site" style="left: {113 + k * 345}px; top: 650px; width: 320px; height: 180px; opacity: 0">'
           f'<img src="assets/img/gh-{v}.jpg" alt="" /><b class="pj-num">{k + 1}</b></div>')
cam(s, perso("s04-toi", 1760, 600, 260))
s.add(hud_g("s04-hud", "La solution", "5 skills"))
s.claque("#s04-gh", t_mot(37), 1.8)
son(t_mot(37), "power-up", 0.45, "GitHub")
s.choc("#s04-t", t_mot(36))
s.eclair(t_mot(36))
son(t_mot(36), "impact-whoosh", 0.55, "5 SKILLS")
for k in range(5):
    s.claque(f"#s04-c{k}", t_mot(39) + k * 0.12, 1.5)
    son(t_mot(39) + k * 0.12, tour(POPS), 0.4, f"skill {k + 1}")
victoire(s, "s04-toi", t_mot(38), 2)
zoom(s, t_mot(39) - 0.1, 960, 600, 1.1)
s.ecrire()

# ---------------------------------------------------------------- S5 : 1. Frontend Design
s = scene(4, "Scène 5 · « 1. Frontend Design : une véritable direction artistique, une identité visuelle… pas un simple template. »")
badge5(s, "s05-b", 1, t_mot(42))
titre_skill(s, "s05-titre", "Frontend Design", "anthropics/skills", "187 k", t_mot(43))
ecran(s, "s05-gh", 113, 400, 760, 428, "gh-frontend-design", "GitHub · la vraie page")
ecran(s, "s05-md", 1060, 330, 760, 428, "gh-fd-skillmd", "SKILL.md")
panneau(s, "s05-art", 1060, 330, 760, 428, ("video", "graphiste", 0, round(s.fin - s.debut, 2)), "Direction artistique", piste=7)
cam(s, f'<div id="s05-tpl" class="pj-tuile-site" style="left: 1200px; top: 380px; width: 480px; height: 270px; opacity: 0"><img src="assets/img/site-ia-2-0.3.jpg" alt="" /></div>')
cam(s, '<div id="s05-x" class="pj-x" style="left: 1200px; top: 380px; width: 480px; height: 270px; opacity: 0"></div>')
guide(s, "s05-toi", t_mot(43) + 0.3, t_mot(45) + 0.1, t_mot(53), t_mot(64))
s.add(hud_g("s05-hud", "Skill 1", "Une vraie identité"))
s.apparait("#s05-gh", t_mot(43) + 0.2, 40)
son(t_mot(43) + 0.2, "declencheur", 0.4, "capture GitHub")
s.apparait("#s05-md", t_mot(45), 40)
son(t_mot(45), "swoosh-monte", 0.4, "SKILL.md")
zoom(s, t_mot(45) - 0.1, 1385, 540, 1.2)
s.cache("#s05-md", t_mot(52) - 0.1)
s.apparait("#s05-art", t_mot(52), 40)
son(t_mot(52), "magie", 0.4, "direction artistique")
zoom(s, t_mot(56) - 0.1, 1385, 540, 1.3)
s.claque("#s05-tpl", t_mot(63), 1.5)
s.croix("#s05-x", t_mot(65))
son(t_mot(65), "buzz-faux", 0.42, "pas un template")
zoom(s, t_mot(63) - 0.1, 1390, 475, 1.25)
s.ecrire()

# ---------------------------------------------------------------- S6 : 2. UI/UX Pro Max
s = scene(5, "Scène 6 · « 2. UI/UX Pro Max : des centaines de styles, de palettes de couleurs et de typographies… »")
badge5(s, "s06-b", 2, t_mot(66))
titre_skill(s, "s06-titre", "UI/UX Pro Max", "nextlevelbuilder/ui-ux-pro-max-skill", "146 k", t_mot(67))
ecran(s, "s06-site", 113, 380, 760, 428, "gh-uupm-site", "uupm.cc · le vrai site")
ecran(s, "s06-gh", 1060, 330, 760, 428, "gh-ui-ux-pro-max", "GitHub")
nuancier(s, "s06-n", 1070, 540, t_mot(79))
typos = (("Anton", "Aa", ""), ("Instrument Serif", "Aa", "font-style: italic;"), ("JetBrains Mono", "Aa", ""), ("Inter", "Aa", "font-weight: 700;"))
for k, (f, t, st) in enumerate(typos):
    cam(s, f'<div id="s06-f{k}" class="pj-typo" style="left: {1065 + k * 190}px; top: 300px; font-family: \'{f}\', sans-serif; {st} opacity: 0">{t}<span>{f}</span></div>')
puce(s, "s06-p", "Des centaines de styles", 1410, 270, t_mot(75), "font-size: 46px")
guide(s, "s06-toi", t_mot(67) + 0.4, t_mot(70) + 0.1, t_mot(77), t_mot(90))
s.add(hud_g("s06-hud", "Skill 2", "Styles, couleurs, typos"))
s.apparait("#s06-site", t_mot(67) + 0.3, 40)
son(t_mot(67) + 0.3, "declencheur", 0.4, "capture du site")
s.apparait("#s06-gh", t_mot(70), 40)
son(t_mot(70), "swoosh-monte", 0.38, "dépôt GitHub")
son(t_mot(75), "pop-bulle", 0.4, "centaines de styles")
s.cache("#s06-gh", t_mot(79) - 0.15)
s.cache("#s06-p", t_mot(79) - 0.15)
for k in range(0, 8, 2):
    son(t_mot(79) + k * 0.05, tour(["pop-click", "pop-sec", "pop-long"]), 0.35, "couleur")
zoom(s, t_mot(79) - 0.1, 1360, 700, 1.25)
for k in range(4):
    s.claque(f"#s06-f{k}", t_mot(86) + k * 0.1, 1.6)
    son(t_mot(86) + k * 0.1, tour(["pop-bulle", "pop-cartoon"]), 0.38, "typo")
zoom(s, t_mot(86) - 0.1, 1420, 400, 1.2)
zoom(s, t_mot(90), 960, 540, 1.0)
s.ecrire()

# ---------------------------------------------------------------- S7 : 3. shadcn
s = scene(6, "Scène 7 · « 3. shadcn : choisir, assembler et personnaliser des composants d'interface… »")
badge5(s, "s07-b", 3, t_mot(92))
titre_skill(s, "s07-titre", "shadcn", "shadcn-ui/ui · skills/shadcn", "127 k", t_mot(93))
ecran(s, "s07-site", 113, 380, 760, 428, "gh-shadcn-site", "ui.shadcn.com")
ecran(s, "s07-md", 1060, 330, 760, 428, "gh-shadcn-skillmd", "SKILL.md officiel")
comps = ('<div class="pj-c-btn">Bouton</div>', '<div class="pj-c-input">Ton e-mail…</div>',
         '<div class="pj-c-card"><b>Carte</b><span>Composant assemblé</span></div>')
for k, c in enumerate(comps):
    cam(s, f'<div id="s07-c{k}" style="position: absolute; left: {1060 + k * 0}px; top: {330 + k * 130}px; opacity: 0">{c}</div>')
for k, (m, i) in enumerate((("Choisir", 96), ("Assembler", 97), ("Personnaliser", 99))):
    puce(s, f"s07-p{k}", m, 1650, 380 + k * 110, t_mot(i), "font-size: 44px")
guide(s, "s07-toi", t_mot(93) + 0.4, t_mot(94) + 0.1, t_mot(99), t_mot(106))
s.add(hud_g("s07-hud", "Skill 3", "Des composants harmonieux"))
s.apparait("#s07-site", t_mot(93) + 0.3, 40)
son(t_mot(93) + 0.3, "declencheur", 0.4, "capture du site")
s.apparait("#s07-md", t_mot(94), 40)
son(t_mot(94), "swoosh-monte", 0.38, "SKILL.md")
zoom(s, t_mot(94), 1410, 530, 1.2)
s.cache("#s07-md", t_mot(96) - 0.15)
for k, i in enumerate((96, 97, 99)):
    s.j(f'tl.fromTo("#s07-c{k}", {{ opacity: 0, x: 300, rotation: 8 }}, {{ opacity: 1, x: 0, rotation: 0, duration: 0.25, ease: "back.out(1.8)" }}, {s.L(t_mot(i))});')
    son(t_mot(i), tour(["clic-positif", "bouton-tech", "interrupteur"]), 0.42, "composant")
    son(t_mot(i) + 0.1, "pop-click", 0.3, "étiquette")
s.j(f'tl.to(".pj-c-btn", {{ backgroundColor: "#DCFC1C", color: "#000000", duration: 0.2 }}, {s.L(t_mot(99) + 0.3)});')
zoom(s, t_mot(96) - 0.1, 1350, 480, 1.2)
son(t_mot(108), "notif-positive", 0.4, "harmonieux")
zoom(s, t_mot(106), 960, 540, 1.0)
s.ecrire()

# ---------------------------------------------------------------- S8 : 4. Taste Skill
s = scene(7, "Scène 8 · « 4. Taste Skill : sortir des designs génériques… choix esthétiques et références visuelles. »")
badge5(s, "s08-b", 4, t_mot(109))
titre_skill(s, "s08-titre", "Taste Skill", "Leonxlnx/taste-skill", "111 k", t_mot(110))
ecran(s, "s08-site", 113, 380, 760, 428, "gh-taste-site", "tasteskill.dev")
ecran(s, "s08-gh", 1060, 330, 760, 428, "gh-taste-skill", "GitHub")
for k in range(3):
    cam(s, f'<div id="s08-g{k}" class="pj-tuile-site" style="left: {1040 + k * 70}px; top: {340 + k * 50}px; width: 420px; height: 236px; opacity: 0"><img src="assets/img/site-ia-{k * 3}-0.3.jpg" alt="" /></div>')
refs = ("gh-taste-site-bas", "gh-uupm-site-haut", "gh-shadcn-site-haut", "gh-emil-site-haut")
for k, r in enumerate(refs):
    cam(s, f'<div id="s08-r{k}" class="pj-photo" style="left: {1060 + (k % 2) * 390}px; top: {290 + (k // 2) * 250}px; transform: rotate({(-4, 3, 2, -3)[k]}deg); opacity: 0">'
           f'<img src="assets/img/{r}.jpg" alt="" /></div>')
guide(s, "s08-toi", t_mot(110) + 0.4, t_mot(112) + 0.1, t_mot(119), t_mot(128))
s.add(hud_g("s08-hud", "Skill 4", "Du goût, des références"))
s.apparait("#s08-site", t_mot(110) + 0.3, 40)
son(t_mot(110) + 0.3, "declencheur", 0.4, "capture du site")
s.apparait("#s08-gh", t_mot(112), 40)
son(t_mot(112), "swoosh-monte", 0.38, "GitHub")
s.cache("#s08-gh", t_mot(116) - 0.15)
for k in range(3):
    s.claque(f"#s08-g{k}", t_mot(116) + k * 0.08, 1.4)
    s.j(f'tl.to("#s08-g{k}", {{ x: {900 + k * 100}, rotation: {20 + k * 10}, opacity: 0, duration: 0.4, ease: "power2.in" }}, {s.L(t_mot(119))});')
son(t_mot(116), "glitch-court", 0.4, "designs génériques")
son(t_mot(119), "souffle-rapide", 0.45, "génériques éjectés")
zoom(s, t_mot(116) - 0.1, 1350, 460, 1.15)
for k in range(4):
    s.claque(f"#s08-r{k}", t_mot(124) + k * 0.18, 1.5)
    son(t_mot(124) + k * 0.18, "declencheur", 0.38, "référence épinglée")
zoom(s, t_mot(128) - 0.1, 1420, 540, 1.15)
s.ecrire()

# ---------------------------------------------------------------- S9 : 5. Emil Design Engineering
s = scene(8, "Scène 9 · « 5. Emil Design Engineering : animations, transitions et micro-interactions… qualité professionnelle. »")
badge5(s, "s09-b", 5, t_mot(130))
titre_skill(s, "s09-titre", "Emil Design Eng.", "emilkowalski/skills", "54 k", t_mot(131))
ecran(s, "s09-md", 113, 380, 760, 428, "gh-emil-skillmd", "SKILL.md · emil-design-eng")
ecran(s, "s09-site", 1060, 330, 760, 428, "gh-emil-site", "Le site d'Emil Kowalski")
cam(s, '<div id="s09-toast" class="pj-toast" style="left: 1080px; top: 330px; opacity: 0"><b>✓</b> Enregistré avec succès</div>')
cam(s, '<div id="s09-btn" class="pj-c-btn" style="position: absolute; left: 1100px; top: 470px; opacity: 0">Publier</div>')
cam(s, '<div id="s09-inter" class="pj-inter" style="position: absolute; left: 1420px; top: 460px; opacity: 0"><i id="s09-rond"></i></div>')
tampon(s, "s09-pro", "Qualité pro", 1150, 640, t_mot(151), -5, 96)
guide(s, "s09-toi", t_mot(131) + 0.4, t_mot(134) + 0.1, t_mot(144), t_mot(149))
s.add(hud_g("s09-hud", "Skill 5", "Animations soignées"))
s.apparait("#s09-md", t_mot(131) + 0.3, 40)
son(t_mot(131) + 0.3, "declencheur", 0.4, "capture SKILL.md")
s.apparait("#s09-site", t_mot(134), 40)
son(t_mot(134), "swoosh-monte", 0.38, "site")
zoom(s, t_mot(134), 1410, 530, 1.15)
s.cache("#s09-site", t_mot(139) - 0.15)
s.j(f'tl.fromTo("#s09-toast", {{ opacity: 0, y: -80, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "elastic.out(1, 0.6)" }}, {s.L(t_mot(139))});')
son(t_mot(139), "notif-magique", 0.42, "animation")
s.j(f'tl.fromTo("#s09-btn", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.5)" }}, {s.L(t_mot(141))});')
s.j(f'tl.to("#s09-btn", {{ keyframes: [{{ scale: 0.9, duration: 0.08 }}, {{ scale: 1.06, duration: 0.12 }}, {{ scale: 1, duration: 0.14 }}] }}, {s.L(t_mot(141) + 0.6)});')
son(t_mot(141), "swoosh-accent", 0.4, "transition")
son(t_mot(141) + 0.6, "clic-positif", 0.42, "bouton")
s.apparait("#s09-inter", t_mot(144) - 0.1, 20)
s.j(f'tl.to("#s09-rond", {{ x: 96, duration: 0.3, ease: "back.out(2)" }}, {s.L(t_mot(144) + 0.3)});')
s.j(f'tl.to("#s09-inter", {{ backgroundColor: "{ACCENT}", duration: 0.15 }}, {s.L(t_mot(144) + 0.3)});')
son(t_mot(144) + 0.3, "interrupteur", 0.45, "micro-interaction")
zoom(s, t_mot(139) - 0.1, 1350, 480, 1.25)
son(t_mot(151), "impact-basse", 0.5, "QUALITÉ PRO")
zoom(s, t_mot(150), 960, 540, 1.0)
confettis(s, "s09-conf", t_mot(152), 1400, 520)
son(t_mot(152), "cloche-succes", 0.4, "final")
s.ecrire()

# ================================================================ SONS GÉNÉRAUX
for k, c in enumerate(COUPES[1:-1], start=1):
    son(c, tour(TRANSITIONS), 0.46, f"transition vers {NOMS[k]}")
son(t_mot(36), "riser-trailer", 0.3, "montée vers 5 SKILLS")
son(0.02, "scratch", 0.4, "ouverture")
son(0.05, "impact-whoosh", 0.5, "ouverture")

MUSIQUES = [  # (début, fichier, durée, volume) — 0,63 ≈ −21 LUFS (5–6 dB sous la voix, réglage validé)
    (0, "partie-1-hazy-after-hours", 12.9, 0.63),
    (12.4, "partie-2-house-02", 30.5, 0.63),
    (42.2, "partie-3-trap-electro", 18.4, 0.63),
]
MASQUES = []


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


for nom in NOMS:
    contenu = (ICI / "compositions" / f"{nom}.html").read_text(encoding="utf-8")
    assert not re.search(rf'(?<![-\w])id="{nom}"|"#{nom}"', contenu), f"un élément porte l'identifiant de la scène {nom}"
n = ecrire_index()
ecrire_cadre()
print(f"{len(NOMS)} scènes écrites, {n} bruitages placés, fin à {FIN} s")
