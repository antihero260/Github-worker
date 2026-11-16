#!/usr/bin/env python3
"""Edit vertical 1080×1920 « Tous les modèles Claude » (2023 → 2026), calé sur les temps d'un mix de deux morceaux Mixkit.

Son : assets/music/mix-claude.mp3 (tools/temps.json) : « Hip Hop 02 » 32 temps (0–20,06 s), puis « Thunder » :
8 temps de montée calme (silence au temps 38, roulement au 39), DROP au temps 40 (25,08 s), 32 temps à fond, fin 46,6 s.

Déroulé (en temps) :
  0–6    hook : vraie vidéo à chaque demi-temps, logo Claude qui claque, « TOUS LES MODÈLES », « 2023 → 2026 »
  6–28   2023, 2024, 2025 : carte de l'année (2 temps) puis un modèle par temps (nom géant + date)
  28–32  récap : les 16 noms défilent au quart de temps, « 16 MODÈLES EN 3 ANS »
  32–39  montée : « ET EN 2026… », page officielle des annonces, image qui s'assombrit, silence au temps 38
  40     DROP : « 2026 » explose
  41–55  les 15 modèles de 2026, un par temps (stroboscope, secousses)
  56–63  la famille actuelle : Fable 5.2, Opus 5.5, Sonnet 5.5, Haiku 5.5 (rôle de chacun, d'après la doc officielle)
  64–fin les 4 cartes + logo + « TU UTILISES LEQUEL ? »
Sources des dates : platform.claude.com/docs (Models overview) et Wikipédia « Claude (language model) », vérifiées le 16 nov. 2026.
Relancer ce script ÉCRASE index.html.
"""
import json
import math
import subprocess
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent.parent
TP = json.loads((ICI / "tools/temps.json").read_text())
BEATS = TP["beats"]
FIN = TP["fin"]
P = 60 / TP["bpm"]
TERRA, CREME, NOIR, BLANC = "#D97757", "#F0EEE6", "#141413", "#FFFFFF"


def B(x):
    """Temps (en secondes) du temps musical x (fractions acceptées)."""
    return round(x * P, 3)


HTML, JS, SONS = [], [], []


def j(l):
    JS.append("      " + l)


# ================================================================ SON
SFX = ICI / "assets/sfx"


def _pics():
    f = SFX / "pics.json"
    if f.exists():
        return json.loads(f.read_text())
    d = {}
    for m in sorted(SFX.glob("*.mp3")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(m), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, dtype=np.float32)
        n = len(x) // 400
        e = (x[: n * 400].reshape(n, 400) ** 2).mean(1)
        d[m.stem] = {"pic": round(float(e.argmax()) * 400 / 8000, 3), "duree": round(len(x) / 8000, 3)}
    f.write_text(json.dumps(d, indent=1) + "\n")
    return d


PICS = _pics()


def son(t, nom, v=0.35, note="", sur_pic=True, d=None):
    p = PICS[nom]
    debut = max(0.0, t - (p["pic"] if sur_pic else 0))
    duree = min(p["duree"], d or 99, FIN - debut)
    if duree > 0.05:
        SONS.append((round(debut, 3), nom, round(v, 3), note, round(duree, 3)))


TOURS = {}


def tour(liste):
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


WHOOSH = ["whoosh-cine", "swoosh-court", "whoosh-fusee", "balaie-rapide", "whoosh-metal", "fouet", "swoosh-vitesse", "whoosh-stutter"]
IMPACT = ["impact-basse", "trailer-impact", "impact-tambour", "impact-futur", "trailer-impact-2"]

# ================================================================ VIDÉOS (plein cadre, une par temps)
PISTE = [10]


