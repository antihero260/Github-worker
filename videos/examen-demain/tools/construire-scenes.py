#!/usr/bin/env python3
"""Écrit les 12 scènes de « examen-demain » dans compositions/ (HTML statique).

Attention : relancer ce script ÉCRASE compositions/s*.html. Après une retouche à la main
(ou dans le Studio), modifier les fichiers HTML directement plutôt que de relancer.
"""
import importlib.util
import json
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
MOTS = json.loads((PROJET / "assets/mots.json").read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location("st", PROJET / "tools/sous-titres.py")
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)
TEXTE = st.mots_du_script(PROJET / "script.txt")  # casse et ponctuation d'origine
assert len(TEXTE) == len(MOTS)


def t_mot(i):
    return MOTS[i]["start"]


PICTO = ('<g class="pj-contour"><circle cx="50" cy="26" r="24" /><rect x="16" y="58" width="68" height="96" rx="10" />'
         '<rect x="21" y="140" width="25" height="118" rx="5" /><rect x="54" y="140" width="25" height="118" rx="5" /></g>'
         '<g class="pj-plein"><circle cx="50" cy="26" r="24" /><rect x="16" y="58" width="68" height="96" rx="10" />'
         '<rect x="21" y="140" width="25" height="118" rx="5" /><rect x="54" y="140" width="25" height="118" rx="5" /></g>')


def toi(id_, cx, pieds, h):
    w = round(h * 116 / 276)
    return (f'<svg id="{id_}" class="pj-picto pj-toi" viewBox="-8 -8 116 276" '
            f'style="left: {cx - w // 2}px; top: {pieds - h}px; width: {w}px; height: {h}px">{PICTO}</svg>')


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
        <div class="pj-horizon" style="top: 760px"></div>
        {corps}
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


# ---------------------------------------------------------------- S1
s = Scene("s1-heure", 0, 7.30, "Scène 1 · « Il est 23 h 17. Ton examen est demain matin… »", premiere=True)
cam(s, projecteur(560))
cam(s, toi("s1-toi", 560, 800, 400))
cam(s, '<div style="position: absolute; left: 700px; top: 640px; width: 460px; height: 22px; background: #8c8c8c"></div>'
       '<div style="position: absolute; left: 730px; top: 662px; width: 18px; height: 160px; background: #5a5a5a"></div>'
       '<div style="position: absolute; left: 1112px; top: 662px; width: 18px; height: 160px; background: #5a5a5a"></div>')
pages = "".join(f'<div class="s1-page" style="position: absolute; left: {800 + (k % 2) * 6}px; top: {622 - k * 13}px; width: 260px; height: 13px; '
                f'background: {"#ECECE8" if k % 2 == 0 else "#d6d6d0"}; border: 1px solid #9a9a96"></div>' for k in range(10))
cam(s, f'<div id="s1-pages">{pages}</div>')
cam(s, '<div id="s1-heure-bloc" style="position: absolute; left: 1180px; top: 150px">'
       '<div class="pj-label" style="position: static"><span class="pj-k">Heure</span><span class="pj-d">Veille d\'examen</span></div>'
       '<div class="pj-stat" style="position: static; font-size: 190px; line-height: 1">23:17</div></div>')
cam(s, '<div id="s1-pages-label" class="pj-label" style="left: 1180px; top: 470px"><span class="pj-k">À réviser</span>'
       '<span class="pj-d"><span id="s1-n">0</span> pages</span></div>')
cam(s, '<div id="s1-jauge" style="position: absolute; left: 1180px; top: 600px; width: 560px">'
       '<div class="pj-label" style="position: static"><span class="pj-k">Mémorisé</span></div>'
       '<div style="display: flex; gap: 8px; margin-top: 12px">' +
       "".join(f'<i class="s1-seg" style="flex: 1; height: 36px; background: #2a2a2a"></i>' for _ in range(10)) +
       '</div><div id="s1-pct" class="pj-stat" style="position: static; font-size: 64px; margin-top: 10px">0 %</div></div>')
s.add(hud_g("s1-hud", "Examen", "Demain · 08:00"))
s.add(hud_d("s1-rec", "Rec ●"))
s.j('tl.fromTo("#s1-hud", { opacity: 0 }, { opacity: 1, duration: 0.12 }, %s);' % s.L(t_mot(6)))
s.j('tl.fromTo(".s1-page", { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.08, stagger: 0.04, ease: "power2.out" }, %s);' % s.L(t_mot(12)))
s.apparait("#s1-pages-label", t_mot(12))
s.compteur("#s1-n", t_mot(12), 0, 40, 0.7)
s.apparait("#s1-jauge", t_mot(19))
s.j('tl.set(".s1-seg:first-child", { backgroundColor: "#DCFC1C" }, %s);' % s.L(t_mot(21)))
s.compteur("#s1-pct", t_mot(19), 0, 3, 0.8, "pct")
s.ecrire()

