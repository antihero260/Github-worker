#!/usr/bin/env python3
"""Écrit les 15 scènes de « ia-te-donne-raison » dans compositions/ (HTML statique).

Attention : relancer ce script ÉCRASE compositions/s*.html.
Bibliothèque partagée : hyperframes-style/outils/projecteur.py.
"""
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI.parent.parent / "hyperframes-style" / "outils"))
from projecteur import *  # noqa: E402,F403
from projecteur import Scene, init, t_mot  # noqa: E402
import projecteur as P  # noqa: E402

init(ICI)


def b(i):
    """Coupure de scène juste avant le mot i."""
    return round(t_mot(i) - 0.12, 2)


FIN = 103.0
COUPES = [0, b(10), b(26), b(39), b(50), b(85), b(120), b(132), b(150), b(176), b(187), b(215), b(239), b(261), b(287), FIN]
NOMS = ["s01-certitude", "s02-question", "s03-victoire", "s04-piege", "s05-prompt-pour", "s06-prompt-contre",
        "s07-plaisir", "s08-entrainement", "s09-complaisance", "s10-observe", "s11-danger", "s12-eviter",
        "s13-bonnes-questions", "s14-certitudes", "s15-et-toi"]


def scene(k, titre):
    return Scene(NOMS[k], COUPES[k], COUPES[k + 1], titre, premiere=(k == 0), derniere=(k == 14))


def serif_tape(s, sid, i1, i2, x, y, taille, largeur=1700):
    """Phrase en serif italique qui s'écrit mot à mot avec la voix (mots i1..i2)."""
    spans = []
    for i in range(i1, i2 + 1):
        mot = P.TEXTE[i].replace("« ", "").replace(" »", "")
        spans.append(f'<span id="{sid}-{i}">{mot}</span>')
        s.montre(f"#{sid}-{i}", t_mot(i))
    cam(s, f'<div id="{sid}" class="pj-serif" style="left: {x}px; top: {y}px; width: {largeur}px; font-size: {taille}px">{" ".join(spans)}</div>')


def jauge(s, jid, x, y, w, label, n=10):
    segs = "".join(f'<i class="{jid}-seg" style="flex: 1; height: 34px; background: #2a2a2a"></i>' for _ in range(n))
    cam(s, f'<div id="{jid}" style="position: absolute; left: {x}px; top: {y}px; width: {w}px">'
           f'<div class="pj-label" style="position: static"><span class="pj-k">{label}</span></div>'
           f'<div style="display: flex; gap: 8px; margin-top: 12px">{segs}</div>'
           f'<div id="{jid}-pct" class="pj-stat" style="position: static; font-size: 64px; margin-top: 8px">0 %</div></div>')


def remplit(s, jid, g0, g1, n=10, pct=100):
    s.j(f'tl.to(".{jid}-seg", {{ backgroundColor: "#DCFC1C", duration: 0.04, stagger: {round((g1 - g0) / n, 3)} }}, {s.L(g0)});')
    s.compteur(f"#{jid}-pct", g0, 0, pct, round(g1 - g0, 2), "pct")


def carte_argument(cid, x, y, titre, signe="✓", sombre=False):
    fond = "#1c1c1c" if sombre else "#ECECE8"
    encre = "#ECECE8" if sombre else "#0a0a06"
    bord = "border: 4px solid #DCFC1C;" if sombre else ""
    lignes = "".join(f'<div style="height: 12px; width: {w}%; background: {"#4a4a4a" if sombre else "#bdbdb8"}; margin-top: 12px"></div>' for w in (90, 72, 84))
    return (f'<div id="{cid}" class="pj-carte" style="left: {x}px; top: {y}px; width: 360px; padding: 18px 22px; text-align: left; '
            f'background: {fond}; color: {encre}; {bord} opacity: 0"><div style="font-size: 44px"><span style="color: #98ac18">{signe}</span> {titre}</div>{lignes}</div>')


def trou(tid, cx, y, w=380):
    return (f'<div id="{tid}" style="position: absolute; left: {cx - w // 2}px; top: {y - 45}px; width: {w}px; height: 90px; '
            f'border-radius: 50%; background: #000; box-shadow: 0 0 0 5px #DCFC1C"></div>')


def carte_noire(s, cid, texte, g, taille=320):
    s.add(f'<div id="{cid}-noir" style="position: absolute; inset: 0; background: #000; opacity: 0"></div>'
          f'<div id="{cid}" class="pj-impact" style="position: absolute; left: 0; width: 1920px; top: {540 - taille // 2 - 20}px; '
          f'text-align: center; font-size: {taille}px; opacity: 0">{texte}</div>')
    s.j(f'tl.set("#{cid}-noir", {{ opacity: 1 }}, {s.L(g)});')
    s.choc(f"#{cid}", g)
    s.eclair(g)