def plein(f, t0, t1, src="video", filtre=""):
    vid = f"v{len(HTML)}"
    PISTE[0] += 1
    HTML.append(f'<video id="{vid}" class="clip vp" src="assets/{src}/{f}.mp4" data-start="{t0}" data-duration="{round(t1 - t0 + 0.04, 3)}" '
                f'data-track-index="{2 + PISTE[0] % 6}" muted playsinline style="opacity: 0{filtre}"></video>')
    j(f'tl.set("#{vid}", {{ opacity: 1 }}, {t0});')
    j(f'tl.fromTo("#{vid}", {{ scale: 1.22 }}, {{ scale: 1.02, duration: {round(t1 - t0, 3)}, ease: "power2.out", immediateRender: false }}, {t0});')
    j(f'tl.set("#{vid}", {{ opacity: 0 }}, {round(t1 + 0.02, 3)});')
    return vid


def rafale(liste, debut, pas, src="video", sons=True, v=0.3):
    for k, f in enumerate(liste):
        t0, t1 = round(debut + k * pas, 3), round(debut + (k + 1) * pas, 3)
        plein(f, t0, t1, src)
        if sons and k:
            son(t0, tour(WHOOSH), v, f"coupe {f}")


# ================================================================ CALQUES (textes, logo, effets) : toujours dans le DOM, animés par la timeline
CALQUES = []


def calque(h):
    CALQUES.append(h)


NID = [0]


def nid(p="e"):
    NID[0] += 1
    return f"{p}{NID[0]}"


def claque(sel, t, s0=2.2, d=0.14):
    j(f'tl.fromTo("{sel}", {{ opacity: 0, scale: {s0} }}, {{ opacity: 1, scale: 1, duration: {d}, ease: "power4.in", immediateRender: false }}, {t});')


def sort(sel, t, d=0.08):
    j(f'tl.to("{sel}", {{ opacity: 0, duration: {d} }}, {t});')


def flash(t, coul=BLANC, op=0.85):
    i = nid("fl")
    calque(f'<div id="{i}" class="flash" style="background: {coul}"></div>')
    j(f'tl.fromTo("#{i}", {{ opacity: {op} }}, {{ opacity: 0, duration: 0.22, immediateRender: false }}, {t});')


def secousse(t, a=22):
    j(f'tl.to("#cadre", {{ keyframes: [{{ x: -{a}, y: {a // 2}, duration: 0.03 }}, {{ x: {a}, y: -{a // 2}, duration: 0.04 }}, {{ x: -{a // 2}, duration: 0.04 }}, {{ x: 0, y: 0, duration: 0.03 }}] }}, {t});')


def punch(t, s=1.08, d=0.3):
    j(f'tl.fromTo("#cadre", {{ scale: {s} }}, {{ scale: 1, duration: {d}, ease: "power3.out", immediateRender: false }}, {t});')


def modele(nom, date, t, t_fin, gros=200, effet=0, etiquette=""):
    """Nom de modèle géant (« CLAUDE » au-dessus, date dessous) qui claque sur le temps."""
    i = nid("m")
    tag = f'<em>{etiquette}</em>' if etiquette else ""
    calque(f'<div id="{i}" class="modele" style="opacity: 0"><span>CLAUDE</span><b style="font-size: {gros}px">{nom}</b><i>{date}</i>{tag}</div>')
    if effet % 3 == 0:
        claque(f"#{i}", t)
    elif effet % 3 == 1:
        j(f'tl.fromTo("#{i}", {{ opacity: 0, x: 420, skewX: -18 }}, {{ opacity: 1, x: 0, skewX: 0, duration: 0.14, ease: "power3.out", immediateRender: false }}, {t});')
    else:
        j(f'tl.fromTo("#{i}", {{ opacity: 0, y: 260, rotation: -6 }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.14, ease: "back.out(2)", immediateRender: false }}, {t});')
    j(f'tl.fromTo("#{i} b", {{ textShadow: "-14px 0 0 #00e5ff, 14px 0 0 #ff2a6d" }}, {{ textShadow: "0px 0 0 #00e5ff, 0px 0 0 #ff2a6d", duration: 0.2, immediateRender: false }}, {t});')
    sort(f"#{i}", round(t_fin - 0.02, 3), 0.04)
    return i