# ---------------------------------------------------------------- S2
s = Scene("s2-panique", 7.30, 15.45, "Scène 2 · « Tu commences à paniquer… tu as déjà oublié la moitié »")
cam(s, projecteur(560))
cam(s, toi("s2-toi", 560, 800, 400))
cam(s, '<div id="s2-equerres" class="pj-equerres" style="left: 450px; top: 360px; width: 220px; height: 480px"><i></i><i></i><i></i><i></i></div>')
cam(s, '<svg style="position: absolute; left: 113px; top: 230px; width: 900px; height: 120px; overflow: visible">'
       '<polyline id="s2-pouls" points="0,60 180,60 210,60 230,10 255,110 280,30 300,60 420,60 445,0 470,120 495,20 515,60 640,60 660,5 685,115 710,15 730,60 900,60" '
       'fill="none" stroke="#DCFC1C" stroke-width="5" stroke-dasharray="1400" stroke-dashoffset="1400" /></svg>')
cam(s, '<div id="s2-p1" class="pj-papier" data-layout-allow-overlap style="left: 960px; top: 250px; width: 500px; height: 560px; transform: rotate(-4deg)">'
       '<h3 style="font-size: 72px">Page 01</h3>' + "".join(f'<div class="s2-l1" style="height: 18px; width: {w}%; background: #b5b5b0; margin-top: 22px"></div>' for w in (96, 88, 92, 70, 94, 82, 90, 60, 86, 76, 93, 66)) + '</div>')
cam(s, '<div id="s2-p2" class="pj-papier" data-layout-allow-overlap style="left: 1080px; top: 280px; width: 500px; height: 560px; transform: rotate(3deg)">'
       '<h3 style="font-size: 72px">Page 02</h3>' + "".join(f'<div class="s2-l2" style="height: 18px; width: {w}%; background: #b5b5b0; margin-top: 22px"></div>' for w in (90, 94, 72, 88, 96, 64, 91, 83, 70, 95, 80, 68)) + '</div>')
cam(s, '<div id="s2-oublie" class="pj-sticker" style="left: 1150px; top: 620px; transform: rotate(-6deg)">Oublié.</div>')
cam(s, '<div id="s2-moitie" class="pj-stat" style="left: 113px; top: 400px; font-size: 90px">−50 %</div>')
s.add(hud_g("s2-hud", "Stress", "En hausse"))
s.add('<div id="s2-heure" class="pj-label" style="right: 113px; top: 107px; text-align: right"><span class="pj-k">Heure</span>'
      '<span id="s2-h" class="pj-stat" style="position: static; font-size: 90px; letter-spacing: 0; line-height: 1.1">23:17</span></div>')
s.claque("#s2-equerres", t_mot(23), 1.25)
s.j('tl.fromTo("#s2-pouls", { strokeDashoffset: 1400 }, { strokeDashoffset: 0, duration: 1.1, ease: "none" }, %s);' % s.L(t_mot(23)))
s.j('tl.fromTo("#s2-toi", { x: 0 }, { keyframes: [{ x: -8, duration: 0.05 }, { x: 8, duration: 0.05 }, { x: -6, duration: 0.05 }, { x: 0, duration: 0.05 }] }, %s);' % s.L(t_mot(25)))
s.glisse("#s2-p1", t_mot(29), 300)
s.glisse("#s2-p2", t_mot(33), 300)
s.compteur("#s2-h", t_mot(34), 23 * 60 + 17, 23 * 60 + 27, 0.9, "hhmm")
s.j('tl.to(".s2-l2:nth-child(odd)", { opacity: 0.08, duration: 0.25, stagger: 0.05 }, %s);' % s.L(t_mot(41)))
s.claque("#s2-oublie", t_mot(41))
s.apparait("#s2-moitie", t_mot(43))
s.ecrire()

# ---------------------------------------------------------------- S3
s = Scene("s3-chatgpt", 15.45, 23.10, "Scène 3 · « Alors, tu ouvres ChatGPT… une mission beaucoup plus utile »")
cam(s, projecteur(420))
cam(s, toi("s3-toi", 420, 800, 380))
cam(s, '<div id="s3-chat" class="pj-chat" style="left: 780px; top: 220px; width: 1000px; height: 590px">'
       '<div class="pj-chat-tete"><i></i><i></i><i></i><span style="margin-left: 14px">ChatGPT · nouvelle conversation</span></div>'
       '<div id="s3-msg" class="pj-msg" style="right: 30px; top: 110px">Résume mes 40 pages.</div>'
       '<div id="s3-x" class="pj-x" style="right: 30px; top: 110px; width: 470px; height: 103px"></div></div>')
