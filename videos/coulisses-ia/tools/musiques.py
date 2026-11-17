#!/usr/bin/env python3
"""Prépare les 4 musiques de la montée en tension (Mixkit, licence gratuite sans crédit obligatoire), calées sur le montage.
  1. accroche → game changer : « Silent Descent » (Mixkit 614), suspense qui monte
  2. HyperFrames → possibilités : « Cyberpunk City » (Mixkit 140), énergique
  3. prix → attention → le modèle : « Epical Drums 01 » (Mixkit 676), tambours qui montent (volume en rampe)
  4. Opus / Fable → fin : « I Won't Surrender » (Mixkit 846), final épique
Chaque morceau : extrait, normalisé à −17 LUFS, rampe de volume, fondus courts. Sortie : assets/music/tension-1..4.mp3 + tension.json (bornes)."""
import json, subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC = Path("/tmp/claude-0/-home-user-Github-worker/dc3cf4ad-cec2-5288-bb16-b638c74edad6/scratchpad/mkmus")
M = json.loads((ICI / "assets/mots.json").read_text())
T = lambda i: M[i]["start"]
FIN = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ICI / "assets/montage/parole.mp4")],
                           capture_output=True, text=True).stdout) + 0.6
B = [0.0, T(40), T(99), T(161), FIN]
PLAN = [(614, 44.0, 0.55, 1.0, 0.6), (140, 4.0, 0.9, 1.0, 0.03), (676, 2.0, 0.55, 1.15, 0.2), (846, 64.0, 0.85, 1.1, 0.03)]
out = []
for k, (mid, debut, v0, v1, fin_entree) in enumerate(PLAN):
    a, b = B[k], B[k + 1]
    d = round(b - a + (0.35 if k < 3 else 0), 3)
    f = ICI / f"assets/music/tension-{k + 1}.mp3"
    af = (f"atrim=start={debut}:duration={d},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-2:LRA=11,"
          f"volume='{v0}+({v1}-{v0})*t/{d}':eval=frame,afade=t=in:d={fin_entree},afade=t=out:st={max(0, d - 0.35):.3f}:d=0.35")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC / f"{mid}.mp3"), "-af", af, "-ar", "48000", "-b:a", "192k", str(f)], check=True)
    out.append({"fichier": f.name, "mixkit": mid, "debut": round(a, 3), "duree": d})
    print(f.name, round(a, 2), d)
(ICI / "assets/music/tension.json").write_text(json.dumps(out, indent=1))