def annee(an, t, t_fin, sous=""):
    i = nid("a")
    calque(f'<div id="{i}" class="annee" style="opacity: 0"><b>{an}</b><span>{sous}</span></div>')
    claque(f"#{i}", t, 3.0, 0.16)
    j(f'tl.to("#{i} b", {{ scale: 1.12, duration: {round(t_fin - t, 3)}, ease: "none" }}, {t});')
    sort(f"#{i}", round(t_fin - 0.02, 3), 0.05)
    son(t, tour(IMPACT), 0.55, f"année {an}")
    flash(t, TERRA, 0.9)
    secousse(t + 0.05, 26)


# ================================================================ 1. HOOK (temps 0 → 6)
hook = ["claude-code-site", "ecrans-code", "hologramme-main", "data-center", "robot-yeux", "doigts-tapent", "globe-reseau", "code-html-bleu",
        "main-hologramme", "serveurs-lumieres", "tunnel-virtuel-bleu", "macbook-pro"]
rafale(hook, 0, B(0.5), v=0.34)
son(0, "trailer-impact", 0.6, "début")
son(0, "whoosh-cine", 0.45, "début")
calque('<div id="logo" class="logo" style="opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /></div>')
claque("#logo", 0.02, 3.0, 0.18)
j('tl.fromTo("#logo img", { rotation: 0 }, { rotation: 360, duration: %s, ease: "none", immediateRender: false }, 0.02);' % B(6))
j(f'tl.to("#logo", {{ scale: 0.42, y: -560, duration: 0.3, ease: "power3.inOut" }}, {B(2) - 0.1});')
calque('<div id="h-claude" class="gros-titre" style="opacity: 0">CLAUDE</div>')
claque("#h-claude", B(1), 2.6)
son(B(1), "impact-futur", 0.5, "CLAUDE")
calque('<div id="h-tous" class="bande-titre" style="opacity: 0">TOUS SES MODÈLES</div>')
claque("#h-tous", B(2), 1.8)
son(B(2), "impact-tambour", 0.5, "tous ses modèles")
calque('<div id="h-dates" class="dates-hook" style="opacity: 0">2023 <i>→</i> 2026</div>')
claque("#h-dates", B(3), 1.8)
son(B(3), "glitch-cine", 0.45, "2023 → 2026")
for k in range(4, 6):
    punch(B(k), 1.06, 0.25)
flash(B(4) + 0.0, BLANC, 0.5)
for sel in ("#h-claude", "#h-tous", "#h-dates"):
    sort(sel, B(6) - 0.03, 0.05)
j(f'tl.to("#logo", {{ opacity: 0, duration: 0.1 }}, {B(6) - 0.05});')
son(B(5.5), "riser-tech", 0.35, "montée vers 2023", d=0.4)

# ================================================================ 2. 2023 → 2025 (temps 6 → 28)
ANS = [
    ("2023", 6, [("1", "MARS 2023"), ("2", "JUILLET 2023"), ("INSTANT 1.2", "AOÛT 2023"), ("2.1", "NOVEMBRE 2023")]),
    ("2024", 12, [("3 HAIKU", "MARS 2024"), ("3 SONNET", "MARS 2024"), ("3 OPUS", "MARS 2024"), ("3.5 SONNET", "JUIN 2024"), ("3.5 HAIKU", "OCTOBRE 2024")]),
    ("2025", 19, [("3.7 SONNET", "FÉVRIER 2025"), ("OPUS 4", "MAI 2025"), ("SONNET 4", "MAI 2025"), ("OPUS 4.1", "AOÛT 2025"), ("SONNET 4.5", "SEPTEMBRE 2025"),
                  ("HAIKU 4.5", "OCTOBRE 2025"), ("OPUS 4.5", "NOVEMBRE 2025")]),
]
FONDS_A = ["code-ecran", "laptop-homme", "clavier-gros-plan", "ecrans-matrix", "hologramme-web", "sphere-donnees", "robot-salut", "cursor-site",
           "code-techno", "traces-lumiere", "particules-lumineuses", "vr-mains-interface", "homme-ordi-joie", "neon-3d-route", "terre-3d", "hologramme-paiement"]