cam(s, '<div id="s3-mission" class="pj-sticker" style="left: 1020px; top: 560px; transform: rotate(-4deg); font-size: 110px">Mission.</div>')
s.add(hud_g("s3-hud", "Outil", "ChatGPT"))
s.add(hud_d("s3-obj", "Objectif", "Plus utile", "opacity: 0"))
s.j('tl.fromTo("#s3-chat", { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 0.26, ease: "power4.out" }, %s);' % s.L(t_mot(53)))
s.apparait("#s3-hud", t_mot(53))
s.claque("#s3-msg", t_mot(62), 1.3)
s.croix("#s3-x", t_mot(66))
s.j('tl.to("#s3-msg", { opacity: 0.35, duration: 0.2 }, %s);' % s.L(t_mot(66) + 0.1))
s.claque("#s3-mission", t_mot(71))
s.j('tl.to("#s3-obj", { opacity: 1, duration: 0.12 }, %s);' % s.L(t_mot(72)))
s.ecrire()

# ---------------------------------------------------------------- S4
s = Scene("s4-prompt1", 23.10, 39.50, "Scène 4 · le premier prompt, tapé mot à mot")
cam(s, projecteur(300, op=0.85))
cam(s, toi("s4-toi", 300, 800, 340))
msg = message(s, "s4", 83, 121, {89, 90, 95, 96, 99, 100, 102, 107, 112, 113, 114, 115, 120, 121})
cam(s, '<div id="s4-chat" class="pj-chat" style="left: 560px; top: 210px; width: 1250px; height: 630px">'
       '<div class="pj-chat-tete"><i></i><i></i><i></i><span style="margin-left: 14px">ChatGPT · ta mission</span></div>'
       '<div id="s4-pj" class="pj-label" style="left: 30px; top: 92px; background: #262626; padding: 8px 18px; letter-spacing: 0.1em">'
       '<span class="pj-k">▣ cours.pdf · 40 pages</span></div>'
       f'<div class="pj-msg" style="left: 30px; top: 160px; width: 1186px">{msg}</div></div>')
s.add(hud_g("s4-hud", "Prompt 01", "La mission"))
s.add(etapes(s, "s4-c", ["Consignes : 0/5", "Consignes : 1/5", "Consignes : 2/5", "Consignes : 3/5", "Consignes : 4/5", "Consignes : 5/5"],
             [t_mot(97), t_mot(102), t_mot(107), t_mot(113), t_mot(116)], "right: 113px; top: 107px; width: 480px"))
s.apparait("#s4-pj", t_mot(77))
s.ecrire()

# ---------------------------------------------------------------- S5
s = Scene("s5-carte", 39.50, 49.80, "Scène 5 · « une première carte de révision. Mais attention… »")
cam(s, projecteur(420))
cam(s, toi("s5-toi", 420, 800, 380))
lignes = [("Notions essentielles", "12"), ("Définitions", "18"), ("Concepts à ne pas confondre", "5"), ("Passages ambigus", "2")]
cam(s, '<div id="s5-fiche" class="pj-papier" style="left: 820px; top: 150px; width: 900px; transform: rotate(-2deg)">'
       '<h3 style="font-size: 92px">Carte de révision</h3>' +
       "".join(f'<div id="s5-l{k}" class="pj-ligne" style="font-size: 34px; display: flex; justify-content: space-between; border-top: 2px solid #c8c8c2; padding-top: 14px">'
               f'<span>{a.upper()}</span><span style="background: #0a0a06; color: #dcfc1c; padding: 0 12px">{b}</span></div>' for k, (a, b) in enumerate(lignes)) + '</div>')
cam(s, '<div id="s5-gauche" class="pj-impact" style="position: absolute; left: 120px; width: 760px; top: 330px; text-align: center; font-size: 120px; color: #ECECE8; text-shadow: none; white-space: normal; opacity: 0">Lire un résumé</div>')
cam(s, '<div id="s5-diff" style="position: absolute; left: 885px; top: 380px; width: 150px; height: 130px; opacity: 0; filter: drop-shadow(0 0 18px rgba(220,252,28,0.45))">'
       '<i style="position: absolute; left: 0; top: 30px; width: 150px; height: 22px; background: #DCFC1C"></i>'
       '<i style="position: absolute; left: 0; top: 78px; width: 150px; height: 22px; background: #DCFC1C"></i>'
       '<i style="position: absolute; left: 64px; top: -10px; width: 22px; height: 150px; background: #DCFC1C; transform: rotate(28deg)"></i></div>')
cam(s, '<div id="s5-droite" class="pj-impact" style="position: absolute; left: 1040px; width: 760px; top: 330px; text-align: center; font-size: 120px; white-space: normal; opacity: 0">Connaître son cours</div>')
cam(s, '<div id="s5-etape" style="position: absolute; left: 0; width: 1920px; top: 260px; text-align: center; opacity: 0">'
       '<div class="pj-label" style="position: static"><span class="pj-k">Tu passes à</span></div>'
       '<div class="pj-impact" style="font-size: 260px; margin-top: 46px">Étape 02</div></div>')
