#!/usr/bin/env python3
"""Détection des dents image par image, stable dans le temps (demande : « précision extrême pour les dents »).
Version finale : l'intérieur de la bouche est découpé par un modèle de segmentation du visage (BiSeNet entraîné sur
CelebAMask-HQ, assets/modeles/parsing/resnet18.onnx, téléchargé depuis github.com/yakhyo/face-parsing ; classes 11 = intérieur
de la bouche, 12 = lèvre du haut, 13 = lèvre du bas). Dans cet intérieur, les dents sont les pixels clairs (luminosité, nette au
pixel), le fond sombre, la langue et les gencives ne bougent pas. Les étapes ci-dessous (teinte, croissance) ne servent plus.
1. Chaque bouche est recalée dans un repère fixe (similitude calée sur les coins et le centre des lèvres, assets/levres.json) :
   canevas 208×128, largeur de bouche = 160 px.
2. Couleurs lues dans assets/montage-image.mp4 (meilleure que la vidéo détourée, qui a perdu de la chrominance), silhouette dans
   assets/perso.webm. Une dent = teinte ivoire-orangée (teinte ≥ 4,5° ; la lèvre rose est vers 0–4°), plus claire que la peau.
   Elle doit PARTIR DU FOND SOMBRE DE LA BOUCHE : croissance de proche en proche depuis le bord de l'ouverture sombre (16 px au
   plus), arrêtée par les bords horizontaux marqués (limite dent / lèvre). Un reflet sur la lèvre ne touche pas l'ouverture : exclu.
3. Médiane sur 5 images voisines dans le repère fixe, sans traverser les coupes du montage : une dent oubliée sur une image est
   rattrapée, un reflet isolé disparaît, plus de clignotement. Puis on ne garde que là où l'image elle-même a une couleur de dent.
Sortie : assets/dents.npy (float16, images × 128 × 208) + assets/dents.json (repère de chaque image). Utilisé par tools/bouche.py."""
import json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ICI = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
CW, CH, ECH = 208, 128, 160.0
D = json.loads((ICI / "assets/levres.json").read_text())
N = len(D["ext"])
for cle in ("ext", "int"):
    for k in range(N):
        if D[cle][k] is None:
            j = min((q for q in range(N) if D[cle][q] is not None), key=lambda q: abs(q - k))
            D[cle][k] = D[cle][j]
EXT, INT = np.array(D["ext"], float), np.array(D["int"], float)
# coupes du montage (images où commence un nouveau morceau)
dec = json.loads((ICI / "assets/decoupage.json").read_text())
COUPES, c = [0], 0
for o in dec:
    c += round((o["fin"] - o["debut"]) * FPS); COUPES.append(c)
morceau = np.searchsorted(COUPES, np.arange(N), side="right")


def repere(k):
    e = EXT[k]
    g, d = e[0], e[10]                       # coins de la bouche (points 61 et 291)
    w = max(np.hypot(*(d - g)), 30.0)
    th = np.arctan2(d[1] - g[1], d[0] - g[0])
    c = (e.mean(0) + INT[k].mean(0)) / 2
    return c, w, th


def vers_canevas(pts, c, w, th):
    R = np.array([[np.cos(-th), -np.sin(-th)], [np.sin(-th), np.cos(-th)]])
    return (pts - c) @ R.T * (ECH / w) + [CW / 2, CH / 2]


def poly(pts):
    im = Image.new("L", (CW * 2, CH * 2), 0)
    ImageDraw.Draw(im).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    return np.asarray(im.resize((CW, CH), Image.LANCZOS), np.float32) / 255


def echantillonne(f, c, w, th):
    qy, qx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    u, v = (qx - CW / 2) * (w / ECH), (qy - CH / 2) * (w / ECH)
    x = c[0] + u * np.cos(th) - v * np.sin(th)
    y = c[1] + u * np.sin(th) + v * np.cos(th)
    return np.stack([ndimage.map_coordinates(f[..., i].astype(np.float32), [y, x], order=1, mode="nearest") for i in range(4)], -1)


