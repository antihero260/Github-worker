#!/usr/bin/env python3
"""Aftermovie de la conférence JE-FPA du 14 novembre 2026 (« Du CV au "Vous êtes retenu(e)" », avec Yako Africa).
v2 : sans voix, musique Mixkit « Thunder » (hip-hop cinématique, 96 BPM), montage cinéma : vrais ralentis, zooms, coupes sur chaque temps.
(v1 : « Motivating Mornings », refusée.)
Usage : python3 tools/construire.py H   (1920×1080)   |   python3 tools/construire.py V   (1080×1920)
Écrit index.html (à rendre ensuite). Couleurs JE-FPA (bleu #1f4bff, encre #05070d, police Manrope), accents Yako (vert, jaune) pour le partenaire."""
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
MODE = (sys.argv[1] if len(sys.argv) > 1 else "H").upper()
W, H = (1920, 1080) if MODE == "H" else (1080, 1920)
V = MODE == "V"
FIN = 75.6
BLEU, ENCRE, VERT, JAUNE = "#1f4bff", "#05070d", "#0b6b3a", "#FFC000"


def B(k):
    return round(0.43 + 0.4878 * k, 3)


def r(x):
    return round(x, 3)


HTML, JS = [], []
j = JS.append
NV = [0]


def plan(src, t0, t1, zoom=(1.12, 1.0), depart=0.0, flou=False):
    """un plan (vidéo ou photo) ; en vertical : cadre 16:9 au centre + même image floutée derrière"""
    NV[0] += 1
    i = f"p{NV[0]}"
    d = r(t1 - t0 + 0.04)
    if src.endswith(".jpg"):
        media = lambda c: f'<img class="{c}" src="assets/plans/{src}" alt="" />'
    else:
        media = lambda c: (f'<video id="{i}-{c}" class="clip {c}" src="assets/plans/{src}" data-start="{r(t0)}" data-duration="{d}" '
                           f'data-media-start="{depart}" data-track-index="{2 + NV[0] % 6}" muted playsinline></video>')
    if V:
        HTML.append(f'<div id="{i}" class="plan" style="opacity: 0">{media("fondflou")}<div class="cadre">{media("net")}</div></div>')
        cible = f"#{i} .cadre"
    else:
        HTML.append(f'<div id="{i}" class="plan" style="opacity: 0">{media("plein" + (" floute" if flou else ""))}</div>')
        cible = f"#{i} .plein"
    j(f'tl.set("#{i}", {{ opacity: 1 }}, {r(t0)});')
    j(f'tl.fromTo("{cible}", {{ scale: {zoom[0]} }}, {{ scale: {zoom[1]}, duration: {r(t1 - t0)}, ease: "power2.out", immediateRender: false }}, {r(t0)});')
    j(f'tl.set("#{i}", {{ opacity: 0 }}, {r(t1)});')
    return i


def flash(t, op=0.8, coul="#fff"):
    i = f"fl{len(HTML)}"
    HTML.append(f'<div id="{i}" class="flash" style="background: {coul}"></div>')
    j(f'tl.fromTo("#{i}", {{ opacity: {op} }}, {{ opacity: 0, duration: 0.25, immediateRender: false }}, {r(t)});')


