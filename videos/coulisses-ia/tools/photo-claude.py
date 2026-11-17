#!/usr/bin/env python3
"""Photo de l'utilisateur retravaillée en 4K vertical (2160×3840) : fond sombre et lumineux, logo Claude en 3D lumineux
qui flotte dans le creux de la main et éclaire la main et le visage.
Entrées : la photo détourée (hyperframes remove-background) et le logo rendu en PNG. Sortie : PNG + JPG.
Usage : python3 tools/photo-claude.py <detoure.png> <logo.png> <sortie-sans-extension> [3d | plat | plat-lumineux]"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

W, H = 2160, 3840
S = 1.1                      # agrandissement de la photo d'origine (2556×3408)
X0, Y0 = 392, H - round(3408 * S)   # recadrage : visage centré, bas de la photo collé au bas de l'image
LX, LY, LS = 521, 2544, 600   # au creux de la main, derrière l'index (x_final = 1,1·x − 392, y_final = 91 + 1,1·y)  # centre et taille du logo (dans le creux de la main)
rng = np.random.default_rng(7)
MODE = sys.argv[4] if len(sys.argv) > 4 else "3d"
# "3d" : logo en relief lumineux + étincelles ; "plat" : vrai logo, sans brillance ; "plat-lumineux" : vrai logo qui brille, sans aucune particule
PLAT = MODE in ("plat", "plat-lumineux")
L = 1.0 if MODE in ("3d", "plat-lumineux") else 0.0   # intensité de ce qui « brille » autour du logo
PARTICULES = MODE == "3d"


def flou(a, s):
    """flou gaussien rapide : calculé à 1/4 de la résolution puis remis à l'échelle"""
    if s < 6:
        return ndimage.gaussian_filter(a, (s, s, 0) if a.ndim == 3 else s)
    f = 4
    petit = a[::f, ::f]
    b = ndimage.gaussian_filter(petit, (s / f, s / f, 0) if a.ndim == 3 else s / f)
    z = (f, f, 1) if a.ndim == 3 else (f, f)
    out = ndimage.zoom(b, z, order=1)
    return out[:a.shape[0], :a.shape[1]] if out.shape[0] >= a.shape[0] else np.pad(out, [(0, a.shape[0] - out.shape[0]), (0, a.shape[1] - out.shape[1])] + ([(0, 0)] if a.ndim == 3 else []), mode="edge")


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def radial(cx, cy, rx, ry=None, p=2.0):
    ry = ry or rx
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1 - d, 0, 1) ** p


# ------------------------------------------------------------------ fond sombre et lumineux
ORANGE = np.array([1.0, 0.50, 0.30], np.float32)
BLEU = np.array([0.22, 0.38, 0.95], np.float32)
VIOLET = np.array([0.45, 0.25, 0.85], np.float32)
fond = np.zeros((H, W, 3), np.float32) + np.array([0.012, 0.016, 0.03], np.float32)
fond += radial(1150, 1350, 1500, 1300, 1.6)[..., None] * BLEU * 0.30
fond += radial(1700, 700, 900, 900, 2.0)[..., None] * VIOLET * 0.22
fond += radial(LX, LY, 1300, 1300, 2.2)[..., None] * ORANGE * {"3d": 0.55, "plat": 0.10, "plat-lumineux": 0.40}[MODE]
# rayons de lumière qui partent du logo
ang = np.arctan2(yy - LY, xx - LX)
dist = np.sqrt((xx - LX) ** 2 + (yy - LY) ** 2)
rayons = (0.5 + 0.5 * np.sin(ang * 9 + 0.6)) ** 6 * 0.6 + (0.5 + 0.5 * np.sin(ang * 23 + 1.9)) ** 10 * 0.4
rayons *= np.exp(-dist / 1500) * np.clip(dist / 250, 0, 1)
fond += rayons[..., None] * ORANGE * 0.22 * PARTICULES
# particules de lumière (bokeh)
bokeh = np.zeros((H, W, 3), np.float32)
for _ in range(90):
    cx, cy = rng.uniform(0, W), rng.uniform(0, H * 0.75)
    r = rng.uniform(10, 46)
    c = ORANGE if rng.random() < 0.55 else (BLEU if rng.random() < 0.6 else VIOLET)
    k = radial(cx, cy, r, r, 0.6) * rng.uniform(0.25, 0.8)
    bokeh += k[..., None] * c
