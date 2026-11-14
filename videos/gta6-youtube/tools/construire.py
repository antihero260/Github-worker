#!/usr/bin/env python3
"""Écrit index.html de la vidéo 20 : « GTA 6 — 10 things you need to know before November 19 » (YouTube, 16:9, anglais).

Tout est calé sur les mots de la voix (assets/mots.json, alignés par whisper) :
- B-roll : un plan toutes les 0,6–0,9 s dans le hook, toutes les ~2 s ensuite ; les plans « ancrés » tombent sur le mot
  qu'ils illustrent, les plans de remplissage sont choisis dans la réserve du chapitre et coupés sur un début de mot.
  Images officielles Rockstar (presse) en mouvement Ken Burns, extraits des trailers officiels SANS leur son, vidéos Mixkit.
- 11 cartes de chapitre (#1 → #10 + BONUS) + 11 cases mystère en haut à gauche qui se dévoilent une par une.
- Graphiques de données sur chaque chapitre (frise des reports, compteurs de vues, carte, prix, précommandes, stockage…).
- Sous-titres anglais mot à mot (mot prononcé en jaune, mots clés en rose).
- Son : voix, 3 musiques Mixkit (une par partie, fondus enchaînés), bruitages jamais coupés net (fondu de sortie s'ils
  doivent être raccourcis), ambiances (marais, foule, sirène, moteur).
Relancer ce script ÉCRASE index.html (puis relancer tools/mixage.py pour le carve des musiques).
"""
import json
import re
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
MOTS = json.loads((ICI / "assets/mots.json").read_text())
DUREES = json.loads((ICI / "tools/durees.json").read_text())
PICS = json.loads((ICI / "assets/sfx/pics.json").read_text())
IMGS = {p.stem for p in (ICI / "assets/img/gta").glob("*.jpg")}
FIN = 348.4
VOIX_FIN = MOTS[-1]["end"]
DUREES_AUDIO_VOIX = 347.48


def r(x):
    return round(x, 3)


def propre(t):
    return t.rstrip(".,!?…:;").upper()


def mot(txt, t):
    """Début du mot `txt` le plus proche de l'instant t (erreur si rien à moins de 1,5 s)."""
    c = [w for w in MOTS if propre(w["text"]) == txt.upper()]
    w = min(c, key=lambda w: abs(w["start"] - t))
    assert abs(w["start"] - t) < 1.5, (txt, t, w["start"])
    return w["start"]


JS = []


def j(ligne):
    JS.append("      " + ligne)


# ================================================================ SON
SONS = []


def son(t, nom, v=0.3, sur_pic=True, d=None, note=""):
    """Bruitage posé avec son pic sur t. Jamais coupé net : s'il doit être raccourci (d), fondu de sortie."""
    p = PICS[nom]
    debut = max(0.0, t - (p["pic"] if sur_pic else 0))
    duree = min(p["duree"], FIN - debut)
    fondu = None
    if d and d < duree:
        duree, fondu = d, round(min(0.8, d * 0.4), 2)
    if duree > 0.05:
        SONS.append((r(debut), nom, round(v, 3), r(duree), fondu, note))


TOURS = {}


def tour(liste):
    k = TOURS.get(liste[0], 0)
    TOURS[liste[0]] = k + 1
    return liste[k % len(liste)]


WHOOSH = ["balaie-air", "swoosh-court", "balaie-rapide", "souffle-rapide", "swoosh-vol", "balaie-court", "zoom-air",
          "swoosh-vitesse", "souffle-air", "balaie-petit"]
IMPACTS = ["impact-basse", "impact-tambour", "zoom-impact", "impact-futur"]
POPS = ["pop-sec", "pop-click", "pop-bulle", "clic-positif"]

# ================================================================ CHAPITRES
CHAP = [("1", "13 YEARS OF WAITING", mot("FIRST", 36.8)), ("2", "RECORD-BREAKING TRAILERS", mot("SECOND", 69.5)),
        ("3", "WELCOME TO LEONIDA", mot("THIRD", 102.2)), ("4", "A MASSIVE MAP", mot("FOURTH", 128.1)),
        ("5", "TWO HEROES, ONE COUPLE", mot("FIFTH", 157.0)), ("6", "THE PRICE", mot("SIXTH", 184.3)),
        ("7", "THE PRE-ORDER RECORD", mot("SEVENTH", 207.0)), ("8", "NO PC AT LAUNCH", mot("EIGHTH", 232.0)),
        ("9", "ROCKSTAR IS EVERYWHERE", mot("NINTH", 253.5)), ("10", "MAKE ROOM", mot("TENTH", 280.5)),
        ("B", "THE THIRD TRAILER?", mot("BONUS", 307.2))]
T_CH = [c[2] for c in CHAP]

# ================================================================ B-ROLL
# Plans exclus (trop osés pour YouTube ou illisibles) : jamais utilisés.
EXCLUS = {"gta-t2-22", "gta-t2-33", "gta-t2-36", "gta-t2-37", "gta-lt-17", "gta-lt-19", "gta-lt-08", "gta-lt-16",
          "vice-city-07", "vice-city-23", "port-gellhorn-07", "jason-and-lucia-10", "jason-and-lucia-14"}
TRAILER = [f for f in DUREES if f.startswith(("gta-t2", "gta-lt")) and f not in EXCLUS]
ACTION = ["gta-t2-42", "gta-t2-43", "gta-lt-23", "gta-lt-11", "gta-lt-10", "gta-t2-34", "gta-t2-35", "gta-lt-24",
          "gta-t2-41", "gta-t2-40", "gta-lt-12", "gta-lt-20", "gta-lt-26", "gta-t2-11", "gta-lt-18", "gta-t2-32"]
VILLE = ["vice-city-10", "vice-city-11", "vice-city-15", "vice-city-27", "vice-city-08", "vice-city-03", "vice-city-17",
         "vice-city-22", "vice-city-26", "vice-city-09", "gta-t2-11", "gta-lt-26", "stk-miami-nuit", "stk-miami-lumieres",
         "stk-baie-miami", "stk-bateaux-miami", "re-ville-nuit-drone"]
PERSOS = ["jason-and-lucia-01", "jason-and-lucia-03", "jason-and-lucia-05", "jason-and-lucia-08", "jason-and-lucia-09",
          "jason-and-lucia-11", "jason-and-lucia-12", "jason-and-lucia-13", "jason-and-lucia-16", "jason-and-lucia-17",
          "jason-and-lucia-19", "jason-duval-02", "jason-duval-11", "jason-duval-17", "lucia-caminos-02",
          "lucia-caminos-08", "lucia-caminos-13", "gta-lt-09", "gta-lt-15", "gta-lt-25", "gta-t2-19", "gta-t2-20",
          "gta-t2-27", "gta-t2-34", "gta-lt-05", "gta-lt-03"]
NATURE = ["grassrivers-02", "grassrivers-03", "grassrivers-04", "grassrivers-05", "leonida-keys-01", "leonida-keys-04",
          "leonida-keys-05", "leonida-keys-06", "leonida-keys-07", "mount-kalaga-national-park-02",
          "mount-kalaga-national-park-04", "mount-kalaga-national-park-05", "mount-kalaga-national-park-06",
          "ambrosia-04", "port-gellhorn-06", "stk-mangrove-vol", "stk-marais-vol-sombre", "stk-alligator-nage",
          "stk-plage-palmiers-air", "stk-floride-coucher", "gta-t2-24", "gta-t2-25", "gta-t2-05", "gta-t2-03"]
ARGENT = ["stk-billets-tombent", "stk-compteuse-billets", "stk-cash-rotation", "stk-billets-100", "stk-billets-feuillete",
          "stk-bourse-profit", "ue-01", "ue-02", "ue-grotti-cheetah-01", "ue-squalo-01", "vv-pack-01", "gta-t2-10"]
JOUEURS = ["stk-manette-joueur", "stk-manette", "stk-joueur-online", "stk-joueur-crie", "stk-joueur-enerve",
           "re-gamer-rgb", "stk-public-mains", "stk-foule-concert", "stk-sablier", "stk-horloge-approche"]
HYPE = ["stk-foule-concert", "stk-public-mains", "re-feux-artifice", "re-feux-explosions", "vice-city-13", "vice-city-25",
        "gta-t2-29", "gta-t2-28", "gta-t2-31", "stk-foule-rue", "re-lasers-cyberpunk"]
MARQUES = ["ue-stock-305-03", "ue-goodtime-gear-01", "vice-city-09", "port-gellhorn-04", "ue-stock-305-01",
           "vv-pack-exclusive-looks-03", "ue-vice-city-style-01", "ue-electric-fang-01", "vice-city-22", "vice-city-24"]

# (instant, plan, effet) : les plans ancrés sur leur mot. effet : coup / fouet / zoom / flash / None (auto)
A = []


def a(t, plan, eff=None):
    A.append((t, plan, eff))


# ---- HOOK (0 → 36,8 s) : un plan par mot ou presque, que des vraies images du jeu et de vraies vidéos
for t, p, *e in [(0.0, "vice-city-01"), (0.6, "gta-lt-20"), (1.05, "gta-t2-40"), (1.64, "gta-lt-23"), (2.24, "gta-t2-43"),
             (2.54, "stk-manette"), (3.21, "stk-joueur-enerve"), (3.9, "gta-t2-11"), (4.45, "gta-lt-12"),
             (4.73, "stk-sablier"), (5.2, "gta-lt-26"), (5.9, "jason-and-lucia-17"), (6.6, "gta-t2-41"),
             (7.3, "vice-city-15"), (7.9, "stk-compteuse-billets"), (8.5, "stk-billets-tombent"),
             (9.3, "vice-city-18"), (10.0, "stk-cash-rotation"), (10.7, "stk-bourse-profit"),
             (11.7, "stk-horloge-approche"), (12.3, "stk-reveil-sonne"), (13.1, "stk-big-ben-timelapse"),
             (13.7, "stk-sablier"), (14.4, "stk-joueur-online"), (15.1, "gta-lt-09"), (16.0, "gta-logo-vi", "tenir"),
             (16.7, "gta-t2-42"), (17.5, "vice-city-10"), (18.6, "leonida-keys-01"), (19.3, "vice-city-27"),
             (19.7, "stk-foule-concert"), (20.3, "re-feux-artifice"), (21.1, "gta-lt-07"),
             (22.4, "art-official-cover-art"), (23.0, "gta-t2-34"), (23.7, "lucia-caminos-13"), (24.7, "gta-lt-11"),
             (25.3, "stk-joueur-crie"), (26.0, "stk-disque-dur"), (26.9, "re-gamer-rgb"),
             (27.7, "stk-joueur-online"), (28.3, "gta-t2-12"), (29.1, "gta-lt-18"), (29.9, "gta-t2-14"),
             (30.8, "vice-city-11"), (31.6, "gta-lt-15"), (32.1, "gta-date-nov19"), (33.1, "gta-lt-25"),
             (33.9, "gta-t2-35"), (34.7, "gta-lt-10"), (35.7, "gta-lt-24")]:
    a(t, p, *e)