s.add('<div id="s5-noir" style="position: absolute; inset: 0; background: #000; opacity: 0"></div>'
      '<div id="s5-attention" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 330px; text-align: center; font-size: 300px; opacity: 0">Attention.</div>')
s.eclair(t_mot(133))
s.add(hud_g("s5-hud", "Résultat", "En quelques instants"))
s.j('tl.fromTo("#s5-fiche", { opacity: 0, y: 140, rotation: 4 }, { opacity: 1, y: 0, rotation: -2, duration: 0.28, ease: "power4.out" }, %s);' % s.L(t_mot(125)))
for k, i in enumerate((128, 129, 130, 131)):
    s.apparait(f"#s5-l{k}", t_mot(i), dy=14, d=0.12)
s.j('tl.set(["#s5-noir", "#s5-attention"], { opacity: 1 }, %s);' % s.L(t_mot(133)))
s.choc("#s5-attention", t_mot(133))
s.j('tl.set(["#s5-noir", "#s5-attention", "#s5-fiche", "#s5-toi"], { opacity: 0 }, %s);' % s.L(t_mot(134)))
s.apparait("#s5-gauche", t_mot(134))
s.apparait("#s5-droite", t_mot(138))
s.claque("#s5-diff", t_mot(143))
s.j('tl.to(["#s5-gauche", "#s5-droite", "#s5-diff"], { opacity: 0, x: -200, duration: 0.2, ease: "power3.in" }, %s);' % s.L(t_mot(147)))
s.choc("#s5-etape", t_mot(150))
s.ecrire()

# ---------------------------------------------------------------- S6
s = Scene("s6-prompt2", 49.80, 63.80, "Scène 6 · le deuxième prompt : « interroge-moi comme un professeur »")
cam(s, projecteur(300, op=0.85))
cam(s, toi("s6-toi", 300, 800, 340))
msg = message(s, "s6", 159, 199, {161, 162, 163, 164, 165, 166, 167, 168, 175, 176, 177, 178, 184, 185, 186, 194, 195, 196, 197, 198, 199})
cam(s, '<div id="s6-chat" class="pj-chat" style="left: 560px; top: 210px; width: 1250px; height: 630px">'
       '<div class="pj-chat-tete"><i></i><i></i><i></i><span style="margin-left: 14px">ChatGPT · étape 02</span></div>'
       '<div class="pj-label" style="left: 30px; top: 92px; background: #262626; padding: 8px 18px; letter-spacing: 0.1em">'
       '<span class="pj-d">✓ carte de révision</span></div>'
       f'<div class="pj-msg" style="left: 30px; top: 160px; width: 1186px">{msg}</div></div>')
s.add(hud_g("s6-hud", "Prompt 02", "Le professeur"))
s.add(etapes(s, "s6-c", ["Règles : 0/4", "Règles : 1/4", "Règles : 2/4", "Règles : 3/4", "Règles : 4/4"],
             [t_mot(161), t_mot(169), t_mot(184), t_mot(193)], "right: 113px; top: 107px; width: 420px"))
s.ecrire()

# ---------------------------------------------------------------- S7
s = Scene("s7-rappel", 63.80, 73.40, "Scène 7 · relire passivement / rappel actif")
s.css.append("""    .s7-panneau {
      position: absolute;
      top: 235px;
      width: 830px;
      height: 560px;
      border: 2px solid #5a5a5a;
      overflow: hidden;
      background: radial-gradient(ellipse 60% 70% at 30% 72%, #2c2c2c 0%, #121212 75%);
    }""")
for k, (titre, gx) in enumerate((("▶ Avant · relire", 100), ("▶ Maintenant · se souvenir", 990))):
    jauge = "".join(f'<i class="s7-seg{k}" style="flex: 1; height: 30px; background: #2a2a2a"></i>' for _ in range(10))
    contenu = ('<div class="pj-papier" style="left: 300px; top: 150px; width: 300px; height: 300px; transform: rotate(-3deg); opacity: 0.55">' + papier_lignes(7, (92, 80, 95, 70, 88, 76, 90)) + '</div>') if k == 0 else (
        '<div id="s7-q" class="pj-impact" style="position: absolute; left: 330px; top: 120px; font-size: 300px; opacity: 0">?</div>')
    cam(s, f'<div id="s7-p{k}" class="s7-panneau" style="left: {gx}px">'
           f'<div class="pj-label" style="left: 30px; top: 24px"><span class="pj-k">{titre}</span></div>'
           f'<div class="pj-cone" style="left: -60px; height: 640px; width: 420px"></div>'
           + toi(f"s7-toi{k}", 150, 500, 300) + contenu +
           f'<div style="position: absolute; left: 300px; right: 40px; bottom: 40px"><div class="pj-label" style="position: static"><span class="pj-d">Effort de mémoire</span></div>'
           f'<div style="display: flex; gap: 6px; margin-top: 10px">{jauge}</div></div></div>')