def cache_carte_noire(s, cid, g):
    s.j(f'tl.set(["#{cid}-noir", "#{cid}"], {{ opacity: 0 }}, {s.L(g)});')


def coeur(hid, x, y, taille=90):
    return (f'<svg id="{hid}" style="position: absolute; left: {x}px; top: {y}px; width: {taille}px; height: {taille}px; overflow: visible; opacity: 0" viewBox="0 0 100 90">'
            '<path d="M50 88 C20 62 0 46 0 26 C0 10 12 0 26 0 C38 0 46 8 50 16 C54 8 62 0 74 0 C88 0 100 10 100 26 C100 46 80 62 50 88 Z" fill="#DCFC1C" stroke="#000" stroke-width="5" /></svg>')


# ---------------------------------------------------------------- S1 : certitude
s = scene(0, "Scène 1 · « Imagine que tu sois convaincu d'avoir raison sur quelque chose. »")
cam(s, projecteur(860))
cam(s, perso("s01-toi", 860, 800, 430))
jauge(s, "s01-cert", 1240, 330, 520, "Certitude")
s.add(hud_g("s01-hud", "Sujet · toi", "Avis : tranché"))
vit(s, "s01-toi", 0, s.fin - 0.2)
s.recadre(t_mot(4) - 0.1, 860, 440, 1.3)
bras_croises(s, "s01-toi", t_mot(4))
grossit(s, "s01-toi", t_mot(4), 1.08)
s.recadre(t_mot(6) - 0.1, 960, 540, 1)
remplit(s, "s01-cert", t_mot(4), t_mot(9))
pose(s, "s01-toi", t_mot(6), 0.12, bg=0)
pouce(s, "s01-toi", t_mot(6))
saut(s, "s01-toi", t_mot(6), 30)
acquiesce(s, "s01-toi", t_mot(8), 2)
s.ecrire()

# ---------------------------------------------------------------- S2 : la question à ChatGPT
s = scene(1, "Scène 2 · « Tu demandes à ChatGPT ce qu'il en pense… il te répond exactement dans ton sens. »")
cam(s, projecteur(600) + projecteur(1340, op=0.85))
cam(s, perso("s02-toi", 600, 800, 400))
cam(s, perso("s02-ia", 1340, 800, 400, "ia"))
s.add(hud_g("s02-hud", "Question", "À ChatGPT"))
s.add(hud_d("s02-hud-d", "Réponse", "Dans ton sens", "opacity: 0"))
s.j('tl.set("#s02-ia", { x: 700 }, 0);')
court(s, "s02-ia", s.debut + 0.05, t_mot(13) + 0.25, -700)
vit(s, "s02-toi", s.debut, s.fin - 0.2)
vit(s, "s02-ia", t_mot(13) + 0.3, s.fin - 0.2)
parle(s, "s02-toi", t_mot(10), t_mot(17) + 0.3)
bulle(s, "s02-b1", "Tu en penses quoi ?", 660, 240, t_mot(14), fin=t_mot(21))
s.recadre(t_mot(19), 1340, 460, 1.3)
acquiesce(s, "s02-ia", t_mot(21), 5)
bulle(s, "s02-b2", "Tu as totalement raison !", 1030, 220, t_mot(21))
s.recadre(t_mot(21) + 0.5, 960, 540, 1)
pouce(s, "s02-ia", t_mot(23))
tampon(s, "s02-ok", "100 % d'accord.", 700, 560, t_mot(22), -6)
s.j('tl.to("#s02-hud-d", { opacity: 1, duration: 0.12 }, %s);' % s.L(t_mot(24)))
saut(s, "s02-toi", t_mot(25), 26)
s.ecrire()

# ---------------------------------------------------------------- S3 : « même l'IA est d'accord avec moi ! »
s = scene(2, "Scène 3 · « Tu vois, même l'intelligence artificielle est d'accord avec moi ! »")
cam(s, projecteur(1120) + projecteur(1660, op=0.7))
cam(s, perso("s03-toi", 1120, 800, 440))
cam(s, perso("s03-ia", 1660, 800, 300, "ia"))
serif_tape(s, "s03-dit", 30, 38, 113, 200, 80, 760)
s.add(hud_g("s03-hud", "Conclusion", "Validée par l'IA"))
vit(s, "s03-toi", s.debut, s.fin - 0.2)
vit(s, "s03-ia", s.debut, s.fin - 0.2)
pose(s, "s03-toi", t_mot(30), 0.16, "back.out(2)", bd=-92, tete=-6)
acquiesce(s, "s03-ia", t_mot(32), 4)
s.recadre(t_mot(33), 1120, 440, 1.22)
pose(s, "s03-toi", t_mot(35), 0.12, bd=0, tete=0)
s.recadre(t_mot(36), 960, 540, 1)
victoire(s, "s03-toi", t_mot(36), 3)
acquiesce(s, "s03-ia", t_mot(36), 3)
confettis(s, "s03-conf", t_mot(38), 1120, 420)
s.ecrire()

