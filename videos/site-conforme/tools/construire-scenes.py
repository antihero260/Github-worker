#!/usr/bin/env python3
"""Écrit les 9 scènes de « site-conforme » (5 points à vérifier avant de publier ton site créé avec l'IA), le montage,
le cadre, les volets de transition et la check-list. Style « Alerte » (variante dynamique du style « Projecteur »).

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
VOL_SFX = 0.85  # 185 bruitages en 53 s (très dense) : −1,4 dB pour rester vers −20/−21 LUFS au total, comme le réglage validé


def b(i):
    """Coupure de scène juste avant le mot i."""
    return round(t_mot(i) - 0.12, 2)


FIN = 52.8
COUPES = [0] + [b(i) for i in (11, 27, 41, 61, 74, 92, 113, 127)] + [FIN]
NOMS = ["s01-publier", "s02-attention", "s03-mentions", "s04-confidentialite", "s05-cookies", "s06-cgv", "s07-droits",
        "s08-securite", "s09-final"]
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


# ================================================================ STYLE « ALERTE » : ÉLÉMENTS
import math
# Variante dynamique du style « Projecteur » : accent orange signal, coches vertes, fond « plan technique »,
# rubans de chantier, mots-chocs en glitch, secousses de caméra, volets rayés à chaque coupe, check-list en haut.
ACCENT = "#FF5A1F"
VERT = "#2FE38A"
P.TETES["visiteur"] = P.TETES["toi"]

TRIANGLE = ('<svg viewBox="0 0 40 36" width="34" height="30"><path d="M20 2 L38 34 L2 34 Z" fill="#0B0E14" />'
            '<rect x="18" y="12" width="4" height="12" fill="#FF5A1F" /><rect x="18" y="27" width="4" height="4" fill="#FF5A1F" /></svg>')
COCHE = '<svg viewBox="0 0 40 40" width="{w}" height="{w}"><path d="M8 21 L17 30 L33 11" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" /></svg>'
OEIL = ('<svg viewBox="0 0 80 50" width="80" height="50"><path d="M4 25 Q40 -8 76 25 Q40 58 4 25 Z" fill="none" stroke="currentColor" stroke-width="5" />'
        '<circle cx="40" cy="25" r="11" fill="currentColor" /></svg>')
CADENAS = ('<svg id="{id}" viewBox="0 0 120 150" style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; overflow: visible; opacity: 0">'
           '<g id="{id}-anse"><path d="M30 70 L30 42 Q30 12 60 12 Q90 12 90 42 L90 70" fill="none" stroke="#ECECE8" stroke-width="14" stroke-linecap="round" /></g>'
           '<rect x="14" y="66" width="92" height="76" rx="14" fill="#FF5A1F" /><circle cx="60" cy="98" r="10" fill="#0B0E14" />'
           '<rect x="56" y="100" width="8" height="22" rx="3" fill="#0B0E14" /></svg>')


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


def video_html(vid, video, d, piste=5, style=""):
    return (f'<video id="{vid}" class="clip" src="assets/video/{video}.mp4" data-start="0" data-duration="{d}" data-track-index="{piste}" '
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
    cam(s, f'<div id="{bid}" class="al-ok" style="left: {x}px; top: {y}px; font-size: {taille}px; opacity: 0">{COCHE.format(w=taille + 8, c="#0B0E14")}<span>{texte}</span></div>')
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


# ================================================================ SCÈNES
# ---------------------------------------------------------------- S1 : hook — mosaïque de vidéos qui explose, puis PUBLIER
s = scene(0, "Scène 1 · « Ton site créé avec l'IA est enfin prêt à être publié ? »")
d1 = round(s.fin - s.debut, 2)
MOSAIQUE = ["code-html", "web-design", "developpeur", "site-ia-3", "site-ia-0", "macbook", "tablette-web", "site-ia-6", "code-ecran",
            "laptop-homme", "site-ia-8", "bureau-web", "site-ia-1", "site-ia-9", "graphiste", "site-mode"]


def grille(n):
    """Positions des tuiles pour une grille de n tuiles (1, 2, 4, 9, 16)."""
    if n == 1:
        return [(0, 0, 1920, 1080)]
    if n == 2:
        return [(0, 0, 956, 1080), (964, 0, 956, 1080)]
    c = int(round(n ** 0.5))
    w, h = (1920 - (c - 1) * 8) / c, (1080 - (c - 1) * 8) / c
    return [(round((k % c) * (w + 8)), round((k // c) * (h + 8)), round(w), round(h)) for k in range(n)]


ETAPES = [(0.0, 1), (t_mot(1), 2), (t_mot(2), 4), (t_mot(3), 9), (t_mot(4), 16)]
FIN_MOS = t_mot(6) + 0.3
avant = 0
for j, (g, n) in enumerate(ETAPES):
    g_fin = ETAPES[j + 1][0] if j + 1 < len(ETAPES) else FIN_MOS
    for k, (x, y, w, h) in enumerate(grille(n)):
        tid = f"s01-m{j}-{k}"
        cam(s, f'<div id="{tid}" class="al-tuile" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0">'
               f'<video id="{tid}-v" class="clip" src="assets/video/{MOSAIQUE[k]}.mp4" data-start="{round(g, 2)}" data-duration="{round(g_fin - g + 0.05, 2)}" '
               f'data-track-index="{5 + k % 3}" muted playsinline style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover"></video></div>')
        if k < avant:  # tuile déjà là : elle reste, à sa nouvelle place
            s.j(f'tl.set("#{tid}", {{ opacity: 1 }}, {s.L(g)});')
        else:  # nouvelle tuile : surgit
            s.j(f'tl.fromTo("#{tid}", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.16, ease: "power4.out" }}, {s.L(g + (k - avant) * 0.012)});')
        if j + 1 < len(ETAPES):
            s.j(f'tl.set("#{tid}", {{ opacity: 0 }}, {s.L(g_fin + 0.02)});')
    son(g, tour(["glitch-mini", "glitch-court", "glitch-cine", "glitch-scifi", "glitch-data"]), 0.42, f"la mosaïque passe à {n}")
    son(g + 0.03, tour(["fouet", "swoosh-court", "declencheur", "souffle-rapide", "swoosh-accent"]), 0.4, "découpe")
    if n >= 4:
        son(g, tour(["impact-cartoon", "impact-futur", "impact-whoosh"]), 0.36, "choc de la mosaïque")
    avant = n
secousse(s, t_mot(4), 18)
s.eclair(t_mot(4))
# « enfin prêt » : la mosaïque éclate, le navigateur avec ton site arrive
g_nav = t_mot(6)
for k in range(16):
    ang = k * 2.39996
    s.j(f'tl.to("#s01-m4-{k}", {{ x: {round(math.cos(ang) * 1500)}, y: {round(math.sin(ang) * 1000)}, rotation: {(k * 47) % 60 - 30}, opacity: 0, duration: 0.3, ease: "power3.in" }}, {s.L(g_nav - 0.05)});')
son(g_nav, "impact-whoosh", 0.5, "la mosaïque éclate")
corps_nav = (f'<div class="al-nav-video">{video_html("s01-site-v", "site-ia-2", d1)}</div>'
             '<div class="al-nav-pied"><span>ton-site-ia.fr</span><div id="s01-pub" class="al-bouton">Publier</div></div>')
navigateur(s, "s01-nav", 560, 170, 1100, 640, "ton-site-ia.fr", corps_nav)
s.j(f'tl.fromTo("#s01-nav", {{ opacity: 0, scale: 0.5, rotation: -6 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.26, ease: "back.out(1.8)" }}, {s.L(g_nav)});')
cam(s, perso("s01-toi", 330, 830, 330))
s.j(f'tl.set("#s01-toi", {{ x: -500 }}, 0);')
vit(s, "s01-toi", g_nav, s.fin - 0.2)
court(s, "s01-toi", g_nav, t_mot(7), 500)
son(g_nav + 0.1, "swoosh-vitesse", 0.36, "il arrive en courant")
victoire(s, "s01-toi", t_mot(7), 1)
son(t_mot(7), "power-up", 0.38, "prêt !")
souris(s, "s01-souris", 1760, 560)
s.j(f'tl.fromTo("#s01-souris", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {s.L(t_mot(7))});')
deplace(s, "s01-souris", t_mot(7) + 0.05, 1500, 745, 1760, 560, 0.5)
pose(s, "s01-toi", t_mot(9), 0.14, "back.out(2)", bd=-100, bg=0, tete=-6)
clic(s, "s01-souris", t_mot(10), "#s01-pub")
s.j(f'tl.to("#s01-pub", {{ backgroundColor: "{VERT}", duration: 0.1 }}, {s.L(t_mot(10))});')
zoom(s, t_mot(9) - 0.05, 1300, 660, 1.35)
# « publié ? » : décollage plein cadre
gros_plan(s, "s01-fusee", "fusee", d1, 0.55)
s.cache("#s01-nav", t_mot(10) + 0.3, 0.05)
s.j(f'tl.fromTo("#s01-fusee", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power3.out" }}, {s.L(t_mot(10) + 0.12)});')
son(t_mot(10) + 0.12, "fusee", 0.45, "décollage")
choc_mot(s, "s01-q", "En ligne ?", 330, 250, t_mot(10) + 0.2, coul="#FFFFFF")
secousse(s, t_mot(10) + 0.2, 14)
zoom(s, t_mot(10) + 0.12, 960, 540, 1.0, nom="zoom-out")
s.ecrire()

# ---------------------------------------------------------------- S2 : ATTENTION ! + les 5 points + mauvaises surprises
s = scene(1, "Scène 2 · « Attention ! Avant de le mettre en ligne, vérifie ces cinq points pour éviter de mauvaises surprises. »")
d2 = round(s.fin - s.debut, 2)
gros_plan(s, "s02-gyro", "gyrophare", d2, 0.35, op=1)
s.j(f'tl.to("#s02-gyro", {{ opacity: 0, duration: 0.2 }}, {s.L(t_mot(12) - 0.1)});')
alerte_rouge(s, "s02-alerte", t_mot(11), 3)
ruban(s, "s02-r1", 120, -7, "Attention", t_mot(11), 1, t_mot(12) - 0.1)
ruban(s, "s02-r2", 700, 6, "Attention", t_mot(11) + 0.06, -1, t_mot(12) - 0.06)
choc_mot(s, "s02-att", "Attention !", 330, 300, t_mot(11), fin=t_mot(12) - 0.08)
s.eclair(t_mot(11))
secousse(s, t_mot(11), 24)
secousse(s, t_mot(11) + 0.4, 12)
son(t_mot(11), "sirene", 0.5, "sirène ATTENTION")
son(t_mot(11), "impact-basse", 0.6, "ATTENTION")
son(t_mot(11) + 0.02, "glitch-rugit", 0.4, "glitch ATTENTION")
son(t_mot(12) - 0.08, "swoosh-tourbillon", 0.4, "les rubans repartent")
# « avant de le mettre en ligne » : l'interrupteur EN LIGNE, que le perso retient
corps2 = (f'<div class="al-nav-video">{video_html("s02-site-v", "site-ia-4", d2)}</div>'
          '<div class="al-nav-pied"><span>Mettre en ligne</span><div id="s02-inter" class="al-inter"><i id="s02-rond"></i></div></div>')
navigateur(s, "s02-nav", 150, 190, 860, 560, "ton-site-ia.fr", corps2)
s.j(f'tl.fromTo("#s02-nav", {{ opacity: 0, x: -400 }}, {{ opacity: 1, x: 0, duration: 0.24, ease: "power4.out" }}, {s.L(t_mot(12))});')
son(t_mot(12), "swoosh-vol", 0.38, "le site arrive")
cam(s, perso("s02-toi", 1300, 800, 300))
vit(s, "s02-toi", s.debut, s.fin - 0.2)
s.j(f'tl.fromTo("#s02-toi", {{ opacity: 0, x: 300 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "power3.out" }}, {s.L(t_mot(12))});')
pose(s, "s02-toi", t_mot(15), 0.14, "back.out(2.5)", bg=95, tete=-8)
s.j(f'tl.to("#s02-rond", {{ keyframes: [{{ x: 40, duration: 0.18 }}, {{ x: 0, duration: 0.14, ease: "back.out(3)" }}] }}, {s.L(t_mot(17))});')
son(t_mot(17), "erreur-clic", 0.45, "l'interrupteur est retenu")
non(s, "s02-toi", t_mot(17) + 0.05)
zoom(s, t_mot(16) - 0.1, 780, 650, 1.3)
zoom(s, t_mot(18) - 0.12, 960, 540, 1.0, nom="zoom-out")
# « vérifie ces cinq points » : la check-list
s.j(f'tl.to("#s02-nav", {{ x: -1300, opacity: 0, duration: 0.24, ease: "power3.in" }}, {s.L(t_mot(18) - 0.1)});')
lignes5 = "".join(f'<div id="s02-l{k}" class="al-ligne5" style="opacity: 0"><i id="s02-b{k}" class="al-case"></i><b>{k + 1}</b>'
                  f'<span style="width: {(380, 300, 340, 260, 320)[k]}px"></span></div>' for k in range(5))
cam(s, f'<div id="s02-liste" class="al-liste" style="left: 200px; top: 170px">'
       f'<div class="al-liste-tete">Avant de publier</div>{lignes5}</div>')
s.j(f'tl.fromTo("#s02-liste", {{ opacity: 0, x: -200 }}, {{ opacity: 1, x: 0, duration: 0.2, ease: "power4.out" }}, {s.L(t_mot(18))});')
for k in range(5):
    s.j(f'tl.fromTo("#s02-l{k}", {{ opacity: 0, x: -80 }}, {{ opacity: 1, x: 0, duration: 0.14, ease: "power3.out" }}, {s.L(t_mot(18) + 0.12 + k * 0.08)});')
    pop(t_mot(18) + 0.12 + k * 0.08, 0.36, f"ligne {k + 1}")
choc_mot(s, "s02-cinq", "5", 170, 560, t_mot(20), x=1000, w=440)
son(t_mot(20), "impact-whoosh", 0.55, "CINQ")
secousse(s, t_mot(20), 14)
marche(s, "s02-toi", t_mot(18), t_mot(20), 330)
pose(s, "s02-toi", t_mot(20), 0.12, "back.out(2)", bg=150, bd=0, tete=-10)
for k in range(5):
    s.j(f'tl.fromTo("#s02-b{k}", {{ backgroundColor: "rgba(255, 90, 31, 0)" }}, {{ backgroundColor: "rgba(255, 90, 31, 0.9)", duration: 0.08, repeat: 1, yoyo: true, immediateRender: false }}, {s.L(t_mot(21) + k * 0.06)});')
son(t_mot(21), "compteur", 0.32, "les cases clignotent")
zoom(s, t_mot(21) - 0.05, 700, 470, 1.15)
# « mauvaises surprises » : les pop-ups d'erreur pleuvent
s.j(f'tl.to(["#s02-liste", "#s02-cinq"], {{ opacity: 0, scale: 0.6, duration: 0.16, ease: "power3.in" }}, {s.L(t_mot(23) - 0.05)});')
zoom(s, t_mot(23) - 0.1, 960, 540, 1.0, nom="zoom-out")
POPS2 = [("Erreur", "Site non conforme", 150, 180), ("Alerte", "Cookies non autorisés", 820, 140), ("Attention", "Données exposées", 110, 430),
         ("Erreur", "Image protégée", 700, 370), ("Alerte", "Plainte reçue", 1000, 520)]
for k, (t1, t2, x, y) in enumerate(POPS2):
    popup(s, f"s02-p{k}", t1, t2, x, y, t_mot(23) + 0.05 + k * 0.17)
choc_mot(s, "s02-surp", "Mauvaises surprises", 690, 150, t_mot(26) + 0.1, coul="#ECECE8")
secousse(s, t_mot(26) + 0.1, 18)
son(t_mot(26) + 0.1, "impact-basse", 0.5, "SURPRISES")
son(t_mot(23), "alarme-alerte", 0.32, "alarme des pop-ups")
panique(s, "s02-toi", t_mot(25), 0.9)
s.ecrire()

# ---------------------------------------------------------------- S3 : 1. mentions légales
s = scene(2, "Scène 3 · « Premièrement, les mentions légales : elles permettent d'identifier le propriétaire du site et son hébergeur. »")
d3 = round(s.fin - s.debut, 2)
numero(s, "s03-n", "01", t_mot(27), t_mot(29) - 0.3)
titre(s, "s03-titre", "Mentions légales", t_mot(29))
ecran(s, "s03-page", 113, 360, 760, 428, "sp-mentions", "service-public · la vraie page")
s.apparait("#s03-page", t_mot(30), 40)
son(t_mot(30), "declencheur", 0.4, "vraie page")
zoom(s, t_mot(31) - 0.05, 493, 574, 1.3)
scan(s, "s03-scan", 113, 360, 760, 428, t_mot(33))
zoom(s, t_mot(35) - 0.15, 960, 540, 1.0, nom="zoom-out")
proprio = ('<div class="al-id"><svg viewBox="0 0 100 100" width="110" height="110"><circle cx="50" cy="36" r="20" fill="#ECECE8" />'
           '<rect x="18" y="62" width="64" height="34" rx="16" fill="#ECECE8" /></svg>'
           '<div><p>Nom : <b style="width: 230px"></b></p><p>Adresse : <b style="width: 170px"></b></p><p>Contact : <b style="width: 200px"></b></p></div></div>')
carte(s, "s03-proprio", 1080, 330, 720, 220, "Propriétaire du site", proprio)
s.claque("#s03-proprio", t_mot(35), 1.4)
son(t_mot(35), "scanner-caisse", 0.3, "carte d'identité")
zoom(s, t_mot(35) - 0.05, 1440, 440, 1.25)
heb = (f'<div class="al-id"><div class="al-mini">{video_html("s03-dc-v", "data-center", d3)}</div>'
       '<div><p>Hébergeur : <b style="width: 200px"></b></p><p>Adresse : <b style="width: 170px"></b></p><p>Téléphone : <b style="width: 150px"></b></p></div></div>')
carte(s, "s03-heb", 1080, 580, 720, 220, "Hébergeur", heb)
s.claque("#s03-heb", t_mot(40), 1.4)
son(t_mot(40), "robot-elec", 0.35, "hébergeur")
zoom(s, t_mot(40) - 0.05, 1440, 690, 1.25)
guide(s, "s03-toi", t_mot(30) + 0.2, t_mot(35), t_mot(40) + 0.3)
s.ecrire()

# ---------------------------------------------------------------- S4 : 2. politique de confidentialité
s = scene(3, "Scène 4 · « Deuxièmement, la politique de confidentialité : explique aux visiteurs quelles données tu collectes, pourquoi et combien de temps tu les conserves. »")
d4 = round(s.fin - s.debut, 2)
numero(s, "s04-n", "02", t_mot(41), t_mot(43) - 0.3)
titre(s, "s04-titre", "Confidentialité", t_mot(45), sous="Politique de")
ecran(s, "s04-rgpd", 113, 360, 760, 428, "cnil-rgpd", "cnil.fr · la vraie page")
s.apparait("#s04-rgpd", t_mot(43), 40)
son(t_mot(43), "declencheur", 0.4, "page CNIL")
zoom(s, t_mot(45) + 0.3, 493, 574, 1.25)
zoom(s, t_mot(46), 960, 540, 1.0, nom="zoom-out")
for k, x in enumerate((1250, 1450, 1650)):
    cam(s, perso(f"s04-v{k}", x, 600, 190, "visiteur"))
    s.j(f'tl.fromTo("#s04-v{k}", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: "back.out(2)" }}, {s.L(t_mot(48) + k * 0.1)});')
    vit(s, f"s04-v{k}", t_mot(48), t_mot(55), 4, 0.36 + k * 0.04)
    pop(t_mot(48) + k * 0.1, 0.34, "visiteur")
puce(s, "s04-pv", "Visiteurs", 1450, 345, t_mot(48) + 0.3)
cam(s, '<div id="s04-dossier" class="al-dossier" style="left: 1560px; top: 640px; opacity: 0"><b>Données</b></div>')
s.claque("#s04-dossier", t_mot(49), 1.4)
for k, (m, x0, y0) in enumerate((("Nom", 1110, 660), ("E-mail", 1330, 660), ("Adresse IP", 1150, 770), ("Téléphone", 1390, 770))):
    g = t_mot(50) + k * 0.16
    puce(s, f"s04-c{k}", m, x0, y0, g)
    s.j(f'tl.to("#s04-c{k}", {{ x: {1660 - x0}, y: {700 - y0}, scale: 0.3, opacity: 0, duration: 0.3, ease: "power2.in" }}, {s.L(t_mot(52) + k * 0.1)});')
    son(t_mot(52) + k * 0.1, tour(["papier-glisse", "pop-sec", "souffle-air"]), 0.3, f"{m} rangé")
s.j(f'tl.to("#s04-dossier", {{ keyframes: [{{ scale: 1.15, duration: 0.08 }}, {{ scale: 1, duration: 0.12 }}] }}, {s.L(t_mot(53) - 0.1)});')
zoom(s, t_mot(49) - 0.1, 1440, 560, 1.15)
tampon(s, "s04-pq", "Pourquoi ?", 1150, 175, t_mot(53), -6, 76)
son(t_mot(53), "impact-cartoon", 0.45, "POURQUOI")
zoom(s, t_mot(53) - 0.1, 960, 540, 1.0, nom="zoom-out")
# « combien de temps » : la vraie page CNIL des durées + l'horloge
for k in range(3):
    s.cache(f"#s04-v{k}", t_mot(55) - 0.15)
s.cache("#s04-pv", t_mot(55) - 0.15)
s.cache("#s04-dossier", t_mot(55) - 0.15)
s.cache("#s04-pq", t_mot(55) - 0.15)
ecran(s, "s04-durees", 113, 360, 760, 428, "cnil-durees", "cnil.fr · durées de conservation", piste=7)
s.glisse("#s04-durees", t_mot(55), -300)
s.cache("#s04-rgpd", t_mot(55) + 0.2, 0.05)
panneau(s, "s04-horloge", 1060, 360, 760, 428, ("video", "horloge-temps", 0, d4), "Combien de temps ?", piste=8)
s.apparait("#s04-horloge", t_mot(55), 40)
son(t_mot(55), "tic-tac", 0.5, "combien de temps", d=1.9)
son(t_mot(55), "swoosh-monte", 0.36, "horloge")
zoom(s, t_mot(57), 1440, 574, 1.2)
zoom(s, t_mot(60) - 0.1, 493, 574, 1.25)
son(t_mot(60), "impact-tambour", 0.42, "conserves")
guide(s, "s04-toi", t_mot(43) + 0.2, t_mot(48), t_mot(53) + 0.2, t_mot(57))
s.ecrire()

# ---------------------------------------------------------------- S5 : 3. cookies
s = scene(4, "Scène 5 · « Troisièmement, les cookies : certains traceurs nécessitent le consentement des visiteurs avant leur activation. »")
d5 = round(s.fin - s.debut, 2)
numero(s, "s05-n", "03", t_mot(61), t_mot(62) - 0.25)
titre(s, "s05-titre", "Cookies", t_mot(63))
panneau(s, "s05-miam", 1060, 330, 760, 428, ("video", "cookie-casse", 0, d5), "Pas ceux-là !")
s.apparait("#s05-miam", t_mot(63), 40)
son(t_mot(63) + 0.15, "cookie-croque", 0.85, "croc !")
zoom(s, t_mot(63) - 0.05, 1440, 544, 1.2)
s.j(f'tl.to("#s05-miam", {{ keyframes: [{{ x: 18, skewX: 12, duration: 0.05 }}, {{ x: -14, skewX: -8, duration: 0.05 }}, {{ x: 0, skewX: 0, opacity: 0, duration: 0.08 }}] }}, {s.L(t_mot(64))});')
son(t_mot(64), "glitch-scifi", 0.4, "glitch : les vrais cookies")
ecran(s, "s05-sp", 1060, 330, 760, 428, "sp-cookies", "La vraie bannière · service-public", piste=7)
s.apparait("#s05-sp", t_mot(64) + 0.1, 30)
zoom(s, t_mot(64) + 0.05, 960, 540, 1.0, nom="zoom-out")
yeux = "".join(f'<div id="s05-o{k}" class="al-oeil" style="left: {60 + k * 180}px; top: 90px; opacity: 0">{OEIL}<span id="s05-e{k}">En attente</span><span id="s05-a{k}" class="al-actif" style="opacity: 0">Activé</span></div>' for k in range(4))
banniere = ('<div id="s05-ban" class="al-banniere"><p>Ce site utilise des cookies.</p>'
            '<div><span class="al-b2">Refuser</span><span class="al-b2">Personnaliser</span><span id="s05-ok" class="al-b1">Accepter</span></div></div>')
corps5 = f'<div class="al-nav-video">{video_html("s05-site-v", "site-ia-7", d5)}<div class="al-voile"></div>{yeux}</div>{banniere}'
navigateur(s, "s05-nav", 113, 330, 800, 470, "ton-site-ia.fr", corps5)
s.apparait("#s05-nav", t_mot(64) + 0.1, 40)
for k in range(4):
    s.j(f'tl.fromTo("#s05-o{k}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.5)" }}, {s.L(t_mot(65) + k * 0.12)});')
son(t_mot(65), "radar", 0.4, "traceurs")
puce(s, "s05-ptr", "Traceurs", 513, 640, t_mot(65))
s.cache("#s05-ptr", t_mot(68) - 0.1)
zoom(s, t_mot(65) - 0.1, 513, 520, 1.2)
s.j(f'tl.fromTo("#s05-ban", {{ y: 220 }}, {{ y: 0, duration: 0.3, ease: "back.out(1.6)" }}, {s.L(t_mot(68))});')
son(t_mot(68), "swoosh-monte", 0.42, "la bannière monte")
zoom(s, t_mot(68) + 0.1, 513, 700, 1.3)
souris(s, "s05-souris", 860, 560)
s.j(f'tl.fromTo("#s05-souris", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {s.L(t_mot(70))});')
deplace(s, "s05-souris", t_mot(70), 820, 760, 860, 560, 0.5)
clic(s, "s05-souris", t_mot(73), "#s05-ok")
for k in range(4):
    s.j(f'tl.to("#s05-o{k}", {{ color: "{ACCENT}", duration: 0.1 }}, {s.L(t_mot(73) + 0.1 + k * 0.06)});')
    s.j(f'tl.set("#s05-e{k}", {{ opacity: 0 }}, {s.L(t_mot(73) + 0.1 + k * 0.06)});')
    s.j(f'tl.set("#s05-a{k}", {{ opacity: 1 }}, {s.L(t_mot(73) + 0.1 + k * 0.06)});')
s.j(f'tl.to("#s05-ban", {{ y: 220, opacity: 0, duration: 0.2, ease: "power3.in" }}, {s.L(t_mot(73) + 0.35)});')
son(t_mot(73) + 0.1, "interrupteur", 0.45, "activation")
son(t_mot(73) + 0.2, "power-up", 0.36, "traceurs activés")
cam(s, perso("s05-toi", 966, 800, 230))
vit(s, "s05-toi", s.debut, s.fin - 0.2)
pose(s, "s05-toi", t_mot(63) + 0.1, 0.16, "back.out(2)", bd=-110, tete=-8)
pose(s, "s05-toi", t_mot(65), 0.16, "back.out(2)", bd=0, bg=110, tete=8)
pose(s, "s05-toi", t_mot(71), 0.12, "back.out(2.5)", bg=170, tete=0)
tampon(s, "s05-stop", "Avant !", 700, 322, t_mot(71), -5, 70)
son(t_mot(71), "impact-basse", 0.45, "AVANT")
s.cache("#s05-stop", t_mot(73) - 0.05)
victoire(s, "s05-toi", t_mot(73) + 0.2, 1)
s.ecrire()

# ---------------------------------------------------------------- S6 : 4. conditions générales de vente
s = scene(5, "Scène 6 · « Quatrièmement, les conditions générales de vente, si tu proposes des produits ou services à acheter en ligne. »")
d6 = round(s.fin - s.debut, 2)
numero(s, "s06-n", "04", t_mot(74), t_mot(76) - 0.25)
titre(s, "s06-titre", "Conditions générales de vente", t_mot(76), 84, y=185)
panneau(s, "s06-page", 113, 360, 760, 428, ("img", "sp-mentions-bas.jpg"), "service-public · la vraie page")
cam(s, '<div id="s06-surl" class="al-surligne" style="left: 244px; top: 690px; width: 480px; height: 58px; opacity: 0"></div>')
s.apparait("#s06-page", t_mot(77), 40)
son(t_mot(77), "declencheur", 0.4, "vraie page")
s.j(f'tl.fromTo("#s06-surl", {{ opacity: 0, scaleX: 0, transformOrigin: "0% 50%" }}, {{ opacity: 1, scaleX: 1, duration: 0.3 }}, {s.L(t_mot(79))});')
son(t_mot(79), "stylo", 0.42, "surligné")
zoom(s, t_mot(79) - 0.1, 330, 700, 1.6)
zoom(s, t_mot(80), 960, 540, 1.0, nom="zoom-out")
panneau(s, "s06-achat", 1060, 330, 760, 428, ("video", "achat-laptop", 0, d6), "Vente en ligne", piste=7)
s.apparait("#s06-achat", t_mot(76) + 0.2, 40)
son(t_mot(76) + 0.2, "swoosh-vol", 0.36, "achat en ligne")
lignes_p = ''.join(f'<div id="s06-pr{k}" class="al-produit" style="opacity: 0"><i style="background: {c}"></i><span>{m}</span><b>{p}</b></div>'
                   for k, (m, p, c) in enumerate((("Produit", "29,00 €", "#6366F1"), ("Service", "49,00 €", "#14B8A6"))))
panier = (f'{lignes_p}<div class="al-total">Total <b>78,00 €</b></div>'
          f'<div class="al-cgv"><i id="s06-case" class="al-case"></i><span>J’accepte les conditions générales de vente</span></div>'
          f'<div id="s06-payer" class="al-bouton al-bouton-l">Payer</div>')
carte(s, "s06-panier", 1060, 290, 760, 520, "Panier", panier)
s.claque("#s06-panier", t_mot(84) - 0.1, 1.3)
son(t_mot(84) - 0.1, "impact-cartoon", 0.4, "panier")
for k, i in enumerate((84, 86)):
    s.j(f'tl.fromTo("#s06-pr{k}", {{ opacity: 0, x: 120 }}, {{ opacity: 1, x: 0, duration: 0.16, ease: "back.out(2)" }}, {s.L(t_mot(i))});')
    son(t_mot(i), tour(["pieces", "pieces-2"]), 0.38, "article ajouté")
zoom(s, t_mot(84), 1440, 550, 1.15)
souris(s, "s06-souris", 1700, 820)
s.j(f'tl.fromTo("#s06-souris", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {s.L(t_mot(86))});')
deplace(s, "s06-souris", t_mot(86) + 0.1, 1112, 663, 1700, 820, 0.4)
clic(s, "s06-souris", t_mot(88), "#s06-case")
s.j(f'tl.to("#s06-case", {{ backgroundColor: "{VERT}", borderColor: "{VERT}", duration: 0.08 }}, {s.L(t_mot(88))});')
son(t_mot(88) + 0.02, "coche", 0.5, "CGV acceptées")
zoom(s, t_mot(88) - 0.1, 1300, 670, 1.4)
deplace(s, "s06-souris", t_mot(89), 1440, 760, 1112, 663, 0.3)
clic(s, "s06-souris", t_mot(90) + 0.1, "#s06-payer")
s.j(f'tl.to("#s06-payer", {{ backgroundColor: "{VERT}", duration: 0.1 }}, {s.L(t_mot(90) + 0.1)});')
son(t_mot(90) + 0.12, "scanner-caisse", 0.42, "paiement")
guide(s, "s06-toi", t_mot(77) + 0.2, t_mot(84), t_mot(90) + 0.15)
s.ecrire()

# ---------------------------------------------------------------- S7 : 5. droits d'auteur
s = scene(6, "Scène 7 · « Et cinquièmement, les droits d'auteur : assure-toi d'avoir les autorisations nécessaires pour utiliser tes images, tes vidéos, tes polices et tes ressources graphiques. »")
d7 = round(s.fin - s.debut, 2)
numero(s, "s07-n", "05", t_mot(92), t_mot(94) - 0.3)
titre(s, "s07-titre", "Droits d’auteur", t_mot(94))
cam(s, '<div id="s07-c" class="al-copy" style="left: 1150px; top: 150px; opacity: 0">©</div>')
s.claque("#s07-c", t_mot(95), 2)
son(t_mot(95), "impact-basse", 0.5, "©")
ecran(s, "s07-ue", 113, 360, 760, 428, "ue-droit-auteur", "europa.eu · la vraie page")
s.apparait("#s07-ue", t_mot(94) + 0.1, 40)
son(t_mot(94) + 0.1, "declencheur", 0.4, "vraie page")
zoom(s, t_mot(96) - 0.1, 493, 574, 1.25)
panneau(s, "s07-photo", 1060, 360, 760, 428, ("video", "photographe", 0, d7), "Une photo trouvée ?", piste=7)
s.apparait("#s07-photo", t_mot(96), 40)
son(t_mot(96) + 0.1, "obturateur", 0.9, "photo")
zoom(s, t_mot(97), 960, 540, 1.0, nom="zoom-out")
panneau(s, "s07-sign", 1060, 360, 760, 428, ("video", "signature", 0, d7), "Autorisation", piste=8)
s.apparait("#s07-sign", t_mot(99), 40)
s.cache("#s07-photo", t_mot(99) + 0.2, 0.05)
son(t_mot(99), "stylo", 0.45, "signature")
badge_ok(s, "s07-aut", "Autorisé", 1100, 700, t_mot(100))
zoom(s, t_mot(100) - 0.1, 1440, 600, 1.2)
# les 4 ressources : images, vidéos, polices, ressources graphiques
g_b = t_mot(102) - 0.1
s.j(f'tl.to(["#s07-ue", "#s07-photo", "#s07-sign", "#s07-aut", "#s07-c"], {{ opacity: 0, y: -60, duration: 0.2, ease: "power3.in" }}, {s.L(g_b)});')
zoom(s, g_b, 960, 540, 1.0, nom="zoom-out")
RESS = [("Images", "photo-produit", 104, "obturateur-num"), ("Vidéos", "montage-video", 106, "clavier-ordi"),
        ("Polices", None, 108, "pop-long"), ("Ressources graphiques", "graphiste", 111, "magie")]
for k, (m, v, i, bruit) in enumerate(RESS):
    x = 113 + k * 430
    if v:
        panneau(s, f"s07-r{k}", x, 330, 400, 300, ("video", v, 0, d7), m, piste=5 + k)
    else:
        cam(s, f'<div id="s07-r{k}" class="pj-panneau al-typos" style="left: {x}px; top: 330px; width: 400px; height: 300px; opacity: 0">'
               f'<span style="font-family: Anton">Aa</span><span style="font-family: \'Instrument Serif\'; font-style: italic">Aa</span>'
               f'<span style="font-family: Inter; font-weight: 800">Aa</span><div class="pj-panneau-tag">{m}</div></div>')
    s.j(f'tl.fromTo("#s07-r{k}", {{ opacity: 0, y: 80, rotation: {(-4, 3, -3, 4)[k]} }}, {{ opacity: 0.22, y: 0, rotation: 0, duration: 0.2, ease: "back.out(2)" }}, {s.L(g_b + 0.15 + k * 0.08)});')
    son(g_b + 0.15 + k * 0.08, tour(["swoosh-court", "fouet", "pop-sec"]), 0.3, f"cadre {m} (en attente)")
    s.j(f'tl.fromTo("#s07-r{k}", {{ opacity: 0.22, scale: 0.92 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.4)", immediateRender: false }}, {s.L(t_mot(i))});')
    son(t_mot(i), bruit, 0.7 if bruit.startswith("obtur") else 0.4, m)
    badge_ok(s, f"s07-ok{k}", "Licence", x + 20, 570, t_mot(i) + 0.32, 30)
zoom(s, t_mot(104), 313, 510, 1.25)
zoom(s, t_mot(106) - 0.05, 743, 510, 1.25)
zoom(s, t_mot(108) - 0.05, 1173, 510, 1.25)
zoom(s, t_mot(111) - 0.05, 1603, 510, 1.25)
zoom(s, t_mot(112) + 0.3, 960, 540, 1.0, nom="zoom-out")
cam(s, perso("s07-toi", 966, 845, 180))
vit(s, "s07-toi", s.debut, s.fin - 0.2)
pose(s, "s07-toi", t_mot(94) + 0.2, 0.16, "back.out(2)", bg=110, tete=8)
pose(s, "s07-toi", t_mot(96), 0.16, "back.out(2)", bg=0, bd=-110, tete=-8)
acquiesce(s, "s07-toi", t_mot(100), 2)
s.j(f'tl.to("#s07-toi", {{ x: -700, duration: 0.3, ease: "power2.inOut" }}, {s.L(g_b)});')
marche(s, "s07-toi", t_mot(104), t_mot(112), 1300)
pose(s, "s07-toi", t_mot(104) + 0.05, 0.14, bd=-150)
victoire(s, "s07-toi", t_mot(112) + 0.3, 1)
s.ecrire()

# ---------------------------------------------------------------- S8 : bonus — sécuriser les données et les formulaires
s = scene(7, "Scène 8 · « N'oublie pas non plus de sécuriser les données et les formulaires de ton site. »")
d8 = round(s.fin - s.debut, 2)
cam(s, '<div id="s08-bonus" class="al-bonus" style="left: 113px; top: 160px; opacity: 0">Bonus</div>')
s.j(f'tl.fromTo("#s08-bonus", {{ opacity: 0, scale: 2.4, rotation: -10 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.16, ease: "power4.out" }}, {s.L(t_mot(113))});')
son(t_mot(113), "impact-basse", 0.5, "BONUS")
secousse(s, t_mot(113), 10)
titre(s, "s08-titre", "Sécurité", t_mot(118), x=480, y=175)
panneau(s, "s08-hack", 1060, 330, 760, 428, ("video", "hacker-glitch", 0, d8), "Attaque ?")
s.apparait("#s08-hack", t_mot(113) + 0.1, 40)
son(t_mot(113) + 0.1, "glitch-data", 0.4, "hacker")
son(t_mot(114), "alarme-breche", 0.3, "alerte intrusion")
ecran(s, "s08-cnil", 113, 360, 760, 428, "cnil-securite", "cnil.fr · sécuriser les sites web", piste=7)
s.apparait("#s08-cnil", t_mot(116), 40)
son(t_mot(116), "declencheur", 0.4, "page CNIL")
cam(s, CADENAS.format(id="s08-cad", x=1370, y=400, w=140, h=175))
s.claque("#s08-cad", t_mot(118), 1.6)
s.j(f'tl.fromTo("#s08-cad-anse", {{ y: -26 }}, {{ y: 0, duration: 0.12, ease: "power4.in", immediateRender: false }}, {s.L(t_mot(118) + 0.3)});')
son(t_mot(118) + 0.42, "verrou", 0.9, "cadenas fermé")
son(t_mot(118) + 0.42, "bouclier", 0.4, "protégé")
zoom(s, t_mot(118) + 0.2, 1440, 520, 1.25)
tampon(s, "s08-refus", "Accès refusé", 1150, 650, t_mot(120), -6, 64)
son(t_mot(120), "buzzer-faux", 0.45, "accès refusé")
zoom(s, t_mot(121), 960, 540, 1.0, nom="zoom-out")
s.j(f'tl.to(["#s08-hack", "#s08-cad", "#s08-refus"], {{ opacity: 0, duration: 0.15 }}, {s.L(t_mot(123) - 0.15)});')
champs = "".join(f'<div class="al-champ"><span>{m}</span><b id="s08-f{k}"></b></div>' for k, m in enumerate(("Nom", "E-mail", "Message")))
form = (f'{champs}<div class="al-https">{CADENAS.format(id="s08-mini", x=0, y=0, w=26, h=32).replace("position: absolute; left: 0px; top: 0px; ", "position: relative; ").replace("opacity: 0", "opacity: 1")}'
        f'<span>https://</span></div><div id="s08-env" class="al-bouton al-bouton-l">Envoyer</div>')
carte(s, "s08-form", 1060, 270, 760, 580, "Formulaire de contact", form)
s.claque("#s08-form", t_mot(123), 1.3)
son(t_mot(123), "impact-cartoon", 0.4, "formulaire")
for k in range(3):
    s.j(f'tl.fromTo("#s08-f{k}", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.3, ease: "none" }}, {s.L(t_mot(123) + 0.2 + k * 0.3)});')
son(t_mot(123) + 0.2, "clavier-doux", 0.4, "on remplit le formulaire", d=0.9)
badge_ok(s, "s08-ok", "Sécurisé", 1520, 196, t_mot(126))
zoom(s, t_mot(123) + 0.05, 1440, 550, 1.15)
guide(s, "s08-toi", t_mot(116) + 0.1, t_mot(118), t_mot(126))
s.ecrire()

# ---------------------------------------------------------------- S9 : design = conformité
s = scene(8, "Scène 9 · « Ton site peut être magnifique, mais sa conformité est tout aussi importante que son design. »")
d9 = round(s.fin - s.debut, 2)
carte(s, "s09-design", 113, 250, 760, 500, "Design", f'<div class="al-carte-video">{video_html("s09-design-v", "site-mode", d9)}</div>')
s.claque("#s09-design", t_mot(127), 1.3)
son(t_mot(127), "swoosh-vol", 0.4, "design")
cam(s, '<div id="s09-brille" class="al-etoiles" style="left: 113px; top: 250px; width: 760px; height: 500px; opacity: 0"><i></i><i></i><i></i><i></i><i></i></div>')
s.j(f'tl.fromTo("#s09-brille", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {s.L(t_mot(131))});')
s.j(f'tl.to("#s09-brille", {{ opacity: 0, duration: 0.3 }}, {s.L(t_mot(132) + 0.2)});')
son(t_mot(131), "etincelles", 0.5, "magnifique")
zoom(s, t_mot(130), 493, 500, 1.2)
items = "".join(f'<div id="s09-i{k}" class="al-item"><i id="s09-k{k}" class="al-case"><b id="s09-v{k}" style="display: block; opacity: 0">{COCHE.format(w=38, c="#0B0E14")}</b></i><span>{m}</span></div>'
                for k, m in enumerate(("Mentions légales", "Confidentialité", "Cookies", "CGV", "Droits d’auteur")))
carte(s, "s09-conf", 1047, 250, 760, 500, "Conformité", items)
s.claque("#s09-conf", t_mot(134), 1.3)
son(t_mot(134), "impact-whoosh", 0.5, "CONFORMITÉ")
zoom(s, t_mot(133), 1427, 500, 1.2)
for k in range(5):
    g = t_mot(134) + 0.25 + k * 0.13
    s.j(f'tl.to("#s09-k{k}", {{ backgroundColor: "{VERT}", borderColor: "{VERT}", duration: 0.06 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#s09-v{k}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power4.in", immediateRender: false }}, {s.L(g)});')
    son(g, tour(["coche", "pop-click", "clic-positif"]), 0.42, f"coche {k + 1}")
zoom(s, t_mot(137), 960, 500, 1.0, nom="zoom-out")
cam(s, '<div id="s09-egal" class="al-egal" style="left: 905px; top: 440px"><i></i><i></i></div>')
s.j(f'tl.fromTo("#s09-egal i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.18, ease: "back.out(3)", stagger: 0.06 }}, {s.L(t_mot(138))});')
son(t_mot(138), "impact-basse", 0.5, "aussi importante")
s.j(f'tl.to(["#s09-design", "#s09-conf"], {{ boxShadow: "0 0 70px rgba(47, 227, 138, 0.8)", duration: 0.3, repeat: 1, yoyo: true }}, {s.L(t_mot(141))});')
cam(s, perso("s09-toi", 960, 825, 175))
vit(s, "s09-toi", s.debut, s.fin - 0.2)
pose(s, "s09-toi", t_mot(131), 0.16, "back.out(2)", bg=110, tete=8)
pose(s, "s09-toi", t_mot(134), 0.16, "back.out(2)", bg=0, bd=-110, tete=-8)
victoire(s, "s09-toi", t_mot(141), 2)
confettis(s, "s09-conf-e", t_mot(141), 960, 420, 30, 620)
son(t_mot(141), "cloche-succes", 0.45, "final")
son(t_mot(141) + 0.1, "fanfare", 0.3, "final")
s.ecrire()

# ================================================================ SONS GÉNÉRAUX
for k, c in enumerate(COUPES[1:-1], start=1):
    son(c, tour(TRANSITIONS), 0.46, f"volet vers {NOMS[k]}")
son(t_mot(11), "riser-trailer", 0.34, "montée vers ATTENTION")
son(0.02, "impact-whoosh", 0.55, "ouverture")
son(0.03, "scratch", 0.38, "ouverture")
son(t_mot(141), "riser-synth", 0.0, "réserve")  # volume nul : non placé ci-dessous
SONS[:] = [x for x in SONS if x[2] > 0]

MUSIQUES = [  # (début, fichier, durée, volume) — 0,63 ≈ −21 LUFS (5–6 dB sous la voix, réglage validé)
    (0, "partie-1-complicated", 15.4, 0.63),      # le drop tombe sur « Attention ! » (3,48 s)
    (14.4, "partie-2-tech-house-vibes", 20.8, 0.63),
    (34.2, "partie-3-hip-hop-02", 18.6, 0.63),
]
MASQUES = []

# check-list globale (en haut) : point actif / validé, par scène
CHECK = ["Mentions", "Données", "Cookies", "CGV", "Droits"]


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
        box-shadow: 0 0 40px rgba(255, 90, 31, 0.7);
      }
      .pj-impulsion {
        position: absolute;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--color-accent);
        box-shadow: 0 0 30px 12px rgba(255, 90, 31, 0.7);
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
      /* ---- Style « Alerte » (variante dynamique) ---- */
      :root {
        --color-ground: #0b0e14;
        --color-accent: #ff5a1f;
        --accent-shade: #b23a10;
        --accent-glow: rgba(255, 90, 31, 0.4);
        --vert: #2fe38a;
      }
      #fond {
        background: #0b0e14;
      }
      .pj-scene {
        background:
          linear-gradient(rgba(110, 150, 255, 0.07) 1px, transparent 1px) 0 0 / 80px 80px,
          linear-gradient(90deg, rgba(110, 150, 255, 0.07) 1px, transparent 1px) 0 0 / 80px 80px,
          radial-gradient(ellipse 60% 70% at 50% 55%, #17213a 0%, #0b0e14 75%);
      }
      .pj-cadre > .pj-horizon {
        display: none;
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
        border-image: repeating-linear-gradient(-45deg, #0b0e14 0 18px, var(--color-accent) 18px 36px) 16;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      }
      .al-ruban-t {
        font-family: "Anton", sans-serif;
        font-size: 66px;
        line-height: 86px;
        color: #0b0e14;
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
        outline: 3px solid #0b0e14;
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
        background: #0b0e14;
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
        color: #0b0e14;
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
        border: 4px solid #0b0e14;
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
        color: #0b0e14;
        text-transform: uppercase;
      }
      .al-popup-corps {
        padding: 18px 22px 22px;
        font-family: "Inter", sans-serif;
        font-weight: 800;
        font-size: 38px;
        color: #0b0e14;
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
        color: #0b0e14;
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
        color: #0b0e14;
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
        background: radial-gradient(ellipse at center, rgba(255, 90, 31, 0.25), rgba(255, 40, 20, 0.85));
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
        color: #0b0e14;
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
        color: #0b0e14;
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
        background: #0b0e14;
        padding: 3px 0;
      }
      .al-oeil .al-actif {
        background: var(--color-accent);
        color: #0b0e14;
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
        color: #0b0e14;
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
        border: 3px solid #0b0e14;
        color: #0b0e14;
      }
      .al-b1 {
        background: var(--color-accent);
        color: #0b0e14;
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
        color: #0b0e14;
      }
      .al-bonus {
        position: absolute;
        font-family: "Anton", sans-serif;
        font-size: 92px;
        line-height: 1;
        padding: 10px 30px 14px;
        color: #0b0e14;
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
        background: linear-gradient(90deg, #2e3650 0 60%, transparent 60%) 16px 16px / 70% 18px no-repeat, #0b0e14;
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
      background: repeating-linear-gradient(-45deg, #ff5a1f 0 32px, #0b0e14 32px 64px);
    }}
    .vo-p {{
      flex: 1;
      background: #0b0e14;
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
    """Check-list des 5 points SOUS le film, dans la version verticale (../site-conforme-vertical/index.html) :
    case active (orange) pendant le point, puis validée (verte). Hors du film : elle ne cache jamais rien."""
    cases, js = [], []
    for k, m in enumerate(CHECK):
        cases.append(f'        <div id="ck-{k}" class="ck-case"><b>{k + 1}</b><span>{m}</span><i id="ck-v{k}">{COCHE.format(w=40, c="#0B0E14")}</i></div>')
        g_act, g_ok = COUPES[2 + k], COUPES[3 + k]
        js.append(f'      tl.to("#ck-{k}", {{ borderColor: "#FF5A1F", backgroundColor: "rgba(255, 90, 31, 0.3)", scale: 1.08, duration: 0.18 }}, {round(g_act + 0.1, 3)});')
        js.append(f'      tl.to("#ck-{k}", {{ borderColor: "#2FE38A", backgroundColor: "#2FE38A", color: "#0B0E14", scale: 1, duration: 0.16 }}, {round(g_ok - 0.05, 3)});')
        js.append(f'      tl.fromTo("#ck-v{k}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.in", immediateRender: false }}, {round(g_ok - 0.05, 3)});')
    js.append(f'      tl.fromTo("#ck-barre", {{ opacity: 0, y: 80 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.8)" }}, {round(t_mot(20), 3)});')
    js.append(f'      tl.to(".ck-case", {{ keyframes: [{{ scale: 1.12, duration: 0.12 }}, {{ scale: 1, duration: 0.16 }}], stagger: 0.06 }}, {round(t_mot(141), 3)});')
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
        color: #ff5a1f;
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
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 196px;
        height: 132px;
        border: 4px solid #3a4462;
        background: #0b0e14;
        color: #ecece8;
        font-family: "Anton", sans-serif;
        text-transform: uppercase;
      }
      .ck-case b {
        font-weight: 400;
        font-size: 54px;
        line-height: 1;
      }
      .ck-case span {
        font-size: 30px;
        line-height: 1.1;
        white-space: nowrap;
      }
      .ck-case i {
        position: absolute;
        right: 8px;
        top: 8px;
        opacity: 0;
      }
"""
    html = (f'      <div id="ck-barre" class="clip" data-start="0" data-duration="{FIN}" data-track-index="3" style="opacity: 0">\n'
            f'        <div id="ck-tete">Check-list avant publication</div>\n        <div id="ck-cases">\n' + "\n".join("  " + c for c in cases) +
            "\n        </div>\n      </div>")
    f = ICI.parent / "site-conforme-vertical/index.html"
    h = f.read_text(encoding="utf-8")
    h = re.sub(r"(      /\* check : début \*/\n).*?(      /\* check : fin \*/)", lambda m: m.group(1) + css + m.group(2), h, flags=re.S)
    h = re.sub(r"(      <!-- check : début -->\n).*?(      <!-- check : fin -->)", lambda m: m.group(1) + html + "\n" + m.group(2), h, flags=re.S)
    h = re.sub(r"(      // check : début\n).*?(      // check : fin)", lambda m: m.group(1) + "\n".join(js) + "\n" + m.group(2), h, flags=re.S)
    f.write_text(h, encoding="utf-8")