s.add('<div id="s7-noir" style="position: absolute; inset: 0; background: #000; opacity: 0"></div>'
      '<div id="s7-titre" style="position: absolute; left: 0; width: 1920px; top: 280px; text-align: center; opacity: 0; transform-origin: 50% 0">'
      '<div class="pj-label" style="position: static"><span class="pj-k">La méthode</span></div>'
      '<div class="pj-impact" style="font-size: 250px; margin-top: 10px">Rappel actif.</div></div>'
      '<div id="s7-source" class="pj-label" style="left: 0; width: 1920px; top: 640px; text-align: center; opacity: 0"><span class="pj-k">Étudiée en sciences de l\'apprentissage</span></div>')
s.eclair(t_mot(222))
s.add(hud_g("s7-hud", "Comparaison", "Passif / actif"))
s.glisse("#s7-p0", t_mot(201), -900)
s.j('tl.set(".s7-seg0:nth-child(-n+1)", { backgroundColor: "#7a7a7a" }, %s);' % s.L(t_mot(208)))
s.glisse("#s7-p1", t_mot(209), 900)
s.claque("#s7-q", t_mot(212))
s.j('tl.to(".s7-seg1", { backgroundColor: "#DCFC1C", duration: 0.04, stagger: 0.08 }, %s);' % s.L(t_mot(214)))
s.j('tl.set(["#s7-noir", "#s7-titre"], { opacity: 1 }, %s);' % s.L(t_mot(222)))
s.j('tl.set(["#s7-p0", "#s7-p1"], { visibility: "hidden" }, %s);' % s.L(t_mot(222)))
s.choc("#s7-titre .pj-impact", t_mot(222))
s.j('tl.to("#s7-titre", { y: -60, duration: 0.3, ease: "power3.inOut" }, %s);' % s.L(t_mot(224)))
s.apparait("#s7-source", t_mot(224))
s.ecrire()

# ---------------------------------------------------------------- S8
s = Scene("s8-examen", 73.40, 81.45, "Scène 8 · cinq questions difficiles, puis un mini-examen")
cam(s, projecteur(360, op=0.9))
cam(s, toi("s8-toi", 360, 800, 360))
maitrise = ("20 %", "15 %", "30 %", "10 %", "25 %")
cam(s, '<div id="s8-cartes" style="position: absolute; left: 640px; top: 170px; width: 1180px; transform-origin: 50% 0">'
       '<div class="pj-label" style="position: static"><span class="pj-k">Questions difficiles</span><span class="pj-d">Sur tes points faibles</span></div>'
       '<div style="display: flex; gap: 26px; margin-top: 24px">' +
       "".join(f'<div style="width: 210px"><div class="pj-carte s8-q" style="position: relative; height: 260px; padding-top: 50px">'
               f'<div style="font-size: 110px">Q{k + 1}</div><div style="font-size: 60px; color: #98ac18">?</div></div>'
               f'<div class="pj-label s8-m" style="position: static; margin-top: 16px; text-align: center"><span class="pj-d">Maîtrise</span><span class="pj-k">{maitrise[k]}</span></div></div>'
               for k in range(5)) + '</div></div>')
cam(s, '<div id="s8-exam" class="pj-papier" style="left: 700px; top: 260px; width: 640px; opacity: 0; transform: rotate(-2deg)">'
       '<h3 style="font-size: 96px">Mini-examen</h3><div class="pj-ligne">5 QUESTIONS · SANS NOTES</div>' + papier_lignes(4, (92, 76, 88, 64)) + '</div>')
cam(s, '<div id="s8-chrono" style="position: absolute; left: 1420px; top: 300px; opacity: 0"><div class="pj-label" style="position: static"><span class="pj-k">Chrono</span></div>'
       '<div id="s8-t" class="pj-stat" style="position: static; font-size: 110px">15:00</div></div>')
cam(s, '<div id="s8-notes" class="pj-papier" style="left: 1420px; top: 520px; width: 330px; padding: 24px 30px; opacity: 0; transform: rotate(4deg)">'
       '<h3 style="font-size: 64px">Notes</h3>' + papier_lignes(3, (90, 70, 84)) + '<div id="s8-x" class="pj-x" style="left: 0; top: 0; width: 330px; height: 200px"></div></div>')
