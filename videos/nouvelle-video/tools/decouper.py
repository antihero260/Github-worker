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
    (191, 205, "Vous définissez une série d'actions à l'avance. Par exemple, recevoir un mail, le résumer, puis"),
    (239, 244, "enregistrer les informations dans votre CRM."),
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
# 7 → 8 : « résumé, puis » est enchaîné sans pause ; on coupe dans le creux après « puis » (120,03) et on reprend « enregistrez… votre CRM »
# de la prise suivante dans le creux entre « Puis » et « enregistrez » (139,16)
FIN_FORCE = {2: 61.70, 5: 93.45, 7: 120.03, 8: 141.42, 9: 146.90, 10: 155.45, 17: 305.32}
DEBUT_FORCE = {8: 139.16}

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


out = []
for k, (m0, m1, texte) in enumerate(MORCEAUX):
    prec = MOTS[m0 - 1]["end"] if m0 > 0 else 0.0
    suiv = MOTS[m1 + 1]["start"] if m1 + 1 < len(MOTS) else MOTS[m1]["end"] + 1
    d = silence_avant(MOTS[m0]["start"], prec + 0.02)
    f_ = silence_apres(MOTS[m1]["end"], suiv - 0.02)
    debut = max(prec + 0.02, d - 0.06)        # petite marge avant l'attaque
    fin = min(suiv - 0.04, f_ + 0.10)         # et après la dernière syllabe (le souffle)
    fin = FIN_FORCE.get(k + 1, fin)
    debut = DEBUT_FORCE.get(k + 1, debut)
    out.append({"n": k + 1, "debut": round(debut, 2), "fin": round(fin, 2), "texte": texte,
                "mots": " ".join(MOTS[i]["text"] for i in range(m0, m1 + 1))})
    print(f"{k + 1:2d}  {debut:7.2f} → {fin:7.2f}  ({fin - debut:4.2f} s)  {texte}")
(ICI / "assets/decoupage.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print("total", round(sum(o["fin"] - o["debut"] for o in out), 2), "s")

# assemblage : chaque morceau extrait à part (coupe précise à l'image), fondus de 15 ms sur le son pour éviter les clics, puis collage
TMP = ICI / "assets/morceaux"
TMP.mkdir(exist_ok=True)
liste = []
for o in out:
    f = TMP / f"m{o['n']:02d}.mp4"
    d = o["fin"] - o["debut"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(o["debut"]), "-i", str(SRC), "-t", f"{d:.3f}",
                    "-af", f"afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015", "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                    "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(f)], check=True)
    liste.append(f"file '{f}'")
(TMP / "liste.txt").write_text("\n".join(liste) + "\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(TMP / "liste.txt"), "-c", "copy",
                str(ICI / "assets/montage-brut.mp4")], check=True)
print("assemblage : assets/montage-brut.mp4")
