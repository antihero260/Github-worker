#!/usr/bin/env python3
"""Découpage de la vidéo « les 3 niveaux de l'IA » : une seule prise continue de 5 min 24 où chaque phrase est dite plusieurs fois.
Pour chaque phrase on garde la meilleure prise (complète, sans hésitation ; en général la dernière), choisie à la main sur la
transcription mot à mot (assets/transcript-brut.json, Parakeet). Les bords de chaque morceau sont ensuite recalés sur le son :
on coupe dans le silence le plus proche, jamais au milieu d'une syllabe, avec une petite marge.
Sortie : assets/decoupage.json (liste des morceaux) et assets/montage-brut.mp4 (assemblage, image + son)."""
import json, subprocess, wave
from pathlib import Path
import numpy as np

ICI = Path(__file__).resolve().parent.parent
MOTS = json.loads((ICI / "assets/transcript-brut.json").read_text())
MOTS = MOTS if isinstance(MOTS, list) else MOTS["words"]
SRC = ICI / "brut/20261117_144935.mp4"

# (premier mot, dernier mot, texte attendu) — indices de la transcription brute
MORCEAUX = [
    (15, 37, "On entend parler des agents IA partout, mais concrètement, qu'est-ce que c'est et quelle est la différence avec ChatGPT et les automatisations ?"),
    (103, 104, "Premier niveau :"),
    (105, 106, "le prompting."),
    (115, 124, "Vous décrivez quelque chose à ChatGPT, il vous répond,"),
    (153, 159, "mais chaque nouvelle tâche nécessite votre intervention."),
    (164, 167, "Deuxième niveau : l'automatisation IA."),
    (191, 204, "Vous définissez une série d'actions à l'avance. Par exemple, recevoir un mail, le résumer,"),
    (238, 244, "puis enregistrer les informations dans votre CRM."),
    (250, 254, "L'IA exécute simplement votre scénario."),
    (257, 264, "Et enfin, le troisième niveau : les agents IA."),
    (287, 289, "Ici, c'est différent."),
    (310, 313, "Vous donnez un objectif"),
    (339, 346, "et l'agent décide lui-même des étapes pour l'atteindre."),
    (363, 368, "Par exemple, préparer un rendez-vous client."),
    (381, 389, "Il peut consulter vos mails, analyser les anciens échanges,"),
    (408, 416, "vérifier votre calendrier et vous préparer un compte rendu."),
    (427, 435, "Et moi, je trouve que c'est ça, la révolution :"),
    (451, 465, "passer d'une IA qui répond à une IA à laquelle on peut déléguer du travail."),
]

# fins recalées à la main après écoute de l'énergie et vérification image par image (bruit de manipulation, bras qui entre dans le champ,
# syllabe du mot suivant)
# 7 → 8 : on coupe dans le creux entre « résumé » et « puis » (120,03 ; vérifié avec Whisper sur l'extrait) et on reprend
# « Puis enregistrez… votre CRM » dans la prise suivante (attaque de « Puis » à 138,85)
FIN_FORCE = {2: 61.70, 5: 93.45, 7: 120.03, 8: 141.42, 9: 146.90, 10: 155.45, 17: 305.32}
DEBUT_FORCE = {8: 138.80}

# énergie du son (fenêtres de 10 ms)
with wave.open(str(ICI / "assets/voix-16k.wav")) as f:
    sr = f.getframerate()
    a = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
N = sr // 100
rms = np.sqrt(np.convolve(a ** 2, np.ones(N) / N, mode="same"))[::N]
db = 20 * np.log10(rms + 1e-6)
bruit = np.percentile(db, 10)
SEUIL = bruit + 12           # au-dessus : parole


def silence_avant(t, limite):
    """dernier instant calme avant t (sans remonter avant `limite`)"""
    i = int(t * 100)
    j0 = max(int(limite * 100), i - 40)
    while i > j0 and db[i] > SEUIL:
        i -= 1
    return i / 100


def silence_apres(t, limite):
    i = int(t * 100)
    j1 = min(int(limite * 100), i + 60, len(db) - 1)
    while i < j1 and db[i] > SEUIL:
        i += 1
    return i / 100


PAROLE = bruit + 14            # seuil strict : le souffle et le bruit de la pièce ne comptent pas comme de la parole
PAUSE_MIN, PAUSE_GARDE = 0.18, 0.05   # pauses internes ≥ 0,18 s ramenées à 0,10 s (0,05 s de chaque côté)
out = []
for k, (m0, m1, texte) in enumerate(MORCEAUX):
    prec = MOTS[m0 - 1]["end"] if m0 > 0 else 0.0
    suiv = MOTS[m1 + 1]["start"] if m1 + 1 < len(MOTS) else MOTS[m1]["end"] + 1
    d = silence_avant(MOTS[m0]["start"], prec + 0.02)
    f_ = silence_apres(MOTS[m1]["end"], suiv - 0.02)
    debut = max(prec + 0.02, d - 0.06)
    fin = min(suiv - 0.04, f_ + 0.10)
    fin = FIN_FORCE.get(k + 1, fin)
    debut = DEBUT_FORCE.get(k + 1, debut)
    # recalage serré sur la parole réelle (silences « non stratégiques » supprimés)
    i0, i1 = int(debut * 100), int(fin * 100)
    seg = db[i0:i1] - bruit
    parle = np.where(seg > 14)[0]
    if k + 1 not in DEBUT_FORCE:
        debut = round(max(debut, debut + parle[0] / 100 - 0.05), 2)
    fin = round(min(fin, i0 / 100 + parle[-1] / 100 + 0.12), 2)
    # pauses internes
    i0, i1 = int(debut * 100), int(fin * 100)
    calme = (db[i0:i1] - bruit) < 14
    coupes, st = [], None
    for q, c in enumerate(calme):
        if c and st is None:
            st = q
        if (not c) and st is not None:
            if (q - st) / 100 >= PAUSE_MIN and st > 5:
                coupes.append(((i0 + st) / 100 + PAUSE_GARDE, (i0 + q) / 100 - PAUSE_GARDE))
            st = None
    bornes = [debut] + [x for c in coupes for x in c] + [fin]
    morceaux = [(round(bornes[q], 2), round(bornes[q + 1], 2)) for q in range(0, len(bornes), 2)]
    for q, (a_, b_) in enumerate(morceaux):
        out.append({"n": k + 1, "piece": q + 1, "debut": a_, "fin": b_, "texte": texte if q == 0 else "…"})
    print(f"{k + 1:2d}  {debut:7.2f} → {fin:7.2f}  ({fin - debut:4.2f} s, {len(morceaux)} pièce(s))  {texte}")
(ICI / "assets/decoupage.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print("total", round(sum(o["fin"] - o["debut"] for o in out), 2), "s,", len(out), "pièces")

# assemblage : chaque morceau extrait à part (coupe précise à l'image), fondus de 15 ms sur le son pour éviter les clics, puis collage
TMP = ICI / "assets/morceaux"
TMP.mkdir(exist_ok=True)
liste = []
for o in out:
    f = TMP / f"m{o['n']:02d}-{o['piece']}.mp4"
    d = o["fin"] - o["debut"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(o["debut"]), "-i", str(SRC), "-t", f"{d:.3f}",
                    "-af", f"afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015", "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                    "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(f)], check=True)
    liste.append(f"file '{f}'")
(TMP / "liste.txt").write_text("\n".join(liste) + "\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(TMP / "liste.txt"), "-c", "copy",
                str(ICI / "assets/montage-brut.mp4")], check=True)
print("assemblage : assets/montage-brut.mp4")
