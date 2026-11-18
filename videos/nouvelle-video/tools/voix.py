#!/usr/bin/env python3
"""Reconstruit la piste voix calée image par image sur le montage (correction du 18 nov.).
Problème : dans assets/montage-brut.mp4, chaque pièce concaténée garde le « préchargement » de son encodage AAC (~21 ms) ;
sur 27 pièces le son prenait jusqu'à ~0,5 s de retard sur les lèvres et la fin (« déléguer du travail ») était coupée.
Ici, chaque pièce est relue dans la prise brute (son exact, échantillon près) et posée sous ses images :
pièce k = image V_k + 1 du montage (V_k = somme des ceil(durée × 30) des pièces précédentes ; +1 : image dupliquée en tête de
assets/montage-image.mp4, vérifié sur les raccords visibles). Fondus de 15 ms aux bords. Sortie : assets/voix-montage.wav
et assets/positions.json (début de chaque pièce, fin de la voix) utilisés par tools/construire.py."""
import json, math, subprocess
from pathlib import Path
import numpy as np

ICI = Path(__file__).resolve().parent.parent
SR, FPS = 48000, 30
r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ICI / "brut/20261117_144935.mp4"), "-vn", "-ac", "2", "-ar", str(SR),
                    "-f", "f32le", "-"], capture_output=True, check=True).stdout
brut = np.frombuffer(r, np.float32).reshape(-1, 2)
dec = json.loads((ICI / "assets/decoupage.json").read_text())
images = [math.ceil((o["fin"] - o["debut"]) * FPS - 1e-6) for o in dec]
debuts = [(1 + sum(images[:k])) / FPS for k in range(len(dec))]
fin = debuts[-1] + (dec[-1]["fin"] - dec[-1]["debut"])
out = np.zeros((int((fin + 0.05) * SR), 2), np.float32)
F = int(0.015 * SR)
for o, t in zip(dec, debuts):
    seg = brut[int(round(o["debut"] * SR)):int(round(o["fin"] * SR))].copy()
    rampe = np.linspace(0, 1, F)[:, None]
    seg[:F] *= rampe; seg[-F:] *= rampe[::-1]
    i = int(round(t * SR))
    out[i:i + len(seg)] += seg
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le",
                str(ICI / "assets/voix-montage.wav")], input=out.tobytes(), check=True)
(ICI / "assets/positions.json").write_text(json.dumps({"pieces": [round(t, 4) for t in debuts], "fin_voix": round(fin, 3)}))
print("pièces", len(dec), "fin de la voix", round(fin, 3), "s (images :", 1 + sum(images), ")")