s.add(hud_g("s8-hud", "Entraînement", "Comme le jour J"))
s.j('tl.fromTo(".s8-q", { opacity: 0, y: 60, rotation: -6 }, { opacity: 1, y: 0, rotation: 0, duration: 0.18, stagger: 0.1, ease: "back.out(1.8)" }, %s);' % s.L(t_mot(236)))
s.j('tl.fromTo(".s8-m", { opacity: 0 }, { opacity: 1, duration: 0.1, stagger: 0.08 }, %s);' % s.L(t_mot(244)))
s.j('tl.to("#s8-cartes", { y: -400, opacity: 0, duration: 0.25, ease: "power3.in" }, %s);' % s.L(t_mot(250)))
s.j('tl.fromTo("#s8-exam", { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 0.26, ease: "power4.out", immediateRender: false }, %s);' % s.L(t_mot(252)))
s.j('tl.fromTo("#s8-chrono", { opacity: 0 }, { opacity: 1, duration: 0.12, immediateRender: false }, %s);' % s.L(t_mot(252)))
s.compteur("#s8-t", t_mot(252), 900, 893, 81.45 - t_mot(252) - 0.2, "mmss")
s.j('tl.fromTo("#s8-notes", { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: 0.18, ease: "power3.out", immediateRender: false }, %s);' % s.L(t_mot(253)))
s.croix("#s8-x", t_mot(255))
s.ecrire()

# ---------------------------------------------------------------- S9
s = Scene("s9-piege", 81.45, 91.85, "Scène 9 · le piège : vérifier dans le document original")
cam(s, '<div id="s9-chat" class="pj-chat" style="left: 120px; top: 240px; width: 820px; height: 580px; opacity: 0">'
       '<div class="pj-chat-tete"><i></i><i></i><i></i><span style="margin-left: 14px">Réponse de l\'IA</span></div>'
       '<div style="position: absolute; left: 30px; right: 30px; top: 100px; background: #232323; padding: 30px">'
       + "".join(f'<div style="height: 18px; width: {w}%; background: #5a5a5a; margin-bottom: 22px"></div>' for w in (94, 82, 90, 66, 88, 74, 92)) + '</div>'
       '<div id="s9-verite" class="pj-sticker" style="left: 150px; top: 330px; transform: rotate(-5deg); font-size: 80px; background: #ECECE8">Vérité absolue'
       '<div id="s9-rature" style="position: absolute; left: -12px; right: -12px; top: 50%; height: 12px; margin-top: -6px; background: #DCFC1C; transform-origin: 0 50%"></div></div></div>')
cam(s, '<div id="s9-liste" style="position: absolute; left: 1060px; top: 200px; opacity: 0">'
       '<div class="pj-label" style="position: static; margin-bottom: 30px"><span class="pj-k">Vérifie</span><span class="pj-d">Dans ton cours</span></div>' +
       "".join(f'<div class="pj-ligne-coche"><b id="s9-c{k}"></b>{t}</div>' for k, t in enumerate(("DÉFINITIONS", "FORMULES", "CORRECTIONS"))) + '</div>')
cam(s, '<div id="s9-doc" class="pj-papier" style="left: 1080px; top: 560px; width: 560px; padding: 26px 34px; opacity: 0">'
       '<h3 style="font-size: 66px">Document original</h3><div class="pj-ligne">COURS.PDF · 40 PAGES</div></div>')
cam(s, '<div id="s9-equerres" class="pj-equerres" style="left: 1050px; top: 530px; width: 620px; height: 230px; opacity: 0"><i></i><i></i><i></i><i></i></div>')
s.add('<div id="s9-noir" style="position: absolute; inset: 0; background: #000; opacity: 0"></div>'
      '<div id="s9-titre" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: 330px; text-align: center; font-size: 300px; opacity: 0">Le piège.</div>')
s.eclair(t_mot(260))
s.add(hud_g("s9-hud", "Attention", "Piège à éviter"))
s.j('tl.set("#s9-noir", { opacity: 1 }, 0);')
s.j('tl.set("#s9-titre", { opacity: 1 }, %s);' % s.L(t_mot(260)))
s.choc("#s9-titre", t_mot(260))
s.j('tl.set(["#s9-noir", "#s9-titre"], { opacity: 0 }, %s);' % s.L(t_mot(263)))
s.j('tl.fromTo("#s9-chat", { opacity: 0, x: -120 }, { opacity: 1, x: 0, duration: 0.24, ease: "power4.out", immediateRender: false }, %s);' % s.L(t_mot(263)))
s.claque("#s9-verite", t_mot(272))
s.rature("#s9-rature", t_mot(273))
s.j('tl.fromTo("#s9-liste", { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: 0.2, ease: "power3.out", immediateRender: false }, %s);' % s.L(t_mot(274)))
for k, i in enumerate((276, 278, 281)):
    s.j(f'tl.set("#s9-c{k}", {{ backgroundColor: "#DCFC1C", borderColor: "#DCFC1C" }}, {s.L(t_mot(i) + 0.1)});')
