#!/usr/bin/env python3
"""Suit le bout des doigts image par image dans une fenêtre du montage (peau sombre sur chemise / mur clair).
Usage : python3 tools/suivre-doigt.py DEBUT FIN  -> assets/montage/doigt.json [[t, x, y], …] (pixels 1080×1920 du montage)."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy import ndimage

ICI = Path(__file__).resolve().parent.parent
a, b = float(sys.argv[1]), float(sys.argv[2])
w, h, fps = 540, 960, 30
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a}", "-t", f"{b - a}", "-i", str(ICI / "assets/montage/parole-net.mp4"),
                      "-vf", f"scale={w}:{h},format=yuv444p", "-f", "rawvideo", "-pix_fmt", "yuv444p", "-"], capture_output=True, check=True).stdout
n = len(raw) // (w * h * 3)
v = np.frombuffer(raw[: n * w * h * 3], np.uint8).reshape(n, 3, h, w).astype(np.int16)
vis = json.loads((ICI / "assets/montage/visage.json").read_text())
pts = []
for k in range(n):
    Y, Cb, Cr = v[k]
    peau = (Cr > 136) & (Cr < 180) & (Cb > 80) & (Cb < 132) & (Y > 25) & (Y < 165)
    peau = ndimage.binary_opening(peau, iterations=2)
    t = a + k / fps
    fx, fy = min(vis, key=lambda e: abs(e[0] - t))[1:]
    fx, fy = fx / 2, fy / 2
    # on retire le visage et le cou (ellipse autour du visage)
    yy, xx = np.mgrid[0:h, 0:w]
    peau &= ~((((xx - fx) / 95) ** 2 + ((yy - fy) / 150) ** 2) < 1)
    peau[: int(h * 0.30)] = False
    lab, nb = ndimage.label(peau)
    if nb == 0:
        pts.append(None); continue
    tailles = ndimage.sum(peau, lab, range(1, nb + 1))
    i = int(np.argmax(tailles)) + 1
    if tailles[i - 1] < 600:
        pts.append(None); continue
    ys, xs = np.nonzero(lab == i)
    top = ys < np.percentile(ys, 4)  # le bout des doigts = le haut de la main
    pts.append([round(t, 3), int(xs[top].mean() * 2), int(ys[top].mean() * 2)])
ok = [p for p in pts if p]
# lissage léger
xs = ndimage.uniform_filter1d(np.array([p[1] for p in ok], float), 3)
ys = ndimage.uniform_filter1d(np.array([p[2] for p in ok], float), 3)
out = [[p[0], int(x), int(y)] for p, x, y in zip(ok, xs, ys)]
(ICI / "assets/montage/doigt.json").write_text(json.dumps(out))
print(len(out), "/", n)
for p in out[::3]:
    print(p)
