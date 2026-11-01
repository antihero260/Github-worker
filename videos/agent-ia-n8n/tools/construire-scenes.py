#!/usr/bin/env python3
"""Écrit les 27 scènes de « agent-ia-n8n » dans compositions/, le montage (index.html) et le cadre.

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


FIN = 130.3
COUPES = [0] + [b(i) for i in (19, 32, 45, 51, 55, 76, 87, 99, 112, 125, 134, 152, 168, 177, 189, 216, 221, 240, 246, 252, 267,
                                286, 308, 321, 333, 350)] + [FIN]
NOMS = ["s01-message", "s02-recherche", "s03-compte-rendu", "s04-science-fiction", "s05-agent-ia", "s06-a-z", "s07-etape1",
        "s08-create-agent", "s09-etape2", "s10-fournisseur", "s11-etape3", "s12-assistant", "s13-sources", "s14-etape4",
        "s15-agir", "s16-outil", "s17-etape5", "s18-botfather", "s19-workflow", "s20-publier", "s21-test", "s22-voila",
        "s23-bravo", "s24-verifier", "s25-imagine", "s26-exemples", "s27-executant"]
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


# ================================================================ SCÈNES
def demi(i):
    return round(t_mot(i) - 0.1, 2)


# ---------------------------------------------------------------- S1 : un simple message
s = scene(0, "Scène 1 · « Imagine que tu envoies simplement un message à ton téléphone : « Fais-moi un résumé… » »")
panneau(s, "s01-vid", 113, 230, 720, 405, ("video", "message-nuit", 0, round(s.fin - s.debut, 2)), "Toi, ce soir")
s.montre("#s01-vid", 0)
cam(s, perso("s01-toi", 1030, 800, 330))
telegram(s, "s01-tg", 1320, 100, "Mon assistant IA", [("m1", "moi", mots_bulle("s01-tg", "m1", 10, 18))])
s.add(hud_g("s01-hud", "Imagine", "Un simple message"))
vit(s, "s01-toi", 0, s.fin - 0.2)
pose(s, "s01-toi", t_mot(4), 0.16, "back.out(2)", bg=110, tete=6)
zoom(s, t_mot(5) - 0.1, 480, 430, 1.18)
pose(s, "s01-toi", t_mot(9), 0.12, bg=0, tete=0)
tape(s, "s01-toi", t_mot(10) - 0.1, t_mot(18) + 0.3)
ecrit_bulle(s, "s01-tg", "m1", 10, 18)
zoom(s, t_mot(10) - 0.15, 1530, 380, 1.3)
envoie(s, t_mot(18) + 0.55)
s.ecrire()

# ---------------------------------------------------------------- S2 : l'assistant cherche sur Internet
s = scene(1, "Scène 2 · « Et quelques instants plus tard, ton assistant va chercher les informations sur Internet, »")
panneau(s, "s02-vid", 113, 230, 780, 439, ("video", "lunettes-ecran", 0, round(s.fin - s.debut, 2)), "Ton assistant cherche")
cam(s, '<div id="s02-barre" class="pj-recherche" style="left: 990px; top: 210px; width: 820px; opacity: 0"><i class="pj-loupe"></i>'
       + "".join(f'<span id="s02-q{k}" style="opacity: 0">{m}</span> ' for k, m in enumerate(("actualités", "intelligence", "artificielle")))
       + "</div>")
resultats(s, "s02-r", 990, 330, 560, 3, 110)
cam(s, perso("s02-ia", 1720, 800, 300, "ia"))
s.add(hud_g("s02-hud", "Quelques instants plus tard", "Il cherche sur Internet"))
s.glisse("#s02-vid", s.debut + 0.05, -400)
s.j('tl.set("#s02-ia", { x: 420 }, 0);')
court(s, "s02-ia", s.debut + 0.2, t_mot(25), -420)
son(s.debut + 0.4, "swoosh-vitesse", 0.4, "l'assistant arrive en courant")
vit(s, "s02-ia", t_mot(25) + 0.05, s.fin - 0.2)
s.apparait("#s02-barre", t_mot(26), 20)
son(t_mot(26), "bouton-tech", 0.4, "barre de recherche")
for k, i in enumerate((27, 28, 29)):
    s.montre(f"#s02-q{k}", t_mot(i))
son(t_mot(27), "clavier-ordi", 0.38, "recherche tapée", d=1.0, sur_pic=False)
zoom(s, t_mot(27) - 0.1, 1350, 380, 1.2)
pose(s, "s02-ia", t_mot(29), 0.16, "back.out(2)", bg=120, tete=8)
for k in range(3):
    s.glisse(f"#s02-r-{k}", t_mot(31) + k * 0.14, 160)
son(t_mot(30), "radar", 0.35, "recherche en cours", d=1.2, sur_pic=False)
for k in range(3):
    pop(t_mot(31) + k * 0.14, 0.34, "résultat")
s.ecrire()

# ---------------------------------------------------------------- S3 : il trie et renvoie un compte rendu sur Telegram
s = scene(2, "Scène 3 · « …sélectionne les résultats pertinents et te renvoie un compte rendu directement sur Telegram. »")
resultats(s, "s03-r", 113, 230, 560, 5, 104, visibles_a=s.debut)
panneau(s, "s03-vid", 730, 230, 560, 315, ("video", "actus-tablette", 0, round(s.fin - s.debut, 2)), "Le tri")
cam(s, perso("s03-ia", 1010, 800, 240, "ia"))
telegram(s, "s03-tg", 1360, 100, "Mon assistant IA",
         [("m1", "moi", "Fais-moi un résumé des dernières actualités sur l'IA."),
          ("m2", "bot", "<b>Compte rendu prêt</b><br>3 actus IA du jour, avec les sources.")])
cam(s, carte_logo("s03-logo", "telegram", 1080, 560, 200))
s.add(hud_g("s03-hud", "Le tri", "Puis le compte rendu"))
s.j('tl.set("#s03-tg-m1", { opacity: 1 }, 0);')
s.apparait("#s03-vid", s.debut + 0.05, 30)
vit(s, "s03-ia", s.debut, s.fin - 0.2)
pertinents = (0, 2, 3)
for k in range(5):
    g = t_mot(32) + 0.12 + k * 0.22
    if k in pertinents:
        s.j(f'tl.set("#s03-r-{k}-m", {{ opacity: 1, backgroundColor: "{ACCENT}" }}, {s.L(g)});')
        s.j(f'tl.to("#s03-r-{k}", {{ borderColor: "{ACCENT}", duration: 0.1 }}, {s.L(g)});')
        son(g, "coche", 0.4, "résultat pertinent")
    else:
        s.j(f'tl.to("#s03-r-{k}", {{ opacity: 0.25, duration: 0.15 }}, {s.L(g)});')
        son(g, "tic", 0.3, "résultat écarté")
zoom(s, t_mot(32) - 0.1, 450, 470, 1.18)
pose(s, "s03-ia", t_mot(33), 0.16, "back.out(2)", bg=110, tete=8)
acquiesce(s, "s03-ia", t_mot(35), 2)
zoom(s, t_mot(37) - 0.1, 1570, 400, 1.25)
recoit(s, "#s03-tg-m2", t_mot(38))
pose(s, "s03-ia", t_mot(38), 0.12, bg=0, tete=0)
s.claque("#s03-logo", t_mot(44), 1.8)
pop(t_mot(44), 0.45, "logo Telegram")
zoom(s, t_mot(43), 1200, 520, 1.05)
saut(s, "s03-ia", t_mot(44), 30)
s.ecrire()

# ---------------------------------------------------------------- S4 : pas de la science-fiction
s = scene(3, "Scène 4 · « Ce n'est pas de la science-fiction. »")
plein_cadre(s, "s04-plein", "ville-futur", round(s.fin - s.debut, 2))
cam(s, '<div id="s04-t0" class="pj-serif" style="left: 0; width: 1920px; top: 230px; font-size: 90px; text-align: center; opacity: 0">Ce n\'est pas de la</div>')
cam(s, '<div id="s04-t1" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 360px; text-align: center; font-size: 190px; color: #ECECE8; '
       'text-shadow: none; opacity: 0">Science-fiction<i id="s04-r" style="position: absolute; left: 330px; right: 330px; top: 46%; height: 18px; background: #DCFC1C"></i></div>')
s.add(hud_g("s04-hud", "Science-fiction ?", "Non"))
s.j('tl.set("#s04-r", { scaleX: 0, transformOrigin: "0% 50%" }, 0);')
s.apparait("#s04-t0", t_mot(45), 20)
s.choc("#s04-t1", t_mot(50))
son(t_mot(50), "impact-futur", 0.5, "SCIENCE-FICTION")
s.j(f'tl.to("#s04-r", {{ scaleX: 1, duration: 0.16, ease: "power2.out" }}, {s.L(t_mot(50) + 0.45)});')
son(t_mot(50) + 0.45, "buzz-faux", 0.42, "rayé")
s.ecrire()

# ---------------------------------------------------------------- S5 : c'est un agent IA
s = scene(4, "Scène 5 · « C'est un agent IA. »")
plein_cadre(s, "s05-plein", "robot-salut", round(s.fin - s.debut, 2), 0.5)
cam(s, '<div id="s05-t" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 330px; text-align: center; font-size: 250px; opacity: 0">Un agent IA.</div>')
s.add(hud_g("s05-hud", "C'est réel", "Un agent IA"))
s.choc("#s05-t", t_mot(53))
s.eclair(t_mot(53))
son(t_mot(53), "impact-whoosh", 0.55, "UN AGENT IA")
son(t_mot(54) + 0.1, "robot-oui", 0.45, "le robot répond")
zoom(s, t_mot(54), 960, 500, 1.1)
s.ecrire()

# ---------------------------------------------------------------- S6 : de A à Z, sans code
s = scene(5, "Scène 6 · « …je vais te montrer comment en créer un de A à Z, sans écrire une seule ligne de code. »")
cam(s, projecteur(470) + projecteur(780, op=0.8))
cam(s, perso("s06-toi", 470, 800, 400))
cam(s, perso("s06-ia", 780, 800, 350, "ia"))
cam(s, '<div id="s06-a" class="pj-impact" style="position: absolute; left: 1040px; top: 170px; font-size: 230px; opacity: 0">A</div>')
cam(s, '<div id="s06-fl" style="position: absolute; left: 1230px; top: 290px; width: 330px; height: 20px; background: #ECECE8; transform-origin: 0% 50%"></div>')
cam(s, '<div id="s06-z" class="pj-impact" style="position: absolute; left: 1600px; top: 170px; font-size: 230px; opacity: 0">Z</div>')
panneau(s, "s06-vid", 1040, 470, 680, 300, ("video", "code-ecran", 0, round(s.fin - s.debut, 2)), "Du code ?")
cam(s, '<div id="s06-x" class="pj-x" style="left: 1040px; top: 470px; width: 680px; height: 300px; opacity: 0"></div>')
tampon(s, "s06-zero", "0 ligne de code", 1100, 250, t_mot(73) + 0.25, -5, 96)
s.add(hud_g("s06-hud", "Aujourd'hui", "De A à Z, sans code"))
s.j('tl.set("#s06-fl", { scaleX: 0 }, 0);')
vit(s, "s06-toi", s.debut, s.fin - 0.2)
vit(s, "s06-ia", s.debut, s.fin - 0.2)
parle(s, "s06-toi", t_mot(56), t_mot(61))
s.claque("#s06-a", t_mot(66), 1.8)
pop(t_mot(66), 0.42, "A")
s.j(f'tl.to("#s06-fl", {{ scaleX: 1, duration: 0.25, ease: "power2.out" }}, {s.L(t_mot(66) + 0.1)});')
son(t_mot(66) + 0.15, "swoosh-accent", 0.38, "de A…")
s.claque("#s06-z", t_mot(68), 1.8)
pop(t_mot(68), 0.42, "…à Z")
pose(s, "s06-toi", t_mot(66), 0.16, "back.out(2)", bd=-115, tete=-8)
saut(s, "s06-toi", t_mot(68), 30)
zoom(s, t_mot(66) - 0.12, 1330, 330, 1.18)
s.apparait("#s06-vid", t_mot(69), 40)
son(t_mot(69), "clavier-ordi-2", 0.32, "du code", d=1.5, sur_pic=False)
for sel in ("#s06-a", "#s06-z", "#s06-fl"):
    s.cache(sel, t_mot(69) - 0.1)
zoom(s, t_mot(69) - 0.1, 1330, 520, 1.15)
pose(s, "s06-toi", t_mot(70), 0.14, bd=0, tete=0)
s.croix("#s06-x", t_mot(73))
son(t_mot(73), "fouet", 0.45, "code barré")
son(t_mot(73) + 0.25, "impact-cartoon", 0.5, "0 ligne de code")
bras_croises(s, "s06-toi", t_mot(74))
acquiesce(s, "s06-ia", t_mot(73), 2)
s.ecrire()

# ---------------------------------------------------------------- S7 : étape 1, n8n et l'espace de travail
s = scene(6, "Scène 7 · « Première étape : rends-toi sur n8n et crée ton espace de travail. »")
etape(s, "s07-et", 1, t_mot(76))
panneau(s, "s07-vid", 113, 250, 700, 394, ("video", "macbook", 0, round(min(4.6, s.fin - s.debut), 2)), "Ton ordinateur")
cam(s, carte_logo("s07-n8n", "n8n", 880, 230, 280))
fenetre(s, "s07-fen", 1240, 330, 580, 380, "Mon espace de travail",
        '<div class="pj-fen-vide"><b>+</b><span>Nouvel espace</span></div>')
cam(s, perso("s07-toi", 1020, 800, 250))
s.add(hud_g("s07-hud", "Étape 1", "n8n"))
s.glisse("#s07-vid", s.debut + 0.05, -420)
son(s.debut + 0.1, "swoosh-vol", 0.38, "vidéo qui glisse")
vit(s, "s07-toi", s.debut, s.fin - 0.2)
s.claque("#s07-n8n", t_mot(80), 1.8)
son(t_mot(80), "power-up", 0.45, "logo n8n")
zoom(s, t_mot(80) - 0.12, 1020, 420, 1.22)
pose(s, "s07-toi", t_mot(80), 0.16, "back.out(2)", bd=-160, tete=-8)
saut(s, "s07-toi", t_mot(80), 26)
s.apparait("#s07-fen", t_mot(82), 40)
son(t_mot(82), "swoosh-monte", 0.4, "espace de travail")
zoom(s, t_mot(82) - 0.12, 1400, 480, 1.15)
pose(s, "s07-toi", t_mot(83), 0.16, "back.out(2)", bd=-100, tete=-4)
son(t_mot(86), "construit", 0.38, "espace créé")
s.ecrire()

# ---------------------------------------------------------------- S8 : l'onglet Agents, puis Create Agent
s = scene(7, "Scène 8 · « Une fois dans l'interface, ouvre l'onglet « Agents », puis clique sur « Create Agent ». »")
cote = "".join(f'<div id="s08-nav{k}" class="pj-fen-nav">{t}</div>' for k, t in enumerate(("Vue d'ensemble", "Agents", "Workflows", "Identifiants")))
fenetre(s, "s08-fen", 200, 214, 1300, 620, "n8n · Mon espace de travail",
        f'<div class="pj-fen-cote">{cote}</div><div class="pj-fen-main">'
        '<div id="s08-titre" class="pj-fen-h" style="opacity: 0">Agents</div>'
        '<div id="s08-vide" class="pj-fen-vide2" style="opacity: 0">Aucun agent pour l\'instant</div>'
        '<div id="s08-btn" class="pj-fen-bouton" style="opacity: 0">+ Create Agent</div>'
        '<div id="s08-carte" class="pj-fen-carte" style="opacity: 0"><b>Nouvel agent</b><span>Brouillon</span></div></div>')
souris(s, "s08-souris", 1180, 700)
cam(s, perso("s08-toi", 1710, 800, 300))
s.add(hud_g("s08-hud", "Dans n8n", "Agents, puis Create Agent"))
s.apparait("#s08-fen", s.debut + 0.05, 40)
son(s.debut + 0.1, "demarrage", 0.36, "l'interface s'ouvre")
vit(s, "s08-toi", s.debut, s.fin - 0.2)
pose(s, "s08-toi", t_mot(90), 0.16, "back.out(2)", bg=105, tete=6)
deplace(s, "s08-souris", t_mot(91), 320, 400, 1180, 700, 0.55)
zoom(s, t_mot(91) - 0.1, 540, 450, 1.3)
clic(s, "s08-souris", t_mot(93) + 0.05, "#s08-nav1")
s.j(f'tl.to("#s08-nav1", {{ backgroundColor: "{ACCENT}", color: "#000000", duration: 0.08 }}, {s.L(t_mot(93) + 0.05)});')
s.apparait("#s08-titre", t_mot(93) + 0.15, 16)
s.apparait("#s08-vide", t_mot(93) + 0.25, 16)
s.claque("#s08-btn", t_mot(94), 1.4)
pop(t_mot(94), 0.36, "bouton Create Agent")
deplace(s, "s08-souris", t_mot(95), 1000, 610, 1180, 700, 0.5)
zoom(s, t_mot(95) - 0.1, 1000, 470, 1.18)
clic(s, "s08-souris", t_mot(98), "#s08-btn")
s.cache("#s08-vide", t_mot(98) + 0.1)
s.cache("#s08-btn", t_mot(98) + 0.12)
s.claque("#s08-carte", t_mot(98) + 0.2, 1.5)
son(t_mot(98) + 0.2, "mission-ok", 0.42, "agent créé")
pose(s, "s08-toi", t_mot(97), 0.12, bg=0, tete=0)
saut(s, "s08-toi", t_mot(98) + 0.2, 30)
s.ecrire()

# ---------------------------------------------------------------- S9 : étape 2, le modèle d'IA
s = scene(8, "Scène 9 · « Deuxième étape : choisis le modèle d'intelligence artificielle qui va faire fonctionner ton agent. »")
etape(s, "s09-et", 2, t_mot(99))
panneau(s, "s09-vid", 113, 260, 640, 360, ("video", "sphere-donnees", 0, round(s.fin - s.debut, 2)), "Modèle d'IA")
noeud(s, "s09-agent", 1150, 330, "Agent IA", "Ton agent", "IA", 330, agent=True)
noeud(s, "s09-mod", 1150, 620, "Modèle d'IA", "Le cerveau", "svg:puce", 330)
liens(s, "s09-l", [(1150, 385, 1150, 565, "v", t_mot(104))])
cam(s, perso("s09-ia", 1680, 800, 330, "ia"))
s.add(hud_g("s09-hud", "Étape 2", "Le modèle d'IA"))
s.apparait("#s09-agent", t_mot(100), 30)
pop(t_mot(100), 0.38, "nœud agent")
vit(s, "s09-ia", s.debut, s.fin - 0.2)
s.apparait("#s09-vid", t_mot(103) - 0.2, 40)
s.claque("#s09-mod", t_mot(103), 1.5)
pop(t_mot(103), 0.4, "nœud modèle")
zoom(s, t_mot(103) - 0.12, 1150, 480, 1.2)
pose(s, "s09-ia", t_mot(103), 0.16, "back.out(2)", bg=110, tete=8)
brille(s, "#s09-agent", t_mot(109))
grossit(s, "s09-ia", t_mot(109), 1.12)
son(t_mot(109), "power-up", 0.42, "l'agent s'allume")
zoom(s, t_mot(109) - 0.1, 1400, 480, 1.1)
s.ecrire()

# ---------------------------------------------------------------- S10 : Google, OpenAI…
s = scene(9, "Scène 10 · « Tu peux connecter un fournisseur comme Google ou OpenAI, selon les options disponibles. »")
cam(s, projecteur(300) + projecteur(600, op=0.8))
cam(s, perso("s10-toi", 300, 800, 360))
cam(s, perso("s10-ia", 600, 800, 340, "ia"))
lignes = [("google", "logo-google.svg", "Google"), ("openai", "logo-openai.svg", "OpenAI"), ("autres", "", "Autres options…")]
html = '<div class="pj-label" style="position: static; margin-bottom: 18px"><span class="pj-k">Choisir un modèle</span></div>'
for k, (cle, f, nom) in enumerate(lignes):
    ico = f'<img src="assets/img/{f}" alt="" />' if f else '<b class="pj-noeud-ico">…</b>'
    html += f'<div id="s10-opt{k}" class="pj-option" style="opacity: 0">{ico}<span>{nom}</span><i id="s10-ok{k}"></i></div>'
cam(s, f'<div id="s10-liste" class="pj-liste" style="left: 960px; top: 190px; width: 820px">{html}</div>')
s.add(hud_g("s10-hud", "Le fournisseur", "Selon les options"))
vit(s, "s10-toi", s.debut, s.fin - 0.2)
vit(s, "s10-ia", s.debut, s.fin - 0.2)
parle(s, "s10-toi", t_mot(112), t_mot(116))
for k, i in enumerate((118, 120, 123)):
    s.glisse(f"#s10-opt{k}", t_mot(i), 260)
    son(t_mot(i), tour(["swoosh-accent", "swoosh-court", "papier-glisse"]), 0.38, "option")
s.j(f'tl.to("#s10-opt0", {{ borderColor: "{ACCENT}", duration: 0.1 }}, {s.L(t_mot(118) + 0.2)});')
s.j(f'tl.to("#s10-opt1", {{ borderColor: "{ACCENT}", duration: 0.1 }}, {s.L(t_mot(120) + 0.2)});')
s.j(f'tl.set("#s10-ok1", {{ backgroundColor: "{ACCENT}" }}, {s.L(t_mot(121))});')
son(t_mot(121), "coche", 0.42, "OpenAI choisi")
pose(s, "s10-ia", t_mot(118), 0.16, "back.out(2)", bd=-110, tete=-8)
acquiesce(s, "s10-ia", t_mot(120), 2)
zoom(s, t_mot(117) - 0.12, 1340, 330, 1.2)
zoom(s, t_mot(123) - 0.12, 1340, 430, 1.15)
pose(s, "s10-toi", t_mot(123), 0.16, "back.out(2)", bd=-140)
saut(s, "s10-toi", t_mot(123), 24)
s.ecrire()

# ---------------------------------------------------------------- S11 : étape 3, un rôle et des instructions
s = scene(10, "Scène 11 · « Troisième étape : donne-lui un rôle et des instructions précises. »")
etape(s, "s11-et", 3, t_mot(125))
panneau(s, "s11-vid", 113, 250, 680, 383, ("video", "notes-crayon", 0, round(s.fin - s.debut, 2)), "Ses consignes")
for k, (x, titre) in enumerate(((880, "Rôle"), (1340, "Instructions"))):
    traits = "".join(f'<div class="s11-ligne{k}" style="height: 14px; width: {w}%; background: #bdbdb8; margin-top: 16px; transform-origin: 0% 50%"></div>'
                     for w in (92, 76, 88, 64))
    cam(s, f'<div id="s11-p{k}" class="pj-papier" style="left: {x}px; top: 290px; width: 420px; padding: 26px 30px; opacity: 0">'
           f'<h3 style="font-size: 64px">{titre}</h3>{traits}</div>')
cam(s, perso("s11-ia", 1310, 800, 230, "ia"))
s.add(hud_g("s11-hud", "Étape 3", "Rôle + instructions"))
s.glisse("#s11-vid", s.debut + 0.05, -420)
vit(s, "s11-ia", s.debut, s.fin - 0.2)
for k, i in enumerate((129, 132)):
    s.claque(f"#s11-p{k}", t_mot(i), 1.5)
    son(t_mot(i), "page", 0.45, "feuille")
    s.j(f'tl.fromTo(".s11-ligne{k}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.18, stagger: 0.12 }}, {s.L(t_mot(i) + 0.15)});')
    son(t_mot(i) + 0.15, "stylo", 0.42, "on écrit")
zoom(s, t_mot(129) - 0.12, 1340, 460, 1.1)
pose(s, "s11-ia", t_mot(129), 0.16, "back.out(2)", bg=150, bd=-150)
saut(s, "s11-ia", t_mot(133), 26)
pose(s, "s11-ia", t_mot(132), 0.14, bg=0, bd=0)
acquiesce(s, "s11-ia", t_mot(133) + 0.3, 2)
s.ecrire()

# ---------------------------------------------------------------- S12 : un assistant de recherche
s = scene(11, "Scène 12 · « Par exemple, je vais créer un assistant de recherche dont la mission est de trouver des informations récentes, »")
panneau(s, "s12-vid", 113, 210, 600, 338, ("video", "recherche-ordi", 0, round(s.fin - s.debut, 2)), "Assistant de recherche")
consigne = [("Tu", 140), ("es", 140), ("un", 140), ("assistant", 140), ("de", 141), ("recherche.", 142),
            ("Ta", 144), ("mission", 145), (":", 146), ("trouver", 148), ("des", 149), ("informations", 150), ("récentes,", 151)]
spans = " ".join(f'<span id="s12-w{k}" style="opacity: 0{"; color: #DCFC1C" if m in ("assistant", "recherche.", "récentes,") else ""}">{m}</span>'
                 for k, (m, _) in enumerate(consigne))
fenetre(s, "s12-fen", 790, 170, 1020, 470, "n8n · Instructions de l'agent",
        f'<div class="pj-fen-texte">{spans}<b id="s12-curseur" class="pj-tel-curseur"></b></div>')
cam(s, perso("s12-ia", 410, 800, 240, "ia"))
s.add(hud_g("s12-hud", "Exemple", "Un assistant de recherche"))
s.apparait("#s12-fen", s.debut + 0.05, 40)
s.apparait("#s12-vid", s.debut + 0.1, 40)
son(s.debut + 0.1, "swoosh-monte", 0.36, "fenêtre")
vit(s, "s12-ia", s.debut, s.fin - 0.2)
for k, (m, i) in enumerate(consigne):
    s.montre(f"#s12-w{k}", round(t_mot(i) + (0.08 * (k % 3) if i == 140 else 0), 2))
son(t_mot(140) - 0.05, "clavier-ordi", 0.36, "consigne tapée", d=round(t_mot(151) + 0.3 - t_mot(140), 2), sur_pic=False)
tape(s, "s12-ia", t_mot(138), t_mot(151) + 0.2)
zoom(s, t_mot(139) - 0.1, 1300, 380, 1.22)
s.ecrire()

# ---------------------------------------------------------------- S13 : comparer les sources, un résumé avec les liens
s = scene(12, "Scène 13 · « …de comparer les sources et de me présenter un résumé clair avec les liens des articles. »")
panneau(s, "s13-vid", 113, 210, 600, 338, ("video", "journal", 0, round(s.fin - s.debut, 2)), "Les sources")
for k, nom in enumerate(("Source A", "Source B", "Source C")):
    cam(s, f'<div id="s13-src{k}" class="pj-carte" style="left: {780 + k * 150}px; top: {250 + (k % 2) * 60}px; width: 200px; '
           f'padding: 20px 16px; font-size: 40px; opacity: 0">{nom}</div>')
cam(s, '<div id="s13-vs" class="pj-impact" style="position: absolute; left: 905px; top: 440px; font-size: 90px; opacity: 0">VS</div>')
liste = "".join(f'<div class="pj-res-ligne"><div style="width: {w}%"></div><span id="s13-lien{k}" style="opacity: 0">lien →</span></div>'
                for k, w in enumerate((70, 58, 64)))
cam(s, f'<div id="s13-res" class="pj-papier" style="left: 1260px; top: 180px; width: 560px; padding: 30px 34px; opacity: 0">'
       f'<h3 style="font-size: 70px">Résumé</h3>{liste}</div>')
cam(s, perso("s13-toi", 990, 800, 260))
s.add(hud_g("s13-hud", "Sa mission", "Comparer, résumer"))
s.apparait("#s13-vid", s.debut + 0.05, 40)
vit(s, "s13-toi", s.debut, s.fin - 0.2)
for k in range(3):
    s.claque(f"#s13-src{k}", t_mot(153) + k * 0.16, 1.5)
    son(t_mot(153) + k * 0.16, tour(["page", "papiers", "papier-glisse"]), 0.4, "source")
s.claque("#s13-vs", t_mot(155), 1.6)
son(t_mot(155), "scanner", 0.32, "comparaison", d=1.2)
s.j(f'tl.to(["#s13-src0", "#s13-src2"], {{ keyframes: [{{ x: -14, duration: 0.12 }}, {{ x: 14, duration: 0.12 }}, {{ x: 0, duration: 0.12 }}] }}, {s.L(t_mot(155) + 0.2)});')
gratte(s, "s13-toi", t_mot(153))
zoom(s, t_mot(153) - 0.12, 960, 400, 1.15)
s.apparait("#s13-res", t_mot(159), 40)
son(t_mot(159), "swoosh-monte", 0.4, "résumé")
zoom(s, t_mot(159) - 0.12, 1540, 400, 1.2)
pose(s, "s13-toi", t_mot(160), 0.16, "back.out(2)", bd=-120, tete=-6)
for k in range(3):
    s.apparait(f"#s13-lien{k}", t_mot(165) + k * 0.15, 10)
    son(t_mot(165) + k * 0.15, "clic-positif", 0.35, "lien")
pouce(s, "s13-toi", t_mot(166))
s.ecrire()

# ---------------------------------------------------------------- S14 : étape 4, des outils
s = scene(13, "Scène 14 · « Quatrième étape : donne-lui des outils. C'est une étape essentielle. »")
etape(s, "s14-et", 4, t_mot(168))
panneau(s, "s14-vid", 113, 230, 860, 484, ("video", "atelier-outils", 0, round(s.fin - s.debut, 2)), "Des outils")
cam(s, projecteur(1500))
cam(s, perso("s14-ia", 1500, 800, 380, "ia"))
for k, (m, x, y) in enumerate((("Recherche web", 1330, 300), ("Calendrier", 1700, 360), ("E-mail", 1270, 470))):
    puce(s, f"s14-o{k}", m, x, y, t_mot(172) + k * 0.16, "font-size: 40px")
tampon(s, "s14-ess", "Essentiel", 560, 600, t_mot(176), -6, 84)
s.add(hud_g("s14-hud", "Étape 4", "Des outils"))
s.glisse("#s14-vid", s.debut + 0.05, -420)
vit(s, "s14-ia", s.debut, s.fin - 0.2)
for k in range(3):
    son(t_mot(172) + k * 0.16, tour(["robot-meca", "bouton-tech", "interrupteur-2"]), 0.4, "outil")
victoire(s, "s14-ia", t_mot(172), 1)
zoom(s, t_mot(171) - 0.1, 1500, 420, 1.18)
zoom(s, t_mot(176) - 0.12, 760, 520, 1.12)
son(t_mot(176), "impact-basse", 0.5, "ESSENTIEL")
pose(s, "s14-ia", t_mot(176), 0.16, "back.out(2)", bg=0, bd=-110, tete=-6)
s.ecrire()

# ---------------------------------------------------------------- S15 : répondre ne suffit pas, il doit agir
s = scene(14, "Scène 15 · « Un agent ne doit pas seulement savoir répondre : il doit pouvoir agir. »")
cam(s, projecteur(440))
cam(s, perso("s15-ia", 440, 800, 380, "ia"))
cam(s, '<div id="s15-rep" class="pj-impact" style="position: absolute; left: 140px; top: 236px; font-size: 110px; color: #ECECE8; text-shadow: none; opacity: 0">Répondre</div>')
panneau(s, "s15-vid", 1000, 230, 820, 461, ("video", "robot-usine", 0, round(s.fin - s.debut, 2)), "Agir")
cam(s, '<div id="s15-agir-t" class="pj-impact" style="position: absolute; left: 1000px; width: 820px; top: 360px; text-align: center; font-size: 210px; opacity: 0">Agir</div>')
s.add(hud_g("s15-hud", "Un vrai agent", "Il agit"))
vit(s, "s15-ia", s.debut, s.fin - 0.2)
bulle(s, "s15-b", "Je réponds…", 580, 380, t_mot(182), 50, fin=t_mot(187))
pop(t_mot(182), 0.38, "bulle")
parle(s, "s15-ia", t_mot(177), t_mot(184))
s.apparait("#s15-rep", t_mot(184), 20)
son(t_mot(184), "swoosh-accent", 0.38, "répondre")
s.apparait("#s15-vid", t_mot(186), 40)
son(t_mot(186), "robot-meca", 0.4, "le robot agit")
zoom(s, t_mot(186) - 0.12, 1410, 460, 1.18)
s.choc("#s15-agir-t", t_mot(188))
s.eclair(t_mot(188))
son(t_mot(188), "impact-futur", 0.55, "AGIR")
court(s, "s15-ia", t_mot(188) - 0.1, s.fin - 0.3, 160)
s.ecrire()

# ---------------------------------------------------------------- S16 : l'outil de recherche sur Internet
s = scene(15, "Scène 16 · « Je vais donc lui ajouter un outil de recherche sur Internet… au lieu de dépendre de ce qu'il connaît déjà. »")
noeud(s, "s16-agent", 860, 330, "Agent IA", "Assistant de recherche", "IA", 460, agent=True)
noeud(s, "s16-mod", 640, 620, "Modèle d'IA", "OpenAI", "logo-openai.svg", 330)
noeud(s, "s16-out", 1080, 620, "Outil", "Recherche web", "svg:loupe", 330)
liens(s, "s16-l", [(800, 385, 640, 565, "v", None), (920, 385, 1080, 565, "v", t_mot(195))])
panneau(s, "s16-vid", 1340, 220, 480, 270, ("video", "tablette-web", 0, round(s.fin - s.debut, 2)), "Internet")
puce_rayee(s, "s16-mem", "Seulement sa mémoire", 1580, 640, t_mot(209), t_mot(213))
cam(s, perso("s16-ia", 230, 800, 330, "ia"))
s.add(hud_g("s16-hud", "Son outil", "La recherche web"))
s.j('tl.set(["#s16-agent", "#s16-mod"], { opacity: 1 }, 0);')
vit(s, "s16-ia", s.debut, s.fin - 0.2)
parle(s, "s16-ia", t_mot(189), t_mot(193))
s.claque("#s16-out", t_mot(195), 1.6)
son(t_mot(195), "construit", 0.45, "outil ajouté")
brille(s, "#s16-out", t_mot(197))
zoom(s, t_mot(194) - 0.12, 960, 520, 1.18)
pose(s, "s16-ia", t_mot(195), 0.16, "back.out(2)", bd=-100, tete=-8)
s.glisse("#s16-vid", t_mot(199), 300)
son(t_mot(199), "radar", 0.32, "Internet", d=1.4, sur_pic=False)
zoom(s, t_mot(199) - 0.12, 1400, 420, 1.15)
acquiesce(s, "s16-ia", t_mot(203), 2)
zoom(s, t_mot(209) - 0.12, 1300, 560, 1.12)
pose(s, "s16-ia", t_mot(209), 0.14, bd=0, tete=0)
non(s, "s16-ia", t_mot(213))
s.ecrire()

# ---------------------------------------------------------------- S17 : étape 5, Telegram
s = scene(16, "Scène 17 · « Cinquième étape : connecte-le à Telegram. »")
etape(s, "s17-et", 5, t_mot(216))
cam(s, projecteur(560))
cam(s, perso("s17-ia", 560, 800, 400, "ia"))
cam(s, carte_logo("s17-tg", "telegram", 1220, 260, 300))
liens(s, "s17-l", [(680, 520, 1220, 440, "h", t_mot(218) + 0.2)])
s.add(hud_g("s17-hud", "Étape 5", "Telegram"))
vit(s, "s17-ia", s.debut, s.fin - 0.2)
s.claque("#s17-tg", t_mot(218), 1.8)
pop(t_mot(218), 0.45, "logo Telegram")
pose(s, "s17-ia", t_mot(218), 0.16, "back.out(2)", bd=-100, tete=-8)
son(t_mot(220), "deverrouille", 0.45, "connecté à Telegram")
saut(s, "s17-ia", t_mot(220), 30)
zoom(s, t_mot(219), 960, 480, 1.12)
s.ecrire()

# ---------------------------------------------------------------- S18 : BotFather, le jeton, les identifiants dans n8n
s = scene(17, "Scène 18 · « …crée un bot avec BotFather, récupère son jeton de connexion, puis renseigne les identifiants dans n8n… »")
telegram(s, "s18-tg", 150, 100, "BotFather",
         [("m1", "moi", "/newbot"), ("m2", "bot", "Choisis un nom pour ton bot."), ("m3", "moi", "MonAgentIA_bot"),
          ("m4", "bot", 'Voici ton jeton :<br><code class="pj-jeton">7581••••:AAH••••••</code>')])
cam(s, '<div id="s18-jeton" class="pj-jeton-vol" style="left: 230px; top: 560px; opacity: 0">Jeton</div>')
fenetre(s, "s18-fen", 780, 170, 1030, 470, "n8n · Identifiants Telegram",
        '<div class="pj-fen-form"><label>Jeton d\'accès</label><div class="pj-fen-champ"><span id="s18-pts" style="opacity: 0">••••••••••••••••</span></div>'
        '<div class="pj-fen-ligne"><div id="s18-save" class="pj-fen-bouton" style="position: static">Enregistrer</div>'
        '<div id="s18-ok" class="pj-fen-ok" style="opacity: 0">✓ Connecté</div></div></div>')
cam(s, perso("s18-toi", 680, 800, 280))
s.add(hud_g("s18-hud", "Telegram", "Bot + jeton + n8n"))
vit(s, "s18-toi", s.debut, s.fin - 0.2)
recoit(s, "#s18-tg-m1", t_mot(223), 0.4, "swoosh-court")
recoit(s, "#s18-tg-m2", t_mot(227), 0.45)
recoit(s, "#s18-tg-m3", t_mot(227) + 0.55, 0.4, "swoosh-accent")
zoom(s, t_mot(223) - 0.12, 400, 380, 1.25)
recoit(s, "#s18-tg-m4", t_mot(228), 0.5, "deverrouille-2")
pose(s, "s18-toi", t_mot(228), 0.16, "back.out(2)", bg=110, tete=6)
zoom(s, t_mot(229), 480, 520, 1.15)
s.apparait("#s18-fen", t_mot(232) - 0.3, 40)
son(t_mot(232) - 0.3, "swoosh-monte", 0.36, "fenêtre n8n")
s.j(f'tl.fromTo("#s18-jeton", {{ opacity: 1, x: 0, y: 0, scale: 1 }}, {{ x: 1050, y: -120, scale: 0.8, opacity: 1, duration: 0.6, ease: "power2.inOut", immediateRender: false }}, {s.L(t_mot(233))});')
s.j(f'tl.to("#s18-jeton", {{ opacity: 0, duration: 0.1 }}, {s.L(t_mot(233) + 0.6)});')
son(t_mot(233) + 0.2, "fusee-whoosh", 0.4, "le jeton vole vers n8n")
pose(s, "s18-toi", t_mot(233), 0.14, bg=0, bd=-110, tete=-6)
zoom(s, t_mot(233), 1290, 400, 1.15)
s.montre("#s18-pts", t_mot(234) + 0.1)
son(t_mot(234), "clavier-ordi-2", 0.35, "identifiants", d=1.4, sur_pic=False)
clic_btn = t_mot(238)
s.j(f'tl.to("#s18-save", {{ keyframes: [{{ scale: 0.92, duration: 0.07 }}, {{ scale: 1, duration: 0.12 }}] }}, {s.L(clic_btn)});')
son(clic_btn, "souris", 0.5, "enregistrer")
s.claque("#s18-ok", t_mot(239), 1.6)
son(t_mot(239), "mission-ok", 0.45, "connecté")
saut(s, "s18-toi", t_mot(239), 30)
s.ecrire()

# ---------------------------------------------------------------- S19 : Telegram associé à l'agent (le workflow complet)
NOEUDS = [("trig", 400, 360, "Telegram", "Message reçu", "logo-telegram.svg", 320, False),
          ("agent", 960, 360, "Agent IA", "Assistant", "IA", 320, True),
          ("env", 1520, 360, "Telegram", "Envoyer", "logo-telegram.svg", 320, False),
          ("mod", 800, 640, "Modèle", "OpenAI", "logo-openai.svg", 280, False),
          ("out", 1120, 640, "Outil", "Recherche web", "svg:loupe", 300, False)]


def workflow(s, p, visibles=("agent", "mod", "out"), t_liens=None):
    for nid, cx, cy, ti, so, ic, w, ag in NOEUDS:
        noeud(s, f"{p}-{nid}", cx, cy, ti, so, ic, w, agent=ag)
    t = t_liens or {}
    liens(s, f"{p}-l", [(560, 360, 800, 360, "h", t.get("trig")), (1120, 360, 1360, 360, "h", t.get("env")),
                        (900, 415, 800, 585, "v", None), (1020, 415, 1120, 585, "v", None)])
    s.j(f'tl.set([{", ".join(chr(34) + f"#{p}-{n}" + chr(34) for n in visibles)}], {{ opacity: 1 }}, 0);')


s = scene(18, "Scène 19 · « …et associe Telegram à ton agent. »")
workflow(s, "s19", t_liens={"trig": t_mot(242), "env": t_mot(244)})
s.add(hud_g("s19-hud", "Le workflow", "Telegram et agent"))
s.claque("#s19-trig", t_mot(241), 1.6)
pop(t_mot(241), 0.42, "nœud Telegram")
s.claque("#s19-env", t_mot(243), 1.6)
pop(t_mot(243), 0.42, "nœud Telegram")
son(t_mot(245), "deverrouille-2", 0.45, "associé")
zoom(s, t_mot(241) - 0.12, 960, 470, 1.08)
brille(s, "#s19-agent", t_mot(245))
s.ecrire()

# ---------------------------------------------------------------- S20 : publier et tester
s = scene(19, "Scène 20 · « Enfin, publie ton agent et teste-le. »")
cam(s, projecteur(470) + projecteur(780, op=0.8))
cam(s, perso("s20-toi", 470, 800, 400))
cam(s, perso("s20-ia", 780, 800, 350, "ia"))
cam(s, '<div id="s20-pub" class="pj-publier" style="left: 1100px; top: 300px"><span>Publier</span><div id="s20-int" class="pj-inter"><i id="s20-bouton"></i></div></div>')
tampon(s, "s20-actif", "Actif", 1300, 520, t_mot(247) + 0.35, -6, 90)
s.add(hud_g("s20-hud", "Enfin", "Publier, puis tester"))
vit(s, "s20-toi", s.debut, s.fin - 0.2)
vit(s, "s20-ia", s.debut, s.fin - 0.2)
pose(s, "s20-toi", t_mot(246), 0.16, "back.out(2)", bd=-100, tete=-6)
s.j(f'tl.to("#s20-bouton", {{ x: 96, duration: 0.18, ease: "back.out(2)" }}, {s.L(t_mot(247))});')
s.j(f'tl.to("#s20-int", {{ backgroundColor: "{ACCENT}", duration: 0.12 }}, {s.L(t_mot(247))});')
son(t_mot(247), "interrupteur", 0.5, "interrupteur")
son(t_mot(247) + 0.35, "fusee", 0.38, "l'agent est publié")
zoom(s, t_mot(247) - 0.12, 1250, 420, 1.2)
victoire(s, "s20-ia", t_mot(247) + 0.35, 1)
pouce(s, "s20-toi", t_mot(251))
zoom(s, t_mot(251) - 0.1, 960, 520, 1.0)
s.ecrire()

# ---------------------------------------------------------------- S21 : le message de test
s = scene(20, "Scène 21 · « Je lui envoie : « Trouve-moi trois actualités récentes sur l'IA, résume-les et donne-moi les sources. » »")
panneau(s, "s21-vid", 113, 220, 520, 293, ("video", "lecteur-actus", 0, round(s.fin - s.debut, 2)), "Le test")
cam(s, perso("s21-toi", 760, 800, 400))
telegram(s, "s21-tg", 1340, 100, "Mon assistant IA", [("m1", "moi", mots_bulle("s21-tg", "m1", 255, 266))])
for k, (m, i) in enumerate((("3 actus", 256), ("Résumé", 262), ("Sources", 266))):
    puce(s, f"s21-c{k}", m, 1080, 300 + k * 110, t_mot(i), "font-size: 40px")
s.add(hud_g("s21-hud", "Le test", "Une vraie demande"))
s.apparait("#s21-vid", s.debut + 0.05, 40)
vit(s, "s21-toi", s.debut, s.fin - 0.2)
parle(s, "s21-toi", t_mot(252), t_mot(254))
tape(s, "s21-toi", t_mot(255) - 0.1, t_mot(266) + 0.3)
ecrit_bulle(s, "s21-tg", "m1", 255, 266)
zoom(s, t_mot(255) - 0.15, 1550, 380, 1.25)
for k, i in enumerate((256, 262, 266)):
    pop(t_mot(i), 0.36, "mot-clé")
zoom(s, t_mot(262) - 0.15, 1150, 480, 1.08)
envoie(s, t_mot(266) + 0.45)
s.ecrire()

# ---------------------------------------------------------------- S22 : et voilà, l'agent travaille
s = scene(21, "Scène 22 · « Et voilà : mon agent reçoit la mission, utilise son outil de recherche et me renvoie son résultat dans Telegram. »")
workflow(s, "s22", visibles=("trig", "agent", "env", "mod", "out"))
cam(s, '<div id="s22-voila-t" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 130px; text-align: center; font-size: 140px; opacity: 0">Et voilà !</div>')
impulsion(s, "s22-imp", [(t_mot(270), 400, 360), (t_mot(273), 960, 360), (t_mot(275), 960, 360), (t_mot(278), 1120, 640),
                         (t_mot(279), 1120, 640), (t_mot(281), 960, 360), (t_mot(282), 960, 360), (t_mot(284), 1520, 360)])
cam(s, '<div id="s22-rep" class="pj-tg-bulle pj-tg-bot" style="position: absolute; left: 1380px; top: 470px; width: 420px; opacity: 0">'
       '<b>3 actus IA</b><br>1. Résumé · <u>source</u><br>2. Résumé · <u>source</u><br>3. Résumé · <u>source</u></div>')
cam(s, perso("s22-toi", 1760, 800, 250))
s.add(hud_g("s22-hud", "Et voilà", "L'agent travaille"))
s.claque("#s22-voila-t", t_mot(267), 1.6)
s.eclair(t_mot(267))
son(t_mot(267), "impact-whoosh", 0.5, "ET VOILÀ")
s.cache("#s22-voila-t", t_mot(270) - 0.1)
vit(s, "s22-toi", s.debut, s.fin - 0.2)
son(t_mot(270), "notif-indice", 0.42, "la mission arrive")
brille(s, "#s22-agent", t_mot(273))
son(t_mot(273), "robot-elec", 0.42, "l'agent reçoit la mission")
zoom(s, t_mot(272), 760, 420, 1.2)
brille(s, "#s22-out", t_mot(278))
son(t_mot(276), "scanner", 0.38, "recherche", d=1.4)
zoom(s, t_mot(276) - 0.1, 1040, 540, 1.2)
brille(s, "#s22-env", t_mot(284))
recoit(s, "#s22-rep", t_mot(285), 0.5, "notif-positive")
zoom(s, t_mot(284) - 0.1, 1500, 470, 1.2)
victoire(s, "s22-toi", t_mot(285), 2)
s.ecrire()

# ---------------------------------------------------------------- S23 : tu viens de construire un assistant
s = scene(22, "Scène 23 · « Tu viens de construire un assistant capable de recevoir une mission et de choisir les outils… »")
cam(s, projecteur(400) + projecteur(720, op=0.8))
cam(s, perso("s23-toi", 400, 800, 400))
cam(s, perso("s23-ia", 720, 800, 350, "ia"))
panneau(s, "s23-vid", 1060, 240, 740, 416, ("video", "robot-yeux", 0, round(s.fin - s.debut, 2)), "Ton assistant")
for k, (m, i, x) in enumerate((("Mission", 296, 1180), ("Outils", 301, 1440), ("Accompli ✓", 307, 1700))):
    puce(s, f"s23-c{k}", m, x, 730, t_mot(i), "font-size: 40px")
s.add(hud_g("s23-hud", "Bravo", "Ton agent est prêt"))
s.glisse("#s23-vid", s.debut + 0.05, 400)
vit(s, "s23-toi", s.debut, s.fin - 0.2)
vit(s, "s23-ia", s.debut, s.fin - 0.2)
victoire(s, "s23-toi", t_mot(289), 2)
son(t_mot(289), "victoire-tambours", 0.4, "construit")
zoom(s, t_mot(289) - 0.1, 560, 470, 1.15)
for k, i in enumerate((296, 301, 307)):
    son(t_mot(i), tour(["coche", "clic-positif", "mission-ok"]), 0.42, "étape réussie")
zoom(s, t_mot(296) - 0.12, 1440, 520, 1.1)
pose(s, "s23-ia", t_mot(296), 0.16, "back.out(2)", bd=-110, tete=-6)
acquiesce(s, "s23-ia", t_mot(301), 2)
saut(s, "s23-ia", t_mot(307), 30)
pose(s, "s23-toi", t_mot(301), 0.14, bg=0, bd=0)
pouce(s, "s23-toi", t_mot(307))
s.ecrire()

# ---------------------------------------------------------------- S24 : vérifier et contrôler
s = scene(23, "Scène 24 · « Évidemment, il faut toujours vérifier les informations obtenues et contrôler les actions sensibles. »")
panneau(s, "s24-vid", 113, 220, 760, 428, ("video", "controle-qualite", 0, round(s.fin - s.debut, 2)), "Vérifier")
lignes24 = "".join(f'<div class="pj-ligne-coche"><b id="s24-c{k}">✓</b>{t}</div>' for k, t in enumerate(("Informations vérifiées", "Actions sensibles contrôlées")))
cam(s, f'<div id="s24-liste" class="pj-liste" style="left: 960px; top: 230px; width: 860px; opacity: 0">'
       f'<div class="pj-label" style="position: static; margin-bottom: 22px"><span class="pj-k">Toujours</span></div>{lignes24}</div>')
cam(s, perso("s24-toi", 1390, 800, 270))
s.add(hud_g("s24-hud", "Évidemment", "Garde le contrôle"))
s.apparait("#s24-vid", s.debut + 0.05, 40)
s.apparait("#s24-liste", t_mot(310), 30)
son(t_mot(310), "swoosh-monte", 0.36, "liste")
vit(s, "s24-toi", s.debut, s.fin - 0.2)
for k, i in enumerate((312, 317)):
    s.j(f'tl.set("#s24-c{k}", {{ backgroundColor: "{ACCENT}" }}, {s.L(t_mot(i) + 0.2)});')
    son(t_mot(i) + 0.2, "coche", 0.45, "case cochée")
son(t_mot(312) - 0.1, "scanner", 0.32, "vérification", d=1.0)
zoom(s, t_mot(312) - 0.12, 1380, 330, 1.2)
oui(s, "s24-toi", t_mot(313))
pose(s, "s24-toi", t_mot(317), 0.16, "back.out(2)", bd=-120, tete=-6)
zoom(s, t_mot(319), 960, 520, 1.05)
s.ecrire()

# ---------------------------------------------------------------- S25 : imagine tout ce que tu pourrais construire
s = scene(24, "Scène 25 · « Mais imagine maintenant tout ce que tu pourrais construire avec cette méthode : »")
plein_cadre(s, "s25-plein", "interface-vr", round(s.fin - s.debut, 2), 0.55)
serif_tape(s, "s25-dit", 322, 332, 113, 220, 96, 1100)
cam(s, perso("s25-toi", 1560, 800, 400))
s.add(hud_g("s25-hud", "Imagine", "Tout ce que tu peux construire"))
vit(s, "s25-toi", s.debut, s.fin - 0.2)
son(t_mot(322), "aura", 0.38, "imagine")
pose(s, "s25-toi", t_mot(323), 0.16, "back.out(2)", bg=150, bd=-150, tete=-8)
grossit(s, "s25-toi", t_mot(328), 1.12)
son(t_mot(333), "riser-tech", 0.32, "montée vers les exemples")
zoom(s, t_mot(326), 900, 420, 1.12)
s.ecrire()

# ---------------------------------------------------------------- S26 : trois exemples d'agents
s = scene(25, "Scène 26 · « un assistant de recherche, un agent commercial ou même un assistant capable de gérer des tâches répétitives. »")
d26 = round(s.fin - s.debut, 2)
for k, (v, tag, i) in enumerate((("recherche-ordi", "Assistant de recherche", 333), ("reunion", "Agent commercial", 337), ("colis-tapis", "Tâches répétitives", 342))):
    x = 113 + k * 577
    panneau(s, f"s26-v{k}", x, 250, 540, 304, ("video", v, 0, d26), tag, piste=5 + k)
    cam(s, perso(f"s26-ia{k}", x + 270, 800, 210, "ia"))
    s.j(f'tl.set("#s26-ia{k}", {{ opacity: 0 }}, 0);')
    s.glisse(f"#s26-v{k}", t_mot(i), 260)
    s.claque(f"#s26-ia{k}", t_mot(i) + 0.1, 1.6)
    son(t_mot(i), tour(["souffle-cine", "swoosh-vol", "souffle-rapide"]), 0.42, "exemple")
    son(t_mot(i) + 0.15, tour(["robot-oui", "robot-oui-2", "robot-scifi"]), 0.4, "nouvel agent")
    vit(s, f"s26-ia{k}", t_mot(i) + 0.3, s.fin - 0.2)
    zoom(s, t_mot(i) - 0.12, x + 270, 470, 1.2)
son(t_mot(339), "pieces", 0.35, "commercial")
s.add(hud_g("s26-hud", "Avec la même méthode", "Plein d'agents possibles"))
zoom(s, t_mot(348), 960, 520, 1.0)
for k in range(3):
    saut(s, f"s26-ia{k}", t_mot(349) + k * 0.12, 26)
s.ecrire()

# ---------------------------------------------------------------- S27 : un véritable exécutant numérique
s = scene(26, "Scène 27 · « L'IA ne sert plus seulement à répondre à tes questions. Elle peut aussi devenir un véritable exécutant numérique. »")
plein_cadre(s, "s27-plein", "data-center", round(s.fin - s.debut, 2), 0.55)
cam(s, '<div id="s27-rep" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 200px; text-align: center; font-size: 100px; color: #ECECE8; '
       'text-shadow: none; opacity: 0">Répondre à tes questions<i id="s27-r" style="position: absolute; left: 380px; right: 380px; top: 46%; height: 12px; background: #DCFC1C"></i></div>')
cam(s, '<div id="s27-t1" class="pj-serif" style="left: 0; width: 1920px; top: 170px; font-size: 90px; text-align: center; opacity: 0">Un véritable</div>')
cam(s, '<div id="s27-t2" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 290px; text-align: center; font-size: 170px; opacity: 0">Exécutant numérique</div>')
cam(s, perso("s27-toi", 700, 800, 330))
cam(s, perso("s27-ia", 1220, 800, 330, "ia"))
s.add(hud_g("s27-hud", "Demain", "L'IA qui agit"))
s.j('tl.set("#s27-r", { scaleX: 0, transformOrigin: "0% 50%" }, 0);')
vit(s, "s27-toi", s.debut, s.fin - 0.9)
vit(s, "s27-ia", s.debut, s.fin - 0.9)
s.apparait("#s27-rep", t_mot(355), 20)
son(t_mot(355), "swoosh-accent", 0.36, "répondre")
s.j(f'tl.to("#s27-r", {{ scaleX: 1, duration: 0.16 }}, {s.L(t_mot(358))});')
son(t_mot(358), "fouet", 0.4, "rayé")
non(s, "s27-ia", t_mot(358))
s.cache("#s27-rep", t_mot(361) - 0.1)
s.apparait("#s27-t1", t_mot(366), 20)
s.choc("#s27-t2", t_mot(367))
s.eclair(t_mot(367))
son(t_mot(367), "impact-whoosh", 0.55, "EXÉCUTANT NUMÉRIQUE")
grossit(s, "s27-ia", t_mot(363), 1.15)
son(t_mot(363), "power-up", 0.4, "l'agent grandit")
zoom(s, t_mot(362), 960, 460, 1.1)
victoire(s, "s27-toi", t_mot(367) + 0.2, 2)
victoire(s, "s27-ia", t_mot(367) + 0.3, 2)
confettis(s, "s27-conf", t_mot(368) + 0.2, 960, 420)
son(t_mot(368) + 0.2, "fanfare", 0.4, "final")
s.ecrire()

# ================================================================ SONS GÉNÉRAUX
for k, c in enumerate(COUPES[1:-1], start=1):
    son(c, tour(TRANSITIONS), 0.46, f"transition vers {NOMS[k]}")
son(t_mot(50), "riser-trailer", 0.32, "montée vers science-fiction")
son(t_mot(76), "riser-synth", 0.3, "montée vers l'étape 1")
son(t_mot(267), "riser-tech", 0.3, "montée vers ET VOILÀ")
son(t_mot(367), "riser-trailer", 0.32, "montée vers EXÉCUTANT NUMÉRIQUE")

MUSIQUES = [  # (début, fichier, durée, volume) — fichiers à −16,9 LUFS ; 0,63 ≈ −21 LUFS (≈ 6 dB sous la voix) :
    # l'utilisateur après la vidéo 3 : « c'est la musique qu'il faut baisser » (très légèrement) → −2 dB
    (0, "partie-1-digital-clouds", 25.9, 0.63),
    (25.1, "partie-2-tech-house", 61.4, 0.63),
    (86.0, "partie-3-positive-energy", 44.3, 0.63),
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