def texte(html, t0, t1, cls="", style="", monte=40, d=0.45):
    i = f"tx{len(HTML)}"
    HTML.append(f'<div id="{i}" class="txt {cls}" style="opacity: 0; {style}">{html}</div>')
    j(f'tl.fromTo("#{i}", {{ opacity: 0, y: {monte} }}, {{ opacity: 1, y: 0, duration: {d}, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    j(f'tl.to("#{i}", {{ opacity: 0, y: -20, duration: 0.25, ease: "power2.in" }}, {r(t1 - 0.25)});')
    return i


def mots(phrase, t0, t1, cls="", style="", pas=0.07):
    """titre qui apparaît mot par mot"""
    i = f"mt{len(HTML)}"
    spans = " ".join(f'<span id="{i}-{k}" style="display: inline-block; opacity: 0">{m}</span>' for k, m in enumerate(phrase.split(" ")))
    HTML.append(f'<div id="{i}" class="txt {cls}" style="{style}">{spans}</div>')
    for k in range(len(phrase.split(" "))):
        j(f'tl.fromTo("#{i}-{k}", {{ opacity: 0, y: 50, rotationX: -60 }}, {{ opacity: 1, y: 0, rotationX: 0, duration: 0.4, ease: "back.out(1.6)", immediateRender: false }}, {r(t0 + pas * k)});')
    j(f'tl.to("#{i}", {{ opacity: 0, duration: 0.25 }}, {r(t1 - 0.25)});')


# ============================================================ v2 : montage cinéma sur « Thunder » (96 BPM : un temps = 0,625 s, drop à 20,0 s,
#   cassure 58,1–60,6 s, 2e drop à 60,6 s) : ouverture en vrais ralentis avec bandes cinéma, coupes sur chaque temps, zooms qui claquent,
#   secousses, passages normal → ralenti, image presque figée sur la cassure.
def punch(cible, t, s=1.32):
    j(f'tl.fromTo("{cible}", {{ scale: {s} }}, {{ scale: 1.04, duration: 0.24, ease: "power3.out", immediateRender: false }}, {r(t)});')


def secousse(cible, t, a=16):
    j(f'tl.fromTo("{cible}", {{ x: -{a} }}, {{ x: {a}, duration: 0.035, repeat: 5, yoyo: true, ease: "none", immediateRender: false }}, {r(t)});')
    j(f'tl.set("{cible}", {{ x: 0 }}, {r(t + 0.22)});')


def flou_entree(cible, t):
    j(f'tl.fromTo("{cible}", {{ filter: "blur(14px)" }}, {{ filter: "blur(0px)", duration: 0.16, ease: "power2.out", immediateRender: false }}, {r(t)});')


def coupe(src, t0, t1, effet="punch", zoom=(1.12, 1.0), depart=0.0):
    i = plan(src, t0, t1, zoom, depart=depart)
    cible = f"#{i} .net" if V else f"#{i}"  # le zoom qui claque sur un autre élément que la lente dérive du plan
    if effet in ("punch", "punch+secousse"):
        punch(cible, t0)
    if effet in ("secousse", "punch+secousse"):
        secousse(f"#{i}", t0 + 0.02)
    flou_entree(cible, t0)
    return i


P = 0.625
def Bt(k):
    return round(P * k, 3)


# bandes cinéma (horizontal) pendant l'ouverture, qui s'ouvrent sur le drop
if not V:
    HTML.append('<div id="bande-h" class="bande" style="top: 0"></div><div id="bande-b" class="bande" style="bottom: 0"></div>')
    j(f'tl.to("#bande-h, #bande-b", {{ height: 0, duration: 0.3, ease: "power3.in" }}, {r(Bt(32) - 0.05)});')
    j(f'tl.to("#bande-h, #bande-b", {{ height: 110, duration: 0.5, ease: "power3.out" }}, {r(58.125)});')
    j(f'tl.to("#bande-h, #bande-b", {{ height: 0, duration: 0.25, ease: "power3.in" }}, {r(60.625 - 0.05)});')

# ---- OUVERTURE (0 → 20 s) : logo, titre, ralentis
HTML.append('<div id="s1" class="fond-marque"></div>')
j(f'tl.to("#s1", {{ opacity: 0, duration: 0.4 }}, {r(Bt(4) - 0.2)});')
HTML.append('<img id="logo1" class="logo-centre" src="assets/img/logo-recadre.png" alt="" style="opacity: 0" />')
j('tl.fromTo("#logo1", { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: 1.6, ease: "power2.out", immediateRender: false }, 0.2);')
j(f'tl.to("#logo1", {{ opacity: 0, scale: 0.92, duration: 0.4 }}, {r(Bt(4) - 0.3)});')
texte("CONFÉRENCE JE-FPA 2026", Bt(2), Bt(4), "t-ouv petit", "top: 66%;" if not V else "top: 58%;")
coupe("lent-simulation-1.mp4", Bt(4), Bt(12), "aucun", (1.08, 1.0))
HTML.append('<div id="voile2" class="voile"></div>')
j(f'tl.set("#voile2", {{ opacity: 1 }}, {Bt(4)}); tl.set("#voile2", {{ opacity: 0 }}, {Bt(16)});')
mots("Du CV au « Vous êtes retenu(e) »", Bt(5), Bt(12), "t-titre", "top: 36%;" if not V else "top: 18%;", 0.12)
texte("Maîtriser l’entretien", Bt(8), Bt(12), "t-sous", "top: 55%;" if not V else "top: 29%;")
coupe("lent-intervenante.mp4", Bt(12), Bt(16), "aucun", (1.12, 1.0))
texte('<b>Samedi 14 novembre 2026</b><br>Université Félix Houphouët-Boigny', Bt(12) + 0.2, Bt(16), "t-date", "top: 60%;" if not V else "top: 66%;")
HTML.append(f'<div id="s3" class="fond-blanc" style="opacity: 0"><img id="mains" class="mains" src="assets/img/mains-yako.png" alt="" />'
            f'<div class="partenaire"><span>En partenariat avec</span><img id="logoyako" src="assets/img/logo-yako.png" alt="" /></div></div>')
j(f'tl.set("#s3", {{ opacity: 1 }}, {Bt(16)}); tl.set("#s3", {{ opacity: 0 }}, {Bt(22)});')
j(f'tl.fromTo("#mains", {{ x: -900 }}, {{ x: 0, duration: 1.4, ease: "power3.out", immediateRender: false }}, {Bt(16)});')
j(f'tl.fromTo("#logoyako", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.8, ease: "back.out(1.8)", immediateRender: false }}, {Bt(18)});')
flash(Bt(16), 0.5)
# montée : les coupes accélèrent jusqu'au drop
MONTEE = [("lent-public-micro.mp4", 22, 26), ("lent-panel-table.mp4", 26, 28), ("lent-question-duo.mp4", 28, 30),
          ("presentation-ek.mp4", 30, 31), ("debout-public.mp4", 31, 31.5), ("question-micro.mp4", 31.5, 32)]
for src_, a, b in MONTEE:
    coupe(src_, Bt(a), Bt(b), "punch" if a >= 30 else "aucun", (1.1, 1.0), depart=0.5)

# ---- DROP 1 (20 → 37,5 s) : une coupe par temps, zooms qui claquent, secousses, passages normal → ralenti
flash(Bt(32), 1.0)
DROP = [("public-micro.mp4", 1, "punch+secousse"), ("panel-table.mp4", 1, "punch"), ("simulation-2.mp4", 1, "punch"), ("intervenante-face.mp4", 1, "punch"),
        ("presentation-ek.mp4", 1, "punch+secousse"), ("lent-presentation-ek.mp4", 3, "aucun"),
        ("question-duo.mp4", 1, "punch"), ("public-micro-2.mp4", 1, "punch"), ("groupe-2.jpg", 1, "punch+secousse"), ("debout-public.mp4", 1, "punch"),
        ("simulation-1.mp4", 1, "punch"), ("lent-simulation-1.mp4", 3, "aucun"),
        ("panel-large.mp4", 1, "punch"), ("question-micro.mp4", 1, "punch+secousse"), ("salle-photo.jpg", 1, "punch"), ("intervenante.mp4", 1, "punch"),
        ("panel-photo.jpg", 1, "punch"), ("lent-public-micro.mp4", 4, "aucun")]
k = 32
for src_, n, effet in DROP:
    coupe(src_, Bt(k), Bt(k + n), effet, (1.08, 1.0) if src_.startswith("lent") else (1.12, 1.02), depart=0.3)
    if effet != "aucun" and k > 32:
        flash(Bt(k), 0.25)
    k += n
# k = 60

# ---- PANÉLISTES (37,5 → 45 s)
PAN = [("coralie-guei.png", "Coralie GUEÏ", "Directrice des Ressources<br>et de la Transformation"),
       ("emmanuel-kone.png", "Emmanuel KONE", "Responsable des<br>Ressources Humaines"),
       ("oguyr-gagne.png", "O’guyr GAGNE", "Chargé de projet RH")]
coupe("lent-panel-table.mp4", Bt(60), Bt(68), "aucun", (1.1, 1.0))
coupe("panel-large.mp4", Bt(68), Bt(72), "aucun", (1.1, 1.0))
HTML.append('<div id="voile5" class="voile fort"></div>')
j(f'tl.set("#voile5", {{ opacity: 1 }}, {Bt(60)}); tl.set("#voile5", {{ opacity: 0 }}, {Bt(72)});')
flash(Bt(60), 0.5)
texte("NOS PANÉLISTES", Bt(60), Bt(72), "t-etiq", "top: 11%;" if not V else "top: 8%;")
for kk, (img, nom, role) in enumerate(PAN):
    t0, t1 = Bt(60 + 4 * kk), Bt(64 + 4 * kk)
    i = f"pan{kk}"
    HTML.append(f'<div id="{i}" class="carte-pan" style="opacity: 0"><img src="assets/img/{img}" alt="" /><div><b>{nom}</b><span>{role}</span>'
                f'<em><img src="assets/img/logo-yako.png" alt="" /></em></div></div>')
    j(f'tl.fromTo("#{i}", {{ opacity: 0, scale: 1.25 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    j(f'tl.to("#{i}", {{ scale: 1.04, duration: {r(t1 - t0 - 0.5)}, ease: "none" }}, {r(t0 + 0.3)});')
    j(f'tl.to("#{i}", {{ opacity: 0, x: -160, duration: 0.25, ease: "power2.in" }}, {r(t1 - 0.25)});')

# ---- TEMPS FORTS (45 → 58,1 s) : chaque moment = 1 temps normal puis ralenti (passage normal → ralenti), étiquette
MOM = [("01", "Vrai ou faux des idées reçues", "debout-public.mp4", "lent-debout-public.mp4"),
       ("02", "Du CV à l’entretien", "presentation-ek.mp4", "lent-presentation-ek.mp4"),
       ("03", "Simulation d’entretien", "simulation-2.mp4", "lent-simulation-2.mp4"),
       ("04", "Questions du public", "question-micro.mp4", "lent-question-micro.mp4")]
for kk, (num, titre, a_, b_) in enumerate(MOM):
    t0 = Bt(72 + 5 * kk)
    coupe(a_, t0, Bt(73 + 5 * kk), "punch+secousse", (1.12, 1.02), depart=0.6)
    coupe(b_, Bt(73 + 5 * kk), Bt(77 + 5 * kk), "aucun", (1.0, 1.12), depart=0.4)
    flash(t0, 0.45)
    texte(f'<i>{num}</i>{titre}', t0 + 0.05, Bt(77 + 5 * kk), "t-moment")
coupe("lent-groupe.mp4", Bt(92), Bt(93), "punch", (1.1, 1.0))
# ---- CASSURE (58,1 → 60,6 s) : presque figé, zoom lent, message
plan("panel-photo.jpg", 58.125, 60.625, (1.05, 1.25))
HTML.append('<div id="voile7" class="voile fort"></div>')
j('tl.set("#voile7", { opacity: 1 }, 58.125); tl.set("#voile7", { opacity: 0 }, 60.625);')
mots("Un CV n’est pas une biographie.", 58.2, 60.625, "t-message", "top: 40%;" if not V else "top: 20%;", 0.12)

# ---- DROP 2 (60,6 → 73,1 s) : rafale finale, deuxième message, MERCI
def B2(k):
    return round(60.625 + P * k, 3)


flash(B2(0), 1.0)
FIN2 = [("intervenante-face.mp4", "punch+secousse"), ("public-micro-2.mp4", "punch"), ("simulation-1.mp4", "punch"), ("question-duo.mp4", "punch+secousse"),
        ("panel-table.mp4", "punch"), ("groupe-3.jpg", "punch"), ("micro-photo.jpg", "punch+secousse"), ("intervenante.mp4", "punch"),
        ("debout-public.mp4", "punch"), ("presentation-ek.mp4", "punch+secousse"), ("question-micro.mp4", "punch"), ("panel-large.mp4", "punch")]
for kk, (src_, effet) in enumerate(FIN2):
    coupe(src_, B2(kk), B2(kk + 1), effet, (1.12, 1.02), depart=1.2)
    if kk:
        flash(B2(kk), 0.22)
HTML.append('<div id="voile8b" class="voile fort"></div>')
j(f'tl.set("#voile8b", {{ opacity: 1 }}, {B2(0)}); tl.set("#voile8b", {{ opacity: 0 }}, {B2(8)});')
mots("C’est l’outil qui vous ouvre la porte de l’entretien.", B2(0) + 0.1, B2(8), "t-message bleu-clair", "top: 36%;" if not V else "top: 11%;", 0.09)
coupe("lent-groupe.mp4", B2(12), B2(16), "punch", (1.05, 1.0))
plan("groupe-1.jpg", B2(16), B2(20), (1.02, 1.15))
HTML.append('<div id="voile8" class="voile"></div>')
j(f'tl.set("#voile8", {{ opacity: 1 }}, {B2(12)}); tl.set("#voile8", {{ opacity: 0 }}, {B2(20)});')
flash(B2(12), 0.7)
mots("MERCI", B2(12) + 0.1, B2(20), "t-merci", "top: 30%;" if not V else "top: 14%;", 0.0)
texte("à nos panélistes, à YAKO AFRICA<br>et à tous les participants", B2(13), B2(20), "t-sous", "top: 50%;" if not V else "top: 25%;")
# ---- FIN (73,1 → 75,6 s)
HTML.append('<div id="s9" class="fond-marque" style="opacity: 0"></div>')
j(f'tl.fromTo("#s9", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, immediateRender: false }}, {B2(20)});')
HTML.append('<img id="logo2" class="logo-centre" src="assets/img/logo-recadre.png" alt="" style="opacity: 0" />')
j(f'tl.fromTo("#logo2", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "power3.out", immediateRender: false }}, {B2(20) + 0.05});')
texte("Junior Entreprise de la Filière Professionnalisée Actuariat", B2(21), FIN + 0.3, "t-fin", "top: 66%;" if not V else "top: 60%;")
HTML.append('<div id="noir" class="flash" style="background: #000"></div>')
j(f'tl.fromTo("#noir", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.8, immediateRender: false }}, {r(FIN - 0.8)});')

# ============================================================ vertical : en-tête et pied pendant les plans (sinon le haut et le bas restent vides)
if V:
    for a, b in ((20.0, 37.5), (45.0, 58.125)):  # seulement pendant la rafale et les temps forts (pas sur les panélistes ni les messages)
        e = f"entete{int(a)}"
        HTML.append(f'<div id="{e}" class="entete" style="opacity: 0"><img src="assets/img/logo-recadre.png" alt="" /><span>Conférence · 14 novembre 2026</span></div>')
        j(f'tl.fromTo("#{e}", {{ opacity: 0, y: -40 }}, {{ opacity: 1, y: 0, duration: 0.4, immediateRender: false }}, {a});')
        j(f'tl.to("#{e}", {{ opacity: 0, duration: 0.25 }}, {r(b - 0.25)});')
        i = f"pied{int(a)}"
        HTML.append(f'<div id="{i}" class="pied" style="opacity: 0">Du CV au « Vous êtes retenu(e) »</div>')
        j(f'tl.fromTo("#{i}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, immediateRender: false }}, {a});')
        j(f'tl.to("#{i}", {{ opacity: 0, duration: 0.25 }}, {r(b - 0.25)});')

CSS = f"""
      @font-face {{ font-family: "Manrope"; src: url("assets/fonts/manrope-latin.woff2") format("woff2"); font-weight: 200 800; unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215; }}
      @font-face {{ font-family: "Manrope"; src: url("assets/fonts/manrope-latin-ext.woff2") format("woff2"); font-weight: 200 800; unicode-range: U+0100-024F, U+0259, U+1E00-1EFF, U+20A0-20AB, U+20AD-20CF, U+2C60-2C7F, U+A720-A7FF; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {ENCRE}; font-family: "Manrope", sans-serif; }}
      .plan {{ position: absolute; inset: 0; overflow: hidden; background: {ENCRE}; }}
      .plein {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .floute {{ filter: blur(6px) brightness(0.8); transform: scale(1.06); }}
      .fondflou {{ position: absolute; inset: -40px; width: calc(100% + 80px); height: calc(100% + 80px); object-fit: cover; filter: blur(34px) brightness(0.45) saturate(1.2); }}
      .cadre {{ position: absolute; left: 0; top: {(H - 608) // 2 - 40}px; width: 1080px; height: 608px; overflow: hidden; box-shadow: 0 40px 120px rgba(0,0,0,0.6); }}
      .cadre .net {{ width: 100%; height: 100%; object-fit: cover; }}
      .voile {{ position: absolute; inset: 0; opacity: 0; background: linear-gradient(180deg, rgba(5,7,13,0.55), rgba(5,7,13,0.25) 45%, rgba(5,7,13,0.7)); }}
      .voile.fort {{ background: rgba(5,7,13,0.62); }}
      .flash {{ position: absolute; inset: 0; opacity: 0; pointer-events: none; z-index: 40; }}
      .fond-marque {{ position: absolute; inset: 0; background: radial-gradient(ellipse 70% 60% at 50% 45%, #14205a 0%, {ENCRE} 70%); z-index: 20; }}
      .fond-blanc {{ position: absolute; inset: 0; background: #fff; overflow: hidden; z-index: 5; }}
      .mains {{ position: absolute; left: {-300 if not V else -900}px; top: {140 if not V else 260}px; width: {1300 if not V else 2100}px; }}
      .partenaire {{ position: absolute; {"right: 120px; top: 560px; width: 620px;" if not V else "left: 0; right: 0; top: 1150px;"} text-align: center; }}
      .partenaire span {{ display: block; font-size: {40 if not V else 50}px; font-weight: 700; color: {VERT}; letter-spacing: 1px; margin-bottom: 20px; }}
      .partenaire img {{ width: {440 if not V else 560}px; }}
      .logo-centre {{ position: absolute; left: 50%; top: {"38%" if not V else "38%"}; width: {640 if not V else 720}px; margin-left: -{320 if not V else 360}px; margin-top: -{130 if not V else 147}px; z-index: 22;
        box-shadow: 0 0 80px rgba(31,75,255,0.55); border-radius: 26px; }}
      .ligne {{ position: absolute; left: 50%; top: {"80%" if not V else "66%"}; transform: scaleX(0); width: {600 if not V else 520}px; margin-left: -{300 if not V else 260}px; height: 6px; border-radius: 3px; background: {BLEU}; z-index: 22; transform-origin: 50% 50%; }}
      .txt {{ position: absolute; left: 0; right: 0; text-align: center; color: #fff; z-index: 25; padding: 0 {90 if not V else 70}px; }}
      .t-ouv {{ font-size: {110 if not V else 104}px; font-weight: 800; letter-spacing: 6px; line-height: 1; perspective: 600px; }}
      .bleu {{ color: #4f74ff; }}
      .t-titre {{ font-size: {104 if not V else 92}px; font-weight: 800; line-height: 1.08; text-shadow: 0 10px 50px rgba(0,0,0,0.6); perspective: 600px; }}
      .t-sous {{ font-size: {54 if not V else 52}px; font-weight: 600; color: #dfe6ff; text-shadow: 0 6px 30px rgba(0,0,0,0.7); }}
      .t-date {{ font-size: {38 if not V else 42}px; font-weight: 500; color: #fff; line-height: 1.4; }}
      .t-date b {{ display: inline-block; font-weight: 800; color: {ENCRE}; background: #fff; padding: 4px 22px; border-radius: 10px; margin-bottom: 10px; }}
      .t-etiq {{ font-size: {40 if not V else 46}px; font-weight: 800; letter-spacing: 8px; color: {JAUNE}; }}
      .carte-pan {{ position: absolute; z-index: 26; display: flex; {"left: 260px; top: 250px; width: 1400px; align-items: center; gap: 60px;" if not V else "left: 90px; top: 380px; width: 900px; flex-direction: column; align-items: center; gap: 40px; text-align: center;"} }}
      .carte-pan > img {{ width: {420 if not V else 520}px; height: {540 if not V else 660}px; object-fit: cover; border-radius: 28px; border: 8px solid #fff; box-shadow: 0 30px 90px rgba(0,0,0,0.6); }}
      .carte-pan b {{ display: block; font-size: {84 if not V else 80}px; font-weight: 800; color: #fff; line-height: 1.05; }}
      .carte-pan span {{ display: block; margin-top: 18px; font-size: {44 if not V else 44}px; font-weight: 600; color: #dfe6ff; line-height: 1.25; }}
      .carte-pan em {{ display: inline-block; margin-top: 30px; background: #fff; border-radius: 16px; padding: 12px 24px; border-left: 10px solid {JAUNE}; }}
      .carte-pan em img {{ height: {70 if not V else 80}px; display: block; }}
      .t-moment {{ {"left: 70px; right: auto; bottom: 90px; text-align: left;" if not V else "top: 1300px; left: 0; right: 0;"} font-size: {64 if not V else 62}px; font-weight: 800; padding: 0; }}
      .t-moment i {{ font-style: normal; display: inline-block; margin-right: 26px; padding: 6px 22px; border-radius: 14px; background: {BLEU}; color: #fff; }}
      .t-message {{ font-size: {96 if not V else 90}px; font-weight: 800; line-height: 1.1; text-shadow: 0 10px 50px rgba(0,0,0,0.7); perspective: 600px; }}
      .bleu-clair {{ color: #a9bcff; }}
      .t-merci {{ font-size: {200 if not V else 190}px; font-weight: 800; letter-spacing: 12px; text-shadow: 0 14px 60px rgba(0,0,0,0.6); perspective: 600px; }}
      .entete {{ position: absolute; left: 0; right: 0; top: 120px; text-align: center; z-index: 30; }}
      .entete img {{ width: 380px; border-radius: 18px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }}
      .entete span {{ display: block; margin-top: 22px; font-size: 40px; font-weight: 700; color: #fff; letter-spacing: 1px; }}
      .pied {{ position: absolute; left: 0; right: 0; top: 1560px; text-align: center; z-index: 30; font-size: 46px; font-weight: 800; color: #dfe6ff; padding: 0 60px; }}
      .bande {{ position: absolute; left: 0; right: 0; height: 110px; background: #000; z-index: 35; }}
      .t-ouv.petit {{ font-size: {64 if not V else 64}px; letter-spacing: 10px; }}
      .t-fin {{ font-size: {38 if not V else 40}px; font-weight: 600; color: #c9d3ff; }}
"""
if V:  # en vertical, les textes des temps forts sous le cadre et les messages au-dessus
    pass
page = f"""<!doctype html>
<html lang="fr" data-resolution="{'landscape' if not V else 'portrait'}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="{W}" data-height="{H}">
{chr(10).join("      " + h for h in HTML)}
      <audio id="musique" src="assets/music/aftermovie2.mp3" data-start="0" data-duration="{FIN}" data-volume="1" data-track-index="20"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join("      " + l for l in JS)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ICI / ("index.html" if not V else "vertical/index.html")).write_text(page, encoding="utf-8")
print(MODE, W, H, "durée", FIN, "s,", NV[0], "plans")