FONDS_AN = {"2023": "trou-de-ver", "2024": "supernova", "2025": "eclair-ville"}
noms_ab = []
fk = 0
for an, b0, liste in ANS:
    plein(FONDS_AN[an], B(b0), B(b0 + 2))
    annee(an, B(b0), B(b0 + 2))
    for k, (nom, date) in enumerate(liste):
        t0, t1 = B(b0 + 2 + k), B(b0 + 3 + k)
        plein(FONDS_A[fk % len(FONDS_A)], t0, t1)
        modele(nom, date, t0, t1, 210 if len(nom) <= 6 else (170 if len(nom) <= 9 else 140), fk)
        son(t0, tour(WHOOSH), 0.42, f"modèle {nom}")
        son(t0 + 0.02, tour(["pop-sec", "pop-click", "impact-cartoon", "pop-long"]), 0.3, "claque du nom")
        punch(t0, 1.07, 0.28)
        if fk % 2 == 0:
            flash(t0, BLANC, 0.35)
        noms_ab.append(nom)
        fk += 1

# ================================================================ 3. RÉCAP (temps 28 → 32) : les 16 noms au quart de temps
plein("feux-artifice", B(28), B(32))
calque(f'<div id="r-titre" class="bande-titre" style="top: 1180px; opacity: 0">16 MODÈLES EN 3 ANS</div>')
claque("#r-titre", B(28), 1.8)
son(B(28), "impact-basse", 0.5, "16 modèles en 3 ans")
for k, nom in enumerate(noms_ab):
    t0, t1 = B(28 + k * 0.25), B(28 + (k + 1) * 0.25)
    i = nid("rc")
    calque(f'<div id="{i}" class="recap" style="opacity: 0">CLAUDE {nom}</div>')
    j(f'tl.set("#{i}", {{ opacity: 1 }}, {t0});')
    j(f'tl.set("#{i}", {{ opacity: 0 }}, {t1});')
    if k % 2 == 0:
        son(t0, "clic", 0.25, "défilement des noms")
sort("#r-titre", B(32) - 0.03)

# ================================================================ 4. MONTÉE (temps 32 → 40) : « ET EN 2026… »
calque('<div id="m-nav" class="fenetre" style="opacity: 0"><div class="barre-nav"><i></i><i></i><i></i><span>anthropic.com/news</span></div>'
       f'<div class="fen-in"><video id="m-cap" class="clip" src="assets/captures/anthropic-news.mp4" data-start="{B(32)}" data-duration="{round(B(38) - B(32), 3)}" '
       'data-track-index="9" muted playsinline></video></div></div>')
plein("tunnel-virtuel-bleu", B(32), B(38), filtre="; filter: brightness(0.45) saturate(0.6)")
j(f'tl.fromTo("#m-nav", {{ opacity: 0, y: 200, scale: 0.8 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out", immediateRender: false }}, {B(32)});')
j(f'tl.to("#m-nav", {{ scale: 1.5, y: 120, duration: {round(B(38) - B(33), 3)}, ease: "power1.in" }}, {B(33)});')
sort("#m-nav", B(38) - 0.02, 0.05)
calque('<div id="m-et" class="gros-titre" style="top: 1220px; font-size: 130px; opacity: 0">ET EN 2026…</div>')
j(f'tl.fromTo("#m-et", {{ opacity: 0, scaleX: 1.6 }}, {{ opacity: 1, scaleX: 1, duration: 0.8, ease: "power2.out", immediateRender: false }}, {B(34)});')
sort("#m-et", B(38) - 0.02, 0.05)
son(B(32), "whoosh-tunnel", 0.45, "on entre dans 2026")
son(B(34), "riser-trailer", 0.5, "montée", d=B(38) - B(34))
son(B(36), "battements", 0.4, "cœur qui bat", d=B(38) - B(36))
for k in range(34, 38):
    secousse(B(k), 6 + (k - 34) * 4)