def score(s, A, k, c, w, th):
    """Score dent doux (0–1) : bords tracés par la luminosité (nette au pixel), teinte (floue) seulement pour dent / lèvre."""
    R, Gc, B = (ndimage.gaussian_filter(s[..., i], 2.5) for i in range(3))
    Y = 0.299 * s[..., 0] + 0.587 * s[..., 1] + 0.114 * s[..., 2]
    hue = np.degrees(np.arctan2(np.sqrt(3) * (Gc - B), 2 * R - Gc - B))
    mext = poly(vers_canevas(EXT[k], c, w, th))
    mint = poly(vers_canevas(INT[k], c, w, th))
    anneau = (ndimage.grey_dilation(mext, size=21) > 0.5) & (ndimage.grey_dilation(mext, size=7) < 0.5) & (A > 0.5)
    peau = float(np.median(Y[anneau])) if anneau.sum() > 50 else 60.0
    dedans = ndimage.grey_erosion(mext, size=5) * (A > 0.5)
    pres = ndimage.grey_dilation(mint, size=13) > 0.5
    cavite = (dedans > 0.5) & pres & (Y < max(45, peau - 10))
    lab, n = ndimage.label(cavite)
    if n:
        t_ = ndimage.sum(cavite, lab, range(1, n + 1))
        cavite = np.isin(lab, [q + 1 for q in range(n) if t_[q] >= 15])
    # teinte de la lèvre du bas sur cette image (claire, loin de l'ouverture)
    loin = (dedans > 0.5) & ~ndimage.binary_dilation(cavite | (mint > 0.5), iterations=8) & (Y > peau + 25)
    h_levre = float(np.median(hue[loin])) if loin.sum() > 80 else 2.0
    w_hue = np.clip((hue - (h_levre + 1.5)) / 3.0, 0, 1)
    w_lum = np.clip((Y - (peau + 12)) / 18, 0, 1) * np.clip((248 - Y) / 10, 0, 1)
    if cavite.any():
        d_cav = ndimage.distance_transform_edt(~cavite)
        w_geo = np.clip(1 - (d_cav - 8) / 12, 0, 1)        # une dent est à moins de ~20 px de l'ouverture sombre
    else:
        w_geo = np.zeros_like(Y)
    t = w_hue * w_lum * w_geo * dedans
    # limite dent → lèvre : en descendant, après être passé sur de la dent, un bord nettement plus clair = début de la lèvre
    gy = ndimage.sobel(ndimage.gaussian_filter(Y, 0.8), axis=0)
    vu = np.maximum.accumulate(t > 0.5, axis=0)
    bord = (gy > 50) & vu & ~ndimage.binary_dilation(cavite, iterations=3)
    sous_bord = np.maximum.accumulate(bord, axis=0)
    t *= ~sous_bord
    return t, w_hue * w_lum * dedans


import onnxruntime as ort
SESS = None
YC = ALC = PEAU = None   # cache (luminosité, silhouette, peau) par image, rempli par score_modele
MEAN, STD = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])


def proba_bouche(fc, k):
    """probabilité « intérieur de la bouche » (classe 11) du modèle, sur l'image entière (zone du visage)"""
    global SESS
    if SESS is None:
        SESS = ort.InferenceSession(str(ICI / "assets/modeles/parsing/resnet18.onnx"), providers=["CPUExecutionProvider"])
    e = EXT[k]
    c = e.mean(0); w = max(np.hypot(*(e[10] - e[0])), 30.0)
    S = 4.0 * w; cx, cy = c[0], c[1] - 1.0 * w
    x0, y0 = cx - S / 2, cy - S / 2
    im = Image.fromarray(np.ascontiguousarray(fc[..., :3])).transform((512, 512), Image.EXTENT, (x0, y0, x0 + S, y0 + S), Image.BILINEAR)
    x = ((np.asarray(im) / 255.0 - MEAN) / STD).transpose(2, 0, 1)[None].astype(np.float32)
    out = SESS.run(None, {"input": x})[0][0]
    out = out - out.max(0, keepdims=True)
    pr = np.exp(out); pr /= pr.sum(0, keepdims=True)
    return pr[11], (x0, y0, S)


def score_modele(fc, A, k, c, w, th):
    pm, (x0, y0, S) = proba_bouche(fc, k)
    qy, qx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    u, v = (qx - CW / 2) * (w / ECH), (qy - CH / 2) * (w / ECH)
    X = c[0] + u * np.cos(th) - v * np.sin(th)
    Yi = c[1] + u * np.sin(th) + v * np.cos(th)
    P = ndimage.map_coordinates(pm, [(Yi - y0) / S * 512, (X - x0) / S * 512], order=1, mode="constant", cval=0.0)
    s = echantillonne(fc, c, w, th)
    Y = 0.299 * s[..., 0] + 0.587 * s[..., 1] + 0.114 * s[..., 2]
    mext = poly(vers_canevas(EXT[k], c, w, th))
    anneau = (ndimage.grey_dilation(mext, size=21) > 0.5) & (ndimage.grey_dilation(mext, size=7) < 0.5) & (A > 0.5)
    peau = float(np.median(Y[anneau])) if anneau.sum() > 50 else 60.0
    P = np.clip((P - 0.35) / 0.4, 0, 1)                       # bord de la bouche net (sans déborder sur la lèvre)
    YC[k], ALC[k], PEAU[k] = Y, A, peau
    return lum_dents(Y, P, A, peau)


