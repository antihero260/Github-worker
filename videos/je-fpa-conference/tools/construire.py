#!/usr/bin/env python3
"""Aftermovie de la conférence JE-FPA du 14 novembre 2026 (« Du CV au "Vous êtes retenu(e)" », avec Yako Africa).
v3 : très dynamique (55,6 s), musique Mixkit « Thunder » prise à 15 s, une coupe par temps, aucun plan répété, deux ralentis, les trois panélistes ensemble.
(v1 : « Motivating Mornings », refusée ; v2 : trop de ralentis, panélistes un par un, plans répétés.)
Usage : python3 tools/construire.py H   (1920×1080)   |   python3 tools/construire.py V   (1080×1920)
Écrit index.html (à rendre ensuite). Couleurs JE-FPA (bleu #1f4bff, encre #05070d, police Manrope), accents Yako (vert, jaune) pour le partenaire."""
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
MODE = (sys.argv[1] if len(sys.argv) > 1 else "H").upper()
W, H = (1920, 1080) if MODE == "H" else (1080, 1920)
V = MODE == "V"
FIN = 55.6
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


# ============================================================ v3 : TRÈS DYNAMIQUE, plus court (55,6 s). Musique « Thunder » prise à 15,0 s :
#   drop à 5,0 s ; cassure 43,1–45,6 s ; 2e drop 45,6 s. Une coupe par temps (0,625 s), demi-temps dans les montées, zooms qui claquent,
#   secousses, flous de mouvement, éclairs. AUCUN plan ni aucune image utilisé deux fois ; deux ralentis seulement.
import json as _json
POOL = _json.loads((ICI / "assets/plans/segments.json").read_text())
PHOTOS = ["panel-photo.jpg", "salle-photo.jpg", "micro-photo.jpg", "intervenante-photo.jpg", "panel-large-photo.jpg", "ek-photo.jpg", "salle-2-photo.jpg"]
UTILISES = set()


def prochain(photo_tous=5, lettres=None):
    """le plan suivant de la banque (une photo de temps en temps) ; jamais deux fois le même.
    lettres : ne prendre que dans ces sources (pour que l'image corresponde à l'étiquette du temps fort)"""
    if lettres:
        src_ = next(n for n in POOL if n[2] in lettres)
        POOL.remove(src_)
        assert src_ not in UTILISES, src_
        UTILISES.add(src_)
        return src_
    prochain.n = getattr(prochain, "n", 0) + 1
    if PHOTOS and prochain.n % photo_tous == 0:
        src_ = PHOTOS.pop(0)
    else:
        src_ = POOL.pop(0)
    assert src_ not in UTILISES, src_
    UTILISES.add(src_)
    return src_


def punch(cible, t, s=1.35):
    j(f'tl.fromTo("{cible}", {{ scale: {s} }}, {{ scale: 1.04, duration: 0.22, ease: "power3.out", immediateRender: false }}, {r(t)});')


def secousse(cible, t, a=18):
    j(f'tl.fromTo("{cible}", {{ x: -{a} }}, {{ x: {a}, duration: 0.03, repeat: 5, yoyo: true, ease: "none", immediateRender: false }}, {r(t)});')
    j(f'tl.set("{cible}", {{ x: 0 }}, {r(t + 0.2)});')


def glisse(cible, t, sens):
    """entrée en filé (mouvement + flou) depuis un côté"""
    j(f'tl.fromTo("{cible}", {{ x: {sens * 260}, filter: "blur(18px)" }}, {{ x: 0, filter: "blur(0px)", duration: 0.18, ease: "power3.out", immediateRender: false }}, {r(t)});')


def coupe(src_, t0, t1, effet="punch", zoom=(1.14, 1.02), depart=0.1):
    i = plan(src_, t0, t1, zoom, depart=depart)
    cible = f"#{i} .net" if V else f"#{i}"
    if "punch" in effet:
        punch(cible, t0)
    if "glisse" in effet:
        glisse(cible, t0, 1 if (len(HTML) % 2) else -1)
    if "secousse" in effet:
        secousse(f"#{i}", t0 + 0.02)
    return i