# ---------------------------------------------------------------- S4 : le piège
s = scene(3, "Scène 4 · « Sauf que tu viens peut-être de tomber dans un piège. Regarde. »")
cam(s, projecteur(960))
cam(s, trou("s04-trou", 960, 800))
s.j('tl.set("#s04-trou", { scaleX: 0 }, 0);')
cam(s, perso("s04-toi", 960, 800, 420))
s.add(hud_g("s04-hud", "Attention", "Sol instable"))
vit(s, "s04-toi", s.debut, t_mot(45) - 0.05)
pose(s, "s04-toi", t_mot(39), 0.1, bg=0, bd=0, tete=0)
tremble(s, "s04-toi", t_mot(40), 0.5)
s.recadre(t_mot(41), 960, 600, 1.25)
s.j('tl.to("#s04-trou", { scaleX: 1, duration: 0.25, ease: "back.out(2)" }, %s);' % s.L(t_mot(43)))
pose(s, "s04-toi", t_mot(44), 0.12, "back.out(2)", bg=150, bd=-150, tete=-12)
chute(s, "s04-toi", t_mot(45))
s.recadre(t_mot(46), 960, 540, 1)
carte_noire(s, "s04-mot", "Piège.", t_mot(48))
cache_carte_noire(s, "s04-mot", t_mot(49))
s.ecrire()

# ---------------------------------------------------------------- S5 : prompt « explique-moi pourquoi j'ai raison »
s = scene(4, "Scène 5 · premier prompt : « explique-moi pourquoi j'ai raison »")
cam(s, projecteur(300, op=0.85))
cam(s, perso("s05-toi", 300, 800, 340))
msg = message(s, "s05", 56, 73, {60, 61, 62, 63, 70, 71, 72, 73})
cartes = "".join(carte_argument(f"s05-a{k}", 30 + k * 395, 330, f"Argument {k + 1}") for k in range(3))
cam(s, '<div id="s05-chat" class="pj-chat" style="left: 560px; top: 200px; width: 1250px; height: 640px">'
       '<div class="pj-chat-tete"><i></i><i></i><i></i><span style="margin-left: 14px">ChatGPT · test n° 1</span></div>'
       f'<div class="pj-msg" style="left: 30px; top: 90px; width: 1186px">{msg}</div>{cartes}</div>')
s.add(hud_g("s05-hud", "Expérience 1", "Demander d'avoir raison"))
s.j('tl.set("#s05-toi", { y: 420 }, 0);')
remonte(s, "s05-toi", s.debut + 0.1)
vit(s, "s05-toi", s.debut + 0.5, s.fin - 0.2)
tape(s, "s05-toi", t_mot(56) - 0.2, t_mot(73) + 0.4)
s.recadre(t_mot(60) - 0.1, 1185, 330, 1.3)
s.recadre(t_mot(66), 960, 540, 1)
s.recadre(t_mot(70) - 0.1, 1185, 360, 1.25)
s.recadre(t_mot(74), 960, 540, 1)
for k, i in enumerate((77, 78, 79)):
    s.claque(f"#s05-a{k}", t_mot(i), 1.4)
pouce(s, "s05-toi", t_mot(80) + 0.1)
saut(s, "s05-toi", t_mot(80) + 0.1, 30)
acquiesce(s, "s05-toi", t_mot(83), 3)
s.ecrire()

# ---------------------------------------------------------------- S6 : prompt contraire, arguments opposés
s = scene(5, "Scène 6 · deuxième prompt : « pourquoi est-ce une mauvaise stratégie ? »")
cam(s, projecteur(300, op=0.85))
cam(s, perso("s06-toi", 300, 800, 340))
msg = message(s, "s06", 90, 101, {98, 99})
cartes = "".join(carte_argument(f"s06-a{k}", 30 + k * 395, 330, f"Contre {k + 1}", "✗", True) for k in range(3))
cam(s, '<div id="s06-chat" class="pj-chat" style="left: 560px; top: 200px; width: 1250px; height: 640px">'
       '<div class="pj-chat-tete"><i></i><i></i><i></i><span style="margin-left: 14px">ChatGPT · test n° 2</span></div>'
       f'<div class="pj-msg" style="left: 30px; top: 90px; width: 1186px">{msg}</div>{cartes}</div>')
