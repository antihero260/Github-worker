#!/usr/bin/env python3
"""Retouche légère de la bouche, image par image, sur la personne détourée (assets/perso.webm, avec transparence) :
lèvres un peu plus rosées, dents plus blanches (demande de l'utilisateur).
Zone de la bouche : sous le centre du visage repéré par tools/mains.py (assets/mains.json, 15 i/s, interpolé).
Lèvres = pixels nettement plus clairs que la peau autour et un peu rouges ; dents = pixels très clairs et peu colorés
à l'intérieur de la bouche. Masques adoucis (flou) pour une retouche invisible.
Usage : python3 tools/bouche.py essai t1 t2 …   (images avant/après)   |   python3 tools/bouche.py tout   (→ assets/perso-retouche.webm)"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy import ndimage

ICI = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
M = json.loads((ICI / "assets/mains.json").read_text())["images"]
TS = np.array([e[0] for e in M]); FX = np.array([e[1] for e in M], float); FY = np.array([e[2] for e in M], float)
FXs, FYs = ndimage.uniform_filter1d(FX, 5), ndimage.uniform_filter1d(FY, 5)   # centre du visage lissé


OUV, SEUIL_OUV = [], 700   # taille de l'ouverture sombre de la bouche : on ne blanchit que si la bouche est vraiment ouverte


def centre(t):
    return np.interp(t, TS, FXs), np.interp(t, TS, FYs)


def retouche(rgba, t):
    fx, fy = centre(t)
    x0, x1 = int(max(fx - 170, 0)), int(min(fx + 170, W))
    y0, y1 = int(max(fy + 5, 0)), int(min(fy + 210, H))
    roi = rgba[y0:y1, x0:x1, :3].astype(np.float32)
    a = rgba[y0:y1, x0:x1, 3] > 128
    R, G, B = roi[..., 0], roi[..., 1], roi[..., 2]
    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cr = 128 + 0.5 * R - 0.4187 * G - 0.0813 * B
    Cb = 128 - 0.1687 * R - 0.3313 * G + 0.5 * B
    peau = np.median(Y[a]) if a.any() else 80
    # la bouche est ~100 px sous le centre du visage : ellipse douce (rien en dehors, pas de bord visible)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = ((xx - fx) / 120) ** 2 + ((yy - (fy + 108)) / 52) ** 2
    ell = np.clip((1.25 - d) / 0.5, 0, 1)
    # lèvres : plus claires que la peau, un peu rouges, pas blanches ; on ne garde que la plus grande zone
    levres = a & (ell > 0) & (Y > peau + 16) & (Y < 200) & (Cr > 138) & (Cr - Cb > 10)
    levres = ndimage.binary_opening(levres, iterations=1)
    lab, n = ndimage.label(ndimage.binary_closing(levres, iterations=4))
    if n:
        tailles = ndimage.sum(levres, lab, range(1, n + 1))
        k = int(np.argmax(tailles)) + 1
        levres = (lab == k) & levres if tailles[k - 1] > 300 else np.zeros_like(levres)
    levres = ndimage.binary_closing(levres, iterations=3)
    # dents : très claires et peu colorées, à l'intérieur de l'enveloppe des lèvres (entre lèvre du haut et du bas)
    enveloppe = ndimage.binary_fill_holes(ndimage.binary_closing(levres, iterations=10))
    # dents : zones claires collées à l'ouverture sombre de la bouche (entre lèvre du haut et lèvre du bas)
    interieur = ndimage.binary_dilation(enveloppe, iterations=6) & a & (Y < min(peau - 15, 45))
    dents = np.zeros_like(levres)
    OUV.append(int(interieur.sum()))
    if interieur.sum() > SEUIL_OUV:
        sous = np.zeros_like(levres)
        for dy in range(1, 15):            # bande juste sous l'ouverture (dents du haut)
            sous[dy:] |= interieur[:-dy]
        dessus = np.zeros_like(levres)
        for dy in range(1, 8):             # bande juste au-dessus (dents du bas)
            dessus[:-dy] |= interieur[dy:]
        dents = (sous | dessus) & ~interieur & a & (Y > peau + 40) & (ell > 0.2)
        dents = ndimage.binary_opening(dents, iterations=1)
        levres = levres & ~ndimage.binary_dilation(dents, iterations=2)
    ml = ndimage.gaussian_filter(levres.astype(np.float32), 4) * 0.6 * ell
    md = ndimage.gaussian_filter(dents.astype(np.float32), 2) * 0.4 * ell   # éclaircissement doux (la lèvre du bas peut être prise pour des dents)
    # lèvres un peu plus rosées
    out = roi.copy()
    out[..., 0] += ml * 18
    out[..., 1] -= ml * 4
    out[..., 2] += ml * 11
    # dents plus blanches, sans effet artificiel
    lum = 0.299 * out[..., 0] + 0.587 * out[..., 1] + 0.114 * out[..., 2]
    for c, d_ in ((0, 10), (1, 9), (2, 8)):    # blanc légèrement chaud (pas gris)
        out[..., c] = out[..., c] * (1 - md) + np.clip(lum * 1.10 + d_, 0, 255) * md
    rgba[y0:y1, x0:x1, :3] = np.clip(out, 0, 255).astype(np.uint8)
    return rgba


def lecteur(debut=0.0, n=None):
    args = ["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-ss", str(debut), "-i", str(ICI / "assets/perso.webm")]
    if n:
        args += ["-frames:v", str(n)]
    return subprocess.Popen(args + ["-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)


if sys.argv[1] == "essai":
    from PIL import Image
    S = Path("/tmp/claude-0/-home-user-Github-worker/dc3cf4ad-cec2-5288-bb16-b638c74edad6/scratchpad/bouche")
    ims = []
    for t in map(float, sys.argv[2:]):
        p = lecteur(t, 1)
        f = np.frombuffer(p.stdout.read(W * H * 4), np.uint8).reshape(H, W, 4).copy()
        p.wait()
        fx, fy = centre(t)
        box = (int(fx - 200), int(fy - 120), int(fx + 200), int(fy + 260))
        av = Image.fromarray(f).crop(box)
        ap = Image.fromarray(retouche(f, t)).crop(box)
        o = Image.new("RGBA", (800, 380), "white"); o.paste(av, (0, 0)); o.paste(ap, (400, 0)); ims.append(o)
    g = Image.new("RGB", (800, 380 * len(ims)), "white")
    for k, o in enumerate(ims):
        g.paste(o, (0, 380 * k), o)
    g.save(S / "avant-apres.jpg")
    print("ouvertures", OUV)
else:
    p = lecteur()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "20", "-row-mt", "1", "-deadline", "good",
                            "-cpu-used", "4", "-auto-alt-ref", "0", str(ICI / "assets/perso-retouche.webm")], stdin=subprocess.PIPE)
    k = 0
    while True:
        b = p.stdout.read(W * H * 4)
        if len(b) < W * H * 4:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 4).copy()
        enc.stdin.write(retouche(f, k / FPS).tobytes())
        k += 1
        if k % 150 == 0:
            print(k, "images", flush=True)
    enc.stdin.close(); enc.wait(); p.wait()
    print("terminé :", k, "images → assets/perso-retouche.webm")