T0, P = 5.0, 0.625
def Bv(k):
    return round(T0 + P * k, 3)


EFFETS = ["punch", "glisse", "punch+secousse", "punch", "glisse", "punch"]
def rafale(k0, pas, n, flash_tous=4):
    """n coupes de `pas` temps chacune à partir du temps k0 ; renvoie le temps suivant"""
    k = k0
    for m in range(n):
        coupe(prochain(), Bv(k), Bv(k + pas), EFFETS[m % len(EFFETS)])
        if m % flash_tous == 0:
            flash(Bv(k), 0.35)
        k += pas
    return k


# les temps forts piochent dans les vidéos qui les montrent (lettre de la source, voir tools/preparer-segments.py)
MOM = [("01", "Vrai ou faux des idées reçues", "BCK"), ("02", "Du CV à l’entretien", "OQPJE"), ("03", "Simulation d’entretien", "FM"),
       ("04", "Questions du public", "CAL")]
# on les réserve AVANT la rafale d'ouverture pour qu'il en reste
RESERVE = {}
for num_, _, lt in MOM:
    RESERVE[num_] = [prochain(lettres=lt) for _ in range(4 if num_ != "03" else 3)]
k = 26

# ---- OUVERTURE (0 → 5 s) : logo + titre, puis 4 coupes qui accélèrent jusqu'au drop
HTML.append('<div id="s1" class="fond-marque"></div>')
j('tl.to("#s1", { opacity: 0, duration: 0.15 }, 2.45);')
HTML.append('<img id="logo1" class="logo-centre" src="assets/img/logo-recadre.png" alt="" style="opacity: 0" />')
j('tl.fromTo("#logo1", { opacity: 0, scale: 1.4 }, { opacity: 1, scale: 1, duration: 0.7, ease: "power3.out", immediateRender: false }, 0.1);')
j('tl.to("#logo1", { opacity: 0, scale: 0.9, duration: 0.2 }, 2.3);')
texte("CONFÉRENCE JE-FPA 2026", 0.6, 2.5, "t-ouv petit", "top: 64%;" if not V else "top: 56%;")
k = -4
for pas in (2, 1, 0.5, 0.5):
    coupe(prochain(), Bv(k), Bv(k + pas), "punch")
    k += pas
mots("Du CV au « Vous êtes retenu(e) »", Bv(-4) + 0.05, T0, "t-titre", "top: 38%;" if not V else "top: 18%;", 0.06)
HTML.append('<div id="voile1" class="voile"></div>')
j(f'tl.set("#voile1", {{ opacity: 1 }}, {Bv(-4)}); tl.set("#voile1", {{ opacity: 0 }}, {T0});')

# ---- DROP 1 (5 → 15 s) : 16 coupes sur les temps
flash(T0, 1.0)
k = rafale(0, 1, 16)

# ---- PARTENAIRE + DATE (15 → 17,5 s)
HTML.append(f'<div id="s3" class="fond-blanc" style="opacity: 0"><img id="mains" class="mains" src="assets/img/mains-yako.png" alt="" />'
            f'<div class="partenaire"><span>En partenariat avec</span><img id="logoyako" src="assets/img/logo-yako.png" alt="" />'
            f'<em>Samedi 14 novembre 2026 · Université Félix Houphouët-Boigny</em></div></div>')
j(f'tl.set("#s3", {{ opacity: 1 }}, {Bv(16)}); tl.set("#s3", {{ opacity: 0 }}, {Bv(20)});')
j(f'tl.fromTo("#mains", {{ x: -1100 }}, {{ x: 0, duration: 0.45, ease: "power4.out", immediateRender: false }}, {Bv(16)});')
j(f'tl.fromTo("#logoyako", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "power4.in", immediateRender: false }}, {Bv(17)});')
flash(Bv(16), 0.6)

