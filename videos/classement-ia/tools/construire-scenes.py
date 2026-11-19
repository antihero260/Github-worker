#!/usr/bin/env python3
"""Écrit les 20 scènes de « classement-ia » (classement des IA de S à C), le montage (index.html) et le cadre.

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


FIN = 120.2
COUPES = [0] + [b(i) for i in (21, 45, 51, 61, 76, 102, 131, 137, 147, 174, 188, 193, 201, 218, 236, 243, 264, 278, 301)] + [FIN]
NOMS = ["s01-une-seule", "s02-classement", "s03-cat-conversation", "s04-rang-s-chat", "s05-pourquoi-s", "s06-rang-a-chat",
        "s07-grok", "s08-cat-images", "s09-rang-s-images", "s10-trio-images", "s11-rang-a-images", "s12-cat-videos", "s13-rang-s-videos",
        "s14-sequences", "s15-runway", "s16-cat-audio", "s17-voix-musique", "s18-rang-s-audio", "s19-rang-c", "s20-a-toi"]
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


# ================================================================ SCÈNES
def demi(i):
    return round(t_mot(i) - 0.1, 2)


APPS = ["chatgpt", "claude", "gemini", "deepseek", "perplexity", "grok", "midjourney", "kling", "runway", "elevenlabs", "suno", "recraft"]

# ---------------------------------------------------------------- S1 : n'en garder qu'une
s = scene(0, "Scène 1 · « Si tu devais supprimer toutes les applications d'IA de ton téléphone et n'en garder qu'une seule… »")
panneau(s, "s01-vid", 113, 250, 600, 338, ("video", "bureau-tel", 0, round(s.fin - s.debut, 2)), "Ton téléphone")
s.montre("#s01-vid", 0)
cam(s, perso("s01-toi", 960, 800, 380))
ecran_apps(s, "s01-tel", 1320, 100, APPS)
s.add(hud_g("s01-hud", "Choix impossible", "Une seule IA"))
vit(s, "s01-toi", 0, s.fin - 0.2)
for k in range(len(APPS)):
    s.j(f'tl.to("#s01-tel-a{k}", {{ keyframes: [{{ rotation: -8, duration: 0.07 }}, {{ rotation: 8, duration: 0.07 }}, {{ rotation: -6, duration: 0.07 }}, {{ rotation: 0, duration: 0.07 }}] }}, {s.L(t_mot(3) + 0.05)});')
son(t_mot(3), "robot-elec", 0.35, "les applis tremblent")
panique(s, "s01-toi", t_mot(4), 0.9)
for k in range(len(APPS)):
    g = t_mot(4) + 0.12 + k * 0.1
    s.j(f'tl.to("#s01-tel-a{k}", {{ y: 600, rotation: {(k * 37) % 60 - 30}, opacity: 0, duration: 0.4, ease: "power2.in" }}, {s.L(g)});')
    if k % 2 == 0:
        son(g, tour(["pop-sec", "papier-glisse", "pop-long"]), 0.32, "appli supprimée")
s.claque("#s01-tel-q", t_mot(15), 2)
son(t_mot(15), "impact-cartoon", 0.5, "une seule")
zoom(s, t_mot(16), 1530, 380, 1.4)
gratte(s, "s01-toi", t_mot(17))
son(t_mot(18), "swell-court", 0.35, "laquelle ?")
s.ecrire()

# ---------------------------------------------------------------- S2 : le classement de S à C
s = scene(1, "Scène 2 · « Aujourd'hui, je classe les IA les plus populaires de S à C. Et je te préviens… »")
cam(s, projecteur(330) + projecteur(560, op=0.8))
cam(s, perso("s02-toi", 330, 800, 380))
cam(s, perso("s02-ia", 560, 800, 330, "ia"))
t2 = Tableau(s, "s02-t")
cam(s, '<div id="s02-titre" class="pj-serif" style="left: 700px; top: 120px; font-size: 80px; opacity: 0">Les IA les plus populaires</div>')
tampon(s, "s02-att", "Attention", 980, 640, t_mot(37), -6, 96)
s.add(hud_g("s02-hud", "Aujourd'hui", "Le classement des IA"))
vit(s, "s02-toi", s.debut, s.fin - 0.2)
vit(s, "s02-ia", s.debut, s.fin - 0.2)
parle(s, "s02-toi", t_mot(21), t_mot(23))
s.apparait("#s02-titre", t_mot(25), 20)
s.cache("#s02-titre", t_mot(29) - 0.1)
t2.apparait(t_mot(29), 0.09)
zoom(s, t_mot(29) - 0.12, 1250, 480, 1.08)
pose(s, "s02-toi", t_mot(30), 0.16, "back.out(2)", bd=-110, tete=-8)
saut(s, "s02-ia", t_mot(32), 26)
pose(s, "s02-toi", t_mot(36), 0.14, bd=0, tete=0)
bras_croises(s, "s02-toi", t_mot(37))
son(t_mot(37), "impact-basse", 0.5, "ATTENTION")
zoom(s, t_mot(37) - 0.1, 1100, 560, 1.15)
non(s, "s02-ia", t_mot(42))
acquiesce(s, "s02-toi", t_mot(43), 2)
s.ecrire()

# ---------------------------------------------------------------- S3 : catégorie 1, IA conversationnelles
s = scene(2, "Scène 3 · « On commence avec les IA conversationnelles. »")
categorie(s, "s03", 1, "Conversationnelles", "homme-ordi", t_mot(49))
s.add(hud_g("s03-hud", "Catégorie 1", "Les IA qui discutent"))
zoom(s, t_mot(50) + 0.2, 960, 480, 1.1)
s.ecrire()

# ---------------------------------------------------------------- S4 : S = ChatGPT, Claude, Gemini
s = scene(3, "Scène 4 · « Dans le rang S, je place ChatGPT, Claude et Gemini. »")
cam(s, projecteur(380))
cam(s, perso("s04-toi", 380, 800, 400))
t4 = Tableau(s, "s04-t")
montre_tableau(s, "s04-t")
s.add(hud_g("s04-hud", "Rang S", "Les incontournables"))
vit(s, "s04-toi", s.debut, s.fin - 0.2)
t4.surligne("S", t_mot(53))
zoom(s, t_mot(53) - 0.12, 1250, t4.centre("S")[1] + 60, 1.25)
pose(s, "s04-toi", t_mot(55), 0.16, "back.out(2)", bd=-120, tete=-8)
for cle, i in (("chatgpt", 57), ("claude", 58), ("gemini", 60)):
    t4.place(cle, "S", t_mot(i))
saut(s, "s04-toi", t_mot(57), 26)
saut(s, "s04-toi", t_mot(58), 26)
victoire(s, "s04-toi", t_mot(60), 1)
s.ecrire()

# ---------------------------------------------------------------- S5 : pourquoi ces trois-là
s = scene(4, "Scène 5 · « Pour leur polyvalence, leur capacité à raisonner, rédiger, analyser et accomplir des tâches très différentes. »")
panneau(s, "s05-vid", 113, 230, 760, 428, ("video", "recherche-ordi", 0, round(s.fin - s.debut, 2)), "Polyvalentes")
cam(s, perso("s05-ia", 1600, 800, 330, "ia"))
qualites = (("Polyvalence", 63, 1100, 240), ("Raisonner", 67, 1500, 240), ("Rédiger", 68, 1100, 370), ("Analyser", 69, 1500, 370),
            ("Accomplir", 71, 1300, 500))
for k, (m, i, x, y) in enumerate(qualites):
    puce(s, f"s05-q{k}", m, x, y, t_mot(i), "font-size: 50px")
s.add(hud_g("s05-hud", "Pourquoi le rang S", "Elles savent tout faire"))
s.apparait("#s05-vid", s.debut + 0.05, 40)
vit(s, "s05-ia", s.debut, s.fin - 0.2)
for k, (m, i, x, y) in enumerate(qualites):
    son(t_mot(i), tour(["pop-bulle", "pop-click", "pop-cartoon", "bouton-tech", "pop-long"]), 0.4, m)
parle(s, "s05-ia", t_mot(61), t_mot(64))
pose(s, "s05-ia", t_mot(67), 0.14, "back.out(2)", bg=150, tete=8)
tape(s, "s05-ia", t_mot(68), t_mot(70))
victoire(s, "s05-ia", t_mot(72), 2)
zoom(s, t_mot(63) - 0.12, 1250, 330, 1.2)
zoom(s, t_mot(68) - 0.12, 1300, 400, 1.15)
son(t_mot(68), "clavier-ordi", 0.3, "rédiger", d=0.6, sur_pic=False)
zoom(s, t_mot(73), 960, 520, 1.0)
s.ecrire()

# ---------------------------------------------------------------- S6 : A = DeepSeek et Perplexity
s = scene(5, "Scène 6 · « Dans le rang A, je mets DeepSeek et Perplexity : raisonnement… recherche d'informations avec des sources. »")
cam(s, projecteur(380))
cam(s, perso("s06-toi", 380, 800, 400))
t6 = Tableau(s, "s06-t")
montre_tableau(s, "s06-t")
for cle in ("chatgpt", "claude", "gemini"):
    t6.place(cle, "S")
ds = t6.place("deepseek", "A", t_mot(82))
px = t6.place("perplexity", "A", t_mot(84))
cx_ds, cy_a = 700 + 130 + 14 + 75, t6.centre("A")[1]
puce(s, "s06-p1", "Raisonnement", 1400, cy_a - 30, t_mot(92), "font-size: 42px")
puce(s, "s06-p2", "Recherche + sources", 1400, cy_a + 50, t_mot(97), "font-size: 42px")
s.add(hud_g("s06-hud", "Rang A", "Très bonnes, spécialisées"))
vit(s, "s06-toi", s.debut, s.fin - 0.2)
t6.surligne("A", t_mot(78))
zoom(s, t_mot(78) - 0.12, 1250, cy_a, 1.25)
pose(s, "s06-toi", t_mot(80), 0.16, "back.out(2)", bd=-110, tete=-8)
saut(s, "s06-toi", t_mot(82), 24)
saut(s, "s06-toi", t_mot(84), 24)
brille(s, f"#{ds}", t_mot(86))
son(t_mot(86), "magie", 0.35, "le premier")
zoom(s, t_mot(86) - 0.1, 1150, cy_a, 1.35)
son(t_mot(92), "pop-bulle", 0.4, "raisonnement")
brille(s, f"#{px}", t_mot(94))
son(t_mot(94), "magie", 0.35, "le second")
zoom(s, t_mot(94) - 0.1, 1350, cy_a, 1.3)
son(t_mot(97), "radar", 0.3, "recherche", d=1.2, sur_pic=False)
pose(s, "s06-toi", t_mot(95), 0.14, bd=0, tete=0)
acquiesce(s, "s06-toi", t_mot(99), 2)
s.ecrire()

# ---------------------------------------------------------------- S7 : Grok en B
s = scene(6, "Scène 7 · « Et Grok ? Je le place en B… l'actualité et X, mais je ne le choisirais pas comme assistant principal. »")
cam(s, projecteur(380))
cam(s, perso("s07-toi", 380, 800, 400))
t7 = Tableau(s, "s07-t")
montre_tableau(s, "s07-t")
for cle in ("chatgpt", "claude", "gemini"):
    t7.place(cle, "S")
for cle in ("deepseek", "perplexity"):
    t7.place(cle, "A")
cam(s, carte_logo("s07-grok-l", "grok", 1240, 450, 240))
cam(s, '<div id="s07-q" class="pj-impact" style="position: absolute; left: 1510px; top: 440px; font-size: 200px; opacity: 0">?</div>')
gk = t7.place("grok", "B", t_mot(108))
panneau(s, "s07-vid", 1200, 600, 420, 236, ("video", "planete-actus", 0, round(s.fin - s.debut, 2)), "Actualité + X")
tampon(s, "s07-pas", "Pas en principal", 1300, 125, t_mot(127), -4, 64)
s.add(hud_g("s07-hud", "Rang B", "Grok"))
vit(s, "s07-toi", s.debut, s.fin - 0.2)
s.claque("#s07-grok-l", t_mot(103), 1.8)
s.claque("#s07-q", t_mot(103) + 0.15, 2)
son(t_mot(103), "surprise-cartoon", 0.4, "Grok ?")
zoom(s, t_mot(103) - 0.12, 1300, 560, 1.15)
gratte(s, "s07-toi", t_mot(103))
s.cache("#s07-grok-l", t_mot(108) - 0.15)
s.cache("#s07-q", t_mot(108) - 0.15)
zoom(s, t_mot(107), 1250, t7.centre("B")[1], 1.2)
t7.surligne("B", t_mot(107))
pose(s, "s07-toi", t_mot(108), 0.16, "back.out(2)", bd=-100, tete=-6)
s.glisse("#s07-vid", t_mot(117), 300)
son(t_mot(117), "notif-indice", 0.4, "actualité")
zoom(s, t_mot(117) - 0.1, 1250, 560, 1.05)
non(s, "s07-toi", t_mot(123))
pose(s, "s07-toi", t_mot(121), 0.14, bd=0, tete=0)
son(t_mot(127), "buzz-faux", 0.38, "pas en principal")
zoom(s, t_mot(126), 1150, 420, 1.05)
haussement(s, "s07-toi", t_mot(127))
s.ecrire()

# ---------------------------------------------------------------- S8 : catégorie 2, images
s = scene(7, "Scène 8 · « Maintenant, passons à la génération d'images. »")
categorie(s, "s08", 2, "Images", "peinture", t_mot(135))
s.add(hud_g("s08-hud", "Catégorie 2", "Générer des images"))
zoom(s, t_mot(136), 960, 480, 1.1)
s.ecrire()

# ---------------------------------------------------------------- S9 : S = Midjourney, Nano Banana, ChatGPT Images
s = scene(8, "Scène 9 · « En S, je mets Midjourney, Nano Banana et ChatGPT Images. »")
cam(s, projecteur(380))
cam(s, perso("s09-toi", 380, 800, 400))
t9 = Tableau(s, "s09-t")
montre_tableau(s, "s09-t")
s.add(hud_g("s09-hud", "Rang S", "Images"))
vit(s, "s09-toi", s.debut, s.fin - 0.2)
t9.surligne("S", t_mot(137))
zoom(s, t_mot(137) - 0.12, 1250, t9.centre("S")[1] + 60, 1.25)
for cle, i in (("midjourney", 141), ("nanobanana", 142), ("chatgptimg", 145)):
    t9.place(cle, "S", t_mot(i))
pose(s, "s09-toi", t_mot(139), 0.16, "back.out(2)", bd=-120, tete=-8)
saut(s, "s09-toi", t_mot(141), 26)
saut(s, "s09-toi", t_mot(143), 26)
victoire(s, "s09-toi", t_mot(145), 1)
s.ecrire()

# ---------------------------------------------------------------- S10 : pourquoi ces trois-là
s = scene(9, "Scène 10 · « Midjourney pour son rendu artistique, Nano Banana pour la génération et la retouche, ChatGPT Images… »")
d10 = round(s.fin - s.debut, 2)
trio = (("midjourney", "palette", "Rendu artistique", 147), ("nanobanana", "tablette-dessin", "Génération + retouche", 152),
        ("chatgptimg", "retouche-ecran", "Suit tes instructions", 161))
for k, (cle, v, lab, i) in enumerate(trio):
    x = 113 + k * 577
    panneau(s, f"s10-v{k}", x, 250, 540, 304, ("video", v, 0, d10), lab, piste=5 + k)
    cam(s, carte_logo(f"s10-l{k}", cle, x + 380, 470, 150))
    s.glisse(f"#s10-v{k}", t_mot(i), 260)
    s.claque(f"#s10-l{k}", t_mot(i) + 0.25, 1.8)
    son(t_mot(i), tour(["souffle-cine", "swoosh-vol", "souffle-rapide"]), 0.42, lab)
    son(t_mot(i) + 0.25, "pop-click", 0.4, "logo")
    zoom(s, t_mot(i) - 0.12, x + 270, 420, 1.2)
cam(s, perso("s10-toi", 900, 800, 220))
s.add(hud_g("s10-hud", "Pourquoi", "Chacune son talent"))
vit(s, "s10-toi", s.debut, s.fin - 0.2)
son(t_mot(151), "magie", 0.35, "artistique")
son(t_mot(159), "lumiere", 0.3, "retouche")
pose(s, "s10-toi", t_mot(152), 0.16, "back.out(2)", bg=110, tete=6)
pose(s, "s10-toi", t_mot(161), 0.14, bg=0, tete=0)
acquiesce(s, "s10-toi", t_mot(167), 2)
zoom(s, t_mot(170), 960, 520, 1.0)
pouce(s, "s10-toi", t_mot(171))
s.ecrire()

# ---------------------------------------------------------------- S11 : A = Adobe Firefly, Recraft
s = scene(10, "Scène 11 · « Adobe Firefly et Recraft arrivent en A, notamment pour les usages créatifs et graphiques. »")
panneau(s, "s11-vid", 113, 250, 540, 304, ("video", "graphiste", 0, round(s.fin - s.debut, 2)), "Graphisme")
t11 = Tableau(s, "s11-t")
montre_tableau(s, "s11-t")
for cle in ("midjourney", "nanobanana", "chatgptimg"):
    t11.place(cle, "S")
t11.place("firefly", "A", t_mot(175), "Adobe Firefly")
t11.place("recraft", "A", t_mot(177))
cy = t11.centre("A")[1]
puce(s, "s11-p1", "Créatif", 1350, cy, t_mot(185), "font-size: 44px")
puce(s, "s11-p2", "Graphique", 1600, cy, t_mot(187), "font-size: 44px")
cam(s, perso("s11-toi", 380, 800, 230))
s.add(hud_g("s11-hud", "Rang A", "Création et graphisme"))
s.apparait("#s11-vid", s.debut + 0.05, 40)
vit(s, "s11-toi", s.debut, s.fin - 0.2)
t11.surligne("A", t_mot(174) - 0.2)
zoom(s, t_mot(174) - 0.3, 1250, cy, 1.22)
pose(s, "s11-toi", t_mot(175), 0.16, "back.out(2)", bd=-120, tete=-6)
saut(s, "s11-toi", t_mot(177), 24)
son(t_mot(185), "pop-bulle", 0.4, "créatif")
son(t_mot(187), "pop-cartoon", 0.4, "graphique")
zoom(s, t_mot(184), 1400, cy, 1.3)
s.ecrire()

# ---------------------------------------------------------------- S12 : catégorie 3, vidéos
s = scene(11, "Scène 12 · « Pour la génération de vidéos, »")
categorie(s, "s12", 3, "Vidéos", "tournage", t_mot(190))
s.add(hud_g("s12-hud", "Catégorie 3", "Générer des vidéos"))
son(t_mot(190) + 0.4, "photo", 0.4, "caméra")
s.ecrire()

# ---------------------------------------------------------------- S13 : S = Kling, Seedance
s = scene(12, "Scène 13 · « le rang S revient à Kling et Seedance. »")
cam(s, projecteur(380))
cam(s, perso("s13-toi", 380, 800, 400))
t13 = Tableau(s, "s13-t")
montre_tableau(s, "s13-t")
s.add(hud_g("s13-hud", "Rang S", "Vidéo"))
vit(s, "s13-toi", s.debut, s.fin - 0.2)
t13.surligne("S", t_mot(195))
zoom(s, t_mot(194) - 0.12, 1150, t13.centre("S")[1] + 40, 1.3)
t13.place("kling", "S", t_mot(198))
t13.place("seedance", "S", t_mot(200))
pose(s, "s13-toi", t_mot(196), 0.16, "back.out(2)", bd=-120, tete=-8)
victoire(s, "s13-toi", t_mot(200), 1)
s.ecrire()

# ---------------------------------------------------------------- S14 : texte, image, vidéo → séquence
s = scene(13, "Scène 14 · « Deux outils impressionnants pour créer des séquences à partir de textes, d'images et même de références vidéo. »")
panneau(s, "s14-vid", 113, 230, 700, 394, ("video", "camera-retro", 0, round(s.fin - s.debut, 2)), "Impressionnants")
for k, (m, i) in enumerate((("Texte", 211), ("Image", 212), ("Vidéo", 216))):
    puce(s, f"s14-e{k}", m, 1000, 280 + k * 110, t_mot(i), "font-size: 48px")
cam(s, '<div id="s14-fl" style="position: absolute; left: 1120px; top: 380px; width: 200px; height: 18px; background: #DCFC1C; transform-origin: 0% 50%"></div>')
cam(s, f'<div id="s14-seq" class="pj-sticker" style="left: 1360px; top: 340px; font-size: 70px; opacity: 0">Séquence</div>')
cam(s, perso("s14-ia", 1560, 800, 280, "ia"))
s.add(hud_g("s14-hud", "Kling et Seedance", "Du texte à la vidéo"))
s.j('tl.set("#s14-fl", { scaleX: 0 }, 0);')
s.apparait("#s14-vid", s.debut + 0.05, 40)
vit(s, "s14-ia", s.debut, s.fin - 0.2)
son(t_mot(203), "magie", 0.38, "impressionnants")
zoom(s, t_mot(203) - 0.1, 470, 430, 1.15)
for k, i in enumerate((211, 212, 216)):
    son(t_mot(i), tour(["pop-bulle", "pop-click", "pop-long"]), 0.4, "entrée")
zoom(s, t_mot(211) - 0.12, 1250, 420, 1.15)
s.j(f'tl.to("#s14-fl", {{ scaleX: 1, duration: 0.3, ease: "power2.out" }}, {s.L(t_mot(216) + 0.2)});')
son(t_mot(216) + 0.25, "swoosh-vitesse", 0.4, "transformation")
s.claque("#s14-seq", t_mot(217) + 0.1, 1.8)
son(t_mot(217) + 0.1, "impact-cartoon", 0.45, "séquence")
pose(s, "s14-ia", t_mot(211), 0.16, "back.out(2)", bg=110, tete=8)
victoire(s, "s14-ia", t_mot(217), 1)
s.ecrire()

# ---------------------------------------------------------------- S15 : Runway en A
s = scene(14, "Scène 15 · « Runway se place en A, particulièrement intéressant pour les créateurs qui veulent davantage de contrôle sur leurs plans. »")
panneau(s, "s15-vid", 113, 250, 540, 304, ("video", "equipe-tournage", 0, round(s.fin - s.debut, 2)), "Créateurs")
t15 = Tableau(s, "s15-t")
montre_tableau(s, "s15-t")
for cle in ("kling", "seedance"):
    t15.place(cle, "S")
t15.place("runway", "A", t_mot(218))
cy = t15.centre("A")[1]
puce(s, "s15-p", "Contrôle des plans", 1400, cy, t_mot(232), "font-size: 44px")
cam(s, perso("s15-toi", 380, 800, 230))
s.add(hud_g("s15-hud", "Rang A", "Plus de contrôle"))
s.apparait("#s15-vid", s.debut + 0.05, 40)
vit(s, "s15-toi", s.debut, s.fin - 0.2)
t15.surligne("A", t_mot(220))
zoom(s, t_mot(218) - 0.15, 1150, cy, 1.25)
pose(s, "s15-toi", t_mot(219), 0.16, "back.out(2)", bd=-120, tete=-6)
son(t_mot(232), "switch-basse", 0.42, "contrôle")
zoom(s, t_mot(231), 1300, cy, 1.2)
acquiesce(s, "s15-toi", t_mot(227), 2)
s.ecrire()

# ---------------------------------------------------------------- S16 : catégorie 4, audio
s = scene(15, "Scène 16 · « Enfin, l'audio ! Ici, deux noms se démarquent : »")
categorie(s, "s16", 4, "Audio", "micro", t_mot(237))
s.add(hud_g("s16-hud", "Catégorie 4", "Voix et musique"))
zoom(s, t_mot(240), 960, 480, 1.1)
s.ecrire()

# ---------------------------------------------------------------- S17 : ElevenLabs et Suno
s = scene(16, "Scène 17 · « ElevenLabs pour générer des voix artificielles très expressives, et Suno pour créer de véritables morceaux de musique… »")
d17 = round(s.fin - s.debut, 2)
for k, (cle, v, lab, i, x) in enumerate((("elevenlabs", "studio-voix", "Voix expressives", 243, 113), ("suno", "producteur", "Vraie musique", 252, 1010))):
    panneau(s, f"s17-v{k}", x, 230, 800, 450, ("video", v, 0, d17), lab, piste=5 + k)
    cam(s, carte_logo(f"s17-l{k}", cle, x + 620, 520, 170))
    s.glisse(f"#s17-v{k}", t_mot(i) - 0.1, 300 if k else -300)
    s.claque(f"#s17-l{k}", t_mot(i) + 0.2, 1.8)
    son(t_mot(i) - 0.1, tour(["souffle-cine", "swoosh-vol"]), 0.42, lab)
    son(t_mot(i) + 0.2, "pop-click", 0.4, "logo")
barres_son = "".join(f'<i class="s17-onde" style="display: inline-block; width: 14px; height: {40 + (k * 37) % 80}px; margin: 0 5px; background: #DCFC1C; '
                     f'vertical-align: middle; transform-origin: 50% 50%"></i>' for k in range(16))
cam(s, f'<div id="s17-ondes" style="position: absolute; left: 150px; top: 560px; opacity: 0">{barres_son}</div>')
notes = "".join(f'<b class="s17-note" style="position: absolute; left: {1060 + k * 150}px; top: {560 - (k % 2) * 40}px; opacity: 0"><svg viewBox="0 0 40 60" style="width: 60px; height: 90px"><ellipse cx="13" cy="48" rx="12" ry="9" fill="#DCFC1C" /><rect x="22" y="4" width="5" height="44" fill="#DCFC1C" /><path d="M27 4 Q40 12 36 26" stroke="#DCFC1C" stroke-width="5" fill="none" /></svg></b>' for k in range(4))
cam(s, notes)
s.add(hud_g("s17-hud", "Deux noms", "Voix et musique"))
zoom(s, t_mot(243) - 0.2, 513, 450, 1.2)
s.apparait("#s17-ondes", t_mot(245), 10)
s.j(f'tl.fromTo(".s17-onde", {{ scaleY: 0.3 }}, {{ scaleY: 1.2, duration: 0.18, repeat: 11, yoyo: true, stagger: 0.04, ease: "sine.inOut", immediateRender: false }}, {s.L(t_mot(245))});')
son(t_mot(247), "robot-scifi", 0.3, "voix artificielle")
son(t_mot(249), "aura", 0.3, "expressives")
zoom(s, t_mot(252) - 0.2, 1410, 450, 1.2)
s.j(f'tl.fromTo(".s17-note", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: -40, duration: 0.5, stagger: 0.25, ease: "power1.out", immediateRender: false }}, {s.L(t_mot(257))});')
son(t_mot(257), "notif-magique", 0.38, "musique")
zoom(s, t_mot(261), 960, 520, 1.0)
s.ecrire()

# ---------------------------------------------------------------- S18 : les deux en S
s = scene(17, "Scène 18 · « Pour moi, les deux méritent le rang S, mais pas pour les mêmes raisons. »")
cam(s, projecteur(380))
cam(s, perso("s18-toi", 380, 800, 400))
t18 = Tableau(s, "s18-t")
montre_tableau(s, "s18-t")
t18.place("elevenlabs", "S", t_mot(270))
t18.place("suno", "S", t_mot(271))
cy = t18.centre("S")[1]
puce(s, "s18-p1", "Voix", 1300, cy, t_mot(275), "font-size: 44px")
puce(s, "s18-p2", "Musique", 1500, cy, t_mot(277), "font-size: 44px")
s.add(hud_g("s18-hud", "Rang S", "Deux raisons différentes"))
vit(s, "s18-toi", s.debut, s.fin - 0.2)
t18.surligne("S", t_mot(269))
zoom(s, t_mot(269) - 0.15, 1150, cy + 60, 1.25)
parle(s, "s18-toi", t_mot(264), t_mot(268))
victoire(s, "s18-toi", t_mot(271), 1)
son(t_mot(275), "pop-bulle", 0.4, "voix")
son(t_mot(277), "pop-cartoon", 0.4, "musique")
s.ecrire()

# ---------------------------------------------------------------- S19 : le rang C reste vide
s = scene(18, "Scène 19 · « Et le rang C ? Je vais le laisser vide. Parce qu'un outil qui ne figure pas dans mon top n'est pas forcément mauvais. »")
TOUT = {"S": ["chatgpt", "claude", "gemini", "midjourney", "nanobanana", "chatgptimg", "kling", "seedance", "elevenlabs", "suno"],
        "A": ["deepseek", "perplexity", "firefly", "recraft", "runway"], "B": ["grok"]}


def grand_tableau(s, tid):
    t = Tableau(s, tid, x=200, y=200, w=1600, h=130, gap=10, tuile=(132, 112), etiquette=120)
    montre_tableau(s, tid)
    for r, cles in TOUT.items():
        for c in cles:
            t.place(c, r, nom={"chatgptimg": "GPT Images", "nanobanana": "Nano Banana", "firefly": "Firefly"}.get(c))
    return t


t19 = grand_tableau(s, "s19-t")
cyc = t19.centre("C")[1]
tampon(s, "s19-vide", "Vide", 860, cyc - 50, t_mot(286), -4, 90)
cam(s, perso("s19-toi", 1720, 800, 230))
cam(s, '<div id="s19-dit" class="pj-serif" style="left: 0; width: 1920px; top: 100px; text-align: center; font-size: 72px; opacity: 0">Pas dans le top, pas forcément mauvais</div>')
s.add(hud_g("s19-hud", "Rang C", "Laissé vide"))
vit(s, "s19-toi", s.debut, s.fin - 0.2)
t19.surligne("C", t_mot(280))
son(t_mot(286), "impact-cartoon", 0.5, "VIDE")
haussement(s, "s19-toi", t_mot(286))
s.apparait("#s19-dit", t_mot(297), 20)
son(t_mot(297), "swoosh-accent", 0.38, "pas forcément mauvais")
s.ecrire()

# ---------------------------------------------------------------- S20 : et toi ?
s = scene(19, "Scène 20 · « Voilà mon classement ! Maintenant, je veux voir le vôtre : quelle IA mérite le rang S… ? »")
t20 = grand_tableau(s, "s20-t")
cam(s, perso("s20-toi", 1720, 800, 260))
cam(s, '<div id="s20-q" class="pj-impact" style="position: absolute; left: 1560px; top: 110px; font-size: 200px; opacity: 0">?</div>')
tampon(s, "s20-ton", "Et ton classement ?", 760, 625, t_mot(307), -4, 70)
s.add(hud_g("s20-hud", "À toi", "Ton rang S en commentaire"))
vit(s, "s20-toi", s.debut, s.fin - 0.9)
son(t_mot(301), "fanfare", 0.4, "voilà mon classement")
confettis(s, "s20-conf", t_mot(302), 960, 300)
victoire(s, "s20-toi", t_mot(301), 2)
zoom(s, t_mot(304), 960, 440, 1.08)
pose(s, "s20-toi", t_mot(305), 0.16, "back.out(2)", bd=-80, tete=-6)
son(t_mot(307), "impact-basse", 0.45, "et ton classement ?")
s.claque("#s20-q", t_mot(310), 2)
son(t_mot(310), "pop-cartoon", 0.4, "question")
t20.surligne("S", t_mot(314))
gratte(s, "s20-toi", t_mot(317))
s.ecrire()

# ================================================================ SONS GÉNÉRAUX
for k, c in enumerate(COUPES[1:-1], start=1):
    son(c, tour(TRANSITIONS), 0.46, f"transition vers {NOMS[k]}")
son(t_mot(49), "riser-trailer", 0.3, "montée vers catégorie 1")
son(t_mot(135), "riser-synth", 0.3, "montée vers catégorie 2")
son(t_mot(190), "riser-trailer", 0.3, "montée vers catégorie 3")
son(t_mot(237), "riser-tech", 0.3, "montée vers catégorie 4")

MUSIQUES = [  # (début, fichier, durée, volume) — fichiers à −16,9 LUFS ; 0,63 ≈ −21 LUFS (≈ 6 dB sous la voix, réglage validé)
    (0, "partie-1-deep-urban", 50.2, 0.63),
    (49.4, "partie-2-cat-walk", 41.6, 0.63),
    (90.4, "partie-3-trapanomics", 29.8, 0.63),
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
