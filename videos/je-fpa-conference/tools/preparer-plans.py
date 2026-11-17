#!/usr/bin/env python3
"""Prépare les plans de l'aftermovie à partir des vidéos et photos Telegram (848×464 / 1280×960) :
extrait, recadre en 16:9, agrandit en 1920×1080 (lanczos), débruite, accentue, réchauffe légèrement les couleurs.
Sortie : assets/plans/<nom>.mp4 (vidéos, 30 i/s) et assets/plans/<nom>.jpg (photos)."""
import subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC, OUT = ICI / "assets/medias/Telegram", ICI / "assets/plans"
OUT.mkdir(parents=True, exist_ok=True)
FILTRE = ("crop=trunc(ih*16/9/2)*2:ih,scale=1920:1080:flags=lanczos,hqdn3d=2:2:4:4,"
          "unsharp=5:5:0.9:5:5:0.0,eq=contrast=1.06:saturation=1.12:gamma=1.03,colorbalance=rs=0.03:bs=-0.03")
# nom : (fichier, début, durée)
VIDEOS = {
    "question-duo": ("VID_20261117_062052_951.mp4.mov", 2.0, 4),
    "public-micro": ("VID_20261117_062053_462.mp4.mov", 0.8, 4),
    "public-micro-2": ("VID_20261117_062053_462.mp4.mov", 38.0, 4),
    "debout-public": ("VID_20261117_062053_247.mp4.mov", 4.0, 4),
    "simulation-1": ("VID_20261117_062105_358.mp4.mov", 9.0, 4),
    "simulation-2": ("VID_20261117_062106_138.mp4.mov", 20.0, 4),
    "panel-large": ("VID_20261117_062105_797.mp4.mov", 8.0, 4),
    "question-micro": ("VID_20261117_062106_101.mp4.mov", 0.3, 4),
    "presentation-ek": ("VID_20261117_062128_431.mp4.mov", 12.0, 4),
    "panel-table": ("VID_20261117_062128_702.mp4.mov", 8.5, 4),
    "intervenante": ("VID_20261117_062128_719.mp4.mov", 4.0, 4),
    "intervenante-face": ("VID_20261117_062127_904.mp4.mov", 2.5, 4),
}
PHOTOS = {
    "groupe-1": "IMG_20261117_062040_552.jpg", "groupe-2": "IMG_20261117_062041_051.jpg", "groupe-3": "IMG_20261117_062040_605.jpg",
    "panel-photo": "IMG_20261117_062127_967.jpg", "salle-photo": "IMG_20261117_062128_697.jpg", "micro-photo": "IMG_20261117_062052_913.jpg",
    "intervenante-photo": "IMG_20261117_062127_859.jpg",
}
for nom, (f, a, d) in VIDEOS.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-i", str(SRC / f), "-t", str(d), "-an", "-vf", FILTRE + ",fps=30",
                    "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "15", str(OUT / f"{nom}.mp4")], check=True)
    print("vidéo", nom)
for nom, f in PHOTOS.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC / f), "-vf", "scale=2400:-1:flags=lanczos,hqdn3d=1.5:1.5:0:0,unsharp=5:5:0.8:5:5:0.0,"
                    "eq=contrast=1.05:saturation=1.1,colorbalance=rs=0.03:bs=-0.03", "-q:v", "2", str(OUT / f"{nom}.jpg")], check=True)
    print("photo", nom)