s.j('tl.fromTo("#s9-doc", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.2, ease: "power3.out", immediateRender: false }, %s);' % s.L(t_mot(285)))
s.claque("#s9-equerres", t_mot(286), 1.2)
s.ecrire()

# ---------------------------------------------------------------- S10
s = Scene("s10-heures", 91.85, 102.15, "Scène 10 · quelques heures : l'essentiel, puis apprendre et dormir")
cam(s, '<svg id="s10-cible" style="position: absolute; left: 660px; top: 120px; width: 600px; height: 600px; opacity: 0" viewBox="0 0 600 600">'
       '<circle cx="300" cy="300" r="290" fill="#ECECE8" /><circle cx="300" cy="300" r="230" fill="#111" />'
       '<circle cx="300" cy="300" r="170" fill="#ECECE8" /><circle cx="300" cy="300" r="110" fill="#111" /><circle cx="300" cy="300" r="56" fill="#DCFC1C" /></svg>')
cam(s, '<div id="s10-ess" class="pj-label" style="left: 1300px; top: 380px; opacity: 0"><span class="pj-k">Notions essentielles</span><span class="pj-d">Au centre</span></div>')
cam(s, '<div id="s10-lac" style="opacity: 0">' + "".join(f'<div class="s10-pt" style="position: absolute; left: {x}px; top: {y}px; width: 26px; height: 26px; border-radius: 50%; background: #DCFC1C; box-shadow: 0 0 0 6px #000"></div>' for x, y in ((770, 300), (1100, 520), (840, 600))) +
       '<div class="pj-label" style="left: 300px; top: 560px"><span class="pj-k">Tes lacunes</span><span class="pj-d">Questions ratées</span></div></div>')
cam(s, '<div id="s10-fiches" style="position: absolute; left: 260px; top: 330px; width: 1400px; height: 460px; opacity: 0">' +
       "".join(f'<div class="pj-papier s10-f" style="left: {k * 350}px; top: {(k % 2) * 30}px; width: 320px; height: 400px; padding: 26px; transform: rotate({(-3, 2, -2, 3)[k]}deg)">'
               f'<h3 style="font-size: 56px">Fiche {k + 1}</h3>' + papier_lignes(6, (90, 70, 84, 60, 92, 76)) + '</div>' for k in range(4)) +
       '<div id="s10-x" class="pj-x" style="left: 0; top: 0; width: 1400px; height: 460px"></div></div>')
cam(s, '<div id="s10-fin" style="position: absolute; left: 0; width: 1920px; top: 360px; text-align: center">'
       '<div id="s10-a" class="pj-impact" style="display: inline-block; font-size: 200px; margin-right: 80px; opacity: 0">Apprendre.</div>'
       '<div id="s10-d" class="pj-impact" style="display: inline-block; font-size: 200px; color: #ECECE8; text-shadow: none; opacity: 0">Dormir.</div></div>')
s.add('<div id="s10-temps" class="pj-label" style="left: 113px; top: 107px"><span class="pj-k">Temps restant</span>'
      '<span id="s10-t" class="pj-stat" style="position: static; font-size: 90px; letter-spacing: 0; line-height: 1.1">08:00</span></div>')
s.compteur("#s10-t", t_mot(292), 480, 180, 0.8, "hhmm")
s.j('tl.fromTo("#s10-cible", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(1.6)", immediateRender: false }, %s);' % s.L(t_mot(294)))
s.apparait("#s10-ess", t_mot(297))
s.j('tl.fromTo("#s10-lac", { opacity: 0 }, { opacity: 1, duration: 0.1, immediateRender: false }, %s);' % s.L(t_mot(303)))
s.j('tl.fromTo(".s10-pt", { scale: 0 }, { scale: 1, duration: 0.14, stagger: 0.1, ease: "back.out(3)" }, %s);' % s.L(t_mot(303)))
s.j('tl.to(["#s10-cible", "#s10-ess", "#s10-lac"], { opacity: 0, duration: 0.18 }, %s);' % s.L(t_mot(306)))
s.j('tl.set("#s10-fiches", { opacity: 1 }, %s);' % s.L(t_mot(313)))
s.j('tl.fromTo(".s10-f", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 0.16, stagger: 0.09, ease: "power3.out" }, %s);' % s.L(t_mot(313)))
s.croix("#s10-x", t_mot(315))
s.j('tl.to("#s10-fiches", { opacity: 0, duration: 0.15 }, %s);' % s.L(t_mot(318)))
s.choc("#s10-a", t_mot(320))
s.choc("#s10-d", t_mot(322))
s.ecrire()

