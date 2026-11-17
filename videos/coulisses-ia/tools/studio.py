#!/usr/bin/env python3
"""Rendu « studio » de la personne : lumière qui débouche les ombres, couleurs naturelles, détourage propre,
posée sur un fond de studio uni et sombre (une teinte par passage). Pas de halo ni de contour lumineux.

Fonctions réutilisées par tools/composer-studio.py (vidéo entière) ; lancé seul, fait un essai sur des images PNG."""
import sys
import numpy as np
from scipy import ndimage

H, W = 1920, 1080

# fonds de studio : (couleur des bords, couleur de la tache de lumière derrière la personne)
FONDS = {
    "nuit":     ((10, 14, 24), (40, 56, 84)),
    "terre":    ((22, 13, 10), (78, 48, 36)),
    "sarcelle": ((8, 20, 22), (30, 70, 74)),
    "graphite": ((14, 15, 18), (52, 56, 64)),
    "indigo":   ((16, 13, 30), (58, 50, 96)),
    "bordeaux": ((24, 8, 10), (84, 28, 34)),
    "ardoise":  ((12, 16, 24), (48, 62, 84)),
    "petrole":  ((8, 18, 26), (30, 64, 86)),
}


def fond_studio(nom, graine=0):
    """Fond peint de studio : uni, sombre, une tache de lumière douce derrière la tête, légère texture de toile."""
    bord, centre = (np.array(c, np.float32) / 255 for c in FONDS[nom])
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - 540) / 620) ** 2 + ((y - 820) / 900) ** 2)
    k = np.clip(1 - d * 0.8, 0, 1) ** 1.2
    img = bord[None, None] * (1 - k[..., None]) + centre[None, None] * k[..., None]
    rng = np.random.default_rng(graine)
    tache = ndimage.gaussian_filter(rng.standard_normal((H // 8, W // 8)).astype(np.float32), 6)
    tache = ndimage.zoom(tache / (np.abs(tache).max() + 1e-6), 8, order=1)[:H, :W]
    img *= (1 + 0.10 * tache)[..., None]
    return np.clip(img, 0, 1)


def flou(a, s):
    """flou gaussien rapide (calculé à 1/4 de la résolution)"""
    p = a[::4, ::4]
    p = ndimage.gaussian_filter(p, s / 4)
    return ndimage.zoom(p, 4, order=1)[: a.shape[0], : a.shape[1]]


def detourage(alpha, prec=None):
    """bord net mais doux : on rentre d'1 px, on adoucit, on lisse dans le temps"""
    a = alpha.astype(np.float32) / 255
    a = ndimage.grey_erosion(a, size=(5, 5))
    a = ndimage.gaussian_filter(a, 1.2)
    a = np.clip((a - 0.04) / 0.92, 0, 1)
    if prec is not None:
        a = 0.65 * a + 0.35 * prec
    return a


def eclairer(rgb, a):
    """rgb uint8 -> float 0..1 ; lumière de face qui efface les ombres + couleurs naturelles"""
    c = rgb.astype(np.float32) / 255
    # 1. balance des blancs : la pièce éclaire en jaune ; on ramène vers le neutre (gains mesurés sur la chemise grise)
    c *= np.array([1.0, 1.0, 1.04], np.float32)
    lum = 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]
    # 2. débouchage des ombres : gain local, plus fort là où la zone est sombre (dessous des yeux, cou, joues)
    loc = flou(lum * a + 0.35 * (1 - a), 22)
    gain = np.clip((0.40 / (loc + 0.03)) ** 0.55, 1.0, 2.1)
    # 3. lumière douce de face (boîte à lumière virtuelle centrée sur le visage, très large)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    face = np.exp(-(((x - 540) / 520) ** 2 + ((y - 900) / 700) ** 2))
    gain = 1 + (gain - 1) * (0.35 + 0.65 * face)  # la lumière porte surtout sur le visage, moins sur la chemise
    gain *= 1 + 0.14 * face
    c = c * gain[..., None]
    # 4. courbe douce : on garde du contraste, on compresse les reflets (front qui brille)
    c = np.where(c > 0.72, 0.72 + (c - 0.72) * 0.55, c)
    c = c ** 0.96
    # 5. saturation naturelle (légère)
    g = (0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2])[..., None]
    c = g + (c - g) * 1.12
    return np.clip(c, 0, 1)


def decontaminer(rgb, alpha):
    """retire la couleur du mur (crème) qui bave sur les contours : F = (I - (1 - a) * B) / a, B estimé autour"""
    c = rgb.astype(np.float32) / 255
    a = alpha.astype(np.float32) / 255
    m = (a < 0.05).astype(np.float32)
    B = np.stack([flou(c[..., i] * m, 18) for i in range(3)], -1) / (flou(m, 18)[..., None] + 1e-3)
    F = (c - (1 - a[..., None]) * B) / np.maximum(a, 0.25)[..., None]
    bord = (a > 0.02) & (a < 0.98)
    c[bord] = np.clip(F[bord], 0, 1)
    return (c * 255).astype(np.uint8)


def nettete(p, a):
    """accentuation douce (masque flou) sur la personne seulement"""
    b = np.stack([ndimage.gaussian_filter(p[..., i], 1.3) for i in range(3)], -1)
    return np.clip(p + 0.9 * (p - b) * a[..., None], 0, 1)


def composer(rgb, alpha, fond, prec=None):
    rgb = decontaminer(rgb, alpha)
    a = detourage(alpha, prec)
    p = nettete(eclairer(rgb, a), a)
    # bord : le mur clair déborde sur les contours -> on assombrit la frange (pas de liseré clair)
    p *= (0.7 + 0.3 * np.clip(a * 1.15, 0, 1))[..., None]
    out = p * a[..., None] + fond * (1 - a[..., None])
    return out, a


if __name__ == "__main__":
    from PIL import Image
    d = sys.argv[1]
    noms = list(FONDS)
    for k, t in enumerate(sys.argv[2:]):
        rgb = np.array(Image.open(f"{d}/rgb_{t}.png").convert("RGB"))
        al = np.array(Image.open(f"{d}/a_{t}.png").convert("L"))
        out, _ = composer(rgb, al, fond_studio(noms[k * 2 % len(noms)], k))
        Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(f"{d}/studio_{t}.png")