# ---- PANÉLISTES : les trois ensemble (17,5 → 21,25 s)
PAN = [("coralie-guei.png", "Coralie GUEÏ", "Directrice des Ressources et de la Transformation"),
       ("emmanuel-kone.png", "Emmanuel KONE", "Responsable des Ressources Humaines"),
       ("oguyr-gagne.png", "O’guyr GAGNE", "Chargé de projet RH")]
HTML.append('<div id="s5" class="fond-marque" style="opacity: 0; z-index: 6"></div>')
j(f'tl.set("#s5", {{ opacity: 1 }}, {Bv(20)}); tl.set("#s5", {{ opacity: 0 }}, {Bv(26)});')
flash(Bv(20), 0.6)
texte("NOS PANÉLISTES · <b>YAKO AFRICA</b>", Bv(20), Bv(26), "t-etiq", "top: 8%;" if not V else "top: 7%;")
HTML.append('<div id="trio" class="trio">' + "".join(
    f'<div id="tr{kk}" class="tr-carte" style="opacity: 0"><img src="assets/img/{img}" alt="" /><b>{nom}</b><span>{role}</span></div>'
    for kk, (img, nom, role) in enumerate(PAN)) + '</div>')
for kk in range(3):
    j(f'tl.fromTo("#tr{kk}", {{ opacity: 0, y: 120, scale: 0.8 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.7)", immediateRender: false }}, {Bv(20 + kk * 0.5)});')
    j(f'tl.to("#tr{kk}", {{ opacity: 0, y: -60, duration: 0.2 }}, {r(Bv(26) - 0.2)});')
j(f'tl.fromTo("#trio", {{ scale: 1 }}, {{ scale: 1.06, duration: {r(Bv(26) - Bv(20))}, ease: "none", immediateRender: false }}, {Bv(20)});')

# ---- TEMPS FORTS (21,25 → 33,75 s) : 4 × 5 temps, coupes 1-1-1-2 ; un seul ralenti (simulation)
k = 26
for kk, (num, titre, _) in enumerate(MOM):
    t0 = Bv(k)
    res = RESERVE[num]
    for pas in (1, 1, 1):
        coupe(res.pop(0), Bv(k), Bv(k + pas), "punch+secousse" if k == 26 + 5 * kk else "punch")
        k += pas
    if num == "03":
        coupe("lent-simulation-2.mp4", Bv(k), Bv(k + 2), "glisse", (1.0, 1.14), depart=0.5)
    else:
        coupe(res.pop(0), Bv(k), Bv(k + 2), "glisse", (1.0, 1.12))
    k += 2
    flash(t0, 0.5)
    texte(f'<i>{num}</i>{titre}', t0 + 0.03, Bv(k), "t-moment", monte=60, d=0.25)

# ---- RAFALE (33,75 → 43,1 s) : 11 coupes d'un temps puis 8 demi-temps (montée vers la cassure)
k = rafale(46, 1, 11)
k = rafale(k, 0.5, 8, flash_tous=2)

# ---- CASSURE (43,1 → 45,6 s) : le 2e ralenti + message
coupe("lent-debout-public.mp4", Bv(61), Bv(65), "aucun", (1.04, 1.2), depart=0.4)
HTML.append('<div id="voile7" class="voile fort"></div>')
j(f'tl.set("#voile7", {{ opacity: 1 }}, {Bv(61)}); tl.set("#voile7", {{ opacity: 0 }}, {Bv(65)});')
mots("Un CV n’est pas une biographie.", Bv(61) + 0.05, Bv(65), "t-message", "top: 40%;" if not V else "top: 20%;", 0.1)

