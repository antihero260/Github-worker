#!/usr/bin/env python3
"""Prépare les musiques, calées sur le montage. v10 : DEUX morceaux cinématiques seulement (demande de l'utilisateur) ;
NON LIBRES, extraits officiels Deezer de 30 s, non versionnés ; usage TikTok uniquement :
  1. accroche → « HyperFrames intervient » : « Time » (Hans Zimmer, Inception), montée en puissance
  2. « HyperFrames intervient » → fin : « Victory » (Two Steps From Hell), 120 BPM ; l'extrait est prolongé en bouclant
     10 mesures au temps près (temps 9 → 49 : 4,540 s → 24,543 s, même harmonie) pour couvrir les 43 s.
(v9, quatre morceaux rap : tools/musiques-v9.py)"""
import json, subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC = Path("/tmp/claude-0/-home-user-Github-worker/dc3cf4ad-cec2-5288-bb16-b638c74edad6/scratchpad/cine")
M = json.loads((ICI / "assets/mots.json").read_text())
T = lambda i: M[i]["start"]
FIN = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ICI / "assets/montage/parole.mp4")],
                           capture_output=True, text=True).stdout) + 0.6
B = [0.0, T(83), FIN]
TMP = SRC / "victory-long.wav"
# Victory prolongé : [0 ; 24,543[ + [4,540 ; 30[ avec un fondu de 40 ms sur le temps
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC / "c05.mp3"), "-filter_complex",
                "[0:a]atrim=0:24.563,asetpts=PTS-STARTPTS[a];[0:a]atrim=4.52,asetpts=PTS-STARTPTS[b];[a][b]acrossfade=d=0.04:c1=tri:c2=tri",
                str(TMP)], check=True)
PLAN = [(SRC / "c01.mp3", 0.0, 0.6), (TMP, 0.0, 0.02)]  # (source, début dans la source, fondu d'entrée)
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
for vieux in (ICI / "assets/music").glob("tension-[34].mp3"):
    vieux.unlink()
(ICI / "assets/music/tension.json").write_text(json.dumps(out, indent=1))
