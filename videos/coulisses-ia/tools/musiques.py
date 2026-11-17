#!/usr/bin/env python3
"""Prépare les 4 musiques de la montée en tension, calées sur le montage. v7 : les 4 sons TikTok populaires au MEILLEUR RYTHME
(mesuré sur 20 candidats : netteté du beat, kick, régularité — voir SUIVI.md), NON LIBRES, extraits officiels Deezer de 30 s,
non versionnés ; TikTok reconnaît le son à la publication — usage TikTok uniquement :
  1. accroche → game changer : « Sahara » (Hensonn), drop calé sur la fin de l'accroche (tout rentre dans la main)
  2. HyperFrames → possibilités : « METAMORPHOSIS » (Interworld), drop calé sur « HyperFrames »
  3. prix → attention → le modèle : « Murder In My Mind » (Kordhell), drop calé sur « Mais attention »
  4. Opus / Fable → fin : « MONTAGEM URANIUM » (Zaylo), à fond dès Opus"""
import json, subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC = Path("/tmp/claude-0/-home-user-Github-worker/dc3cf4ad-cec2-5288-bb16-b638c74edad6/scratchpad/tiktok2")
M = json.loads((ICI / "assets/mots.json").read_text())
T = lambda i: M[i]["start"]
FIN = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ICI / "assets/montage/parole.mp4")],
                           capture_output=True, text=True).stdout) + 0.6
B = [0.0, T(40), T(99), T(161), FIN]
# (fichier, début dans l'extrait, volume début, volume fin, fondu d'entrée) ; début choisi pour caler drop / sommet sur le bon mot
PLAN = [("c09", round(11.5 - (T(7) + 0.3), 2), 1.0, 1.0, 0.05),
        ("c06", round(11.0 - (T(48) - T(40)), 2), 1.0, 1.0, 0.03),
        ("c05", round(17.0 - (T(137) - T(99)), 2), 1.0, 1.0, 0.05),
        ("c03", 0.0, 1.0, 1.0, 0.03)]

out = []
for k, (mid, debut, v0, v1, fin_entree) in enumerate(PLAN):
    a, b = B[k], B[k + 1]
    d = round(b - a + (0.35 if k < 3 else 0), 3)
    f = ICI / f"assets/music/tension-{k + 1}.mp3"
    af = (f"atrim=start={debut}:duration={d},asetpts=PTS-STARTPTS,acompressor=threshold=-20dB:ratio=3:attack=10:release=200,loudnorm=I=-17:TP=-2:LRA=8,"
          f"volume='{v0}+({v1}-{v0})*t/{d}':eval=frame,afade=t=in:d={fin_entree},afade=t=out:st={max(0, d - 0.35):.3f}:d=0.35")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC / f"{mid}.mp3"), "-af", af, "-ar", "48000", "-b:a", "192k", str(f)], check=True)
    out.append({"fichier": f.name, "source": mid, "debut": round(a, 3), "duree": d})
    print(f.name, round(a, 2), d)
(ICI / "assets/music/tension.json").write_text(json.dumps(out, indent=1))
