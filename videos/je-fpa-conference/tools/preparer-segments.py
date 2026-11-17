#!/usr/bin/env python3
"""v3 : banque de plans TOUS DIFFÉRENTS (un moment différent de chaque vidéo, jamais deux fois le même) pour un montage très
dynamique. Chaque plan : 2,2 s, recadré 16:9, agrandi en 1920×1080, débruité, accentué, réchauffé.
Sortie : assets/plans/s-<lettre><n>.mp4 + assets/plans/segments.json (liste dans un ordre qui varie les sources)."""
import json, subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC, OUT = ICI / "assets/medias/Telegram", ICI / "assets/plans"
FILTRE = ("crop=trunc(ih*16/9/2)*2:ih,scale=1920:1080:flags=lanczos,hqdn3d=2:2:4:4,unsharp=5:5:0.9:5:5:0.0,"
          "eq=contrast=1.07:saturation=1.15:gamma=1.03,colorbalance=rs=0.03:bs=-0.03,fps=30")
# source (doublons de fichiers écartés) : débuts des moments retenus
SOURCES = {
    "A": ("VID_20261117_062052_951.mp4.mov", [1, 6, 12]),          # deux étudiantes, question au micro
    "B": ("VID_20261117_062053_247.mp4.mov", [1, 6]),              # intervenante debout face au public
    "C": ("VID_20261117_062053_462.mp4.mov", [1, 5, 10, 15, 20, 25, 30, 35, 40]),  # étudiante au micro
    "D": ("VID_20261117_062053_606.mp4.mov", [2]),
    "E": ("VID_20261117_062053_663.mp4.mov", [1]),                 # intervenante au pupitre
    "F": ("VID_20261117_062105_358.mp4.mov", [3, 12, 22, 32]),     # simulation d'entretien 1
    "H": ("VID_20261117_062105_479.mp4.mov", [3]),
    "I": ("VID_20261117_062105_796.mp4.mov", [3]),
    "J": ("VID_20261117_062105_797.mp4.mov", [2, 12, 20]),         # panel vu de la salle
    "K": ("VID_20261117_062105_824.mp4.mov", [4, 12]),
    "L": ("VID_20261117_062106_101.mp4.mov", [0.5, 8]),            # question au micro, salle
    "M": ("VID_20261117_062106_138.mp4.mov", [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]),  # simulation d'entretien 2
    "N": ("VID_20261117_062127_904.mp4.mov", [2, 9]),              # intervenante de face
    "O": ("VID_20261117_062128_431.mp4.mov", [2, 10, 18]),         # présentation devant les diapositives
    "P": ("VID_20261117_062128_702.mp4.mov", [3, 12, 21]),         # panel à la table
    "Q": ("VID_20261117_062128_719.mp4.mov", [3, 13, 23]),         # intervenante en bleu
    "R": ("VID_20261117_062128_736.mp4.mov", [0.2]),
}
liste = []
for lettre, (f, debuts) in SOURCES.items():
    for n, a in enumerate(debuts):
        nom = f"s-{lettre}{n}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", "2.2", "-i", str(SRC / f), "-an", "-vf", FILTRE,
                        "-c:v", "libx264", "-crf", "15", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-g", "10", str(OUT / f"{nom}.mp4")], check=True)
        liste.append((lettre, nom + ".mp4"))
# ordre qui alterne les sources (jamais deux fois de suite la même)
par = {}
for l, nom in liste:
    par.setdefault(l, []).append(nom)
ordre = []
while any(par.values()):
    for l in sorted(par, key=lambda x: -len(par[x])):
        if par[l] and (not ordre or ordre[-1][0] != l):
            ordre.append((l, par[l].pop(0)))
(OUT / "segments.json").write_text(json.dumps([n for _, n in ordre], indent=0))
print(len(ordre), "plans différents")
