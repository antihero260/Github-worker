#!/usr/bin/env python3
"""Complète assets/sfx/pics.json : pour chaque bruitage, l'instant du pic (s) et la durée utile (s)."""
import json, subprocess
from pathlib import Path
import numpy as np

SFX = Path(__file__).resolve().parent.parent / "assets/sfx"
f = SFX / "pics.json"
P = json.loads(f.read_text()) if f.exists() else {}
for mp3 in sorted(SFX.glob("*.mp3")):
    if mp3.stem in P:
        continue
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.abs(np.frombuffer(raw, np.int16).astype(np.float32))
    env = np.convolve(a, np.ones(80) / 80, mode="same")
    pic = float(np.argmax(env)) / 8000
    seuil = env.max() * 0.02
    fin = float(np.nonzero(env > seuil)[0][-1]) / 8000 if (env > seuil).any() else len(a) / 8000
    P[mp3.stem] = {"pic": round(pic, 2), "duree": round(min(len(a) / 8000, fin + 0.05), 2)}
    print(mp3.stem, P[mp3.stem])
f.write_text(json.dumps(P, ensure_ascii=False, indent=0))