fond += flou(bokeh, 6) * 0.9 * PARTICULES
tex = flou(rng.standard_normal((H // 4, W // 4)).astype(np.float32), 8)
tex = ndimage.zoom(tex / (np.abs(tex).max() + 1e-6), 4, order=1)[:H, :W]
fond *= (1 + 0.12 * tex)[..., None]

# ------------------------------------------------------------------ la personne
src = Image.open(sys.argv[1]).convert("RGBA")
src = src.resize((round(src.width * S), round(src.height * S)), Image.LANCZOS)
src = src.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
toile = Image.new("RGBA", (W, H), (0, 0, 0, 0))
toile.paste(src, (-X0, Y0), src)
p = np.asarray(toile).astype(np.float32) / 255
rgb, a = p[..., :3], p[..., 3]
a = np.clip((ndimage.gaussian_filter(a, 1.2) - 0.08) / 0.84, 0, 1)        # bord net mais doux
# bords décontaminés (le mur beige de la photo d'origine ne doit pas déborder)
bord = np.clip(1 - a, 0, 1) * (a > 0.02)
rgb = rgb * (1 - 0.6 * bord[..., None])
# étalonnage : un peu plus sombre et plus contrasté, les blancs du t-shirt adoucis
lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
rgb = rgb * 0.86
haut = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None]
rgb = rgb * (1 - 0.30 * haut) + (rgb * np.array([0.82, 0.86, 1.0], np.float32)) * 0.30 * haut
rgb = np.clip((rgb - 0.5) * 1.10 + 0.5 - 0.02, 0, 1)
# lumière chaude du logo sur la main, le visage et le t-shirt
chaud = np.exp(-((xx - LX) ** 2 + (yy - LY) ** 2) / (2 * 620.0 ** 2))
chaud2 = np.exp(-((xx - LX) ** 2 + (yy - LY) ** 2) / (2 * 1250.0 ** 2))
rgb = rgb * (1 + L * (chaud * 1.15 + chaud2 * 0.35)[..., None] * (ORANGE - 0.25))
# liseré bleu froid sur les contours (séparation avec le fond), plus fort à droite et en haut
interieur = ndimage.gaussian_filter(a, 14)
lisere = np.clip(a - interieur, 0, 1) * 2.4
dirn = np.clip(0.55 + 0.45 * (xx - 1080) / 1080, 0.15, 1.0) * np.clip(1.2 - yy / H, 0.3, 1)
rgb = rgb + (lisere * dirn)[..., None] * BLEU * 0.9
img = fond * (1 - a[..., None]) + np.clip(rgb, 0, 1.4) * a[..., None]
PERSO, ALPHA = np.clip(rgb, 0, 1.4), a.copy()
# doigts qui passent DEVANT le logo (pouce, index, deux doigts de droite, dos de la main) : polygones relevés sur la photo d'origine
import json
from PIL import ImageDraw
POLYS = json.loads('''{"pouce": [[330,2120],[385,2092],[440,2118],[490,2140],[525,2250],[565,2380],[650,2490],[600,2580],[520,2580],[460,2480],[410,2330],[360,2230]],
 "index": [[778,2050],[812,2030],[860,2035],[888,2080],[892,2200],[880,2320],[868,2430],[790,2470],[715,2450],[712,2330],[740,2190],[760,2100]],
 "droite": [[1010,2560],[1060,2440],[1130,2350],[1180,2290],[1215,2240],[1262,2215],[1300,2245],[1318,2195],[1360,2185],[1392,2240],[1392,2330],[1370,2430],[1320,2540],[1220,2620],[1080,2640]],
 "dos": [[560,2440],[650,2470],[740,2455],[870,2425],[960,2470],[1030,2530],[1060,2620],[1000,2760],[820,2840],[640,2800],[520,2680],[500,2560]]}''')
mq = Image.new("L", (W, H), 0)
dm = ImageDraw.Draw(mq)
for pts in POLYS.values():
    dm.polygon([(x * S - X0, y * S + Y0) for x, y in pts], fill=255)
DEVANT = ndimage.gaussian_filter(np.asarray(mq).astype(np.float32) / 255, 2.5) * ALPHA

# ------------------------------------------------------------------ logo Claude en 3D lumineux
logo = Image.open(sys.argv[2]).convert("RGBA")
bb = logo.getbbox()
logo = logo.crop(bb).resize((LS, round(LS * (bb[3] - bb[1]) / (bb[2] - bb[0]))), Image.LANCZOS)
if not PLAT:
    logo = logo.rotate(-12, resample=Image.BICUBIC, expand=True)
    logo = logo.resize((logo.width, round(logo.height * 0.86)), Image.LANCZOS)   # légèrement couché vers nous
la = np.asarray(logo).astype(np.float32)[..., 3] / 255
lh, lw = la.shape
ox, oy = LX - lw // 2, LY - lh // 2


def poser(couche_rgb, couche_a, dx=0, dy=0):
    global img
    y0, x0 = oy + dy, ox + dx
    sub = img[y0:y0 + lh, x0:x0 + lw]
    sub[:] = sub * (1 - couche_a[..., None]) + couche_rgb * couche_a[..., None]


# lueurs larges (avant de poser le logo, pour qu'il reste net et bien orange)
gl = np.zeros((H, W), np.float32)
gl[oy:oy + lh, ox:ox + lw] = la
for s_, k_ in (((40, 0.6), (100, 0.7), (240, 0.6)) if MODE == "3d" else ((30, 0.45), (90, 0.45), (220, 0.4))):
    g = flou(gl, s_)
    g = g / (g.max() + 1e-6)
    img += g[..., None] * ORANGE * k_ * L
# halo sous le logo, posé sur la paume
img += radial(LX + 10, LY + lh * 0.45, lw * 0.75, lh * 0.30, 1.5)[..., None] * ORANGE * 0.6 * L
AVANT_LOGO = img.copy()   # l'image juste avant de poser le logo : les doigts « de devant » seront repris d'ici (raccords invisibles)
# épaisseur (extrusion) : copies décalées de plus en plus sombres, de l'arrière vers l'avant
PROF = 0 if PLAT else 46
for i in range(PROF, 0, -1):
    t = i / PROF
    c = np.array([0.72, 0.28, 0.15], np.float32) * (1 - t) + np.array([0.22, 0.07, 0.04], np.float32) * t
    poser(np.broadcast_to(c, (lh, lw, 3)), la, round(i * 0.35), round(i * 0.95))
# face avant : dégradé + biseau éclairé en haut à gauche
gy, gx = np.mgrid[0:lh, 0:lw].astype(np.float32)
grad = np.clip(1 - (gx / lw * 0.55 + gy / lh * 0.75), 0, 1)
face = np.array([0.93, 0.42, 0.22], np.float32) * (1 - grad[..., None]) + np.array([1.0, 0.70, 0.46], np.float32) * grad[..., None]
coeur = np.clip(1 - np.sqrt(((gx - lw / 2) / (lw * 0.42)) ** 2 + ((gy - lh / 2) / (lh * 0.42)) ** 2), 0, 1) ** 1.5
face = face + coeur[..., None] * np.array([0.35, 0.28, 0.2], np.float32)   # cœur lumineux : le logo émet de la lumière
lisse = ndimage.gaussian_filter(la, 5)
ny, nx = np.gradient(lisse)
biseau = np.clip(-(nx * -0.7 + ny * -0.7) * 9, -1, 1)
face = face * (1 + 0.35 * biseau[..., None]) + np.clip(biseau, 0, 1)[..., None] * 0.35
reflet = np.clip(1 - np.sqrt(((gx - lw * 0.35) / (lw * 0.35)) ** 2 + ((gy - lh * 0.3) / (lh * 0.25)) ** 2), 0, 1) ** 2
face = face + reflet[..., None] * 0.25
if MODE == "plat":
    face = np.broadcast_to(np.array([217, 119, 87], np.float32) / 255, (lh, lw, 3))   # la couleur officielle du logo Claude
elif MODE == "plat-lumineux":
    # le vrai logo, plat, mais qui émet de la lumière : orange vif sur les bords, presque blanc au cœur des branches
    interieur = ndimage.gaussian_filter(la, 6) * la * 0.65
    face = np.array([1.0, 0.50, 0.27], np.float32) * (1 - interieur[..., None]) + np.array([1.3, 0.9, 0.66], np.float32) * interieur[..., None]
poser(np.clip(face, 0, 1.4), la)
# fine lueur de contour par-dessus (le logo « émet » sans être brûlé)
g = flou(gl, 12)
contour = np.clip(g / (g.max() + 1e-6) - gl * 0.85, 0, 1)
img += contour[..., None] * ORANGE * 1.1 * L
# étincelles en étoile autour du logo
for _ in range(14 if PARTICULES else 0):
    a_ = rng.uniform(0, 2 * np.pi)
    r_ = rng.uniform(lw * 0.55, lw * 1.25)
    cx, cy = LX + np.cos(a_) * r_, LY + np.sin(a_) * r_ * 0.8
    t_ = rng.uniform(0.5, 1.0)
    croix = (np.exp(-((xx - cx) / 2.5) ** 2 - ((yy - cy) / 40) ** 2) + np.exp(-((xx - cx) / 40) ** 2 - ((yy - cy) / 2.5) ** 2)) * 0.6
    point = radial(cx, cy, 14, 14, 1.5) * 1.2
    img += ((croix + point) * t_)[..., None] * np.array([1.0, 0.8, 0.65], np.float32)

# ------------------------------------------------------------------ la main tient le logo : les doigts repassent devant, rétroéclairés
derriere = np.clip(ndimage.gaussian_filter(gl, 14) * 3, 0, 1)                    # là où le logo est juste derrière
ombre = 1 - 0.38 * L * np.clip(ndimage.gaussian_filter(gl, 30) * 1.8, 0, 1)            # doigts à contre-jour devant la lumière
img = img * (1 - DEVANT[..., None]) + (AVANT_LOGO * ombre[..., None]) * DEVANT[..., None]
bordd = np.clip(DEVANT - ndimage.gaussian_filter(DEVANT, 6), 0, 1) * 3.0
img += (bordd * derriere)[..., None] * np.array([1.0, 0.62, 0.38], np.float32) * 1.5 * L   # la lumière du logo passe sur le bord des doigts
img += (ndimage.gaussian_filter(gl, 40) * 1.4 * DEVANT)[..., None] * ORANGE * 0.12 * L       # et déborde un peu sur eux

# ------------------------------------------------------------------ finition : vignette, grain, compression douce des hautes lumières
img *= (0.55 + 0.45 * radial(1080, 2000, 1900, 2500, 0.7))[..., None]
img = img / (1 + 0.18 * img)                    # compression douce
img = img * 1.15
img += rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
out = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
out.save(sys.argv[3] + ".png")
out.save(sys.argv[3] + ".jpg", quality=95, subsampling=0)
print("ok", out.size)