calque('<div id="noir" class="flash" style="background: #000"></div>')
j(f'tl.set("#noir", {{ opacity: 1 }}, {B(38)});')
j(f'tl.set("#noir", {{ opacity: 0 }}, {B(39)});')
calque('<div id="m-2026" class="annee" style="opacity: 0"><b>2026</b><span>ACCROCHE-TOI</span></div>')
j(f'tl.fromTo("#m-2026", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: {round(P, 3)}, ease: "power2.in", immediateRender: false }}, {B(39)});')
son(B(39), "roulement-suspense", 0.45, "roulement avant le drop", d=P)

# ================================================================ 5. DROP (temps 40) et les 15 modèles de 2026
DROP = B(40)
plein("explosion-particules", DROP, B(41))
j(f'tl.to("#m-2026", {{ scale: 1.6, opacity: 0, duration: {round(P, 3)}, ease: "power2.out" }}, {DROP});')
son(DROP, "trailer-impact", 0.7, "DROP")
son(DROP, "explosion" if "explosion" in PICS else "impact-basse", 0.5, "DROP")
flash(DROP, BLANC, 1.0)
secousse(DROP + 0.04, 40)
M2026 = [("OPUS 4.6", "FÉVRIER 2026", ""), ("SONNET 4.6", "FÉVRIER 2026", ""), ("OPUS 4.7", "AVRIL 2026", ""), ("MYTHOS PREVIEW", "AVRIL 2026", "ACCÈS LIMITÉ"),
         ("OPUS 4.8", "MAI 2026", ""), ("MYTHOS 5", "JUIN 2026", "ACCÈS LIMITÉ"), ("FABLE 5", "JUIN 2026", ""), ("SONNET 5", "JUIN 2026", ""),
         ("OPUS 5", "JUILLET 2026", ""), ("FABLE 5.1", "SEPTEMBRE 2026", ""), ("MYTHOS 5.1", "SEPTEMBRE 2026", "ACCÈS LIMITÉ"), ("OPUS 5.5", "SEPTEMBRE 2026", ""),
         ("SONNET 5.5", "SEPTEMBRE 2026", ""), ("HAIKU 5.5", "OCTOBRE 2026", ""), ("FABLE 5.2", "NOVEMBRE 2026", "LE PLUS RÉCENT")]
FONDS_B = ["nasa-artemis-decolle", "foule-saute", "lasers", "dj-scene", "nasa-booster-feu", "public-mains", "fusee", "festival-saute", "lumieres-scene",
           "foule-bras", "eclair-ville", "poings-joie", "danse-lumieres" if (ICI / "assets/video/danse-lumieres.mp4").exists() else "traces-lumiere",
           "homme-tel-joie", "supernova"]
for k, (nom, date, tag) in enumerate(M2026):
    t0, t1 = B(41 + k), B(42 + k)
    plein(FONDS_B[k], t0, t1)
    modele(nom, date, t0, t1, 190 if len(nom) <= 8 else (150 if len(nom) <= 10 else 112), k, tag)
    son(t0, tour(IMPACT[:4]), 0.42, f"modèle {nom}")
    son(t0, tour(WHOOSH), 0.38, "souffle")
    secousse(t0 + 0.03, 18)
    punch(t0, 1.1, 0.3)
    flash(t0, TERRA if k % 2 else BLANC, 0.45)
    # contre-temps : petit stroboscope
    j(f'tl.fromTo("#strobe", {{ opacity: 0.5 }}, {{ opacity: 0, duration: 0.08, immediateRender: false }}, {B(41.5 + k)});')
calque('<div id="strobe" class="flash" style="background: #fff"></div>')

# ================================================================ 6. LA FAMILLE ACTUELLE (temps 56 → 64), rôles d'après la doc officielle
FAMILLE = [("FABLE 5.2", "Raisonnement exigeant et longues tâches d’agent", "trou-de-ver"),
           ("OPUS 5.5", "Agents et code sur la durée", "ecrans-code"),
           ("SONNET 5.5", "Le meilleur équilibre vitesse / intelligence", "neon-3d-route"),
           ("HAIKU 5.5", "Le plus rapide, pour les tâches en volume", "traces-lumiere")]
