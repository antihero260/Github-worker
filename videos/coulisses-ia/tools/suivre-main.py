#!/usr/bin/env python3
"""Suit la main (centre de la paume) image par image dans plusieurs fenêtres du montage.
Usage : python3 tools/suivre-main.py nom:debut:fin [nom:debut:fin …] -> assets/montage/mains.json {nom: [[t, x, y], …]} (pixels 1080×1920).
La main = la plus grande zone de peau hors visage et cou ; si elle sort du cadre, on garde la dernière position connue."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy import ndimage

ICI = Path(__file__).resolve().parent.parent
w, h, fps = 270, 480, 30
vis = json.loads((ICI / "assets/montage/visage.json").read_text())
sortie = json.loads((ICI / "assets/montage/mains.json").read_text()) if (ICI / "assets/montage/mains.json").exists() else {}
for arg in sys.argv[1:]:
    nom, a, b = arg.split(":"); a, b = float(a), float(b)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a}", "-t", f"{b - a}", "-i", str(ICI / "assets/montage/parole-net.mp4"),
                          "-vf", f"scale={w}:{h},format=yuv444p", "-f", "rawvideo", "-pix_fmt", "yuv444p", "-"], capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    v = np.frombuffer(raw[: n * w * h * 3], np.uint8).reshape(n, 3, h, w).astype(np.int16)
    yy, xx = np.mgrid[0:h, 0:w]
    pts, dernier = [], None
    for k in range(n):
        Y, Cb, Cr = v[k]
        peau = (Cr > 136) & (Cr < 180) & (Cb > 80) & (Cb < 132) & (Y > 25) & (Y < 175)
        peau = ndimage.binary_opening(peau, iterations=1)
        t = a + k / fps
        fx, fy = min(vis, key=lambda e: abs(e[0] - t))[1:]
        fx, fy = fx * w / 1080, fy * h / 1920
        peau &= ~((((xx - fx) / 48) ** 2 + ((yy - fy) / 75) ** 2) < 1)
        peau[: int(h * 0.30)] = False
        lab, nb = ndimage.label(peau)
        pos = None
        if nb:
            tailles = ndimage.sum(peau, lab, range(1, nb + 1))
            i = int(np.argmax(tailles)) + 1
            if tailles[i - 1] > 150:
                ys, xs = np.nonzero(lab == i)
                pos = (xs.mean() * 1080 / w, np.percentile(ys, 30) * 1920 / h)
        if pos is None:
            pos = dernier
        if pos is not None:
            pts.append([round(t, 3), pos[0], pos[1]]); dernier = pos
    if not pts:
        pts = [[a, 300.0, 1650.0], [b, 300.0, 1650.0]]
    xs = ndimage.uniform_filter1d(np.array([p[1] for p in pts]), 5)
    ys = ndimage.uniform_filter1d(np.array([p[2] for p in pts]), 5)
    sortie[nom] = [[p[0], int(x), int(y)] for p, x, y in zip(pts, xs, ys)]
    print(nom, len(pts), "points ; x", int(xs.min()), int(xs.max()), "y", int(ys.min()), int(ys.max()))
(ICI / "assets/montage/mains.json").write_text(json.dumps(sortie))