def lum_dents(Y, P, A, peau):
    dedans = P > 0.5
    if dedans.sum() < 40:
        return np.zeros_like(Y), P, 0.0
    ref = float(np.percentile(Y[dedans], 90))
    seuil = max(peau + 3, 0.45 * ref)                 # les dents dans l'ombre comptent aussi (pas de plaques)
    w_lum = np.clip((Y - seuil) / max(0.3 * ref, 15), 0, 1) * (A > 0.5)
    email = (P > 0.5) & (w_lum > 0.5)
    lum_email = float(np.percentile(Y[email], 75)) if email.sum() > 30 else 0.0
    return w_lum, P, lum_email


if __name__ == "__main__":
    import sys
    CACHE = ICI / "assets/dents-cache.npz"
    if "--cache" in sys.argv and CACHE.exists():      # réglage rapide : on reprend la sortie du modèle déjà calculée
        z = np.load(CACHE)
        G, YC, ALC, PEAU = z["P"].astype(np.float32), z["Y"].astype(np.float32), z["A"].astype(np.float32), z["peau"]
        reperes = json.loads((ICI / "assets/dents.json").read_text())["reperes"]
        T = np.zeros_like(G); LUM = np.zeros(N)
        for k in range(N):
            T[k], _, LUM[k] = lum_dents(YC[k], G[k], ALC[k], PEAU[k])
    else:
        YC = np.zeros((N, CH, CW), np.float32); ALC = np.zeros((N, CH, CW), np.float32); PEAU = np.zeros(N)
        T = np.zeros((N, CH, CW), np.float32)       # luminosité « dent » de chaque image
        G = np.zeros((N, CH, CW), np.float32)       # probabilité « intérieur de la bouche » (modèle)
        LUM = np.zeros(N)                           # luminosité de l'émail (pour un blanc constant)
        pa = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", str(ICI / "assets/perso.webm"),
                               "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
        pc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(ICI / "assets/montage-image.mp4"),
                               "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
        reperes = []
        k = 0
        while k < N:
            ba, bc = pa.stdout.read(W * H * 4), pc.stdout.read(W * H * 4)
            if len(ba) < W * H * 4 or len(bc) < W * H * 4:
                break
            fa = np.frombuffer(ba, np.uint8).reshape(H, W, 4)
            fc = np.frombuffer(bc, np.uint8).reshape(H, W, 4)
            c, w, th = repere(k)
            reperes.append([float(c[0]), float(c[1]), float(w), float(th)])
            A = echantillonne(fa, c, w, th)[..., 3] / 255
            T[k], G[k], LUM[k] = score_modele(fc, A, k, c, w, th)
            if k % 300 == 0:
                print(k, flush=True)
            k += 1
        while len(reperes) < N:
            reperes.append(reperes[-1])
        pa.kill(); pc.kill()
        np.savez(CACHE, P=G.astype(np.float16), Y=YC.astype(np.float16), A=ALC.astype(np.float16), peau=PEAU)
    # le modèle « décroche » parfois une ou deux images : la bouche de l'image = max(elle-même, médiane des 5 voisines du morceau)
    # ; la luminosité (nette, de l'image courante) décide toujours ce qui est dent dans cette bouche
    F = np.zeros_like(T)
    email = np.zeros(N)
    for k in range(N):
        vois = [j for j in range(k - 2, k + 3) if 0 <= j < N and morceau[j] == morceau[k]]
        P = np.maximum(G[k], np.median(G[vois], axis=0))
        F[k] = P * T[k]
        lab, n = ndimage.label(F[k] > 0.3)
        if n:                                                      # petits points isolés retirés
            t_ = ndimage.sum(np.ones_like(F[k]), lab, range(1, n + 1))
            F[k] *= ndimage.binary_dilation(np.isin(lab, [q + 1 for q in range(n) if t_[q] >= 70]), iterations=2)
        F[k] = ndimage.gaussian_filter(F[k], 0.5)
        l = [LUM[j] for j in vois if LUM[j] > 0]
        email[k] = float(np.median(l)) if l else 0.0               # luminosité de l'émail, lissée dans le plan
    aire = np.array([(F[k] > 0.4).sum() for k in range(N)], float)
    for k in range(N):                                             # peu de dent visible (bouts de dents) : blanchiment progressif
        vois = [j for j in range(k - 2, k + 3) if 0 <= j < N and morceau[j] == morceau[k]]
        F[k] *= float(np.clip((np.median(aire[vois]) - 150) / 250, 0, 1))
    np.save(ICI / "assets/dents.npy", F.astype(np.float16))
    (ICI / "assets/dents.json").write_text(json.dumps({"canevas": [CW, CH, ECH], "reperes": reperes, "email": [round(float(e), 1) for e in email]}))
    print("images", N, "avec dents", int((F.max(axis=(1, 2)) > 0.3).sum()))