# ---------------------------------------------------------------- S11
s = Scene("s11-prof", 102.15, 110.60, "Scène 11 · « il peut devenir le professeur qui te pose les questions »")
cam(s, projecteur(1300))
cam(s, toi("s11-toi", 1300, 800, 380))
cam(s, '<div id="s11-chat" class="pj-chat" style="left: 160px; top: 290px; width: 800px; height: 420px">'
       '<div class="pj-chat-tete"><i></i><i></i><i></i><span id="s11-nom" style="margin-left: 14px">ChatGPT</span></div>'
       '<div id="s11-place" class="pj-carte" style="left: 70px; top: 150px; padding: 18px 30px; font-size: 76px">Réviser à ta place'
       '<div id="s11-rature" style="position: absolute; left: -12px; right: -12px; top: 50%; height: 12px; margin-top: -6px; background: #DCFC1C; transform-origin: 0 50%"></div></div>'
       '<div id="s11-prof-mot" class="pj-impact" style="position: absolute; left: 0; width: 800px; top: 150px; text-align: center; font-size: 150px; opacity: 0">Professeur</div></div>')
cam(s, '<div id="s11-eq" class="pj-equerres" style="left: 130px; top: 260px; width: 860px; height: 480px; opacity: 0"><i></i><i></i><i></i><i></i></div>')
bulles = (("Pourquoi ?", 1020, 200), ("Et si… ?", 1460, 250), ("Explique.", 1090, 560), ("Quelle différence ?", 1440, 560))
for k, (t, x, y) in enumerate(bulles):
    cam(s, f'<div class="s11-b pj-serif" style="left: {x}px; top: {y}px; font-size: 56px; color: #0a0a06; background: #ECECE8; padding: 8px 24px; opacity: 0">{t}</div>')
s.add(hud_g("s11-hud", "Bien utilisé", "Mode professeur", "opacity: 0"))
s.j('tl.fromTo("#s11-chat", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 0.24, ease: "power4.out" }, %s);' % s.L(t_mot(323)))
s.rature("#s11-rature", t_mot(330))
s.j('tl.to("#s11-place", { opacity: 0.4, duration: 0.2 }, %s);' % s.L(t_mot(330) + 0.2))
s.j('tl.to("#s11-hud", { opacity: 1, duration: 0.12 }, %s);' % s.L(t_mot(332)))
s.j('tl.to("#s11-place", { opacity: 0, duration: 0.12 }, %s);' % s.L(t_mot(336)))
s.choc("#s11-prof-mot", t_mot(338))
s.claque("#s11-eq", t_mot(338), 1.15)
s.j('tl.fromTo(".s11-b", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.16, stagger: 0.28, ease: "back.out(2)" }, %s);' % s.L(t_mot(342)))
s.ecrire()

# ---------------------------------------------------------------- S12
s = Scene("s12-question", 110.60, 120.0, "Scène 12 · la question finale (appel à commenter)", derniere=True)
cam(s, projecteur(960))
cam(s, toi("s12-toi", 960, 800, 340))
cam(s, '<div id="s12-voix" class="pj-serif" style="left: 113px; top: 230px; font-size: 110px">' +
       " ".join(f'<span id="s12-v{k}">{w}</span>' for k, w in enumerate(("dis-moi", "…"))) + '</div>')
cam(s, '<div id="s12-a" class="pj-carte" style="left: 180px; top: 330px; width: 560px; padding: 40px 30px; font-size: 100px; opacity: 0">'
       '<div class="pj-label" style="position: static; margin-bottom: 18px"><span class="pj-d" style="color: #5a5a5a">Choix A</span></div>Résumer</div>')
cam(s, '<div id="s12-b" class="pj-carte" style="left: 1180px; top: 330px; width: 560px; padding: 40px 30px; font-size: 100px; background: #DCFC1C; opacity: 0">'
       '<div class="pj-label" style="position: static; margin-bottom: 18px"><span class="pj-d" style="color: #3a4a00">Choix B</span></div>T\'interroger</div>')
cam(s, '<div id="s12-q" class="pj-impact" style="position: absolute; left: 860px; width: 200px; top: 150px; text-align: center; font-size: 230px; opacity: 0">?</div>')
s.add(hud_g("s12-hud", "Examen", "Demain · 08:00"))
s.add(hud_d("s12-com", "Ta réponse", "En commentaire", "opacity: 0"))
s.montre("#s12-v0", t_mot(352))
s.montre("#s12-v1", t_mot(352) + 0.4)
s.j('tl.to("#s12-voix", { opacity: 0, duration: 0.15 }, %s);' % s.L(t_mot(362)))
s.glisse("#s12-a", t_mot(363), -200)
s.glisse("#s12-b", t_mot(368), 200)
s.claque("#s12-q", t_mot(374))
s.j('tl.to("#s12-com", { opacity: 1, duration: 0.15 }, %s);' % s.L(t_mot(374)))
s.ecrire()
print("12 scènes écrites")