# ---- #1 13 ans d'attente
for t, p, *e in [(36.8, "vice-city-26"), (39.8, "stk-manette-joueur"), (43.3, "stk-joueur-online"), (45.1, "stk-sablier"),
             (46.8, "gta-t2-11"), (48.9, "stk-floride-coucher"), (50.5, "gta-t2-04"), (52.1, "stk-reveil-sonne"),
             (54.4, "stk-joueur-enerve"), (55.9, "gta-lt-02"), (57.7, "gta-date-nov19"), (60.5, "stk-manette-joueur"),
             (61.3, "gta-t2-11"), (63.5, "stk-horloge-approche"), (64.7, "gta-lt-25"),
             (66.8, "art-jason-and-lucia-01-with-logos")]:
    a(t, p, *e)
# ---- #2 trailers record
for t, p, *e in [(69.5, "gta-logo-vi"), (70.1, "gta-t2-31"), (71.2, "re-feux-explosions"), (73.3, "gta-lt-26"),
             (76.2, "re-lasers-cyberpunk"), (78.8, "gta-t2-11"), (80.6, "stk-public-mains"), (82.6, "stk-horloge-approche"),
             (83.5, "stk-foule-concert"), (86.7, "gta-t2-42"), (88.8, "gta-t2-43"), (89.6, "re-feux-artifice"),
             (92.5, "stk-foule-rue"), (95.0, "vice-city-25"), (98.1, "gta-t2-41"), (100.4, "gta-lt-20")]:
    a(t, p, *e)
# ---- #3 Leonida
for t, p, *e in [(102.2, "leonida-keys-01"), (104.0, "art-vice-city-postcard"), (104.9, "leonida-keys-05"),
             (105.9, "gta-lt-02"), (107.2, "grassrivers-05"), (108.9, "stk-plage-palmiers-air"), (109.9, "stk-miami-nuit"),
             (111.0, "vice-city-01"), (111.7, "vice-city-10"), (113.4, "stk-baie-miami"), (114.6, "vice-city-15"),
             (116.5, "vice-city-11"), (117.4, "gta-t2-12"), (118.0, "vice-city-05"), (118.6, "grassrivers-04"),
             (119.0, "stk-alligator-gueule"), (119.7, "gta-t2-03"), (120.5, "vice-city-03"),
             (121.6, "mount-kalaga-national-park-04"), (122.2, "ambrosia-04"), (122.8, "port-gellhorn-06"),
             (123.7, "leonida-keys-04"), (124.8, "grassrivers-02"), (125.6, "mount-kalaga-national-park-02"),
             (126.5, "vice-city-27")]:
    a(t, p, *e)
# ---- #4 la carte
for t, p, *e in [(128.1, "leonida-keys-01"), (128.8, "vice-city-08"), (131.1, "vice-city-27"), (131.8, "re-ville-nuit-drone"),
             (134.9, "stk-mangrove-vol"), (136.2, "vice-city-15"), (139.3, "mount-kalaga-national-park-04"),
             (142.7, "mount-kalaga-national-park-03"), (144.2, "vice-city-10"), (146.5, "stk-miami-lumieres"),
             (147.3, "gta-t2-40"), (149.0, "leonida-keys-07"), (150.4, "leonida-keys-04"), (151.8, "gta-t2-12"),
             (152.6, "mount-kalaga-national-park-06"), (153.6, "gta-lt-14"), (155.0, "jason-and-lucia-16")]:
    a(t, p, *e)
# ---- #5 Jason et Lucia
for t, p, *e in [(157.0, "art-jason-and-lucia-beach"), (158.7, "jason-and-lucia-01"), (160.3, "gta-lt-15"),
             (161.3, "stk-manette"), (163.9, "gta-lt-05"), (165.5, "gta-lt-09"), (166.2, "art-jason-and-lucia-02", "tenir"),
             (168.7, "gta-lt-12"), (169.8, "jason-and-lucia-13"), (170.9, "gta-lt-25"), (172.0, "jason-and-lucia-08"),
             (172.8, "mount-kalaga-national-park-03"), (175.6, "grassrivers-08"), (177.4, "jason-and-lucia-12"),
             (179.2, "gta-t2-34"), (180.7, "lucia-caminos-13"), (182.2, "gta-lt-23"), (183.1, "jason-and-lucia-05")]:
    a(t, p, *e)
# ---- #6 le prix
for t, p, *e in [(184.3, "ue-02"), (186.1, "stk-billets-feuillete"), (187.3, "stk-billets-tombent"),
             (188.1, "art-official-cover-art"), (192.5, "ue-01"), (194.9, "stk-billets-brules"),
             (195.7, "ue-grotti-cheetah-01"), (197.4, "gta-cover-art"), (201.9, "stk-manette"), (203.1, "vv-pack-01"),
             (205.8, "stk-joueur-enerve")]:
    a(t, p, *e)
# ---- #7 précommandes
for t, p, *e in [(207.0, "gta-t2-31"), (209.5, "stk-foule-concert"), (211.4, "stk-bourse-profit"), (213.1, "stk-joueur-online"),
             (216.6, "stk-compteuse-billets"), (218.5, "vice-city-13"), (220.8, "re-lasers-cyberpunk"),
             (223.1, "re-ville-nuit-drone"), (224.6, "gta-t2-42"), (227.2, "stk-cash-rotation"), (228.7, "gta-t2-43"),
             (230.0, "gta-lt-11")]:
    a(t, p, *e)
# ---- #8 pas de PC
for t, p, *e in [(232.0, "re-gamer-rgb"), (233.3, "stk-joueur-enerve"), (235.6, "stk-joueur-crie"), (237.3, "re-gamer-rgb"),
             (240.3, "stk-manette"), (242.4, "gta-lt-26"), (243.9, "stk-manette-joueur"),
             (245.5, "stk-foule-concert"), (247.5, "stk-public-mains"), (249.0, "stk-joueur-online"), (251.4, "stk-sablier")]:
    a(t, p, *e)
# ---- #9 partout
for t, p, *e in [(253.5, "vice-city-24"), (254.8, "vice-city-09"), (256.5, "port-gellhorn-04"), (257.7, "stk-foule-rue"),
             (260.7, "ue-stock-305-03"), (262.4, "ue-goodtime-gear-01"), (263.3, "vice-city-01"), (264.5, "ue-stock-305-01"),
             (266.6, "vv-pack-exclusive-looks-03"), (267.6, "vice-city-25"), (269.8, "stk-alligator-nage"),
             (271.8, "stk-croco-portrait"), (274.2, "stk-alligator-gueule"), (275.6, "stk-alligator-combat"),
             (276.6, "grassrivers-03"), (278.4, "stk-disque-dur"), (279.3, "stk-manette-joueur")]:
    a(t, p, *e)
# ---- #10 stockage
for t, p, *e in [(280.5, "stk-disque-dur"), (282.1, "gta-t2-14"), (283.2, "stk-manette"), (285.4, "gta-t2-11"),
             (287.4, "stk-disque-dur"), (290.0, "stk-joueur-online"), (292.1, "stk-reveil-sonne"), (293.5, "gta-lt-26"),
             (296.2, "stk-horloge-approche"), (297.1, "stk-joueur-enerve"), (300.6, "stk-joueur-crie"),
             (302.1, "stk-manette-joueur"), (304.3, "stk-foule-concert"), (305.3, "gta-lt-18")]:
    a(t, p, *e)
# ---- BONUS et fin
for t, p, *e in [(307.2, "gta-logo-vi"), (308.7, "gta-lt-24"), (310.2, "gta-lt-11"), (312.3, "gta-t2-35"),
             (313.0, "stk-bourse-profit"), (316.6, "stk-billets-tombent"), (318.4, "stk-foule-concert"),
             (320.7, "re-feux-artifice"), (322.6, "re-feux-explosions"), (324.9, "stk-public-mains"), (325.5, "stk-sablier"),
             (327.0, "gta-lt-20"), (329.7, "vice-city-27"), (333.4, "art-official-cover-art"), (336.5, "ue-01"),
             (339.5, "gta-t2-40"), (341.2, "gta-lt-25"), (342.5, "gta-date-nov19", "tenir"),
             (345.3, "art-jason-and-lucia-beach-with-logos", "tenir")]:
    a(t, p, *e)

# Réserves de remplissage par tranche (instant de début, réserve, longueur visée d'un plan)
TRANCHES = [(0, TRAILER, 0.8), (T_CH[0], JOUEURS + TRAILER[:20], 2.0), (T_CH[1], HYPE + ACTION, 1.9),
            (T_CH[2], NATURE + VILLE, 1.6), (T_CH[3], VILLE + NATURE, 2.0), (T_CH[4], PERSOS, 1.9),
            (T_CH[5], ARGENT + PERSOS[:8], 1.9), (T_CH[6], HYPE + ARGENT, 1.9), (T_CH[7], JOUEURS + ACTION[:6], 1.9),
            (T_CH[8], MARQUES + HYPE, 1.8), (T_CH[9], JOUEURS + ACTION[:6], 1.9), (T_CH[10], ACTION + HYPE, 1.8)]
DEBUTS = [w["start"] for w in MOTS]


def tranche(t):
    return [z for z in TRANCHES if z[0] <= t + 1e-6][-1]


def est_video(p):
    return p in DUREES


for _, p, _ in A:
    assert est_video(p) or p in IMGS, p
    assert p not in EXCLUS, p

USAGE = {}


def choisit(reserve, voisins):
    cand = [p for p in reserve if p not in voisins and p not in EXCLUS]
    return min(cand, key=lambda p: (USAGE.get(p, 0), reserve.index(p)))


def proche_mot(t, lo, hi):
    c = [s for s in DEBUTS if lo < s < hi]
    return min(c, key=lambda s: abs(s - t)) if c else t


A.sort()
PLANS = []  # [t, plan, eff, ancre]
for k, (t, p, eff) in enumerate(A):
    PLANS.append([t, p, eff, True])
    USAGE[p] = USAGE.get(p, 0) + 1
    t1 = A[k + 1][0] if k + 1 < len(A) else FIN
    _, reserve, L = tranche(t)
    n = 0 if eff == "tenir" else max(0, round((t1 - t) / L) - 1)
    prec = p
    for i in range(1, n + 1):
        ideal = t + (t1 - t) * i / (n + 1)
        ti = proche_mot(ideal, PLANS[-1][0] + 0.55, t1 - 0.55)
        if ti - PLANS[-1][0] < 0.5 or t1 - ti < 0.5:
            continue
        f = choisit(reserve, {prec, A[k + 1][1] if k + 1 < len(A) else ""})
        USAGE[f] = USAGE.get(f, 0) + 1
        PLANS.append([ti, f, None, False])
        prec = f

