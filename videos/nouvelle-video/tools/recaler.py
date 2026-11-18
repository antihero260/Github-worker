#!/usr/bin/env python3
"""Position RÉELLE de chaque pièce dans le montage (assets/montage-brut.mp4 / voix-montage.m4a).
Chaque pièce extraite par tools/decouper.py dure quelques ms de plus que prévu (arrondi à l'image et aux paquets audio AAC) :
sur 27 pièces, ~0,4 s de dérive à la fin (la fin de « déléguer du travail » était coupée, sous-titres en avance).
On retrouve chaque pièce en corrélant son son brut avec le son du montage autour de la position attendue.
Sortie : assets/positions.json [début réel de chaque pièce dans le montage, …] + durée réelle de la voix."""
import json, subprocess
from pathlib import Path
import numpy as np

ICI = Path(__file__).resolve().parent.parent
SR = 8000
def son(src, extra=()):
    r = subprocess.run(["ffmpeg", "-v", "error", *extra, "-i", str(src), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32)
brut = son(ICI / "brut/20261117_144935.mp4")
mont = son(ICI / "assets/voix-montage.m4a")
dec = json.loads((ICI / "assets/decoupage.json").read_text())
pos, t = [], 0.0
for o in dec:
    seg = brut[int(o["debut"] * SR):int(o["fin"] * SR)]
    a0 = max(0, int((t - 0.3) * SR)); a1 = min(len(mont), int((t + 0.3) * SR) + len(seg))
    zone = mont[a0:a1]
    c = np.correlate(zone - zone.mean(), seg - seg.mean(), mode="valid")
    d = a0 + int(np.argmax(c))
    pos.append(round(d / SR, 4))
    t = d / SR + (o["fin"] - o["debut"])
fin_voix = round(len(mont) / SR, 3)
(ICI / "assets/positions.json").write_text(json.dumps({"pieces": pos, "fin_voix": fin_voix}))
theo = np.cumsum([0] + [o["fin"] - o["debut"] for o in dec[:-1]])
print("dérive max", round(float(np.max(np.array(pos) - theo)), 3), "s ; fin de la voix", fin_voix)
print([round(p - q, 3) for p, q in zip(pos, theo)])