# ---- 2e DROP (45,6 → 50,6 s) : 8 coupes + message
flash(Bv(65), 1.0)
rafale(65, 2, 4, flash_tous=1)
HTML.append('<div id="voile8b" class="voile fort"></div>')
j(f'tl.set("#voile8b", {{ opacity: 1 }}, {Bv(65)}); tl.set("#voile8b", {{ opacity: 0 }}, {Bv(73)});')
mots("C’est l’outil qui vous ouvre la porte de l’entretien.", Bv(65) + 0.05, Bv(73), "t-message bleu-clair", "top: 36%;" if not V else "top: 11%;", 0.07)

# ---- MERCI (50,6 → 53,1 s) puis logo (53,1 → 55,6 s)
coupe("groupe-1.jpg", Bv(73), Bv(77), "punch", (1.04, 1.16))
HTML.append('<div id="voile8" class="voile"></div>')
j(f'tl.set("#voile8", {{ opacity: 1 }}, {Bv(73)}); tl.set("#voile8", {{ opacity: 0 }}, {Bv(77)});')
flash(Bv(73), 0.8)
mots("MERCI", Bv(73) + 0.05, Bv(77), "t-merci", "top: 30%;" if not V else "top: 14%;", 0.0)
texte("à nos panélistes, à YAKO AFRICA<br>et à tous les participants", Bv(74), Bv(77), "t-sous", "top: 50%;" if not V else "top: 25%;")
HTML.append('<div id="s9" class="fond-marque" style="opacity: 0"></div>')
j(f'tl.fromTo("#s9", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, {Bv(77)});')
HTML.append('<img id="logo2" class="logo-centre" src="assets/img/logo-recadre.png" alt="" style="opacity: 0" />')
j(f'tl.fromTo("#logo2", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "power3.out", immediateRender: false }}, {Bv(77) + 0.05});')
texte("Junior Entreprise de la Filière Professionnalisée Actuariat", Bv(78), FIN + 0.3, "t-fin", "top: 66%;" if not V else "top: 60%;")
HTML.append('<div id="noir" class="flash" style="background: #000"></div>')
j(f'tl.fromTo("#noir", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.7, immediateRender: false }}, {r(FIN - 0.7)});')
print(len(UTILISES), "plans différents utilisés,", len(POOL), "restants")

# ============================================================ vertical : en-tête et pied pendant les plans (sinon le haut et le bas restent vides)
if V:
    for a, b in ((5.0, 15.0), (21.25, 43.125)):  # seulement pendant la rafale et les temps forts (pas sur les panélistes ni les messages)
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
      .partenaire em {{ display: block; margin-top: 26px; font-style: normal; font-size: {30 if not V else 34}px; font-weight: 700; color: {ENCRE}; }}
      .trio {{ position: absolute; z-index: 26; display: flex; {"left: 120px; right: 120px; top: 250px; gap: 50px; justify-content: center;" if not V else "left: 80px; right: 80px; top: 330px; flex-direction: column; gap: 34px;"} }}
      .tr-carte {{ flex: 1; text-align: center; {"" if not V else "display: grid; grid-template-columns: 300px 1fr; grid-template-rows: auto auto; column-gap: 34px; align-items: center; text-align: left;"} }}
      .tr-carte img {{ width: {440 if not V else 300}px; height: {520 if not V else 360}px; object-fit: cover; border-radius: 26px; border: 7px solid #fff; box-shadow: 0 26px 80px rgba(0,0,0,0.6); {"" if not V else "grid-row: 1 / span 2;"} }}
      .tr-carte b {{ display: block; margin-top: {22 if not V else 0}px; font-size: {52 if not V else 56}px; font-weight: 800; color: #fff; line-height: 1.05; {"" if not V else "align-self: end;"} }}
      .tr-carte span {{ display: block; margin-top: 10px; font-size: {30 if not V else 34}px; font-weight: 600; color: #dfe6ff; line-height: 1.25; {"" if not V else "align-self: start;"} }}
      .t-etiq b {{ color: #fff; }}
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
      <audio id="musique" src="assets/music/aftermovie3.mp3" data-start="0" data-duration="{FIN}" data-volume="1" data-track-index="20"></audio>
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