def couleurs_alerte():
    """Remplace l'accent vert-jaune du style « Projecteur » par l'orange du style « Alerte » dans les scènes."""
    for f in (ICI / "compositions").glob("s*.html"):
        h = f.read_text(encoding="utf-8")
        h = h.replace("#DCFC1C", ACCENT).replace("#dcfc1c", ACCENT).replace("rgba(255, 90, 31", "rgba(255, 90, 31")
        f.write_text(h, encoding="utf-8")
    st = ICI / "compositions/sous-titres.html"
    h = st.read_text(encoding="utf-8")
    if "style Alerte" not in h:
        h = h.replace("    .st-mot {\n", "    /* style Alerte */\n    .st-bandeau {\n      box-shadow: 10px 10px 0 #ff5a1f;\n      transform: skewX(-6deg);\n    }\n    .st-mot {\n", 1)
        st.write_text(h, encoding="utf-8")


for nom in NOMS:
    contenu = (ICI / "compositions" / f"{nom}.html").read_text(encoding="utf-8")
    assert not re.search(rf'(?<![-\w])id="{nom}"|"#{nom}"', contenu), f"un élément porte l'identifiant de la scène {nom}"
couleurs_alerte()
ecrire_volets()
ecrire_check()
n = ecrire_index()
ecrire_cadre()
print(f"{len(NOMS)} scènes écrites, {n} bruitages placés, fin à {FIN} s")