pile_pour = "".join(f'<div class="pj-carte" style="left: {12 + k * 8}px; top: {-60 - k * 52}px; width: 250px; padding: 10px; font-size: 34px">✓ Pour {k + 1}</div>' for k in range(3))
pile_contre = "".join(f'<div class="pj-carte" style="left: {12 + k * 8}px; top: {-60 - k * 52}px; width: 250px; padding: 10px; font-size: 34px; background: #1c1c1c; color: #ECECE8; border: 3px solid #DCFC1C">✗ Contre {k + 1}</div>' for k in range(3))
cam(s, '<div id="s06-balance" style="position: absolute; left: 640px; top: 160px; width: 1100px; height: 660px; opacity: 0">'
       '<div style="position: absolute; left: 538px; top: 250px; width: 24px; height: 400px; background: #8c8c8c"></div>'
       '<div style="position: absolute; left: 420px; top: 636px; width: 260px; height: 24px; background: #8c8c8c"></div>'
       '<div id="s06-fleau" style="position: absolute; left: 100px; top: 236px; width: 900px; height: 22px; background: #ECECE8">'
       f'<div style="position: absolute; left: -40px; top: 22px; width: 280px; height: 14px; background: #ECECE8">{pile_pour}</div>'
       f'<div style="position: absolute; right: -40px; top: 22px; width: 280px; height: 14px; background: #ECECE8">{pile_contre}</div></div>'
       '<div class="pj-label" style="left: 600px; top: 330px"><span class="pj-k">Aussi convaincant</span><span class="pj-d">Des deux côtés</span></div></div>')
s.add(hud_g("s06-hud", "Expérience 2", "Demander l'inverse"))
vit(s, "s06-toi", s.debut, s.fin - 0.2)
tape(s, "s06-toi", t_mot(90) - 0.2, t_mot(101) + 0.4)
s.recadre(t_mot(97) - 0.1, 1185, 330, 1.3)
s.recadre(t_mot(102), 960, 540, 1)
for k, i in enumerate((108, 109, 110)):
    s.claque(f"#s06-a{k}", t_mot(i), 1.4)
s.j('tl.to("#s06-chat", { x: 1400, opacity: 0, duration: 0.3, ease: "power3.in" }, %s);' % s.L(t_mot(113)))
s.j('tl.fromTo("#s06-balance", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 0.25, ease: "power3.out", immediateRender: false }, %s);' % s.L(t_mot(113) + 0.2))
s.j('tl.fromTo("#s06-fleau", { rotation: -12 }, { keyframes: [{ rotation: 9, duration: 0.3 }, { rotation: -6, duration: 0.3 }, { rotation: 3, duration: 0.25 }, { rotation: 0, duration: 0.2 }], transformOrigin: "50%% 50%%" }, %s);' % s.L(t_mot(113) + 0.3))
gratte(s, "s06-toi", t_mot(114))
vertiges(s, "s06-toi", t_mot(117), 300, 400, 1.4)
haussement(s, "s06-toi", t_mot(119))
s.ecrire()

# ---------------------------------------------------------------- S7 : « te faire plaisir ? Pas exactement. »
s = scene(6, "Scène 7 · « ChatGPT cherche-t-il simplement à te faire plaisir ? Pas exactement. »")
cam(s, projecteur(560) + projecteur(1340, op=0.85))
cam(s, perso("s07-toi", 560, 800, 400))
cam(s, perso("s07-ia", 1340, 800, 400, "ia"))
cam(s, coeur("s07-coeur", 1150, 430))
s.add(hud_g("s07-hud", "Question", "Il veut te plaire ?"))
vit(s, "s07-toi", s.debut, s.fin - 0.2)
vit(s, "s07-ia", s.debut, s.fin - 0.2)
parle(s, "s07-toi", t_mot(120), t_mot(127))
bulle(s, "s07-b", "Tu veux juste me faire plaisir ?", 620, 230, t_mot(124), fin=t_mot(130))
pose(s, "s07-ia", t_mot(127), 0.16, "back.out(2)", bg=78)
s.j('tl.fromTo("#s07-coeur", { opacity: 0, scale: 0.2 }, { opacity: 1, scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }, %s);' % s.L(t_mot(128)))
s.j('tl.to("#s07-coeur", { scale: 1.15, duration: 0.12, repeat: 3, yoyo: true }, %s);' % s.L(t_mot(128) + 0.2))
haussement(s, "s07-toi", t_mot(129))
non(s, "s07-ia", t_mot(130))
pose(s, "s07-ia", t_mot(130), 0.15, bg=0)
s.j('tl.to("#s07-coeur", { y: 360, rotation: 40, opacity: 0, duration: 0.45, ease: "power2.in" }, %s);' % s.L(t_mot(130)))
tampon(s, "s07-pas", "Pas exactement.", 640, 560, t_mot(131), -5)
s.ecrire()

