#!/usr/bin/env python3
"""Repère les mains qui entrent dans le bas de l'image (pour y faire naître des objets) et suit le visage.
Peau détectée en YCrCb sur une version réduite (270×480, 15 i/s) de assets/montage/parole-net.mp4.
Sorties : assets/montage/gestes.json [[t0, t1, aire, x, y], …] et assets/montage/visage.json [[t, x, y], …] (pixels 1080×1920)."""
import json, subprocess
from pathlib import Path
import numpy as np
from scipy import ndimage

ICI = Path(__file__).resolve().parent.parent
w, h, fps = 270, 480, 15
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ICI / "assets/montage/parole-net.mp4"), "-vf", f"fps={fps},scale={w}:{h},format=yuv444p",
                      "-f", "rawvideo", "-pix_fmt", "yuv444p", "-"], capture_output=True, check=True).stdout
n = len(raw) // (w * h * 3)
v = np.frombuffer(raw[: n * w * h * 3], np.uint8).reshape(n, 3, h, w).astype(np.int16)
Y, Cb, Cr = v[:, 0], v[:, 1], v[:, 2]
peau = (Cr > 138) & (Cr < 178) & (Cb > 80) & (Cb < 130) & (Y > 35)
bas = peau[:, int(h * 0.80):, :]  # bande du bas (sous le col) : les mains
aire = bas.mean((1, 2))
aire = ndimage.uniform_filter1d(aire, 3)
seuil = max(0.02, np.percentile(aire, 60) * 2.5)
gestes, i = [], 0
while i < n:
    if aire[i] > seuil:
        j = i
        while j < n and aire[j] > seuil * 0.7:
            j += 1
        if j - i >= 3:
            k = i + int(np.argmax(aire[i:j]))
            ys, xs = np.nonzero(bas[k])
            gestes.append([round(i / fps, 2), round(j / fps, 2), round(float(aire[i:j].max()), 3),
                           int(np.median(xs) * 1080 / w), int((np.min(ys) + int(h * 0.80) + 8) * 1920 / h)])
        i = j
    else:
        i += 1
visage = []
for k in range(0, n, fps // 2):
    z = peau[k, int(h * 0.25):int(h * 0.62), :]
    ys, xs = np.nonzero(z)
    if len(xs) > 200:
        visage.append([round(k / fps, 2), int(np.median(xs) * 1080 / w), int((np.median(ys) + int(h * 0.25)) * 1920 / h)])
(ICI / "assets/montage/gestes.json").write_text(json.dumps(gestes))
(ICI / "assets/montage/visage.json").write_text(json.dumps(visage))
print(len(gestes), "gestes, seuil", round(seuil, 3))
for g in gestes:
    print(g)
print("visage x", min(x for _, x, _ in visage), max(x for _, x, _ in visage), "y", min(y for *_, y in visage), max(y for *_, y in visage))
