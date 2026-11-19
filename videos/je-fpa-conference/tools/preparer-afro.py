#!/usr/bin/env python3
"""Plans de la version afro (musique de la com) : choisis à la main dans les 18 vidéos et les photos de la conférence,
chacun utilisé une seule fois. Étalonnage plus chaud. Sortie : assets/plans/a-*.mp4 et a-*.jpg."""
import subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC, OUT = ICI / "assets/medias/Telegram", ICI / "assets/plans"
FILTRE = ("crop=trunc(ih*16/9/2)*2:ih,scale=1920:1080:flags=lanczos,hqdn3d=2:2:4:4,unsharp=5:5:0.9:5:5:0.0,"
          "eq=contrast=1.06:saturation=1.18:gamma=1.04,colorbalance=rs=0.06:gs=0.01:bs=-0.06:rm=0.03:bm=-0.03,fps=30")
V = "VID_20261117_0{}.mp4.mov"
PLANS = {  # nom : (vidéo, début, durée)
    "etudiante-micro": ("62053_462", 2, 4), "coralie-public": ("62053_462", 20, 4), "etudiante-micro2": ("62053_462", 38, 4),
    "salle-question": ("62052_951", 4, 4), "intervenante-public": ("62053_247", 2, 4), "coralie-geste": ("62053_606", 2.5, 4),
    "coralie-pupitre": ("62053_663", 1.0, 5), "simulation1": ("62105_358", 10, 4), "simulation1b": ("62105_358", 28, 4),
    "applaudit": ("62105_446", 7.2, 3), "panel-coralie": ("62105_479", 4, 4), "panel-duo": ("62105_797", 10, 4),
    "panel-duo2": ("62105_797", 20, 4), "public-gestes": ("62105_824", 1, 4), "public-gestes2": ("62105_824", 10, 4),
    "question-salle": ("62106_101", 9.5, 3.5), "question-salle2": ("62106_101", 1, 3.5), "simulation2": ("62106_138", 12, 4),
    "coralie-face": ("62127_904", 1, 4), "ek-diapos": ("62128_431", 5, 4), "ek-diapos2": ("62128_431", 20, 4),
    "panel-table": ("62128_702", 9, 4), "panel-table2": ("62128_702", 21, 4), "coralie-bleu": ("62128_719", 6, 4),
    "coralie-bleu2": ("62128_719", 26, 4), "ek-debout": ("62128_736", 0, 2.4),
}
for nom, (v, a, d) in PLANS.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(d), "-i", str(SRC / V.format(v)), "-an", "-vf", FILTRE,
                    "-c:v", "libx264", "-crf", "15", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-g", "10", str(OUT / f"a-{nom}.mp4")], check=True)
PHOTOS = {"salle": "062205_214", "panel-large": "062040_435", "etudiantes": "062052_913", "coralie": "062127_859",
          "salle-rangs": "062128_697", "coralie-etudiantes": "062053_749", "groupe": "062040_411", "groupe-jefpa": "062041_073",
          "ek-table": "062128_593"}
for nom, f in PHOTOS.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC / f"IMG_20261117_{f}.jpg"), "-vf",
                    "scale=iw*1.5:ih*1.5:flags=lanczos,unsharp=5:5:0.7,eq=contrast=1.05:saturation=1.15:gamma=1.04,colorbalance=rs=0.05:bs=-0.05",
                    "-q:v", "2", str(OUT / f"a-{nom}.jpg")], check=True)
print(len(PLANS), "plans vidéo,", len(PHOTOS), "photos")