# ---------------------------------------------------------------- S8 : entraînement
s = scene(7, "Scène 8 · « entraînés à produire des réponses utiles et à suivre les instructions »")
cam(s, projecteur(640))
cam(s, perso("s08-ia", 640, 800, 420, "ia"))
jauge(s, "s08-train", 1080, 200, 640, "Entraînement")
cam(s, '<div id="s08-liste" style="position: absolute; left: 1080px; top: 470px">' +
       "".join(f'<div class="pj-ligne-coche"><b id="s08-c{k}"></b>{t}</div>' for k, t in enumerate(("RÉPONSES UTILES", "SUIT LES INSTRUCTIONS"))) + '</div>')
s.add(hud_g("s08-hud", "Les modèles d'IA", "Comment ils apprennent"))
vit(s, "s08-ia", s.debut, s.fin - 0.2)
remplit(s, "s08-train", t_mot(135), t_mot(149))
g = t_mot(136)
while g < t_mot(141) - 0.3:  # sauts avec écart
    pose(s, "s08-ia", g, 0.12, bg=160, bd=-160, jg=14, jd=-14)
    saut(s, "s08-ia", g, 22)
    pose(s, "s08-ia", g + 0.28, 0.12, bg=0, bd=0, jg=0, jd=0)
    g += 0.56
for k, i in enumerate((141, 146)):
    s.j(f'tl.set("#s08-c{k}", {{ backgroundColor: "#DCFC1C", borderColor: "#DCFC1C" }}, {s.L(t_mot(i) + 0.1)});')
pouce(s, "s08-ia", t_mot(146))
acquiesce(s, "s08-ia", t_mot(148), 2)
s.ecrire()

# ---------------------------------------------------------------- S9 : complaisance
s = scene(8, "Scène 9 · « excessivement complaisants… trop valider le point de vue de l'utilisateur »")
cam(s, projecteur(420) + projecteur(1480, op=0.85))
cam(s, perso("s09-toi", 420, 800, 380))
cam(s, perso("s09-ia", 1480, 800, 400, "ia"))
segs = "".join(f'<i class="s09-seg" style="flex: 1; height: 40px; background: #2a2a2a"></i>' for _ in range(12))
cam(s, f'<div id="s09-jauge" style="position: absolute; left: 600px; top: 150px; width: 720px">'
       f'<div class="pj-label" style="position: static"><span class="pj-k">Complaisance</span></div>'
       f'<div style="display: flex; gap: 8px; margin-top: 12px">{segs}</div></div>')
cam(s, '<div id="s09-max" class="pj-sticker" style="left: 1240px; top: 120px; font-size: 64px; transform: rotate(6deg); opacity: 0">Excessif.</div>')
cam(s, '<div id="s09-idee" class="pj-carte" style="left: 700px; top: 330px; width: 520px; padding: 26px; opacity: 0">'
       '<div class="pj-label" style="position: static"><span class="pj-d" style="color: #5a5a5a">Idée discutable</span></div>'
       '<div style="font-size: 92px; margin-top: 10px">15 h / jour</div></div>')
s.add(hud_g("s09-hud", "Défaut", "La complaisance"))
vit(s, "s09-toi", s.debut, s.fin - 0.2)
vit(s, "s09-ia", s.debut, s.fin - 0.2)
s.j('tl.to(".s09-seg", { backgroundColor: "#DCFC1C", duration: 0.04, stagger: %s }, %s);' % (round((t_mot(155) - t_mot(151)) / 12, 3), s.L(t_mot(151))))
acquiesce(s, "s09-ia", t_mot(151), 8, 0.09)
s.claque("#s09-max", t_mot(155), 1.6)
s.j('tl.fromTo("#s09-idee", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.2, ease: "back.out(2)", immediateRender: false }, %s);' % s.L(t_mot(159)))
pose(s, "s09-toi", t_mot(159), 0.15, "back.out(2)", bd=-100)
pose(s, "s09-toi", t_mot(165), 0.15, bd=0)
for k, i in enumerate((169, 171, 173)):
    pose(s, "s09-ia", t_mot(i) - 0.12, 0.08, bg=150)
    pose(s, "s09-ia", t_mot(i), 0.06, "power4.in", bg=60)
    tampon(s, f"s09-v{k}", "Validé.", 700 + k * 190, 560 + (k % 2) * 40, t_mot(i), (-8, 5, -3)[k], 64)
pose(s, "s09-ia", t_mot(174), 0.15, bg=0)
acquiesce(s, "s09-ia", t_mot(174), 3)
grossit(s, "s09-toi", t_mot(173), 1.25)
pouce(s, "s09-toi", t_mot(175))
s.ecrire()

