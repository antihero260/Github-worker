#!/usr/bin/env python3
"""Aftermovie JE-FPA, version afro sur la musique de la com : montage entièrement repensé (pas une copie de la version « Thunder »).
Musique : assets/music/aftermovie-afro.mp3 = morceau de la com (115 BPM, grille T = 0,0398 + 0,52175 b) recoupé sur les mesures :
temps 16–64 (intro douce + refrain 1), 152–184 (montée du pont + refrain 2), 224–236 (outro, fondu). Durée : 88 temps = 45,9 s.
Style : fond crème, orange et or, grandes lettres condensées (Anton), collage de polaroïds, triptyque, coupes sur le motif 3-3-2.
Plans : tools/preparer-afro.py (a-*), chacun utilisé une seule fois.   Usage : python3 tools/construire-afro.py  →  com/index.html"""
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
W, H = 1920, 1080
P = 0.52175


def T(v):
    """temps (s) du temps musical v de la vidéo"""
    return round(v * P, 3)


def r(x):
    return round(x, 3)


FIN = T(88)
ENCRE, CREME, PAPIER, ORANGE, OR, BLEU, VERT = "#1b1712", "#fff4e0", "#f3e8d6", "#e8772e", "#f2b33d", "#1f4bff", "#0b6b3a"
HTML, JS = [], []
j = JS.append
N = [0]
UTILISES = set()


def uid(p):
    N[0] += 1
    return f"{p}{N[0]}"


def media(src, cls, t0, t1, depart=0.0):
    assert src not in UTILISES, f"plan déjà utilisé : {src}"
    UTILISES.add(src)
    if src.endswith(".jpg") or src.endswith(".png"):
        return f'<img class="{cls}" src="assets/plans/{src}" alt="" />'
    i = uid("v")
    return (f'<video id="{i}" class="clip {cls}" src="assets/plans/{src}" data-start="{r(t0)}" data-duration="{r(t1 - t0 + 0.05)}" '
            f'data-media-start="{depart}" data-track-index="{2 + N[0] % 7}" muted playsinline></video>')


def montrer(i, t0, t1):
    j(f'tl.set("#{i}", {{ opacity: 1 }}, {r(t0)}); tl.set("#{i}", {{ opacity: 0 }}, {r(t1)});')


def papier(t0, t1):
    i = uid("pa")
    HTML.append(f'<div id="{i}" class="papier" style="opacity: 0"></div>')
    montrer(i, t0, t1)


def flash(t, op=0.45, coul="#ffd9a0"):
    i = uid("fl")
    HTML.append(f'<div id="{i}" class="flash" style="background: {coul}"></div>')
    j(f'tl.fromTo("#{i}", {{ opacity: {op} }}, {{ opacity: 0, duration: 0.3, immediateRender: false }}, {r(t)});')


def entree(sel, t, effet, sens=1):
    if effet == "balance":
        j(f'tl.fromTo("{sel}", {{ x: {60 * sens}, rotation: {-1.5 * sens}, scale: 1.12 }}, {{ x: 0, rotation: 0, scale: 1, duration: 0.45, ease: "sine.out", immediateRender: false }}, {r(t)});')
    elif effet == "glisse":
        j(f'tl.fromTo("{sel}", {{ x: {300 * sens}, scale: 1.35, filter: "blur(16px)" }}, {{ x: 0, scale: 1, filter: "blur(0px)", duration: 0.24, ease: "power3.out", immediateRender: false }}, {r(t)});')
    elif effet == "zoom":
        j(f'tl.fromTo("{sel}", {{ scale: 1.3 }}, {{ scale: 1, duration: 0.35, ease: "power3.out", immediateRender: false }}, {r(t)});')


def plein(src, t0, t1, effet="balance", kb=(1.06, 1.15), depart=0.0):
    i = uid("pl")
    HTML.append(f'<div id="{i}" class="plan" style="opacity: 0"><div class="kb">{media(src, "plein", t0, t1, depart)}</div></div>')
    montrer(i, t0, t1)
    j(f'tl.fromTo("#{i} .kb", {{ scale: {kb[0]} }}, {{ scale: {kb[1]}, duration: {r(t1 - t0)}, ease: "none", immediateRender: false }}, {r(t0)});')
    entree(f"#{i}", t0, effet, 1 if N[0] % 2 else -1)
    return i


