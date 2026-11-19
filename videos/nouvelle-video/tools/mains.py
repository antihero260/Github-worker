#!/usr/bin/env python3
"""Repère les mains (et le visage) image par image dans le montage, pour accompagner les gestes.
La peau est cherchée en YCrCb dans assets/montage-image.mp4, mais uniquement à l'intérieur de la silhouette détourée
(canal alpha de assets/perso.webm) : le mur beige ne peut pas être pris pour une main.
Visage = la plus grande zone de peau dans le haut de la silhouette ; mains = les autres zones de peau assez grandes, hors visage et cou.
Sortie : assets/mains.json {"fps": 15, "images": [[t, visage_x, visage_y, [[x, y, aire], …]], …]} (pixels 1080×1920),
puis la liste des gestes (périodes où une ou deux mains sont bien visibles) dans assets/gestes.json."""
import json, subprocess
from pathlib import Path
import numpy as np
from scipy import ndimage

ICI = Path(__file__).resolve().parent.parent
w, h, fps = 270, 480, 15
S = 1080 / w


def lire(args):
    vf = f"fps={fps},scale={w}:{h},format=yuv444p" if "-c:v" not in args else f"format=yuva420p,alphaextract,fps={fps},scale={w}:{h},format=gray"
    raw = subprocess.run(["ffmpeg", "-v", "error"] + args + ["-vf", vf, "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return raw


img = lire(["-i", str(ICI / "assets/montage-image.mp4"), "-pix_fmt", "yuv444p"])
alp = lire(["-c:v", "libvpx-vp9", "-i", str(ICI / "assets/perso.webm"), "-pix_fmt", "gray"])
n = min(len(img) // (w * h * 3), len(alp) // (w * h))
v = np.frombuffer(img[: n * w * h * 3], np.uint8).reshape(n, 3, h, w).astype(np.int16)
A = np.frombuffer(alp[: n * w * h], np.uint8).reshape(n, h, w) > 128
yy, xx = np.mgrid[0:h, 0:w]
images, dernier_v = [], (w / 2, h * 0.5)
for k in range(n):
    Y, Cb, Cr = v[k]
    peau = (Cr > 136) & (Cr < 182) & (Cb > 78) & (Cb < 134) & (Y > 20) & (Y < 200) & A[k]
    peau = ndimage.binary_opening(peau, iterations=1)
    lab, nb = ndimage.label(peau)
    if nb == 0:
        images.append([round(k / fps, 3), round(dernier_v[0] * S), round(dernier_v[1] * S), []])
        continue
    tailles = ndimage.sum(peau, lab, range(1, nb + 1))
    centres = ndimage.center_of_mass(peau, lab, range(1, nb + 1))
    # visage : grande zone dont le centre est dans le tiers supérieur de la silhouette
    cand = [(tailles[q], q) for q in range(nb) if centres[q][0] < h * 0.62]
    iv = max(cand)[1] if cand else int(np.argmax(tailles))
    fy, fx = centres[iv]
    dernier_v = (fx, fy)
    mains = []
    for q in range(nb):
        if q == iv or tailles[q] < 120:
            continue
        cy, cx = centres[q]
        if abs(cx - fx) < 40 and fy < cy < fy + 110:   # le cou, sous le visage
            continue
        mains.append([round(cx * S), round(cy * S), int(tailles[q])])
    mains.sort(key=lambda m: -m[2])
    images.append([round(k / fps, 3), round(fx * S), round(fy * S), mains[:2]])
(ICI / "assets/mains.json").write_text(json.dumps({"fps": fps, "images": images}))

# gestes : au moins une main visible pendant ≥ 0,4 s
gestes, k = [], 0
while k < n:
    if images[k][3]:
        q = k
        while q < n and (images[q][3] or (q + 1 < n and images[q + 1][3])):
            q += 1
        if (q - k) / fps >= 0.4:
            pic = max(range(k, q), key=lambda z: sum(m[2] for m in images[z][3]))
            gestes.append({"debut": images[k][0], "fin": images[q - 1][0], "pic": images[pic][0], "mains": images[pic][3]})
        k = q
    k += 1
(ICI / "assets/gestes.json").write_text(json.dumps(gestes, indent=1))
for g in gestes:
    print(f"{g['debut']:6.2f} → {g['fin']:6.2f}  pic {g['pic']:6.2f}  mains {g['mains']}")
