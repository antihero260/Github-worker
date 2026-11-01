#!/usr/bin/env python3
"""Bibliothèque du style « Projecteur » pour écrire des scènes HyperFrames (HTML statique).

Utilisation, depuis le générateur de scènes d'une vidéo :

    import sys; sys.path.insert(0, "<dépôt>/hyperframes-style/outils")
    from projecteur import *
    init(<dossier du projet>)
    s = Scene("s1-...", debut, fin, "titre")
    cam(s, projecteur(960)); cam(s, perso("s1-toi", 960, 800, 400))
    vit(s, "s1-toi", s.debut, s.fin); pose(s, "s1-toi", t_mot(3), bd=-160) ...
    s.ecrire()

Les temps passés aux fonctions sont ceux de la vidéo (t_mot(i) = début du mot i de assets/mots.json).
"""
import importlib.util
import json
import math
from pathlib import Path

PROJET: Path = Path(".")
MOTS: list = []
TEXTE: list = []


def init(projet):
    """À appeler en premier : charge les mots alignés (assets/mots.json) et le script du projet."""
    global PROJET, MOTS, TEXTE
    PROJET = Path(projet).resolve()
    MOTS = json.loads((PROJET / "assets/mots.json").read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("st", PROJET / "tools/sous-titres.py")
    st = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(st)
    TEXTE = st.mots_du_script(PROJET / "script.txt")  # casse et ponctuation d'origine
    assert len(TEXTE) == len(MOTS), (len(TEXTE), len(MOTS))


def t_mot(i):
    return MOTS[i]["start"]


PICTO = ('<g class="pj-contour"><circle cx="50" cy="26" r="24" /><rect x="16" y="58" width="68" height="96" rx="10" />'
         '<rect x="21" y="140" width="25" height="118" rx="5" /><rect x="54" y="140" width="25" height="118" rx="5" /></g>'
         '<g class="pj-plein"><circle cx="50" cy="26" r="24" /><rect x="16" y="58" width="68" height="96" rx="10" />'
         '<rect x="21" y="140" width="25" height="118" rx="5" /><rect x="54" y="140" width="25" height="118" rx="5" /></g>')


PARTIES = {  # forme (contour + remplissage) et pivot de chaque membre, en unités du SVG
    "jg": ('<rect x="24" y="136" width="24" height="112" rx="8" />', "36 142"),
    "jd": ('<rect x="52" y="136" width="24" height="112" rx="8" />', "64 142"),
    "tronc": ('<rect x="22" y="52" width="56" height="94" rx="12" />', None),
    "bg": ('<rect x="2" y="54" width="18" height="86" rx="9" />', "11 62"),
    "bd": ('<rect x="80" y="54" width="18" height="86" rx="9" />', "89 62"),
    "tete": ('<circle cx="50" cy="24" r="22" />', "50 50"),
}
PIVOTS = {k: v[1] for k, v in PARTIES.items() if v[1]}


TETES = {
    "toi": '<circle cx="50" cy="24" r="22" />',
    "ia": '<rect x="25" y="0" width="50" height="46" rx="13" />',
}


def perso(id_, cx, pieds, h, genre="toi"):
    """Pictogramme articulé (tête, tronc, bras, jambes animables séparément).

    genre "toi" : le héros vert-jaune ; "ia" : l'IA blanc cassé, tête-écran avec deux yeux.
    Structure : svg#id > g#id-vie (mouvements continus) > g#id-corps (sauts, rebonds) > membres.
    """
    w = round(h * 160 / 290)
    groupes = []
    for k, (forme, _) in PARTIES.items():
        if k == "tete":
            forme = TETES[genre]
        yeux = ('<g class="yeux"><circle cx="40" cy="22" r="5" /><circle cx="60" cy="22" r="5" /></g>'
                if (k == "tete" and genre == "ia") else "")
        groupes.append(f'<g id="{id_}-{k}"><g class="c">{forme}</g><g class="p">{forme}</g>{yeux}</g>')
    return (f'<svg id="{id_}" class="pj-perso pj-{genre}-perso" viewBox="-30 -20 160 290" '
            f'style="left: {cx - w // 2}px; top: {pieds - round(h * 268 / 290)}px; width: {w}px; height: {h}px">'
            f'<g id="{id_}-vie"><g id="{id_}-corps">{"".join(groupes)}</g></g></svg>')


def toi(id_, cx, pieds, h):
    return perso(id_, cx, pieds, h, "toi")


# ---- gestes (temps en secondes de la vidéo)
def pose(s, pid, g, d=0.18, ease="power2.out", **angles):
    for k, v in angles.items():
        s.j(f'tl.to("#{pid}-{k}", {{ rotation: {v}, svgOrigin: "{PIVOTS[k]}", duration: {d}, ease: "{ease}" }}, {s.L(g)});')


def repos(s, pid, g, d=0.2):
    pose(s, pid, g, d, bg=0, bd=0, jg=0, jd=0, tete=0)


def marche(s, pid, g0, g1, dx):
    """Marche de g0 à g1 en avançant de dx pixels : jambes et bras alternés, petit rebond."""
    pas = max(2, round((g1 - g0) / 0.28))
    d = round((g1 - g0) / pas / 2, 3)
    s.j(f'tl.to("#{pid}", {{ x: "+={dx}", duration: {round(g1 - g0, 3)}, ease: "none" }}, {s.L(g0)});')
    for k, sens in (("jg", 1), ("jd", -1), ("bg", -1), ("bd", 1)):
        amp = 24 if k[0] == "j" else 20
        kf = ", ".join(f'{{ rotation: {sens * amp * (1 if n % 2 == 0 else -1)}, duration: {d} }}' for n in range(pas * 2 - 1)) + f', {{ rotation: 0, duration: {d} }}'
        s.j(f'tl.to("#{pid}-{k}", {{ svgOrigin: "{PIVOTS[k]}", keyframes: [{kf}] }}, {s.L(g0)});')
    kf = ", ".join(f'{{ y: {-6 if n % 2 == 0 else 0}, duration: {d} }}' for n in range(pas * 2))
    s.j(f'tl.to("#{pid}-corps", {{ keyframes: [{kf}] }}, {s.L(g0)});')


def tape(s, pid, g0, g1, vite=0.11):
    """Tape au clavier : avant-bras rentrés qui alternent."""
    n = max(1, int((g1 - g0 - 0.15 - vite) / vite) - 1)  # se termine avant g1
    pose(s, pid, g0, 0.15, bg=-28, bd=28, tete=10)
    s.j(f'tl.to("#{pid}-bg", {{ rotation: -18, svgOrigin: "{PIVOTS["bg"]}", duration: {vite}, repeat: {n}, yoyo: true, ease: "sine.inOut" }}, {s.L(g0 + 0.15)});')
    s.j(f'tl.to("#{pid}-bd", {{ rotation: 38, svgOrigin: "{PIVOTS["bd"]}", duration: {vite}, repeat: {n}, yoyo: true, ease: "sine.inOut" }}, {s.L(g0 + 0.15 + vite / 2)});')
    repos(s, pid, g1)


def non(s, pid, g):
    s.j(f'tl.to("#{pid}-tete", {{ svgOrigin: "{PIVOTS["tete"]}", keyframes: [{{ rotation: -14, duration: 0.08 }}, {{ rotation: 14, duration: 0.1 }}, {{ rotation: -10, duration: 0.1 }}, {{ rotation: 0, duration: 0.08 }}] }}, {s.L(g)});')


def oui(s, pid, g):
    s.j(f'tl.to("#{pid}-tete", {{ svgOrigin: "{PIVOTS["tete"]}", keyframes: [{{ rotation: 10, y: 4, duration: 0.1 }}, {{ rotation: 0, y: 0, duration: 0.12 }}] }}, {s.L(g)});')


def saut(s, pid, g, h=34):
    s.j(f'tl.to("#{pid}-corps", {{ keyframes: [{{ y: -{h}, duration: 0.13, ease: "power2.out" }}, {{ y: 0, duration: 0.15, ease: "power2.in" }}] }}, {s.L(g)});')


def tremble(s, pid, g, d=0.8):
    n = round(d / 0.05)
    s.j(f'tl.to("#{pid}-corps", {{ x: 5, duration: 0.05, repeat: {n}, yoyo: true, ease: "none" }}, {s.L(g)});')
    s.j(f'tl.to("#{pid}-corps", {{ x: 0, duration: 0.05 }}, {s.L(g + d + 0.06)});')


def panique(s, pid, g, d=1.0):
    n = round(d / 0.16)
    kf_g = ", ".join(f'{{ rotation: {150 if k % 2 == 0 else 95}, duration: 0.08 }}' for k in range(n))
    kf_d = ", ".join(f'{{ rotation: {-95 if k % 2 == 0 else -150}, duration: 0.08 }}' for k in range(n))
    s.j(f'tl.to("#{pid}-bg", {{ svgOrigin: "{PIVOTS["bg"]}", keyframes: [{kf_g}] }}, {s.L(g)});')
    s.j(f'tl.to("#{pid}-bd", {{ svgOrigin: "{PIVOTS["bd"]}", keyframes: [{kf_d}] }}, {s.L(g)});')
    tremble(s, pid, g, d)


def gratte(s, pid, g):
    pose(s, pid, g, 0.16, bd=-158, tete=-8)
    s.j(f'tl.to("#{pid}-bd", {{ rotation: -146, svgOrigin: "{PIVOTS["bd"]}", duration: 0.09, repeat: 5, yoyo: true }}, {s.L(g + 0.18)});')


def haussement(s, pid, g):
    pose(s, pid, g, 0.16, "back.out(2)", bg=48, bd=-48, tete=8)
    saut(s, pid, g, 14)


def vertiges(s, pid, g, cx, y, d=1.6):
    """Petits points qui tournent au-dessus de la tête (perdu, sonné)."""
    vid = f"{pid}-vertige"
    pts = "".join(f'<circle cx="{round(40 + 34 * __import__("math").cos(k * 1.2566), 1)}" cy="{round(14 + 10 * __import__("math").sin(k * 1.2566), 1)}" r="5" fill="#DCFC1C" />' for k in range(5))
    cam(s, f'<svg id="{vid}" style="position: absolute; left: {cx - 40}px; top: {y}px; width: 80px; height: 28px; overflow: visible; opacity: 0" viewBox="0 0 80 28">{pts}</svg>')
    s.j(f'tl.fromTo("#{vid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{vid}", {{ rotation: 0 }}, {{ rotation: 360, svgOrigin: "40 14", duration: 0.8, repeat: {max(1, round(d / 0.8) - 1)}, ease: "none" }}, {s.L(g)});')
    s.j(f'tl.to("#{vid}", {{ opacity: 0, duration: 0.15 }}, {s.L(g + d)});')


def dort(s, pid, g, cx, y):
    s.j(f'tl.to("#{pid}", {{ rotation: -90, transformOrigin: "50% 92%", duration: 0.35, ease: "power2.inOut" }}, {s.L(g)});')
    zid = f"{pid}-z"
    cam(s, f'<div id="{zid}" class="pj-serif" style="left: {cx}px; top: {y}px; font-size: 64px; color: #ECECE8">'
           '<span style="opacity: 1">z</span> <span style="opacity: 1; font-size: 84px">Z</span></div>')
    s.j(f'tl.fromTo("#{zid}", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: -30, duration: 0.6, ease: "power1.out" }}, {s.L(g + 0.3)});')


def projecteur(cx, sol_y=815, h=900, op=1.0):
    return (f'<div class="pj-cone" style="left: {cx - 280}px; height: {h}px; opacity: {op}"></div>'
            f'<div class="pj-sol" style="left: {cx - 310}px; top: {sol_y - 75}px; opacity: {op}"></div>')


def hud_g(id_, k, d=None, style=""):
    d_html = f'<span class="pj-d">{d}</span>' if d else ""
    return f'<div id="{id_}" class="pj-label" style="left: 113px; top: 107px; {style}"><span class="pj-k">{k}</span>{d_html}</div>'


def hud_d(id_, k, d=None, style=""):
    d_html = f'<span class="pj-d">{d}</span>' if d else ""
    return f'<div id="{id_}" class="pj-label" style="right: 113px; top: 107px; text-align: right; {style}"><span class="pj-k">{k}</span>{d_html}</div>'


class Scene:
    def __init__(self, id_, debut, fin, titre, premiere=False, derniere=False):
        self.id, self.debut, self.fin, self.titre = id_, debut, fin, titre
        self.premiere, self.derniere = premiere, derniere
        self.html, self.js, self.css = [], [], []
        self.n_proxy = 0

    # temps local
    def L(self, g):
        return round(max(0.0, g - self.debut), 3)

    def add(self, h):
        self.html.append(h)

    def j(self, ligne):
        self.js.append("    " + ligne)

    def apparait(self, sel, g, dy=30, d=0.18):
        self.j(f'tl.fromTo("{sel}", {{ opacity: 0, y: {dy} }}, {{ opacity: 1, y: 0, duration: {d}, ease: "power3.out" }}, {self.L(g)});')

    def glisse(self, sel, g, dx, d=0.24):
        self.j(f'tl.fromTo("{sel}", {{ opacity: 0, x: {dx} }}, {{ opacity: 1, x: 0, duration: {d}, ease: "power4.out" }}, {self.L(g)});')

    def claque(self, sel, g, s=1.6):
        self.j(f'tl.fromTo("{sel}", {{ opacity: 0, scale: {s} }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.2)" }}, {self.L(g)});')

    def choc(self, sel, g):
        self.j(f'tl.fromTo("{sel}", {{ opacity: 0, scale: 1.45 }}, {{ opacity: 1, scale: 1, duration: 0.13, ease: "power4.out" }}, {self.L(g)});')

    def montre(self, sel, g):
        self.j(f'tl.set("{sel}", {{ opacity: 1 }}, {self.L(g)});')

    def cache(self, sel, g, d=0.15):
        self.j(f'tl.to("{sel}", {{ opacity: 0, duration: {d} }}, {self.L(g)});')

    def rature(self, sel, g):
        self.j(f'tl.fromTo("{sel}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.16, ease: "power2.out" }}, {self.L(g)});')

    def croix(self, sel, g):
        self.j(f'tl.fromTo("{sel}", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.out" }}, {self.L(g)});')

    def recadre(self, g, px, py, sc, d=0.24):
        """Recadrage rapide (filé) : amène le point (px, py) au centre, grossi sc fois."""
        x, y = round(-(px - 960) * sc), round(-(py - 540) * sc)
        self.j(f'tl.to("#{self.id}-cadre", {{ x: {x}, y: {y}, scale: {sc}, duration: {d}, ease: "power3.inOut" }}, {self.L(g)});')
        self.j(f'tl.to("#{self.id}-cadre", {{ keyframes: [{{ filter: "blur(10px)", duration: {round(d / 2, 3)} }}, {{ filter: "blur(0px)", duration: {round(d / 2, 3)} }}] }}, {self.L(g)});')

    def eclair(self, g):
        self.add(f'<div id="{self.id}-eclair" class="pj-flash"></div>')
        self.j(f'tl.set("#{self.id}-eclair", {{ opacity: 1 }}, {self.L(g)});')
        self.j(f'tl.set("#{self.id}-eclair", {{ opacity: 0 }}, {round(self.L(g) + 0.067, 3)});')

    def compteur(self, sel, g, de, a, d, fmt="n"):
        """Compteur qui défile ; fmt : 'n', 'pct', 'hhmm' (minutes depuis minuit), 'mmss' (secondes)."""
        self.n_proxy += 1
        p = f"p{self.n_proxy}"
        f = {
            "n": f'String(Math.round({p}.v))',
            "pct": f'Math.round({p}.v) + " %"',
            "hhmm": f'String(Math.floor({p}.v / 60) % 24).padStart(2, "0") + ":" + String(Math.floor({p}.v % 60)).padStart(2, "0")',
            "mmss": f'String(Math.floor({p}.v / 60)).padStart(2, "0") + ":" + String(Math.floor({p}.v % 60)).padStart(2, "0")',
        }[fmt]
        self.j(f'const {p} = {{ v: {de} }};')
        self.j(f'tl.fromTo({p}, {{ v: {de} }}, {{ v: {a}, duration: {d}, ease: "{"power2.out" if fmt != "mmss" else "none"}", immediateRender: false, '
               f'onUpdate: () => {{ document.querySelector("{sel}").textContent = {f}; }} }}, {self.L(g)});')

    def ecrire(self):
        duree = round(self.fin - self.debut, 3)
        cam = [f'tl.fromTo("#{self.id}-cam", {{ scale: 1 }}, {{ scale: 1.05, duration: {round(duree - 0.2, 3)}, ease: "none" }}, 0);']
        if not self.premiere:
            cam.append(f'tl.fromTo("#{self.id}-cam", {{ filter: "blur(14px)" }}, {{ filter: "blur(0px)", duration: 0.16, ease: "power2.out" }}, 0);')
        if not self.derniere:
            sortie = [f'tl.to("#{self.id}-cam", {{ scale: 1.3, filter: "blur(14px)", duration: 0.2, ease: "power3.in" }}, {round(duree - 0.2, 3)});']
        else:
            sortie = [f'tl.fromTo("#{self.id}-noir", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.8, ease: "power2.in" }}, {round(duree - 0.8, 3)});']
            self.add(f'<div id="{self.id}-noir" style="position: absolute; inset: 0; background: #000; opacity: 0"></div>')
        cam_html = [h for h in self.html if h.startswith("CAM:")]
        hors = [h for h in self.html if not h.startswith("CAM:")]
        corps = "\n        ".join(h[4:] for h in cam_html)
        hors_cam = "\n      ".join(hors)
        css = "\n".join(self.css)
        js = "\n".join("    " + c for c in cam) + "\n" + "\n".join(self.js) + "\n" + "\n".join("    " + c for c in sortie)
        page = f"""<!-- {self.titre} ({self.debut} → {self.fin} s). Fichier écrit par un générateur, modifiable à la main. -->
<template>
  <style>
    #root {{
      position: absolute;
      inset: 0;
    }}
{css}
  </style>
  <div id="root" data-composition-id="{self.id}" data-width="1920" data-height="1080">
    <div class="pj-scene">
      <div id="{self.id}-cam" class="pj-cam">
        <div id="{self.id}-cadre" class="pj-cadre">
        <div class="pj-horizon" style="top: 760px"></div>
        {corps}
        </div>
      </div>
      {hors_cam}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{self.id}"] = tl;
  </script>
</template>
"""
        (PROJET / "compositions" / f"{self.id}.html").write_text(page, encoding="utf-8")


def cam(scene, h):
    scene.add("CAM:" + h)


def message(scene, id_, i1, i2, surligne):
    """Message tapé mot à mot avec la voix ; surligne = indices de mots passés au vert-jaune."""
    spans = []
    for i in range(i1, i2 + 1):
        mot = TEXTE[i].replace("« ", "").replace(" »", "")
        spans.append(f'<span id="{id_}-m{i}">{mot}</span>')
        scene.montre(f"#{id_}-m{i}", t_mot(i))
        if i in surligne:
            scene.j(f'tl.set("#{id_}-m{i}", {{ backgroundColor: "#DCFC1C" }}, {scene.L(t_mot(i) + 0.15)});')
    return " ".join(spans)


def etapes(scene, id_, textes, temps, style):
    """Texte qui change d'un coup (ex. « CONSIGNES : 2/5 ») : spans superposés."""
    spans = "".join(f'<span id="{id_}-{k}" style="position: absolute; right: 0; opacity: {1 if k == 0 else 0}">{t}</span>'
                    for k, t in enumerate(textes))
    for k, g in enumerate(temps, start=1):
        scene.j(f'tl.set("#{id_}-{k - 1}", {{ opacity: 0 }}, {scene.L(g)});')
        scene.j(f'tl.set("#{id_}-{k}", {{ opacity: 1 }}, {scene.L(g)});')
    return f'<div class="pj-label" style="{style}"><span class="pj-k" style="position: relative; display: block; height: 40px">{spans}</span></div>'


def papier_lignes(n, largeurs):
    return "".join(f'<div style="height: 18px; width: {w}%; background: #bdbdb8; margin-top: 18px"></div>' for w in largeurs[:n])




# ---- gestes ajoutés pour un personnage plus vivant (« ia-te-donne-raison »)
def vit(s, pid, g0, g1, amp=5, periode=0.42):
    """Ne jamais rester figé : léger rebond continu du personnage entre g0 et g1."""
    n = max(1, int((g1 - g0) / periode) - 1)
    s.j(f'tl.fromTo("#{pid}-vie", {{ y: 0 }}, {{ y: -{amp}, duration: {periode}, repeat: {n}, yoyo: true, ease: "sine.inOut", immediateRender: false }}, {s.L(g0)});')


def parle(s, pid, g0, g1, bras="bd"):
    """Gestes de la main pendant qu'il parle."""
    hauts = (-62, -118) if bras == "bd" else (62, 118)
    n = max(2, int((g1 - g0) / 0.24))
    kf = ", ".join(f'{{ rotation: {hauts[k % 2]}, duration: 0.24, ease: "sine.inOut" }}' for k in range(n))
    s.j(f'tl.to("#{pid}-{bras}", {{ svgOrigin: "{PIVOTS[bras]}", keyframes: [{kf}, {{ rotation: 0, duration: 0.2 }}] }}, {s.L(g0)});')
    s.j(f'tl.to("#{pid}-tete", {{ svgOrigin: "{PIVOTS["tete"]}", keyframes: [' + ", ".join(
        f'{{ rotation: {(-6, 6)[k % 2]}, duration: 0.36 }}' for k in range(max(1, int((g1 - g0) / 0.36)))) + ', { rotation: 0, duration: 0.2 }] }, %s);' % s.L(g0))


def acquiesce(s, pid, g, n=4, vite=0.11):
    """Hoche la tête plusieurs fois (« oui, oui, oui »)."""
    kf = ", ".join(f'{{ rotation: {14 if k % 2 == 0 else -2}, duration: {vite} }}' for k in range(n * 2)) + f', {{ rotation: 0, duration: {vite} }}'
    s.j(f'tl.to("#{pid}-tete", {{ svgOrigin: "{PIVOTS["tete"]}", keyframes: [{kf}] }}, {s.L(g)});')


def court(s, pid, g0, g1, dx):
    """Course : comme marche, mais pas plus rapides et plus amples."""
    pas = max(2, round((g1 - g0) / 0.18))
    d = round((g1 - g0) / pas / 2, 3)
    s.j(f'tl.to("#{pid}", {{ x: "+={dx}", duration: {round(g1 - g0, 3)}, ease: "power1.inOut" }}, {s.L(g0)});')
    for k, sens, amp in (("jg", 1, 38), ("jd", -1, 38), ("bg", -1, 40), ("bd", 1, 40)):
        kf = ", ".join(f'{{ rotation: {sens * amp * (1 if n % 2 == 0 else -1)}, duration: {d} }}' for n in range(pas * 2 - 1)) + f', {{ rotation: 0, duration: {d} }}'
        s.j(f'tl.to("#{pid}-{k}", {{ svgOrigin: "{PIVOTS[k]}", keyframes: [{kf}] }}, {s.L(g0)});')
    kf = ", ".join(f'{{ y: {-12 if n % 2 == 0 else 0}, duration: {d} }}' for n in range(pas * 2))
    s.j(f'tl.to("#{pid}-corps", {{ keyframes: [{kf}] }}, {s.L(g0)});')


def chute(s, pid, g, dy=560, rot=28):
    """Tombe (dans un trou) : glisse vers le bas en basculant."""
    s.j(f'tl.to("#{pid}", {{ y: {dy}, rotation: {rot}, transformOrigin: "50% 90%", duration: 0.42, ease: "power2.in" }}, {s.L(g)});')


def remonte(s, pid, g, d=0.35):
    s.j(f'tl.to("#{pid}", {{ y: 0, rotation: 0, transformOrigin: "50% 90%", duration: {d}, ease: "back.out(1.6)" }}, {s.L(g)});')


def grossit(s, pid, g, f=1.3, d=0.3):
    s.j(f'tl.to("#{pid}", {{ scale: {f}, transformOrigin: "50% 92%", duration: {d}, ease: "back.out(2)" }}, {s.L(g)});')


def bras_croises(s, pid, g):
    pose(s, pid, g, 0.18, "back.out(2)", bg=-46, bd=46, tete=-6)


def pouce(s, pid, g, bras="bd"):
    pose(s, pid, g, 0.16, "back.out(2.5)", **{bras: -152 if bras == "bd" else 152})
    s.j(f'tl.to("#{pid}-{bras}", {{ rotation: "{"+=" if bras == "bd" else "-="}12", svgOrigin: "{PIVOTS[bras]}", duration: 0.08, repeat: 3, yoyo: true }}, {s.L(g + 0.18)});')


def victoire(s, pid, g, sauts=2):
    pose(s, pid, g, 0.14, "back.out(2)", bg=165, bd=-165, tete=-8)
    for k in range(sauts):
        saut(s, pid, g + 0.05 + k * 0.32, 40)


def confettis(s, cid, g, cx, cy, n=22, rayon=420):
    """Explosion de confettis vert-jaune et blancs (positions fixes : rendu identique à chaque fois)."""
    morceaux = []
    for k in range(n):
        ang = k * 2.39996
        dist = rayon * (0.45 + 0.55 * ((k * 37) % 11) / 10)
        dx, dy = round(math.cos(ang) * dist), round(math.sin(ang) * dist * 0.7 - 120)
        coul = "#DCFC1C" if k % 3 else "#ECECE8"
        w, h = (18, 10) if k % 2 else (12, 12)
        morceaux.append(f'<i id="{cid}-{k}" style="position: absolute; left: {cx}px; top: {cy}px; width: {w}px; height: {h}px; background: {coul}; opacity: 0"></i>')
        s.j(f'tl.fromTo("#{cid}-{k}", {{ x: 0, y: 0, rotation: 0, opacity: 1 }}, {{ x: {dx}, y: {dy + 260}, rotation: {(k * 97) % 540 - 270}, opacity: 0, duration: 1.3, ease: "power2.out" }}, {s.L(g)});')
    cam(s, "".join(morceaux))


def bulle(s, bid, texte, x, y, g, taille=52, fin=None):
    """Bulle de dialogue (serif italique, fond blanc cassé) qui surgit à g."""
    cam(s, f'<div id="{bid}" class="pj-serif" style="left: {x}px; top: {y}px; font-size: {taille}px; color: #0a0a06; '
           f'background: #ECECE8; padding: 10px 26px; opacity: 0; transform-origin: 0% 100%">{texte}</div>')
    s.j(f'tl.fromTo("#{bid}", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.4)" }}, {s.L(g)});')
    if fin is not None:
        s.j(f'tl.to("#{bid}", {{ opacity: 0, scale: 0.8, duration: 0.15 }}, {s.L(fin)});')


def tampon(s, tid, texte, x, y, g, rot=-8, taille=84, fond="#DCFC1C"):
    """Autocollant / tampon qui s'écrase avec une petite secousse."""
    cam(s, f'<div id="{tid}" class="pj-sticker" style="left: {x}px; top: {y}px; font-size: {taille}px; background: {fond}; '
           f'transform: rotate({rot}deg); opacity: 0">{texte}</div>')
    s.j(f'tl.fromTo("#{tid}", {{ opacity: 0, scale: 2.2 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power4.in" }}, {s.L(g)});')
    s.j(f'tl.fromTo("#{tid}", {{ x: 0 }}, {{ keyframes: [{{ x: -10, duration: 0.03 }}, {{ x: 8, duration: 0.03 }}, {{ x: 0, duration: 0.03 }}] }}, {s.L(g + 0.14)});')