# Une vidéo trop courte pour son plan : on coupe avant sa fin et on enchaîne sur un autre plan de la réserve.
for _ in range(6):
    ajout = []
    for k, (t, p, eff, anc) in enumerate(PLANS):
        t1 = PLANS[k + 1][0] if k + 1 < len(PLANS) else FIN
        if est_video(p) and t1 - t > DUREES[p] - 0.1:
            tc = t + DUREES[p] - 0.15
            if t1 - tc < 0.3:
                continue
            _, reserve, _ = tranche(t)
            f = choisit([x for x in reserve if not est_video(x) or DUREES[x] > 2.5] or reserve, {p})
            USAGE[f] = USAGE.get(f, 0) + 1
            ajout.append([r(tc), f, None, False])
    if not ajout:
        break
    PLANS = sorted(PLANS + ajout, key=lambda z: z[0])

# ================================================================ HTML des plans
VIDS, OVER = [], []
DEPARTS = {}
EFFETS_AUTO = ["coup", "fouet", "coup", "zoom", "coup", "flash"]
for k, (t0, p, eff, anc) in enumerate(PLANS):
    t1 = PLANS[k + 1][0] if k + 1 < len(PLANS) else FIN
    d = r(t1 - t0)
    pid = f"p{k:03d}"
    piste = 1 + k % 2
    if est_video(p):
        marge = DUREES[p] - d - 0.08
        u = DEPARTS.get(p, 0)
        DEPARTS[p] = u + 1
        dep = 0.0 if marge <= 0.05 else round((0.15 + u * 0.7) % marge, 2)
        if p == "gta-cover-art":
            dep = round(min(marge, 2.0 + u * 6.0), 2)
        VIDS.append(f'<video id="{pid}" class="clip pl" src="assets/video/{p}.mp4" data-start="{r(t0)}" data-duration="{d}" '
                    f'data-media-start="{dep}" data-track-index="{piste}" muted playsinline></video>')
        j(f'tl.fromTo("#{pid}", {{ scale: 1.03 }}, {{ scale: 1.1, duration: {d}, ease: "none", immediateRender: false }}, {r(t0)});')
    else:
        VIDS.append(f'<img id="{pid}" class="clip pl" src="assets/img/gta/{p}.jpg" data-start="{r(t0)}" data-duration="{d}" '
                    f'data-track-index="{piste}" alt="" />')
        m = k % 4  # Ken Burns : 4 mouvements de caméra différents
        de, a_ = [("scale: 1.04, x: 0", "scale: 1.17, x: 0"), ("scale: 1.14, x: -50", "scale: 1.14, x: 50"),
                  ("scale: 1.2, y: 20", "scale: 1.06, y: -10"), ("scale: 1.1, x: 50, y: -15", "scale: 1.2, x: -40, y: 15")][m]
        j(f'tl.fromTo("#{pid}", {{ {de} }}, {{ {a_}, duration: {d}, ease: "sine.inOut", immediateRender: false }}, {r(t0)});')
    if k == 0:
        continue
    e = (eff if eff != "tenir" else None) or (EFFETS_AUTO[k % len(EFFETS_AUTO)] if anc else None)
    if e == "coup":  # recadrage sec : la caméra cogne puis se pose
        j(f'tl.fromTo("#cam", {{ scale: 1.12 }}, {{ scale: 1.0, duration: 0.28, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif e == "fouet":  # filé horizontal
        sens = 1 if k % 2 else -1
        j(f'tl.fromTo("#cam", {{ x: {sens * 140}, filter: "blur(14px)" }}, {{ x: 0, filter: "blur(0px)", duration: 0.16, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif e == "zoom":  # zoom traversant
        j(f'tl.fromTo("#cam", {{ scale: 1.35, filter: "blur(10px)" }}, {{ scale: 1.0, filter: "blur(0px)", duration: 0.22, ease: "power3.out", immediateRender: false }}, {r(t0)});')
    elif e == "flash":
        OVER.append(f'<div id="fl{k}" class="flash"></div>')
        j(f'tl.fromTo("#fl{k}", {{ opacity: 0.55 }}, {{ opacity: 0, duration: 0.18, ease: "power2.out", immediateRender: false }}, {r(t0)});')
    son(t0, tour(WHOOSH), 0.2 if anc else 0.11, note=f"coupe {p}")

# ================================================================ EFFETS GLOBAUX
def secousse(t, amp=16, n=5):
    kf = [f'{{ x: {r(amp * (1 - i / n) * (1 if i % 2 == 0 else -1))}, y: {r(amp * 0.6 * (1 - i / n) * (-1 if i % 2 == 0 else 1))}, duration: 0.035 }}'
          for i in range(n)]
    kf.append('{ x: 0, y: 0, duration: 0.04 }')
    j(f'tl.to("#cadre", {{ keyframes: [{", ".join(kf)}] }}, {r(t)});')


def flash(t, coul="#ffffff", op=0.6, d=0.2):
    k = len(OVER)
    OVER.append(f'<div id="fx{k}" class="flash" style="background: {coul}"></div>')
    j(f'tl.fromTo("#fx{k}", {{ opacity: {op} }}, {{ opacity: 0, duration: {d}, ease: "power2.out", immediateRender: false }}, {r(t)});')


FUITES = ["fuite-violette", "fuite-ambre", "fuite-rouge", "flare-soleil", "fuite-bleue", "fuite-spirale"]


def fuite(t, d=1.4, op=0.6):
    k = len(OVER)
    OVER.append(f'<video id="lk{k}" class="clip fuite" src="assets/fx/{tour(FUITES)}.mp4" data-start="{r(t)}" data-duration="{r(d)}" '
                f'data-media-start="0.3" data-track-index="{40 + k % 3}" muted playsinline></video>')
    j(f'tl.fromTo("#lk{k}", {{ opacity: 0 }}, {{ opacity: {op}, duration: {r(d * 0.3)}, ease: "sine.out", immediateRender: false }}, {r(t)});')
    j(f'tl.to("#lk{k}", {{ opacity: 0, duration: {r(d * 0.5)}, ease: "sine.in" }}, {r(t + d * 0.5)});')


def rgb(t, force=20, d=0.18):
    j(f'tl.set("#rgbw", {{ filter: "url(#rgb)" }}, {r(t)});')
    j(f'tl.fromTo("#rgb-r", {{ attr: {{ dx: {force} }} }}, {{ attr: {{ dx: 0 }}, duration: {d}, ease: "power2.out", immediateRender: false }}, {r(t)});')
    j(f'tl.fromTo("#rgb-b", {{ attr: {{ dx: {-force} }} }}, {{ attr: {{ dx: 0 }}, duration: {d}, ease: "power2.out", immediateRender: false }}, {r(t)});')
    j(f'tl.set("#rgbw", {{ filter: "none" }}, {r(t + d + 0.01)});')


VOILES = []


def voile(t0, t1, op=0.5):
    """Assombrit le B-roll pendant un graphique (lisibilité)."""
    VOILES.append((t0, t1, op))


# ================================================================ GRAPHIQUES
GFX = []
NC = [0]


BLOC_T = []


def bloc(gid, t0, t1, contenu, style="", sortie=True):
    BLOC_T.append(t0)
    GFX.append(f'<div id="{gid}" class="clip gx" data-start="{r(t0)}" data-duration="{r(t1 - t0)}" '
               f'data-track-index="{30 + len(GFX) % 6}" style="{style}">{contenu}</div>')
    if sortie:
        j(f'tl.to("#{gid}", {{ opacity: 0, scale: 0.96, duration: 0.3, ease: "power2.in" }}, {r(t1 - 0.3)});')


def entre(sel, t, de="opacity: 0, y: 50", a_="opacity: 1, y: 0", d=0.4, ease="back.out(1.7)", s=None, v=0.22):
    j(f'tl.fromTo("{sel}", {{ {de} }}, {{ {a_}, duration: {d}, ease: "{ease}", immediateRender: false }}, {r(t)});')
    if s:
        son(t, s, v, note=f"apparition {sel}")


def slam(sel, t, s="impact-basse", v=0.32):
    entre(sel, t, "opacity: 0, scale: 2.6", "opacity: 1, scale: 1", 0.3, "power4.out")
    son(t, s, v, note=f"slam {sel}")
    secousse(t + 0.05, 12, 4)


def compteur(sel, t, de, a_, d, fmt, ease="power2.out", s="compteur", v=0.2):
    NC[0] += 1
    p = f"cp{NC[0]}"
    j(f'const {p} = {{ v: {de} }};')
    j(f'tl.fromTo({p}, {{ v: {de} }}, {{ v: {a_}, duration: {d}, ease: "{ease}", immediateRender: false, '
      f'onUpdate: () => {{ const v = {p}.v; document.querySelector("{sel}").textContent = {fmt}; }} }}, {r(t)});')
    if s:
        son(t, s, v, d=d + 0.3, note=f"compteur {sel}")


def barre(sel, t, largeur, d=0.9, s="swoosh-monte", v=0.18):
    j(f'tl.fromTo("{sel}", {{ width: 0 }}, {{ width: {largeur}, duration: {d}, ease: "power3.out", immediateRender: false }}, {r(t)});')
    if s:
        son(t, s, v, note=f"barre {sel}")


def croix(sel, t, v=0.3):
    entre(sel, t, "opacity: 0, scale: 2.2, rotation: -20", "opacity: 1, scale: 1, rotation: 0", 0.25, "power4.out")
    son(t, "buzz-faux", v, note=f"croix {sel}")


def tampon(sel, t, s="marteau", v=0.3):
    entre(sel, t, "opacity: 0, scale: 3, rotation: -18", "opacity: 1, scale: 1, rotation: -8", 0.22, "power4.out")
    son(t, s, v, note=f"tampon {sel}")
    secousse(t + 0.05, 14, 4)


CROIX_SVG = ('<svg viewBox="0 0 100 100"><path d="M14 14 L86 86 M86 14 L14 86" stroke="#ff2d55" stroke-width="13" '
             'stroke-linecap="round"/></svg>')
COCHE_SVG = ('<svg viewBox="0 0 100 100"><path d="M16 54 L40 76 L86 24" fill="none" stroke="#2ee59d" stroke-width="13" '
             'stroke-linecap="round" stroke-linejoin="round"/></svg>')


ALERTE_SVG = ('<svg class="ico-alerte" viewBox="0 0 100 90"><path d="M50 6 L96 86 H4 Z" fill="#ff2d55" stroke="#ff2d55" '
              'stroke-width="6" stroke-linejoin="round"/><path d="M50 32 V58" stroke="#fff" stroke-width="10" stroke-linecap="round"/>'
              '<circle cx="50" cy="72" r="6" fill="#fff"/></svg>')


PC_SVG = ('<svg viewBox="0 0 120 100" style="width: 190px; height: 160px"><rect x="8" y="6" width="104" height="66" rx="8" fill="none" '
          'stroke="#fff" stroke-width="8"/><path d="M48 72 L44 90 M72 72 L76 90 M34 92 H86" stroke="#fff" stroke-width="8" '
          'stroke-linecap="round"/></svg>')


def logo(nom, taille=120, style=""):
    return f'<img class="logo" src="assets/img/logos/{nom}.svg" alt="" style="height: {taille}px; {style}" />'


# ---------------------------------------------------------------- HOOK : mots qui claquent au centre
SLAMS = [(2.54, 4.4, "NOBODY HAS PLAYED IT", "#ffffff"), (8.5, 11.5, "$ HUNDREDS OF MILLIONS", "#2ee59d"),
         (12.3, 13.6, "12 DAYS", "#ffd23f"), (13.7, 15.9, "13 YEARS", "#ff3d8b"), (18.6, 19.6, "GIGANTIC MAP", "#26d6c8"),
         (19.7, 21.0, "INSANE RECORDS", "#ffd23f"), (21.1, 22.9, "CONTROVERSIAL PRICE", "#ff8a3d"),
         (26.0, 28.2, "DELETE HALF YOUR GAMES?", "#ff2d55"), (29.1, 31.5, "10 THINGS", "#ffffff"),
         (32.1, 33.0, "NOVEMBER 19", "#ff3d8b"), (34.2, 36.7, "THE LAST ONE COULD HURT", "#ff2d55")]
for i, (t0, t1, txt, c) in enumerate(SLAMS):
    gid = f"hk{i}"
    bloc(gid, t0, t1, f'<div id="{gid}-t" class="slam o0" style="color: {c}">{txt}</div>')
    slam(f"#{gid}-t", t0, tour(IMPACTS), 0.3)
    voile(t0, t1, 0.35)
    if i % 2 == 0:
        rgb(t0)
son(mot("DOLLARS", 10.0), "caisse-enreg", 0.32, note="dollars")
son(mot("MILLIONS", 9.3), "pieces", 0.25, note="millions")
son(mot("GTA", 16.0), "riser-trailer", 0.3, note="montée logo")
flash(mot("GTA", 16.0), "#ff3d8b", 0.5, 0.35)
fuite(mot("GTA", 16.0), 1.6, 0.7)
son(16.7, "moteur-sport", 0.22, note="voiture trailer")
son(mot("RECORDS", 20.3), "foule-wow", 0.22, note="records")
son(26.0, "alarme-alerte", 0.18, d=1.6, note="supprimer")
son(29.1, "sirene-police", 0.12, d=2.4, note="police plage")
son(mot("SERIOUSLY", 35.0), "battement-mystere", 0.3, note="suspense")
son(1.64, "tir-echo", 0.14, note="explosion trailer")
son(0.0, "intro-mystere", 0.28, sur_pic=False, note="ouverture")

# ---------------------------------------------------------------- CASES MYSTÈRE (1 → 10 + B) et titre du chapitre
T_CASES = mot("THINGS", 29.2)
cases = "".join(f'<div id="cz{i}" class="case"><span class="q">?</span><span class="n">{c[0]}</span></div>'
                for i, c in enumerate(CHAP))
GFX.append(f'<div id="cases" class="clip" data-start="{r(T_CASES)}" data-duration="{r(FIN - T_CASES)}" data-track-index="29">{cases}</div>')
for i in range(len(CHAP)):
    entre(f"#cz{i}", T_CASES + 0.05 * i, "opacity: 0, y: -30", "opacity: 1, y: 0", 0.3, "back.out(2)")
son(T_CASES, "verrou", 0.25, note="cases verrouillées")
for i, (n, titre, t) in enumerate(CHAP):
    j(f'tl.set("#cz{i} .q", {{ opacity: 0 }}, {r(t + 0.3)});')
    j(f'tl.set("#cz{i} .n", {{ opacity: 1 }}, {r(t + 0.3)});')
    j(f'tl.set("#cz{i}", {{ backgroundColor: "#ff3d8b", borderColor: "#ffd23f" }}, {r(t + 0.3)});')
    j(f'tl.fromTo("#cz{i}", {{ scale: 1.6 }}, {{ scale: 1.12, duration: 0.35, ease: "back.out(2)", immediateRender: false }}, {r(t + 0.3)});')
    if i > 0:
        j(f'tl.set("#cz{i - 1}", {{ backgroundColor: "rgba(255, 255, 255, 0.9)", borderColor: "rgba(255, 255, 255, 0.9)", color: "#16101f", scale: 1 }}, {r(t + 0.3)});')
    t_fin = T_CH[i + 1] if i + 1 < len(CHAP) else FIN
    GFX.append(f'<div id="ct{i}" class="clip titre-ch" data-start="{r(t + 2.6)}" data-duration="{r(t_fin - t - 2.6)}" '
               f'data-track-index="28"><b>#{n}</b> {titre}</div>')
    entre(f"#ct{i}", t + 2.6, "opacity: 0, x: -40", "opacity: 1, x: 0", 0.4, "power3.out")

# ---------------------------------------------------------------- #1 frise des reports
t0, t1 = mot("SEPTEMBER", 41.7), mot("THIRTEEN", 63.5)
noeuds = [("SEP 2013", "GTA V RELEASED", 0), ("FALL 2025", "FIRST DATE", 1), ("MAY 26, 2026", "SECOND DATE", 2),
          ("NOV 19, 2026", "RELEASE DATE", 3)]
html = '<div class="carte frise"><div class="frise-ligne"></div><div id="f1-prog" class="frise-prog"></div>'
for lab, sous, k in noeuds:
    x = 110 + k * 420
    html += (f'<div id="f1-n{k}" class="noeud o0" style="left: {x}px"><i></i><b>{lab}</b><span>{sous}</span></div>')
    if k in (1, 2):
        html += f'<div id="f1-x{k}" class="croix o0" style="left: {x - 60}px; top: 14px">{CROIX_SVG}</div>'
        html += f'<div id="f1-d{k}" class="mini-rouge o0" style="left: {x - 70}px; top: 238px">DELAYED</div>'
html += (f'<div id="f1-pf" class="plateformes o0" style="left: 860px">{logo("playstation5", 70)}<span>PS5</span></div>'
         f'<div id="f1-xb" class="plateformes o0" style="left: 1150px">{logo("xbox", 70)}<span>XBOX SERIES X|S</span></div></div>')
bloc("f1", t0, t1, html)
voile(t0, t1, 0.42)
entre("#f1-n0", t0, s="pop-sec")
j(f'tl.fromTo("#f1-prog", {{ width: 0 }}, {{ width: 1290, duration: {r(mot("NOVEMBER", 58.6) - t0)}, ease: "none", immediateRender: false }}, {r(t0)});')
entre("#f1-n1", mot("FALL", 48.9), s="pop-click")
croix("#f1-x1", mot("PUSHED", 51.0))
entre("#f1-d1", mot("PUSHED", 51.0) + 0.1, "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.25)
entre("#f1-n2", mot("MAY", 52.1), s="pop-click")
croix("#f1-x2", mot("DELAYED", 54.4))
entre("#f1-d2", mot("DELAYED", 54.4) + 0.1, "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.25)
tn = mot("NOVEMBER", 58.6)
entre("#f1-n3", tn, "opacity: 0, scale: 0.4", "opacity: 1, scale: 1.08", 0.4, "back.out(2.5)", s="cloche-succes", v=0.3)
j(f'tl.fromTo("#f1-n3 i", {{ boxShadow: "0 0 0px #ff3d8b" }}, {{ boxShadow: "0 0 40px #ff3d8b", duration: 0.6, repeat: 5, yoyo: true, ease: "sine.inOut", immediateRender: false }}, {r(tn + 0.3)});')
entre("#f1-pf", mot("PS5", 60.5), s="pop-sec")
entre("#f1-xb", mot("XBOX", 61.3), s="pop-sec")
# 13 ans + Rockstar : date verrouillée
t0 = mot("THIRTEEN", 63.5)
bloc("f1b", t0, mot("SECOND", 69.5) - 0.1,
     '<div id="f1b-n" class="gros o0" style="top: 210px">13 YEARS</div>'
     f'<div id="f1b-r" class="o0" style="position: absolute; left: 860px; top: 470px">{logo("rockstar", 200, "filter: none")}</div>'
     '<div id="f1b-s" class="tampon o0" style="left: 1060px; top: 520px">DATE LOCKED</div>')
voile(t0, mot("SECOND", 69.5), 0.4)
slam("#f1b-n", t0)
entre("#f1b-r", mot("ROCKSTAR", 66.8), "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.4, "back.out(2)", s="whoosh-accent" if "whoosh-accent" in PICS else "swoosh-accent")
tampon("#f1b-s", mot("SET", 68.4), "verrou")

# ---------------------------------------------------------------- #2 records des trailers
t0 = mot("DECEMBER", 73.3)
bloc("f2a", t0, mot("RESULT", 79.1),
     '<div id="f2a-d" class="carte date o0"><small>TRAILER 1</small>DEC 2023</div>'
     '<div id="f2a-l" class="tampon o0" style="left: 1000px; top: 420px; font-size: 120px">LEAKED</div>')
voile(t0, mot("RESULT", 79.1), 0.35)
entre("#f2a-d", t0, s="papier-glisse")
tampon("#f2a-l", mot("LEAKS", 76.2), "glitch-cine", 0.32)
rgb(mot("LEAKS", 76.2), 30, 0.3)
son(mot("ONLINE", 76.5), "clavier-long", 0.14, sur_pic=False, d=1.8, note="fuite en ligne")
t0, t1 = mot("MORE", 79.8), mot("BUT", 86.3)
bloc("f2b", t0, t1,
     '<div id="f2b-n" class="gros o0" style="top: 170px; font-size: 260px">0M</div>'
     '<div id="f2b-s" class="sous o0" style="top: 470px">VIEWS IN 24 HOURS</div>'
     '<div id="f2b-g" class="badge-or o0">GUINNESS WORLD RECORD<small>MOST VIEWED VIDEO GAME TRAILER IN 24H</small></div>')
voile(t0, t1, 0.45)
entre("#f2b-n", mot("90", 80.6), "opacity: 0, scale: 0.6", "opacity: 1, scale: 1", 0.3, "power4.out")
compteur("#f2b-n", mot("90", 80.6), 0, 90, 0.9, '"+" + Math.round(v) + "M"')
entre("#f2b-s", mot("24", 82.6), s="pop-sec")
entre("#f2b-g", mot("GUINNESS", 83.5), "opacity: 0, scale: 0.3, rotation: 10", "opacity: 1, scale: 1, rotation: -3", 0.45, "back.out(2)",
      s="trophee-magique", v=0.3)
son(mot("GUINNESS", 83.5), "foule-acclame", 0.16, d=2.8, note="record")
t0, t1 = mot("REACHING", 88.8), mot("THIRD", 102.2) - 0.1
bloc("f2c", t0, t1,
     '<div class="carte barres"><div class="b-titre">TRAILER VIEWS IN 24 HOURS</div>'
     '<div class="ligne"><div class="nom">GTA VI TRAILER 2</div><div id="f2c-b1" class="barre rose"></div><div id="f2c-v1" class="val o0">475M</div></div>'
     '<div class="ligne"><div class="nom">DEADPOOL &amp; WOLVERINE</div><div id="f2c-b2" class="barre gris"></div><div id="f2c-v2" class="val o0">365M</div></div>'
     '<div id="f2c-p" class="mini o0">ACROSS ALL PLATFORMS</div></div>')
voile(t0, t1, 0.45)
entre("#f2c-b1", t0, "opacity: 0", "opacity: 1", 0.2, "none")
barre("#f2c-b1", mot("475", 89.6), 900, 1.0)
entre("#f2c-v1", mot("475", 89.6) + 0.6, s="pop-sec")
son(mot("475", 89.6), "foule-wow", 0.2, note="475 millions")
entre("#f2c-p", mot("PLATFORMS", 93.4), s="pop-click")
barre("#f2c-b2", mot("DEADPOOL", 98.1), 693, 0.9)
entre("#f2c-v2", mot("DEADPOOL", 98.1) + 0.6, s="pop-sec")

# ---------------------------------------------------------------- #3 Leonida
t0 = mot("FLORIDA", 108.9)
bloc("f3a", t0, mot("BUT", 115.0),
     '<div id="f3a-1" class="egal o0" style="top: 230px"><b>LEONIDA</b><i>=</i><span>FLORIDA</span></div>'
     '<div id="f3a-2" class="egal o0" style="top: 430px"><b>VICE CITY</b><i>=</i><span>MIAMI</span></div>')
voile(t0, mot("BUT", 115.0), 0.4)
entre("#f3a-1", t0, "opacity: 0, x: -200", "opacity: 1, x: 0", 0.4, "power4.out", s="swoosh-vitesse")
entre("#f3a-2", mot("VICE", 111.0), "opacity: 0, x: 200", "opacity: 1, x: 0", 0.4, "power4.out", s="swoosh-vitesse")
j(f'tl.fromTo("#f3a-2 span", {{ color: "#ffffff" }}, {{ color: "#26d6c8", duration: 0.3, immediateRender: false }}, {r(mot("MIAMI", 113.4))});')
son(mot("MIAMI", 113.4), "notif-indice", 0.22, note="Miami")
t0, t1 = mot("SKYSCRAPERS", 116.5), mot("ROCKSTAR", 123.7)
lieux = [("SKYSCRAPERS", "SKYSCRAPERS", 116.5), ("BEACHES", "BEACHES", 118.0), ("SWAMPS", "SWAMPS", 118.6),
         ("ALLIGATORS", "ALLIGATORS", 119.0), ("NEIGHBORHOODS", "NEIGHBORHOODS", 120.5), ("ENVIRONMENTS", "NEW ENVIRONMENTS", 122.8)]
bloc("f3b", t0, t1, '<div class="liste">' + "".join(
    f'<div id="f3b-{k}" class="item o0"><i>{COCHE_SVG}</i>{lab}</div>' for k, (_, lab, _) in enumerate(lieux)) + '</div>')
for k, (m_, _, tt) in enumerate(lieux):
    entre(f"#f3b-{k}", mot(m_, tt), "opacity: 0, x: -120", "opacity: 1, x: 0", 0.3, "power4.out", s=tour(POPS), v=0.24)
son(mot("SWAMPS", 118.6), "marais-nuit", 0.2, sur_pic=False, d=3.2, note="ambiance marais")
son(mot("BEACHES", 118.0), "vent-roulement", 0.12, sur_pic=False, d=1.5, note="vent plage")
t0, t1 = mot("ROCKSTAR", 123.7), mot("FOURTH", 128.1) - 0.1
cartes = ["art-vice-city-postcard", "art-leonida-keys-postcard", "art-grassrivers-postcard", "art-port-gellhorn-postcard",
          "art-ambrosia-postcard", "art-mount-kalaga-national-park-postcard"]
pos = [(90, 150, -7), (650, 120, 4), (1210, 160, -3), (210, 470, 5), (770, 450, -4), (1310, 480, 6)]
bloc("f3c", t0, t1, "".join(f'<img id="f3c-{k}" class="carte-postale o0" src="assets/img/gta/{c}.jpg" alt="" '
                            f'style="left: {x}px; top: {y}px; transform: rotate({rot}deg)" />'
                            for k, (c, (x, y, rot)) in enumerate(zip(cartes, pos)))
     + '<div id="f3c-t" class="tampon o0" style="left: 640px; top: 360px; font-size: 100px">AN ENTIRE STATE</div>')
voile(t0, t1, 0.5)
for k in range(6):
    tk = t0 + 0.32 * k
    j(f'tl.fromTo("#f3c-{k}", {{ opacity: 0, y: 300, rotation: {pos[k][2] * 4} }}, {{ opacity: 1, y: 0, rotation: {pos[k][2]}, duration: 0.4, ease: "back.out(1.6)", immediateRender: false }}, {r(tk)});')
    son(tk, "photo" if k % 2 else "papier-glisse", 0.2, note="carte postale")
tampon("#f3c-t", mot("STATE", 126.0), "marteau", 0.3)

# ---------------------------------------------------------------- #4 taille de la carte
t0, t1 = mot("ACCORDING", 131.8), mot("IMAGINE", 147.3)
bloc("f4", t0, t1,
     '<div id="f4-tag" class="mini o0" style="left: 660px; top: 150px">ESTIMATES CIRCULATING ONLINE</div>'
     '<div id="f4-a" class="carre o0" style="left: 330px; top: 520px; width: 260px; height: 260px; background: rgba(160, 160, 175, 0.85)"><b>GTA V</b><span>1×</span></div>'
     '<div id="f4-b" class="carre o0" style="left: 690px; top: 412px; width: 368px; height: 368px; background: rgba(255, 61, 139, 0.9)"><b>GTA VI</b><span>~2×</span></div>'
     '<div id="f4-c" class="carre o0" style="left: 1160px; top: 470px; width: 310px; height: 310px; background: rgba(176, 106, 52, 0.9)"><b>RDR 2</b><span>?</span></div>'
     '<div id="f4-v" class="tampon o0" style="left: 600px; top: 200px; font-size: 96px">VICE CITY: ENORMOUS</div>')
voile(t0, t1, 0.45)
entre("#f4-tag", mot("ESTIMATES", 132.7), s="pop-click")
entre("#f4-a", mot("MAP", 134.9), "opacity: 0, scale: 0", "opacity: 1, scale: 1", 0.4, "back.out(2)", s="pop-long")
entre("#f4-b", mot("TWICE", 136.2), "opacity: 0, scale: 0", "opacity: 1, scale: 1", 0.5, "back.out(2)", s="zoom-expand", v=0.3)
secousse(mot("TWICE", 136.2) + 0.2, 12, 4)
entre("#f4-c", mot("RED", 142.7), "opacity: 0, scale: 0", "opacity: 1, scale: 1", 0.4, "back.out(2)", s="pop-long")
j(f'tl.to(["#f4-a", "#f4-b", "#f4-c"], {{ opacity: 0.25, duration: 0.3 }}, {r(mot("VICE", 144.2))});')
tampon("#f4-v", mot("ENORMOUS", 146.5), "impact-basse", 0.32)
t0, t1 = mot("HOURS", 149.0), mot("STORY", 155.9) + 0.5
bloc("f4b", t0, t1, '<div class="liste">'
     f'<div id="f4b-0" class="item o0"><i>{COCHE_SVG}</i>HOURS OF EXPLORATION</div>'
     f'<div id="f4b-1" class="item o0"><i>{COCHE_SVG}</i>HIDDEN LOCATIONS</div>'
     f'<div id="f4b-2" class="item o0"><i>{COCHE_SVG}</i>ACTIVITIES EVERYWHERE</div>'
     '<div id="f4b-3" class="item o0" style="color: #ffd23f">...BUT A GREAT STORY?</div></div>')
voile(t0, t1, 0.35)
for k, (m_, tt) in enumerate([("HOURS", 149.0), ("HIDDEN", 150.4), ("ACTIVITIES", 151.8), ("STORY", 155.9)]):
    entre(f"#f4b-{k}", mot(m_, tt), "opacity: 0, x: -120", "opacity: 1, x: 0", 0.3, "power4.out", s=tour(POPS), v=0.24)
son(mot("STORY", 155.9), "battement-mystere", 0.25, note="histoire ?")

# ---------------------------------------------------------------- #5 deux héros
t0, t1 = mot("TWO", 158.7), mot("THIS", 164.8)
bloc("f5a", t0, t1,
     '<div id="f5a-2" class="gros o0" style="left: 280px; width: 600px; top: 200px; font-size: 330px">2</div>'
     '<div id="f5a-2s" class="sous o0" style="left: 280px; width: 600px; top: 560px">MAIN CHARACTERS</div>'
     '<div id="f5a-3" class="gros o0" style="left: 1040px; width: 600px; top: 200px; font-size: 330px; color: #9a96a8">3</div>'
     '<div id="f5a-3s" class="sous o0" style="left: 1040px; width: 600px; top: 560px">GTA V PROTAGONISTS</div>'
     f'<div id="f5a-x" class="croix o0" style="left: 1190px; top: 230px; width: 300px; height: 300px">{CROIX_SVG}</div>')
voile(t0, t1, 0.5)
slam("#f5a-2", t0)
entre("#f5a-2s", t0 + 0.3, s="pop-sec")
entre("#f5a-3", mot("THREE", 162.6), "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.3, "back.out(2)", s="pop-long")
entre("#f5a-3s", mot("THREE", 162.6) + 0.2)
croix("#f5a-x", mot("PROTAGONISTS", 163.0) + 0.3)
t0, t1 = mot("JASON", 166.2), mot("CRIMINAL", 168.7)
bloc("f5b", t0, t1, '<div id="f5b-j" class="nom-tag o0" style="left: 250px; top: 600px">JASON<small>DUVAL</small></div>'
     '<div id="f5b-l" class="nom-tag o0" style="left: 1240px; top: 600px">LUCIA<small>CAMINOS</small></div>')
entre("#f5b-j", t0, "opacity: 0, x: -200", "opacity: 1, x: 0", 0.35, "power4.out", s="swoosh-court", v=0.25)
entre("#f5b-l", mot("LUCIA", 166.8), "opacity: 0, x: 200", "opacity: 1, x: 0", 0.35, "power4.out", s="swoosh-court", v=0.25)
t0, t1 = mot("MORAL", 177.4), mot("SIXTH", 184.3) - 0.1
bloc("f5c", t0, t1,
     '<div id="f5c-t" class="mini o0" style="left: 690px; top: 160px">A MORAL DIMENSION</div>'
     '<div id="f5c-a" class="boite o0" style="left: 300px; top: 330px">YOUR<br>CHOICES</div>'
     '<div id="f5c-f" class="fleche o0" style="left: 800px; top: 420px"><svg viewBox="0 0 120 60"><path d="M4 30 H96 M72 8 L104 30 L72 52" fill="none" stroke="#ffd23f" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
     '<div id="f5c-b" class="boite o0" style="left: 1060px; top: 330px; border-color: #ff2d55">REAL<br>CONSEQUENCES</div>')
voile(t0, t1, 0.45)
entre("#f5c-t", t0, s="pop-click")
entre("#f5c-a", mot("DECISIONS", 180.7), "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.35, "back.out(2)", s="pop-long")
entre("#f5c-f", mot("DECISIONS", 180.7) + 0.5, "opacity: 0, x: -60", "opacity: 1, x: 0", 0.3, s="swoosh-court")
entre("#f5c-b", mot("CONSEQUENCES", 182.2), "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.35, "back.out(2)", s="impact-tambour", v=0.3)
secousse(mot("CONSEQUENCES", 182.2) + 0.1, 12, 4)

# ---------------------------------------------------------------- #6 le prix
t0, t1 = mot("STANDARD", 188.1), mot("SOME", 197.4)
bloc("f6a", t0, t1,
     '<div id="f6a-s" class="prix o0" style="left: 330px"><small>STANDARD EDITION</small><b id="f6a-sv">$0.00</b></div>'
     '<div id="f6a-u" class="prix or o0" style="left: 1010px"><small>ULTIMATE EDITION</small><b id="f6a-uv">$0.00</b></div>')
voile(t0, t1, 0.45)
entre("#f6a-s", t0, "opacity: 0, y: 200, rotation: -6", "opacity: 1, y: 0, rotation: -2", 0.45, "back.out(1.6)", s="papier-glisse")
compteur("#f6a-sv", mot("$79.99", 190.8) - 0.5, 0, 79.99, 0.6, '"$" + v.toFixed(2)', s="pieces", v=0.22)
son(mot("$79.99", 190.8), "caisse-enreg", 0.32, note="79,99")
entre("#f6a-u", mot("ULTIMATE", 192.5), "opacity: 0, y: 200, rotation: 6", "opacity: 1, y: 0, rotation: 2", 0.45, "back.out(1.6)", s="papier-glisse")
compteur("#f6a-uv", mot("$99.99", 194.9) - 0.5, 0, 99.99, 0.6, '"$" + v.toFixed(2)', s="pieces", v=0.22)
son(mot("$99.99", 194.9), "caisse-enreg", 0.34, note="99,99")
j(f'tl.fromTo("#f6a-u", {{ boxShadow: "0 0 0px rgba(255, 210, 63, 0)" }}, {{ boxShadow: "0 0 60px rgba(255, 210, 63, 0.9)", duration: 0.5, repeat: 3, yoyo: true, immediateRender: false }}, {r(mot("$99.99", 194.9))});')
t0, t1 = mot("SOME", 197.4), mot("SEVENTH", 207.0) - 0.1
bloc("f6b", t0, t1,
     '<div id="f6b-box" class="boitier o0"><img src="assets/img/gta/art-official-cover-art.jpg" alt="" /><span>PHYSICAL EDITION</span></div>'
     '<div id="f6b-disc" class="disque o0"></div>'
     f'<div id="f6b-x" class="croix o0" style="left: 1010px; top: 230px; width: 300px; height: 300px">{CROIX_SVG}</div>'
     '<div id="f6b-code" class="code o0"><small>DOWNLOAD CODE</small>XXXX-XXXX-XXXX</div>'
     '<div id="f6b-t" class="tampon o0" style="left: 980px; top: 640px; font-size: 90px">NO DISC INSIDE</div>')
voile(t0, t1, 0.5)
entre("#f6b-box", mot("PHYSICAL", 198.3), "opacity: 0, x: -300, rotation: -12", "opacity: 1, x: 0, rotation: -4", 0.45, "back.out(1.6)", s="papier-glisse")
entre("#f6b-disc", mot("DISC", 200.3) - 0.2, "opacity: 0, scale: 0, rotation: -180", "opacity: 1, scale: 1, rotation: 0", 0.4, "back.out(2)", s="pop-long")
croix("#f6b-x", mot("DISC", 200.3) + 0.25)
entre("#f6b-code", mot("DOWNLOAD", 201.0), "opacity: 0, x: 200", "opacity: 1, x: 0", 0.4, "back.out(1.8)", s="notif-positive")
j(f'tl.to(["#f6b-disc", "#f6b-x"], {{ opacity: 0, duration: 0.25 }}, {r(mot("DOWNLOAD", 201.0))});')
tampon("#f6b-t", mot("DISC", 205.8) - 0.1, "buzzer-faux", 0.25)

# ---------------------------------------------------------------- #7 précommandes
t0, t1 = mot("ACCORDING", 211.4), mot("CRAZIEST", 230.4)
bloc("f7", t0, t1,
     '<div class="carte barres" style="top: 200px"><div class="b-titre">PRE-ORDERS</div>'
     '<div class="ligne"><div class="nom">GTA VI</div><div id="f7-b1" class="barre rose"></div><div id="f7-v1" class="val o0">0M</div></div>'
     '<div class="ligne"><div class="nom">CYBERPUNK 2077</div><div id="f7-b2" class="barre jaune"></div><div id="f7-v2" class="val o0">8M</div></div>'
     '<div id="f7-s" class="mini o0">SOURCE: SENSOR TOWER ESTIMATE</div></div>'
     '<div id="f7-g" class="ecart o0">ONLY ~300,000 TO GO</div>')
voile(t0, t1, 0.45)
entre("#f7-s", mot("SENSOR", 213.1), s="pop-click")
t77 = mot("7.7", 216.6)
barre("#f7-b1", t77 - 0.6, 866, 1.0)
entre("#f7-v1", t77 - 0.6, "opacity: 0", "opacity: 1", 0.2, "none")
compteur("#f7-v1", t77 - 0.6, 0, 7.7, 1.0, 'v.toFixed(1) + "M"', s=None)
son(t77, "pieces-2", 0.25, note="7,7 M")
barre("#f7-b2", mot("CYBERPUNK", 220.8), 900, 1.0)
entre("#f7-v2", mot("8", 223.1), "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.3, "back.out(2)", s="pop-sec")
entre("#f7-g", mot("300,000", 227.2), "opacity: 0, scale: 2.5", "opacity: 1, scale: 1", 0.3, "power4.out", s="impact-tambour", v=0.32)
j(f'tl.fromTo("#f7-g", {{ opacity: 1 }}, {{ opacity: 0.4, duration: 0.25, repeat: 5, yoyo: true, immediateRender: false }}, {r(mot("300,000", 227.2) + 0.4)});')
son(mot("CRAZIEST", 230.4), "battement-mystere", 0.28, note="suspense")

# ---------------------------------------------------------------- #8 pas de PC
t0, t1 = T_CH[7] + 2.3, mot("JUST", 244.4)
bloc("f8", t0, t1,
     f'<div id="f8-pc" class="plateforme o0" style="left: 220px">{PC_SVG}<b>PC</b></div>'
     f'<div id="f8-x" class="croix o0" style="left: 250px; top: 260px; width: 340px; height: 340px">{CROIX_SVG}</div>'
     '<div id="f8-n" class="tampon o0" style="left: 140px; top: 650px; font-size: 70px">NOT AT LAUNCH</div>'
     f'<div id="f8-ps" class="plateforme o0" style="left: 820px">{logo("playstation5", 170)}<b>PS5</b></div>'
     f'<div id="f8-xb" class="plateforme o0" style="left: 1380px">{logo("xbox", 170)}<b>XBOX SERIES</b></div>'
     f'<div id="f8-c1" class="coche o0" style="left: 940px">{COCHE_SVG}</div>'
     f'<div id="f8-c2" class="coche o0" style="left: 1500px">{COCHE_SVG}</div>')
voile(t0, t1, 0.5)
entre("#f8-pc", t0, "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.4, "back.out(2)", s="pop-long")
croix("#f8-x", mot("PC", 237.4), 0.34)
secousse(mot("PC", 237.4) + 0.05, 16, 5)
tampon("#f8-n", mot("ANNOUNCED", 239.1), "marteau", 0.26)
entre("#f8-ps", mot("PS5", 241.8), "opacity: 0, y: 120", "opacity: 1, y: 0", 0.35, "back.out(2)", s="pop-sec")
entre("#f8-c1", mot("PS5", 241.8) + 0.25, "opacity: 0, scale: 0", "opacity: 1, scale: 1", 0.3, "back.out(3)", s="coche")
entre("#f8-xb", mot("XBOX", 242.4), "opacity: 0, y: 120", "opacity: 1, y: 0", 0.35, "back.out(2)", s="pop-sec")
entre("#f8-c2", mot("XBOX", 242.4) + 0.25, "opacity: 0, scale: 0", "opacity: 1, scale: 1", 0.3, "back.out(3)", s="coche")
t0, t1 = mot("WHILE", 249.0), mot("NINTH", 253.5) - 0.1
bloc("f8b", t0, t1, '<div id="f8b-t" class="slam o0" style="font-size: 120px">PC PLAYERS: STILL WAITING...</div>')
voile(t0, t1, 0.4)
entre("#f8b-t", t0, "opacity: 0, y: 60", "opacity: 1, y: 0", 0.4, "power3.out", s="tic-tac", v=0.2)

# ---------------------------------------------------------------- #9 partout
t0, t1 = mot("HYPE", 257.7), mot("BETWEEN", 262.8)
bloc("f9a", t0, t1, '<div class="carte jauge"><div class="b-titre">HYPE LEVEL</div><div class="jauge-fond"><div id="f9a-b" class="jauge-plein"></div></div>'
     '<div id="f9a-m" class="mini-rouge o0" style="left: 1080px; top: 30px; font-size: 44px">MAX</div></div>')
voile(t0, t1, 0.4)
barre("#f9a-b", t0, 1180, 1.8, "riser-synth", 0.22)
tampon("#f9a-m", t0 + 1.8, "alarme-alerte", 0.15)
t0, t1 = mot("BETWEEN", 262.8), mot("XBOX", 269.8)
bloc("f9b", t0, t1, '<div class="liste">'
     f'<div id="f9b-0" class="item o0"><i>{COCHE_SVG}</i>VICE CITY REFERENCES</div>'
     f'<div id="f9b-1" class="item o0"><i>{COCHE_SVG}</i>MARKETING CAMPAIGNS</div>'
     f'<div id="f9b-2" class="item o0"><i>{COCHE_SVG}</i>EASTER EGGS</div>'
     f'<div id="f9b-3" class="item o0" style="color: #ffd23f"><i>{COCHE_SVG}</i>EVEN COMPETITORS</div></div>')
voile(t0, t1, 0.35)
for k, (m_, tt) in enumerate([("VICE", 263.3), ("MARKETING", 264.5), ("EASTER", 266.6), ("COMPETITORS", 267.6)]):
    entre(f"#f9b-{k}", mot(m_, tt), "opacity: 0, x: -120", "opacity: 1, x: 0", 0.3, "power4.out", s=tour(POPS), v=0.24)
t0, t1 = mot("XBOX", 269.8), mot("BUT", 276.6)
bloc("f9c", t0, t1, f'<div id="f9c-x" class="o0" style="position: absolute; left: 820px; top: 250px">{logo("xbox", 280)}</div>'
     '<div id="f9c-r" class="mini o0" style="left: 790px; top: 160px">REPORTEDLY</div>'
     '<div id="f9c-q" class="slam o0" style="top: 600px; font-size: 100px; color: #2ee59d">A CONSOLE INSIDE AN ALLIGATOR?!</div>')
voile(t0, t1, 0.3)
entre("#f9c-x", t0, "opacity: 0, scale: 0.2, rotation: -90", "opacity: 1, scale: 1, rotation: 0", 0.5, "back.out(2)", s="power-up", v=0.25)
entre("#f9c-r", t0 + 0.3, s="pop-click")
slam("#f9c-q", mot("ALLIGATOR", 274.2), "surprise-cartoon", 0.28)
son(mot("ALLIGATOR", 275.6), "foule-wow", 0.2, note="un alligator")
t0, t1 = mot("DIRECTLY", 278.4), mot("TENTH", 280.5) - 0.1
bloc("f9d", t0, t1, f'<div id="f9d-t" class="alerte o0">{ALERTE_SVG}YOUR CONSOLE</div>')
entre("#f9d-t", t0, "opacity: 0, scale: 1.8", "opacity: 1, scale: 1", 0.25, "power4.out", s="signal-alerte", v=0.22)
flash(t0, "#ff2d55", 0.35, 0.3)

# ---------------------------------------------------------------- #10 stockage
t0, t1 = T_CH[9] + 2.3, mot("AND", 290.0)
bloc("f10a", t0, t1,
     '<div class="carte stock"><div class="b-titre">CONSOLE STORAGE</div><div class="jauge-fond">'
     '<div id="f10a-o" class="jauge-autres"></div><div id="f10a-g" class="jauge-gta"></div></div>'
     '<div class="leg"><span class="pt gris"></span>YOUR OTHER GAMES <span class="pt rose" style="margin-left: 50px"></span>GTA VI</div>'
     '<div id="f10a-v" class="val-gb o0">0 GB</div><div id="f10a-e" class="mini o0" style="left: 440px; top: 44px">ESTIMATE</div></div>')
voile(t0, t1, 0.5)
barre("#f10a-o", t0 + 0.2, 640, 0.8, "swoosh-monte", 0.15)
entre("#f10a-e", mot("ESTIMATES", 283.8), s="pop-click")
t212 = mot("212", 287.4)
barre("#f10a-g", t212 - 0.4, 620, 1.2, None)
entre("#f10a-v", t212 - 0.4, "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.3, "back.out(2)")
compteur("#f10a-v", t212 - 0.4, 0, 212, 1.2, 'Math.round(v) + " GB"', s="disque-charge" if "disque-charge" in PICS else "compteur", v=0.22)
son(t212 + 0.8, "alarme-alerte", 0.14, d=1.4, note="212 Go")
t0, t1 = mot("PRE-LOAD", 293.5), mot("SO", 297.1)
bloc("f10b", t0, t1, '<div id="f10b-c" class="calendrier o0"><div class="cal-h">NOVEMBER</div><div id="f10b-n" class="cal-n">10</div>'
     '<div class="cal-b">PRE-LOAD</div></div><div id="f10b-r" class="mini o0" style="left: 1080px; top: 640px">REPORTEDLY</div>')
voile(t0, t1, 0.45)
entre("#f10b-c", t0, "opacity: 0, y: -300, rotation: 10", "opacity: 1, y: 0, rotation: -3", 0.5, "bounce.out", s="page")
entre("#f10b-r", mot("REPORTEDLY", 294.2), s="pop-click")
j(f'tl.fromTo("#f10b-n", {{ scale: 1.8, color: "#ffd23f" }}, {{ scale: 1, color: "#ff3d8b", duration: 0.35, ease: "back.out(2)", immediateRender: false }}, {r(mot("10", 296.8))});')
son(mot("10", 296.8), "cloche-bois", 0.3, note="10 novembre")
t0, t1 = mot("FULL", 298.8), mot("BONUS", 307.2) - 0.1
bloc("f10c", t0, t1, f'<div id="f10c-m" class="modal o0"><div class="m-t">{ALERTE_SVG}STORAGE FULL</div>'
     '<div class="m-s">Not enough space to install GTA VI.<br>Free up <b>212 GB</b> to continue.</div>'
     '<div class="m-btn">MANAGE STORAGE</div></div>')
voile(t0, t1, 0.5)
entre("#f10c-m", t0, "opacity: 0, scale: 0.6", "opacity: 1, scale: 1", 0.3, "back.out(2)", s="erreur-echec", v=0.3)
tq = mot("ENOUGH", 303.3)
j(f'tl.fromTo("#f10c-m", {{ x: -30 }}, {{ x: 0, duration: 0.4, ease: "elastic.out(1, 0.25)", immediateRender: false }}, {r(tq)});')
son(tq, "buzzer-faux", 0.3, note="pas assez de place")
flash(tq, "#ff2d55", 0.4, 0.3)
secousse(tq, 18, 5)

# ---------------------------------------------------------------- BONUS
t0, t1 = T_CH[10] + 2.65, mot("MEANWHILE", 313.0)
bloc("fba", t0, t1, '<div id="fba-t" class="trailer3 o0"><small>TRAILER</small>3<b>?</b></div>')
voile(t0, t1, 0.5)
entre("#fba-t", t0, "opacity: 0, scale: 0.4", "opacity: 1, scale: 1", 0.4, "back.out(2)", s="coup-mystere", v=0.3)
j(f'tl.fromTo("#fba-t b", {{ rotation: -12 }}, {{ rotation: 12, duration: 0.4, repeat: 7, yoyo: true, ease: "sine.inOut", immediateRender: false }}, {r(t0 + 0.4)});')
t0, t1 = mot("50", 316.6), mot("THIRTEEN", 325.5)
bloc("fbb", t0 - 0.5, t1,
     '<div id="fbb-n" class="gros o0" style="top: 170px; font-size: 270px">0M</div>'
     '<div id="fbb-s" class="sous o0" style="top: 480px">COPIES IN THE FIRST WEEK</div>'
     '<div id="fbb-p" class="mini o0" style="left: 780px; top: 120px">PROJECTION</div>'
     '<div id="fbb-h" class="tampon o0" style="left: 340px; top: 620px; font-size: 80px">ONE OF THE BIGGEST LAUNCHES EVER?</div>')
voile(t0 - 0.5, t1, 0.45)
entre("#fbb-n", t0 - 0.5, "opacity: 0, scale: 0.6", "opacity: 1, scale: 1", 0.3, "power4.out")
compteur("#fbb-n", t0 - 0.5, 0, 50, 1.0, 'Math.round(v) + "M"')
entre("#fbb-p", t0 - 0.3, s="pop-click")
entre("#fbb-s", mot("COPIES", 317.2), s="pop-sec")
son(t0, "foule-acclame", 0.15, d=3.0, note="50 millions")
tampon("#fbb-h", mot("BIGGEST", 322.6), "impact-basse", 0.3)
t0, t1 = mot("FINAL", 330.6), mot("AND", 341.0)
bloc("fbc", t0, t1,
     '<div id="fbc-q" class="mini o0" style="left: 760px; top: 130px; font-size: 44px">FINAL QUESTION</div>'
     '<div id="fbc-s" class="prix o0" style="left: 300px; top: 260px"><small>STANDARD</small><b>$79.99</b></div>'
     '<div id="fbc-vs" class="vs o0">VS</div>'
     '<div id="fbc-u" class="prix or o0" style="left: 1040px; top: 260px"><small>ULTIMATE</small><b>$99.99</b></div>'
     '<div id="fbc-c" class="bulle o0">TELL ME IN THE COMMENTS</div>')
voile(t0, t1, 0.5)
entre("#fbc-q", t0, s="notif-indice")
entre("#fbc-s", mot("STANDARD", 333.4), "opacity: 0, x: -300", "opacity: 1, x: 0", 0.4, "back.out(1.6)", s="swoosh-vitesse")
entre("#fbc-vs", mot("OR", 335.8), "opacity: 0, scale: 3", "opacity: 1, scale: 1", 0.3, "power4.out", s="impact-tambour", v=0.3)
entre("#fbc-u", mot("ULTIMATE", 336.5), "opacity: 0, x: 300", "opacity: 1, x: 0", 0.4, "back.out(1.6)", s="swoosh-vitesse")
entre("#fbc-c", mot("COMMENTS", 340.4) - 0.3, "opacity: 0, y: 80, scale: 0.6", "opacity: 1, y: 0, scale: 1", 0.35, "back.out(2)", s="notif-positive")
t0 = mot("SUBSCRIBE", 341.2)
bloc("fbd", t0, mot("NOVEMBER", 342.5) + 1.4,
     '<div id="fbd-b" class="abonne o0"><span id="fbd-bt">SUBSCRIBE</span></div>'
     '<div id="fbd-cl" class="cloche o0"><svg viewBox="0 0 24 24"><path fill="#fff" d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-6V11a7 7 0 0 0-5.5-6.84V3.5a1.5 1.5 0 0 0-3 0v.66A7 7 0 0 0 5 11v5l-2 2v1h18v-1Z"/></svg></div>'
     '<div id="fbd-m" class="souris o0"><svg viewBox="0 0 24 24"><path fill="#fff" stroke="#000" stroke-width="1.2" d="M4 2 L4 19 L8.5 14.8 L11.5 21.5 L14.2 20.3 L11.3 13.8 L17.5 13.6 Z"/></svg></div>')
entre("#fbd-b", t0, "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.35, "back.out(2)", s="pop-long")
entre("#fbd-cl", t0 + 0.15, "opacity: 0, scale: 0.5", "opacity: 1, scale: 1", 0.35, "back.out(2)")
entre("#fbd-m", t0 + 0.1, "opacity: 0, x: 260, y: 200", "opacity: 1, x: 0, y: 0", 0.45, "power3.out")
tc = t0 + 0.6
j(f'tl.fromTo("#fbd-m", {{ scale: 1 }}, {{ scale: 0.8, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }}, {r(tc)});')
j(f'tl.set("#fbd-b", {{ backgroundColor: "#3a3a44" }}, {r(tc + 0.08)});')
j(f'tl.set("#fbd-bt", {{ textContent: "SUBSCRIBED" }}, {r(tc + 0.08)});')
j(f'tl.fromTo("#fbd-cl", {{ rotation: -25 }}, {{ rotation: 25, duration: 0.12, repeat: 5, yoyo: true, ease: "sine.inOut", immediateRender: false }}, {r(tc + 0.3)});')
son(tc, "clic-souris", 0.35, note="clic abonnement")
son(tc + 0.3, "cloche-boutique", 0.28, note="cloche")
t0 = mot("NOVEMBER", 342.5)
son(t0, "choeur-brille", 0.25, note="date finale")
j(f'tl.to(["#cases", "#ct10"], {{ opacity: 0, duration: 0.4, ease: "sine.in" }}, {r(t0 - 0.2)});')
j(f'tl.to("#fondu-fin", {{ opacity: 1, duration: 1.2, ease: "sine.in" }}, {r(FIN - 1.2)});')

# ---------------------------------------------------------------- CARTES DE CHAPITRE
for i, (n, titre, t) in enumerate(CHAP):
    gid = f"ch{i}"
    num = "BONUS" if n == "B" else f"#{n}"
    dc = min([b for b in BLOC_T if t + 0.5 < b < t + 2.6] + [t + 2.65]) - t - 0.05
    bloc(gid, t, t + dc, f'<div id="{gid}-n" class="ch-num o0">{num}</div><div id="{gid}-t" class="ch-titre o0">{titre}</div>')
    entre(f"#{gid}-n", t, "opacity: 0, scale: 3.2, rotation: -8", "opacity: 1, scale: 1, rotation: 0", 0.32, "power4.out")
    entre(f"#{gid}-t", t + 0.22, "opacity: 0, clipPath: \"inset(0% 100% 0% 0%)\"", "opacity: 1, clipPath: \"inset(0% 0% 0% 0%)\"", 0.4, "power3.out")
    voile(t - 0.05, t + dc, 0.42)
    son(t, "riser-trailer", 0.22, note=f"montée chapitre {n}")
    son(t, "impact-basse", 0.42, note=f"impact chapitre {n}")
    son(t + 0.22, "swoosh-accent", 0.25, note=f"titre chapitre {n}")
    son(t + 0.3, "deverrouille", 0.25, note=f"case {n} dévoilée")
    flash(t, "#ffffff", 0.7, 0.25)
    rgb(t, 26, 0.25)
    secousse(t + 0.04, 20, 6)
    fuite(t, 1.8, 0.65)

# Ambiances discrètes sous certains plans
for t, nom, v, d in [(mot("CRIMINAL", 168.7), "sirene-police", 0.08, 2.5), (mot("PUSHED", 51.0), "erreur-scifi", 0.15, None),
                     (mot("CONSEQUENCES", 182.2) + 0.2, "tir-echo", 0.12, None),
                     (mot("ALLIGATORS", 119.0), "grillons", 0.1, 2.0), (mot("MASSIVE", 131.1), "drone-scifi", 0.12, 2.5),
                     (mot("PRE-ORDERS", 210.4), "foule-acclame", 0.1, 2.5), (mot("CYBERPUNK", 220.8), "glitch-data", 0.18, None),
                     (mot("GAMING", 250.4), "clavier-bit", 0.12, 1.5), (mot("WAVE", 262.4), "vent-roulement", 0.12, 1.5),
                     (mot("EXPLORATION", 149.6), "vent-roulement", 0.1, 1.8)]:
    son(t, nom, v, d=d, note="ambiance")

# ================================================================ SOUS-TITRES (anglais, mot à mot)
CLES = {"GTA", "6", "VI", "JASON", "LUCIA", "LEONIDA", "VICE", "CITY", "MIAMI", "FLORIDA", "ROCKSTAR", "XBOX", "PS5", "PC",
        "GUINNESS", "CYBERPUNK", "NOVEMBER", "19", "MILLION", "MILLIONS", "DOLLARS", "THIRTEEN", "13", "12", "10", "TWICE",
        "STANDARD", "ULTIMATE", "DISC", "SENSOR", "TOWER", "ALLIGATOR", "212", "GB", "BONUS", "TRAILER", "RECORD",
        "RECORDS", "DEADPOOL", "WOLVERINE", "DELAYED", "LEAKS", "STORAGE", "PRE-LOAD", "MORAL", "CONSEQUENCES", "SPACE"}
groupes, g = [], []
for k, w in enumerate(MOTS):
    g.append(k)
    nxt = MOTS[k + 1] if k + 1 < len(MOTS) else None
    longueur = sum(len(MOTS[i]["text"]) + 1 for i in g)
    fin_phrase = w["text"][-1] in ".,!?…:;"
    if (len(g) >= 3 or fin_phrase or longueur > 15 or nxt is None or nxt["start"] - w["end"] > 0.35
            or (nxt and longueur + len(nxt["text"]) > 18)):
        groupes.append(g)
        g = []
SUBS = []
for gi, g in enumerate(groupes):
    t0 = MOTS[g[0]]["start"]
    t_suiv = MOTS[groupes[gi + 1][0]]["start"] if gi + 1 < len(groupes) else FIN
    t1 = min(t_suiv, MOTS[g[-1]]["end"] + 0.5)
    spans = []
    for i in g:
        txt = MOTS[i]["text"].rstrip(",.;:…")
        cle = propre(txt) in CLES or any(c.isdigit() for c in txt)
        spans.append(f'<span id="w{i}" class="{"k" if cle else ""}">{txt.replace("&", "&amp;")}</span>')
    SUBS.append(f'<div id="sg{gi}" class="clip sub" data-start="{r(t0)}" data-duration="{r(t1 - t0)}" data-track-index="{60 + gi % 2}">'
                f'{" ".join(spans)}</div>')
    j(f'tl.fromTo("#sg{gi}", {{ scale: 0.82, y: 16 }}, {{ scale: 1, y: 0, duration: 0.14, ease: "back.out(2.5)", immediateRender: false }}, {r(t0)});')
    for n_, i in enumerate(g):
        base = "#ff3d8b" if 'class="k"' in spans[n_] else "#ffffff"
        j(f'tl.set("#w{i}", {{ color: "#ffd23f", scale: 1.1 }}, {r(MOTS[i]["start"])});')
        if n_ + 1 < len(g):
            j(f'tl.set("#w{i}", {{ color: "{base}", scale: 1 }}, {r(MOTS[g[n_ + 1]]["start"])});')

# ================================================================ VOILES (fusion des intervalles)
VOILES.sort()
fus = []
for t0, t1, op in VOILES:
    if fus and t0 <= fus[-1][1] + 0.3:
        fus[-1] = [fus[-1][0], max(fus[-1][1], t1), max(fus[-1][2], op)]
    else:
        fus.append([t0, t1, op])
for t0, t1, op in fus:
    j(f'tl.fromTo("#voile", {{ opacity: 0 }}, {{ opacity: {op}, duration: 0.25, ease: "sine.out", immediateRender: false }}, {r(t0)});')
    j(f'tl.to("#voile", {{ opacity: 0, duration: 0.3, ease: "sine.in" }}, {r(t1)});')

# ================================================================ ÉCRITURE
MUSIQUES = [("partie-1-complicated", 0.0, T_CH[3] + 0.5, 0.57, 0.0, 1.0),
            ("partie-2-hip-hop-02", T_CH[3] - 0.5, T_CH[7] + 0.5, 0.61, 1.0, 1.0),
            ("partie-3-need-for-speed", T_CH[7] - 0.5, FIN, 0.54, 1.0, 3.0)]
musiques = [f'<audio id="musique-{k + 1}" src="assets/music/{f}.mp3" data-start="{r(t0)}" data-duration="{r(t1 - t0)}" '
            f'data-volume="{v}"{f" data-fade-in={chr(34)}{fi}{chr(34)}" if fi else ""} data-fade-out="{fo}" data-track-index="{11 + k}"></audio>'
            for k, (f, t0, t1, v, fi, fo) in enumerate(MUSIQUES)]
sons_html, libre = [], []
for k, (t0, nom, v, d, fo, note) in enumerate(sorted(SONS)):
    piste = next((i for i, f in enumerate(libre) if f <= t0), None)
    if piste is None:
        libre.append(0)
        piste = len(libre) - 1
    libre[piste] = t0 + d + 0.01
    fade = f' data-fade-out="{fo}"' if fo else ""
    sons_html.append(f'<audio id="sfx-{k + 1:03d}" src="assets/sfx/{nom}.mp3" data-start="{t0}" data-duration="{d}" data-volume="{v}"{fade} '
                     f'data-track-index="{70 + piste}"></audio><!-- {note} -->')

CSS = (ICI / "tools/style.css").read_text()
NL = "\n"
page = f"""<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <svg width="0" height="0" style="position: absolute">
      <filter id="rgb" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
        <feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r" />
        <feOffset id="rgb-r" in="r" dx="0" dy="0" result="ro" />
        <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g" />
        <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b" />
        <feOffset id="rgb-b" in="b" dx="0" dy="0" result="bo" />
        <feBlend in="ro" in2="g" mode="screen" result="rg" />
        <feBlend in="rg" in2="bo" mode="screen" />
      </filter>
    </svg>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FIN}" data-width="1920" data-height="1080">
      <div id="fond" class="clip" data-start="0" data-duration="{FIN}" data-track-index="0"></div>
      <div id="cadre">
        <div id="rgbw">
          <div id="cam">
{NL.join("            " + v for v in VIDS)}
          </div>
          <div id="teinte"></div>
          <div id="voile"></div>
          <div id="bas"></div>
{NL.join("          " + h for h in OVER)}
        </div>
{NL.join("        " + h for h in GFX)}
      </div>
{NL.join("      " + s for s in SUBS)}
      <div id="vignette"></div>
      <div id="fondu-fin"></div>
      <audio id="voix" src="assets/audio/voix.mp3" data-start="0" data-duration="{r(DUREES_AUDIO_VOIX)}" data-volume="1" data-track-index="10"></audio>
{NL.join("      " + m for m in musiques)}
{NL.join("      " + s for s in sons_html)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{NL.join(JS)}
      tl.set({{}}, {{}}, {FIN});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ICI / "index.html").write_text(page, encoding="utf-8")
nv = sum(1 for z in PLANS if est_video(z[1]))
print(f"GTA 6 écrit : {len(PLANS)} plans ({nv} vidéos, {len(PLANS) - nv} images, {len({z[1] for z in PLANS})} différents), "
      f"{len(SONS)} bruitages, {len(SUBS)} groupes de sous-titres, {len(GFX)} graphiques, fin {FIN} s")
