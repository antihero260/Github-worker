#!/usr/bin/env python3
"""Vrais ralentis pour l'aftermovie v2 : les images intermédiaires sont calculées (ffmpeg minterpolate, compensation de mouvement)
sur la vidéo d'origine (848×464), puis le plan est recadré en 16:9, agrandi en 1920×1080, débruité, accentué, réchauffé.
Sortie : assets/plans/lent-<nom>.mp4 (30 i/s)."""
import subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC, OUT = ICI / "assets/medias/Telegram", ICI / "assets/plans"
FINI = ("crop=trunc(ih*16/9/2)*2:ih,scale=1920:1080:flags=lanczos,hqdn3d=2:2:4:4,unsharp=5:5:0.9:5:5:0.0,"
        "eq=contrast=1.06:saturation=1.12:gamma=1.03,colorbalance=rs=0.03:bs=-0.03")
# nom : (fichier, début dans la source, durée source, facteur de ralenti)
LENTS = {
    "groupe": ("VID_20261117_062040_383.mp4.mov", 0.0, 1.1, 3.5),
    "simulation-1": ("VID_20261117_062105_358.mp4.mov", 10.0, 2.0, 2.7),
    "simulation-2": ("VID_20261117_062106_138.mp4.mov", 22.0, 2.0, 2.5),
    "public-micro": ("VID_20261117_062053_462.mp4.mov", 1.0, 2.0, 2.5),
    "intervenante": ("VID_20261117_062128_719.mp4.mov", 5.0, 2.0, 2.5),
    "panel-table": ("VID_20261117_062128_702.mp4.mov", 9.0, 2.0, 2.7),
    "presentation-ek": ("VID_20261117_062128_431.mp4.mov", 13.0, 2.0, 2.5),
    "question-micro": ("VID_20261117_062106_101.mp4.mov", 0.3, 2.0, 2.5),
    "debout-public": ("VID_20261117_062053_247.mp4.mov", 4.0, 2.0, 2.5),
    "question-duo": ("VID_20261117_062052_951.mp4.mov", 2.0, 2.0, 2.5),
}
for nom, (f, a, d, k) in LENTS.items():
    vf = f"setpts={k}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,{FINI}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(d), "-i", str(SRC / f), "-an", "-vf", vf,  # -t AVANT -i : durée de la source
                    "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "15", str(OUT / f"lent-{nom}.mp4")], check=True)
    print("ralenti", nom, round(d * k, 2), "s")