# ---------------------------------------------------------------- S10 : observé
s = scene(9, "Scène 10 · « Ce comportement a même été observé dans des versions de ChatGPT. »")
cam(s, projecteur(960))
cam(s, perso("s10-ia", 960, 800, 440, "ia"))
cam(s, '<svg id="s10-loupe" style="position: absolute; left: 300px; top: 300px; width: 260px; height: 260px; overflow: visible" viewBox="0 0 260 260">'
       '<circle cx="110" cy="110" r="90" fill="rgba(220,252,28,0.12)" stroke="#ECECE8" stroke-width="14" />'
       '<rect x="170" y="175" width="26" height="100" rx="10" fill="#ECECE8" transform="rotate(-45 183 225)" /></svg>')
cam(s, '<div id="s10-eq" class="pj-equerres" style="left: 810px; top: 330px; width: 300px; height: 520px; opacity: 0"><i></i><i></i><i></i><i></i></div>')
cam(s, '<div id="s10-leg" class="pj-label" style="left: 1150px; top: 330px; opacity: 0"><span class="pj-k">Complaisance</span><span class="pj-d">Constatée</span></div>')
s.add(hud_g("s10-hud", "Rapport", "Versions de ChatGPT"))
s.add(hud_d("s10-obs", "Observé", "Comportement réel", "opacity: 0"))
vit(s, "s10-ia", s.debut, s.fin - 0.2)
s.j('tl.fromTo("#s10-loupe", { x: -200, y: 120 }, { keyframes: [{ x: 420, y: -60, duration: 0.6 }, { x: 650, y: 40, duration: 0.5 }, { x: 560, y: -20, duration: 0.4 }], ease: "sine.inOut" }, %s);' % s.L(t_mot(176)))
s.claque("#s10-eq", t_mot(181), 1.2)
s.apparait("#s10-leg", t_mot(181))
s.j('tl.to("#s10-loupe", { opacity: 0, duration: 0.2 }, %s);' % s.L(t_mot(181)))
pose(s, "s10-ia", t_mot(181), 0.15, "back.out(2)", bg=150, bd=-150, tete=12)
pose(s, "s10-ia", t_mot(183), 0.2, bg=-40, bd=40, tete=16)
s.j('tl.to("#s10-obs", { opacity: 1, duration: 0.12 }, %s);' % s.L(t_mot(184)))
s.recadre(t_mot(183), 960, 460, 1.25)
s.ecrire()

# ---------------------------------------------------------------- S11 : le vrai danger
s = scene(10, "Scène 11 · « plus une réponse est bien formulée… une réponse convaincante n'est pas forcément vraie »")
cam(s, projecteur(380))
cam(s, perso("s11-toi", 380, 800, 380))
cam(s, '<div id="s11-rep" class="pj-papier" style="left: 760px; top: 170px; width: 700px; border: 8px solid #DCFC1C; opacity: 0">'
       '<h3 style="font-size: 78px">Réponse parfaite</h3>' + papier_lignes(5, (92, 84, 96, 70, 88)) + '</div>')
for k, (x, y) in enumerate(((720, 140), (1460, 200), (1430, 560), (740, 620), (1100, 110))):
    cam(s, f'<div class="s11-eclat pj-stat" style="left: {x}px; top: {y}px; font-size: 70px; opacity: 0">✦</div>')
cam(s, '<div id="s11-conv" class="pj-impact" style="position: absolute; left: 640px; width: 640px; top: 300px; text-align: center; font-size: 130px; color: #ECECE8; text-shadow: none; opacity: 0">Convaincant</div>')
cam(s, '<div id="s11-diff" style="position: absolute; left: 1290px; top: 320px; width: 130px; height: 120px; opacity: 0">'
       '<i style="position: absolute; left: 0; top: 26px; width: 130px; height: 20px; background: #DCFC1C"></i>'
       '<i style="position: absolute; left: 0; top: 70px; width: 130px; height: 20px; background: #DCFC1C"></i>'
       '<i style="position: absolute; left: 55px; top: -10px; width: 20px; height: 140px; background: #DCFC1C; transform: rotate(28deg)"></i></div>')