def demi(src, t0, t1, effet="glisse"):
    """plan sur la moitié gauche de l'écran"""
    i = uid("dm")
    HTML.append(f'<div id="{i}" class="demi" style="opacity: 0"><div class="kb">{media(src, "plein", t0, t1)}</div></div>')
    montrer(i, t0, t1)
    j(f'tl.fromTo("#{i} .kb", {{ scale: 1.08 }}, {{ scale: 1.18, duration: {r(t1 - t0)}, ease: "none", immediateRender: false }}, {r(t0)});')
    j(f'tl.fromTo("#{i} .kb", {{ y: -1080 }}, {{ y: 0, duration: 0.4, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    return i


def polaroid(src, t0, t1, x, y, w, h, rot, depuis=-1, z=12):
    i = uid("po")
    HTML.append(f'<div id="{i}" class="polaroid" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px; opacity: 0; z-index: {z}">'
                f'<div class="pol-in">{media(src, "pol-media", t0, t1)}</div></div>')
    j(f'tl.fromTo("#{i}", {{ opacity: 0, y: {700 * depuis}, rotation: {rot * 3}, scale: 1.15 }}, {{ opacity: 1, y: 0, rotation: {rot}, scale: 1, duration: 0.55, ease: "back.out(1.3)", immediateRender: false }}, {r(t0)});')
    j(f'tl.fromTo("#{i} .pol-media", {{ scale: 1 }}, {{ scale: 1.09, duration: {r(t1 - t0)}, ease: "none", immediateRender: false }}, {r(t0)});')
    j(f'tl.set("#{i}", {{ opacity: 0 }}, {r(t1)});')
    return i


def etiquette(txt, t0, t1, style, rot=-2.0, fond=ORANGE, coul="#fff", taille=46):
    i = uid("et")
    HTML.append(f'<div id="{i}" class="etiq" style="opacity: 0; background: {fond}; color: {coul}; font-size: {taille}px; {style}">{txt}</div>')
    j(f'tl.fromTo("#{i}", {{ opacity: 0, scale: 0.3, rotation: {rot - 12} }}, {{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.35, ease: "back.out(2)", immediateRender: false }}, {r(t0)});')
    j(f'tl.to("#{i}", {{ opacity: 0, duration: 0.2 }}, {r(t1 - 0.2)});')
    return i


def motcle(txt, t0, t1):
    i = uid("mc")
    HTML.append(f'<div id="{i}" class="motcle" data-layout-allow-overlap style="opacity: 0">{txt}</div>')
    j(f'tl.fromTo("#{i}", {{ opacity: 0, y: 60, rotation: -5, scale: 1.2 }}, {{ opacity: 1, y: 0, rotation: -2, scale: 1, duration: 0.25, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    j(f'tl.set("#{i}", {{ opacity: 0 }}, {r(t1)});')


def mots(phrase, t0, t1, cls, style="", pas=0.1):
    i = uid("mt")
    ms = phrase.split(" ")
    spans = " ".join(f'<span id="{i}-{k}" style="display: inline-block; opacity: 0">{m}</span>' for k, m in enumerate(ms))
    HTML.append(f'<div id="{i}" class="txt {cls}" style="{style}">{spans}</div>')
    for k in range(len(ms)):
        j(f'tl.fromTo("#{i}-{k}", {{ opacity: 0, y: 40, rotation: -6 }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.35, ease: "back.out(1.8)", immediateRender: false }}, {r(t0 + pas * k)});')
    j(f'tl.to("#{i}", {{ opacity: 0, duration: 0.25 }}, {r(t1 - 0.25)});')
    return i


TRESILLO = (1.5, 1.5, 1)


def groove(v0, plans):
    """coupes plein écran sur le motif 3-3-2 de la grosse caisse ; plans = [(src, effet), …] (3 par mesure)"""
    v = v0
    for k, (src, effet) in enumerate(plans):
        pas = TRESILLO[k % 3]
        plein(src, T(v), T(v + pas), effet)
        if k % 3 == 0:
            flash(T(v), 0.3)
        v += pas
    return v


# ===================================================================== INTRO (temps 0 → 16, 0 → 8,3 s) : le collage se construit
papier(0, T(16))
HTML.append('<img id="logo1" class="logo-intro" src="assets/img/logo-recadre.png" alt="" />')
j('tl.fromTo("#logo1", { opacity: 0.4, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.8, ease: "power3.out", immediateRender: false }, 0);')
j(f'tl.to("#logo1", {{ opacity: 0, y: -60, duration: 0.3 }}, {r(T(4) - 0.3)});')
HTML.append('<div id="date1" class="txt t-date" style="opacity: 0">CONFÉRENCE · 14.11.2026</div>')
j('tl.fromTo("#date1", { opacity: 0, scaleX: 1.25 }, { opacity: 1, scaleX: 1, duration: 1.0, ease: "power3.out", immediateRender: false }, 0.35);')
j(f'tl.to("#date1", {{ opacity: 0, duration: 0.3 }}, {r(T(4) - 0.3)});')
polaroid("a-salle.jpg", T(4), T(16), 70, 70, 540, 450, -7, -1)
polaroid("a-panel-large.jpg", T(5.5), T(16), 1310, 60, 540, 450, 6, -1)
polaroid("a-etudiante-micro.mp4", T(7), T(16), 110, 570, 560, 440, 4, 1)
polaroid("a-coralie.jpg", T(8), T(16), 1270, 580, 560, 440, -5, 1)
cent = polaroid("a-coralie-pupitre.mp4", T(9.5), T(16), 640, 230, 640, 500, -2, -1, z=20)
HTML.append('<div id="titre1" class="titre-bande" style="opacity: 0"><span>DU CV AU</span> <em>« VOUS ÊTES RETENU(E) »</em></div>')
j(f'tl.fromTo("#titre1", {{ opacity: 0, scaleX: 0.2, rotation: -6 }}, {{ opacity: 1, scaleX: 1, rotation: -2, duration: 0.45, ease: "back.out(1.6)", immediateRender: false }}, {T(10)});')
j(f'tl.to("#titre1", {{ opacity: 0, y: 80, duration: 0.3 }}, {r(T(14) - 0.05)});')
# le polaroïd central grandit jusqu'à remplir l'écran au moment du refrain
# (transformations seulement : échelle 3,2 autour du centre du cadre, l'image intérieure couvre alors tout l'écran)
j(f'tl.set("#{cent}", {{ zIndex: 30 }}, {T(14)});')
j(f'tl.to("#{cent}", {{ x: 0, y: 121, scale: 3.2, rotation: 0, duration: {r(T(16) - T(14))}, ease: "power2.in" }}, {T(14)});')

# ===================================================================== REFRAIN 1 (temps 16 → 48)
flash(T(16), 0.6)
groove(16, [("a-coralie-public.mp4", "zoom"), ("a-public-gestes.mp4", "balance"), ("a-panel-duo.mp4", "glisse"),
            ("a-etudiante-micro2.mp4", "balance"), ("a-ek-diapos.mp4", "glisse"), ("a-question-salle.mp4", "zoom")])
for k, mot in enumerate(["PRÉPARER", "CONVAINCRE", "UN BON CV", "SUR MESURE"]):
    motcle(mot, T(16 + 2 * k), T(18 + 2 * k) - 0.02)

# ---- partenaire (24 → 28)
papier(T(24), T(28))
HTML.append(f'<div id="part" class="partenaire" style="opacity: 0"><img id="mains" class="mains" src="assets/img/mains-yako.png" alt="" />'
            f'<div class="part-txt"><span>EN PARTENARIAT AVEC</span><img id="logoyako" src="assets/img/logo-yako.png" alt="" /><b id="nomyako">Yako Africa Assurances Vie</b></div></div>')
montrer("part", T(24), T(28))
j(f'tl.fromTo("#mains", {{ x: -1200 }}, {{ x: 0, duration: 0.55, ease: "power3.out", immediateRender: false }}, {T(24)});')
j(f'tl.fromTo("#logoyako", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.7)", immediateRender: false }}, {T(25.5)});')
j(f'tl.fromTo("#nomyako", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out", immediateRender: false }}, {T(26)});')
etiquette("Samedi 14 novembre 2026 · Université Félix Houphouët-Boigny", T(24.5), T(28), "right: 110px; top: 890px;", -1.5, ENCRE, CREME, 34)

# ---- panélistes (28 → 36) : Coralie Gueï au milieu, cadre plus grand, noms en grand
papier(T(28), T(36))
etiquette('NOS PANÉLISTES · <b style="color: #f2b33d">YAKO AFRICA ASSURANCES VIE</b>', T(28), T(36), "left: 50%; margin-left: -470px; top: 46px; width: 940px; text-align: center;", -1.5, ENCRE, CREME, 40)
PAN = [("emmanuel-kone.png", "EMMANUEL KONE", "Responsable des Ressources Humaines", -3),
       ("coralie-guei.png", "CORALIE GUEÏ", "Directrice des Ressources et de la Transformation", 0),
       ("oguyr-gagne.png", "O’GUYR GAGNE", "Chargé de projet RH", 3)]
HTML.append('<div id="trio" class="trio" style="opacity: 0">' + "".join(
    f'<div id="tr{k}" class="tr-carte{" centre" if k == 1 else ""}" style="opacity: 0"><div class="tr-photo"><img src="assets/img/{img}" alt="" /></div>'
    f'<b>{nom}</b><span>{role}</span></div>' for k, (img, nom, role, _) in enumerate(PAN)) + '</div>')
montrer("trio", T(28), T(36))
for k, (_, _, _, rot) in enumerate(PAN):
    t = T(28 + (1.5, 0, 3)[k])
    j(f'tl.fromTo("#tr{k}", {{ opacity: 0, y: -600, rotation: {rot * 4} }}, {{ opacity: 1, y: 0, rotation: {rot}, duration: 0.55, ease: "back.out(1.3)", immediateRender: false }}, {r(t)});')
j(f'tl.fromTo("#trio", {{ scale: 1 }}, {{ scale: 1.04, duration: {r(T(36) - T(28))}, ease: "none", immediateRender: false }}, {T(28)});')

# ---- temps forts en triptyque (36 → 44) : trois panneaux, chacun change de plan
papier(T(36), T(44))
HTML.append('<div id="tripty" class="tripty" style="opacity: 0">' + "".join(f'<div id="pan{k}" class="panneau"></div>' for k in range(3)) + '</div>')
montrer("tripty", T(36), T(44))
TRI = [("VRAI OU FAUX", "#c4540f", "#fff", ["a-intervenante-public.mp4", "a-coralie-geste.mp4"]),
       ("SIMULATION D’ENTRETIEN", OR, ENCRE, ["a-simulation1.mp4", "a-simulation2.mp4"]),
       ("QUESTIONS DU PUBLIC", BLEU, "#fff", ["a-salle-question.mp4", "a-question-salle2.mp4"])]
for k, (lab, fond, coul, (s1, s2)) in enumerate(TRI):
    a, b = (36, 37.5, 39)[k], (40, 41, 42)[k]
    for src, t0, t1, sens in ((s1, T(a), T(b), -1 if k % 2 == 0 else 1), (s2, T(b), T(44), 1 if k % 2 == 0 else -1)):
        i = uid("pc")
        HTML.append(f'<div id="{i}" class="pan-clip" style="left: {20 + k * 632}px; opacity: 0">{media(src, "plein", t0, t1)}</div>')
        montrer(i, t0, t1 if t1 < T(44) else T(44))
        j(f'tl.fromTo("#{i}", {{ y: {1080 * sens} }}, {{ y: 0, duration: 0.42, ease: "power3.out", immediateRender: false }}, {r(t0)});')
        j(f'tl.fromTo("#{i} .plein", {{ scale: 1.05 }}, {{ scale: 1.14, duration: {r(t1 - t0)}, ease: "none", immediateRender: false }}, {r(t0)});')
    etiquette(lab, T(a) + 0.2, T(44), f"left: {40 + k * 632}px; top: 930px;", (-2, 1.5, -1.5)[k], fond, coul, 40)

# ---- montée (44 → 48) : 4 coupes d'un temps
v = 44
for src, eff in (("a-ek-diapos2.mp4", "zoom"), ("a-coralie-bleu.mp4", "balance"), ("a-panel-table.mp4", "glisse"), ("a-coralie-face.mp4", "zoom")):
    plein(src, T(v), T(v + 1), eff)
    v += 1
etiquette("DU CV À L’ENTRETIEN", T(44) + 0.05, T(48), "left: 50%; margin-left: -330px; width: 660px; text-align: center; top: 820px;", -2, ORANGE, "#fff", 64)

# ===================================================================== PONT (48 → 56) : le ralenti de la simulation + message
plein("lent-simulation-2.mp4", T(48), T(56), "zoom", (1.04, 1.16), depart=0.3)
HTML.append('<div id="voile-p" class="voile-chaud" style="opacity: 0"></div>')
montrer("voile-p", T(48), T(56))
mots("Un CV n’est pas une biographie.", T(48) + 0.1, T(56), "t-message", "top: 400px;", 0.14)
HTML.append('<div id="trait" class="trait"></div>')
j(f'tl.fromTo("#trait", {{ scaleX: 0, opacity: 1 }}, {{ scaleX: 1, duration: 0.9, ease: "power2.inOut", immediateRender: false }}, {r(T(50))});')
j(f'tl.set("#trait", {{ opacity: 0 }}, {T(56)});')

# ===================================================================== REFRAIN 2 (56 → 80)
flash(T(56), 0.7)
groove(56, [("a-panel-coralie.mp4", "zoom"), ("a-applaudit.mp4", "balance"), ("a-coralie-bleu2.mp4", "glisse"),
            ("a-public-gestes2.mp4", "balance"), ("a-panel-duo2.mp4", "glisse"), ("a-simulation1b.mp4", "zoom")])
for k, mot in enumerate(["ÉCOUTE", "MOTIVATION", "ESPRIT D’ÉQUIPE", "L’APRÈS-ENTRETIEN"]):
    motcle(mot, T(56 + 2 * k), T(58 + 2 * k) - 0.02)

# ---- écran partagé (64 → 72) : vidéo à gauche, message à droite
papier(T(64), T(72))
demi("a-panel-table2.mp4", T(64), T(68))
demi("a-ek-debout.mp4", T(68), T(72))
mots("C’est l’outil qui vous ouvre", T(64) + 0.15, T(72), "t-split", "top: 300px;", 0.12)
mots("la porte de l’entretien.", T(66), T(72), "t-split orange", "top: 560px;", 0.14)
flash(T(64), 0.4)

# ---- MERCI (72 → 80) : mur de photos, la grande photo de groupe au centre
papier(T(72), T(80))
polaroid("lent-groupe.mp4", T(72), T(80), 580, 40, 760, 590, -1, -1, z=20)
polaroid("a-groupe.jpg", T(73.5), T(80), 50, 110, 520, 420, -6, -1)
polaroid("a-salle-rangs.jpg", T(75), T(80), 1350, 100, 520, 420, 5, -1)
polaroid("a-coralie-etudiantes.jpg", T(76), T(80), 100, 600, 470, 380, 4, 1)
polaroid("a-ek-table.jpg", T(77), T(80), 1340, 600, 470, 380, -4, 1)
mots("MERCI", T(74), T(80), "t-merci", "top: 650px;", 0)
HTML.append('<div id="merci-sous" class="txt t-merci-sous" style="opacity: 0">à nos panélistes, à<br><b>YAKO AFRICA ASSURANCES VIE</b><br>et à tous les participants</div>')
j(f'tl.fromTo("#merci-sous", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out", immediateRender: false }}, {T(75)});')
j(f'tl.to("#merci-sous", {{ opacity: 0, duration: 0.2 }}, {r(T(80) - 0.2)});')
flash(T(72), 0.4)

# ===================================================================== FIN (80 → 88) : JE-FPA sur la petite photo de groupe
plein("a-groupe-jefpa.jpg", T(80), FIN + 0.1, "zoom", (1.03, 1.12))
HTML.append('<div id="voile-f" class="voile-chaud leger" style="opacity: 0"></div>')
montrer("voile-f", T(80), FIN + 0.1)
flash(T(80), 0.6)
HTML.append('<img id="logo2" class="logo-fin" src="assets/img/logo-recadre.png" alt="" style="opacity: 0" />')
j(f'tl.fromTo("#logo2", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.5)", immediateRender: false }}, {r(T(80) + 0.05)});')
mots("JE-FPA", T(80) + 0.1, FIN + 0.3, "t-jefpa", "top: 380px;", 0)
HTML.append('<div id="fin-sous" class="txt t-fin-sous" style="opacity: 0">Junior Entreprise de la Filière Professionnalisée Actuariat</div>')
j(f'tl.fromTo("#fin-sous", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out", immediateRender: false }}, {T(81.5)});')
HTML.append('<div id="noir" class="flash" style="background: #000"></div>')
j(f'tl.fromTo("#noir", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.0, immediateRender: false }}, {r(FIN - 1.0)});')
HTML.append('<div class="vignette"></div>')

print(len(UTILISES), "plans utilisés (chacun une seule fois), durée", FIN, "s")

CSS = f"""
      @font-face {{ font-family: "Manrope"; src: url("assets/fonts/manrope-latin.woff2") format("woff2"); font-weight: 200 800; unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215; }}
      @font-face {{ font-family: "Manrope"; src: url("assets/fonts/manrope-latin-ext.woff2") format("woff2"); font-weight: 200 800; unicode-range: U+0100-024F, U+0259, U+1E00-1EFF, U+20A0-20AB, U+20AD-20CF, U+2C60-2C7F, U+A720-A7FF; }}
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.woff2") format("woff2"); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {PAPIER}; font-family: "Manrope", sans-serif; }}
      .papier {{ position: absolute; inset: 0; z-index: 5; background: radial-gradient(ellipse 80% 70% at 50% 45%, #fbf3e6 0%, {PAPIER} 55%, #e6d5bb 100%); }}
      .plan {{ position: absolute; inset: 0; overflow: hidden; z-index: 10; background: {ENCRE}; }}
      .kb {{ position: absolute; inset: 0; }}
      .plein {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .demi {{ position: absolute; left: 0; top: 0; width: 960px; height: 1080px; overflow: hidden; z-index: 10; background: {ENCRE}; }}
      .polaroid {{ position: absolute; background: #fffaf0; padding: 14px 14px 52px; box-shadow: 0 24px 60px rgba(60,30,0,0.35), 0 3px 8px rgba(0,0,0,0.2); }}
      .pol-in {{ width: 100%; height: 100%; overflow: hidden; background: #ddd; }}
      .pol-media {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
      .logo-intro {{ position: absolute; left: 50%; top: 300px; width: 600px; margin-left: -300px; z-index: 22; border-radius: 26px; box-shadow: 0 20px 60px rgba(60,30,0,0.25); }}
      .txt {{ position: absolute; left: 0; right: 0; text-align: center; z-index: 40; }}
      .t-date {{ top: 640px; font-size: 44px; font-weight: 800; color: {ENCRE}; letter-spacing: 12px; }}
      .titre-bande {{ position: absolute; left: 50%; top: 770px; width: 1600px; margin-left: -800px; white-space: nowrap; z-index: 25; text-align: center; padding: 18px 30px 22px;
        background: {ENCRE}; font-family: "Anton", sans-serif; font-size: 100px; line-height: 1; box-shadow: 0 20px 50px rgba(0,0,0,0.35); }}
      .titre-bande span {{ color: {CREME}; }}
      .titre-bande em {{ font-style: normal; color: {OR}; }}
      .flash {{ position: absolute; inset: 0; opacity: 0; pointer-events: none; z-index: 60; }}
      .vignette {{ position: absolute; inset: 0; pointer-events: none; z-index: 55; background: radial-gradient(ellipse 75% 70% at 50% 50%, rgba(0,0,0,0) 60%, rgba(40,18,0,0.38) 100%); }}
      .motcle {{ position: absolute; left: 90px; bottom: 100px; z-index: 40; font-family: "Anton", sans-serif; font-size: 150px; line-height: 1; color: {CREME};
        text-shadow: 0 8px 0 {ORANGE}, 0 18px 50px rgba(0,0,0,0.6); letter-spacing: 2px; }}
      .etiq {{ position: absolute; z-index: 42; font-family: "Anton", sans-serif; line-height: 1.05; padding: 10px 26px 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.3); letter-spacing: 1px; white-space: nowrap; }}
      .partenaire {{ position: absolute; inset: 0; z-index: 12; }}
      .mains {{ position: absolute; left: -320px; top: 150px; width: 1320px; }}
      .part-txt {{ position: absolute; right: 150px; top: 330px; width: 600px; text-align: center; }}
      .part-txt span {{ display: block; font-size: 42px; font-weight: 800; color: {VERT}; letter-spacing: 2px; margin-bottom: 26px; }}
      .part-txt img {{ width: 460px; }}
      .part-txt b {{ display: block; margin-top: 22px; font-family: "Anton", sans-serif; font-weight: 400; font-size: 50px; color: {VERT}; letter-spacing: 1px; white-space: nowrap; }}
      .trio {{ position: absolute; z-index: 20; left: 60px; right: 60px; top: 170px; display: flex; gap: 46px; justify-content: center; align-items: center; }}
      .tr-carte {{ flex: 1; text-align: center; }}
      .tr-carte.centre {{ flex: 1.3; }}
      .tr-photo {{ display: inline-block; background: #fffaf0; padding: 14px 14px 18px; box-shadow: 0 24px 60px rgba(60,30,0,0.35); }}
      .tr-photo img {{ display: block; width: 360px; height: 440px; object-fit: cover; }}
      .tr-carte.centre .tr-photo {{ padding: 16px 16px 20px; box-shadow: 0 0 0 6px {ORANGE}, 0 30px 80px rgba(60,30,0,0.4); }}
      .tr-carte.centre .tr-photo img {{ width: 480px; height: 580px; }}
      .tr-carte b {{ display: block; margin-top: 22px; font-family: "Anton", sans-serif; font-weight: 400; font-size: 66px; color: {ENCRE}; line-height: 1; letter-spacing: 1px; }}
      .tr-carte.centre b {{ font-size: 80px; color: {ORANGE}; }}
      .tr-carte span {{ display: block; min-height: 2.5em; margin-top: 10px; font-size: 28px; font-weight: 700; color: #5a4a36; line-height: 1.25; }}
      .tripty {{ position: absolute; inset: 0; z-index: 8; }}
      .panneau {{ position: absolute; top: 20px; width: 616px; height: 1040px; background: #e2d2b8; }}
      #pan0 {{ left: 20px; }} #pan1 {{ left: 652px; }} #pan2 {{ left: 1284px; }}
      .pan-clip {{ position: absolute; top: 20px; width: 616px; height: 1040px; overflow: hidden; z-index: 12; }}
      .voile-chaud {{ position: absolute; inset: 0; z-index: 30; background: linear-gradient(180deg, rgba(40,20,5,0.55), rgba(40,20,5,0.35) 50%, rgba(40,20,5,0.6)); }}
      .voile-chaud.leger {{ background: linear-gradient(180deg, rgba(40,20,5,0.45), rgba(40,20,5,0.2) 45%, rgba(40,20,5,0.55)); }}
      .t-message {{ font-size: 100px; font-weight: 800; color: {CREME}; line-height: 1.1; padding: 0 120px; text-shadow: 0 10px 40px rgba(0,0,0,0.5); }}
      .trait {{ position: absolute; left: 50%; top: 540px; width: 900px; margin-left: -450px; height: 10px; border-radius: 5px; background: {ORANGE}; z-index: 41; transform-origin: 0 50%; opacity: 0; }}
      .t-split {{ left: 960px; right: 0; padding: 0 70px; font-family: "Anton", sans-serif; font-size: 110px; line-height: 1.04; color: {ENCRE}; text-align: left; }}
      .t-split.orange {{ color: {ORANGE}; }}
      .t-merci {{ font-family: "Anton", sans-serif; font-size: 200px; line-height: 1; color: {ORANGE}; text-shadow: 0 8px 0 {ENCRE}, 0 20px 50px rgba(0,0,0,0.35); letter-spacing: 6px; }}
      .t-merci-sous {{ top: 858px; font-size: 32px; font-weight: 800; color: {ENCRE}; line-height: 1.25; }}
      .t-merci-sous b {{ display: inline-block; margin: 4px 0 6px; font-family: "Anton", sans-serif; font-weight: 400; font-size: 64px; line-height: 1.05; color: {VERT}; letter-spacing: 1px; }}
      .logo-fin {{ position: absolute; left: 50%; top: 110px; width: 440px; margin-left: -220px; z-index: 41; border-radius: 22px; box-shadow: 0 16px 50px rgba(0,0,0,0.4); }}
      .t-jefpa {{ font-family: "Anton", sans-serif; font-size: 240px; line-height: 1; color: {CREME}; text-shadow: 0 8px 0 {ORANGE}, 0 24px 60px rgba(0,0,0,0.5); letter-spacing: 8px; }}
      .t-fin-sous {{ top: 680px; font-size: 48px; font-weight: 800; color: {CREME}; text-shadow: 0 6px 30px rgba(0,0,0,0.6); }}
"""
page = f"""<!doctype html>
<html lang="fr" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="{W}" data-height="{H}">
{chr(10).join("      " + h for h in HTML)}
      <audio id="musique" src="assets/music/aftermovie-afro.mp3" data-start="0" data-duration="{FIN}" data-volume="1" data-track-index="20"></audio>
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
(ICI / "com/index.html").write_text(page, encoding="utf-8")