calque('<div id="f-lab" class="bande-titre" style="top: 360px; opacity: 0">LA FAMILLE ACTUELLE</div>')
claque("#f-lab", B(56), 1.8)
son(B(56), "impact-basse", 0.55, "la famille actuelle")
for k, (nom, role, fond) in enumerate(FAMILLE):
    t0, t1 = B(56 + 2 * k), B(58 + 2 * k)
    plein(fond, t0, t1, filtre="; filter: brightness(0.7)")
    i = nid("fa")
    calque(f'<div id="{i}" class="carte-fam" style="opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /><b>{nom}</b><span>{role}</span></div>')
    j(f'tl.fromTo("#{i}", {{ opacity: 0, rotationY: 90 }}, {{ opacity: 1, rotationY: 0, duration: 0.25, ease: "back.out(1.6)", immediateRender: false }}, {t0});')
    sort(f"#{i}", t1 - 0.02, 0.05)
    son(t0, tour(["whoosh-tunnel", "whoosh-cine", "zoom-impact", "whoosh-fusee"]), 0.45, f"carte {nom}")
    son(t0 + 0.05, "revelation", 0.4, "révélation")
    punch(t0, 1.08, 0.35)
    secousse(B(57 + 2 * k), 14)
sort("#f-lab", B(64) - 0.03)

# ================================================================ 7. FIN (temps 64 → fin) : les 4 cartes, la page officielle, « tu utilises lequel ? »
plein("particules-lumineuses", B(64), FIN, filtre="; filter: brightness(0.55)")
cartes = "".join(f'<div id="g{k}" class="mini-fam" style="opacity: 0"><b>{nom}</b></div>' for k, (nom, _, _) in enumerate(FAMILLE))
calque(f'<div id="grille" class="grille-fam">{cartes}</div>')
for k in range(4):
    claque(f"#g{k}", B(64 + k * 0.5), 1.8)
    son(B(64 + k * 0.5), tour(["pop-sec", "pop-cartoon", "pop-click", "pop-long"]), 0.4, "mini carte")
calque('<div id="fin-logo" class="logo" style="top: 360px; opacity: 0"><img src="assets/img/logo-claude.svg" alt="" /></div>')
claque("#fin-logo", B(64), 2.4)
j(f'tl.fromTo("#fin-logo img", {{ rotation: 0 }}, {{ rotation: 180, duration: {round(FIN - B(64), 3)}, ease: "none", immediateRender: false }}, {B(64)});')
calque('<div id="fin-q" class="gros-titre" style="top: 1170px; font-size: 110px; opacity: 0">TU UTILISES LEQUEL ?</div>')
claque("#fin-q", B(66), 1.8)
son(B(66), "impact-tambour", 0.5, "tu utilises lequel")
calque('<div id="fin-com" class="etiq-com" style="opacity: 0">DIS-LE EN COMMENTAIRE</div>')
claque("#fin-com", B(68), 1.6)
son(B(68), "notif-positive", 0.4, "commentaire")
for k in range(64, 72, 2):
    secousse(B(k), 10)
j(f'tl.fromTo("#fondu", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.8, immediateRender: false }}, {round(FIN - 0.8, 3)});')
calque('<div id="fondu" class="flash" style="background: #000"></div>')

