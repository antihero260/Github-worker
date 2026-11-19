#!/usr/bin/env python3
"""Prépare les musiques, calées sur le montage. v12 (18 nov. 2026, « mets des musiques captivantes qui matchent bien ») :
deux beats phonk très écoutés sur TikTok ; NON LIBRES, extraits officiels Deezer de 30 s, non versionnés, usage TikTok uniquement.
  1. première image (« comment je faisais… ») → « HyperFrames intervient » : « METAMORPHOSIS » (Interworld), 175 BPM ;
     la vidéo démarre sur le drop (10,975 s), puis la pause (16 temps), puis le drop revient.
  2. « HyperFrames intervient » → fin : « Sahara » (Hensonn), 115 BPM ; démarre sur son drop (11,50 s), bouclé par 32 temps
     (11,50 → 28,19 s).
(v11 Superhero + Timeless : tools/musiques-v11.py ; morceaux cinématiques : tools/musiques-cine.py)"""
import json
import subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC = Path("/tmp/claude-0/-home-user-Github-worker/dc3cf4ad-cec2-5288-bb16-b638c74edad6/scratchpad/beat2")
M = json.loads((ICI / "assets/mots.json").read_text())
T = lambda i: M[i]["start"]
S = 2.64  # début de la vidéo finale (voir tools/construire3.py)
FIN = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ICI / "assets/montage/parole.mp4")],
                           capture_output=True, text=True).stdout) + 0.6


def boucle(src, morceaux, sortie):
    """Colle des tranches [a ; b[ de la source avec des fondus de 30 ms sur les temps."""
    fc, prev = [], None
    for k, (a, b) in enumerate(morceaux):
        fc.append(f"[0:a]atrim={a - 0.015:.3f}:{b + 0.015:.3f},asetpts=PTS-STARTPTS[s{k}]")
    prev = "s0"
    for k in range(1, len(morceaux)):
        fc.append(f"[{prev}][s{k}]acrossfade=d=0.03:c1=tri:c2=tri[x{k}]")
        prev = f"x{k}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", ";".join(fc), "-map", f"[{prev}]", str(sortie)], check=True)


META = SRC / "meta-long.wav"
boucle(SRC / "m1655692952.mp3", [(10.975, 27.445), (10.975, 21.955), (10.975, 21.955)], META)
SAHA = SRC / "sahara-long.wav"
boucle(SRC / "m1543584272.mp3", [(11.50, 28.19)] * 3, SAHA)
B = [S, T(83), FIN]
PLAN = [(META, 0.015, 0.01), (SAHA, 0.015, 0.01)]  # (source, début dans la source, fondu d'entrée)
out = []
for k, (src, debut, fe) in enumerate(PLAN):
    a, b = B[k], B[k + 1]
    d = round(b - a + (0.35 if k == 0 else 0), 3)
    f = ICI / f"assets/music/tension-{k + 1}.mp3"
    fin_fondu = 0.35 if k == 0 else 2.5
    af = (f"atrim=start={debut}:duration={d},asetpts=PTS-STARTPTS,acompressor=threshold=-20dB:ratio=3:attack=10:release=200,loudnorm=I=-17:TP=-2:LRA=8,"
          f"afade=t=in:d={fe},afade=t=out:st={max(0, d - fin_fondu):.3f}:d={fin_fondu}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", af, "-ar", "48000", "-b:a", "192k", str(f)], check=True)
    out.append({"fichier": f.name, "source": src.name, "debut": round(a, 3), "duree": d})
    print(f.name, round(a, 2), d)
(ICI / "assets/music/tension.json").write_text(json.dumps(out, indent=1))
