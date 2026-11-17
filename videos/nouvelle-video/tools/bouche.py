#!/usr/bin/env python3
"""Retouche de la bouche image par image sur la personne détourée (assets/perso.webm, avec transparence) :
lèvres plus rosées, dents plus blanches (demande de l'utilisateur, « très méticuleux »).
Contours exacts des lèvres : assets/levres.json (tools/levres.py, MediaPipe Face Landmarker, 20 points extérieurs + 20 intérieurs).
- lèvres = entre le contour extérieur et le contour intérieur (masque anticrénelé, bord adouci de 1,5 px, jamais sur la peau) ;
- dents = pixels clairs et peu rouges À L'INTÉRIEUR du contour intérieur (la langue, les gencives et le fond sombre ne bougent pas).
Usage : python3 tools/bouche.py essai t1 t2 …   (planche avant/après)   |   python3 tools/bouche.py tout   (→ assets/perso-retouche.webm)"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ICI = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
D = json.loads((ICI / "assets/levres.json").read_text())
N = len(D["ext"])
# images sans visage : on reprend la plus proche ; puis lissage léger sur 3 images (anti-tremblement) sauf mouvement rapide
for cle in ("ext", "int"):
    L = D[cle]
    for k in range(N):
        if L[k] is None:
            j = min((q for q in range(N) if L[q] is not None), key=lambda q: abs(q - k))
            L[k] = L[j]
    A = np.array(L, float)
    B = A.copy()
    for k in range(1, N - 1):
        if np.abs(A[k + 1] - A[k - 1]).max() < 12:
            B[k] = (A[k - 1] + 2 * A[k] + A[k + 1]) / 4
    D[cle] = B
SS = 3   # suréchantillonnage du masque (bords anticrénelés)


def masque(poly, x0, y0, w, h):
    im = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(im).polygon([((x - x0) * SS, (y - y0) * SS) for x, y in poly], fill=255)
    return np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255


def retouche(rgba, k):
    k = min(k, N - 1)
    ext, inn = D["ext"][k], D["int"][k]
    x0, y0 = int(ext[:, 0].min()) - 8, int(ext[:, 1].min()) - 8
    x1, y1 = int(ext[:, 0].max()) + 9, int(ext[:, 1].max()) + 9
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
    w, h = x1 - x0, y1 - y0
    if w < 20 or h < 10:
        return rgba
    roi = rgba[y0:y1, x0:x1, :3].astype(np.float32)
    a = rgba[y0:y1, x0:x1, 3].astype(np.float32) / 255
    mext, mint = masque(ext, x0, y0, w, h), masque(inn, x0, y0, w, h)
    R, G, B = roi[..., 0], roi[..., 1], roi[..., 2]
    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cb = 128 - 0.1687 * R - 0.3313 * G + 0.5 * B
    Cr = 128 + 0.5 * R - 0.4187 * G - 0.0813 * B
    # peau de référence : anneau juste autour de la bouche
    anneau = (ndimage.grey_dilation(mext, size=25) > 0.5) & (ndimage.grey_dilation(mext, size=9) < 0.5) & (a > 0.5)
    peau = float(np.median(Y[anneau])) if anneau.sum() > 50 else 70.0
    # dents : dans l'ouverture (contour intérieur un peu élargi vers le haut), claires et plus jaunes que la lèvre (Cb bas)
    zone_d = ndimage.grey_dilation(mint, size=(7, 3)) > 0.5
    zone_l = ndimage.grey_dilation(mext, size=7) > 0.5
    GB = ndimage.gaussian_filter(G - B, 2.0)          # dents : vert > bleu (ivoire) ; lèvres : bleu ≥ vert (rose)
    dents = zone_d & (Y > max(70, peau + 8)) & (GB >= 1.0) & (Cr < 158) & (a > 0.5)
    # tri par zone entière (jamais pixel par pixel, sinon les dents deviennent tachetées) : une zone de dents doit toucher le fond
    # sombre de la bouche ; sa force dépend de sa teinte ivoire moyenne et de sa taille. Les vraies dents (ivoire net, grande zone)
    # blanchissent pleinement, un reflet jaunâtre sur la lèvre (teinte faible, petite zone) presque pas.
    sombre = ndimage.binary_dilation(zone_d & (Y < max(45, peau - 10)) & (a > 0.5), iterations=6)
    lab, n = ndimage.label(dents)
    poids = np.zeros_like(Y)
    for q in range(1, n + 1):
        z = lab == q
        if (sombre & z).any():
            poids[z] = np.clip((GB[z].mean() - 1.8) / 2.5, 0, 1) * np.clip((z.sum() - 150) / 400, 0, 1)
    dents = poids > 0
    dents = ndimage.binary_opening(dents, iterations=1)
    if dents.sum() < 30:
        dents[:] = False
    # lèvre du bas (claire, rosée) : suivie à la couleur, à l'intérieur du contour (légèrement élargi), jamais sur les dents
    bas = zone_l & (Y > peau + 22) & (a > 0.5) & ~ndimage.binary_dilation(dents, iterations=1)
    lab, n = ndimage.label(bas)
    if n:
        t_ = ndimage.sum(bas, lab, range(1, n + 1))
        bas = np.isin(lab, [q + 1 for q in range(n) if t_[q] > max(60, 0.15 * t_.max())])
    bas = ndimage.binary_fill_holes(ndimage.binary_closing(bas, iterations=2)) & zone_l & ~dents
    # lèvre du haut (foncée) : contour extérieur resserré de 10 % vers le centre, au-dessus de l'ouverture, plus discrète
    c = ext.mean(0)
    ext_s = c + (ext - c) * np.array([0.94, 0.86])
    haut = (masque(ext_s, x0, y0, w, h) > 0.5) & (mint < 0.5) & ~bas & ~dents
    yy = np.arange(h)[:, None] + y0
    haut &= yy < np.interp(np.arange(w) + x0, np.sort(inn[:, 0]), inn[np.argsort(inn[:, 0]), 1])[None, :] + 2
    ml = np.maximum(ndimage.gaussian_filter(bas.astype(np.float32), 1.3), 0.55 * ndimage.gaussian_filter(haut.astype(np.float32), 2.0)) * a
    # rose : teinte rose appliquée en gardant la texture (lumière) de la lèvre
    rose = np.stack([Y * 1.16 + 24, Y * 0.86 + 2, Y * 0.98 + 10], -1)
    out = roi * (1 - 0.40 * ml[..., None]) + np.clip(rose, 0, 255) * (0.40 * ml[..., None])
    # force progressive (pas de bord net) : plus c'est clair et ivoire, plus on blanchit ; les dents dans l'ombre un peu moins
    wY = np.clip((Y - (peau + 5)) / 45, 0, 1)
    wGB = np.clip((GB - 1.0) / 5.0, 0, 1)
    coeur = ndimage.grey_erosion(mint, size=3) > 0.5
    lab, n = ndimage.label(dents)
    if n:   # on ne garde que les zones de dents qui touchent le cœur de l'ouverture (pas un coin de lèvre)
        dents = np.isin(lab, [q for q in range(1, n + 1) if (coeur & (lab == q)).any() and (lab == q).sum() >= 25])
    md = ndimage.gaussian_filter(ndimage.grey_dilation(poids * dents, size=3) * wY * wGB, 1.2) * a
    md *= ~ndimage.binary_dilation(bas, iterations=1)
    lum = 0.299 * out[..., 0] + 0.587 * out[..., 1] + 0.114 * out[..., 2]
    nl = lum * 1.32 + 22
    blanc = np.stack([nl, nl * 0.965, nl * 0.91], -1)   # blanc chaud (R > V > B, comme l'éclairage), texture conservée
    out = out * (1 - 0.85 * md[..., None]) + np.clip(blanc, 0, 255) * (0.85 * md[..., None])
    rgba[y0:y1, x0:x1, :3] = np.clip(out, 0, 255).astype(np.uint8)
    return rgba


def lecteur(debut=0.0, n=None, src="assets/perso.webm"):
    args = ["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-ss", f"{debut:.3f}", "-i", str(ICI / src)]
    if n:
        args += ["-frames:v", str(n)]
    return subprocess.Popen(args + ["-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)


if sys.argv[1] == "essai":
    S = Path("/tmp/claude-0/-home-user-Github-worker/dc3cf4ad-cec2-5288-bb16-b638c74edad6/scratchpad/bouche")
    S.mkdir(exist_ok=True)
    lignes = []
    for t in map(float, sys.argv[2:]):
        p = lecteur(t, 1)
        f = np.frombuffer(p.stdout.read(W * H * 4), np.uint8).reshape(H, W, 4).copy()
        p.wait()
        k = int(round(t * FPS))
        e = D["ext"][min(k, N - 1)]
        cx, cy = e[:, 0].mean(), e[:, 1].mean()
        box = (int(cx - 85), int(cy - 55), int(cx + 85), int(cy + 55))
        av = Image.fromarray(f).convert("RGB").crop(box).resize((340, 220), Image.LANCZOS)
        ap = Image.fromarray(retouche(f.copy(), k)).convert("RGB").crop(box).resize((340, 220), Image.LANCZOS)
        o = Image.new("RGB", (680, 220)); o.paste(av, (0, 0)); o.paste(ap, (340, 0))
        ImageDraw.Draw(o).text((4, 4), f"{t:.2f}s", fill=(255, 0, 0))
        lignes.append(o)
    g = Image.new("RGB", (680, 220 * len(lignes)))
    for k, o in enumerate(lignes):
        g.paste(o, (0, 220 * k))
    g.save(S / "avant-apres.jpg")
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
        enc.stdin.write(retouche(f, k).tobytes())
        k += 1
        if k % 150 == 0:
            print(k, "images", flush=True)
    enc.stdin.close(); enc.wait(); p.wait()
    print("terminé :", k, "images → assets/perso-retouche.webm")