# ================================================================ ÉCRITURE
_vus = set()
SONS[:] = [x for x in SONS if not ((x[0], x[1]) in _vus or _vus.add((x[0], x[1])))]
CSS = f"""
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.woff2") format("woff2"); }}
      @font-face {{ font-family: "Inter Lf"; src: url("assets/fonts/Inter-ExtraBold.otf") format("opentype"); font-weight: 800; }}
      @font-face {{ font-family: "Serif It"; src: url("assets/fonts/InstrumentSerif-Italic.woff2") format("woff2"); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: {NOIR}; }}
      #cadre {{ position: absolute; inset: 0; overflow: hidden; transform-origin: 50% 50%; }}
      .vp {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #voile {{ position: absolute; inset: 0; z-index: 20; pointer-events: none;
        background: radial-gradient(ellipse 75% 55% at 50% 50%, rgba(20,20,19,0.25) 0%, rgba(20,20,19,0.78) 100%), linear-gradient(180deg, rgba(217,119,87,0.18), rgba(20,20,19,0) 40%, rgba(217,119,87,0.12)); }}
      #calques {{ position: absolute; inset: 0; z-index: 30; pointer-events: none; }}
      .flash {{ position: absolute; inset: 0; opacity: 0; z-index: 60; }}
      #titre {{ position: absolute; left: 0; top: 0; width: 1080px; height: 300px; z-index: 50; display: flex; justify-content: center; padding-top: 140px;
        background: linear-gradient(180deg, rgba(20,20,19,0.9), rgba(20,20,19,0)); }}
      #titre b {{ font-family: "Anton", sans-serif; font-weight: 400; font-size: 60px; color: #fff; letter-spacing: 1px; }}
      #titre b i {{ font-style: normal; color: {TERRA}; }}
      .logo {{ position: absolute; left: 340px; top: 700px; width: 400px; height: 400px; z-index: 31; filter: drop-shadow(0 0 60px rgba(217,119,87,0.8)); }}
      .logo img {{ width: 100%; height: 100%; }}
      .gros-titre {{ position: absolute; left: 0; top: 1130px; width: 1080px; text-align: center; font-family: "Anton", sans-serif; font-size: 230px; line-height: 1; color: {CREME};
        -webkit-text-stroke: 14px {NOIR}; paint-order: stroke fill; text-shadow: 0 0 50px rgba(217,119,87,0.6); }}
      .bande-titre {{ position: absolute; left: 90px; top: 1400px; width: 900px; text-align: center; font-family: "Anton", sans-serif; font-size: 96px; line-height: 1; color: {NOIR};
        background: {TERRA}; border: 8px solid {NOIR}; padding: 18px 0 10px; transform: rotate(-3deg); }}
      .dates-hook {{ position: absolute; left: 0; top: 1570px; width: 1080px; text-align: center; font-family: "Anton", sans-serif; font-size: 110px; color: #fff;
        -webkit-text-stroke: 10px {NOIR}; paint-order: stroke fill; }}
      .dates-hook i {{ font-style: normal; color: {TERRA}; }}
      .annee {{ position: absolute; left: 0; top: 560px; width: 1080px; text-align: center; }}
      .annee b {{ display: block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 400px; line-height: 1; color: {CREME}; -webkit-text-stroke: 18px {NOIR}; paint-order: stroke fill;
        text-shadow: 0 0 90px rgba(217,119,87,0.9); }}
      .annee span {{ display: inline-block; margin-top: 30px; font-family: "Anton", sans-serif; font-size: 80px; color: {NOIR}; background: {TERRA}; padding: 8px 30px 2px; border: 6px solid {NOIR}; }}
      .annee span:empty {{ display: none; }}
      .modele {{ position: absolute; left: 0; top: 660px; width: 1080px; text-align: center; }}
      .modele span {{ display: inline-block; font-family: "Anton", sans-serif; font-size: 84px; letter-spacing: 12px; color: {NOIR}; background: {TERRA}; padding: 6px 28px 0; border: 6px solid {NOIR}; }}
      .modele b {{ display: block; font-family: "Anton", sans-serif; font-weight: 400; line-height: 1.02; color: {CREME}; -webkit-text-stroke: 14px {NOIR}; paint-order: stroke fill; margin-top: 20px; white-space: nowrap; }}
      .modele i {{ display: inline-block; margin-top: 26px; font-family: "Inter Lf", sans-serif; font-weight: 800; font-style: normal; font-size: 48px; color: #fff; background: rgba(20,20,19,0.85);
        border: 4px solid {CREME}; border-radius: 40px; padding: 10px 34px; }}
      .modele em {{ display: block; width: max-content; margin: 22px auto 0; font-family: "Anton", sans-serif; font-style: normal; font-size: 56px; color: {NOIR}; background: {CREME}; padding: 6px 24px 0; transform: rotate(-3deg); }}
      .recap {{ position: absolute; left: 0; top: 820px; width: 1080px; text-align: center; font-family: "Anton", sans-serif; font-size: 150px; line-height: 1; color: {CREME};
        -webkit-text-stroke: 12px {NOIR}; paint-order: stroke fill; white-space: nowrap; }}
      .fenetre {{ position: absolute; left: 60px; top: 520px; width: 960px; height: 600px; border-radius: 26px; overflow: hidden; background: #fff; border: 6px solid {CREME};
        box-shadow: 0 40px 120px rgba(0,0,0,0.7); z-index: 32; }}
      .barre-nav {{ height: 60px; background: #e8e6df; display: flex; align-items: center; gap: 12px; padding: 0 20px; }}
      .barre-nav i {{ width: 18px; height: 18px; border-radius: 50%; background: #c9c5ba; }}
      .barre-nav span {{ margin-left: 16px; flex: 1; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 26px; color: #555; background: #fff; border-radius: 20px; padding: 6px 18px; }}
      .fen-in {{ position: absolute; left: 0; top: 60px; right: 0; bottom: 0; overflow: hidden; }}
      .fen-in video {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 0; }}
      .carte-fam {{ position: absolute; left: 90px; top: 620px; width: 900px; padding: 50px 50px 56px; text-align: center; background: rgba(240,238,230,0.96); border: 10px solid {NOIR};
        border-radius: 44px; box-shadow: 0 40px 120px rgba(0,0,0,0.7); }}
      .carte-fam img {{ width: 150px; height: 150px; }}
      .carte-fam b {{ display: block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 170px; line-height: 1.05; color: {NOIR}; margin-top: 10px; }}
      .carte-fam span {{ display: block; font-family: "Inter Lf", sans-serif; font-weight: 800; font-size: 46px; line-height: 1.2; color: {TERRA}; margin-top: 16px; }}
      .grille-fam {{ position: absolute; left: 70px; top: 760px; width: 940px; display: grid; grid-template-columns: 1fr 1fr; gap: 26px; }}
      .mini-fam {{ background: {CREME}; border: 8px solid {NOIR}; border-radius: 28px; padding: 30px 10px 22px; text-align: center; }}
      .mini-fam b {{ font-family: "Anton", sans-serif; font-weight: 400; font-size: 88px; line-height: 1; color: {NOIR}; }}
      .etiq-com {{ position: absolute; left: 240px; top: 1330px; font-family: "Anton", sans-serif; font-size: 56px; color: {NOIR}; background: #fff; border: 6px solid {NOIR};
        padding: 8px 26px 2px; transform: rotate(-2deg); }}
"""
corps = "\n".join("      " + h for h in HTML)
calques = "\n".join("        " + c for c in CALQUES)
audios = [f'      <audio id="musique" src="assets/music/mix-claude.mp3" data-start="0" data-duration="{FIN}" data-volume="1" data-track-index="20"></audio>']
pistes = {}
for n, (d0, f, v, note, dd) in enumerate(sorted(SONS), start=1):
    p = 30
    while pistes.get(p, -1) > d0 - 0.01:
        p += 1
    pistes[p] = d0 + dd
    audios.append(f'      <audio id="sfx-{n:03d}" src="assets/sfx/{f}.mp3" data-start="{d0}" data-duration="{dd}" data-volume="{v}" data-track-index="{p}"></audio><!-- {note} -->')
page = f"""<!doctype html>
<html lang="fr" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="1080" data-height="1920">
      <div id="cadre">
{corps}
        <div id="voile"></div>
        <div id="calques">
{calques}
        </div>
      </div>
      <div id="titre" class="clip" data-layout-allow-overlap data-start="0" data-duration="{FIN}" data-track-index="0"><b>TOUS LES MODÈLES <i>CLAUDE</i></b></div>
{chr(10).join(audios)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(JS)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ICI / "index.html").write_text(page, encoding="utf-8")
print(f"{len([h for h in HTML if h.startswith('<video')])} vidéos, {len(SONS)} bruitages, durée {FIN} s, drop à {DROP} s")