cam(s, '<div id="s11-vrai" class="pj-impact" style="position: absolute; left: 1430px; width: 400px; top: 300px; text-align: center; font-size: 150px; opacity: 0">Vrai</div>')
carte_noire(s, "s11-mot", "Le vrai danger.", t_mot(187), 230)
cache_carte_noire(s, "s11-mot", t_mot(190))
vit(s, "s11-toi", s.debut, s.fin - 0.2)
s.j('tl.fromTo("#s11-rep", { opacity: 0, y: 80, rotation: 4 }, { opacity: 1, y: 0, rotation: -2, duration: 0.25, ease: "back.out(1.8)", immediateRender: false }, %s);' % s.L(t_mot(192)))
s.j('tl.fromTo(".s11-eclat", { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.14, stagger: 0.08, ease: "back.out(3)", immediateRender: false }, %s);' % s.L(t_mot(196)))
s.j('tl.to(".s11-eclat", { rotation: 90, duration: 0.6, repeat: 2, yoyo: true }, %s);' % s.L(t_mot(196) + 0.5))
pose(s, "s11-toi", t_mot(196), 0.16, "back.out(2)", bd=-70)
acquiesce(s, "s11-toi", t_mot(197), 3)
s.recadre(t_mot(198), 1110, 420, 1.2)
tampon(s, "s11-preuve", "Preuve ?", 1150, 470, t_mot(206), 8, 96)
s.recadre(t_mot(207), 960, 540, 1)
non(s, "s11-toi", t_mot(207))
pose(s, "s11-toi", t_mot(207), 0.15, bd=0)
s.j('tl.to(["#s11-rep", ".s11-eclat", "#s11-preuve"], { opacity: 0, y: -60, duration: 0.2 }, %s);' % s.L(t_mot(208)))
s.apparait("#s11-conv", t_mot(210))
s.claque("#s11-diff", t_mot(211))
s.choc("#s11-vrai", t_mot(213))
bras_croises(s, "s11-toi", t_mot(213))
s.ecrire()

# ---------------------------------------------------------------- S12 : éviter le piège
s = scene(11, "Scène 12 · « pour éviter ce piège, change ta manière de poser tes questions »")
cam(s, projecteur(960, op=0.7))
cam(s, '<div id="s12-trou-p" style="position: absolute; left: 0; top: 0">' + trou("s12-trou", 960, 800, 420) + '</div>')
cam(s, perso("s12-toi", 330, 800, 380))
cam(s, '<div id="s12-raison" class="pj-carte" style="left: 560px; top: 180px; width: 800px; padding: 30px; font-family: \'Instrument Serif\', serif; font-style: italic; text-transform: none; font-size: 84px; opacity: 0">'
       '« Donne-moi raison. »<div id="s12-x" class="pj-x" style="left: 0; top: 0; width: 800px; height: 160px; opacity: 0"></div></div>')
s.add(hud_g("s12-hud", "La parade", "Changer de question"))
vit(s, "s12-toi", s.debut, t_mot(215))
court(s, "s12-toi", t_mot(215), t_mot(219) + 0.2, 1000)
saut(s, "s12-toi", t_mot(217) + 0.2, 150)
s.recadre(t_mot(216), 960, 600, 1.15)
s.recadre(t_mot(219) + 0.3, 960, 540, 1)
vit(s, "s12-toi", t_mot(219) + 0.4, s.fin - 0.2)
s.j('tl.fromTo("#s12-raison", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.22, ease: "back.out(2)", immediateRender: false }, %s);' % s.L(t_mot(220)))
pose(s, "s12-toi", t_mot(222), 0.16, "back.out(2)", bg=96)
pose(s, "s12-toi", t_mot(236), 0.12, bg=0)
s.croix("#s12-x", t_mot(236))
non(s, "s12-toi", t_mot(237))
pouce(s, "s12-toi", t_mot(238))
s.ecrire()

# ---------------------------------------------------------------- S13 : les bonnes questions
s = scene(12, "Scène 13 · « Quels arguments contre mon idée ? Mes erreurs ? Quelles preuves que j'ai tort ? »")
cam(s, projecteur(320) + projecteur(720, op=0.7))
cam(s, perso("s13-toi", 320, 800, 360))
cam(s, perso("s13-ia", 720, 800, 330, "ia"))
questions = ("Arguments contre mon idée ?", "Mes erreurs de raisonnement ?", "Preuves que j'ai tort ?")
for k, q in enumerate(questions):
    cam(s, f'<div id="s13-q{k}" class="pj-carte" style="left: 980px; top: {180 + k * 200}px; width: 840px; padding: 26px 30px; text-align: left; font-size: 50px; white-space: nowrap; opacity: 0">'
           f'<b id="s13-c{k}" style="display: inline-block; width: 52px; height: 52px; border: 5px solid #0a0a06; margin-right: 22px; vertical-align: -6px"></b>{q}</div>')
s.add(hud_g("s13-hud", "Bonnes questions", "Demander la contradiction"))
vit(s, "s13-toi", s.debut, s.fin - 0.2)
vit(s, "s13-ia", s.debut, s.fin - 0.2)
for k, (i0, i1) in enumerate(((239, 245), (246, 251), (252, 260))):
    s.glisse(f"#s13-q{k}", t_mot(i0), 300)
    s.j(f'tl.set("#s13-c{k}", {{ backgroundColor: "#DCFC1C" }}, {s.L(t_mot(i1) + 0.15)});')
parle(s, "s13-toi", t_mot(239), t_mot(245))
pose(s, "s13-ia", t_mot(243), 0.15, "back.out(2)", bd=-168, tete=-6)
pose(s, "s13-ia", t_mot(247), 0.15, bd=-100)
non(s, "s13-ia", t_mot(249))
gratte(s, "s13-toi", t_mot(249))
pose(s, "s13-toi", t_mot(252), 0.12, bd=0, tete=0)
acquiesce(s, "s13-toi", t_mot(254), 3)
pose(s, "s13-ia", t_mot(254), 0.15, bd=0, tete=0)
s.recadre(t_mot(246), 1390, 420, 1.2)
s.recadre(t_mot(252), 960, 540, 1)
pouce(s, "s13-ia", t_mot(260))
saut(s, "s13-toi", t_mot(260), 24)
s.ecrire()

# ---------------------------------------------------------------- S14 : le mur de certitudes
s = scene(13, "Scène 14 · « tu ne l'utilises pas pour réfléchir : tu l'utilises pour renforcer tes certitudes »")
cam(s, projecteur(900))
cam(s, perso("s14-toi", 900, 800, 400))
cam(s, perso("s14-ia", 1580, 800, 300, "ia"))
briques = []
k = 0
for rang in range(5):
    for col in range(7):
        x = 560 + col * 100 + (50 if rang % 2 else 0)
        if x > 1180:
            continue
        briques.append(f'<i class="s14-br" style="position: absolute; left: {x}px; top: {760 - rang * 52}px; width: 94px; height: 46px; background: #8c8c8c; border: 3px solid #5a5a5a; opacity: 0"></i>')
        k += 1
cam(s, "".join(briques))
cam(s, '<div id="s14-reflechir" class="pj-impact" style="position: absolute; left: 200px; top: 260px; font-size: 110px; color: #ECECE8; text-shadow: none; opacity: 0">Réfléchir'
       '<div id="s14-rature" style="position: absolute; left: -10px; right: -10px; top: 50%; height: 14px; background: #DCFC1C; transform-origin: 0 50%"></div></div>')
s.add(hud_g("s14-hud", "Chambre d'écho", "Tu entends ce que tu penses"))
vit(s, "s14-toi", s.debut, s.fin - 0.2)
vit(s, "s14-ia", s.debut, s.fin - 0.2)
parle(s, "s14-toi", t_mot(263), t_mot(268))
for k, (txt, i) in enumerate((("Oui.", 269), ("Exactement.", 271), ("Tout à fait.", 273))):
    bulle(s, f"s14-b{k}", txt, 1300 + (k % 2) * 160, 230 + k * 80, t_mot(i), 46, fin=t_mot(278))
acquiesce(s, "s14-ia", t_mot(269), 6)
s.j('tl.fromTo(".s14-br", { opacity: 0, y: -80 }, { opacity: 1, y: 0, duration: 0.14, stagger: %s, ease: "power2.in" }, %s);' % (round((t_mot(286) - t_mot(269)) / len(briques), 3), s.L(t_mot(269))))
s.apparait("#s14-reflechir", t_mot(278))
s.j('tl.fromTo("#s14-rature", { scaleX: 0 }, { scaleX: 1, duration: 0.16 }, %s);' % s.L(t_mot(280)))
bras_croises(s, "s14-toi", t_mot(281))
tampon(s, "s14-cert", "Certitudes.", 640, 560, t_mot(286), -4, 96)
s.cache("#s14-reflechir", t_mot(283))
s.recadre(t_mot(284), 900, 560, 1.15)
s.ecrire()

# ---------------------------------------------------------------- S15 : et toi ?
s = scene(14, "Scène 15 · « Et toi, as-tu déjà demandé à une IA de vérifier si tu avais tort ? »")
cam(s, projecteur(960))
cam(s, perso("s15-toi", 960, 800, 360))
cam(s, '<div id="s15-q" class="pj-impact" style="position: absolute; left: 1250px; top: 200px; font-size: 300px; opacity: 0">?</div>')
serif_tape(s, "s15-dit", 287, 288, 113, 220, 120, 700)
s.add(hud_g("s15-hud", "Ta réponse", "En commentaire"))
s.add(hud_d("s15-d", "Question", "Pour toi", "opacity: 0"))
vit(s, "s15-toi", s.debut, s.fin - 1.0)
marche(s, "s15-toi", t_mot(287), t_mot(289), 0)
grossit(s, "s15-toi", t_mot(287), 1.35, 0.6)
pose(s, "s15-toi", t_mot(289), 0.18, "back.out(2)", bd=-82)
s.j('tl.to("#s15-d", { opacity: 1, duration: 0.12 }, %s);' % s.L(t_mot(290)))
pose(s, "s15-toi", t_mot(296), 0.12, bd=0)
gratte(s, "s15-toi", t_mot(296) + 0.15)
s.claque("#s15-q", t_mot(299), 1.8)
haussement(s, "s15-toi", t_mot(303))
s.ecrire()

print("15 scènes écrites")
